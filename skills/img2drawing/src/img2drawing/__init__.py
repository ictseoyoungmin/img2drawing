from ._version import __version__

from .run import DrawingRun, DrawingRunResult
from .core import DrawingAction, AgentDrawingSession, Stroke, StrokeIR, CanvasHistory
from .observation import ObservationContract
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
from .review import (
    CropBox, LocalReviewError, LocalReviewArtifacts,
    ActionMemory, StagePassMemory, ReopenRecord,
    StageReviewRecord,
    ReferenceReviewArtifacts,
    DualReferenceReviewArtifacts,
    StaleReviewError,
)

__all__=[
    "DrawingRun","DrawingRunResult",
    "DrawingAction","AgentDrawingSession","Stroke","StrokeIR","CanvasHistory",
    "ObservationContract","StageSpec","StageContract","StageContractRegistry","StageContractError","ExemplarContract",
    "get_stage_registry","get_stage_contract_registry",
    "SubjectReference","TaskStageTarget","GrammarExemplar","StageReferenceView",
    "ReferenceBundle","ReferenceBundleError","build_reference_bundle",
    "StageReviewRecord","ReferenceReviewArtifacts","DualReferenceReviewArtifacts",
    "CropBox","LocalReviewError","LocalReviewArtifacts",
    "ActionMemory","StagePassMemory","ReopenRecord",
    "StaleReviewError",
    "ExemplarAuditFinding","ExemplarAuditRecord","ExemplarAuditRegistry","ExemplarAuditError","load_exemplar_audit_registry",
]
