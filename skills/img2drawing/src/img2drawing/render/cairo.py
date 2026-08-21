from __future__ import annotations
from ..core.ir import StrokeIR


def render(ir: StrokeIR, path: str, background=(1,1,1,1)) -> None:
    try:
        import cairo
    except ImportError as e:
        raise RuntimeError("Cairo renderer requires pycairo: pip install img2drawing[cairo]") from e
    surface = cairo.SVGSurface(path, ir.width, ir.height) if path.lower().endswith('.svg') else cairo.ImageSurface(cairo.FORMAT_ARGB32, ir.width, ir.height)
    ctx = cairo.Context(surface)
    ctx.set_source_rgba(*background); ctx.paint()
    ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    for s in sorted(ir.strokes, key=lambda z: z.layer):
        if len(s.points)<2: continue
        ctx.set_source_rgba(0.08,0.08,0.08,s.opacity); ctx.set_line_width(s.width)
        ctx.move_to(*s.points[0])
        for p in s.points[1:]: ctx.line_to(*p)
        ctx.stroke()
    surface.finish()
