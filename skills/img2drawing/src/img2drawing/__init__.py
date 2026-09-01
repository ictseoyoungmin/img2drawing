"""Public package exports.

The vNext surface is intentionally importable without importing the legacy
stage/review workflow. Legacy names remain available through lazy compatibility
exports so existing R23 callers keep their public import shape.
"""

from importlib import import_module

from ._version import __version__
from .core import DrawingAction, AgentDrawingSession, Stroke, StrokeIR, CanvasHistory
from .core.fill import FillRegion, ReservedLight, expand_fill
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
    ConstructionMark,
    CorrectionRecord,
    DrawingSession,
    EvidencePolicy,
    EvidenceReadRecord,
    EvidenceTelemetry,
    COMPATIBILITY_INTENTS,
    DRAWING_MODES,
    FINISH_INTENTS,
    REFERENCE_MODES,
    STYLE_PROFILES,
    DrawingIntent,
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
    resolve_style_guide,
)

VNextDrawingSession = DrawingSession


_LAZY_EXPORTS = {
    "DrawingRun": ("img2drawing.run", "DrawingRun"),
    "DrawingRunResult": ("img2drawing.run", "DrawingRunResult"),
    "ObservationContract": ("img2drawing.observation", "ObservationContract"),
    "ViewObservation": ("img2drawing.observation", "ViewObservation"),
    "FrozenObservationRecord": ("img2drawing.observation", "FrozenObservationRecord"),
    "ObservationReopenRecord": ("img2drawing.observation", "ObservationReopenRecord"),
    "StageSpec": ("img2drawing.stages", "StageSpec"),
    "StageContract": ("img2drawing.stages", "StageContract"),
    "StageContractRegistry": ("img2drawing.stages", "StageContractRegistry"),
    "StageContractError": ("img2drawing.stages", "StageContractError"),
    "get_stage_registry": ("img2drawing.stages", "get_stage_registry"),
    "get_stage_contract_registry": ("img2drawing.stages", "get_stage_contract_registry"),
    "SubjectReference": ("img2drawing.reference", "SubjectReference"),
    "TaskStageTarget": ("img2drawing.reference", "TaskStageTarget"),
    "StageReferenceView": ("img2drawing.reference", "StageReferenceView"),
    "ReferenceBundle": ("img2drawing.reference", "ReferenceBundle"),
    "ReferenceBundleError": ("img2drawing.reference", "ReferenceBundleError"),
    "build_reference_bundle": ("img2drawing.reference", "build_reference_bundle"),
    "ABLATION_CONDITIONS": ("img2drawing.exemplar.ablation", "ABLATION_CONDITIONS"),
    "ModularGrammarCard": ("img2drawing.exemplar.ablation", "ModularGrammarCard"),
    "consume_grammar_card": ("img2drawing.exemplar.ablation", "consume_grammar_card"),
    "AblationTrial": ("img2drawing.exemplar.ablation", "AblationTrial"),
    "ExemplarAblationReport": ("img2drawing.exemplar.ablation", "ExemplarAblationReport"),
    "run_exemplar_ablation": ("img2drawing.exemplar.ablation", "run_exemplar_ablation"),
    "CropBox": ("img2drawing.review", "CropBox"),
    "LocalReviewError": ("img2drawing.review", "LocalReviewError"),
    "LocalReviewArtifacts": ("img2drawing.review", "LocalReviewArtifacts"),
    "ActionMemory": ("img2drawing.review", "ActionMemory"),
    "StagePassMemory": ("img2drawing.review", "StagePassMemory"),
    "ReopenRecord": ("img2drawing.review", "ReopenRecord"),
    "StageReviewRecord": ("img2drawing.review", "StageReviewRecord"),
    "ReferenceReviewArtifacts": ("img2drawing.review", "ReferenceReviewArtifacts"),
    "StaleReviewError": ("img2drawing.review", "StaleReviewError"),
    "REQUIRED_P3_REGIONS": ("img2drawing.review", "REQUIRED_P3_REGIONS"),
    "RegionClosureEntry": ("img2drawing.review", "RegionClosureEntry"),
    "RegionClosureManifest": ("img2drawing.review", "RegionClosureManifest"),
    "VisualFidelityReviewRecord": ("img2drawing.review", "VisualFidelityReviewRecord"),
    "blind_observation_projection": ("img2drawing.review", "blind_observation_projection"),
    "build_blind_visual_packet": ("img2drawing.review", "build_blind_visual_packet"),
    "P4_RESOLVED_REGIONS": ("img2drawing.review", "P4_RESOLVED_REGIONS"),
    "P5_RESOLVED_REGIONS": ("img2drawing.review", "P5_RESOLVED_REGIONS"),
    "ResolvedFormEntry": ("img2drawing.review", "ResolvedFormEntry"),
    "ResolvedFormManifest": ("img2drawing.review", "ResolvedFormManifest"),
    "ResolvedFormReviewRecord": ("img2drawing.review", "ResolvedFormReviewRecord"),
    "ConstructionRetirementRecord": ("img2drawing.review", "ConstructionRetirementRecord"),
    "IdentityFinishProfile": ("img2drawing.review", "IdentityFinishProfile"),
    "CalibrationSheet": ("img2drawing.review", "CalibrationSheet"),
    "IdentityPreflightResult": ("img2drawing.review", "IdentityPreflightResult"),
    "preflight_identity_finish": ("img2drawing.review", "preflight_identity_finish"),
    "IdentityFinishManifest": ("img2drawing.review", "IdentityFinishManifest"),
    "build_resolved_form_blind_packet": ("img2drawing.review", "build_resolved_form_blind_packet"),
    "AssistiveROIProposal": ("img2drawing.review", "AssistiveROIProposal"),
    "ExcludedRegion": ("img2drawing.review", "ExcludedRegion"),
    "AcceptedResidual": ("img2drawing.review", "AcceptedResidual"),
    "AdaptiveEvidencePolicy": ("img2drawing.review", "AdaptiveEvidencePolicy"),
    "PreviewArtifact": ("img2drawing.review", "PreviewArtifact"),
    "render_preview": ("img2drawing.review", "render_preview"),
    "EnvelopeStation": ("img2drawing.registration", "EnvelopeStation"),
    "RegionEnvelopeObservation": ("img2drawing.registration", "RegionEnvelopeObservation"),
    "RegionEnvelopeIntegrityError": ("img2drawing.registration", "RegionEnvelopeIntegrityError"),
    "EnvelopeIntegrity": ("img2drawing.registration", "EnvelopeIntegrity"),
    "AxisEnvelopeEvidence": ("img2drawing.registration", "AxisEnvelopeEvidence"),
    "StationEnvelopeEvidence": ("img2drawing.registration", "StationEnvelopeEvidence"),
    "RegionGeometryComparison": ("img2drawing.registration", "RegionGeometryComparison"),
    "compare_region_envelopes": ("img2drawing.registration", "compare_region_envelopes"),
    "TorsoOrientationObservation": ("img2drawing.registration", "TorsoOrientationObservation"),
    "TorsoOrientationIntegrityError": ("img2drawing.registration", "TorsoOrientationIntegrityError"),
    "TorsoOrientationComparison": ("img2drawing.registration", "TorsoOrientationComparison"),
    "compare_torso_orientation": ("img2drawing.registration", "compare_torso_orientation"),
    "LowerBodyObservation": ("img2drawing.registration", "LowerBodyObservation"),
    "LowerBodyIntegrityError": ("img2drawing.registration", "LowerBodyIntegrityError"),
    "LowerBodyComparison": ("img2drawing.registration", "LowerBodyComparison"),
    "compare_lower_body": ("img2drawing.registration", "compare_lower_body"),
    "HeadHairObservation": ("img2drawing.registration", "HeadHairObservation"),
    "HeadHairIntegrityError": ("img2drawing.registration", "HeadHairIntegrityError"),
    "HeadHairComparison": ("img2drawing.registration", "HeadHairComparison"),
    "compare_head_hair": ("img2drawing.registration", "compare_head_hair"),
    "PropWidthChangePoint": ("img2drawing.registration", "PropWidthChangePoint"),
    "PropTerminalMass": ("img2drawing.registration", "PropTerminalMass"),
    "PropBodyOverlapPoint": ("img2drawing.registration", "PropBodyOverlapPoint"),
    "PropTopologyObservation": ("img2drawing.registration", "PropTopologyObservation"),
    "PropTopologyIntegrityError": ("img2drawing.registration", "PropTopologyIntegrityError"),
    "PropTopologyComparison": ("img2drawing.registration", "PropTopologyComparison"),
    "compare_prop_topology": ("img2drawing.registration", "compare_prop_topology"),
}


def __getattr__(name: str):
    try:
        module_name, attribute = _LAZY_EXPORTS[name]
    except KeyError as exc:
        raise AttributeError(name) from exc
    value = getattr(import_module(module_name), attribute)
    globals()[name] = value
    return value


__all__ = [
    "DrawingRun", "DrawingRunResult", "DrawingAction", "AgentDrawingSession", "Stroke", "StrokeIR", "CanvasHistory",
    "ObservationContract", "ViewObservation", "FrozenObservationRecord", "ObservationReopenRecord",
    "StageSpec", "StageContract", "StageContractRegistry", "StageContractError", "get_stage_registry", "get_stage_contract_registry",
    "SubjectReference", "TaskStageTarget", "StageReferenceView", "ReferenceBundle", "ReferenceBundleError", "build_reference_bundle",
    "StageReviewRecord", "ReferenceReviewArtifacts", "CropBox", "LocalReviewError", "LocalReviewArtifacts", "ActionMemory",
    "StagePassMemory", "ReopenRecord", "StaleReviewError", "REQUIRED_P3_REGIONS", "RegionClosureEntry", "RegionClosureManifest",
    "VisualFidelityReviewRecord", "blind_observation_projection", "build_blind_visual_packet", "P4_RESOLVED_REGIONS",
    "P5_RESOLVED_REGIONS", "ResolvedFormEntry", "ResolvedFormManifest", "ResolvedFormReviewRecord", "ConstructionRetirementRecord",
    "IdentityFinishProfile", "CalibrationSheet", "IdentityPreflightResult", "preflight_identity_finish", "IdentityFinishManifest",
    "build_resolved_form_blind_packet", "AssistiveROIProposal", "ExcludedRegion", "AcceptedResidual", "AdaptiveEvidencePolicy",
    "PreviewArtifact", "render_preview", "EnvelopeStation", "RegionEnvelopeObservation", "RegionEnvelopeIntegrityError",
    "EnvelopeIntegrity", "AxisEnvelopeEvidence", "StationEnvelopeEvidence", "RegionGeometryComparison", "compare_region_envelopes",
    "TorsoOrientationObservation", "TorsoOrientationIntegrityError", "TorsoOrientationComparison", "compare_torso_orientation",
    "LowerBodyObservation", "LowerBodyIntegrityError", "LowerBodyComparison", "compare_lower_body", "HeadHairObservation",
    "HeadHairIntegrityError", "HeadHairComparison", "compare_head_hair", "PropWidthChangePoint", "PropTerminalMass",
    "PropBodyOverlapPoint", "PropTopologyObservation", "PropTopologyIntegrityError", "PropTopologyComparison", "compare_prop_topology",
    "FillRegion", "ReservedLight", "expand_fill", "ToneRecipe", "resolve_tone", "available_values",
    "Box", "GroundGuide", "Grid", "GridMeasurement", "InspectionSheet", "Measurement", "PixelSample", "PlumbLine", "Point",
    "PointMapping", "Profile", "Registration", "ROI", "Size", "angle", "distance", "drawing_state_hash", "drawing_state_payload",
    "ground_guide", "grid", "horizontal_profile", "map_subject_to_canvas", "point", "plumb_line", "sample_pixel",
    "stage_free_drawing_state_hash", "vertical_profile", "DrawingSession", "VNextDrawingSession", "CONSTRUCTION_PHASES",
    "ConstructionMark", "CorrectionRecord", "InitialConstruct", "InitialConstructResult", "PoseObservation",
    "ResidualRecord", "EvidencePolicy", "EvidenceReadRecord", "EvidenceTelemetry", "author_initial_construct", "inspect_initial_construct", "observe_pose", "replace_fill_region", "ABLATION_CONDITIONS", "ModularGrammarCard",
    "COMPATIBILITY_INTENTS", "DRAWING_MODES", "FINISH_INTENTS", "REFERENCE_MODES", "STYLE_PROFILES",
    "DrawingIntent", "IntentChangeRecord", "IntentProvenance", "ModeGuide", "StyleGuide",
    "compatibility_intent", "resolve_mode_guide", "resolve_style_guide",
    "consume_grammar_card", "AblationTrial", "ExemplarAblationReport", "run_exemplar_ablation",
]
