"""Eraser passes lift deposited graphite; they never paint the paper raster."""

from __future__ import annotations

from math import ceil, hypot

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from ..core.ir import Stroke
from ..core.contact_width import profile_from_stroke
from ..core.surface_contact import surface_from_stroke
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


def is_explicit_path_eraser(stroke: Stroke) -> bool:
    ts = _tool_state(stroke)
    return (is_eraser(stroke) and ts.get("path_lift_contract") in {"ordered-graphite-lift-v1", "ordered-graphite-pressure-lift-v1"}
            and ts.get("tool") in {"hard_eraser", "soft_eraser"})


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


def _profiled_footprint(stroke: Stroke, factor: float, bounds: tuple[int, int, int, int], hardness: float) -> np.ndarray:
    """Union of radial pressure-weighted contacts; no per-sample optical accumulation.

    Explicit path and pressure remain authoritative (no automatic hand jitter).
    The contact radius scales with sqrt(pressure), pickup amplitude with pressure.
    Each pass is a max-union, so denser sampling does not multiply lift.
    """
    pts = stroke.points
    pressure = stroke.pressure
    if (pressure is None or len(pressure) != len(pts)
            or any(not np.isfinite(p) or not 0 <= p <= 1 for p in pressure)):
        raise ValueError("invalid profiled eraser pressure")
    steps = [max(1, int(ceil(hypot(b[0]-a[0], b[1]-a[1]) / .5))) for a,b in zip(pts, pts[1:])]
    if sum(steps) + 1 > 100000:
        raise ValueError("pressure-lift sample budget exceeded")
    ox, oy, x1, y1 = bounds
    mask = np.zeros((y1-oy,x1-ox),dtype=np.float32)
    exponent = np.float32(.35 + 1.65*(1-hardness))
    def stamp(x,y,p):
        if p <= 0:
            return
        cx,cy = x*factor-ox,y*factor-oy
        radius = .5*float(stroke.width)*factor*np.sqrt(p)
        if radius <= 0:
            return
        xa,xb=max(0,int(np.floor(cx-radius))),min(mask.shape[1],int(np.ceil(cx+radius))+1)
        ya,yb=max(0,int(np.floor(cy-radius))),min(mask.shape[0],int(np.ceil(cy+radius))+1)
        if xa>=xb or ya>=yb:
            return
        # Preserve the scalar expression and dtype/order of the original
        # contact kernel, but reuse its scratch arrays within bounded row slabs.
        # The mask itself remains the exact max-union of all authored contacts.
        x2 = (np.arange(xa, xb)[None, :] + .5 - cx)**2
        rows = max(1, 262144 // (xb - xa))
        for lo in range(ya, yb, rows):
            hi = min(yb, lo + rows)
            y2 = (np.arange(lo, hi)[:, None] + .5 - cy)**2
            d = x2 + y2
            np.divide(d, radius*radius, out=d)
            np.subtract(1, d, out=d)
            np.maximum(d, 0, out=d)
            contact = d.astype(np.float32)
            np.power(contact, exponent, out=contact)
            np.multiply(np.float32(p), contact, out=contact)
            dst = mask[lo:hi, xa:xb]
            np.maximum(dst, contact, out=dst)
    for i,n in enumerate(steps):
        a,b=pts[i],pts[i+1]
        for j in range(n):
            t=j/n
            stamp(a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t,pressure[i]+(pressure[i+1]-pressure[i])*t)
    stamp(*pts[-1],pressure[-1])
    return np.rint(np.clip(mask,0,1)*255).astype(np.uint8)


def _lift_alpha(alpha: np.ndarray, footprint: np.ndarray, *, stroke: Stroke,
                factor: float, origin: tuple[int, int], tooth: float,
                paper_scale: float, paper_seed: int, profiled: bool = False) -> np.ndarray:
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

    pressure_gain = np.float32(1.0 if profiled else 0.72 + 0.28 * pressure)
    lift = f * np.float32(strength) * pressure_gain * access_tooth * contact
    lift = np.clip(lift, 0.0, 0.985)
    return np.clip(alpha.astype(np.float32) * (np.float32(1.0) - lift), 0.0, 255.0).astype(np.uint8)


def erase(graphite_canvas: Image.Image, stroke: Stroke, *, factor: float,
          hi_size: tuple[int, int], tooth: float, paper_scale: float,
          paper_seed: int, allow_pressure_lift: bool = False) -> tuple[int, int, int, int] | None:
    """Apply one ordered pass in place and return its supersampled bounds."""

    if surface_from_stroke(stroke) is not None:
        raise ValueError("surface contact supports graphite drawing only")
    if profile_from_stroke(stroke) is not None:
        raise ValueError("contact width profile supports graphite drawing only")
    if len(stroke.points) < 2:
        return
    marker = _tool_state(stroke).get("path_lift_contract")
    if marker not in (None, "ordered-graphite-lift-v1", "ordered-graphite-pressure-lift-v1"):
        raise ValueError("unsupported path-lift contract")
    profiled = marker == "ordered-graphite-pressure-lift-v1"
    if profiled and not allow_pressure_lift:
        raise ValueError("pressure-lift stroke requires its explicit renderer contract")
    dynamic = stroke if profiled else eraser_hand_dynamics(stroke)
    _, hardness, _ = _eraser_material(dynamic)
    bounds = _eraser_bounds(dynamic, factor, hi_size, hardness)
    footprint = (Image.fromarray(_profiled_footprint(dynamic, factor, bounds, hardness), mode="L")
                 if profiled else _eraser_footprint(dynamic, factor, bounds, hardness))
    region = graphite_canvas.crop(bounds)
    alpha = np.asarray(region.getchannel("A"), dtype=np.uint8)
    lifted = _lift_alpha(
        alpha, np.asarray(footprint, dtype=np.uint8), stroke=dynamic, factor=factor,
        origin=(bounds[0], bounds[1]), tooth=tooth, paper_scale=paper_scale,
        paper_seed=paper_seed, profiled=profiled,
    )
    region.putalpha(Image.fromarray(lifted, mode="L"))
    graphite_canvas.paste(region, (bounds[0], bounds[1]))
    region.close()
    footprint.close()
    return bounds


__all__ = ["erase", "is_eraser", "is_explicit_path_eraser"]
