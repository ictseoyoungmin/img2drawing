"""The pencil renderer: authored stroke IR in, supersampled graphite on paper out."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from PIL import Image

from ..core.ir import Stroke, StrokeIR
from .contact_profile import PencilContactProfile, load_pencil_contact_profile
from .contract import CONTACT_WIDTH_CONTRACT, OPACITY_NORMALIZED_CONTRACT, PRESSURE_LIFT_CONTRACT, RENDERER_ID, RENDERER_VERSION, contract_for_identity, MIXED_MEDIA_CONTRACT, MIXED_RENDERER_VERSIONS
from .deposit import build_patch
from .eraser import erase, is_eraser
from .grades import get_pencil_preset, prepare_grade
from .hand import pencil_hand_dynamics
from .paper import paper_settings

DEFAULT_SUPERSAMPLE = 4
HIGH_QUALITY_SUPERSAMPLE = 8
DEFAULT_GRAPHITE = (36, 34, 32)
DEFAULT_BACKGROUND = (255, 255, 255, 255)


def load_contact_profile(renderer_version: str = RENDERER_VERSION) -> PencilContactProfile:
    """Resolve immutable contact behavior without changing global renderer state."""
    contract = (CONTACT_WIDTH_CONTRACT if renderer_version in MIXED_RENDERER_VERSIONS
                else contract_for_identity(RENDERER_ID, renderer_version))
    profile = load_pencil_contact_profile(None)
    if contract is CONTACT_WIDTH_CONTRACT:
        return replace(profile, opacity_normalized=True, contact_width_control=True)
    return replace(profile, opacity_normalized=True) if contract in (OPACITY_NORMALIZED_CONTRACT, PRESSURE_LIFT_CONTRACT) else profile


def prepare_stroke(stroke: Stroke, grade: str | None, profile: PencilContactProfile) -> Stroke:
    """Derive the render-time stroke: named grade first, then hand dynamics."""

    return pencil_hand_dynamics(prepare_grade(stroke, grade), profile)


def render_image(
    ir: StrokeIR,
    *,
    background=DEFAULT_BACKGROUND,
    scale: int = 1,
    supersample: int = DEFAULT_SUPERSAMPLE,
    graphite=DEFAULT_GRAPHITE,
    grade: str | None = None,
    renderer_version: str = RENDERER_VERSION,
) -> Image.Image:
    """Render ``ir`` and return the RGBA image at ``scale`` x canvas size."""

    if renderer_version in MIXED_RENDERER_VERSIONS:
        from .mixed import render_mixed_image
        return render_mixed_image(ir, background=background, scale=scale, supersample=supersample,
                                  graphite=graphite, grade=grade,renderer_version=renderer_version)
    if ir.media_contract is not None or ir.ink_elements or ir.element_order:
        raise ValueError("mixed history requires a mixed-media renderer")
    if int(scale) != scale or scale < 1:
        raise ValueError("scale must be a positive integer")
    if int(supersample) != supersample or supersample < 2:
        raise ValueError("supersample must be an integer >= 2")
    if grade is not None:
        get_pencil_preset(grade)
    profile = load_contact_profile(renderer_version)
    factor = float(int(scale) * int(supersample))
    hi_size = (int(ir.width * factor), int(ir.height * factor))
    out_size = (int(ir.width * int(scale)), int(ir.height * int(scale)))
    tooth, paper_scale, paper_seed = paper_settings(ir)
    graphite_rgb = (int(graphite[0]), int(graphite[1]), int(graphite[2]))
    graphite_canvas = Image.new("RGBA", hi_size, (*graphite_rgb, 0))
    for stroke in sorted(ir.strokes, key=lambda item: item.layer):
        if is_eraser(stroke):
            erase(
                graphite_canvas, stroke, factor=factor, hi_size=hi_size,
                tooth=tooth, paper_scale=paper_scale, paper_seed=paper_seed,
                allow_pressure_lift=renderer_version in (PRESSURE_LIFT_CONTRACT.renderer_version, CONTACT_WIDTH_CONTRACT.renderer_version),
            )
            continue
        bounds, layer = build_patch(
            prepare_stroke(stroke, grade, profile),
            factor=factor, hi_size=hi_size, tooth=tooth, paper_scale=paper_scale,
            paper_seed=paper_seed, graphite=graphite_rgb, profile=profile,
        )
        graphite_canvas.alpha_composite(layer, dest=(bounds[0], bounds[1]))
        layer.close()
    base = Image.new("RGBA", hi_size, background)
    return Image.alpha_composite(base, graphite_canvas).resize(out_size, Image.Resampling.LANCZOS)


def render(
    ir: StrokeIR,
    path: str | Path,
    background=DEFAULT_BACKGROUND,
    *,
    scale: int = 1,
    supersample: int = DEFAULT_SUPERSAMPLE,
    graphite=DEFAULT_GRAPHITE,
    grade: str | None = None,
    renderer_version: str = RENDERER_VERSION,
) -> None:
    """Render ``ir`` to ``path`` (PNG keeps RGBA; JPEG is flattened to RGB)."""

    final = render_image(ir, background=background, scale=scale, supersample=supersample, graphite=graphite, grade=grade,
                         renderer_version=renderer_version)
    output = str(path)
    if output.lower().endswith((".jpg", ".jpeg")):
        final.convert("RGB").save(output, quality=95)
    else:
        final.save(output)


__all__ = [
    "DEFAULT_SUPERSAMPLE",
    "HIGH_QUALITY_SUPERSAMPLE",
    "build_patch",
    "erase",
    "is_eraser",
    "load_contact_profile",
    "prepare_stroke",
    "render",
    "render_image",
]
