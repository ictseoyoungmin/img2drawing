from __future__ import annotations

"""Small, opt-in R23 evidence helpers.

These objects intentionally stop at proposals and policy validation.  They do not
select regions, infer anatomy, or decide visual likeness.  A worker must bind a
proposal to the frozen observation before it can be used in a review packet.
"""

from dataclasses import dataclass
import json
import re
from pathlib import Path
from typing import Any, Mapping, Sequence

from ..core.session import sha256_obj


def _box(value: Sequence[float]) -> tuple[float, float, float, float]:
    if len(value) != 4:
        raise ValueError("ROI box requires u0,v0,u1,v1")
    u0, v0, u1, v1 = map(float, value)
    if not (0 <= u0 < u1 <= 1 and 0 <= v0 < v1 <= 1):
        raise ValueError("ROI box must be ordered inside normalized canvas")
    return u0, v0, u1, v1


def _strings(value: Sequence[Any] | None) -> tuple[str, ...]:
    return tuple(x for x in (str(v).strip() for v in (value or ())) if x)


@dataclass(frozen=True)
class AssistiveROIProposal:
    proposal_id: str
    region_id: str
    box: tuple[float, float, float, float]
    source: str
    confidence: float
    observation_lock_digest: str
    validated_by_agent: bool = False
    validation_note: str = ""

    def __post_init__(self) -> None:
        if not str(self.proposal_id).strip() or not str(self.region_id).strip():
            raise ValueError("ROI proposal requires proposal_id and region_id")
        if not str(self.source).strip():
            raise ValueError("ROI proposal requires source provenance")
        if not 0 <= float(self.confidence) <= 1:
            raise ValueError("ROI confidence must be in [0,1]")
        digest = str(self.observation_lock_digest).lower()
        if not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise ValueError("ROI proposal requires an observation lock digest")
        if self.validated_by_agent and not str(self.validation_note).strip():
            raise ValueError("validated ROI proposal requires validation_note")
        object.__setattr__(self, "proposal_id", str(self.proposal_id).strip())
        object.__setattr__(self, "region_id", str(self.region_id).strip())
        object.__setattr__(self, "box", _box(self.box))
        object.__setattr__(self, "source", str(self.source).strip())
        object.__setattr__(self, "confidence", float(self.confidence))
        object.__setattr__(self, "observation_lock_digest", digest)
        object.__setattr__(self, "validation_note", str(self.validation_note).strip())

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "img2drawing.assistive_roi_proposal.v1",
            "proposal_id": self.proposal_id,
            "region_id": self.region_id,
            "box": list(self.box),
            "source": self.source,
            "confidence": self.confidence,
            "observation_lock_digest": self.observation_lock_digest,
            "authority": "assistive_proposal_not_geometry_truth",
            "validated_by_agent": self.validated_by_agent,
            "validation_note": self.validation_note,
        }

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "AssistiveROIProposal":
        return cls(
            proposal_id=str(raw["proposal_id"]), region_id=str(raw["region_id"]),
            box=tuple(raw["box"]), source=str(raw["source"]),
            confidence=float(raw.get("confidence", 0)),
            observation_lock_digest=str(raw["observation_lock_digest"]),
            validated_by_agent=bool(raw.get("validated_by_agent", False)),
            validation_note=str(raw.get("validation_note", "")),
        )


@dataclass(frozen=True)
class ExcludedRegion:
    region_id: str
    reason: str
    basis: tuple[str, ...]
    observation_lock_digest: str

    def __post_init__(self) -> None:
        if not str(self.region_id).strip() or not str(self.reason).strip():
            raise ValueError("excluded region requires region_id and reason")
        basis = _strings(self.basis)
        if not {"occlusion", "uncertainty"}.intersection(basis):
            raise ValueError("excluded region requires occlusion or uncertainty basis")
        digest = str(self.observation_lock_digest).lower()
        if not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise ValueError("excluded region requires observation lock digest")
        object.__setattr__(self, "region_id", str(self.region_id).strip())
        object.__setattr__(self, "reason", str(self.reason).strip())
        object.__setattr__(self, "basis", basis)
        object.__setattr__(self, "observation_lock_digest", digest)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "img2drawing.excluded_region.v1",
            "region_id": self.region_id,
            "reason": self.reason,
            "basis": list(self.basis),
            "observation_lock_digest": self.observation_lock_digest,
        }

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "ExcludedRegion":
        return cls(
            region_id=str(raw["region_id"]), reason=str(raw["reason"]),
            basis=tuple(raw.get("basis", ())),
            observation_lock_digest=str(raw["observation_lock_digest"]),
        )


@dataclass(frozen=True)
class AcceptedResidual:
    """A bounded residual that may be recorded, never used to skip owned defects."""

    region_id: str
    stage: str
    description: str
    rationale: str
    material_mismatch: bool = False
    stage_owned: bool = False

    def __post_init__(self) -> None:
        if not str(self.region_id).strip() or not str(self.stage).strip():
            raise ValueError("accepted residual requires region_id and stage")
        if not str(self.description).strip() or not str(self.rationale).strip():
            raise ValueError("accepted residual requires description and rationale")
        if bool(self.material_mismatch) or bool(self.stage_owned):
            raise ValueError("owned or material-mismatch residuals cannot be accepted")
        object.__setattr__(self, "region_id", str(self.region_id).strip())
        object.__setattr__(self, "stage", str(self.stage).strip())
        object.__setattr__(self, "description", str(self.description).strip())
        object.__setattr__(self, "rationale", str(self.rationale).strip())

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "img2drawing.accepted_residual.v1",
            "region_id": self.region_id,
            "stage": self.stage,
            "description": self.description,
            "rationale": self.rationale,
            "material_mismatch": self.material_mismatch,
            "stage_owned": self.stage_owned,
        }

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "AcceptedResidual":
        return cls(
            region_id=str(raw["region_id"]), stage=str(raw["stage"]),
            description=str(raw["description"]), rationale=str(raw["rationale"]),
            material_mismatch=bool(raw.get("material_mismatch", False)),
            stage_owned=bool(raw.get("stage_owned", False)),
        )


@dataclass(frozen=True)
class AdaptiveEvidencePolicy:
    """Portable manifest for proposal/exclusion policy decisions."""

    observation_lock_digest: str
    proposals: tuple[AssistiveROIProposal, ...] = ()
    excluded_regions: tuple[ExcludedRegion, ...] = ()
    accepted_residuals: tuple[AcceptedResidual, ...] = ()
    preview_only: bool = True

    def __post_init__(self) -> None:
        digest = str(self.observation_lock_digest).lower()
        if not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise ValueError("adaptive policy requires observation lock digest")
        proposals = tuple(item if isinstance(item, AssistiveROIProposal) else AssistiveROIProposal.from_dict(item) for item in self.proposals)
        excluded = tuple(item if isinstance(item, ExcludedRegion) else ExcludedRegion.from_dict(item) for item in self.excluded_regions)
        residuals = tuple(item if isinstance(item, AcceptedResidual) else AcceptedResidual.from_dict(item) for item in self.accepted_residuals)
        for proposal in proposals:
            if proposal.observation_lock_digest != digest:
                raise ValueError("all ROI proposals must share the frozen observation lock")
        for item in excluded:
            if item.observation_lock_digest != digest:
                raise ValueError("all exclusions must share the frozen observation lock")
        if len({p.proposal_id for p in proposals}) != len(proposals):
            raise ValueError("adaptive ROI proposal ids must be unique")
        if len({item.region_id for item in excluded}) != len(excluded):
            raise ValueError("adaptive exclusions must contain unique regions")
        object.__setattr__(self, "observation_lock_digest", digest)
        object.__setattr__(self, "proposals", proposals)
        object.__setattr__(self, "excluded_regions", excluded)
        object.__setattr__(self, "accepted_residuals", residuals)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "img2drawing.adaptive_evidence_policy.v1",
            "observation_lock_digest": self.observation_lock_digest,
            "proposals": [item.to_dict() for item in self.proposals],
            "excluded_regions": [item.to_dict() for item in self.excluded_regions],
            "accepted_residuals": [item.to_dict() for item in self.accepted_residuals],
            "preview_only": self.preview_only,
            "authority": "agent_validation_required; evidence_not_likeness_gate",
        }

    def digest(self) -> str:
        return sha256_obj(self.to_dict())

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "AdaptiveEvidencePolicy":
        if raw.get("schema") not in (None, "img2drawing.adaptive_evidence_policy.v1"):
            raise ValueError(f"unsupported adaptive evidence schema: {raw.get('schema')!r}")
        return cls(
            observation_lock_digest=str(raw["observation_lock_digest"]),
            proposals=tuple(AssistiveROIProposal.from_dict(item) for item in raw.get("proposals", ())),
            excluded_regions=tuple(ExcludedRegion.from_dict(item) for item in raw.get("excluded_regions", ())),
            accepted_residuals=tuple(AcceptedResidual.from_dict(item) for item in raw.get("accepted_residuals", ())),
            preview_only=bool(raw.get("preview_only", True)),
        )

    def save(self, path: str | Path) -> Path:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(self.to_dict(), indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")
        return target


__all__ = ["AssistiveROIProposal", "ExcludedRegion", "AcceptedResidual", "AdaptiveEvidencePolicy"]
