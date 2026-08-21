from __future__ import annotations

import hashlib
import json
from math import ceil, floor, hypot
from typing import Iterable

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter

from ..core.ir import Stroke, StrokeIR
from . import pillow_graphite as p2

RENDERER_ID = "pillow-graphite-grain-v4"
RENDERER_VERSION = "1"
DEFAULT_SUPERSAMPLE = 8
DEFAULT_GRAIN = 0.30
DEFAULT_HARDNESS = 0.65


def _clamp01(v: float) -> float:
    return max(0.0, min(1.0, float(v)))


def _material(stroke: Stroke) -> tuple[float, float]:
    ts = stroke.tool_state if isinstance(stroke.tool_state, dict) else {}
    grain = _clamp01(ts.get("grain", DEFAULT_GRAIN))
    hardness = _clamp01(ts.get("hardness", DEFAULT_HARDNESS))
    return grain, hardness


def material_width(base_width: float, pressure: float, hardness: float) -> float:
    """P2 contact width with a modest core-hardness response.

    A soft core flattens/spreads a little more; a hard core remains slightly narrower.
    P6 will package these primitives into named grades, but P3 activates only the
    material parameter itself.
    """
    h = _clamp01(hardness)
    return max(0.18, p2.graphite_width(base_width, pressure) * (1.08 - 0.16 * h))


def material_deposition(base_opacity: float, pressure: float, hardness: float) -> float:
    """P2 deposition with a restrained hardness-dependent graphite-release factor."""
    h = _clamp01(hardness)
    return _clamp01(p2.graphite_deposition(base_opacity, pressure) * (1.10 - 0.18 * h))


def _pressure_value(stroke: Stroke) -> float:
    if isinstance(stroke.tool_state, dict) and "pressure" in stroke.tool_state:
        return _clamp01(stroke.tool_state["pressure"])
    return 0.55


def _stroke_seed(stroke: Stroke) -> int:
    """Stable material-particle seed independent of grain/hardness values.

    Keeping material values out of the seed means a diagnostic can change grain or
    hardness while observing the *same* latent particle field at a different strength
    or scale.  Explicitly different strokes (IDs/paths/pressure) get different fields.
    """
    payload = {
        "stroke_id": stroke.stroke_id,
        "points": [[float(x), float(y)] for x, y in stroke.points],
        "pressure": None if stroke.pressure is None else [float(v) for v in stroke.pressure],
        "width": float(stroke.width),
        "opacity": float(stroke.opacity),
        "role": stroke.role,
        "part": stroke.part,
        "stage": stroke.stage,
        "layer": int(stroke.layer),
    }
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return int.from_bytes(hashlib.sha256(blob).digest()[:4], "little")


def _hash01(x: np.ndarray, y: np.ndarray, seed: int) -> np.ndarray:
    """Small deterministic integer hash -> float field in [0,1].

    This avoids global RNG state and makes the same StrokeIR replay byte-stably in
    the same renderer environment. Coordinates are canvas-space integer cells.
    """
    xx = np.asarray(x, dtype=np.uint64)
    yy = np.asarray(y, dtype=np.uint64)
    n = (xx * np.uint64(0x9E3779B1) + yy * np.uint64(0x85EBCA77) + np.uint64(seed)) & np.uint64(0xFFFFFFFF)
    n ^= n >> np.uint64(16)
    n = (n * np.uint64(0x7FEB352D)) & np.uint64(0xFFFFFFFF)
    n ^= n >> np.uint64(15)
    n = (n * np.uint64(0x846CA68B)) & np.uint64(0xFFFFFFFF)
    n ^= n >> np.uint64(16)
    return (n & np.uint64(0x00FFFFFF)).astype(np.float32) / np.float32(0x00FFFFFF)


def _stamp(draw: ImageDraw.ImageDraw, xy: tuple[float, float], diameter: float, value: int) -> None:
    r = max(0.5, float(diameter) * 0.5)
    x, y = xy
    draw.ellipse((x - r, y - r, x + r, y + r), fill=int(value))


def _stroke_bounds(stroke: Stroke, factor: float, hardness: float, hi_size: tuple[int, int]) -> tuple[int, int, int, int]:
    pts = [(float(x) * factor, float(y) * factor) for x, y in stroke.points]
    if not pts:
        return (0, 0, 1, 1)
    max_contact = material_width(stroke.width, 1.0, hardness) * factor
    halo = ((1.0 - hardness) ** 1.35) * 0.34 * factor
    margin = max(3.0, max_contact * 0.70 + halo * 2.0 + 3.0)
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    x0 = max(0, int(floor(min(xs) - margin)))
    y0 = max(0, int(floor(min(ys) - margin)))
    x1 = min(hi_size[0], int(ceil(max(xs) + margin)) + 1)
    y1 = min(hi_size[1], int(ceil(max(ys) + margin)) + 1)
    return x0, y0, max(x0 + 1, x1), max(y0 + 1, y1)


def _iter_pressure_samples(stroke: Stroke, factor: float, hardness: float):
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
            yield (
                x,
                y,
                material_width(stroke.width, p, hardness) * factor,
                int(round(material_deposition(stroke.opacity, p, hardness) * 255.0)),
                p,
            )
    x, y = map(float, pts[-1])
    p = float(pressure[-1])
    yield (
        x * factor,
        y * factor,
        material_width(stroke.width, p, hardness) * factor,
        int(round(material_deposition(stroke.opacity, p, hardness) * 255.0)),
        p,
    )


def _render_base_mask_local(
    stroke: Stroke,
    factor: float,
    hardness: float,
    bounds: tuple[int, int, int, int],
) -> Image.Image:
    x0, y0, x1, y1 = bounds
    size = (x1 - x0, y1 - y0)
    mask = Image.new("L", size, 0)
    d = ImageDraw.Draw(mask)

    if stroke.pressure is None or len(stroke.pressure) != len(stroke.points):
        p = _pressure_value(stroke)
        width = material_width(stroke.width, p, hardness) * factor
        alpha = int(round(material_deposition(stroke.opacity, p, hardness) * 255.0))
        pts = [(float(x) * factor - x0, float(y) * factor - y0) for x, y in stroke.points]
        w = max(1, int(round(width)))
        d.line(pts, fill=alpha, width=w, joint="curve")
        _stamp(d, pts[0], width, alpha)
        _stamp(d, pts[-1], width, alpha)
    else:
        samples = list(_iter_pressure_samples(stroke, factor, hardness))
        if not samples:
            return mask
        prev = samples[0]
        _stamp(d, (prev[0] - x0, prev[1] - y0), prev[2], prev[3])
        for cur in samples[1:]:
            width = max(1, int(round((prev[2] + cur[2]) * 0.5)))
            alpha = int(round((prev[3] + cur[3]) * 0.5))
            a = (prev[0] - x0, prev[1] - y0)
            b = (cur[0] - x0, cur[1] - y0)
            d.line([a, b], fill=alpha, width=width)
            _stamp(d, b, (prev[2] + cur[2]) * 0.5, alpha)
            prev = cur

    # Core-hardness affects only the local edge profile. Soft material keeps a small
    # graphite halo; hard material keeps the crisp P2-like core. This is not paper tooth.
    softness = (1.0 - hardness) ** 1.35
    if softness > 0.015:
        radius = softness * 0.34 * factor
        if radius > 0.05:
            halo = mask.filter(ImageFilter.GaussianBlur(radius=radius))
            halo_strength = 0.32 * softness
            table = [int(round(i * halo_strength)) for i in range(256)]
            halo = halo.point(table)
            mask = ImageChops.lighter(mask, halo)
    return mask


def _grain_modulate(
    mask: Image.Image,
    *,
    grain: float,
    hardness: float,
    factor: float,
    global_origin: tuple[int, int],
    seed: int,
) -> Image.Image:
    """Apply deterministic graphite-particle heterogeneity *inside* one stroke.

    The background remains untouched. No final-raster noise is applied.  P5 will later
    introduce a paper-coordinate tooth field; this P3 field is emitted per explicit
    stroke and therefore follows the stroke/material, not the page.
    """
    g = _clamp01(grain)
    if g <= 1e-6:
        return mask

    arr = np.asarray(mask, dtype=np.float32)
    active = arr > 0.5
    if not np.any(active):
        return mask

    h = _clamp01(hardness)
    hh, ww = arr.shape
    oy, ox = int(global_origin[1]), int(global_origin[0])

    # Grain controls both amplitude and particle-cluster scale. Softer graphite is
    # slightly clumpier at the same grain value; harder graphite stays finer/crisper.
    cell_logical = 0.28 + 0.92 * g + 0.16 * (1.0 - h)
    cell_px = max(1, int(round(cell_logical * factor)))
    fine_px = max(1, int(round(cell_px * 0.38)))

    yy, xx = np.indices((hh, ww), dtype=np.int64)
    gx = (xx + ox) // cell_px
    gy = (yy + oy) // cell_px
    fx = (xx + ox) // fine_px
    fy = (yy + oy) // fine_px

    coarse = _hash01(gx, gy, seed)
    fine = _hash01(fx, fy, seed ^ 0xA511E9B3)
    field = coarse * np.float32(0.72) + fine * np.float32(0.28)

    strength = np.float32(0.58 * g)
    mod = np.float32(1.0) + strength * (field - np.float32(0.5)) * np.float32(2.0)

    # A small number of particle clusters deposit weakly. This is stroke-local porosity,
    # not a paper pattern. Keep it restrained so P3 does not pre-empt P5 paper tooth.
    dropout_prob = np.float32(0.075 * g)
    if dropout_prob > 0:
        dropout_field = _hash01(gx, gy, seed ^ 0x63D83595)
        drop = dropout_field < dropout_prob
        drop_factor = np.float32(0.52 + 0.18 * h)
        mod = np.where(drop, mod * drop_factor, mod)

    # Grain should primarily change local texture, not silently become another opacity
    # control. Preserve the mean modulation over the deposited footprint.
    mean_mod = float(np.mean(mod[active]))
    if mean_mod > 1e-6:
        mod = mod / np.float32(mean_mod)
    mod = np.clip(mod, np.float32(0.22), np.float32(1.55))

    out = np.clip(arr * mod, 0.0, 255.0).astype(np.uint8)
    return Image.fromarray(out, mode="L")


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
    """Render explicit StrokeIR with P2 deposition + P3 grain/hardness semantics.

    P3 consumes ONLY existing stroke-local material fields:
      * tool_state.grain     -> particle/deposition heterogeneity inside the stroke
      * tool_state.hardness  -> contact spread, edge profile, graphite release

    Still deliberately absent: hand-path dynamics, paper tooth, named pencil grades,
    eraser material simulation, and any final-raster sketch/noise filter.
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
        grain, hardness = _material(stroke)
        bounds = _stroke_bounds(stroke, factor, hardness, hi_size)
        mask = _render_base_mask_local(stroke, factor, hardness, bounds)
        mask = _grain_modulate(
            mask,
            grain=grain,
            hardness=hardness,
            factor=factor,
            global_origin=(bounds[0], bounds[1]),
            seed=_stroke_seed(stroke),
        )
        layer = _graphite_layer(mask.size, mask, graphite=graphite)
        base.alpha_composite(layer, dest=(bounds[0], bounds[1]))

    final = base.resize(out_size, Image.Resampling.LANCZOS)
    p = str(path)
    if p.lower().endswith((".jpg", ".jpeg")):
        final.convert("RGB").save(p, quality=95)
    else:
        final.save(p)
