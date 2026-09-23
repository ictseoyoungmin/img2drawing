"""Eraser passes lift deposited graphite; they never paint the paper raster."""

from __future__ import annotations

from math import ceil, hypot

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from ..core.ir import Stroke
from .hand import eraser_hand_dynamics
from .paper import mean_stroke_pressure, paper_field


def _clamp01(v: float) -> float:
    return max(0.0, min(1.0, float(v)))


def _tool_state(stroke: Stroke) -> dict:
    return stroke.tool_state if isinstance(stroke.tool_state, dict) else {}


def is_eraser(stroke: Stroke) -> bool:
    ts = _tool_state(stroke)
    tool = str(ts.get("tool", "")).lower()
    return str(ts.get("mode", "draw")).lower() == "erase" or tool.endswith("eraser")


def _eraser_material(stroke: Stroke) -> tuple[float, float, float]:
    ts = _tool_state(stroke)
    strength = _clamp01(ts.get("erase_strength", stroke.opacity))
    hardness = _clamp01(ts.get("hardness", 0.5))
    grain = _clamp01(ts.get("grain", 0.0))
    return strength, hardness, grain


def _eraser_bounds(stroke: Stroke, factor: float, hi_size: tuple[int, int], hardness: float) -> tuple[int, int, int, int]:
    pts = [(float(x) * factor, float(y) * factor) for x, y in stroke.points]
    if not pts:
        return (0, 0, 1, 1)
    max_width = max(0.5, float(stroke.width) * factor)
    feather = (1.0 - hardness) * 0.26 * max_width
    margin = max_width * 0.62 + feather * 2.5 + 4.0
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    x0 = max(0, int(np.floor(min(xs) - margin)))
    y0 = max(0, int(np.floor(min(ys) - margin)))
    x1 = min(int(hi_size[0]), int(np.ceil(max(xs) + margin)) + 1)
    y1 = min(int(hi_size[1]), int(np.ceil(max(ys) + margin)) + 1)
    return (x0, y0, max(x0 + 1, x1), max(y0 + 1, y1))


def _pressure_samples(stroke: Stroke, factor: float, origin: tuple[int, int]):
    pts = stroke.points
    if len(pts) < 2:
        return []
    if stroke.pressure is not None and len(stroke.pressure) == len(pts):
        pressure = [float(v) for v in stroke.pressure]
    else:
        pressure = [mean_stroke_pressure(stroke)] * len(pts)
    ox, oy = origin
    out = []
    for i in range(len(pts) - 1):
        x0, y0 = map(float, pts[i]); x1, y1 = map(float, pts[i + 1])
        p0, p1 = pressure[i], pressure[i + 1]
        distance = hypot(x1 - x0, y1 - y0)
        steps = max(1, int(ceil(distance / 0.70)))
        for j in range(steps):
            t = j / steps
            p = _clamp01(p0 + (p1 - p0) * t)
            x = (x0 + (x1 - x0) * t) * factor - ox
            y = (y0 + (y1 - y0) * t) * factor - oy
            # Pressure changes eraser contact patch modestly; lift strength is handled separately.
            width = max(0.6, float(stroke.width) * (0.74 + 0.26 * p) * factor)
            out.append((x, y, width))
    p = _clamp01(pressure[-1])
    out.append((float(pts[-1][0]) * factor - ox, float(pts[-1][1]) * factor - oy,
                max(0.6, float(stroke.width) * (0.74 + 0.26 * p) * factor)))
    return out


def _stamp(draw: ImageDraw.ImageDraw, x: float, y: float, diameter: float, value: int = 255) -> None:
    r = max(0.5, float(diameter) * 0.5)
    draw.ellipse((x-r, y-r, x+r, y+r), fill=int(value))


def _eraser_footprint(stroke: Stroke, factor: float, bounds: tuple[int, int, int, int], hardness: float) -> Image.Image:
    w, h = bounds[2] - bounds[0], bounds[3] - bounds[1]
    mask = Image.new("L", (w, h), 0)
    draw = ImageDraw.Draw(mask)
    samples = _pressure_samples(stroke, factor, (bounds[0], bounds[1]))
    if not samples:
        return mask
    prev = samples[0]
    _stamp(draw, prev[0], prev[1], prev[2])
    for cur in samples[1:]:
        width = max(1, int(round((prev[2] + cur[2]) * 0.5)))
        draw.line([(prev[0], prev[1]), (cur[0], cur[1])], fill=255, width=width)
        _stamp(draw, cur[0], cur[1], cur[2])
        prev = cur
    # Soft/kneaded erasers deform at the contact boundary. This is footprint physics,
    # not a final image blur; a hard vinyl eraser keeps an almost binary edge.
    blur_radius = (1.0 - hardness) * 0.13 * max(1.0, float(stroke.width) * factor)
    if blur_radius > 0.35:
        mask = mask.filter(ImageFilter.GaussianBlur(radius=blur_radius))
    return mask


def _lift_alpha(alpha: np.ndarray, footprint: np.ndarray, *, stroke: Stroke,
                factor: float, origin: tuple[int, int], tooth: float,
                paper_scale: float, paper_seed: int) -> np.ndarray:
    """Lift deposited graphite only.

    Soft erasers mostly pick material from exposed paper peaks and leave graphite in
    valleys. Hard erasers reach much deeper and have a firmer edge. Repeated explicit
    passes multiply the remaining material, producing natural cumulative lift.
    """
    if alpha.size == 0 or not np.any(alpha > 0):
        return alpha
    strength, hardness, grain = _eraser_material(stroke)
    if strength <= 1e-12:
        return alpha
    pressure = mean_stroke_pressure(stroke)
    f = np.clip(footprint.astype(np.float32) / np.float32(255.0), 0.0, 1.0)
    if not np.any(f > 1e-6):
        return alpha

    field = paper_field(
        alpha.shape,
        factor=factor,
        global_origin=origin,
        paper_scale=paper_scale,
        paper_seed=paper_seed,
    )
    # Low field = paper valleys. Kneaded rubber preferentially touches the exposed peaks;
    # hard vinyl approaches uniform valley reach.
    soft_access = np.float32(0.30) + np.float32(0.70) * field
    hard_access = np.float32(0.90) + np.float32(0.10) * field
    access_tooth = (np.float32(1.0 - tooth) + np.float32(tooth) *
                    ((np.float32(1.0 - hardness) * soft_access) + np.float32(hardness) * hard_access))

    # A second page-fixed field represents uneven kneaded-rubber contact.
    pickup = paper_field(
        alpha.shape,
        factor=factor,
        global_origin=origin,
        paper_scale=max(0.45, paper_scale * 0.82),
        paper_seed=(int(paper_seed) ^ 0x6D2B79F5) & 0xFFFFFFFF,
    )
    # ToolState.grain becomes rubber-contact irregularity in erase mode.
    irregularity = np.float32(min(0.34, 0.10 + 0.30 * grain + 0.18 * (1.0 - hardness)))
    contact = np.float32(1.0) + irregularity * (pickup - np.float32(0.5)) * np.float32(2.0)
    contact = np.clip(contact, np.float32(0.62), np.float32(1.28))

    pressure_gain = np.float32(0.72 + 0.28 * pressure)
    lift = f * np.float32(strength) * pressure_gain * access_tooth * contact
    lift = np.clip(lift, 0.0, 0.985)
    return np.clip(alpha.astype(np.float32) * (np.float32(1.0) - lift), 0.0, 255.0).astype(np.uint8)


def erase(graphite_canvas: Image.Image, stroke: Stroke, *, factor: float,
          hi_size: tuple[int, int], tooth: float, paper_scale: float,
          paper_seed: int) -> None:
    """Apply one ordered eraser pass to the supersampled graphite canvas in place."""

    if len(stroke.points) < 2:
        return
    dynamic = eraser_hand_dynamics(stroke)
    _, hardness, _ = _eraser_material(dynamic)
    bounds = _eraser_bounds(dynamic, factor, hi_size, hardness)
    footprint = _eraser_footprint(dynamic, factor, bounds, hardness)
    region = graphite_canvas.crop(bounds)
    alpha = np.asarray(region.getchannel("A"), dtype=np.uint8)
    lifted = _lift_alpha(
        alpha, np.asarray(footprint, dtype=np.uint8), stroke=dynamic, factor=factor,
        origin=(bounds[0], bounds[1]), tooth=tooth, paper_scale=paper_scale,
        paper_seed=paper_seed,
    )
    region.putalpha(Image.fromarray(lifted, mode="L"))
    graphite_canvas.paste(region, (bounds[0], bounds[1]))


__all__ = ["erase", "is_eraser"]
