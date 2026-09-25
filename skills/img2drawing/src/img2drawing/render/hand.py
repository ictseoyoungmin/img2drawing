"""Deterministic hand dynamics and stroke seeds.

Seeds are derived from authored stroke identity/geometry only. The private compatibility
``Stroke.stage`` field is excluded (seed identity model ``stage-free-render-seed-v1``), so
identical authored geometry renders identically wherever it is replayed.
"""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from math import pi

import numpy as np

from ..core.ir import Stroke
from .contact_profile import PencilContactProfile


def _clamp01(v: float) -> float:
    return max(0.0, min(1.0, float(v)))


def _seed_payload(stroke: Stroke) -> bytes:
    payload = {
        "stroke_id": stroke.stroke_id,
        "points": [[float(x), float(y)] for x, y in stroke.points],
        "pressure": None if stroke.pressure is None else [float(v) for v in stroke.pressure],
        "width": float(stroke.width),
        "opacity": float(stroke.opacity),
        "role": stroke.role,
        "part": stroke.part,
        "stage": None,
        "layer": int(stroke.layer),
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def grain_seed(stroke: Stroke) -> int:
    """Material-particle seed, independent of grain/hardness values."""

    return int.from_bytes(hashlib.sha256(_seed_payload(stroke)).digest()[:4], "little")


def hand_seed(stroke: Stroke) -> int:
    """Latent hand-motion seed, independent of dynamics strength."""

    return int.from_bytes(hashlib.sha256(_seed_payload(stroke)).digest()[:8], "little")


def stroke_material(stroke: Stroke) -> tuple[float, float]:
    """Return ``(grain, hardness)`` from tool state with the pencil defaults."""

    ts = stroke.tool_state if isinstance(stroke.tool_state, dict) else {}
    return _clamp01(ts.get("grain", 0.30)), _clamp01(ts.get("hardness", 0.65))


def _dynamics(stroke: Stroke) -> tuple[float, float, float]:
    ts = stroke.tool_state if isinstance(stroke.tool_state, dict) else {}
    return (
        _clamp01(ts.get("jitter", 0.0)),
        _clamp01(ts.get("taper_in", 0.0)),
        _clamp01(ts.get("taper_out", 0.0)),
    )


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
    strength = 0.30 * np.sqrt(jitter)
    return 1.0 - strength * (cadence ** 8)


def _normals(pts: np.ndarray) -> np.ndarray:
    tangent = np.empty_like(pts)
    tangent[0] = pts[1] - pts[0]
    tangent[-1] = pts[-1] - pts[-2]
    if len(pts) > 2:
        tangent[1:-1] = pts[2:] - pts[:-2]
    norm = np.linalg.norm(tangent, axis=1)
    norm[norm < 1e-9] = 1.0
    tangent /= norm[:, None]
    return np.column_stack([-tangent[:, 1], tangent[:, 0]])


def eraser_hand_dynamics(stroke: Stroke) -> Stroke:
    """Hand dynamics for eraser passes: path wobble plus micro pressure dips.

    Endpoints stay anchored; explicit pressure remains the authority and only gets a
    bounded entry/release touch and cadence variation.
    """
    jitter, taper_in, taper_out = _dynamics(stroke)
    if jitter <= 1e-12 and taper_in <= 1e-12 and taper_out <= 1e-12:
        return deepcopy(stroke)

    pts, pressure, t = _resample(stroke)
    if len(pts) < 2:
        return deepcopy(stroke)
    normal = _normals(pts)

    seed = hand_seed(stroke)
    wave = _hand_wave(t, seed)
    end_anchor = np.sin(pi * t) ** 0.78
    amp = min(1.35, (0.42 + 0.14 * min(float(stroke.width), 5.0)) * np.sqrt(jitter))
    moved = pts + normal * (amp * end_anchor * wave)[:, None]
    moved[0] = pts[0]
    moved[-1] = pts[-1]

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


def pencil_hand_dynamics(stroke: Stroke, profile: PencilContactProfile) -> Stroke:
    """Path wobble with continuous pressure variation, not micro-breaks."""
    jitter, taper_in, taper_out = _dynamics(stroke)
    if jitter <= 1e-12 and taper_in <= 1e-12 and (taper_out <= 1e-12):
        return deepcopy(stroke)
    pts, pressure, t = _resample(stroke, spacing=profile.trajectory_spacing)
    if len(pts) < 2:
        return deepcopy(stroke)
    normal = _normals(pts)
    seed = hand_seed(stroke)
    wave = _hand_wave(t, seed)
    end_anchor = np.sin(pi * t) ** 0.78
    amp = min(1.35, (0.42 + 0.14 * min(float(stroke.width), 5.0)) * np.sqrt(jitter))
    moved = pts + normal * (amp * end_anchor * wave)[:, None]
    moved[0] = pts[0]
    moved[-1] = pts[-1]
    hp = profile.hand
    entry = _smoothstep(t / hp.tip_span)
    release = _smoothstep((1.0 - t) / hp.tip_span)
    tip_factor = (1.0 - hp.taper_in_strength * taper_in * (1.0 - entry)) * (1.0 - hp.taper_out_strength * taper_out * (1.0 - release))
    phase = 2.0 * pi * _seed_unit(seed ^ 3039394381, 12)
    freq = hp.pressure_cadence_frequency_min + hp.pressure_cadence_frequency_span * _seed_unit(seed, 28)
    cadence = 1.0 + hp.pressure_cadence_strength * np.sqrt(jitter) * np.sin(2.0 * pi * freq * t + phase)
    dyn_pressure = np.clip(pressure * tip_factor * cadence, 0.025, 1.0)
    out = deepcopy(stroke)
    out.points = [(float(x), float(y)) for x, y in moved]
    out.pressure = [float(v) for v in dyn_pressure]
    return out.cleaned()


__all__ = [
    "eraser_hand_dynamics",
    "grain_seed",
    "hand_seed",
    "pencil_hand_dynamics",
    "stroke_material",
]
