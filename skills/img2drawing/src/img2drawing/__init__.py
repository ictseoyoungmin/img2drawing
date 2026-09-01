"""Canonical, stage-free img2drawing public API.

Historical R23 names are not advertised here. Existing direct imports resolve
as deprecated lazy shims; explicit compatibility code belongs under
``img2drawing.legacy.r23``.
"""

from importlib import import_module
import warnings

from ._version import __version__
from .core import DrawingAction, AgentDrawingSession, Stroke, StrokeIR, CanvasHistory
from .core.fill import FillRegion, ReservedLight, expand_fill
from .observation.palette import MaterialSample, SubjectPalette
from .render.tone_scale import ToneRecipe, available_values, resolve_tone
from .inspection import (
    Box, GroundGuide, Grid, GridMeasurement, InspectionSheet, Measurement,
    PixelSample, PlumbLine, Point, PointMapping, Profile, Registration, ROI, Size,
    angle, distance, drawing_state_hash, drawing_state_payload, ground_guide, grid,
    horizontal_profile, map_subject_to_canvas, point, plumb_line, sample_pixel,
    stage_free_drawing_state_hash, vertical_profile,
)
from .vnext import (
    CONSTRUCTION_PHASES,
    CONSTRAINT_DISPOSITIONS,
    ConstructionMark,
    CorrectionRecord,
    DrawingSession,
    EvidencePolicy,
    EvidenceReadRecord,
    EvidenceTelemetry,
    COMPATIBILITY_INTENTS,
    DRAWING_MODES,
    FINISH_INTENTS,
    FINISH_GUIDE_SCHEMA,
    FINISH_RELATION_SCHEMA,
    FINISH_RECORD_SCHEMA,
    RENDER_PROFILE_SCHEMA,
    RENDER_ARTIFACT_SCHEMA,
    REPLAY_EXPORT_SCHEMA,
    REFERENCE_MODES,
    REFERENCE_AUTHORITY_SCHEMA,
    REFERENCE_CONSTRAINT_SCHEMA,
    STYLE_PROFILES,
    DrawingIntent,
    FinishGuide,
    FinishRelation,
    FinishRecord,
    RenderProfile,
    ReferenceAuthority,
    ReferenceConstraint,
    ReferenceUnavailableError,
    RenderArtifact,
    ReplayExport,
    IntentChangeRecord,
    IntentProvenance,
    ModeGuide,
    StyleGuide,
    InitialConstruct,
    InitialConstructResult,
    PoseObservation,
    ResidualRecord,
    author_initial_construct,
    inspect_initial_construct,
    observe_pose,
    compatibility_intent,
    replace_fill_region,
    resolve_mode_guide,
    resolve_finish_guide,
    resolve_style_guide,
)

VNextDrawingSession = DrawingSession


def __getattr__(name: str):
    legacy = import_module("img2drawing.legacy.r23")
    if name not in legacy.LEGACY_EXPORTS:
        raise AttributeError(name)
    warnings.warn(
        f"img2drawing.{name} is an R23 compatibility shim; import it from "
        f"img2drawing.legacy.r23 instead",
        DeprecationWarning,
        stacklevel=2,
    )
    value = getattr(legacy, name)
    globals()[name] = value
    return value


__all__ = [
    "__version__", "DrawingAction", "AgentDrawingSession", "Stroke", "StrokeIR", "CanvasHistory",
    "FillRegion", "ReservedLight", "expand_fill", "SubjectPalette", "MaterialSample", "ToneRecipe", "resolve_tone", "available_values",
    "Box", "GroundGuide", "Grid", "GridMeasurement", "InspectionSheet", "Measurement", "PixelSample", "PlumbLine", "Point",
    "PointMapping", "Profile", "Registration", "ROI", "Size", "angle", "distance", "drawing_state_hash", "drawing_state_payload",
    "ground_guide", "grid", "horizontal_profile", "map_subject_to_canvas", "point", "plumb_line", "sample_pixel",
    "stage_free_drawing_state_hash", "vertical_profile", "DrawingSession", "VNextDrawingSession", "CONSTRUCTION_PHASES", "CONSTRAINT_DISPOSITIONS",
    "ConstructionMark", "CorrectionRecord", "InitialConstruct", "InitialConstructResult", "PoseObservation",
    "ResidualRecord", "EvidencePolicy", "EvidenceReadRecord", "EvidenceTelemetry", "author_initial_construct", "inspect_initial_construct", "observe_pose", "replace_fill_region",
    "COMPATIBILITY_INTENTS", "DRAWING_MODES", "FINISH_INTENTS", "FINISH_GUIDE_SCHEMA", "FINISH_RELATION_SCHEMA", "FINISH_RECORD_SCHEMA", "RENDER_PROFILE_SCHEMA", "RENDER_ARTIFACT_SCHEMA", "REPLAY_EXPORT_SCHEMA", "REFERENCE_MODES", "REFERENCE_AUTHORITY_SCHEMA", "REFERENCE_CONSTRAINT_SCHEMA", "STYLE_PROFILES",
    "DrawingIntent", "FinishGuide", "FinishRelation", "FinishRecord", "RenderProfile", "ReferenceAuthority", "ReferenceConstraint", "ReferenceUnavailableError", "RenderArtifact", "ReplayExport", "IntentChangeRecord", "IntentProvenance", "ModeGuide", "StyleGuide",
    "compatibility_intent", "resolve_finish_guide", "resolve_mode_guide", "resolve_style_guide",
]
