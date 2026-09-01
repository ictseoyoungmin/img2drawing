"""Portable reference-authority records for one shared vNext session.

Authority describes what the Agent may compare the current drawing against. It
does not score the comparison, choose a residual, or create a mode pipeline.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Iterable, Mapping

from ..core.session import sha256_obj
from .intent import REFERENCE_MODES


REFERENCE_AUTHORITY_SCHEMA = "img2drawing.vnext.reference_authority.v1"
REFERENCE_CONSTRAINT_SCHEMA = "img2drawing.vnext.reference_constraint.v1"
CONSTRAINT_DISPOSITIONS = ("preserved", "transformed")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


class ReferenceUnavailableError(RuntimeError):
    """A caller requested subject evidence from a subjectless session."""


def _text(value: Any, field: str) -> str:
    result = str(value).strip()
    if not result:
        raise ValueError(f"{field} must be non-empty")
    return result


def _strings(values: Iterable[Any], field: str) -> tuple[str, ...]:
    result = tuple(_text(value, field) for value in values)
    if len(set(result)) != len(result):
        raise ValueError(f"{field} must contain unique values")
    return result


def _sha256(value: Any, field: str) -> str:
    result = str(value).strip().lower()
    if not _SHA256.fullmatch(result):
        raise ValueError(f"{field} must be a SHA-256 digest")
    return result


@dataclass(frozen=True)
class ReferenceConstraint:
    """One hybrid reference fact and its declared treatment."""

    constraint_id: str
    description: str
    disposition: str
    transformation: str | None = None
    rationale: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "constraint_id", _text(self.constraint_id, "constraint_id"))
        object.__setattr__(self, "description", _text(self.description, "description"))
        disposition = _text(self.disposition, "disposition").lower()
        if disposition not in CONSTRAINT_DISPOSITIONS:
            raise ValueError(f"unsupported constraint disposition: {disposition}")
        object.__setattr__(self, "disposition", disposition)
        transformation = (
            None
            if self.transformation is None
            else _text(self.transformation, "transformation")
        )
        rationale = None if self.rationale is None else _text(self.rationale, "rationale")
        if disposition == "preserved" and transformation is not None:
            raise ValueError("preserved constraint cannot declare a transformation")
        if disposition == "transformed" and (transformation is None or rationale is None):
            raise ValueError("transformed constraint requires transformation and rationale")
        object.__setattr__(self, "transformation", transformation)
        object.__setattr__(self, "rationale", rationale)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": REFERENCE_CONSTRAINT_SCHEMA,
            "constraint_id": self.constraint_id,
            "description": self.description,
            "disposition": self.disposition,
            "transformation": self.transformation,
            "rationale": self.rationale,
        }

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "ReferenceConstraint":
        if raw.get("schema") not in (None, REFERENCE_CONSTRAINT_SCHEMA):
            raise ValueError(f"unsupported reference constraint schema: {raw.get('schema')!r}")
        return cls(
            constraint_id=str(raw["constraint_id"]),
            description=str(raw["description"]),
            disposition=str(raw["disposition"]),
            transformation=raw.get("transformation"),
            rationale=raw.get("rationale"),
        )


@dataclass(frozen=True)
class ReferenceAuthority:
    """Immutable comparison authority for an observed, imaginative, or hybrid session."""

    mode: str
    subject_sha256: str | None = None
    declared_goals: tuple[str, ...] = ()
    constraints: tuple[ReferenceConstraint, ...] = ()

    def __post_init__(self) -> None:
        mode = _text(self.mode, "mode").lower()
        if mode not in REFERENCE_MODES:
            raise ValueError(f"unsupported reference authority mode: {mode}")
        object.__setattr__(self, "mode", mode)
        subject_sha256 = (
            None
            if self.subject_sha256 is None
            else _sha256(self.subject_sha256, "subject_sha256")
        )
        object.__setattr__(self, "subject_sha256", subject_sha256)
        goals = _strings(self.declared_goals, "declared_goals")
        object.__setattr__(self, "declared_goals", goals)
        constraints = tuple(
            item if isinstance(item, ReferenceConstraint) else ReferenceConstraint.from_dict(item)
            for item in self.constraints
        )
        if len({item.constraint_id for item in constraints}) != len(constraints):
            raise ValueError("reference constraints require unique constraint_id values")
        object.__setattr__(self, "constraints", constraints)

        if mode == "observed":
            if subject_sha256 is None:
                raise ValueError("observed authority requires subject_sha256")
            if goals or constraints:
                raise ValueError("observed authority is the readable subject, not declared goals or transformations")
        elif mode == "imaginative":
            if subject_sha256 is not None:
                raise ValueError("imaginative authority cannot carry a subject hash")
            if not goals:
                raise ValueError("imaginative authority requires declared_goals")
            if constraints:
                raise ValueError("imaginative authority cannot carry reference constraints")
        else:
            if subject_sha256 is None:
                raise ValueError("hybrid authority requires subject_sha256")
            dispositions = {item.disposition for item in constraints}
            if dispositions != set(CONSTRAINT_DISPOSITIONS):
                raise ValueError("hybrid authority requires both preserved and transformed constraints")

    @classmethod
    def observed(cls, subject_sha256: str) -> "ReferenceAuthority":
        return cls(mode="observed", subject_sha256=subject_sha256)

    @classmethod
    def imaginative(cls, declared_goals: Iterable[str]) -> "ReferenceAuthority":
        return cls(mode="imaginative", declared_goals=tuple(declared_goals))

    @classmethod
    def hybrid(
        cls,
        subject_sha256: str,
        constraints: Iterable[ReferenceConstraint | Mapping[str, Any]],
        *,
        declared_goals: Iterable[str] = (),
    ) -> "ReferenceAuthority":
        return cls(
            mode="hybrid",
            subject_sha256=subject_sha256,
            declared_goals=tuple(declared_goals),
            constraints=tuple(constraints),
        )

    @property
    def preserved_constraints(self) -> tuple[ReferenceConstraint, ...]:
        return tuple(item for item in self.constraints if item.disposition == "preserved")

    @property
    def transformed_constraints(self) -> tuple[ReferenceConstraint, ...]:
        return tuple(item for item in self.constraints if item.disposition == "transformed")

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": REFERENCE_AUTHORITY_SCHEMA,
            "mode": self.mode,
            "subject_sha256": self.subject_sha256,
            "declared_goals": list(self.declared_goals),
            "constraints": [item.to_dict() for item in self.constraints],
        }

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "ReferenceAuthority":
        if raw.get("schema") not in (None, REFERENCE_AUTHORITY_SCHEMA):
            raise ValueError(f"unsupported reference authority schema: {raw.get('schema')!r}")
        authority = cls(
            mode=str(raw["mode"]),
            subject_sha256=raw.get("subject_sha256"),
            declared_goals=tuple(raw.get("declared_goals", ())),
            constraints=tuple(raw.get("constraints", ())),
        )
        supplied_digest = raw.get("digest")
        if supplied_digest is not None and str(supplied_digest).lower() != authority.digest():
            raise ValueError("reference authority digest does not match payload")
        return authority

    def digest(self) -> str:
        return sha256_obj(self.to_dict())

    def checkpoint_dict(self) -> dict[str, Any]:
        return {**self.to_dict(), "digest": self.digest()}


__all__ = [
    "CONSTRAINT_DISPOSITIONS",
    "REFERENCE_AUTHORITY_SCHEMA",
    "REFERENCE_CONSTRAINT_SCHEMA",
    "ReferenceAuthority",
    "ReferenceConstraint",
    "ReferenceUnavailableError",
]
