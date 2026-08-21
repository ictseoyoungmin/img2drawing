from __future__ import annotations
from copy import deepcopy
from dataclasses import dataclass
from statistics import mean
from ..core.ir import StrokeIR

@dataclass(frozen=True)
class LineWeightProfile:
    reference_part: str
    reference_width: float
    reference_pressure_mean: float
    reference_opacity: float
    major_width_ratio: float = 0.95
    major_pressure_ratio: float = 0.90
    major_opacity_ratio: float = 0.90
    minor_width_ratio: float = 0.80
    minor_pressure_ratio: float = 0.72
    minor_opacity_ratio: float = 0.72

def _pmean(stroke):
    if stroke.pressure:
        return mean(float(x) for x in stroke.pressure)
    if stroke.tool_state and stroke.tool_state.get("pressure") is not None:
        return float(stroke.tool_state["pressure"])
    return 0.0

def profile_from_reference(ir: StrokeIR, reference_part: str) -> LineWeightProfile:
    ref=next((s for s in ir.strokes if s.part==reference_part),None)
    if ref is None:
        raise ValueError(f"reference stroke part not found: {reference_part}")
    return LineWeightProfile(
        reference_part=reference_part,
        reference_width=float(ref.width),
        reference_pressure_mean=_pmean(ref),
        reference_opacity=float(ref.opacity),
    )

def calibrate_line_weight(
    ir: StrokeIR,
    *,
    reference_part: str,
    major_roles=("gesture","axis","mass"),
    minor_roles=("construction","cross_contour"),
    preserve_reference=True,
) -> tuple[StrokeIR, LineWeightProfile]:
    """Raise the average visual weight of structural strokes toward one reference.

    This is a mechanical reweighting utility only. It does not infer anatomy or
    decide which geometry is correct.

    Per-point pressure modulation is preserved by scaling each stroke's existing
    pressure curve to a new target mean, rather than flattening pressure values.
    """
    out=deepcopy(ir)
    prof=profile_from_reference(out,reference_part)

    for s in out.strokes:
        if preserve_reference and s.part==reference_part:
            continue

        if s.role in major_roles:
            wr,pr,orr=prof.major_width_ratio,prof.major_pressure_ratio,prof.major_opacity_ratio
        elif s.role in minor_roles:
            wr,pr,orr=prof.minor_width_ratio,prof.minor_pressure_ratio,prof.minor_opacity_ratio
        else:
            continue

        s.width=max(float(s.width),prof.reference_width*wr)
        s.opacity=max(float(s.opacity),min(1.0,prof.reference_opacity*orr))

        target=prof.reference_pressure_mean*pr
        if s.pressure:
            old=mean(float(x) for x in s.pressure)
            if old>1e-8:
                scale=target/old
                s.pressure=[max(0.0,min(1.0,float(x)*scale)) for x in s.pressure]
        if s.tool_state is not None:
            ts=dict(s.tool_state)
            ts["width"]=float(s.width)
            ts["opacity"]=float(s.opacity)
            ts["pressure"]=target
            ts["line_weight_calibration"]={
                "reference_part":reference_part,
                "pressure_curve_preserved":True,
            }
            s.tool_state=ts
    out.metadata=dict(out.metadata)
    out.metadata["line_weight_calibration"]={
        "reference_part":reference_part,
        "major_width_ratio":prof.major_width_ratio,
        "major_pressure_ratio":prof.major_pressure_ratio,
        "minor_width_ratio":prof.minor_width_ratio,
        "minor_pressure_ratio":prof.minor_pressure_ratio,
        "pressure_curve_preserved":True,
    }
    return out,prof
