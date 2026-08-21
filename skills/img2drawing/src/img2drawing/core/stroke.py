from __future__ import annotations
import numpy as np
from .ir import Stroke
from .tools import ToolState


def polyline_stroke(points, *, width=1.5, opacity=1.0, role="structure", confidence=1.0, layer=0,
                    pressure=None, tool_state=None, part=None, stage=None):
    pts = [(float(x), float(y)) for x, y in points]
    ts = tool_state.to_dict() if isinstance(tool_state, ToolState) else tool_state
    return Stroke(
        pts,
        width=width,
        opacity=opacity,
        role=role,
        confidence=confidence,
        layer=layer,
        pressure=pressure,
        tool_state=ts,
        part=part,
        stage=stage,
    )


def pressure_profile(n: int, floor: float = 0.45) -> list[float]:
    if n <= 1:
        return [1.0] * n
    t = np.linspace(0, 1, n)
    # taper at ends, slightly imperfect center weight
    p = floor + (1 - floor) * np.sin(np.pi * t) ** 0.7
    p *= 0.96 + 0.04 * np.sin(7.0 * np.pi * t)
    return np.clip(p, 0.15, 1.0).tolist()


def shaped_pressure_profile(
    n: int,
    *,
    start: float = 0.18,
    peak: float = 0.78,
    end: float = 0.14,
    peak_at: float = 0.54,
    wobble: float = 0.025,
) -> list[float]:
    """A deterministic hand-like pressure curve stored as explicit path samples."""
    if n <= 0:
        return []
    if n == 1:
        return [max(0.0, min(1.0, peak))]
    t = np.linspace(0.0, 1.0, n)
    values = np.empty(n, dtype=float)
    for i, u in enumerate(t):
        if u <= peak_at:
            local = u / max(peak_at, 1e-6)
            # smoother than a linear ramp; avoids a mechanical triangular profile.
            ease = local * local * (3.0 - 2.0 * local)
            v = start + (peak - start) * ease
        else:
            local = (u - peak_at) / max(1.0 - peak_at, 1e-6)
            ease = local * local * (3.0 - 2.0 * local)
            v = peak + (end - peak) * ease
        if 0.04 < u < 0.96:
            v += wobble * np.sin(5.0 * np.pi * u) * np.sin(np.pi * u)
        values[i] = v
    return np.clip(values, 0.04, 1.0).tolist()


def tool_stroke(points, tool: ToolState, *, pressure=None, role="form", part=None, stage="A1_tool_proof", layer=0):
    tool = tool.validated()
    pts = [(float(x), float(y)) for x, y in points]
    if pressure is None:
        pressure = shaped_pressure_profile(
            len(pts),
            start=max(0.05, tool.pressure * (0.25 + 0.20 * (1.0 - tool.taper_in))),
            peak=min(1.0, tool.pressure * 1.18),
            end=max(0.04, tool.pressure * (0.20 + 0.20 * (1.0 - tool.taper_out))),
        )
    return Stroke(
        pts,
        width=tool.width,
        opacity=tool.opacity,
        role=role,
        confidence=1.0,
        layer=layer,
        pressure=pressure,
        tool_state=tool.to_dict(),
        part=part,
        stage=stage,
    )
