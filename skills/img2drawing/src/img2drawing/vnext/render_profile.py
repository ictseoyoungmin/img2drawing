"""Versioned raster configuration for canonical vNext output and replay."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Mapping

from ..core.session import sha256_obj
from ..render.pillow_paper_interaction import (
    DEFAULT_PAPER_SCALE,
    DEFAULT_PAPER_SEED,
    DEFAULT_PAPER_TOOTH,
)
from ..render.pillow_pencil_contact import (
    DEFAULT_SUPERSAMPLE,
    RENDERER_ID,
    RENDERER_VERSION,
)


RENDER_PROFILE_SCHEMA = "img2drawing.vnext.render_profile.v1"
SEED_DOMAIN = "pencil-contact-stroke-and-paper-coordinate-v1"
_FIELDS = {
    "profile_id",
    "renderer_id",
    "renderer_version",
    "canvas_width",
    "canvas_height",
    "material_profile",
    "paper_tooth",
    "paper_scale",
    "paper_seed",
    "supersample",
    "output_scale",
    "background_rgba",
    "graphite_rgb",
    "seed_domain",
    "compositing",
    "png_mode",
    "gif_palette_colors",
    "gif_loop",
    "gif_disposal",
}


def _text(value: Any, field: str) -> str:
    result = str(value).strip()
    if not result:
        raise ValueError(f"{field} must be non-empty")
    return result


def _channels(values: Any, count: int, field: str) -> tuple[int, ...]:
    try:
        raw = tuple(values)
        result = tuple(int(value) for value in raw)
    except TypeError as exc:
        raise TypeError(f"{field} must contain {count} integer channels") from exc
    if (
        len(result) != count
        or any(converted != original for converted, original in zip(result, raw))
        or any(value < 0 or value > 255 for value in result)
    ):
        raise ValueError(f"{field} must contain {count} channels in [0,255]")
    return result


@dataclass(frozen=True)
class RenderProfile:
    """Complete deterministic renderer input, separate from authored style guidance."""

    profile_id: str
    renderer_id: str
    renderer_version: str
    canvas_width: int
    canvas_height: int
    material_profile: str = "builtin:pencil-contact"
    paper_tooth: float = DEFAULT_PAPER_TOOTH
    paper_scale: float = DEFAULT_PAPER_SCALE
    paper_seed: int = DEFAULT_PAPER_SEED
    supersample: int = DEFAULT_SUPERSAMPLE
    output_scale: int = 1
    background_rgba: tuple[int, int, int, int] = (255, 255, 255, 255)
    graphite_rgb: tuple[int, int, int] = (36, 34, 32)
    seed_domain: str = SEED_DOMAIN
    compositing: str = "rgba-source-over-background-v1"
    png_mode: str = "RGBA"
    gif_palette_colors: int = 256
    gif_loop: int = 0
    gif_disposal: int = 2

    def __post_init__(self) -> None:
        object.__setattr__(self, "profile_id", _text(self.profile_id, "profile_id"))
        renderer_id = _text(self.renderer_id, "renderer_id")
        renderer_version = _text(self.renderer_version, "renderer_version")
        if renderer_id != RENDERER_ID or renderer_version != RENDERER_VERSION:
            raise ValueError(
                "unsupported renderer identity/version; explicit migration is required"
            )
        object.__setattr__(self, "renderer_id", renderer_id)
        object.__setattr__(self, "renderer_version", renderer_version)
        width, height = int(self.canvas_width), int(self.canvas_height)
        if width <= 0 or height <= 0:
            raise ValueError("render profile canvas dimensions must be positive")
        object.__setattr__(self, "canvas_width", width)
        object.__setattr__(self, "canvas_height", height)
        material = _text(self.material_profile, "material_profile")
        if material != "builtin:pencil-contact":
            raise ValueError("unsupported material_profile; custom file paths are not portable")
        object.__setattr__(self, "material_profile", material)
        tooth = float(self.paper_tooth)
        scale = float(self.paper_scale)
        seed = int(self.paper_seed)
        if not 0.0 <= tooth <= 1.0:
            raise ValueError("paper_tooth must be in [0,1]")
        if not 0.35 <= scale <= 4.0:
            raise ValueError("paper_scale must be in [0.35,4.0]")
        if seed != self.paper_seed or not 0 <= seed <= 0xFFFFFFFF:
            raise ValueError("paper_seed must be an unsigned 32-bit integer")
        object.__setattr__(self, "paper_tooth", tooth)
        object.__setattr__(self, "paper_scale", scale)
        object.__setattr__(self, "paper_seed", seed)
        supersample, output_scale = int(self.supersample), int(self.output_scale)
        if supersample != self.supersample or supersample < 2:
            raise ValueError("supersample must be >= 2")
        if output_scale != self.output_scale or output_scale < 1:
            raise ValueError("output_scale must be >= 1")
        object.__setattr__(self, "supersample", supersample)
        object.__setattr__(self, "output_scale", output_scale)
        object.__setattr__(self, "background_rgba", _channels(self.background_rgba, 4, "background_rgba"))
        object.__setattr__(self, "graphite_rgb", _channels(self.graphite_rgb, 3, "graphite_rgb"))
        if _text(self.seed_domain, "seed_domain") != SEED_DOMAIN:
            raise ValueError("unsupported seed_domain")
        object.__setattr__(self, "seed_domain", SEED_DOMAIN)
        if _text(self.compositing, "compositing") != "rgba-source-over-background-v1":
            raise ValueError("unsupported compositing policy")
        object.__setattr__(self, "compositing", "rgba-source-over-background-v1")
        if _text(self.png_mode, "png_mode") != "RGBA":
            raise ValueError("unsupported PNG mode")
        object.__setattr__(self, "png_mode", "RGBA")
        colors, loop, disposal = int(self.gif_palette_colors), int(self.gif_loop), int(self.gif_disposal)
        if colors != self.gif_palette_colors or not 2 <= colors <= 256:
            raise ValueError("gif_palette_colors must be in [2,256]")
        if loop != self.gif_loop or loop < 0:
            raise ValueError("gif_loop must be >= 0")
        if disposal != self.gif_disposal or disposal not in (1, 2, 3):
            raise ValueError("gif_disposal must be 1, 2, or 3")
        object.__setattr__(self, "gif_palette_colors", colors)
        object.__setattr__(self, "gif_loop", loop)
        object.__setattr__(self, "gif_disposal", disposal)

    @classmethod
    def canonical(cls, width: int, height: int) -> "RenderProfile":
        return cls(
            profile_id="pencil-contact-canonical-v1",
            renderer_id=RENDERER_ID,
            renderer_version=RENDERER_VERSION,
            canvas_width=int(width),
            canvas_height=int(height),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": RENDER_PROFILE_SCHEMA,
            "profile_id": self.profile_id,
            "renderer_id": self.renderer_id,
            "renderer_version": self.renderer_version,
            "canvas_width": self.canvas_width,
            "canvas_height": self.canvas_height,
            "material_profile": self.material_profile,
            "paper_tooth": self.paper_tooth,
            "paper_scale": self.paper_scale,
            "paper_seed": self.paper_seed,
            "supersample": self.supersample,
            "output_scale": self.output_scale,
            "background_rgba": list(self.background_rgba),
            "graphite_rgb": list(self.graphite_rgb),
            "seed_domain": self.seed_domain,
            "compositing": self.compositing,
            "png_mode": self.png_mode,
            "gif_palette_colors": self.gif_palette_colors,
            "gif_loop": self.gif_loop,
            "gif_disposal": self.gif_disposal,
        }

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "RenderProfile":
        if raw.get("schema") not in (None, RENDER_PROFILE_SCHEMA):
            raise ValueError(f"unsupported render profile schema: {raw.get('schema')!r}")
        unknown = set(raw).difference(_FIELDS | {"schema"})
        if unknown:
            raise ValueError(f"render profile contains unsupported fields: {sorted(unknown)}")
        return cls(**{field: raw[field] for field in _FIELDS})

    def digest(self) -> str:
        return sha256_obj(self.to_dict())

    def validate_canvas(self, width: int, height: int) -> None:
        if (self.canvas_width, self.canvas_height) != (int(width), int(height)):
            raise ValueError("render profile canvas does not match session canvas")

    def prepared_ir(self, ir):
        """Return a render-only view with profile-owned paper state; geometry is copied."""

        self.validate_canvas(ir.width, ir.height)
        prepared = deepcopy(ir)
        metadata = deepcopy(prepared.metadata if isinstance(prepared.metadata, dict) else {})
        metadata["paper"] = {
            "tooth": self.paper_tooth,
            "scale": self.paper_scale,
            "seed": self.paper_seed,
        }
        prepared.metadata = metadata
        return prepared

    def renderer_kwargs(self) -> dict[str, Any]:
        return {
            "background": self.background_rgba,
            "scale": self.output_scale,
            "supersample": self.supersample,
            "graphite": self.graphite_rgb,
            "contact_profile": None,
        }


__all__ = ["RENDER_PROFILE_SCHEMA", "SEED_DOMAIN", "RenderProfile"]
