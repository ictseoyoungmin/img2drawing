from __future__ import annotations

from copy import deepcopy
from typing import Mapping

from ..core.ir import Stroke, StrokeIR
from .presets import PencilPreset, get_pencil_preset, list_pencil_grades, load_pencil_presets
from . import pillow_paper_interaction as p5

RENDERER_ID = "pillow-pencil-grades-v7"
RENDERER_VERSION = "2"
DEFAULT_SUPERSAMPLE = 8

# Backwards-compatible public alias. Presets are data-driven and loaded from
# img2drawing/data/pencil_presets.json rather than authored inline in renderer logic.
PENCIL_GRADES: Mapping[str, PencilPreset] = load_pencil_presets()


def _clamp01(v: float) -> float:
    return max(0.0, min(1.0, float(v)))


def get_grade(name: str) -> PencilPreset:
    return get_pencil_preset(name)


def grade_names() -> tuple[str, ...]:
    return list_pencil_grades()


def _stroke_grade(stroke: Stroke, global_grade: str | None) -> str | None:
    ts = stroke.tool_state if isinstance(stroke.tool_state, dict) else {}
    local = ts.get("pencil_grade")
    if local is not None:
        return str(local).upper()
    return None if global_grade is None else str(global_grade).upper()


def apply_grade(stroke: Stroke, grade: str) -> Stroke:
    """Return a derived P6 material stroke without mutating authoritative StrokeIR.

    Tool role still owns authored pressure/width/opacity/hand dynamics.  Grade owns the
    graphite core response.  We blend existing role material toward the named core so a
    construction line remains a construction line while still reading as a chosen named grade.
    """
    profile = get_grade(grade)
    out = deepcopy(stroke)
    ts = deepcopy(out.tool_state) if isinstance(out.tool_state, dict) else {}

    base_h = _clamp01(ts.get("hardness", 0.65))
    base_g = _clamp01(ts.get("grain", 0.30))

    # Grade is the dominant material identity; role preset retains a smaller local bias.
    ts["hardness"] = _clamp01(0.30 * base_h + 0.70 * profile.target_hardness)
    ts["grain"] = _clamp01(0.35 * base_g + 0.65 * profile.target_grain)
    ts["pencil_grade"] = profile.name

    # Width represents physical core/paper contact spread, not a screen-space outline.
    out.width = max(0.18, float(out.width) * profile.contact_spread)
    # In the P2 contract opacity is maximum graphite load.  Scaling it here is therefore
    # graphite release at the core, not a post-render alpha filter.
    out.opacity = _clamp01(float(out.opacity) * profile.graphite_release)
    out.tool_state = ts
    return out.cleaned()


def graded_ir(ir: StrokeIR, grade: str | None = None) -> StrokeIR:
    """Derive named-grade material state while preserving page metadata and source IR."""
    out = StrokeIR(int(ir.width), int(ir.height), metadata=deepcopy(ir.metadata))
    for stroke in ir.strokes:
        selected = _stroke_grade(stroke, grade)
        out.add(deepcopy(stroke) if selected is None else apply_grade(stroke, selected))
    return out


def render(
    ir: StrokeIR,
    path: str,
    background=(255, 255, 255, 255),
    *,
    scale: int = 1,
    supersample: int = DEFAULT_SUPERSAMPLE,
    graphite=(36, 34, 32),
    grade: str | None = None,
) -> None:
    """Render P1-P5 material semantics with P6 named pencil-grade response.

    `grade=None` and no per-stroke `tool_state.pencil_grade` delegates exactly to P5.
    A global grade is useful for controlled visual comparisons; per-stroke grade remains
    available for mixed-pencil drawings.  P6 never changes paper relief and never applies
    a final-raster darkness/sharpen/noise filter.
    """
    has_local = any(
        isinstance(s.tool_state, dict) and s.tool_state.get("pencil_grade") is not None
        for s in ir.strokes
    )
    if grade is None and not has_local:
        p5.render(ir, path, background=background, scale=scale, supersample=supersample, graphite=graphite)
        return
    if grade is not None:
        get_grade(grade)  # fail before deriving any output
    derived = graded_ir(ir, grade=grade)
    p5.render(derived, path, background=background, scale=scale, supersample=supersample, graphite=graphite)
