from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
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


# v9 is the already-published historical replay authority. Its implementation stays
# frozen in pillow_pencil_contact.py; this contract gives registry/cache identity an
# explicit immutable anchor without changing any v9 pixels.
V9_CONTRACT = RendererContract(
    renderer_id="pillow-pencil-contact-v9",
    renderer_version="1",
    parameters=(
        ("authority", "published-v1.0.2-historical-replay"),
        ("material_model", "continuous-contact-p9"),
    ),
)


# Candidate v10 material contract derived from the graphite / terminal research.
# These values are renderer semantics, not user-adjustable style knobs. Changing one
# requires a new renderer identity/version rather than mutating a published contract.
V10_CONTRACT = RendererContract(
    renderer_id="pillow-pencil-contact-v10",
    renderer_version="1",
    parameters=(
        ("authored_contrast_gamma", 0.42),
        ("broad_diameter_scale", 0.90),
        ("broad_flow_gain", 1.28),
        ("broad_full", 10.0),
        ("broad_pigment_darken", 0.22),
        ("broad_start", 4.5),
        ("default_material_policy", "canonical-pencil"),
        ("deposition_variability_amp", 0.24),
        ("deposition_variability_coarse", 7.5),
        ("deposition_variability_fine", 3.6),
        ("deposition_variability_fine_mix", 0.32),
        ("material_model", "pixel-tooth-low-flow-radial-contact"),
        ("material_policy_model", "resolved-markmaking-v1"),
        ("policy_core_floor_model", "authored-core-preservation-v1"),
        ("policy_grain_model", "style-governed-page-tooth-v1"),
        ("seed_identity_model", "stage-free-render-seed-v1"),
        ("terminal_model", "physical-px-expressive-v1"),
        ("thin_flick_model", "specialized-continuity-v1"),
    ),
)


def contract_for(renderer_id: str, renderer_version: str | int) -> RendererContract:
    key = (str(renderer_id), str(renderer_version))
    if key == (V9_CONTRACT.renderer_id, V9_CONTRACT.renderer_version):
        return V9_CONTRACT
    if key == (V10_CONTRACT.renderer_id, V10_CONTRACT.renderer_version):
        return V10_CONTRACT
    raise ValueError(f"no renderer contract registered for {key[0]!r}/{key[1]!r}")


__all__ = [
    "CONTRACT_SCHEMA",
    "RendererContract",
    "V9_CONTRACT",
    "V10_CONTRACT",
    "contract_for",
]
