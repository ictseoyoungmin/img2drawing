"""Canonical img2drawing public API.

Normal Agent/user code should discover one orchestration surface: ``DrawingSession`` plus
its small declarative input types. Specialized inspection, evidence, record, and low-level
history utilities remain available from their explicit modules.

Names that were advertised at the package root before 0.6.0rc2 remain available through
deprecated lazy shims so existing callers do not break abruptly. They are intentionally
absent from ``__all__`` and ``dir(img2drawing)``. Historical R23 compatibility belongs
under ``img2drawing.legacy.r23``.
"""

from importlib import import_module
import warnings

from ._version import __version__
from .vnext import (
    ConstructionMark,
    DrawingIntent,
    DrawingSession,
    InitialConstruct,
    PoseObservation,
    ReferenceAuthority,
    ReferenceConstraint,
    ReferenceUnavailableError,
    RenderProfile,
    author_initial_construct,
    inspect_initial_construct,
    observe_pose,
)


# The root compatibility map preserves pre-rc2 direct imports without advertising those
# names as normal framework entry points. New code should import the owning public module.
_ROOT_COMPAT_TARGETS: dict[str, tuple[str, str]] = {
    # Low-level drawing/history.
    "DrawingAction": ("img2drawing.core", "DrawingAction"),
    "AgentDrawingSession": ("img2drawing.core", "AgentDrawingSession"),
    "Stroke": ("img2drawing.core", "Stroke"),
    "StrokeIR": ("img2drawing.core", "StrokeIR"),
    "CanvasHistory": ("img2drawing.core", "CanvasHistory"),
    "FillRegion": ("img2drawing.core.fill", "FillRegion"),
    "ReservedLight": ("img2drawing.core.fill", "ReservedLight"),
    "expand_fill": ("img2drawing.core.fill", "expand_fill"),

    # Optional observation/material evidence.
    "MaterialSample": ("img2drawing.observation.palette", "MaterialSample"),
    "SubjectPalette": ("img2drawing.observation.palette", "SubjectPalette"),

    # Optional tone helpers.
    "ToneRecipe": ("img2drawing.render.tone_scale", "ToneRecipe"),
    "available_values": ("img2drawing.render.tone_scale", "available_values"),
    "resolve_tone": ("img2drawing.render.tone_scale", "resolve_tone"),

    # Specialized inspection namespace.
    "Box": ("img2drawing.inspection", "Box"),
    "GroundGuide": ("img2drawing.inspection", "GroundGuide"),
    "Grid": ("img2drawing.inspection", "Grid"),
    "GridMeasurement": ("img2drawing.inspection", "GridMeasurement"),
    "InspectionSheet": ("img2drawing.inspection", "InspectionSheet"),
    "Measurement": ("img2drawing.inspection", "Measurement"),
    "PixelSample": ("img2drawing.inspection", "PixelSample"),
    "PlumbLine": ("img2drawing.inspection", "PlumbLine"),
    "Point": ("img2drawing.inspection", "Point"),
    "PointMapping": ("img2drawing.inspection", "PointMapping"),
    "Profile": ("img2drawing.inspection", "Profile"),
    "Registration": ("img2drawing.inspection", "Registration"),
    "ROI": ("img2drawing.inspection", "ROI"),
    "Size": ("img2drawing.inspection", "Size"),
    "angle": ("img2drawing.inspection", "angle"),
    "distance": ("img2drawing.inspection", "distance"),
    "drawing_state_hash": ("img2drawing.inspection", "drawing_state_hash"),
    "drawing_state_payload": ("img2drawing.inspection", "drawing_state_payload"),
    "ground_guide": ("img2drawing.inspection", "ground_guide"),
    "grid": ("img2drawing.inspection", "grid"),
    "horizontal_profile": ("img2drawing.inspection", "horizontal_profile"),
    "map_subject_to_canvas": ("img2drawing.inspection", "map_subject_to_canvas"),
    "point": ("img2drawing.inspection", "point"),
    "plumb_line": ("img2drawing.inspection", "plumb_line"),
    "sample_pixel": ("img2drawing.inspection", "sample_pixel"),
    "stage_free_drawing_state_hash": ("img2drawing.inspection", "stage_free_drawing_state_hash"),
    "vertical_profile": ("img2drawing.inspection", "vertical_profile"),

    # Advanced vNext records, schemas, guides, and compatibility aliases.
    "VNextDrawingSession": ("img2drawing.vnext", "DrawingSession"),
    "CONSTRUCTION_PHASES": ("img2drawing.vnext", "CONSTRUCTION_PHASES"),
    "CONSTRAINT_DISPOSITIONS": ("img2drawing.vnext", "CONSTRAINT_DISPOSITIONS"),
    "CorrectionRecord": ("img2drawing.vnext", "CorrectionRecord"),
    "InitialConstructResult": ("img2drawing.vnext", "InitialConstructResult"),
    "ResidualRecord": ("img2drawing.vnext", "ResidualRecord"),
    "EvidencePolicy": ("img2drawing.vnext", "EvidencePolicy"),
    "EvidenceReadRecord": ("img2drawing.vnext", "EvidenceReadRecord"),
    "EvidenceTelemetry": ("img2drawing.vnext", "EvidenceTelemetry"),
    "AUTHORED_ELEMENT_SCHEMA": ("img2drawing.vnext", "AUTHORED_ELEMENT_SCHEMA"),
    "AUTHORING_SUMMARY_SCHEMA": ("img2drawing.vnext", "AUTHORING_SUMMARY_SCHEMA"),
    "ELEMENT_STATUSES": ("img2drawing.vnext", "ELEMENT_STATUSES"),
    "ELEMENT_TYPES": ("img2drawing.vnext", "ELEMENT_TYPES"),
    "AuthoredElement": ("img2drawing.vnext", "AuthoredElement"),
    "AuthoringSummary": ("img2drawing.vnext", "AuthoringSummary"),
    "replace_fill_region": ("img2drawing.vnext", "replace_fill_region"),
    "COMPATIBILITY_INTENTS": ("img2drawing.vnext", "COMPATIBILITY_INTENTS"),
    "DRAWING_MODES": ("img2drawing.vnext", "DRAWING_MODES"),
    "FINISH_INTENTS": ("img2drawing.vnext", "FINISH_INTENTS"),
    "FINISH_GUIDE_SCHEMA": ("img2drawing.vnext", "FINISH_GUIDE_SCHEMA"),
    "FINISH_RELATION_SCHEMA": ("img2drawing.vnext", "FINISH_RELATION_SCHEMA"),
    "FINISH_RECORD_SCHEMA": ("img2drawing.vnext", "FINISH_RECORD_SCHEMA"),
    "RENDER_PROFILE_SCHEMA": ("img2drawing.vnext", "RENDER_PROFILE_SCHEMA"),
    "RENDER_ARTIFACT_SCHEMA": ("img2drawing.vnext", "RENDER_ARTIFACT_SCHEMA"),
    "REPLAY_EXPORT_SCHEMA": ("img2drawing.vnext", "REPLAY_EXPORT_SCHEMA"),
    "REFERENCE_MODES": ("img2drawing.vnext", "REFERENCE_MODES"),
    "REFERENCE_AUTHORITY_SCHEMA": ("img2drawing.vnext", "REFERENCE_AUTHORITY_SCHEMA"),
    "REFERENCE_CONSTRAINT_SCHEMA": ("img2drawing.vnext", "REFERENCE_CONSTRAINT_SCHEMA"),
    "STYLE_PROFILES": ("img2drawing.vnext", "STYLE_PROFILES"),
    "FinishGuide": ("img2drawing.vnext", "FinishGuide"),
    "FinishRelation": ("img2drawing.vnext", "FinishRelation"),
    "FinishRecord": ("img2drawing.vnext", "FinishRecord"),
    "RenderArtifact": ("img2drawing.vnext", "RenderArtifact"),
    "ReplayExport": ("img2drawing.vnext", "ReplayExport"),
    "IntentChangeRecord": ("img2drawing.vnext", "IntentChangeRecord"),
    "IntentProvenance": ("img2drawing.vnext", "IntentProvenance"),
    "ModeGuide": ("img2drawing.vnext", "ModeGuide"),
    "StyleClarificationRequired": ("img2drawing.vnext", "StyleClarificationRequired"),
    "StyleConflictError": ("img2drawing.vnext", "StyleConflictError"),
    "StyleGuide": ("img2drawing.vnext", "StyleGuide"),
    "compatibility_intent": ("img2drawing.vnext", "compatibility_intent"),
    "resolve_finish_guide": ("img2drawing.vnext", "resolve_finish_guide"),
    "resolve_mode_guide": ("img2drawing.vnext", "resolve_mode_guide"),
    "resolve_style_guide": ("img2drawing.vnext", "resolve_style_guide"),
}


__all__ = [
    "__version__",
    "DrawingSession",
    "DrawingIntent",
    "ReferenceAuthority",
    "ReferenceConstraint",
    "ReferenceUnavailableError",
    "RenderProfile",
    "PoseObservation",
    "InitialConstruct",
    "ConstructionMark",
    "author_initial_construct",
    "inspect_initial_construct",
    "observe_pose",
]


def __getattr__(name: str):
    target = _ROOT_COMPAT_TARGETS.get(name)
    if target is not None:
        module_name, attribute_name = target
        warnings.warn(
            f"img2drawing.{name} is a pre-0.6.0rc2 root-compat shim; import "
            f"{attribute_name} from {module_name} instead. The name is no longer part of "
            "the canonical package-root API.",
            DeprecationWarning,
            stacklevel=2,
        )
        return getattr(import_module(module_name), attribute_name)

    legacy = import_module("img2drawing.legacy.r23")
    if name not in legacy.LEGACY_EXPORTS:
        raise AttributeError(name)
    warnings.warn(
        f"img2drawing.{name} is an R23 compatibility shim; import it from "
        "img2drawing.legacy.r23 instead",
        DeprecationWarning,
        stacklevel=2,
    )
    return getattr(legacy, name)


def __dir__() -> list[str]:
    """Expose only the canonical normal-user root surface to discovery tools."""

    return sorted(__all__)
