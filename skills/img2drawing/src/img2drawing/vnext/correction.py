"""Stage-free residual and correction records for the vNext session.

The records keep the Agent's visual judgement and the session's immutable evidence
references together.  They do not rank residuals, score images, or create a lifecycle
gate; the Agent chooses the residual and decides whether a correction improved it.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Mapping

from ..core.session import sha256_obj


_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_RESIDUAL_STATUSES = {"open", "resolved"}
_CORRECTION_DECISIONS = {"keep", "revise"}


def _text(value: Any, field: str) -> str:
    result = str(value).strip()
    if not result:
        raise ValueError(f"{field} must be non-empty")
    return result


def _strings(values: Any, field: str) -> tuple[str, ...]:
    if isinstance(values, str):
        values = (values,)
    try:
        result = tuple(_text(value, field) for value in values)
    except TypeError as exc:
        raise TypeError(f"{field} must be an iterable of strings") from exc
    if len(set(result)) != len(result):
        raise ValueError(f"{field} must contain unique values")
    return result


def _digest(value: Any, field: str) -> str:
    result = str(value).lower().strip()
    if not _SHA256.fullmatch(result):
        raise ValueError(f"{field} must be a SHA-256 digest")
    return result


@dataclass(frozen=True)
class ResidualRecord:
    """One Agent-authored mismatch anchored to a fresh inspection snapshot."""

    residual_id: str
    observation_id: str
    observation: str
    scope: str
    severity: str
    impact_rationale: str
    responsible_premise: str | None
    responsible_stroke_ids: tuple[str, ...]
    planned_edit: str
    before_inspection_id: str
    before_drawing_state_hash: str
    before_history_cursor: int = 0
    status: str = "open"
    after_inspection_id: str | None = None
    after_drawing_state_hash: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "residual_id", _text(self.residual_id, "residual_id"))
        object.__setattr__(self, "observation_id", _text(self.observation_id, "observation_id"))
        object.__setattr__(self, "observation", _text(self.observation, "observation"))
        object.__setattr__(self, "scope", _text(self.scope, "scope"))
        object.__setattr__(self, "severity", _text(self.severity, "severity"))
        object.__setattr__(self, "impact_rationale", _text(self.impact_rationale, "impact_rationale"))
        premise = None if self.responsible_premise is None else _text(self.responsible_premise, "responsible_premise")
        object.__setattr__(self, "responsible_premise", premise)
        object.__setattr__(self, "responsible_stroke_ids", _strings(self.responsible_stroke_ids, "responsible_stroke_ids"))
        object.__setattr__(self, "planned_edit", _text(self.planned_edit, "planned_edit"))
        object.__setattr__(self, "before_inspection_id", _text(self.before_inspection_id, "before_inspection_id"))
        object.__setattr__(self, "before_drawing_state_hash", _digest(self.before_drawing_state_hash, "before_drawing_state_hash"))
        cursor = int(self.before_history_cursor)
        if cursor < 0:
            raise ValueError("before_history_cursor must be >= 0")
        object.__setattr__(self, "before_history_cursor", cursor)
        status = _text(self.status, "status")
        if status not in _RESIDUAL_STATUSES:
            raise ValueError(f"unsupported residual status: {status}")
        object.__setattr__(self, "status", status)
        after_id = None if self.after_inspection_id is None else _text(self.after_inspection_id, "after_inspection_id")
        after_hash = None if self.after_drawing_state_hash is None else _digest(self.after_drawing_state_hash, "after_drawing_state_hash")
        if status == "resolved" and (after_id is None or after_hash is None):
            raise ValueError("resolved residual requires after inspection evidence")
        if (after_id is None) != (after_hash is None):
            raise ValueError("after inspection id and digest must be supplied together")
        object.__setattr__(self, "after_inspection_id", after_id)
        object.__setattr__(self, "after_drawing_state_hash", after_hash)

    @property
    def impact(self) -> str:
        """Compatibility alias for callers that call the rationale ``impact``."""

        return self.impact_rationale

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "img2drawing.vnext.residual.v1",
            "residual_id": self.residual_id,
            "observation_id": self.observation_id,
            "observation": self.observation,
            "scope": self.scope,
            "severity": self.severity,
            "impact_rationale": self.impact_rationale,
            "responsible_premise": self.responsible_premise,
            "responsible_stroke_ids": list(self.responsible_stroke_ids),
            "planned_edit": self.planned_edit,
            "before_inspection_id": self.before_inspection_id,
            "before_drawing_state_hash": self.before_drawing_state_hash,
            "before_history_cursor": self.before_history_cursor,
            "status": self.status,
            "after_inspection_id": self.after_inspection_id,
            "after_drawing_state_hash": self.after_drawing_state_hash,
        }

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "ResidualRecord":
        if raw.get("schema") not in (None, "img2drawing.vnext.residual.v1"):
            raise ValueError(f"unsupported residual schema: {raw.get('schema')!r}")
        return cls(
            residual_id=str(raw["residual_id"]),
            observation_id=str(raw["observation_id"]),
            observation=str(raw["observation"]),
            scope=str(raw["scope"]),
            severity=str(raw["severity"]),
            impact_rationale=str(raw["impact_rationale"]),
            responsible_premise=raw.get("responsible_premise"),
            responsible_stroke_ids=tuple(raw.get("responsible_stroke_ids", ())),
            planned_edit=str(raw["planned_edit"]),
            before_inspection_id=str(raw["before_inspection_id"]),
            before_drawing_state_hash=str(raw["before_drawing_state_hash"]),
            before_history_cursor=int(raw.get("before_history_cursor", 0)),
            status=str(raw.get("status", "open")),
            after_inspection_id=raw.get("after_inspection_id"),
            after_drawing_state_hash=raw.get("after_drawing_state_hash"),
        )

    def digest(self) -> str:
        return sha256_obj(self.to_dict())


@dataclass(frozen=True)
class CorrectionRecord:
    """One explicit edit and its fresh before/after evidence binding."""

    correction_id: str
    residual_id: str
    observation_id: str
    before_inspection_id: str
    before_drawing_state_hash: str
    before_history_cursor: int
    action_ids: tuple[str, ...]
    after_inspection_id: str
    after_drawing_state_hash: str
    decision: str
    rationale: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "correction_id", _text(self.correction_id, "correction_id"))
        object.__setattr__(self, "residual_id", _text(self.residual_id, "residual_id"))
        object.__setattr__(self, "observation_id", _text(self.observation_id, "observation_id"))
        object.__setattr__(self, "before_inspection_id", _text(self.before_inspection_id, "before_inspection_id"))
        object.__setattr__(self, "before_drawing_state_hash", _digest(self.before_drawing_state_hash, "before_drawing_state_hash"))
        cursor = int(self.before_history_cursor)
        if cursor < 0:
            raise ValueError("before_history_cursor must be >= 0")
        object.__setattr__(self, "before_history_cursor", cursor)
        object.__setattr__(self, "action_ids", _strings(self.action_ids, "action_ids"))
        if not self.action_ids:
            raise ValueError("correction requires at least one action_id")
        object.__setattr__(self, "after_inspection_id", _text(self.after_inspection_id, "after_inspection_id"))
        object.__setattr__(self, "after_drawing_state_hash", _digest(self.after_drawing_state_hash, "after_drawing_state_hash"))
        if self.before_drawing_state_hash == self.after_drawing_state_hash:
            raise ValueError("correction after evidence must differ from before evidence")
        decision = _text(self.decision, "decision")
        if decision not in _CORRECTION_DECISIONS:
            raise ValueError(f"unsupported correction decision: {decision}")
        object.__setattr__(self, "decision", decision)
        object.__setattr__(self, "rationale", _text(self.rationale, "rationale"))

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "img2drawing.vnext.correction.v1",
            "correction_id": self.correction_id,
            "residual_id": self.residual_id,
            "observation_id": self.observation_id,
            "before_inspection_id": self.before_inspection_id,
            "before_drawing_state_hash": self.before_drawing_state_hash,
            "before_history_cursor": self.before_history_cursor,
            "action_ids": list(self.action_ids),
            "after_inspection_id": self.after_inspection_id,
            "after_drawing_state_hash": self.after_drawing_state_hash,
            "decision": self.decision,
            "rationale": self.rationale,
        }

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "CorrectionRecord":
        if raw.get("schema") not in (None, "img2drawing.vnext.correction.v1"):
            raise ValueError(f"unsupported correction schema: {raw.get('schema')!r}")
        return cls(
            correction_id=str(raw["correction_id"]),
            residual_id=str(raw["residual_id"]),
            observation_id=str(raw["observation_id"]),
            before_inspection_id=str(raw["before_inspection_id"]),
            before_drawing_state_hash=str(raw["before_drawing_state_hash"]),
            before_history_cursor=int(raw.get("before_history_cursor", 0)),
            action_ids=tuple(raw.get("action_ids", ())),
            after_inspection_id=str(raw["after_inspection_id"]),
            after_drawing_state_hash=str(raw["after_drawing_state_hash"]),
            decision=str(raw.get("decision", "keep")),
            rationale=str(raw["rationale"]),
        )

    def digest(self) -> str:
        return sha256_obj(self.to_dict())


__all__ = ["CorrectionRecord", "ResidualRecord"]
