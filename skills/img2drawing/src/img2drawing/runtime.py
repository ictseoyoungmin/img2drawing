"""Small public runtime discovery surface for ordinary drawing workers.

This module exists so an Agent can confirm that img2drawing provides a supported authoring
runtime without reading the implementation tree.  It intentionally reports capabilities and
boundaries, not renderer classes, cache internals, module paths, or persistence details.
"""

from __future__ import annotations

from dataclasses import dataclass


RUNTIME_CAPABILITY_SCHEMA = "img2drawing.runtime.capabilities.v2"


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
        "img2drawing.authoring",
        "img2drawing.inspection",
        "img2drawing.observation",
        "img2drawing.session",
        "img2drawing.runtime",
    )
    authoring_operations: tuple[str, ...] = (
        "draw",
        "replace-stroke",
        "soft-lift",
        "delete-stroke",
        "replace-segment",
        "soft-lift-segment",
        "erase-path",
    )
    output_operations: tuple[str, ...] = (
        "inspect",
        "render",
        "replay",
        "timelapse",
    )
    supported_operations: tuple[str, ...] = authoring_operations + output_operations

    @property
    def supported_authoring_operations(self) -> tuple[str, ...]:
        """Compatibility alias for the pre-v1.1.1 mixed operation list."""

        return self.supported_operations
    authoring_entrypoints: tuple[str, ...] = (
        "DrawingSession.draw",
        "DrawingSession.replace_stroke",
        "DrawingSession.soft_lift",
        "DrawingSession.delete_stroke",
        "DrawingSession.replace_segment",
        "DrawingSession.soft_lift_segment",
        "DrawingSession.erase_path",
    )
    authoring_helpers: tuple[str, ...] = (
        "img2drawing.authoring.SemanticGroup",
        "img2drawing.authoring.record_semantic_groups",
        "img2drawing.authoring.inspect_semantic_groups",
        "img2drawing.authoring.review_semantic_group",
        "img2drawing.authoring.prepare_group_transform",
        "img2drawing.authoring.retire_group_guides",
        "img2drawing.authoring.inspect_tonal_proposals",
        "img2drawing.authoring.ContactWidthProfile",
        "img2drawing.authoring.read_contact_width_profile",
        "img2drawing.authoring.TonalPressureAdjustment",
        "img2drawing.authoring.prepare_tonal_pressure_edits",
        "img2drawing.authoring.resample_polyline",
        "img2drawing.authoring.sample_cubic_bezier",
        "img2drawing.authoring.pressure_along_path",
        "img2drawing.authoring.curve_join",
        "img2drawing.authoring.deform_interval",
        "img2drawing.authoring.StrokeEdit",
        "img2drawing.authoring.transform_strokes",
        "img2drawing.authoring.apply_stroke_edits",
        "img2drawing.authoring.preview_stroke_edits",
        "img2drawing.authoring.ProjectionCamera",
        "img2drawing.authoring.VolumeStation",
        "img2drawing.authoring.ProjectedVolume",
        "img2drawing.authoring.inspect_attachment",
        "img2drawing.authoring.align_attachment",
        "img2drawing.authoring.prepare_volume_edits",
        "img2drawing.authoring.CurveDefinition",
        "img2drawing.authoring.read_parametric_curve",
        "img2drawing.authoring.ProjectedSection",
        "img2drawing.authoring.projected_ellipse",
        "img2drawing.authoring.projected_envelope",
        "img2drawing.authoring.author_projection_guides",
        "img2drawing.authoring.reshape_stroke",
        "img2drawing.authoring.retune_stroke",
        "img2drawing.authoring.retune_strokes",
    )
    observation_helpers: tuple[str, ...] = (
        "img2drawing.inspection.inspect_tonal_interval",
        "img2drawing.inspection.TonalBandProbe",
        "img2drawing.inspection.inspect_tonal_bands",
        "img2drawing.inspection.compare_tonal_bands",
        "img2drawing.inspection.TonalPatch",
        "img2drawing.inspection.compare_tonal_patches",
        "img2drawing.inspection.inspect_tonal_patches",
        "img2drawing.observation.Landmark",
        "img2drawing.observation.LandmarkSet",
        "img2drawing.observation.compare_landmarks",
        "img2drawing.observation.compare_ratios",
        "img2drawing.observation.compare_axes",
        "img2drawing.observation.cross_section",
        "img2drawing.observation.compare_negative_space",
        "img2drawing.observation.occlusion_relation",
    )
    render_profile_entrypoints: tuple[str, ...] = (
        "RenderProfile.canonical",
        "RenderProfile.opacity_normalized",
    )
    output_entrypoints: tuple[str, ...] = (
        "DrawingSession.inspect",
        "DrawingSession.render_final",
        "DrawingSession.render_at",
        "DrawingSession.export_timelapse",
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
            "supported_operations": list(self.supported_operations),
            "authoring_operations": list(self.authoring_operations),
            "output_operations": list(self.output_operations),
            # Compatibility key retained for callers that consumed the v1.1.0 payload.
            "supported_authoring_operations": list(self.supported_authoring_operations),
            "authoring_entrypoints": list(self.authoring_entrypoints),
            "authoring_helpers": list(self.authoring_helpers),
            "output_entrypoints": list(self.output_entrypoints),
            "render_profile_entrypoints": list(self.render_profile_entrypoints),
            "observation_helpers": list(self.observation_helpers),
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
