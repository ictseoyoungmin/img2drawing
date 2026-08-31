"""Portable, stage-free drawing intent and authoring guidance.

The values in this module are selections, not workflow state.  A mode does not
open a pipeline, a style does not select a renderer, and changing intent never
changes drawing geometry.  ``DrawingSession`` records when these plain-data
values are selected or changed.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, replace
from typing import Any, Mapping, Sequence

from ..core.session import sha256_obj


REFERENCE_MODES = ("observed", "imaginative", "hybrid")
DRAWING_MODES = ("croquis", "figure_drawing", "tonal_study", "free_draw")
FINISH_INTENTS = ("pose", "subject", "form_light", "expressive")
STYLE_PROFILES = ("pencil_loose", "graphite_academic")
COMPATIBILITY_INTENTS = ("full_body_croquis",)
INTENT_SCHEMA = "img2drawing.vnext.drawing_intent.v1"
MODE_GUIDE_SCHEMA = "img2drawing.vnext.mode_guide.v1"
STYLE_GUIDE_SCHEMA = "img2drawing.vnext.style_guide.v1"
INTENT_EVENT_SCHEMA = "img2drawing.vnext.intent_change.v1"
_CUSTOM_STYLE = re.compile(r"^custom:[a-z0-9][a-z0-9._-]*$")
_FORBIDDEN_GUIDE_KEYS = {
    "phase",
    "phase_count",
    "stage",
    "cursor",
    "advance",
    "close",
    "verdict",
    "pass_fail",
}
_GUIDE_FIELDS = {
    "guide_id",
    "drawing_mode",
    "primary_observations",
    "recommended_grammar",
    "omissions",
    "finish_emphasis",
    "completion_questions",
}
_STYLE_FIELDS = {
    "style_profile",
    "line_behavior",
    "construction_visibility",
    "detail_policy",
    "value_policy",
    "edge_policy",
    "authoring_notes",
}


def _text(value: Any, field: str) -> str:
    result = str(value).strip()
    if not result:
        raise ValueError(f"{field} must be non-empty")
    return result


def _axis(value: Any, field: str, choices: Sequence[str]) -> str:
    result = _text(value, field).lower()
    if result not in choices:
        raise ValueError(f"unsupported {field}: {result}")
    return result


def _style(value: Any) -> str:
    result = _text(value, "style_profile").lower()
    if result not in STYLE_PROFILES and not _CUSTOM_STYLE.fullmatch(result):
        raise ValueError(
            f"unsupported style_profile: {result}; use a built-in profile or custom:<identifier>"
        )
    return result


def _strings(values: Any, field: str) -> tuple[str, ...]:
    if isinstance(values, str):
        values = (values,)
    try:
        result = tuple(_text(value, field) for value in values)
    except TypeError as exc:
        raise TypeError(f"{field} must be an iterable of strings") from exc
    if not result:
        raise ValueError(f"{field} must contain at least one item")
    return result


@dataclass(frozen=True)
class IntentProvenance:
    """Optional source context carried by one intent value."""

    source: str | None = None
    reason: str | None = None
    compatibility_key: str | None = None

    def __post_init__(self) -> None:
        normalized = {
            name: None if value is None else _text(value, name)
            for name, value in (
                ("source", self.source),
                ("reason", self.reason),
                ("compatibility_key", self.compatibility_key),
            )
        }
        if not any(normalized.values()):
            raise ValueError("intent provenance requires source, reason, or compatibility_key")
        object.__setattr__(self, "source", normalized["source"])
        object.__setattr__(self, "reason", normalized["reason"])
        object.__setattr__(self, "compatibility_key", normalized["compatibility_key"])

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "reason": self.reason,
            "compatibility_key": self.compatibility_key,
        }

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "IntentProvenance":
        return cls(
            source=raw.get("source"),
            reason=raw.get("reason"),
            compatibility_key=raw.get("compatibility_key"),
        )


@dataclass(frozen=True)
class DrawingIntent:
    """Four independent data selections for one shared drawing core."""

    reference_mode: str = "observed"
    drawing_mode: str = "croquis"
    finish_intent: str = "pose"
    style_profile: str = "pencil_loose"
    provenance: IntentProvenance | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "reference_mode", _axis(self.reference_mode, "reference_mode", REFERENCE_MODES))
        object.__setattr__(self, "drawing_mode", _axis(self.drawing_mode, "drawing_mode", DRAWING_MODES))
        object.__setattr__(self, "finish_intent", _axis(self.finish_intent, "finish_intent", FINISH_INTENTS))
        object.__setattr__(self, "style_profile", _style(self.style_profile))
        provenance = self.provenance
        if provenance is not None and not isinstance(provenance, IntentProvenance):
            provenance = IntentProvenance.from_dict(provenance)
        object.__setattr__(self, "provenance", provenance)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": INTENT_SCHEMA,
            "reference_mode": self.reference_mode,
            "drawing_mode": self.drawing_mode,
            "finish_intent": self.finish_intent,
            "style_profile": self.style_profile,
            "provenance": None if self.provenance is None else self.provenance.to_dict(),
        }

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "DrawingIntent":
        if raw.get("schema") not in (None, INTENT_SCHEMA):
            raise ValueError(f"unsupported drawing intent schema: {raw.get('schema')!r}")
        provenance = raw.get("provenance")
        return cls(
            reference_mode=raw.get("reference_mode", "observed"),
            drawing_mode=raw.get("drawing_mode", "croquis"),
            finish_intent=raw.get("finish_intent", "pose"),
            style_profile=raw.get("style_profile", "pencil_loose"),
            provenance=None if provenance is None else IntentProvenance.from_dict(provenance),
        )

    def digest(self) -> str:
        return sha256_obj(self.to_dict())


@dataclass(frozen=True)
class IntentChangeRecord:
    """Append-only session provenance for one selected intent value."""

    event_id: str
    intent: DrawingIntent
    previous_intent_digest: str | None
    reason: str
    history_cursor: int

    def __post_init__(self) -> None:
        object.__setattr__(self, "event_id", _text(self.event_id, "event_id"))
        intent = self.intent if isinstance(self.intent, DrawingIntent) else DrawingIntent.from_dict(self.intent)
        object.__setattr__(self, "intent", intent)
        previous = self.previous_intent_digest
        if previous is not None:
            previous = _text(previous, "previous_intent_digest").lower()
            if not re.fullmatch(r"[0-9a-f]{64}", previous):
                raise ValueError("previous_intent_digest must be a SHA-256 digest")
        object.__setattr__(self, "previous_intent_digest", previous)
        object.__setattr__(self, "reason", _text(self.reason, "reason"))
        cursor = int(self.history_cursor)
        if cursor < 0:
            raise ValueError("history_cursor must be >= 0")
        object.__setattr__(self, "history_cursor", cursor)

    @property
    def intent_digest(self) -> str:
        return self.intent.digest()

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": INTENT_EVENT_SCHEMA,
            "event_id": self.event_id,
            "intent": self.intent.to_dict(),
            "intent_digest": self.intent_digest,
            "previous_intent_digest": self.previous_intent_digest,
            "reason": self.reason,
            "history_cursor": self.history_cursor,
        }

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "IntentChangeRecord":
        if raw.get("schema") not in (None, INTENT_EVENT_SCHEMA):
            raise ValueError(f"unsupported intent change schema: {raw.get('schema')!r}")
        intent = DrawingIntent.from_dict(raw["intent"])
        supplied_digest = raw.get("intent_digest")
        if supplied_digest is None or str(supplied_digest).lower() != intent.digest():
            raise ValueError("intent change digest does not match intent payload")
        return cls(
            event_id=str(raw["event_id"]),
            intent=intent,
            previous_intent_digest=raw.get("previous_intent_digest"),
            reason=str(raw["reason"]),
            history_cursor=int(raw.get("history_cursor", 0)),
        )


@dataclass(frozen=True)
class ModeGuide:
    """Immutable observations and questions for one drawing mode."""

    guide_id: str
    drawing_mode: str
    primary_observations: tuple[str, ...]
    recommended_grammar: tuple[str, ...]
    omissions: tuple[str, ...]
    finish_emphasis: tuple[str, ...]
    completion_questions: tuple[str, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "guide_id", _text(self.guide_id, "guide_id"))
        object.__setattr__(self, "drawing_mode", _axis(self.drawing_mode, "drawing_mode", DRAWING_MODES))
        for field in (
            "primary_observations",
            "recommended_grammar",
            "omissions",
            "finish_emphasis",
            "completion_questions",
        ):
            object.__setattr__(self, field, _strings(getattr(self, field), field))

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": MODE_GUIDE_SCHEMA,
            "guide_id": self.guide_id,
            "drawing_mode": self.drawing_mode,
            "primary_observations": list(self.primary_observations),
            "recommended_grammar": list(self.recommended_grammar),
            "omissions": list(self.omissions),
            "finish_emphasis": list(self.finish_emphasis),
            "completion_questions": list(self.completion_questions),
        }

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "ModeGuide":
        if raw.get("schema") not in (None, MODE_GUIDE_SCHEMA):
            raise ValueError(f"unsupported mode guide schema: {raw.get('schema')!r}")
        forbidden = _FORBIDDEN_GUIDE_KEYS.intersection(str(key).lower() for key in raw)
        if forbidden:
            raise ValueError(f"mode guide contains lifecycle fields: {sorted(forbidden)}")
        unknown = set(raw).difference(_GUIDE_FIELDS | {"schema"})
        if unknown:
            raise ValueError(f"mode guide contains unsupported fields: {sorted(unknown)}")
        return cls(
            guide_id=str(raw["guide_id"]),
            drawing_mode=str(raw["drawing_mode"]),
            primary_observations=tuple(raw["primary_observations"]),
            recommended_grammar=tuple(raw["recommended_grammar"]),
            omissions=tuple(raw["omissions"]),
            finish_emphasis=tuple(raw["finish_emphasis"]),
            completion_questions=tuple(raw["completion_questions"]),
        )


@dataclass(frozen=True)
class StyleGuide:
    """Authoring guidance for a style profile; never a pixel post-filter."""

    style_profile: str
    line_behavior: tuple[str, ...]
    construction_visibility: tuple[str, ...]
    detail_policy: tuple[str, ...]
    value_policy: tuple[str, ...]
    edge_policy: tuple[str, ...]
    authoring_notes: tuple[str, ...]

    def __post_init__(self) -> None:
        profile = _style(self.style_profile)
        if profile not in STYLE_PROFILES:
            raise ValueError("StyleGuide requires a built-in style_profile")
        object.__setattr__(self, "style_profile", profile)
        for field in (
            "line_behavior",
            "construction_visibility",
            "detail_policy",
            "value_policy",
            "edge_policy",
            "authoring_notes",
        ):
            object.__setattr__(self, field, _strings(getattr(self, field), field))

    def with_overrides(self, overrides: Mapping[str, Any]) -> "StyleGuide":
        if not isinstance(overrides, Mapping):
            raise TypeError("style overrides must be a mapping")
        unknown = set(overrides).difference(_STYLE_FIELDS)
        if unknown:
            raise ValueError(f"style overrides contain unsupported fields: {sorted(unknown)}")
        if "style_profile" in overrides:
            raise ValueError("style overrides cannot replace the base style_profile")
        values = {}
        for field in _STYLE_FIELDS - {"style_profile"}:
            if field in overrides:
                values[field] = _strings(overrides[field], field)
        return replace(self, **values)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": STYLE_GUIDE_SCHEMA,
            "style_profile": self.style_profile,
            "line_behavior": list(self.line_behavior),
            "construction_visibility": list(self.construction_visibility),
            "detail_policy": list(self.detail_policy),
            "value_policy": list(self.value_policy),
            "edge_policy": list(self.edge_policy),
            "authoring_notes": list(self.authoring_notes),
        }

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "StyleGuide":
        if raw.get("schema") not in (None, STYLE_GUIDE_SCHEMA):
            raise ValueError(f"unsupported style guide schema: {raw.get('schema')!r}")
        forbidden = _FORBIDDEN_GUIDE_KEYS.intersection(str(key).lower() for key in raw)
        if forbidden:
            raise ValueError(f"style guide contains lifecycle fields: {sorted(forbidden)}")
        unknown = set(raw).difference(_STYLE_FIELDS | {"schema"})
        if unknown:
            raise ValueError(f"style guide contains unsupported fields: {sorted(unknown)}")
        return cls(
            style_profile=str(raw["style_profile"]),
            line_behavior=tuple(raw["line_behavior"]),
            construction_visibility=tuple(raw["construction_visibility"]),
            detail_policy=tuple(raw["detail_policy"]),
            value_policy=tuple(raw["value_policy"]),
            edge_policy=tuple(raw["edge_policy"]),
            authoring_notes=tuple(raw["authoring_notes"]),
        )


_MODE_GUIDES = {
    "croquis": ModeGuide(
        "mode-croquis-v1", "croquis",
        ("gesture direction", "weight and balance", "major turning points"),
        ("whole pose", "flow through masses", "selected contour"),
        ("small features", "uniform contour polishing"),
        ("liveliness of the pose", "economical decisive marks"),
        ("Does the gesture read at a glance?", "Do the largest masses balance?")
    ),
    "figure_drawing": ModeGuide(
        "mode-figure-drawing-v1", "figure_drawing",
        ("landmark alignment", "joint relationships", "weight-bearing structure"),
        ("envelope", "mass relationships", "limb connections", "selected contour"),
        ("decorative detail before structure", "isolated local polish"),
        ("clarity of anatomy and overlap", "coherent contour rhythm"),
        ("Do the landmarks agree across the pose?", "Are overlaps and weight legible?")
    ),
    "tonal_study": ModeGuide(
        "mode-tonal-study-v1", "tonal_study",
        ("value grouping", "light direction", "dominant shadow mass"),
        ("large value fields", "form turns", "edge accents"),
        ("micro-detail without value support", "equal emphasis everywhere"),
        ("stable value hierarchy", "edges serving the light"),
        ("Is the light direction consistent?", "Do the value groups describe form?")
    ),
    "free_draw": ModeGuide(
        "mode-free-draw-v1", "free_draw",
        ("chosen motif", "spatial rhythm", "mark intent"),
        ("motif selection", "rhythmic construction", "selective emphasis"),
        ("unselected detail", "accidental uniformity"),
        ("expressive coherence", "intentional variation"),
        ("What is the drawing asking the viewer to notice?", "Do the marks support that choice?")
    ),
}

_STYLE_GUIDES = {
    "pencil_loose": StyleGuide(
        "pencil_loose",
        ("vary pressure and speed", "let searching lines remain economical"),
        ("keep useful construction visible", "separate exploratory and committed marks by role"),
        ("prefer selective accents", "stop before detail flattens the gesture"),
        ("use sparse value cues", "reserve darker marks for structural emphasis"),
        ("allow lively edge variation", "avoid tracing every boundary uniformly"),
        ("Author the marks directly; this profile does not apply a raster effect.",),
    ),
    "graphite_academic": StyleGuide(
        "graphite_academic",
        ("use measured, controlled strokes", "vary pressure to describe turning form"),
        ("retain construction when it explains alignment", "clarify committed contours by role"),
        ("build detail from large relationships", "let detail follow observed structure"),
        ("group values before accents", "use a measured dark-light hierarchy"),
        ("sharpen edges selectively", "soften edges where form turns away"),
        ("Author value and edge decisions in the drawing; this is not a post-filter.",),
    ),
}


def resolve_mode_guide(drawing_mode: str) -> ModeGuide:
    mode = _axis(drawing_mode, "drawing_mode", DRAWING_MODES)
    return _MODE_GUIDES[mode]


def resolve_style_guide(style_profile: str, overrides: Mapping[str, Any] | None = None) -> StyleGuide:
    profile = _style(style_profile)
    try:
        guide = _STYLE_GUIDES[profile]
    except KeyError as exc:
        raise ValueError("custom style profiles require explicit Agent-authored prose") from exc
    return guide if overrides is None else guide.with_overrides(overrides)


def compatibility_intent(alias: str) -> DrawingIntent:
    key = _text(alias, "compatibility alias").lower()
    if key != "full_body_croquis":
        raise ValueError(f"unsupported compatibility intent: {key}")
    return DrawingIntent(
        reference_mode="observed",
        drawing_mode="croquis",
        finish_intent="pose",
        style_profile="pencil_loose",
        provenance=IntentProvenance(
            source="legacy compatibility lookup",
            compatibility_key=key,
        ),
    )


__all__ = [
    "COMPATIBILITY_INTENTS",
    "DRAWING_MODES",
    "FINISH_INTENTS",
    "INTENT_SCHEMA",
    "IntentChangeRecord",
    "IntentProvenance",
    "DrawingIntent",
    "ModeGuide",
    "REFERENCE_MODES",
    "STYLE_PROFILES",
    "STYLE_GUIDE_SCHEMA",
    "MODE_GUIDE_SCHEMA",
    "StyleGuide",
    "compatibility_intent",
    "resolve_mode_guide",
    "resolve_style_guide",
]
