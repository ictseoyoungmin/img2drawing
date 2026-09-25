"""The pencil renderer: authored stroke IR in, supersampled graphite on paper out."""

from __future__ import annotations

from pathlib import Path

from PIL import Image

from ..core.ir import Stroke, StrokeIR
from .contact_profile import PencilContactProfile, load_pencil_contact_profile
from .deposit import build_patch
from .eraser import erase, is_eraser
from .grades import get_pencil_preset, prepare_grade
from .hand import pencil_hand_dynamics
from .paper import paper_settings

DEFAULT_SUPERSAMPLE = 4
HIGH_QUALITY_SUPERSAMPLE = 8
DEFAULT_GRAPHITE = (36, 34, 32)
DEFAULT_BACKGROUND = (255, 255, 255, 255)


def load_contact_profile() -> PencilContactProfile:
    """The built-in pencil contact profile bound to the renderer contract."""

    return load_pencil_contact_profile(None)


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
) -> Image.Image:
    """Render ``ir`` and return the RGBA image at ``scale`` x canvas size."""

    if int(scale) != scale or scale < 1:
        raise ValueError("scale must be a positive integer")
    if int(supersample) != supersample or supersample < 2:
        raise ValueError("supersample must be an integer >= 2")
    if grade is not None:
        get_pencil_preset(grade)
    profile = load_contact_profile()
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
) -> None:
    """Render ``ir`` to ``path`` (PNG keeps RGBA; JPEG is flattened to RGB)."""

    final = render_image(ir, background=background, scale=scale, supersample=supersample, graphite=graphite, grade=grade)
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
