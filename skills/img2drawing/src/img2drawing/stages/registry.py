from .full_body_croquis import FULL_BODY_CROQUIS
from .full_body_contracts import FULL_BODY_CROQUIS_CONTRACTS
from .contract import StageContractRegistry, validate_contracts_against_specs
from .identity_finish import IDENTITY_FINISH_STAGE, IDENTITY_FINISH_CONTRACT

REGISTRIES = {
    "full_body_croquis": {
        "specs": FULL_BODY_CROQUIS,
        "contracts": FULL_BODY_CROQUIS_CONTRACTS,
    },
    "full_body_croquis_with_p6": {
        "specs": FULL_BODY_CROQUIS + (IDENTITY_FINISH_STAGE,),
        "contracts": StageContractRegistry(FULL_BODY_CROQUIS_CONTRACTS.contracts + (IDENTITY_FINISH_CONTRACT,)),
    }
}

validate_contracts_against_specs(
    FULL_BODY_CROQUIS,
    FULL_BODY_CROQUIS_CONTRACTS,
)
validate_contracts_against_specs(
    FULL_BODY_CROQUIS + (IDENTITY_FINISH_STAGE,),
    REGISTRIES["full_body_croquis_with_p6"]["contracts"],
)

def get_stage_registry(name: str = "full_body_croquis"):
    try:
        return REGISTRIES[str(name)]["specs"]
    except KeyError as exc:
        raise ValueError(f"unknown stage registry: {name!r}") from exc

def get_stage_contract_registry(name: str = "full_body_croquis"):
    try:
        return REGISTRIES[str(name)]["contracts"]
    except KeyError as exc:
        raise ValueError(f"unknown stage registry: {name!r}") from exc
