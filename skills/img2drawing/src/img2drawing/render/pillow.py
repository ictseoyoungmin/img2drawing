from __future__ import annotations
from PIL import Image, ImageDraw
from ..core.ir import StrokeIR


def _pressure_width(base_width: float, pressure: float) -> float:
    # Keep even a very light touch visible while letting pressure materially change width.
    return max(0.25, base_width * (0.28 + 0.90 * max(0.0, min(1.0, pressure))))


def _pressure_alpha(base_opacity: float, pressure: float) -> int:
    p = max(0.0, min(1.0, pressure))
    # Pencil-like light touch is also a little paler. This is derived from explicit pressure,
    # not a post-process applied to the final raster.
    opacity = max(0.0, min(1.0, base_opacity)) * (0.72 + 0.28 * p)
    return int(round(opacity * 255))


def render_image(ir: StrokeIR, background=(255,255,255,255), scale: int = 1) -> Image.Image:
    """Render the frozen Pillow stroke path to an in-memory image.

    `render()` remains the file API.  Debug/replay tooling can use this helper to avoid
    a PNG write→reopen cycle for every history cursor.
    """
    im = Image.new("RGBA", (ir.width*scale, ir.height*scale), background)
    draw = ImageDraw.Draw(im, "RGBA")
    for s in sorted(ir.strokes, key=lambda z: z.layer):
        pts = [(int(round(x*scale)), int(round(y*scale))) for x,y in s.points]
        if len(pts) < 2:
            continue
        if s.pressure is None or len(s.pressure) != len(pts):
            alpha = int(max(0,min(1,s.opacity))*255)
            draw.line(pts, fill=(20,20,20,alpha), width=max(1,int(round(s.width*scale))), joint="curve")
            continue
        for i in range(len(pts)-1):
            p = (float(s.pressure[i]) + float(s.pressure[i+1])) * 0.5
            width = max(1, int(round(_pressure_width(s.width, p) * scale)))
            alpha = _pressure_alpha(s.opacity, p)
            draw.line([pts[i], pts[i+1]], fill=(20,20,20,alpha), width=width)
            r = width / 2.0
            x2,y2 = pts[i+1]
            draw.ellipse((x2-r, y2-r, x2+r, y2+r), fill=(20,20,20,alpha))
    return im


def render(ir: StrokeIR, path: str, background=(255,255,255,255), scale: int = 1) -> None:
    im = render_image(ir, background=background, scale=scale)
    if path.lower().endswith((".jpg", ".jpeg")):
        im.convert("RGB").save(path, quality=95)
    else:
        im.save(path)
