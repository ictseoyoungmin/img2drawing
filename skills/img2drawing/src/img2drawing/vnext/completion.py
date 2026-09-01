"""Portable Agent completion provenance for the stage-free vNext session.

A finish record binds one Agent decision to immutable session facts. It is not a
stage, artistic score, or PASS certificate, and it never prevents later edits.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Mapping


FINISH_RECORD_SCHEMA = "img2drawing.vnext.finish_record.v1"
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_FIELDS = {
    "record_id",
    "intent_digest",
    "drawing_state_hash",
    "final_inspection_id",
    "history_cursor",
    "accepted_limitations",
    "unresolved_nonmaterial_notes",
    "rationale",
}
_FORBIDDEN = {"stage", "phase", "cursor", "advance", "close", "reopen", "verdict", "pass_fail", "score"}


def _text(value: Any, field: str) -> str:
    result = str(value).strip()
    if not result:
        raise ValueError(f"{field} must be non-empty")
    return result


def _digest(value: Any, field: str) -> str:
    result = str(value).strip().lower()
    if not _SHA256.fullmatch(result):
        raise ValueError(f"{field} must be a SHA-256 digest")
    return result


def _notes(values: Any, field: str) -> tuple[str, ...]:
    if isinstance(values, str):
        values = (values,)
    try:
        result = tuple(_text(value, field) for value in values)
    except TypeError as exc:
        raise TypeError(f"{field} must be an iterable of strings") from exc
    if len(result) != len(set(result)):
        raise ValueError(f"{field} must contain unique values")
    return result


@dataclass(frozen=True)
class FinishRecord:
    """One Agent decision bound to exact intent, drawing, and inspection truth."""

    record_id: str
    intent_digest: str
    drawing_state_hash: str
    final_inspection_id: str
    history_cursor: int
    accepted_limitations: tuple[str, ...]
    unresolved_nonmaterial_notes: tuple[str, ...]
    rationale: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "record_id", _text(self.record_id, "record_id"))
        object.__setattr__(self, "intent_digest", _digest(self.intent_digest, "intent_digest"))
        object.__setattr__(
            self,
            "drawing_state_hash",
            _digest(self.drawing_state_hash, "drawing_state_hash"),
        )
        inspection_id = _text(self.final_inspection_id, "final_inspection_id")
        if len(inspection_id) != 6 or not inspection_id.isdigit():
            raise ValueError("final_inspection_id must be a six-digit inspection id")
        object.__setattr__(self, "final_inspection_id", inspection_id)
        cursor = int(self.history_cursor)
        if cursor < 0:
            raise ValueError("history_cursor must be >= 0")
        object.__setattr__(self, "history_cursor", cursor)
        object.__setattr__(
            self,
            "accepted_limitations",
            _notes(self.accepted_limitations, "accepted_limitations"),
        )
        object.__setattr__(
            self,
            "unresolved_nonmaterial_notes",
            _notes(self.unresolved_nonmaterial_notes, "unresolved_nonmaterial_notes"),
        )
        object.__setattr__(self, "rationale", _text(self.rationale, "rationale"))

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": FINISH_RECORD_SCHEMA,
            "record_id": self.record_id,
            "intent_digest": self.intent_digest,
            "drawing_state_hash": self.drawing_state_hash,
            "final_inspection_id": self.final_inspection_id,
            "history_cursor": self.history_cursor,
            "accepted_limitations": list(self.accepted_limitations),
            "unresolved_nonmaterial_notes": list(self.unresolved_nonmaterial_notes),
            "rationale": self.rationale,
        }

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "FinishRecord":
        if raw.get("schema") not in (None, FINISH_RECORD_SCHEMA):
            raise ValueError(f"unsupported finish record schema: {raw.get('schema')!r}")
        normalized_keys = {str(key).lower() for key in raw}
        forbidden = _FORBIDDEN.intersection(normalized_keys)
        if forbidden:
            raise ValueError(f"finish record contains lifecycle/verdict fields: {sorted(forbidden)}")
        unknown = set(raw).difference(_FIELDS | {"schema"})
        if unknown:
            raise ValueError(f"finish record contains unsupported fields: {sorted(unknown)}")
        return cls(
            record_id=str(raw["record_id"]),
            intent_digest=str(raw["intent_digest"]),
            drawing_state_hash=str(raw["drawing_state_hash"]),
            final_inspection_id=str(raw["final_inspection_id"]),
            history_cursor=int(raw["history_cursor"]),
            accepted_limitations=tuple(raw.get("accepted_limitations", ())),
            unresolved_nonmaterial_notes=tuple(raw.get("unresolved_nonmaterial_notes", ())),
            rationale=str(raw["rationale"]),
        )

    def matches(
        self,
        *,
        intent_digest: str,
        drawing_state_hash: str,
        history_cursor: int,
    ) -> bool:
        """Return whether this historical decision still describes current truth."""

        return (
            self.intent_digest == str(intent_digest).lower()
            and self.drawing_state_hash == str(drawing_state_hash).lower()
            and self.history_cursor == int(history_cursor)
        )


__all__ = ["FINISH_RECORD_SCHEMA", "FinishRecord"]
