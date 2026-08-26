from __future__ import annotations

"""Independent visual-fidelity review records and the P3 closure manifest."""

from dataclasses import dataclass
import json
import re
from pathlib import Path
from typing import Any, Mapping, Sequence

from ..observation import FrozenObservationRecord
from .artifact import sha256_obj


REQUIRED_P3_REGIONS = (
    "head_hair",
    "torso_orientation",
    "near_arm",
    "far_arm",
    "pelvis",
    "leg_A",
    "leg_B",
    "attached_object",
)
_DECISIONS = frozenset({"closed", "revise", "accept-with-rationale"})
_REVIEW_DECISIONS = frozenset({"revise", "advance"})
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def _digest(value: str, *, label: str) -> str:
    value = str(value).lower()
    if not _SHA256.fullmatch(value):
        raise ValueError(f"{label} must be a 64-character lowercase hex digest")
    return value


def _strings(value: Sequence[Any] | None) -> tuple[str, ...]:
    return tuple(item for item in (str(v).strip() for v in (value or ())) if item)


@dataclass(frozen=True)
class RegionClosureEntry:
    region_id: str
    subject_finding: str
    drawing_finding: str
    evidence_refs: tuple[str, ...]
    decision: str
    blocker: bool = False
    rationale: str = ""
    rationale_basis: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        region_id = str(self.region_id).strip()
        if not region_id:
            raise ValueError("region closure requires region_id")
        if not str(self.subject_finding).strip() or not str(self.drawing_finding).strip():
            raise ValueError(f"region {region_id!r} requires fresh subject and drawing findings")
        refs = _strings(self.evidence_refs)
        if not refs:
            raise ValueError(f"region {region_id!r} requires independent evidence_refs")
        decision = str(self.decision)
        if decision not in _DECISIONS:
            raise ValueError(f"decision must be one of {sorted(_DECISIONS)}")
        basis = _strings(self.rationale_basis)
        if decision == "accept-with-rationale":
            if not str(self.rationale).strip():
                raise ValueError("accept-with-rationale requires rationale")
            if not {"uncertainty", "occlusion"}.intersection(basis):
                raise ValueError(
                    "accept-with-rationale requires uncertainty or occlusion evidence"
                )
        object.__setattr__(self, "region_id", region_id)
        object.__setattr__(self, "subject_finding", str(self.subject_finding).strip())
        object.__setattr__(self, "drawing_finding", str(self.drawing_finding).strip())
        object.__setattr__(self, "evidence_refs", refs)
        object.__setattr__(self, "decision", decision)
        object.__setattr__(self, "blocker", bool(self.blocker))
        object.__setattr__(self, "rationale", str(self.rationale).strip())
        object.__setattr__(self, "rationale_basis", basis)

    @property
    def blocks_advance(self) -> bool:
        return self.blocker or self.decision == "revise"

    def to_dict(self) -> dict[str, Any]:
        return {
            "region_id": self.region_id,
            "subject_finding": self.subject_finding,
            "drawing_finding": self.drawing_finding,
            "evidence_refs": list(self.evidence_refs),
            "decision": self.decision,
            "blocker": self.blocker,
            "rationale": self.rationale,
            "rationale_basis": list(self.rationale_basis),
        }

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "RegionClosureEntry":
        return cls(
            region_id=str(raw["region_id"]),
            subject_finding=str(raw["subject_finding"]),
            drawing_finding=str(raw["drawing_finding"]),
            evidence_refs=tuple(map(str, raw.get("evidence_refs", ()))),
            decision=str(raw["decision"]),
            blocker=bool(raw.get("blocker", False)),
            rationale=str(raw.get("rationale", "")),
            rationale_basis=tuple(map(str, raw.get("rationale_basis", ()))),
        )


@dataclass(frozen=True)
class RegionClosureManifest:
    stage: str
    drawing_state_sha256: str
    drawing_artifact_sha256: str
    history_cursor: int
    observation_lock_digest: str
    regions: tuple[RegionClosureEntry, ...]
    evaluator_id: str
    manifest_id: str = ""

    def __post_init__(self) -> None:
        if str(self.stage) != "P3_primary_masses":
            raise ValueError("region closure manifest is currently defined for P3_primary_masses")
        if int(self.history_cursor) < 0:
            raise ValueError("history_cursor must be >= 0")
        _digest(self.drawing_state_sha256, label="drawing_state_sha256")
        _digest(self.drawing_artifact_sha256, label="drawing_artifact_sha256")
        _digest(self.observation_lock_digest, label="observation_lock_digest")
        regions = tuple(
            item if isinstance(item, RegionClosureEntry) else RegionClosureEntry.from_dict(item)
            for item in self.regions
        )
        ids = tuple(item.region_id for item in regions)
        if set(ids) != set(REQUIRED_P3_REGIONS) or len(ids) != len(REQUIRED_P3_REGIONS):
            missing = sorted(set(REQUIRED_P3_REGIONS) - set(ids))
            extra = sorted(set(ids) - set(REQUIRED_P3_REGIONS))
            raise ValueError(f"P3 region closure must contain exactly eight regions; missing={missing}, extra={extra}")
        if len(set(ids)) != len(ids):
            raise ValueError("region closure manifest cannot contain duplicate regions")
        evaluator_id = str(self.evaluator_id).strip()
        if not evaluator_id:
            raise ValueError("visual fidelity manifest requires evaluator_id")
        manifest_id = str(self.manifest_id).strip() or f"manifest_{sha256_obj([item.to_dict() for item in regions])[:12]}"
        object.__setattr__(self, "stage", str(self.stage))
        object.__setattr__(self, "drawing_state_sha256", str(self.drawing_state_sha256).lower())
        object.__setattr__(self, "drawing_artifact_sha256", str(self.drawing_artifact_sha256).lower())
        object.__setattr__(self, "history_cursor", int(self.history_cursor))
        object.__setattr__(self, "observation_lock_digest", str(self.observation_lock_digest).lower())
        object.__setattr__(self, "regions", regions)
        object.__setattr__(self, "evaluator_id", evaluator_id)
        object.__setattr__(self, "manifest_id", manifest_id)

    @property
    def blockers(self) -> tuple[str, ...]:
        return tuple(item.region_id for item in self.regions if item.blocks_advance)

    @property
    def can_advance(self) -> bool:
        return not self.blockers

    def digest(self) -> str:
        return sha256_obj(self.to_dict())

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "img2drawing.region_closure_manifest.v1",
            "stage": self.stage,
            "drawing_state_sha256": self.drawing_state_sha256,
            "drawing_artifact_sha256": self.drawing_artifact_sha256,
            "history_cursor": self.history_cursor,
            "observation_lock_digest": self.observation_lock_digest,
            "regions": [item.to_dict() for item in self.regions],
            "evaluator_id": self.evaluator_id,
            "manifest_id": self.manifest_id,
            "blockers": list(self.blockers),
        }

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "RegionClosureManifest":
        if raw.get("schema") not in (None, "img2drawing.region_closure_manifest.v1"):
            raise ValueError(f"unsupported region closure schema: {raw.get('schema')!r}")
        return cls(
            stage=str(raw["stage"]),
            drawing_state_sha256=str(raw["drawing_state_sha256"]),
            drawing_artifact_sha256=str(raw["drawing_artifact_sha256"]),
            history_cursor=int(raw["history_cursor"]),
            observation_lock_digest=str(raw["observation_lock_digest"]),
            regions=tuple(RegionClosureEntry.from_dict(item) for item in raw["regions"]),
            evaluator_id=str(raw["evaluator_id"]),
            manifest_id=str(raw.get("manifest_id", "")),
        )

    def save(self, path: str | Path) -> Path:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(self.to_dict(), indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")
        return target


@dataclass(frozen=True)
class VisualFidelityReviewRecord:
    stage: str
    manifest_digest: str
    drawing_state_sha256: str
    drawing_artifact_sha256: str
    history_cursor: int
    observation_lock_digest: str
    evaluator_id: str
    decision: str
    findings: tuple[str, ...]
    rationale: str
    blind_packet_digest: str

    def __post_init__(self) -> None:
        if str(self.stage) != "P3_primary_masses":
            raise ValueError("visual fidelity review is currently defined for P3_primary_masses")
        for value, label in (
            (self.manifest_digest, "manifest_digest"),
            (self.drawing_state_sha256, "drawing_state_sha256"),
            (self.drawing_artifact_sha256, "drawing_artifact_sha256"),
            (self.observation_lock_digest, "observation_lock_digest"),
            (self.blind_packet_digest, "blind_packet_digest"),
        ):
            _digest(value, label=label)
        if int(self.history_cursor) < 0:
            raise ValueError("history_cursor must be >= 0")
        evaluator_id = str(self.evaluator_id).strip()
        if not evaluator_id:
            raise ValueError("visual fidelity review requires evaluator_id")
        decision = str(self.decision)
        if decision not in _REVIEW_DECISIONS:
            raise ValueError(f"decision must be one of {sorted(_REVIEW_DECISIONS)}")
        findings = _strings(self.findings)
        if not findings:
            raise ValueError("visual fidelity review requires findings")
        if decision == "advance" and not str(self.rationale).strip():
            raise ValueError("visual fidelity advance requires rationale")
        object.__setattr__(self, "stage", str(self.stage))
        object.__setattr__(self, "manifest_digest", str(self.manifest_digest).lower())
        object.__setattr__(self, "drawing_state_sha256", str(self.drawing_state_sha256).lower())
        object.__setattr__(self, "drawing_artifact_sha256", str(self.drawing_artifact_sha256).lower())
        object.__setattr__(self, "history_cursor", int(self.history_cursor))
        object.__setattr__(self, "observation_lock_digest", str(self.observation_lock_digest).lower())
        object.__setattr__(self, "evaluator_id", evaluator_id)
        object.__setattr__(self, "decision", decision)
        object.__setattr__(self, "findings", findings)
        object.__setattr__(self, "rationale", str(self.rationale).strip())
        object.__setattr__(self, "blind_packet_digest", str(self.blind_packet_digest).lower())

    def digest(self) -> str:
        return sha256_obj(self.to_dict())

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "img2drawing.visual_fidelity_review.v1",
            "stage": self.stage,
            "manifest_digest": self.manifest_digest,
            "drawing_state_sha256": self.drawing_state_sha256,
            "drawing_artifact_sha256": self.drawing_artifact_sha256,
            "history_cursor": self.history_cursor,
            "observation_lock_digest": self.observation_lock_digest,
            "evaluator_id": self.evaluator_id,
            "decision": self.decision,
            "findings": list(self.findings),
            "rationale": self.rationale,
            "blind_packet_digest": self.blind_packet_digest,
        }

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "VisualFidelityReviewRecord":
        if raw.get("schema") != "img2drawing.visual_fidelity_review.v1":
            raise ValueError(f"unsupported visual fidelity review schema: {raw.get('schema')!r}")
        return cls(
            stage=str(raw["stage"]),
            manifest_digest=str(raw["manifest_digest"]),
            drawing_state_sha256=str(raw["drawing_state_sha256"]),
            drawing_artifact_sha256=str(raw["drawing_artifact_sha256"]),
            history_cursor=int(raw["history_cursor"]),
            observation_lock_digest=str(raw["observation_lock_digest"]),
            evaluator_id=str(raw["evaluator_id"]),
            decision=str(raw["decision"]),
            findings=tuple(map(str, raw.get("findings", ()))),
            rationale=str(raw.get("rationale", "")),
            blind_packet_digest=str(raw["blind_packet_digest"]),
        )

    def save(self, path: str | Path) -> Path:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(self.to_dict(), indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")
        return target


def blind_observation_projection(lock: FrozenObservationRecord) -> dict[str, Any]:
    """Return only subject facts needed by an independent evaluator."""
    return {
        "schema": "img2drawing.blind_observation_projection.v1",
        "observation_id": lock.observation_id,
        "observation_digest": lock.observation_digest,
        "subject_reference_sha256": lock.subject_reference_sha256,
        "observation": {
            "subject_summary": lock.observation.subject_summary,
            "view": None if lock.observation.view is None else lock.observation.view.to_dict(),
            "uncertainties": list(lock.observation.uncertainties)
            + ([] if lock.observation.view is None else list(lock.observation.view.uncertainties)),
        },
        "hidden_from_evaluator": [
            "worker_rationale",
            "previous_review_findings",
            "previous_advance_claim",
        ],
    }


def build_blind_visual_packet(
    *,
    observation_lock: FrozenObservationRecord,
    stage_contract: Mapping[str, Any],
    drawing_artifact: Mapping[str, Any],
    subject_reference_path: str,
    region_evidence_refs: Sequence[str] = (),
) -> dict[str, Any]:
    """Build a rationale-free packet for an independent visual evaluator."""
    packet = {
        "schema": "img2drawing.blind_visual_packet.v1",
        "stage": "P3_primary_masses",
        "subject_reference_path": str(subject_reference_path),
        "observation_lock": blind_observation_projection(observation_lock),
        "stage_contract": dict(stage_contract),
        "drawing_artifact": dict(drawing_artifact),
        "region_evidence_refs": list(map(str, region_evidence_refs)),
        "evaluator_instruction": "Inspect subject and current drawing independently; do not use worker rationale or any prior verdict.",
    }
    packet["packet_digest"] = sha256_obj(packet)
    return packet


__all__ = [
    "REQUIRED_P3_REGIONS",
    "RegionClosureEntry",
    "RegionClosureManifest",
    "VisualFidelityReviewRecord",
    "blind_observation_projection",
    "build_blind_visual_packet",
]
