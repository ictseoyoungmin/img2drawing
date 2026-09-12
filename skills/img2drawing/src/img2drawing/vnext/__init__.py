"""Stage-agnostic vNext workflow surfaces."""

from .construction import (
    CONSTRUCTION_PHASES,
    ConstructionMark,
    InitialConstruct,
    InitialConstructResult,
    PoseObservation,
    author_initial_construct,
    inspect_initial_construct,
    observe_pose,
)
from .correction import CorrectionRecord, ResidualRecord
from .completion import FINISH_RECORD_SCHEMA, FinishRecord
from .render_profile import RENDER_PROFILE_SCHEMA, RenderProfile
from .reference_authority import (
    CONSTRAINT_DISPOSITIONS,
    REFERENCE_AUTHORITY_SCHEMA,
    REFERENCE_CONSTRAINT_SCHEMA,
    ReferenceAuthority,
    ReferenceConstraint,
    ReferenceUnavailableError,
)
from .output import (
    RENDER_ARTIFACT_SCHEMA,
    REPLAY_EXPORT_SCHEMA,
    RenderArtifact,
    ReplayExport,
)
from .evidence import EvidencePolicy, EvidenceReadRecord, EvidenceTelemetry
from .editing import (
    AUTHORED_ELEMENT_SCHEMA,
    AUTHORING_SUMMARY_SCHEMA,
    ELEMENT_STATUSES,
    ELEMENT_TYPES,
    AuthoredElement,
    AuthoringSummary,
)
from .authoring import retune_stroke, retune_strokes, sample_catmull_rom
from .intent import (
    COMPATIBILITY_INTENTS,
    DRAWING_MODES,
    FINISH_INTENTS,
    FINISH_GUIDE_SCHEMA,
    FINISH_RELATION_SCHEMA,
    REFERENCE_MODES,
    STYLE_PROFILES,
    DrawingIntent,
    FinishGuide,
    FinishRelation,
    IntentChangeRecord,
    IntentProvenance,
    ModeGuide,
    StyleClarificationRequired,
    StyleConflictError,
    StyleGuide,
    compatibility_intent,
    resolve_mode_guide,
    resolve_finish_guide,
    resolve_style_guide,
)
from .markmaking import (
    MARKMAKING_SCHEMA,
    MATERIAL_POLICIES,
    MATERIAL_POLICY_REVISION,
    SEMANTIC_STROKE_ROLES,
    TERMINAL_MODES,
    TOOL_PRESETS,
    TOOL_PRESET_REVISION,
    MaterialPolicy,
    ResolvedMark,
    ToolPreset,
    material_policy_for_style,
    resolve_mark_for_intent,
    resolve_markmaking,
)
from .session import DrawingSession
from .value import replace_fill_region

__all__ = [
    "CONSTRUCTION_PHASES",
    "CorrectionRecord",
    "FINISH_RECORD_SCHEMA",
    "FinishRecord",
    "RENDER_PROFILE_SCHEMA",
    "RenderProfile",
    "CONSTRAINT_DISPOSITIONS",
    "REFERENCE_AUTHORITY_SCHEMA",
    "REFERENCE_CONSTRAINT_SCHEMA",
    "ReferenceAuthority",
    "ReferenceConstraint",
    "ReferenceUnavailableError",
    "RENDER_ARTIFACT_SCHEMA",
    "REPLAY_EXPORT_SCHEMA",
    "RenderArtifact",
    "ReplayExport",
    "ConstructionMark",
    "DrawingSession",
    "EvidencePolicy",
    "EvidenceReadRecord",
    "EvidenceTelemetry",
    "AUTHORED_ELEMENT_SCHEMA",
    "AUTHORING_SUMMARY_SCHEMA",
    "ELEMENT_STATUSES",
    "ELEMENT_TYPES",
    "AuthoredElement",
    "AuthoringSummary",
    "COMPATIBILITY_INTENTS",
    "DRAWING_MODES",
    "FINISH_INTENTS",
    "FINISH_GUIDE_SCHEMA",
    "FINISH_RELATION_SCHEMA",
    "REFERENCE_MODES",
    "STYLE_PROFILES",
    "DrawingIntent",
    "FinishGuide",
    "FinishRelation",
    "IntentChangeRecord",
    "IntentProvenance",
    "ModeGuide",
    "StyleClarificationRequired",
    "StyleConflictError",
    "StyleGuide",
    "compatibility_intent",
    "resolve_finish_guide",
    "resolve_mode_guide",
    "resolve_style_guide",
    "MARKMAKING_SCHEMA",
    "MATERIAL_POLICIES",
    "MATERIAL_POLICY_REVISION",
    "SEMANTIC_STROKE_ROLES",
    "TERMINAL_MODES",
    "TOOL_PRESETS",
    "TOOL_PRESET_REVISION",
    "MaterialPolicy",
    "ResolvedMark",
    "ToolPreset",
    "material_policy_for_style",
    "resolve_mark_for_intent",
    "resolve_markmaking",
    "InitialConstruct",
    "InitialConstructResult",
    "PoseObservation",
    "ResidualRecord",
    "author_initial_construct",
    "inspect_initial_construct",
    "observe_pose",
    "replace_fill_region",
    "retune_stroke",
    "retune_strokes",
    "sample_catmull_rom",
]

# Bind the stable vNext public session/output hooks to the renderer registry only after
# the ordinary public modules above have finished importing. This keeps the worker-facing
# API source-opaque while making RenderProfile renderer identity authoritative at runtime.
from .renderer_binding import bind_vnext_renderer_runtime as _bind_vnext_renderer_runtime

_bind_vnext_renderer_runtime()
del _bind_vnext_renderer_runtime

# Gesture is a user-facing drawing mode, not a workflow stage. Bind it after the base intent
# module is loaded, then refresh the exported mode tuple so public discovery stays consistent.
from .gesture_binding import bind_gesture_intent_runtime as _bind_gesture_intent_runtime

DRAWING_MODES = _bind_gesture_intent_runtime()
del _bind_gesture_intent_runtime
