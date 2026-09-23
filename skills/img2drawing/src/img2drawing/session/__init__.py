"""``DrawingSession`` and the records it persists.

``DrawingSession`` is the single orchestration surface: it owns authored history, inspection
evidence, residual/correction provenance, intent, reference authority, the render profile, and
finish records. The declarative inputs are re-exported from the package root; this namespace
also exposes the record types and schemas for framework and debugging work.
"""

from ..render.artifact import RENDER_ARTIFACT_SCHEMA, RenderArtifact
from ..render.profile import RENDER_PROFILE_SCHEMA, RenderProfile
from ..timelapse import REPLAY_EXPORT_SCHEMA, ReplayExport
from .completion import FINISH_RECORD_SCHEMA, FinishRecord
from .correction import CorrectionRecord, ResidualRecord
from .drawing_session import DrawingSession
from .editing import (
    AUTHORED_ELEMENT_SCHEMA,
    AUTHORING_SUMMARY_SCHEMA,
    ELEMENT_STATUSES,
    ELEMENT_TYPES,
    AuthoredElement,
    AuthoringSummary,
)
from .evidence import EvidencePolicy, EvidenceReadRecord, EvidenceTelemetry
from .intent import (
    COMPATIBILITY_INTENTS,
    DRAWING_MODES,
    FINISH_GUIDE_SCHEMA,
    FINISH_INTENTS,
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
    resolve_finish_guide,
    resolve_mode_guide,
    resolve_style_guide,
)
from .reference import (
    CONSTRAINT_DISPOSITIONS,
    REFERENCE_AUTHORITY_SCHEMA,
    REFERENCE_CONSTRAINT_SCHEMA,
    ReferenceAuthority,
    ReferenceConstraint,
    ReferenceUnavailableError,
)

__all__ = [
    "AUTHORED_ELEMENT_SCHEMA",
    "AUTHORING_SUMMARY_SCHEMA",
    "COMPATIBILITY_INTENTS",
    "CONSTRAINT_DISPOSITIONS",
    "DRAWING_MODES",
    "ELEMENT_STATUSES",
    "ELEMENT_TYPES",
    "FINISH_GUIDE_SCHEMA",
    "FINISH_INTENTS",
    "FINISH_RECORD_SCHEMA",
    "FINISH_RELATION_SCHEMA",
    "REFERENCE_AUTHORITY_SCHEMA",
    "REFERENCE_CONSTRAINT_SCHEMA",
    "REFERENCE_MODES",
    "RENDER_ARTIFACT_SCHEMA",
    "RENDER_PROFILE_SCHEMA",
    "REPLAY_EXPORT_SCHEMA",
    "STYLE_PROFILES",
    "AuthoredElement",
    "AuthoringSummary",
    "CorrectionRecord",
    "DrawingIntent",
    "DrawingSession",
    "EvidencePolicy",
    "EvidenceReadRecord",
    "EvidenceTelemetry",
    "FinishGuide",
    "FinishRecord",
    "FinishRelation",
    "IntentChangeRecord",
    "IntentProvenance",
    "ModeGuide",
    "ReferenceAuthority",
    "ReferenceConstraint",
    "ReferenceUnavailableError",
    "RenderArtifact",
    "RenderProfile",
    "ReplayExport",
    "ResidualRecord",
    "StyleClarificationRequired",
    "StyleConflictError",
    "StyleGuide",
    "compatibility_intent",
    "resolve_finish_guide",
    "resolve_mode_guide",
    "resolve_style_guide",
]
