from __future__ import annotations

from math import ceil, hypot
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw

from ..core.ir import Stroke, StrokeIR

RENDERER_ID = "pillow-subpixel-v2"
RENDERER_VERSION = "1"
DEFAULT_SUPERSAMPLE = 4


def _clamp01(v: float) -> float:
    return max(0.0, min(1.0, float(v)))


def _pressure_width(base_width: float, pressure: float) -> float:
    """Same logical pressure-to-width contract as pillow-pressure-v1, but remains float."""
    return max(0.25, float(base_width) * (0.28 + 0.90 * _clamp01(pressure)))


def _pressure_alpha(base_opacity: float, pressure: float) -> int:
    p = _clamp01(pressure)
    opacity = _clamp01(base_opacity) * (0.72 + 0.28 * p)
    return int(round(opacity * 255.0))


def _scaled_points(points: Iterable[tuple[float, float]], factor: float) -> list[tuple[float, float]]:
    # Keep subpixel coordinates as floats until Pillow's high-resolution raster boundary.
    return [(float(x) * factor, float(y) * factor) for x, y in points]


def _stamp(draw: ImageDraw.ImageDraw, xy: tuple[float, float], diameter: float, value: int) -> None:
    r = max(0.5, diameter * 0.5)
    x, y = xy
    draw.ellipse((x-r, y-r, x+r, y+r), fill=int(value))


def _render_pressureless_mask(size: tuple[int, int], stroke: Stroke, factor: float) -> Image.Image:
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    pts = _scaled_points(stroke.points, factor)
    width = max(1, int(round(max(0.10, float(stroke.width)) * factor)))
    alpha = int(round(_clamp01(stroke.opacity) * 255.0))
    draw.line(pts, fill=alpha, width=width, joint="curve")
    # Explicit round caps make short construction marks behave consistently across Pillow versions.
    _stamp(draw, pts[0], width, alpha)
    _stamp(draw, pts[-1], width, alpha)
    return mask


def _iter_pressure_samples(stroke: Stroke, factor: float):
    """Yield densely sampled (x, y, width_px, alpha) values with interpolated pressure.

    The source StrokeIR remains untouched.  Dense sampling exists only at the raster boundary so
    pressure tapers do not jump from one sparse path vertex to the next.
    """
    pts = stroke.points
    pressure = stroke.pressure or []
    for i in range(len(pts) - 1):
        x0, y0 = map(float, pts[i])
        x1, y1 = map(float, pts[i + 1])
        p0 = float(pressure[i])
        p1 = float(pressure[i + 1])
        distance = hypot(x1 - x0, y1 - y0)
        # <= 0.45 logical px between samples. This is intentionally tied to logical space,
        # not the supersample factor, so 4x and 8x preserve the same stroke semantics.
        steps = max(1, int(ceil(distance / 0.45)))
        for j in range(steps):
            t = j / steps
            x = (x0 + (x1 - x0) * t) * factor
            y = (y0 + (y1 - y0) * t) * factor
            p = p0 + (p1 - p0) * t
            width = _pressure_width(stroke.width, p) * factor
            alpha = _pressure_alpha(stroke.opacity, p)
            yield x, y, width, alpha
    x, y = map(float, pts[-1])
    p = float(pressure[-1])
    yield x * factor, y * factor, _pressure_width(stroke.width, p) * factor, _pressure_alpha(stroke.opacity, p)


def _render_pressure_mask(size: tuple[int, int], stroke: Stroke, factor: float) -> Image.Image:
    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    samples = list(_iter_pressure_samples(stroke, factor))
    if not samples:
        return mask

    # Draw densely connected samples into one coverage mask. Because the mask stores coverage
    # directly rather than alpha-compositing many round-cap segments, joins do not accumulate
    # into the mechanical dark dots that motivated the earlier A1 SVG correction.
    prev = samples[0]
    _stamp(draw, (prev[0], prev[1]), prev[2], prev[3])
    for cur in samples[1:]:
        width = max(1, int(round((prev[2] + cur[2]) * 0.5)))
        alpha = int(round((prev[3] + cur[3]) * 0.5))
        draw.line([(prev[0], prev[1]), (cur[0], cur[1])], fill=alpha, width=width)
        _stamp(draw, (cur[0], cur[1]), cur[2], cur[3])
        prev = cur
    return mask


def _ink_layer(size: tuple[int, int], mask: Image.Image, ink=(20, 20, 20)) -> Image.Image:
    layer = Image.new("RGBA", size, (int(ink[0]), int(ink[1]), int(ink[2]), 0))
    layer.putalpha(mask)
    return layer


def render(
    ir: StrokeIR,
    path: str,
    background=(255, 255, 255, 255),
    *,
    scale: int = 1,
    supersample: int = DEFAULT_SUPERSAMPLE,
    ink=(20, 20, 20),
) -> None:
    """Render StrokeIR with a supersampled subpixel raster path.

    This renderer is intentionally separate from `renderer.pillow` so all accepted v1 replay
    artifacts remain frozen.  `scale` controls requested output size; `supersample` is an internal
    raster quality factor and does not change the logical canvas dimensions.
    """
    if int(scale) != scale or scale < 1:
        raise ValueError("scale must be a positive integer")
    if int(supersample) != supersample or supersample < 2:
        raise ValueError("supersample must be an integer >= 2")
    scale = int(scale)
    supersample = int(supersample)
    factor = float(scale * supersample)
    hi_size = (int(ir.width * factor), int(ir.height * factor))
    out_size = (ir.width * scale, ir.height * scale)

    base = Image.new("RGBA", hi_size, background)
    for stroke in sorted(ir.strokes, key=lambda z: z.layer):
        if len(stroke.points) < 2:
            continue
        if stroke.pressure is None or len(stroke.pressure) != len(stroke.points):
            mask = _render_pressureless_mask(hi_size, stroke, factor)
        else:
            mask = _render_pressure_mask(hi_size, stroke, factor)
        base = Image.alpha_composite(base, _ink_layer(hi_size, mask, ink=ink))

    # LANCZOS integrates high-resolution coverage into subpixel edge intensity.
    final = base.resize(out_size, Image.Resampling.LANCZOS)
    p = str(path)
    if p.lower().endswith((".jpg", ".jpeg")):
        final.convert("RGB").save(p, quality=95)
    else:
        final.save(p)
