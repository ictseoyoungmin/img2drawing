from __future__ import annotations

from dataclasses import dataclass
from types import ModuleType
from typing import Callable

from PIL import ImageChops

from . import pillow_pencil_contact as v9
from . import pillow_pencil_contact_v10 as v10
from .pillow_graphite_grain import _graphite_layer, _material, _stroke_seed
from .renderer_contracts import RendererContract, V9_CONTRACT, V10_CONTRACT


def _v9_build_patch(*, module, stroke, factor, hi_size, tooth, paper_scale, paper_seed, graphite, profile):
    grain, hardness = _material(stroke)
    bounds = module._contact_bounds(stroke, factor, hardness, hi_size, profile)
    mask = module._continuous_contact_mask(stroke, factor, hardness, bounds, profile)
    continuity = module._continuity_floor_mask(stroke, factor, hardness, bounds, profile)
    mask = module._smooth_grain_modulate(
        mask, stroke=stroke, grain=grain, hardness=hardness, factor=factor,
        global_origin=(bounds[0], bounds[1]), seed=_stroke_seed(stroke), profile=profile,
    )
    mask = module._smooth_paper_modulate(
        mask, stroke=stroke, tooth=tooth, paper_scale=paper_scale,
        paper_seed=paper_seed, factor=factor, global_origin=(bounds[0], bounds[1]),
        hardness=hardness, profile=profile,
    )
    mask = ImageChops.lighter(mask, continuity)
    layer = _graphite_layer(mask.size, mask, graphite=graphite)
    mask.close()
    continuity.close()
    return bounds, layer


def _v10_build_patch(*, module, stroke, factor, hi_size, tooth, paper_scale, paper_seed, graphite, profile):
    return module._build_contact_patch(
        stroke, factor=factor, hi_size=hi_size, tooth=tooth, paper_scale=paper_scale,
        paper_seed=paper_seed, graphite=graphite, profile=profile,
    )


@dataclass(frozen=True)
class RendererBackend:
    renderer_id: str
    renderer_version: str
    module: ModuleType
    patch_builder: Callable
    contract: RendererContract
    current: bool = False

    @property
    def identity(self) -> tuple[str, str]:
        return (self.renderer_id, self.renderer_version)

    @property
    def default_supersample(self) -> int:
        return int(self.module.DEFAULT_SUPERSAMPLE)

    @property
    def contract_digest(self) -> str:
        return self.contract.digest()

    @property
    def contract_payload(self) -> dict:
        return self.contract.to_dict()

    @property
    def render(self) -> Callable:
        return self.module.render

    def helper(self, name: str):
        try:
            return getattr(self.module, name)
        except AttributeError as exc:
            raise RuntimeError(
                f"renderer backend {self.renderer_id}/{self.renderer_version} "
                f"does not expose required helper {name}"
            ) from exc

    def prepare_stroke(self, stroke, grade, profile):
        return self.helper("_smooth_hand_dynamics")(
            self.helper("_prepare_grade")(stroke, grade), profile
        )

    def build_patch(self, *, stroke, factor, hi_size, tooth, paper_scale, paper_seed, graphite, profile):
        return self.patch_builder(
            module=self.module, stroke=stroke, factor=factor, hi_size=hi_size,
            tooth=tooth, paper_scale=paper_scale, paper_seed=paper_seed,
            graphite=graphite, profile=profile,
        )


_BACKENDS = {
    (v9.RENDERER_ID, str(v9.RENDERER_VERSION)): RendererBackend(
        v9.RENDERER_ID, str(v9.RENDERER_VERSION), v9, _v9_build_patch, V9_CONTRACT, current=False
    ),
    (v10.RENDERER_ID, str(v10.RENDERER_VERSION)): RendererBackend(
        v10.RENDERER_ID, str(v10.RENDERER_VERSION), v10, _v10_build_patch, V10_CONTRACT, current=True
    ),
}
_CURRENT_IDENTITY = (v10.RENDERER_ID, str(v10.RENDERER_VERSION))

for _identity, _backend in _BACKENDS.items():
    if (
        _backend.contract.renderer_id != _backend.renderer_id
        or _backend.contract.renderer_version != _backend.renderer_version
    ):
        raise RuntimeError(f"renderer contract identity mismatch for {_identity!r}")


def registered_renderer_identities() -> tuple[tuple[str, str], ...]:
    return tuple(sorted(_BACKENDS))


def resolve_renderer(renderer_id: str, renderer_version: str | int) -> RendererBackend:
    key = (str(renderer_id), str(renderer_version))
    try:
        return _BACKENDS[key]
    except KeyError as exc:
        supported = ", ".join(f"{rid}/{ver}" for rid, ver in sorted(_BACKENDS))
        raise ValueError(
            f"unsupported renderer identity/version {key[0]!r}/{key[1]!r}; "
            f"supported: {supported}; explicit migration is required"
        ) from exc


def current_renderer() -> RendererBackend:
    return _BACKENDS[_CURRENT_IDENTITY]


def is_registered_renderer(renderer_id: str, renderer_version: str | int) -> bool:
    return (str(renderer_id), str(renderer_version)) in _BACKENDS


__all__ = [
    "RendererBackend",
    "current_renderer",
    "is_registered_renderer",
    "registered_renderer_identities",
    "resolve_renderer",
]
