"""Small public runtime discovery surface for ordinary drawing workers.

This module exists so an Agent can confirm that img2drawing provides a supported authoring
runtime without reading the implementation tree.  It intentionally reports capabilities and
boundaries, not renderer classes, cache internals, module paths, or persistence details.
"""

from __future__ import annotations

from dataclasses import dataclass


RUNTIME_CAPABILITY_SCHEMA = "img2drawing.runtime.capabilities.v1"


@dataclass(frozen=True)
class RuntimeCapabilities:
    """Source-opaque description of the supported worker-facing runtime."""

    schema: str = RUNTIME_CAPABILITY_SCHEMA
    orchestration: str = "DrawingSession"
    final_authoring_runtime: bool = True
    implementation_read_required: bool = False
    bespoke_raster_authoring_supported: bool = False
    capability_gap_policy: str = "report-not-bypass"
    public_namespaces: tuple[str, ...] = (
        "img2drawing",
        "img2drawing.vnext",
        "img2drawing.inspection",
        "img2drawing.observation",
        "img2drawing.runtime",
    )
    supported_authoring_operations: tuple[str, ...] = (
        "draw",
        "replace-stroke",
        "soften-stroke",
        "delete-stroke",
        "fill",
        "replace-fill",
        "inspect",
        "render",
        "replay",
        "timelapse",
    )
    markmaking_contract: str = "semantic-role -> public tool preset -> resolved authored state"
    prohibited_final_authoring_bypasses: tuple[str, ...] = (
        "hand-written Pillow/ImageDraw raster drawing",
        "raw OpenCV raster drawing",
        "bespoke SVG/canvas rasterizer",
        "private renderer helper used as an authoring API",
    )

    def to_dict(self) -> dict[str, object]:
        return {
            "schema": self.schema,
            "orchestration": self.orchestration,
            "final_authoring_runtime": self.final_authoring_runtime,
            "implementation_read_required": self.implementation_read_required,
            "bespoke_raster_authoring_supported": self.bespoke_raster_authoring_supported,
            "capability_gap_policy": self.capability_gap_policy,
            "public_namespaces": list(self.public_namespaces),
            "supported_authoring_operations": list(self.supported_authoring_operations),
            "markmaking_contract": self.markmaking_contract,
            "prohibited_final_authoring_bypasses": list(self.prohibited_final_authoring_bypasses),
        }


_RUNTIME_CAPABILITIES = RuntimeCapabilities()


def runtime_capabilities() -> RuntimeCapabilities:
    """Return the stable worker-facing capability/boundary manifest.

    The result is deliberately sufficient for capability discovery while remaining opaque to
    implementation details.  A worker that needs a missing capability should report a runtime
    gap rather than inspect private modules and invent a replacement authoring path.
    """

    return _RUNTIME_CAPABILITIES


__all__ = [
    "RUNTIME_CAPABILITY_SCHEMA",
    "RuntimeCapabilities",
    "runtime_capabilities",
]
