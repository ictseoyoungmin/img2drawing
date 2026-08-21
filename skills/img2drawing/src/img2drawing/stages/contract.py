from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


class StageContractError(ValueError):
    """Structural error in the stage-representation contract."""


@dataclass(frozen=True)
class ExemplarContract:
    """What a grammar exemplar is allowed to teach for one stage.

    This class only freezes the contract; auditing exemplars against it is a
    separate, independent step (see the exemplar audit in SKILL.md).
    """
    must_show: tuple[str, ...]
    may_show: tuple[str, ...]
    must_not_show: tuple[str, ...]

    def __post_init__(self):
        required=set(self.must_show)
        optional=set(self.may_show)
        forbidden=set(self.must_not_show)
        overlap=(required|optional)&forbidden
        if overlap:
            raise StageContractError(
                "exemplar contract both allows/requires and forbids: "
                + ", ".join(sorted(overlap))
            )
        if not required:
            raise StageContractError("exemplar contract must define must_show")

    def to_dict(self) -> dict:
        return {
            "must_show":list(self.must_show),
            "may_show":list(self.may_show),
            "must_not_show":list(self.must_not_show),
        }


@dataclass(frozen=True)
class StageContract:
    """Machine-readable representation scope for one drawing stage.

    The contract says what vocabulary belongs to the stage. It does not
    decide whether a drawn pose is artistically correct.
    """
    contract_id: str
    stage_id: str
    tier: int
    representation_name: str
    owns: tuple[str, ...]
    inherits_from: str | None
    must_preserve: tuple[str, ...]
    allowed_representation: tuple[str, ...]
    forbidden_representation: tuple[str, ...]
    detail_ceiling: tuple[str, ...]
    next_stage_unlocks: tuple[str, ...]
    exemplar: ExemplarContract

    def __post_init__(self):
        if not self.contract_id.strip() or not self.stage_id.strip():
            raise StageContractError("contract_id and stage_id are required")
        if self.tier < 1:
            raise StageContractError("tier must be >= 1")
        if not self.owns:
            raise StageContractError(f"{self.stage_id}: owns must be non-empty")
        if not self.allowed_representation:
            raise StageContractError(
                f"{self.stage_id}: allowed_representation must be non-empty"
            )
        overlap=set(self.allowed_representation)&set(self.forbidden_representation)
        if overlap:
            raise StageContractError(
                f"{self.stage_id}: representation both allowed and forbidden: "
                + ", ".join(sorted(overlap))
            )

    def to_dict(self) -> dict:
        return {
            "schema":"img2drawing.stage_contract.v1",
            "contract_id":self.contract_id,
            "stage_id":self.stage_id,
            "tier":self.tier,
            "representation_name":self.representation_name,
            "owns":list(self.owns),
            "inherits_from":self.inherits_from,
            "must_preserve":list(self.must_preserve),
            "allowed_representation":list(self.allowed_representation),
            "forbidden_representation":list(self.forbidden_representation),
            "detail_ceiling":list(self.detail_ceiling),
            "next_stage_unlocks":list(self.next_stage_unlocks),
            "exemplar_contract":self.exemplar.to_dict(),
            "authority_note":(
                "This contract governs representation scope only. "
                "Subject/task references remain visual truth; the Agent remains semantic authority."
            ),
        }


@dataclass(frozen=True)
class StageContractRegistry:
    contracts: tuple[StageContract, ...]

    def __post_init__(self):
        if not self.contracts:
            raise StageContractError("stage contract registry cannot be empty")

        stage_ids=[c.stage_id for c in self.contracts]
        contract_ids=[c.contract_id for c in self.contracts]
        tiers=[c.tier for c in self.contracts]
        if len(stage_ids) != len(set(stage_ids)):
            raise StageContractError("duplicate stage_id in stage contracts")
        if len(contract_ids) != len(set(contract_ids)):
            raise StageContractError("duplicate contract_id in stage contracts")
        if tiers != list(range(1,len(tiers)+1)):
            raise StageContractError(
                f"tiers must be contiguous 1..N, got {tiers}"
            )

        for i,c in enumerate(self.contracts):
            if i == 0:
                if c.inherits_from is not None:
                    raise StageContractError(
                        f"{c.stage_id}: first stage cannot inherit from another stage"
                    )
            else:
                prev=self.contracts[i-1]
                if c.inherits_from != prev.stage_id:
                    raise StageContractError(
                        f"{c.stage_id}: must inherit from predecessor {prev.stage_id!r}"
                    )

        # Every representation unlocked by a stage should become allowed
        # by the immediate successor. This catches drifting stage boundaries.
        for i,c in enumerate(self.contracts[:-1]):
            successor=self.contracts[i+1]
            missing=set(c.next_stage_unlocks)-set(successor.allowed_representation)
            if missing:
                raise StageContractError(
                    f"{c.stage_id} unlocks representation absent from "
                    f"{successor.stage_id}: {sorted(missing)}"
                )

    def for_stage(self,stage_id: str) -> StageContract:
        for c in self.contracts:
            if c.stage_id == stage_id:
                return c
        raise StageContractError(f"no stage contract for {stage_id!r}")

    def to_dict(self) -> dict:
        return {
            "schema":"img2drawing.stage_contract_registry.v1",
            "contracts":[c.to_dict() for c in self.contracts],
        }


def validate_contracts_against_specs(stage_specs, registry: StageContractRegistry) -> None:
    specs=tuple(stage_specs)
    contracts=registry.contracts
    if len(specs) != len(contracts):
        raise StageContractError(
            f"stage spec/contract count mismatch: {len(specs)} != {len(contracts)}"
        )
    for spec,contract in zip(specs,contracts):
        if spec.stage_id != contract.stage_id:
            raise StageContractError(
                f"stage order mismatch: spec={spec.stage_id!r}, "
                f"contract={contract.stage_id!r}"
            )
        if spec.index != contract.tier:
            raise StageContractError(
                f"{spec.stage_id}: spec index {spec.index} != contract tier {contract.tier}"
            )
