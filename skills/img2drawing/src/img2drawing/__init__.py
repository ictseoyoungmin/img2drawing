from ._version import __version__

from .run import DrawingRun, DrawingRunResult
from .core import DrawingAction, AgentDrawingSession, Stroke, StrokeIR, CanvasHistory
from .observation import (
    ObservationContract,
    ViewObservation,
    FrozenObservationRecord,
    ObservationReopenRecord,
)
from .stages import (
    StageSpec, StageContract, StageContractRegistry, StageContractError,
    ExemplarContract, get_stage_registry, get_stage_contract_registry,
)
from .reference import (
    SubjectReference,
    TaskStageTarget,
    GrammarExemplar,
    StageReferenceView,
    ReferenceBundle,
    ReferenceBundleError,
    build_reference_bundle,
)
from .exemplar.audit import (
    ExemplarAuditFinding, ExemplarAuditRecord, ExemplarAuditRegistry, ExemplarAuditError,
    load_exemplar_audit_registry,
)
from .exemplar.ablation import (
    ABLATION_CONDITIONS, ModularGrammarCard, consume_grammar_card, AblationTrial,
    ExemplarAblationReport, run_exemplar_ablation,
)
from .review import (
    CropBox, LocalReviewError, LocalReviewArtifacts,
    ActionMemory, StagePassMemory, ReopenRecord,
    StageReviewRecord,
    ReferenceReviewArtifacts,
    DualReferenceReviewArtifacts,
    StaleReviewError,
    REQUIRED_P3_REGIONS, RegionClosureEntry, RegionClosureManifest,
    VisualFidelityReviewRecord, blind_observation_projection,
    build_blind_visual_packet,
)
from .registration import (
    EnvelopeStation, RegionEnvelopeObservation, RegionEnvelopeIntegrityError,
    EnvelopeIntegrity, AxisEnvelopeEvidence, StationEnvelopeEvidence,
    RegionGeometryComparison, compare_region_envelopes,
    TorsoOrientationObservation, TorsoOrientationIntegrityError,
    TorsoOrientationComparison, compare_torso_orientation,
    LowerBodyObservation, LowerBodyIntegrityError, LowerBodyComparison,
    compare_lower_body,
    HeadHairObservation, HeadHairIntegrityError, HeadHairComparison,
    compare_head_hair,
    PropWidthChangePoint, PropTerminalMass, PropBodyOverlapPoint,
    PropTopologyObservation, PropTopologyIntegrityError,
    PropTopologyComparison, compare_prop_topology,
)

__all__=[
    "DrawingRun","DrawingRunResult",
    "DrawingAction","AgentDrawingSession","Stroke","StrokeIR","CanvasHistory",
    "ObservationContract","ViewObservation","FrozenObservationRecord","ObservationReopenRecord",
    "StageSpec","StageContract","StageContractRegistry","StageContractError","ExemplarContract",
    "get_stage_registry","get_stage_contract_registry",
    "SubjectReference","TaskStageTarget","GrammarExemplar","StageReferenceView",
    "ReferenceBundle","ReferenceBundleError","build_reference_bundle",
    "StageReviewRecord","ReferenceReviewArtifacts","DualReferenceReviewArtifacts",
    "CropBox","LocalReviewError","LocalReviewArtifacts",
    "ActionMemory","StagePassMemory","ReopenRecord",
    "StaleReviewError",
    "REQUIRED_P3_REGIONS","RegionClosureEntry","RegionClosureManifest",
    "VisualFidelityReviewRecord","blind_observation_projection","build_blind_visual_packet",
    "EnvelopeStation","RegionEnvelopeObservation","RegionEnvelopeIntegrityError",
    "EnvelopeIntegrity","AxisEnvelopeEvidence","StationEnvelopeEvidence",
    "RegionGeometryComparison","compare_region_envelopes",
    "TorsoOrientationObservation","TorsoOrientationIntegrityError",
    "TorsoOrientationComparison","compare_torso_orientation",
    "LowerBodyObservation","LowerBodyIntegrityError","LowerBodyComparison",
    "compare_lower_body",
    "HeadHairObservation","HeadHairIntegrityError","HeadHairComparison",
    "compare_head_hair",
    "PropWidthChangePoint","PropTerminalMass","PropBodyOverlapPoint",
    "PropTopologyObservation","PropTopologyIntegrityError",
    "PropTopologyComparison","compare_prop_topology",
    "ExemplarAuditFinding","ExemplarAuditRecord","ExemplarAuditRegistry","ExemplarAuditError","load_exemplar_audit_registry",
    "ABLATION_CONDITIONS","ModularGrammarCard","consume_grammar_card","AblationTrial",
    "ExemplarAblationReport","run_exemplar_ablation",
]
