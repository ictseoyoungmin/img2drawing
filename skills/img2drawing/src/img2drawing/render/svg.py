from __future__ import annotations
import svgwrite
from ..core.ir import StrokeIR


def _pressure_width(base_width: float, pressure: float) -> float:
    return max(0.25, base_width * (0.28 + 0.90 * max(0.0, min(1.0, pressure))))


def _pressure_opacity(base_opacity: float, pressure: float) -> float:
    p = max(0.0, min(1.0, pressure))
    return max(0.0, min(1.0, base_opacity)) * (0.72 + 0.28 * p)


def render(ir: StrokeIR, path: str, background: str = "white") -> None:
    dwg = svgwrite.Drawing(path, size=(ir.width, ir.height), viewBox=f"0 0 {ir.width} {ir.height}")
    if background != "none":
        dwg.add(dwg.rect(insert=(0,0), size=(ir.width,ir.height), fill=background))
    group = dwg.g(fill="none", stroke="black", stroke_linecap="round", stroke_linejoin="round")
    for s in sorted(ir.strokes, key=lambda z: z.layer):
        pts = [(round(x,2), round(y,2)) for x,y in s.points]
        if len(pts) < 2:
            continue
        # Frozen B2 behavior for old strokes.
        if s.pressure is None or len(s.pressure) != len(pts):
            group.add(dwg.polyline(points=pts, stroke_width=s.width, opacity=s.opacity))
            continue
        # SVG 1.x has no portable pressure-varying polyline width. Approximate deterministically
        # with overlapping round-cap segments. Apply opacity once at the stroke-group level so
        # cap overlap does not create dark mechanical dots at pressure sample boundaries.
        pressure_group = dwg.g(
            fill="none",
            stroke="black",
            stroke_linecap="round",
            stroke_linejoin="round",
            opacity=round(max(0.0, min(1.0, s.opacity)), 4),
        )
        for i in range(len(pts)-1):
            p = (float(s.pressure[i]) + float(s.pressure[i+1])) * 0.5
            pressure_group.add(dwg.line(
                start=pts[i],
                end=pts[i+1],
                stroke_width=round(_pressure_width(s.width, p), 3),
                opacity=1.0,
            ))
        group.add(pressure_group)
    dwg.add(group)
    dwg.save()
