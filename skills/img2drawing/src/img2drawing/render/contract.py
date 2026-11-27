"""Renderer identity and the parameter contract that binds persisted sessions to pixels.

The package ships one pencil engine with explicit immutable material contracts.
Identity and digest are persisted in every RenderProfile. Legacy v11 remains the
default and exact replay authority. Unavailable identities/digests fail closed.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

CONTRACT_SCHEMA = "img2drawing.renderer-contract.v1"


@dataclass(frozen=True)
class RendererContract:
    renderer_id: str
    renderer_version: str
    parameters: tuple[tuple[str, Any], ...]
    schema: str = CONTRACT_SCHEMA

    def __post_init__(self) -> None:
        if not self.renderer_id or not self.renderer_version:
            raise ValueError("renderer contract identity must be non-empty")
        names = [name for name, _ in self.parameters]
        if names != sorted(names) or len(set(names)) != len(names):
            raise ValueError("renderer contract parameters must be unique and sorted")

    @property
    def identity(self) -> tuple[str, str]:
        return (self.renderer_id, self.renderer_version)

    def value(self, name: str) -> Any:
        for key, value in self.parameters:
            if key == name:
                return value
        raise KeyError(name)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": self.schema,
            "renderer_id": self.renderer_id,
            "renderer_version": self.renderer_version,
            "parameters": {key: value for key, value in self.parameters},
        }

    def digest(self) -> str:
        blob = json.dumps(self.to_dict(), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(blob.encode("utf-8")).hexdigest()


PENCIL_CONTRACT = RendererContract(
    renderer_id="img2drawing-pencil",
    renderer_version="11",
    parameters=(
        ("authored_contrast_gamma", 0.42),
        ("broad_core_model", "round-terminal-authored-core-v1"),
        ("broad_diameter_scale", 0.90),
        ("broad_flow_gain", 1.28),
        ("broad_full", 10.0),
        ("broad_pigment_darken", 0.22),
        ("broad_start", 4.5),
        ("broad_terminal_model", "pressure-resolved-round-contact-v2"),
        ("broad_texture_base", 0.16),
        ("broad_texture_exposure_gain", 0.28),
        ("broad_texture_model", "page-fixed-graphite-tooth-v2"),
        ("broad_texture_valley_depth", 0.10),
        ("contact_profile", "natural-graphite-v1"),
        ("default_material_policy", "canonical-pencil"),
        ("deposition_variability_amp", 0.24),
        ("deposition_variability_coarse", 7.5),
        ("deposition_variability_fine", 3.6),
        ("deposition_variability_fine_mix", 0.32),
        ("material_model", "radial-contact-shoulder-authored-core"),
        ("material_policy_model", "resolved-markmaking-v1"),
        ("policy_core_floor_model", "authored-core-shoulder-v2"),
        ("policy_core_texture_model", "page-fixed-subtle-core-v1"),
        ("policy_grain_model", "style-governed-page-tooth-v1"),
        ("seed_identity_model", "stage-free-render-seed-v1"),
        ("thin_flick_model", "specialized-continuity-v1"),
        ("thin_terminal_model", "physical-px-expressive-v1"),
    ),
)

# An additive, opt-in material contract. Do not modify PENCIL_CONTRACT's parameters:
# historical v11 profiles and cache identities rely on its exact digest.
OPACITY_NORMALIZED_CONTRACT = RendererContract(
    renderer_id=PENCIL_CONTRACT.renderer_id,
    renderer_version="11-opacity-normalized-v1",
    parameters=tuple(sorted({
        **dict(PENCIL_CONTRACT.parameters),
        "material_model": "arc-length-normalized-optical-contact-v1",
        "opacity_model": "authored-alpha-log-transmittance-v1",
        "continuity_opacity": "local-authored-alpha-cap-v1",
        "zero_opacity": "empty-patch-v1",
        "radial_integration": "trapezoidal-sample-distance-v1",
        "contact_alpha_minimum": 0,
        "optical_alpha_cap": 0.999,
    }.items())),
)

# New contact semantics require a distinct identity so older packages fail closed.
PRESSURE_LIFT_CONTRACT = RendererContract(
    renderer_id=PENCIL_CONTRACT.renderer_id,
    renderer_version="11-opacity-normalized-v2",
    parameters=tuple(sorted({
        **dict(OPACITY_NORMALIZED_CONTRACT.parameters),
        "path_lift_model": "explicit-pressure-max-radial-contact-v1",
        "path_lift_sample_spacing": 0.5,
        "path_lift_radius": "sqrt-pressure-v1",
        "path_lift_edge_exponent": "hardness-linear-v1",
        "path_lift_max_samples": 100000,
    }.items())),
)

CONTACT_WIDTH_CONTRACT = RendererContract(
    renderer_id=PENCIL_CONTRACT.renderer_id,
    renderer_version="11-opacity-normalized-v3",
    parameters=tuple(sorted({
        **dict(PRESSURE_LIFT_CONTRACT.parameters),
        "contact_width_model": "explicit-resolved-diameter-arc-knots-v1",
        "contact_width_range": (0.15, 1.0),
        "contact_width_max_knots": 64,
    }.items())),
)

# Distinct opt-in identity: earlier runtimes fail closed instead of treating ink as graphite.
MIXED_MEDIA_CONTRACT = RendererContract(
    renderer_id="img2drawing-mixed",
    renderer_version="mixed-media-v1",
    parameters=tuple(sorted({
        "graphite_contract_digest": CONTACT_WIDTH_CONTRACT.digest(),
        "history_contract": "img2drawing.mixed_history.v1",
        "ink_geometry": "img2drawing.ink_mark.v1",
        "ink_kernel": "opaque-swept-disks-even-odd-v1",
        "composition": "ordered-local-graphite-runs-ink-v1",
        "selective_lift": "all-prior-graphite-runs-v1",
        "resampling": "supersampled-lanczos-v1",
        "max_working_pixels": 16 * 1024 * 1024,
        "max_factor": 16,
        "max_patch_pixels": 16 * 1024 * 1024,
        "max_ink_kernel_work": 64 * 1024 * 1024,
        "max_composite_work": 256 * 1024 * 1024,
        "max_lift_pairs": 4096,
    }.items())),
)


def validate_mixed_raster_budget(width, height, supersample, scale):
    factor = supersample * scale
    if (type(width) is not int or type(height) is not int or width <= 0 or height <= 0
            or type(supersample) is not int or supersample < 2
            or type(scale) is not int or scale < 1
            or factor > MIXED_MEDIA_CONTRACT.value("max_factor")
            or width * height * factor * factor > MIXED_MEDIA_CONTRACT.value("max_working_pixels")):
        raise ValueError("mixed-media working raster budget exceeded; choose an explicit supported profile")
    return factor


RENDERER_ID = PENCIL_CONTRACT.renderer_id
RENDERER_VERSION = PENCIL_CONTRACT.renderer_version
RENDERER_CONTRACT_DIGEST = PENCIL_CONTRACT.digest()

# v1.0.3 persisted this renderer under its pre-1.1 identity. The pixels are identical
# (pinned by the v11 golden tests), so those sessions resume under the current contract.
_EQUIVALENT_IDENTITIES = frozenset({("pillow-pencil-contact-v11", "1")})

REPLAY_RELEASE_HINT = (
    "replay it with the published img2drawing release that shipped that renderer "
    "(pip install 'img2drawing==1.0.3' for pillow-pencil-contact-v9/v10/v11 sessions)"
)


class UnsupportedRendererError(ValueError):
    """A persisted renderer identity or contract cannot be reproduced by this package."""


def canonical_identity(renderer_id: str, renderer_version: str | int) -> tuple[str, str]:
    """Return a supported exact identity, or fail closed."""

    key = (str(renderer_id).strip(), str(renderer_version).strip())
    if key in _EQUIVALENT_IDENTITIES:
        return PENCIL_CONTRACT.identity
    if key in (PENCIL_CONTRACT.identity, OPACITY_NORMALIZED_CONTRACT.identity, PRESSURE_LIFT_CONTRACT.identity, CONTACT_WIDTH_CONTRACT.identity, MIXED_MEDIA_CONTRACT.identity):
        return key
    raise UnsupportedRendererError(
        f"renderer {key[0]!r}/{key[1]!r} is not available in this package; "
        f"default renderer is {RENDERER_ID}/{RENDERER_VERSION}. To reproduce the session exactly, "
        + REPLAY_RELEASE_HINT
    )


def contract_for_identity(renderer_id: str, renderer_version: str | int) -> RendererContract:
    key = canonical_identity(renderer_id, renderer_version)
    if key == MIXED_MEDIA_CONTRACT.identity:
        return MIXED_MEDIA_CONTRACT
    if key == PENCIL_CONTRACT.identity:
        return PENCIL_CONTRACT
    if key == CONTACT_WIDTH_CONTRACT.identity:
        return CONTACT_WIDTH_CONTRACT
    return PRESSURE_LIFT_CONTRACT if key == PRESSURE_LIFT_CONTRACT.identity else OPACITY_NORMALIZED_CONTRACT


def verify_contract_digest(digest: str | None, *, renderer_id: str = RENDERER_ID,
                           renderer_version: str | int = RENDERER_VERSION) -> str:
    """Validate against the selected identity; only legacy v11 accepts a missing digest."""
    contract = contract_for_identity(renderer_id, renderer_version)
    expected = contract.digest()
    if digest is None and contract is PENCIL_CONTRACT:
        return expected
    if digest is None or str(digest) != expected:
        raise UnsupportedRendererError(
            "render profile was bound to a different renderer contract "
            f"({str(digest)[:12]}…, selected {expected[:12]}…); exact replay is not "
            "possible with this package. " + REPLAY_RELEASE_HINT
        )
    return expected


__all__ = [
    "CONTRACT_SCHEMA",
    "PENCIL_CONTRACT",
    "OPACITY_NORMALIZED_CONTRACT",
    "PRESSURE_LIFT_CONTRACT",
    "CONTACT_WIDTH_CONTRACT",
    "contract_for_identity",
    "RENDERER_CONTRACT_DIGEST",
    "RENDERER_ID",
    "RENDERER_VERSION",
    "RendererContract",
    "UnsupportedRendererError",
    "canonical_identity",
    "verify_contract_digest",
]
