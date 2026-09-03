"""R23 compatibility implementation for the historical Pn stage runtime.

New work must use the stage-free :class:`img2drawing.DrawingSession` route. This package
remains importable only to support explicit R23 compatibility and is not part of the
instruction graph or canonical vNext orchestration path.
"""

from .model import StageSpec, StageProgress, StageOrderError
from .contract import (
    StageContract,
    StageContractError,
    StageContractRegistry,
    validate_contracts_against_specs,
)
from .registry import get_stage_registry, get_stage_contract_registry
from .identity_finish import IDENTITY_FINISH_STAGE, IDENTITY_FINISH_CONTRACT

__all__=[
    "StageSpec","StageProgress","StageOrderError",
    "StageContract","StageContractError","StageContractRegistry",
    "validate_contracts_against_specs",
    "get_stage_registry","get_stage_contract_registry",
    "IDENTITY_FINISH_STAGE","IDENTITY_FINISH_CONTRACT",
]
