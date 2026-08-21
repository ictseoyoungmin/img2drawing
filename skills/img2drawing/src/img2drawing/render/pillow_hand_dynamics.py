from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from math import hypot, pi

import numpy as np

from ..core.ir import Stroke, StrokeIR
from . import pillow_graphite_grain as p3

RENDERER_ID = "pillow-hand-dynamics-v5"
RENDERER_VERSION = "1"
DEFAULT_SUPERSAMPLE = 8
DEFAULT_JITTER = 0.0
DEFAULT_TAPER_IN = 0.0
DEFAULT_TAPER_OUT = 0.0


def _clamp01(v: float) -> float:
    return max(0.0, min(1.0, float(v)))


def _dynamics(stroke: Stroke) -> tuple[float, float, float]:
    ts = stroke.tool_state if isinstance(stroke.tool_state, dict) else {}
    return (
        _clamp01(ts.get("jitter", DEFAULT_JITTER)),
        _clamp01(ts.get("taper_in", DEFAULT_TAPER_IN)),
        _clamp01(ts.get("taper_out", DEFAULT_TAPER_OUT)),
    )


def _stable_seed(stroke: Stroke) -> int:
    """Stable latent hand-motion seed independent of dynamics strength.

    Geometry, stroke identity and semantic ownership define the latent motion field.
    Changing jitter/taper therefore exposes more or less of the same field rather than
    inventing an unrelated stroke.  No process-global RNG state is used.
    """
    payload = {
        "stroke_id": stroke.stroke_id,
        "points": [[float(x), float(y)] for x, y in stroke.points],
        "pressure": None if stroke.pressure is None else [float(v) for v in stroke.pressure],
        "width": float(stroke.width),
        "opacity": float(stroke.opacity),
        "role": stroke.role,
        "part": stroke.part,
        "stage": stroke.stage,
        "layer": int(stroke.layer),
    }
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return int.from_bytes(hashlib.sha256(blob).digest()[:8], "little")


def _seed_unit(seed: int, shift: int) -> float:
    x = (seed >> shift) & 0xFFFF
    return float(x) / 65535.0


def _smoothstep(x: np.ndarray) -> np.ndarray:
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3.0 - 2.0 * x)


def _resample(stroke: Stroke, spacing: float = 1.15) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    pts = np.asarray(stroke.points, dtype=np.float64)
    if len(pts) < 2:
        p = np.asarray(stroke.pressure or [0.55] * len(pts), dtype=np.float64)
        return pts, p, np.zeros(len(pts), dtype=np.float64)

    seg = np.linalg.norm(np.diff(pts, axis=0), axis=1)
    cumulative = np.concatenate([[0.0], np.cumsum(seg)])
    total = float(cumulative[-1])
    if total <= 1e-9:
        p = np.asarray(stroke.pressure or [0.55] * len(pts), dtype=np.float64)
        return pts, p, np.linspace(0.0, 1.0, len(pts))

    count = max(2, int(np.ceil(total / max(0.45, float(spacing)))) + 1)
    s = np.linspace(0.0, total, count)
    x = np.interp(s, cumulative, pts[:, 0])
    y = np.interp(s, cumulative, pts[:, 1])

    if stroke.pressure is not None and len(stroke.pressure) == len(stroke.points):
        src_p = np.asarray(stroke.pressure, dtype=np.float64)
    else:
        ts = stroke.tool_state if isinstance(stroke.tool_state, dict) else {}
        src_p = np.full(len(stroke.points), _clamp01(ts.get("pressure", 0.55)), dtype=np.float64)
    p = np.interp(s, cumulative, src_p)
    return np.column_stack([x, y]), p, s / total


def _hand_wave(t: np.ndarray, seed: int) -> np.ndarray:
    """Low-amplitude band-limited hand motion, zero-mean-ish and deterministic."""
    phase1 = 2.0 * pi * _seed_unit(seed, 0)
    phase2 = 2.0 * pi * _seed_unit(seed, 16)
    phase3 = 2.0 * pi * _seed_unit(seed, 32)
    f1 = 1.65 + 1.10 * _seed_unit(seed, 8)
    f2 = 3.80 + 1.75 * _seed_unit(seed, 24)
    f3 = 7.25 + 2.50 * _seed_unit(seed, 40)
    wave = (
        0.60 * np.sin(2.0 * pi * f1 * t + phase1)
        + 0.28 * np.sin(2.0 * pi * f2 * t + phase2)
        + 0.12 * np.sin(2.0 * pi * f3 * t + phase3)
    )
    wave -= float(np.mean(wave))
    denom = max(1e-6, float(np.max(np.abs(wave))))
    return wave / denom


def _micro_pressure(t: np.ndarray, seed: int, jitter: float) -> np.ndarray:
    """Bounded cadence variation used for tiny pressure dips, never canvas noise."""
    if jitter <= 0.0:
        return np.ones_like(t)
    phase = 2.0 * pi * _seed_unit(seed, 12)
    freq = 5.5 + 4.0 * _seed_unit(seed, 28)
    cadence = 0.5 + 0.5 * np.sin(2.0 * pi * freq * t + phase)
    # Hand dynamics remain restrained at preset jitter values. At diagnostic jitter=1,
    # weak touches can momentarily drop by about 30%, enough to create micro-break feel.
    strength = 0.30 * np.sqrt(jitter)
    return 1.0 - strength * (cadence ** 8)


def apply_hand_dynamics(stroke: Stroke) -> Stroke:
    """Return a derived stroke with deterministic tangent-aware hand dynamics.

    The source Stroke is never mutated.  Dynamics are applied in logical coordinates
    before P3 material deposition, so every visible change remains attributable to the
    explicit stroke and deterministic under replay.
    """
    jitter, taper_in, taper_out = _dynamics(stroke)
    if jitter <= 1e-12 and taper_in <= 1e-12 and taper_out <= 1e-12:
        return deepcopy(stroke)

    pts, pressure, t = _resample(stroke)
    if len(pts) < 2:
        return deepcopy(stroke)

    # Tangent from centered finite differences; displacement occurs along the local normal,
    # so dynamics do not introduce systematic shortening/lengthening of the intended path.
    tangent = np.empty_like(pts)
    tangent[0] = pts[1] - pts[0]
    tangent[-1] = pts[-1] - pts[-2]
    if len(pts) > 2:
        tangent[1:-1] = pts[2:] - pts[:-2]
    norm = np.linalg.norm(tangent, axis=1)
    norm[norm < 1e-9] = 1.0
    tangent /= norm[:, None]
    normal = np.column_stack([-tangent[:, 1], tangent[:, 0]])

    seed = _stable_seed(stroke)
    wave = _hand_wave(t, seed)
    # Endpoints remain anchored. sqrt(jitter) makes low preset values perceptible without
    # allowing high diagnostic values to wander arbitrarily far from the authored path.
    end_anchor = np.sin(pi * t) ** 0.78
    amp = min(1.35, (0.42 + 0.14 * min(float(stroke.width), 5.0)) * np.sqrt(jitter))
    displacement = amp * end_anchor * wave
    moved = pts + normal * displacement[:, None]
    moved[0] = pts[0]
    moved[-1] = pts[-1]

    # Explicit pressure remains the authority. P4 only adds a bounded entry/release touch
    # and cadence variation. This avoids re-authoring the stroke in the renderer.
    tip_span = 0.14
    entry = _smoothstep(t / tip_span)
    release = _smoothstep((1.0 - t) / tip_span)
    tip_factor = (1.0 - 0.22 * taper_in * (1.0 - entry)) * (1.0 - 0.24 * taper_out * (1.0 - release))
    cadence = _micro_pressure(t, seed ^ 0xB5297A4D, jitter)
    dyn_pressure = np.clip(pressure * tip_factor * cadence, 0.025, 1.0)

    out = deepcopy(stroke)
    out.points = [(float(x), float(y)) for x, y in moved]
    out.pressure = [float(v) for v in dyn_pressure]
    return out.cleaned()


def dynamic_ir(ir: StrokeIR) -> StrokeIR:
    """Derive a replay-stable P4 IR view without mutating authoritative StrokeIR."""
    out = StrokeIR(int(ir.width), int(ir.height), metadata=deepcopy(ir.metadata))
    for stroke in ir.strokes:
        out.add(apply_hand_dynamics(stroke))
    return out


def render(
    ir: StrokeIR,
    path: str,
    background=(255, 255, 255, 255),
    *,
    scale: int = 1,
    supersample: int = DEFAULT_SUPERSAMPLE,
    graphite=(36, 34, 32),
) -> None:
    """Render P3 graphite material with deterministic P4 hand dynamics.

    P4 adds only stroke-local path/touch dynamics:
      * tangent-aware subpixel wobble controlled by tool_state.jitter;
      * restrained deterministic pressure cadence/micro-break behavior;
      * bounded entry/release touch controlled by taper_in/taper_out.

    Deliberately absent: paper-coordinate tooth (P5), named grades (P6), graphite-aware
    erasing (P7), and any final-raster sketch/noise filter.
    """
    # Exact delegation preserves P3 byte behavior when dynamics are explicitly disabled.
    if all(sum(_dynamics(s)) <= 1e-12 for s in ir.strokes):
        p3.render(ir, path, background=background, scale=scale, supersample=supersample, graphite=graphite)
        return
    p3.render(dynamic_ir(ir), path, background=background, scale=scale, supersample=supersample, graphite=graphite)
