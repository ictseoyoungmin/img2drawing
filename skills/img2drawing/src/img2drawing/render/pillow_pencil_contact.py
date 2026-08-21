from __future__ import annotations

from copy import deepcopy
from math import pi
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter

from ..core.ir import Stroke, StrokeIR
from .contact_profile import PencilContactProfile, load_pencil_contact_profile
from . import pillow_graphite_grain as p3
from . import pillow_hand_dynamics as p4
from . import pillow_paper_interaction as p5
from . import pillow_pencil_grades as p6
from . import pillow_eraser_material as p7

RENDERER_ID = "pillow-pencil-contact-v9"
RENDERER_VERSION = "1"
DEFAULT_SUPERSAMPLE = 4
HIGH_QUALITY_SUPERSAMPLE = 8


def _clamp01(v: float) -> float:
    return max(0.0, min(1.0, float(v)))


def _selected_grade(stroke: Stroke, global_grade: str | None) -> str | None:
    ts = stroke.tool_state if isinstance(stroke.tool_state, dict) else {}
    local = ts.get("pencil_grade")
    if local is not None:
        return str(local).upper()
    return None if global_grade is None else str(global_grade).upper()


def _prepare_grade(stroke: Stroke, global_grade: str | None) -> Stroke:
    grade = _selected_grade(stroke, global_grade)
    return deepcopy(stroke) if grade is None else p6.apply_grade(stroke, grade)


def _smooth_hand_dynamics(stroke: Stroke, profile: PencilContactProfile) -> Stroke:
    """P4-compatible path wobble with continuous pressure variation, not micro-breaks."""
    jitter, taper_in, taper_out = p4._dynamics(stroke)
    if jitter <= 1e-12 and taper_in <= 1e-12 and taper_out <= 1e-12:
        return deepcopy(stroke)

    pts, pressure, t = p4._resample(stroke, spacing=profile.trajectory_spacing)
    if len(pts) < 2:
        return deepcopy(stroke)

    tangent = np.empty_like(pts)
    tangent[0] = pts[1] - pts[0]
    tangent[-1] = pts[-1] - pts[-2]
    if len(pts) > 2:
        tangent[1:-1] = pts[2:] - pts[:-2]
    norm = np.linalg.norm(tangent, axis=1)
    norm[norm < 1e-9] = 1.0
    tangent /= norm[:, None]
    normal = np.column_stack([-tangent[:, 1], tangent[:, 0]])

    seed = p4._stable_seed(stroke)
    wave = p4._hand_wave(t, seed)
    end_anchor = np.sin(pi * t) ** 0.78
    amp = min(1.35, (0.42 + 0.14 * min(float(stroke.width), 5.0)) * np.sqrt(jitter))
    moved = pts + normal * (amp * end_anchor * wave)[:, None]
    moved[0] = pts[0]
    moved[-1] = pts[-1]

    hp = profile.hand
    entry = p4._smoothstep(t / hp.tip_span)
    release = p4._smoothstep((1.0 - t) / hp.tip_span)
    tip_factor = (
        1.0 - hp.taper_in_strength * taper_in * (1.0 - entry)
    ) * (
        1.0 - hp.taper_out_strength * taper_out * (1.0 - release)
    )

    # Smooth, zero-centered cadence: graphite density breathes without creating abrupt
    # pressure holes. This intentionally replaces P4's legacy micro-break cadence only in P9.
    phase = 2.0 * pi * p4._seed_unit(seed ^ 0xB5297A4D, 12)
    freq = hp.pressure_cadence_frequency_min + hp.pressure_cadence_frequency_span * p4._seed_unit(seed, 28)
    cadence = 1.0 + hp.pressure_cadence_strength * np.sqrt(jitter) * np.sin(2.0 * pi * freq * t + phase)
    dyn_pressure = np.clip(pressure * tip_factor * cadence, 0.025, 1.0)

    out = deepcopy(stroke)
    out.points = [(float(x), float(y)) for x, y in moved]
    out.pressure = [float(v) for v in dyn_pressure]
    return out.cleaned()


def _contact_width(base_width: float, pressure: float, hardness: float, profile: PencilContactProfile) -> float:
    m = profile.material
    p = _clamp01(pressure)
    h = _clamp01(hardness)
    pressure_width = float(base_width) * (m.width_base + m.width_pressure_gain * p)
    return max(m.min_width, pressure_width * (1.08 - 0.16 * h))


def _contact_deposition(base_opacity: float, pressure: float, hardness: float, profile: PencilContactProfile) -> float:
    m = profile.material
    p = _clamp01(pressure)
    h = _clamp01(hardness)
    load = m.deposition_floor + (1.0 - m.deposition_floor) * (p ** m.deposition_exponent)
    hardness_release = 1.10 - 0.18 * h
    return _clamp01(float(base_opacity) * load * hardness_release)


def _contact_bounds(stroke: Stroke, factor: float, hardness: float, hi_size: tuple[int, int], profile: PencilContactProfile) -> tuple[int, int, int, int]:
    pts = [(float(x) * factor, float(y) * factor) for x, y in stroke.points]
    if not pts:
        return (0, 0, 1, 1)
    max_contact = _contact_width(stroke.width, 1.0, hardness, profile) * factor
    softness = (1.0 - hardness) ** 1.35
    halo = softness * profile.edge.soft_halo_radius * factor
    margin = max(3.0, max_contact * 0.70 + halo * 2.0 + 3.0)
    xs = [q[0] for q in pts]; ys = [q[1] for q in pts]
    x0 = max(0, int(np.floor(min(xs) - margin)))
    y0 = max(0, int(np.floor(min(ys) - margin)))
    x1 = min(int(hi_size[0]), int(np.ceil(max(xs) + margin)) + 1)
    y1 = min(int(hi_size[1]), int(np.ceil(max(ys) + margin)) + 1)
    return (x0, y0, max(x0 + 1, x1), max(y0 + 1, y1))


def _pressure_samples(stroke: Stroke, factor: float, hardness: float, spacing: float, profile: PencilContactProfile):
    pts = np.asarray(stroke.points, dtype=np.float64)
    if len(pts) < 2:
        return []
    seg = np.linalg.norm(np.diff(pts, axis=0), axis=1)
    cumulative = np.concatenate([[0.0], np.cumsum(seg)])
    total = float(cumulative[-1])
    if total <= 1e-9:
        return []
    count = max(2, int(np.ceil(total / max(0.18, float(spacing)))) + 1)
    s = np.linspace(0.0, total, count)
    x = np.interp(s, cumulative, pts[:, 0])
    y = np.interp(s, cumulative, pts[:, 1])
    if stroke.pressure is not None and len(stroke.pressure) == len(stroke.points):
        src_p = np.asarray(stroke.pressure, dtype=np.float64)
    else:
        ts = stroke.tool_state if isinstance(stroke.tool_state, dict) else {}
        src_p = np.full(len(stroke.points), _clamp01(ts.get("pressure", 0.55)), dtype=np.float64)
    p = np.interp(s, cumulative, src_p)
    out = []
    for xx, yy, pp in zip(x, y, p):
        pp = _clamp01(pp)
        out.append((
            float(xx) * factor,
            float(yy) * factor,
            _contact_width(stroke.width, pp, hardness, profile) * factor,
            int(round(_contact_deposition(stroke.opacity, pp, hardness, profile) * 255.0)),
            pp,
        ))
    return out


def _continuous_contact_mask(
    stroke: Stroke,
    factor: float,
    hardness: float,
    bounds: tuple[int, int, int, int],
    profile: PencilContactProfile,
) -> Image.Image:
    """Rasterize one continuous contact path without per-sample circular stamps."""
    x0, y0, x1, y1 = bounds
    mask = Image.new("L", (x1 - x0, y1 - y0), 0)
    samples = _pressure_samples(stroke, factor, hardness, profile.trajectory_spacing, profile)
    if len(samples) < 2:
        return mask

    segments = []
    for prev, cur in zip(samples, samples[1:]):
        width = max(1, int(round((prev[2] + cur[2]) * 0.5)))
        alpha = int(round((prev[3] + cur[3]) * 0.5))
        segments.append((alpha, width, (prev[0] - x0, prev[1] - y0), (cur[0] - x0, cur[1] - y0)))

    # Draw lower-deposition spans first so overlap at joins keeps the stronger local
    # deposition rather than repeatedly accumulating or stamping circular beads.
    d = ImageDraw.Draw(mask)
    for alpha, width, a, b in sorted(segments, key=lambda row: row[0]):
        d.line([a, b], fill=alpha, width=width)

    softness = (1.0 - hardness) ** 1.35
    radius = softness * profile.edge.soft_halo_radius * factor
    if radius > 0.05 and profile.edge.soft_halo_strength > 1e-6:
        halo = mask.filter(ImageFilter.GaussianBlur(radius=radius))
        halo = halo.point([int(round(i * profile.edge.soft_halo_strength * softness)) for i in range(256)])
        mask = ImageChops.lighter(mask, halo)
    return mask




def _continuity_floor_mask(
    stroke: Stroke,
    factor: float,
    hardness: float,
    bounds: tuple[int, int, int, int],
    profile: PencilContactProfile,
) -> Image.Image:
    x0, y0, x1, y1 = bounds
    mask = Image.new("L", (x1 - x0, y1 - y0), 0)
    samples = _pressure_samples(stroke, factor, hardness, profile.trajectory_spacing, profile)
    if len(samples) < 2:
        return mask
    pts = [(s[0] - x0, s[1] - y0) for s in samples]
    min_width = max(1, int(round(min(s[2] for s in samples))))
    min_alpha = min(s[3] for s in samples)
    m = profile.material
    alpha = max(int(round(m.continuity_min_coverage * 255.0)), int(round(min_alpha * m.continuity_floor_ratio)))
    d = ImageDraw.Draw(mask)
    d.line(pts, fill=alpha, width=min_width, joint="curve")
    return mask


def _thin_texture_gain(width_logical: float, reference: float, floor: float) -> float:
    if reference <= 1e-9:
        return 1.0
    u = np.clip(float(width_logical) / float(reference), 0.0, 1.0)
    # Smoothstep avoids a visible threshold where a stroke crosses the protection width.
    s = float(u * u * (3.0 - 2.0 * u))
    return float(floor + (1.0 - floor) * s)


def _mean_contact_width(stroke: Stroke, hardness: float, profile: PencilContactProfile) -> float:
    if stroke.pressure is not None and len(stroke.pressure) == len(stroke.points) and stroke.pressure:
        pressure = float(np.mean(np.asarray(stroke.pressure, dtype=np.float32)))
    else:
        ts = stroke.tool_state if isinstance(stroke.tool_state, dict) else {}
        pressure = _clamp01(ts.get("pressure", 0.55))
    return _contact_width(stroke.width, pressure, hardness, profile)


def _smooth_grain_modulate(
    mask: Image.Image,
    *,
    stroke: Stroke,
    grain: float,
    hardness: float,
    factor: float,
    global_origin: tuple[int, int],
    seed: int,
    profile: PencilContactProfile,
) -> Image.Image:
    """Continuous correlated grain modulation; never removes isolated pixels."""
    g = _clamp01(grain)
    if g <= 1e-8:
        return mask
    arr = np.asarray(mask, dtype=np.float32)
    active = arr > 0.5
    if not np.any(active):
        return mask

    hh, ww = arr.shape
    oy, ox = int(global_origin[1]), int(global_origin[0])
    yy, xx = np.indices((hh, ww), dtype=np.float64)
    lx = (xx + float(ox)) / float(factor)
    ly = (yy + float(oy)) / float(factor)

    gp = profile.grain
    coarse = p5._value_noise(lx, ly, gp.coarse_cell, seed ^ 0xA511E9B3)
    fine = p5._value_noise(lx, ly, gp.fine_cell, seed ^ 0x63D83595)
    field = np.float32(0.72) * coarse + np.float32(0.28) * fine

    width = _mean_contact_width(stroke, hardness, profile)
    thin_gain = _thin_texture_gain(width, gp.thin_width_reference, gp.thin_texture_floor)
    strength = np.float32(gp.strength * g * thin_gain)
    mod = np.float32(1.0) + strength * (field - np.float32(0.5)) * np.float32(2.0)

    mean_mod = float(np.mean(mod[active]))
    if mean_mod > 1e-6:
        mod = mod / np.float32(mean_mod)
    mod = np.clip(mod, np.float32(gp.min_modulation), np.float32(gp.max_modulation))
    out = np.clip(arr * mod, 0.0, 255.0).astype(np.uint8)
    return Image.fromarray(out, mode="L")


def _smooth_paper_modulate(
    mask: Image.Image,
    *,
    stroke: Stroke,
    tooth: float,
    paper_scale: float,
    paper_seed: int,
    factor: float,
    global_origin: tuple[int, int],
    hardness: float,
    profile: PencilContactProfile,
) -> Image.Image:
    """Page-fixed tooth with smooth valley attenuation and thin-line protection."""
    t = _clamp01(tooth)
    if t <= 1e-8:
        return mask
    arr = np.asarray(mask, dtype=np.float32)
    active = arr > 0.5
    if not np.any(active):
        return mask

    pressure = p5._stroke_pressure(stroke)
    field = p5.paper_field(
        arr.shape,
        factor=factor,
        global_origin=global_origin,
        paper_scale=paper_scale,
        paper_seed=paper_seed,
    )
    pp = profile.paper
    width = _mean_contact_width(stroke, hardness, profile)
    thin_gain = _thin_texture_gain(width, pp.thin_width_reference, pp.thin_texture_floor)

    relief = (field - np.float32(0.5)) * np.float32(2.0)
    contact = np.float32((0.52 + 0.56 * hardness) * (1.0 - 0.56 * pressure))
    strength = np.float32(pp.strength * t * thin_gain) * contact
    mod = np.float32(1.0) + strength * relief

    # Replace P5's binary deep-valley dropout with a smooth contact falloff across a
    # configurable band. Thin strokes attenuate the effect further so paper tooth reads
    # as density variation rather than pinholes/dashes.
    valley_cut = float(0.23 + 0.12 * t - 0.11 * pressure)
    band = float(pp.valley_band)
    lo = valley_cut - band
    hi = valley_cut + band
    u = np.clip((field - np.float32(lo)) / np.float32(max(1e-6, hi - lo)), 0.0, 1.0)
    smooth = u * u * (np.float32(3.0) - np.float32(2.0) * u)
    valley_weight = np.float32(1.0) - smooth
    valley_depth = np.float32(pp.valley_depth * t * thin_gain * (1.0 - 0.45 * pressure))
    mod *= np.float32(1.0) - valley_weight * valley_depth

    mean_mod = float(np.mean(mod[active]))
    if mean_mod > 1e-6:
        mod = mod / np.float32(mean_mod)
    mod = np.clip(mod, np.float32(pp.min_modulation), np.float32(pp.max_modulation))
    out = np.clip(arr * mod, 0.0, 255.0).astype(np.uint8)
    return Image.fromarray(out, mode="L")


def _deposit(
    graphite_canvas: Image.Image,
    stroke: Stroke,
    *,
    factor: float,
    hi_size: tuple[int, int],
    tooth: float,
    paper_scale: float,
    paper_seed: int,
    graphite: tuple[int, int, int],
    profile: PencilContactProfile,
) -> None:
    if len(stroke.points) < 2:
        return
    grain, hardness = p3._material(stroke)
    bounds = _contact_bounds(stroke, factor, hardness, hi_size, profile)
    mask = _continuous_contact_mask(stroke, factor, hardness, bounds, profile)
    continuity = _continuity_floor_mask(stroke, factor, hardness, bounds, profile)
    mask = _smooth_grain_modulate(
        mask,
        stroke=stroke,
        grain=grain,
        hardness=hardness,
        factor=factor,
        global_origin=(bounds[0], bounds[1]),
        seed=p3._stroke_seed(stroke),
        profile=profile,
    )
    mask = _smooth_paper_modulate(
        mask,
        stroke=stroke,
        tooth=tooth,
        paper_scale=paper_scale,
        paper_seed=paper_seed,
        factor=factor,
        global_origin=(bounds[0], bounds[1]),
        hardness=hardness,
        profile=profile,
    )
    # Preserve a low, soft, continuous graphite contact floor after texture modulation.
    # This removes threshold-level dot chains without flattening stronger material variation.
    mask = ImageChops.lighter(mask, continuity)
    layer = p3._graphite_layer(mask.size, mask, graphite=graphite)
    graphite_canvas.alpha_composite(layer, dest=(bounds[0], bounds[1]))


def render(
    ir: StrokeIR,
    path: str | Path,
    background=(255, 255, 255, 255),
    *,
    scale: int = 1,
    supersample: int = DEFAULT_SUPERSAMPLE,
    graphite=(36, 34, 32),
    grade: str | None = None,
    contact_profile: str | Path | None = None,
) -> None:
    """Hardened final pencil material renderer.

    P9 preserves explicit StrokeIR geometry while replacing legacy pixel-dropout/stamp
    artifacts with continuous contact deposition, smooth graphite grain, smooth paper
    valleys, and non-breaking hand-pressure cadence. Eraser actions remain spatial and
    ordered through the existing P7 erase semantics.
    """
    if int(scale) != scale or scale < 1:
        raise ValueError("scale must be a positive integer")
    if int(supersample) != supersample or supersample < 2:
        raise ValueError("supersample must be an integer >= 2")
    if grade is not None:
        p6.get_grade(grade)
    profile = load_pencil_contact_profile(contact_profile)
    scale = int(scale); supersample = int(supersample)
    factor = float(scale * supersample)
    hi_size = (int(ir.width * factor), int(ir.height * factor))
    out_size = (int(ir.width * scale), int(ir.height * scale))
    tooth, paper_scale, paper_seed = p5._paper_settings(ir)

    graphite_canvas = Image.new("RGBA", hi_size, (int(graphite[0]), int(graphite[1]), int(graphite[2]), 0))
    for stroke in sorted(ir.strokes, key=lambda z: z.layer):
        if p7.is_eraser(stroke):
            p7._erase(
                graphite_canvas,
                stroke,
                factor=factor,
                hi_size=hi_size,
                tooth=tooth,
                paper_scale=paper_scale,
                paper_seed=paper_seed,
            )
            continue
        prepared = _prepare_grade(stroke, grade)
        prepared = _smooth_hand_dynamics(prepared, profile)
        _deposit(
            graphite_canvas,
            prepared,
            factor=factor,
            hi_size=hi_size,
            tooth=tooth,
            paper_scale=paper_scale,
            paper_seed=paper_seed,
            graphite=(int(graphite[0]), int(graphite[1]), int(graphite[2])),
            profile=profile,
        )

    base = Image.new("RGBA", hi_size, background)
    base = Image.alpha_composite(base, graphite_canvas)
    final = base.resize(out_size, Image.Resampling.LANCZOS)
    p = str(path)
    if p.lower().endswith((".jpg", ".jpeg")):
        final.convert("RGB").save(p, quality=95)
    else:
        final.save(p)
