from __future__ import annotations

from math import ceil, hypot
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageChops, ImageDraw

from ..core.ir import Stroke, StrokeIR

RENDERER_ID = "pillow-graphite-v3"
RENDERER_VERSION = "1"
DEFAULT_SUPERSAMPLE = 8


def _clamp01(v: float) -> float:
    return max(0.0, min(1.0, float(v)))


def graphite_width(base_width: float, pressure: float) -> float:
    """Pressure changes contact width only modestly.

    P2 deliberately moves pressure expression away from mostly-width and toward
    graphite deposition. P3+ will add hardness/grain/paper interaction.
    """
    p = _clamp01(pressure)
    return max(0.20, float(base_width) * (0.72 + 0.28 * p))


def graphite_deposition(base_opacity: float, pressure: float) -> float:
    """Return deposited graphite coverage in [0,1].

    The curve is intentionally nonlinear: light touches leave little graphite,
    while firm pressure deposits much more material. `opacity` is the tool's
    maximum graphite load, not a post-render filter opacity.
    """
    p = _clamp01(pressure)
    load = 0.055 + 0.945 * (p ** 1.55)
    return _clamp01(base_opacity) * load


def _scaled_points(points: Iterable[tuple[float, float]], factor: float) -> list[tuple[float, float]]:
    return [(float(x) * factor, float(y) * factor) for x, y in points]


def _stamp(draw: ImageDraw.ImageDraw, xy: tuple[float, float], diameter: float, value: int) -> None:
    r = max(0.5, diameter * 0.5)
    x, y = xy
    draw.ellipse((x-r, y-r, x+r, y+r), fill=int(value))


def _segment_mask(size: tuple[int, int], a, b, width: float, alpha: int) -> Image.Image:
    mask = Image.new("L", size, 0)
    d = ImageDraw.Draw(mask)
    w = max(1, int(round(width)))
    d.line([a, b], fill=int(alpha), width=w)
    _stamp(d, a, width, alpha)
    _stamp(d, b, width, alpha)
    return mask


def _iter_pressure_samples(stroke: Stroke, factor: float):
    pts = stroke.points
    pressure = stroke.pressure or []
    for i in range(len(pts) - 1):
        x0, y0 = map(float, pts[i])
        x1, y1 = map(float, pts[i + 1])
        p0 = float(pressure[i])
        p1 = float(pressure[i + 1])
        distance = hypot(x1 - x0, y1 - y0)
        steps = max(1, int(ceil(distance / 0.45)))
        for j in range(steps):
            t = j / steps
            x = (x0 + (x1 - x0) * t) * factor
            y = (y0 + (y1 - y0) * t) * factor
            p = p0 + (p1 - p0) * t
            width = graphite_width(stroke.width, p) * factor
            alpha = int(round(graphite_deposition(stroke.opacity, p) * 255.0))
            yield x, y, width, alpha, p
    x, y = map(float, pts[-1])
    p = float(pressure[-1])
    yield (
        x * factor,
        y * factor,
        graphite_width(stroke.width, p) * factor,
        int(round(graphite_deposition(stroke.opacity, p) * 255.0)),
        p,
    )


def _pressureless_value(stroke: Stroke) -> tuple[float, int]:
    # New renderer semantics only. Pressure-less legacy data gets a neutral touch;
    # no attempt is made to mutate or reinterpret the frozen legacy renderer.
    if isinstance(stroke.tool_state, dict) and "pressure" in stroke.tool_state:
        p = _clamp01(stroke.tool_state["pressure"])
    else:
        p = 0.55
    return graphite_width(stroke.width, p), int(round(graphite_deposition(stroke.opacity, p) * 255.0))


def _render_stroke_deposition_mask(size: tuple[int, int], stroke: Stroke, factor: float) -> Image.Image:
    """Rasterize one stroke's deposited graphite coverage.

    Dense segments are written directly into one grayscale deposition mask. Pillow's
    grayscale drawing replaces coverage instead of alpha-compositing it, so dense
    sampling does not manufacture dark join dots. Separate explicit strokes are
    composited later and therefore still accumulate graphite.
    """
    mask = Image.new("L", size, 0)
    d = ImageDraw.Draw(mask)
    if stroke.pressure is None or len(stroke.pressure) != len(stroke.points):
        pts = _scaled_points(stroke.points, factor)
        width, alpha = _pressureless_value(stroke)
        w = max(1, int(round(width * factor)))
        d.line(pts, fill=alpha, width=w, joint="curve")
        _stamp(d, pts[0], w, alpha)
        _stamp(d, pts[-1], w, alpha)
        return mask

    samples = list(_iter_pressure_samples(stroke, factor))
    if not samples:
        return mask
    prev = samples[0]
    _stamp(d, (prev[0], prev[1]), prev[2], prev[3])
    for cur in samples[1:]:
        width = max(1, int(round((prev[2] + cur[2]) * 0.5)))
        alpha = int(round((prev[3] + cur[3]) * 0.5))
        d.line([(prev[0], prev[1]), (cur[0], cur[1])], fill=alpha, width=width)
        # Only stamp at the current sample; direct grayscale writes avoid alpha buildup.
        _stamp(d, (cur[0], cur[1]), (prev[2] + cur[2]) * 0.5, alpha)
        prev = cur
    return mask


def _graphite_layer(size: tuple[int, int], mask: Image.Image, graphite=(36, 34, 32)) -> Image.Image:
    layer = Image.new("RGBA", size, (int(graphite[0]), int(graphite[1]), int(graphite[2]), 0))
    layer.putalpha(mask)
    return layer


def render(
    ir: StrokeIR,
    path: str,
    background=(255, 255, 255, 255),
    *,
    scale: int = 1,
    supersample: int = DEFAULT_SUPERSAMPLE,
    graphite=(36, 34, 32),
) -> None:
    """Render explicit StrokeIR as smooth graphite deposition.

    P2 scope:
      * supersampled subpixel geometry from P1
      * pressure-driven graphite deposition
      * explicit-stroke accumulation

    Deliberately NOT consumed yet: tool_state.grain, tool_state.hardness,
    paper tooth, pencil grade, hand jitter. Those belong to later slices.
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
        mask = _render_stroke_deposition_mask(hi_size, stroke, factor)
        # Separate explicit strokes alpha-composite naturally, so repeated passes
        # deposit additional graphite instead of merely replacing prior darkness.
        base = Image.alpha_composite(base, _graphite_layer(hi_size, mask, graphite=graphite))

    final = base.resize(out_size, Image.Resampling.LANCZOS)
    p = str(path)
    if p.lower().endswith((".jpg", ".jpeg")):
        final.convert("RGB").save(p, quality=95)
    else:
        final.save(p)
