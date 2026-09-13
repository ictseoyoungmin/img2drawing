from __future__ import annotations

from copy import deepcopy
import hashlib
from pathlib import Path

import numpy as np
from PIL import Image

from ..core.ir import Stroke, StrokeIR
from . import pillow_pencil_contact_core as v10
from . import pillow_pencil_contact_material as v11
from .renderer_contracts import V12_CONTRACT

RENDERER_ID = "pillow-pencil-contact-v12"
RENDERER_VERSION = "1"
RENDERER_CONTRACT = V12_CONTRACT
DEFAULT_SUPERSAMPLE = v11.DEFAULT_SUPERSAMPLE
HIGH_QUALITY_SUPERSAMPLE = v11.HIGH_QUALITY_SUPERSAMPLE

load_pencil_contact_profile = v11.load_pencil_contact_profile
_prepare_grade = v11._prepare_grade

_TERMINAL_MODES = {"contact", "gentle", "flick", "residue"}


def _stroke_terminal_mode(stroke: Stroke) -> str | None:
    """Read persisted semantic terminal intent without importing vNext."""

    ts = stroke.tool_state if isinstance(stroke.tool_state, dict) else {}
    markmaking = None
    provenance = ts.get("provenance")
    if isinstance(provenance, dict):
        metadata = provenance.get("metadata")
        if isinstance(metadata, dict):
            candidate = metadata.get("markmaking")
            if isinstance(candidate, dict):
                markmaking = candidate
    if markmaking is None:
        candidate = ts.get("markmaking")
        if isinstance(candidate, dict):
            markmaking = candidate
    if not isinstance(markmaking, dict):
        return None
    mode = str(markmaking.get("terminal_mode", "")).strip().lower()
    return mode if mode in _TERMINAL_MODES else None


def _stable_terminal_seed(stroke: Stroke) -> int:
    identity = stroke.stroke_id
    if identity is None:
        identity = repr((stroke.points, stroke.width, stroke.role, stroke.part))
    digest = hashlib.sha256(str(identity).encode("utf-8")).digest()
    return int.from_bytes(digest[:4], "little", signed=False)


def _terminal_span(width: float, mode: str) -> float:
    base = v10._physical_terminal_span(max(0.5, float(width)), incoming=False)
    if mode == "flick":
        return max(4.0, 0.55 * base)
    if mode == "residue":
        return min(34.0, 1.25 * base)
    return base


def _apply_terminal_mode(stroke: Stroke, profile) -> Stroke:
    """Resolve semantic terminal intent into a render-only pressure envelope.

    v11 remains exact authority for strokes with no semantic terminal metadata and for
    ``contact`` terminals. Other modes first resample onto the contact trajectory and then
    modify only a bounded physical suffix. This prevents a sparse authored polyline from
    stretching a nominal terminal fade across an entire long segment.
    """

    mode = _stroke_terminal_mode(stroke)
    if mode is None or mode == "contact" or len(stroke.points) < 2:
        return stroke

    pts, pressure, _ = v10.p4._resample(
        stroke, spacing=profile.trajectory_spacing
    )
    if len(pts) < 2:
        return stroke

    seg = np.linalg.norm(np.diff(pts, axis=0), axis=1)
    arc = np.concatenate([[0.0], np.cumsum(seg)])
    total = float(arc[-1])
    if total <= 1e-09:
        return stroke

    span = min(total, _terminal_span(float(stroke.width), mode))
    start = total - span
    u = np.clip((arc - start) / max(span, 1e-09), 0.0, 1.0)
    smooth = u * u * (3.0 - 2.0 * u)

    if mode == "gentle":
        factor = 1.0 - 0.72 * smooth
    elif mode == "flick":
        late = np.power(u, 1.8)
        late = late * late * (3.0 - 2.0 * late)
        factor = 1.0 - 0.965 * late
    else:
        seed = _stable_terminal_seed(stroke) ^ 0x6A09E667
        cell = max(0.8, 0.45 * float(stroke.width))
        noise = v10._value_noise_1d(arc, cell, seed)
        decay = 1.0 - 0.82 * smooth
        breakup = 1.0 - 0.50 * u * (1.0 - noise)
        factor = decay * breakup

    resolved = np.clip(pressure * factor, 0.01, 1.0)
    out = deepcopy(stroke)
    out.points = [(float(x), float(y)) for x, y in pts]
    out.pressure = [float(value) for value in resolved]
    return out.cleaned()


def _smooth_hand_dynamics(stroke: Stroke, profile) -> Stroke:
    prepared = v11._smooth_hand_dynamics(stroke, profile)
    return _apply_terminal_mode(prepared, profile)


def _build_contact_patch(
    stroke: Stroke,
    *,
    factor: float,
    hi_size: tuple[int, int],
    tooth: float,
    paper_scale: float,
    paper_seed: int,
    graphite: tuple[int, int, int],
    profile,
):
    return v11._build_contact_patch(
        stroke,
        factor=factor,
        hi_size=hi_size,
        tooth=tooth,
        paper_scale=paper_scale,
        paper_seed=paper_seed,
        graphite=graphite,
        profile=profile,
    )


def _deposit(
    graphite_canvas: Image.Image,
    stroke: Stroke,
    *,
    factor: float,
    hi_size: tuple[int, int],
    tooth: float,
    paper_scale: float,
    paper_seed: int,
    graphite: tuple[int, int, int],
    profile,
) -> None:
    bounds, layer = _build_contact_patch(
        stroke,
        factor=factor,
        hi_size=hi_size,
        tooth=tooth,
        paper_scale=paper_scale,
        paper_seed=paper_seed,
        graphite=graphite,
        profile=profile,
    )
    graphite_canvas.alpha_composite(layer, dest=(bounds[0], bounds[1]))
    layer.close()


def render(
    ir: StrokeIR,
    path: str | Path,
    background=(255, 255, 255, 255),
    *,
    scale: int = 1,
    supersample: int = DEFAULT_SUPERSAMPLE,
    graphite=(36, 34, 32),
    grade: str | None = None,
    contact_profile: str | Path | None = None,
) -> None:
    if int(scale) != scale or scale < 1:
        raise ValueError("scale must be a positive integer")
    if int(supersample) != supersample or supersample < 2:
        raise ValueError("supersample must be an integer >= 2")
    if grade is not None:
        v10.p6.get_grade(grade)
    profile = load_pencil_contact_profile(contact_profile)
    scale = int(scale)
    supersample = int(supersample)
    factor = float(scale * supersample)
    hi_size = (int(ir.width * factor), int(ir.height * factor))
    out_size = (int(ir.width * scale), int(ir.height * scale))
    tooth, paper_scale, paper_seed = v10.p5._paper_settings(ir)
    graphite_rgb = (int(graphite[0]), int(graphite[1]), int(graphite[2]))
    graphite_canvas = Image.new("RGBA", hi_size, (*graphite_rgb, 0))

    for stroke in sorted(ir.strokes, key=lambda item: item.layer):
        if v10.p7.is_eraser(stroke):
            v10.p7._erase(
                graphite_canvas,
                stroke,
                factor=factor,
                hi_size=hi_size,
                tooth=tooth,
                paper_scale=paper_scale,
                paper_seed=paper_seed,
            )
            continue
        prepared = _smooth_hand_dynamics(_prepare_grade(stroke, grade), profile)
        _deposit(
            graphite_canvas,
            prepared,
            factor=factor,
            hi_size=hi_size,
            tooth=tooth,
            paper_scale=paper_scale,
            paper_seed=paper_seed,
            graphite=graphite_rgb,
            profile=profile,
        )

    base = Image.new("RGBA", hi_size, background)
    final = Image.alpha_composite(base, graphite_canvas).resize(
        out_size, Image.Resampling.LANCZOS
    )
    output = str(path)
    if output.lower().endswith((".jpg", ".jpeg")):
        final.convert("RGB").save(output, quality=95)
    else:
        final.save(output)


__all__ = [
    "DEFAULT_SUPERSAMPLE",
    "HIGH_QUALITY_SUPERSAMPLE",
    "RENDERER_CONTRACT",
    "RENDERER_ID",
    "RENDERER_VERSION",
    "_apply_terminal_mode",
    "_build_contact_patch",
    "_prepare_grade",
    "_smooth_hand_dynamics",
    "_stroke_terminal_mode",
    "load_pencil_contact_profile",
    "render",
]
