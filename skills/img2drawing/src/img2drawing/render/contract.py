"""Renderer identity and the parameter contract that binds persisted sessions to pixels.

The package ships exactly one renderer. Its identity and contract digest are persisted in
every ``RenderProfile`` so a session can prove which renderer produced its pixels. Sessions
bound to an identity this package cannot reproduce exactly fail closed; they must be replayed
with the published release that shipped that renderer.
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
    """Return the current identity for a persisted one, or fail closed."""

    key = (str(renderer_id).strip(), str(renderer_version).strip())
    if key == PENCIL_CONTRACT.identity or key in _EQUIVALENT_IDENTITIES:
        return PENCIL_CONTRACT.identity
    raise UnsupportedRendererError(
        f"renderer {key[0]!r}/{key[1]!r} is not available in this package; "
        f"current renderer is {RENDERER_ID}/{RENDERER_VERSION}. To reproduce the session exactly, "
        + REPLAY_RELEASE_HINT
    )


def verify_contract_digest(digest: str | None) -> str:
    """Accept only the current contract digest; ``None`` means a pre-digest v1.0.3 profile."""

    if digest is None:
        return RENDERER_CONTRACT_DIGEST
    if str(digest) != RENDERER_CONTRACT_DIGEST:
        raise UnsupportedRendererError(
            "render profile was bound to a different renderer contract "
            f"({str(digest)[:12]}…, current {RENDERER_CONTRACT_DIGEST[:12]}…); exact replay is not "
            "possible with this package. " + REPLAY_RELEASE_HINT
        )
    return RENDERER_CONTRACT_DIGEST


__all__ = [
    "CONTRACT_SCHEMA",
    "PENCIL_CONTRACT",
    "RENDERER_CONTRACT_DIGEST",
    "RENDERER_ID",
    "RENDERER_VERSION",
    "RendererContract",
    "UnsupportedRendererError",
    "canonical_identity",
    "verify_contract_digest",
]
