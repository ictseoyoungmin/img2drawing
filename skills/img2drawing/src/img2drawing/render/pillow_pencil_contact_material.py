from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageDraw

from ..core.ir import Stroke, StrokeIR
from . import pillow_graphite_grain as p3
from . import pillow_pencil_contact_core as v10
from .renderer_contracts import V11_CONTRACT

RENDERER_ID = "pillow-pencil-contact-v11"
RENDERER_VERSION = "1"
RENDERER_CONTRACT = V11_CONTRACT
DEFAULT_SUPERSAMPLE = v10.DEFAULT_SUPERSAMPLE
HIGH_QUALITY_SUPERSAMPLE = v10.HIGH_QUALITY_SUPERSAMPLE

# Public helper surface consumed by RendererBackend / patch cache.
load_pencil_contact_profile = v10.load_pencil_contact_profile
_prepare_grade = v10._prepare_grade
_smooth_hand_dynamics = v10._smooth_hand_dynamics

_BROAD_TEXTURE_BASE = float(RENDERER_CONTRACT.value("broad_texture_base"))
_BROAD_TEXTURE_EXPOSURE_GAIN = float(
    RENDERER_CONTRACT.value("broad_texture_exposure_gain")
)
_BROAD_TEXTURE_VALLEY_DEPTH = float(
    RENDERER_CONTRACT.value("broad_texture_valley_depth")
)


def _broad_core_mask(
    stroke: Stroke,
    factor: float,
    hardness: float,
    bounds: tuple[int, int, int, int],
    profile,
) -> Image.Image:
    """Authored-value broad core with physical round terminals.

    v10's broad shoulder already has radial contact, but its continuity core is drawn by
    Pillow line segments whose terminal is a square/butt cut. At transitional broad widths
    that core can dominate the shoulder and make the visible stroke end look digitally
    chopped. v11 keeps the same body/value authority while explicitly rounding the two
    physical contact terminals with the actual pressure/tapered sample diameter.
    """

    x0, y0, x1, y1 = bounds
    samples = v10._pressure_samples(
        stroke, factor, hardness, profile.trajectory_spacing, profile
    )
    mask = Image.new("L", (x1 - x0, y1 - y0), 0)
    if len(samples) < 2:
        return mask

    mean_width = float(np.mean([sample[2] for sample in samples])) / float(factor)
    broadness = v10._broadness(mean_width)
    if broadness <= 1e-08:
        return v10._continuity_floor_mask(
            stroke, factor, hardness, bounds, profile
        )

    points = [(sample[0] - x0, sample[1] - y0) for sample in samples]
    policy = v10._stroke_material_policy(stroke)
    core = v10._clamp01(policy["core_preservation"])
    strictness = {
        "relaxed": 0.0,
        "balanced": 0.5,
        "strict": 1.0,
    }[policy["value_authority"]]

    target_width_ratio = v10._clamp01(0.10 + 0.18 * core + 0.06 * strictness)
    width_ratio = 1.0 - broadness * (1.0 - target_width_ratio)
    target_alpha_retention = v10._clamp01(
        0.45 + 0.45 * core + 0.08 * strictness
    )
    alpha_retention = 1.0 - broadness * (1.0 - target_alpha_retention)
    material = profile.material
    coverage_floor = int(round(material.continuity_min_coverage * 255.0))

    draw = ImageDraw.Draw(mask)
    for index in range(len(samples) - 1):
        a = points[index]
        b = points[index + 1]
        width_src = 0.5 * (samples[index][2] + samples[index + 1][2])
        alpha_src = 0.5 * (samples[index][3] + samples[index + 1][3])
        width = max(1, int(round(width_src * width_ratio)))
        legacy_floor = max(
            coverage_floor,
            int(round(alpha_src * material.continuity_floor_ratio)),
        )
        authored_floor = int(round(alpha_src * alpha_retention))
        alpha = max(1, legacy_floor, authored_floor)
        draw.line([a, b], fill=alpha, width=width, joint="curve")

    # The line body remains authored-value authority. Only the two physical terminals get
    # explicit contact discs, using the already pressure/taper-resolved sample width/alpha.
    for index in (0, -1):
        cx, cy = points[index]
        width = max(1, int(round(samples[index][2] * width_ratio)))
        alpha_src = samples[index][3]
        alpha = max(
            1,
            coverage_floor,
            int(round(alpha_src * material.continuity_floor_ratio)),
            int(round(alpha_src * alpha_retention)),
        )
        radius = max(0.5, 0.5 * float(width))
        draw.ellipse(
            (cx - radius, cy - radius, cx + radius, cy + radius),
            fill=alpha,
        )
    return mask


def _broad_graphite_modulate(
    mask: Image.Image,
    *,
    stroke: Stroke,
    broadness: float,
    factor: float,
    global_origin: tuple[int, int],
    paper_scale: float,
    paper_seed: int,
) -> Image.Image:
    """Strengthen page-fixed graphite/tooth read without re-authoring mean value."""

    if broadness <= 1e-08:
        return mask
    arr = np.asarray(mask, dtype=np.float32)
    active = arr > 0.5
    if not np.any(active):
        return mask

    height, width = arr.shape
    yy, xx = np.indices((height, width), dtype=np.float64)
    lx = (xx + float(global_origin[0])) / float(factor)
    ly = (yy + float(global_origin[1])) / float(factor)
    paper = v10.p5.paper_field(
        arr.shape,
        factor=factor,
        global_origin=global_origin,
        paper_scale=paper_scale,
        paper_seed=paper_seed,
    ).astype(np.float32)
    micro = v10._pixel_hash_tooth(
        lx, ly, paper_seed ^ 0x5F356495
    ).astype(np.float32)
    field = np.float32(0.70) * paper + np.float32(0.30) * micro

    policy = v10._stroke_material_policy(stroke)
    exposure = v10._clamp01(policy["grain_exposure"])
    strength = np.float32(
        broadness * (_BROAD_TEXTURE_BASE + _BROAD_TEXTURE_EXPOSURE_GAIN * exposure)
    )
    modulation = (
        np.float32(1.0)
        + strength * (field - np.float32(0.5)) * np.float32(2.0)
    )
    valley = np.clip(
        (np.float32(0.48) - field) / np.float32(0.48), 0.0, 1.0
    )
    modulation *= (
        np.float32(1.0)
        - np.float32(_BROAD_TEXTURE_VALLEY_DEPTH * broadness) * valley
    )

    # Keep authored mean density stable while allowing local tooth/grain variation.
    mean = float(np.mean(modulation[active]))
    if mean > 1e-06:
        modulation = modulation / np.float32(mean)
    modulation = np.clip(modulation, np.float32(0.74), np.float32(1.26))
    arr[active] *= modulation[active]
    return Image.fromarray(np.clip(arr, 0.0, 255.0).astype(np.uint8), mode="L")


def _build_contact_patch(
    stroke: Stroke,
    *,
    factor: float,
    hi_size: tuple[int, int],
    tooth: float,
    paper_scale: float,
    paper_seed: int,
    graphite: tuple[int, int, int],
    profile,
):
    """Return one v11 patch; thin strokes remain pixel-identical to v10."""

    grain, hardness = p3._material(stroke)
    mean_width = v10._mean_contact_width(stroke, hardness, profile)
    broadness = v10._broadness(mean_width)
    if broadness <= 1e-08:
        return v10._build_contact_patch(
            stroke,
            factor=factor,
            hi_size=hi_size,
            tooth=tooth,
            paper_scale=paper_scale,
            paper_seed=paper_seed,
            graphite=graphite,
            profile=profile,
        )

    bounds = v10._contact_bounds(stroke, factor, hardness, hi_size, profile)
    shoulder = v10._continuous_contact_mask(
        stroke, factor, hardness, bounds, profile
    )
    core = _broad_core_mask(stroke, factor, hardness, bounds, profile)

    # Preserve the v10 transitional shoulder treatment.
    if broadness < 0.35:
        shoulder = v10._smooth_grain_modulate(
            shoulder,
            stroke=stroke,
            grain=grain,
            hardness=hardness,
            factor=factor,
            global_origin=(bounds[0], bounds[1]),
            seed=p3._stroke_seed(stroke),
            profile=profile,
        )
        shoulder = v10._smooth_paper_modulate(
            shoulder,
            stroke=stroke,
            tooth=tooth,
            paper_scale=paper_scale,
            paper_seed=paper_seed,
            factor=factor,
            global_origin=(bounds[0], bounds[1]),
            hardness=hardness,
            profile=profile,
        )
    elif broadness < 0.7:
        soft_grain = max(0.0, float(grain) * (0.7 - broadness) / 0.35)
        if soft_grain > 1e-06:
            shoulder = v10._smooth_grain_modulate(
                shoulder,
                stroke=stroke,
                grain=soft_grain,
                hardness=hardness,
                factor=factor,
                global_origin=(bounds[0], bounds[1]),
                seed=p3._stroke_seed(stroke),
                profile=profile,
            )

    mask = ImageChops.lighter(shoulder, core)
    textured = _broad_graphite_modulate(
        mask,
        stroke=stroke,
        broadness=broadness,
        factor=factor,
        global_origin=(bounds[0], bounds[1]),
        paper_scale=paper_scale,
        paper_seed=paper_seed,
    )
    mask.close()
    shoulder.close()
    core.close()

    policy = v10._stroke_material_policy(stroke)
    darken = v10._policy_pigment_darken(policy, broadness)
    local_graphite = tuple(
        max(0, min(255, int(round(float(channel) * (1.0 - darken)))))
        for channel in graphite
    )
    layer = p3._graphite_layer(textured.size, textured, graphite=local_graphite)
    textured.close()
    return bounds, layer


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
    profile,
) -> None:
    bounds, layer = _build_contact_patch(
        stroke,
        factor=factor,
        hi_size=hi_size,
        tooth=tooth,
        paper_scale=paper_scale,
        paper_seed=paper_seed,
        graphite=graphite,
        profile=profile,
    )
    graphite_canvas.alpha_composite(layer, dest=(bounds[0], bounds[1]))
    layer.close()


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
    if int(scale) != scale or scale < 1:
        raise ValueError("scale must be a positive integer")
    if int(supersample) != supersample or supersample < 2:
        raise ValueError("supersample must be an integer >= 2")
    if grade is not None:
        v10.p6.get_grade(grade)
    profile = load_pencil_contact_profile(contact_profile)
    scale = int(scale)
    supersample = int(supersample)
    factor = float(scale * supersample)
    hi_size = (int(ir.width * factor), int(ir.height * factor))
    out_size = (int(ir.width * scale), int(ir.height * scale))
    tooth, paper_scale, paper_seed = v10.p5._paper_settings(ir)
    graphite_rgb = (int(graphite[0]), int(graphite[1]), int(graphite[2]))
    graphite_canvas = Image.new(
        "RGBA", hi_size, (*graphite_rgb, 0)
    )
    for stroke in sorted(ir.strokes, key=lambda item: item.layer):
        if v10.p7.is_eraser(stroke):
            v10.p7._erase(
                graphite_canvas,
                stroke,
                factor=factor,
                hi_size=hi_size,
                tooth=tooth,
                paper_scale=paper_scale,
                paper_seed=paper_seed,
            )
            continue
        prepared = _smooth_hand_dynamics(_prepare_grade(stroke, grade), profile)
        _deposit(
            graphite_canvas,
            prepared,
            factor=factor,
            hi_size=hi_size,
            tooth=tooth,
            paper_scale=paper_scale,
            paper_seed=paper_seed,
            graphite=graphite_rgb,
            profile=profile,
        )
    base = Image.new("RGBA", hi_size, background)
    final = Image.alpha_composite(base, graphite_canvas).resize(
        out_size, Image.Resampling.LANCZOS
    )
    output = str(path)
    if output.lower().endswith((".jpg", ".jpeg")):
        final.convert("RGB").save(output, quality=95)
    else:
        final.save(output)


__all__ = [
    "DEFAULT_SUPERSAMPLE",
    "HIGH_QUALITY_SUPERSAMPLE",
    "RENDERER_CONTRACT",
    "RENDERER_ID",
    "RENDERER_VERSION",
    "_build_contact_patch",
    "_prepare_grade",
    "_smooth_hand_dynamics",
    "load_pencil_contact_profile",
    "render",
]
