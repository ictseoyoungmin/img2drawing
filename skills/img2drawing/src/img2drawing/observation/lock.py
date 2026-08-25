from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from ..core.session import sha256_obj
from .contract import ObservationContract


_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def _observation_digest(observation: ObservationContract, subject_reference_sha256: str) -> str:
    return sha256_obj({
        "subject_reference_sha256": str(subject_reference_sha256).lower(),
        "observation": observation.to_dict(),
    })


@dataclass(frozen=True)
class FrozenObservationRecord:
    """Immutable, provenance-bound pre-draw observation record.

    The semantic observation remains agent-authored.  This record only makes its
    lifecycle, subject binding, and replacement history authoritative for a run.
    """

    observation: ObservationContract
    subject_reference_sha256: str
    observation_id: str
    locked_at_cursor: int
    locked_at_stage: str
    observation_digest: str
    replacement_of: str | None = None

    def __post_init__(self):
        subject_hash = str(self.subject_reference_sha256).lower()
        if not _SHA256.fullmatch(subject_hash):
            raise ValueError("subject_reference_sha256 must be a 64-character lowercase hex digest")
        if not str(self.observation_id).strip():
            raise ValueError("observation_id must be non-empty")
        if int(self.locked_at_cursor) < 0:
            raise ValueError("locked_at_cursor must be >= 0")
        if not str(self.locked_at_stage).strip():
            raise ValueError("locked_at_stage must be non-empty")
        if not isinstance(self.observation, ObservationContract):
            raise TypeError("observation must be an ObservationContract")
        if self.observation.view is None:
            raise ValueError("a frozen observation requires typed view observation")
        required_arms = {"subject_left", "subject_right"}
        if set(self.observation.view.arm_visibility) != required_arms:
            raise ValueError(
                "a frozen observation requires visibility for subject_left and subject_right"
            )
        if set(self.observation.view.arm_occlusion) != required_arms:
            raise ValueError(
                "a frozen observation requires occlusion for subject_left and subject_right"
            )

        # Clone through the serialized representation so later mutation of the
        # caller's nested dictionaries cannot mutate this locked record.
        cloned = ObservationContract.from_dict(self.observation.to_dict())
        expected = _observation_digest(cloned, subject_hash)
        if str(self.observation_digest) != expected:
            raise ValueError("observation_digest does not match observation and subject hash")
        if self.replacement_of is not None and not _SHA256.fullmatch(str(self.replacement_of)):
            raise ValueError("replacement_of must be a prior observation digest")

        object.__setattr__(self, "observation", cloned)
        object.__setattr__(self, "subject_reference_sha256", subject_hash)
        object.__setattr__(self, "observation_id", str(self.observation_id))
        object.__setattr__(self, "locked_at_cursor", int(self.locked_at_cursor))
        object.__setattr__(self, "locked_at_stage", str(self.locked_at_stage))

    @classmethod
    def create(
        cls,
        observation: ObservationContract,
        *,
        subject_reference_sha256: str,
        observation_id: str,
        locked_at_cursor: int,
        locked_at_stage: str,
        replacement_of: str | None = None,
    ) -> "FrozenObservationRecord":
        cloned = ObservationContract.from_dict(observation.to_dict())
        digest = _observation_digest(cloned, str(subject_reference_sha256).lower())
        return cls(
            observation=cloned,
            subject_reference_sha256=str(subject_reference_sha256).lower(),
            observation_id=str(observation_id),
            locked_at_cursor=int(locked_at_cursor),
            locked_at_stage=str(locked_at_stage),
            observation_digest=digest,
            replacement_of=replacement_of,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "img2drawing.observation_lock.v1",
            "observation": self.observation.to_dict(),
            "subject_reference_sha256": self.subject_reference_sha256,
            "observation_id": self.observation_id,
            "locked_at_cursor": self.locked_at_cursor,
            "locked_at_stage": self.locked_at_stage,
            "observation_digest": self.observation_digest,
            "replacement_of": self.replacement_of,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "FrozenObservationRecord":
        if data.get("schema") != "img2drawing.observation_lock.v1":
            raise ValueError(f"unsupported observation lock schema: {data.get('schema')!r}")
        return cls(
            observation=ObservationContract.from_dict(data["observation"]),
            subject_reference_sha256=str(data["subject_reference_sha256"]),
            observation_id=str(data["observation_id"]),
            locked_at_cursor=int(data["locked_at_cursor"]),
            locked_at_stage=str(data["locked_at_stage"]),
            observation_digest=str(data["observation_digest"]),
            replacement_of=data.get("replacement_of"),
        )


@dataclass(frozen=True)
class ObservationReopenRecord:
    """Audit record for replacing a frozen observation and its consequences."""

    reopen_id: str
    reason: str
    previous_observation_digest: str
    replacement_observation_digest: str
    source_cursor: int
    restored_cursor: int
    target_stage: str
    invalidated_stages: tuple[str, ...] = ()

    def __post_init__(self):
        if not str(self.reopen_id).strip() or not str(self.reason).strip():
            raise ValueError("observation reopen requires id and reason")
        for name in (self.previous_observation_digest, self.replacement_observation_digest):
            if not _SHA256.fullmatch(str(name)):
                raise ValueError("observation reopen digests must be SHA-256 hex")
        if int(self.source_cursor) < 0 or int(self.restored_cursor) < 0:
            raise ValueError("observation reopen cursors must be >= 0")
        if not str(self.target_stage).strip():
            raise ValueError("observation reopen requires target_stage")
        object.__setattr__(self, "invalidated_stages", tuple(map(str, self.invalidated_stages)))

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "img2drawing.observation_reopen.v1",
            "reopen_id": self.reopen_id,
            "reason": self.reason,
            "previous_observation_digest": self.previous_observation_digest,
            "replacement_observation_digest": self.replacement_observation_digest,
            "source_cursor": int(self.source_cursor),
            "restored_cursor": int(self.restored_cursor),
            "target_stage": self.target_stage,
            "invalidated_stages": list(self.invalidated_stages),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ObservationReopenRecord":
        if data.get("schema") != "img2drawing.observation_reopen.v1":
            raise ValueError(f"unsupported observation reopen schema: {data.get('schema')!r}")
        return cls(
            reopen_id=str(data["reopen_id"]),
            reason=str(data["reason"]),
            previous_observation_digest=str(data["previous_observation_digest"]),
            replacement_observation_digest=str(data["replacement_observation_digest"]),
            source_cursor=int(data["source_cursor"]),
            restored_cursor=int(data["restored_cursor"]),
            target_stage=str(data["target_stage"]),
            invalidated_stages=tuple(map(str, data.get("invalidated_stages", ()))),
        )
