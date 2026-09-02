"""Derived navigation records for the one authoritative drawing history.

Nothing in this module is persisted as mutable ownership state. Every record is rebuilt
from ``CanvasHistory`` up to its current cursor, so queries and summaries can never drift
from replay truth or turn into a second edit history.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, Iterable, Mapping, Sequence

from ..core.history import CanvasAction, CanvasHistory


AUTHORED_ELEMENT_SCHEMA = "img2drawing.vnext.authored_element.v1"
AUTHORING_SUMMARY_SCHEMA = "img2drawing.vnext.authoring_summary.v1"
ELEMENT_TYPES = ("stroke", "fill")
ELEMENT_STATUSES = ("current", "superseded", "deleted")


def _optional_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _identity(value: Any, field: str) -> str:
    text = str(value).strip()
    if not text:
        raise ValueError(f"{field} must be non-empty")
    return text


@dataclass(frozen=True)
class AuthoredElement:
    """Portable identity/provenance view of one authored stroke or fill decision."""

    element_type: str
    element_id: str
    status: str
    part: str | None
    role: str | None
    created_seq: int
    latest_seq: int
    created_action_id: str | None
    latest_action_id: str | None
    latest_action_kind: str
    action_ids: tuple[str, ...]
    observation_ids: tuple[str, ...]
    reason: str | None = None
    superseded_by: str | None = None
    revision_count: int = 0

    def __post_init__(self) -> None:
        element_type = _identity(self.element_type, "element_type")
        if element_type not in ELEMENT_TYPES:
            raise ValueError(f"unsupported element_type: {element_type}")
        status = _identity(self.status, "status")
        if status not in ELEMENT_STATUSES:
            raise ValueError(f"unsupported element status: {status}")
        object.__setattr__(self, "element_type", element_type)
        object.__setattr__(self, "element_id", _identity(self.element_id, "element_id"))
        object.__setattr__(self, "status", status)
        object.__setattr__(self, "part", _optional_text(self.part))
        object.__setattr__(self, "role", _optional_text(self.role))
        created_seq = int(self.created_seq)
        latest_seq = int(self.latest_seq)
        if created_seq <= 0 or latest_seq < created_seq:
            raise ValueError("authored element sequence range is invalid")
        object.__setattr__(self, "created_seq", created_seq)
        object.__setattr__(self, "latest_seq", latest_seq)
        object.__setattr__(self, "created_action_id", _optional_text(self.created_action_id))
        object.__setattr__(self, "latest_action_id", _optional_text(self.latest_action_id))
        object.__setattr__(self, "latest_action_kind", _identity(self.latest_action_kind, "latest_action_kind"))
        action_ids = tuple(dict.fromkeys(_identity(item, "action_id") for item in self.action_ids))
        observations = tuple(
            dict.fromkeys(_identity(item, "observation_id") for item in self.observation_ids)
        )
        object.__setattr__(self, "action_ids", action_ids)
        object.__setattr__(self, "observation_ids", observations)
        object.__setattr__(self, "reason", _optional_text(self.reason))
        object.__setattr__(self, "superseded_by", _optional_text(self.superseded_by))
        revisions = int(self.revision_count)
        if revisions < 0:
            raise ValueError("revision_count must be >= 0")
        object.__setattr__(self, "revision_count", revisions)
        if status == "superseded" and self.superseded_by is None:
            raise ValueError("superseded element requires superseded_by")
        if status != "superseded" and self.superseded_by is not None:
            raise ValueError("only superseded elements may carry superseded_by")

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": AUTHORED_ELEMENT_SCHEMA,
            "element_type": self.element_type,
            "element_id": self.element_id,
            "status": self.status,
            "part": self.part,
            "role": self.role,
            "created_seq": self.created_seq,
            "latest_seq": self.latest_seq,
            "created_action_id": self.created_action_id,
            "latest_action_id": self.latest_action_id,
            "latest_action_kind": self.latest_action_kind,
            "action_ids": list(self.action_ids),
            "observation_ids": list(self.observation_ids),
            "reason": self.reason,
            "superseded_by": self.superseded_by,
            "revision_count": self.revision_count,
        }

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "AuthoredElement":
        if raw.get("schema") not in (None, AUTHORED_ELEMENT_SCHEMA):
            raise ValueError(f"unsupported authored element schema: {raw.get('schema')!r}")
        return cls(
            element_type=str(raw["element_type"]),
            element_id=str(raw["element_id"]),
            status=str(raw["status"]),
            part=raw.get("part"),
            role=raw.get("role"),
            created_seq=int(raw["created_seq"]),
            latest_seq=int(raw["latest_seq"]),
            created_action_id=raw.get("created_action_id"),
            latest_action_id=raw.get("latest_action_id"),
            latest_action_kind=str(raw["latest_action_kind"]),
            action_ids=tuple(raw.get("action_ids", ())),
            observation_ids=tuple(raw.get("observation_ids", ())),
            reason=raw.get("reason"),
            superseded_by=raw.get("superseded_by"),
            revision_count=int(raw.get("revision_count", 0)),
        )


@dataclass(frozen=True)
class AuthoringSummary:
    """Bounded, derived context view tied to a cursor and drawing-state digest."""

    history_cursor: int
    drawing_state_hash: str
    current_strokes: int
    current_fills: int
    superseded_strokes: int
    deleted_strokes: int
    open_residual_ids: tuple[str, ...]
    elements: tuple[AuthoredElement, ...]
    total_matching_elements: int
    truncated: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": AUTHORING_SUMMARY_SCHEMA,
            "history_cursor": self.history_cursor,
            "drawing_state_hash": self.drawing_state_hash,
            "counts": {
                "current_strokes": self.current_strokes,
                "current_fills": self.current_fills,
                "superseded_strokes": self.superseded_strokes,
                "deleted_strokes": self.deleted_strokes,
                "open_residuals": len(self.open_residual_ids),
            },
            "open_residual_ids": list(self.open_residual_ids),
            "elements": [element.to_dict() for element in self.elements],
            "total_matching_elements": self.total_matching_elements,
            "truncated": self.truncated,
        }


def _action_facts(action: CanvasAction) -> tuple[str | None, str | None, str | None]:
    provenance = action.provenance or {}
    return (
        _optional_text(provenance.get("action_id")),
        _optional_text(provenance.get("observation_id")),
        _optional_text(provenance.get("reason")),
    )


def _append_unique(values: tuple[str, ...], value: str | None) -> tuple[str, ...]:
    if value is None or value in values:
        return values
    return (*values, value)


def _new_element(
    *,
    element_type: str,
    element_id: str,
    action: CanvasAction,
    part: str | None,
    role: str | None,
) -> AuthoredElement:
    action_id, observation_id, reason = _action_facts(action)
    return AuthoredElement(
        element_type=element_type,
        element_id=element_id,
        status="current",
        part=part,
        role=role,
        created_seq=action.seq,
        latest_seq=action.seq,
        created_action_id=action_id,
        latest_action_id=action_id,
        latest_action_kind=action.action,
        action_ids=() if action_id is None else (action_id,),
        observation_ids=() if observation_id is None else (observation_id,),
        reason=reason,
    )


def _touch(
    element: AuthoredElement,
    action: CanvasAction,
    *,
    status: str | None = None,
    superseded_by: str | None = None,
    part: str | None = None,
    role: str | None = None,
    revision_increment: int = 0,
) -> AuthoredElement:
    action_id, observation_id, reason = _action_facts(action)
    return replace(
        element,
        status=element.status if status is None else status,
        part=element.part if part is None else part,
        role=element.role if role is None else role,
        latest_seq=action.seq,
        latest_action_id=action_id,
        latest_action_kind=action.action,
        action_ids=_append_unique(element.action_ids, action_id),
        observation_ids=_append_unique(element.observation_ids, observation_id),
        reason=reason,
        superseded_by=superseded_by,
        revision_count=element.revision_count + int(revision_increment),
    )


def authored_elements(history: CanvasHistory) -> tuple[AuthoredElement, ...]:
    """Rebuild authored stroke/fill identity state from actions up to current cursor."""

    records: dict[tuple[str, str], AuthoredElement] = {}
    order: list[tuple[str, str]] = []
    for action in history.actions[: history.cursor]:
        payload = action.payload
        if action.action == "stroke.add":
            raw = payload.get("stroke") or {}
            stroke_id = _identity(raw.get("stroke_id"), "stroke_id")
            key = ("stroke", stroke_id)
            if key in records:
                raise ValueError(f"duplicate authored stroke identity: {stroke_id}")
            records[key] = _new_element(
                element_type="stroke",
                element_id=stroke_id,
                action=action,
                part=raw.get("part", action.part),
                role=raw.get("role", action.role),
            )
            order.append(key)
        elif action.action == "stroke.replace":
            old_id = _identity(payload.get("stroke_id"), "stroke_id")
            raw = payload.get("stroke") or {}
            new_id = _identity(raw.get("stroke_id"), "replacement stroke_id")
            old_key = ("stroke", old_id)
            if old_key not in records or records[old_key].status != "current":
                raise ValueError(f"replacement targets non-current stroke: {old_id}")
            if new_id == old_id:
                records[old_key] = _touch(
                    records[old_key],
                    action,
                    part=raw.get("part", action.part),
                    role=raw.get("role", action.role),
                    revision_increment=1,
                )
            else:
                new_key = ("stroke", new_id)
                if new_key in records:
                    raise ValueError(f"duplicate replacement stroke identity: {new_id}")
                records[old_key] = _touch(
                    records[old_key], action, status="superseded", superseded_by=new_id
                )
                records[new_key] = _new_element(
                    element_type="stroke",
                    element_id=new_id,
                    action=action,
                    part=raw.get("part", action.part),
                    role=raw.get("role", action.role),
                )
                order.append(new_key)
        elif action.action in {"stroke.segment_replace", "stroke.segment_soft_lift", "stroke.soft_lift"}:
            stroke_id = _identity(payload.get("stroke_id"), "stroke_id")
            key = ("stroke", stroke_id)
            if key not in records or records[key].status != "current":
                raise ValueError(f"local edit targets non-current stroke: {stroke_id}")
            records[key] = _touch(records[key], action, revision_increment=1)
        elif action.action == "stroke.delete":
            stroke_id = _identity(payload.get("stroke_id"), "stroke_id")
            key = ("stroke", stroke_id)
            if key not in records or records[key].status != "current":
                raise ValueError(f"delete targets non-current stroke: {stroke_id}")
            records[key] = _touch(records[key], action, status="deleted")
        elif action.action == "region.fill":
            raw = payload.get("region") or {}
            fill_id = _identity(raw.get("fill_id"), "fill_id")
            key = ("fill", fill_id)
            if key in records:
                raise ValueError(f"duplicate authored fill identity: {fill_id}")
            records[key] = _new_element(
                element_type="fill",
                element_id=fill_id,
                action=action,
                part=raw.get("part", action.part),
                role=raw.get("role", action.role),
            )
            order.append(key)
        elif action.action == "region.replace":
            raw = payload.get("region") or {}
            fill_id = _identity(payload.get("fill_id") or raw.get("fill_id"), "fill_id")
            key = ("fill", fill_id)
            if key not in records or records[key].status != "current":
                raise ValueError(f"replacement targets non-current fill: {fill_id}")
            records[key] = _touch(
                records[key],
                action,
                part=raw.get("part", action.part),
                role=raw.get("role", action.role),
                revision_increment=1,
            )
    return tuple(records[key] for key in order)


def filter_elements(
    elements: Iterable[AuthoredElement],
    *,
    element_type: str | None = None,
    status: str | None = "current",
    part: str | None = None,
    role: str | None = None,
    action_id: str | None = None,
    observation_id: str | None = None,
) -> tuple[AuthoredElement, ...]:
    """Filter one derived index without inspecting or mutating drawing geometry."""

    if element_type is not None and element_type not in ELEMENT_TYPES:
        raise ValueError(f"unsupported element_type: {element_type}")
    if status is not None and status not in ELEMENT_STATUSES:
        raise ValueError(f"unsupported element status: {status}")
    return tuple(
        element
        for element in elements
        if (element_type is None or element.element_type == element_type)
        and (status is None or element.status == status)
        and (part is None or element.part == part)
        and (role is None or element.role == role)
        and (action_id is None or action_id in element.action_ids)
        and (observation_id is None or observation_id in element.observation_ids)
    )


def resolve_current_element(
    elements: Sequence[AuthoredElement],
    element_id: str,
    *,
    element_type: str | None = None,
) -> AuthoredElement | None:
    """Follow a stroke replacement chain; deleted identities resolve to ``None``."""

    requested = _identity(element_id, "element_id")
    candidates = [
        element
        for element in elements
        if element.element_id == requested
        and (element_type is None or element.element_type == element_type)
    ]
    if len(candidates) > 1:
        raise ValueError(f"ambiguous authored element identity: {requested}; supply element_type")
    if not candidates:
        raise ValueError(f"missing authored element: {requested}")
    current = candidates[0]
    seen = {(current.element_type, current.element_id)}
    while current.status == "superseded":
        next_id = current.superseded_by
        matches = [
            element
            for element in elements
            if element.element_type == current.element_type and element.element_id == next_id
        ]
        if len(matches) != 1:
            raise ValueError(f"broken supersession chain from {current.element_id}")
        current = matches[0]
        key = (current.element_type, current.element_id)
        if key in seen:
            raise ValueError(f"cyclic supersession chain at {current.element_id}")
        seen.add(key)
    return None if current.status == "deleted" else current


__all__ = [
    "AUTHORED_ELEMENT_SCHEMA",
    "AUTHORING_SUMMARY_SCHEMA",
    "ELEMENT_STATUSES",
    "ELEMENT_TYPES",
    "AuthoredElement",
    "AuthoringSummary",
    "authored_elements",
    "filter_elements",
    "resolve_current_element",
]
