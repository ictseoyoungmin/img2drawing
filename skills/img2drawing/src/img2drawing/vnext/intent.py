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
FINISH_GUIDE_SCHEMA = "img2drawing.vnext.finish_guide.v1"
FINISH_RELATION_SCHEMA = "img2drawing.vnext.finish_relation.v1"
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
_FINISH_RELATION_FIELDS = {
    "part",
    "observations",
    "authoring_policy",
    "avoid",
}
_FINISH_GUIDE_FIELDS = {
    "guide_id",
    "finish_intent",
    "priorities",
    "preserve",
    "mark_policy",
    "value_policy",
    "edge_policy",
    "omissions",
    "relations",
    "completion_questions",
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
class FinishRelation:
    """One observed relationship that can carry a finish intent."""

    part: str
    observations: tuple[str, ...]
    authoring_policy: tuple[str, ...]
    avoid: tuple[str, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "part", _text(self.part, "part"))
        for field in ("observations", "authoring_policy", "avoid"):
            object.__setattr__(self, field, _strings(getattr(self, field), field))

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": FINISH_RELATION_SCHEMA,
            "part": self.part,
            "observations": list(self.observations),
            "authoring_policy": list(self.authoring_policy),
            "avoid": list(self.avoid),
        }

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "FinishRelation":
        if raw.get("schema") not in (None, FINISH_RELATION_SCHEMA):
            raise ValueError(f"unsupported finish relation schema: {raw.get('schema')!r}")
        forbidden = _FORBIDDEN_GUIDE_KEYS.intersection(str(key).lower() for key in raw)
        if forbidden:
            raise ValueError(f"finish relation contains lifecycle fields: {sorted(forbidden)}")
        unknown = set(raw).difference(_FINISH_RELATION_FIELDS | {"schema"})
        if unknown:
            raise ValueError(f"finish relation contains unsupported fields: {sorted(unknown)}")
        return cls(
            part=str(raw["part"]),
            observations=tuple(raw["observations"]),
            authoring_policy=tuple(raw["authoring_policy"]),
            avoid=tuple(raw["avoid"]),
        )


@dataclass(frozen=True)
class FinishGuide:
    """Immutable authoring policy for one finish intent; never a finish state."""

    guide_id: str
    finish_intent: str
    priorities: tuple[str, ...]
    preserve: tuple[str, ...]
    mark_policy: tuple[str, ...]
    value_policy: tuple[str, ...]
    edge_policy: tuple[str, ...]
    omissions: tuple[str, ...]
    relations: tuple[FinishRelation, ...]
    completion_questions: tuple[str, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "guide_id", _text(self.guide_id, "guide_id"))
        object.__setattr__(
            self,
            "finish_intent",
            _axis(self.finish_intent, "finish_intent", FINISH_INTENTS),
        )
        for field in (
            "priorities",
            "preserve",
            "mark_policy",
            "value_policy",
            "edge_policy",
            "omissions",
            "completion_questions",
        ):
            object.__setattr__(self, field, _strings(getattr(self, field), field))
        relations = tuple(
            value if isinstance(value, FinishRelation) else FinishRelation.from_dict(value)
            for value in self.relations
        )
        if not relations:
            raise ValueError("relations must contain at least one finish relation")
        parts = [relation.part for relation in relations]
        if len(parts) != len(set(parts)):
            raise ValueError("finish relation parts must be unique")
        object.__setattr__(self, "relations", relations)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": FINISH_GUIDE_SCHEMA,
            "guide_id": self.guide_id,
            "finish_intent": self.finish_intent,
            "priorities": list(self.priorities),
            "preserve": list(self.preserve),
            "mark_policy": list(self.mark_policy),
            "value_policy": list(self.value_policy),
            "edge_policy": list(self.edge_policy),
            "omissions": list(self.omissions),
            "relations": [relation.to_dict() for relation in self.relations],
            "completion_questions": list(self.completion_questions),
        }

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "FinishGuide":
        if raw.get("schema") not in (None, FINISH_GUIDE_SCHEMA):
            raise ValueError(f"unsupported finish guide schema: {raw.get('schema')!r}")
        forbidden = _FORBIDDEN_GUIDE_KEYS.intersection(str(key).lower() for key in raw)
        if forbidden:
            raise ValueError(f"finish guide contains lifecycle fields: {sorted(forbidden)}")
        unknown = set(raw).difference(_FINISH_GUIDE_FIELDS | {"schema"})
        if unknown:
            raise ValueError(f"finish guide contains unsupported fields: {sorted(unknown)}")
        return cls(
            guide_id=str(raw["guide_id"]),
            finish_intent=str(raw["finish_intent"]),
            priorities=tuple(raw["priorities"]),
            preserve=tuple(raw["preserve"]),
            mark_policy=tuple(raw["mark_policy"]),
            value_policy=tuple(raw["value_policy"]),
            edge_policy=tuple(raw["edge_policy"]),
            omissions=tuple(raw["omissions"]),
            relations=tuple(FinishRelation.from_dict(item) for item in raw["relations"]),
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


def _relation(
    part: str,
    observations: Sequence[str],
    authoring_policy: Sequence[str],
    avoid: Sequence[str],
) -> FinishRelation:
    return FinishRelation(
        part=part,
        observations=tuple(observations),
        authoring_policy=tuple(authoring_policy),
        avoid=tuple(avoid),
    )


_FINISH_GUIDES = {
    "pose": FinishGuide(
        guide_id="finish-pose-v1",
        finish_intent="pose",
        priorities=(
            "gesture and line of action",
            "support, balance, and stance",
            "major masses, silhouette, and limb-chain relation",
            "ground contact and major prop relation",
        ),
        preserve=(
            "observed macro proportion and mass",
            "near/far overlap and contact",
            "economy of the pose statement",
        ),
        mark_policy=(
            "strengthen only marks that clarify force, balance, mass, or overlap",
            "retire duplicate construction when a selected contour carries the relation",
        ),
        value_policy=(
            "omit broad value unless it is required to separate a pose-defining mass",
            "never use tone to repair missing thickness, contact, or overlap",
        ),
        edge_policy=(
            "accent support, contact, and decisive silhouette changes selectively",
            "leave subordinate searching lines lighter than the pose statement",
        ),
        omissions=(
            "dense facial features",
            "surface texture and repeated micro-detail",
            "uniform contour confirmation",
        ),
        relations=(
            _relation(
                "whole_pose",
                ("dominant flow", "head/ribcage/pelvis relation", "support side"),
                ("carry the force through connected masses", "show the weight-bearing path"),
                ("isolated polished parts", "detail that hides a macro mismatch"),
            ),
            _relation(
                "limbs_and_ground",
                ("joint chains", "negative spaces", "foot direction and contact"),
                ("preserve curved centre paths and observed taper", "land the feet on one ground relation"),
                ("parallel tube limbs", "decorative footwear before contact reads"),
            ),
            _relation(
                "major_prop",
                ("axis", "width changes", "body contact and overlap"),
                ("include only the topology needed to explain pose",),
                ("floating prop detail", "a prop silhouette detached from the body"),
            ),
        ),
        completion_questions=(
            "Does the pose read at whole-image scale without dense detail?",
            "Do balance, limb relation, ground contact, and major prop contact agree?",
        ),
    ),
    "subject": FinishGuide(
        guide_id="finish-subject-v1",
        finish_intent="subject",
        priorities=(
            "all pose-level relationships",
            "identity-bearing spacing, direction, overlap, contact, topology, and termination",
            "selective distinctive garment and prop relations",
        ),
        preserve=(
            "macro pose, proportion, mass, and contact",
            "observed visibility and occlusion",
            "parent chains before terminal detail",
        ),
        mark_policy=(
            "add a detail only when it carries an observed identity relation",
            "name both sides of every contour and stop it at the observed termination",
            "vary repeated marks from the structure they terminate",
        ),
        value_policy=(
            "use value families only after line/tone-off form remains readable",
            "group identity-bearing value masses rather than darkening every local part",
        ),
        edge_policy=(
            "concentrate sharper or darker accents at identity-bearing relations",
            "soften or omit edges that do not separate named forms",
        ),
        omissions=(
            "feature inventory with no spacing or directional relation",
            "invented hidden anatomy or terminals",
            "uniform hair strands, folds, laces, or fingers",
        ),
        relations=(
            _relation(
                "face",
                ("eye spacing and direction", "nose–mouth–chin intervals", "cheek/jaw/hair occlusion"),
                ("anchor features to the turned facial centreline", "select accents by relational importance"),
                ("eyes, nose, and mouth placed as isolated symbols", "jaw continued beneath occluding hair"),
            ),
            _relation(
                "hair",
                ("outer envelope", "major groups", "termination direction", "face/neck/body overlap"),
                ("author grouped masses before selected strands", "let tips inherit direction and length from their group"),
                ("regular sawtooth tips", "uniform radiating strand rows"),
            ),
            _relation(
                "hands_and_feet",
                ("parent joint chain", "major mass", "contact", "visible, partial, or occluded termination"),
                ("draw only the visible terminal", "preserve contact ownership with pocket, ground, or prop"),
                ("invented fingers or toes", "terminal detail before the parent chain reads"),
            ),
            _relation(
                "clothing",
                ("garment mass", "openings", "compression and tension", "body overlap", "distinctive seams"),
                ("hang the garment from the underlying body chain", "preserve observed occupied envelope"),
                ("parallel contour duplication", "fold inventory detached from joints or contact"),
            ),
            _relation(
                "prop",
                ("topology", "width changes", "body contact", "overlap", "terminal mass", "distinctive parts"),
                ("keep topology continuous through occlusion", "accent distinctive parts only after contact reads"),
                ("floating component inventory", "generic prop axis with no occupied envelope"),
            ),
        ),
        completion_questions=(
            "Do identity-bearing relations survive whole-image review?",
            "Would the subject still read if non-relational micro-detail were removed?",
        ),
    ),
    "form_light": FinishGuide(
        guide_id="finish-form-light-v1",
        finish_intent="form_light",
        priorities=(
            "line/tone-off structural readability",
            "large light and shadow families",
            "value range, form turn, and edge hierarchy",
        ),
        preserve=(
            "major limb, torso, clothing, and prop volume before tone",
            "observed light direction and family membership",
            "compact authored region decisions",
        ),
        mark_policy=(
            "correct contour and overlap premises before adding value",
            "use form-directed cross-contour only where it clarifies turning volume",
        ),
        value_policy=(
            "author one calibrated region decision per observed value family",
            "reserve observed light inside a correct dark form instead of erasing it back out",
            "revise a disproved region rather than stacking another fill",
        ),
        edge_policy=(
            "sharpen selected cast/contact edges and focal turns",
            "soften edges where form turns or value families merge",
        ),
        omissions=(
            "arbitrary dark bands",
            "brute-force authored hatch microstrokes",
            "tone that manufactures missing geometry",
        ),
        relations=(
            _relation(
                "geometry_preflight",
                ("limb thickness", "torso/limb separation", "garment volume", "prop contact"),
                ("repair structure in a line-only state before tone",),
                ("using shadow to hide a missing boundary or contact",),
            ),
            _relation(
                "light_shadow_families",
                ("light direction", "connected shadow family", "reserved observed lights"),
                ("group broad regions by observed family", "keep value decisions compact"),
                ("local banding", "one-off opacity guessing inside the session"),
            ),
            _relation(
                "form_edges",
                ("form turn", "cast edge", "contact edge", "focal hierarchy"),
                ("vary edge treatment by observed cause",),
                ("equal edge sharpness everywhere",),
            ),
        ),
        completion_questions=(
            "Does the form remain valid with tone removed?",
            "Do large value families and edge changes describe one coherent light?",
        ),
    ),
    "expressive": FinishGuide(
        guide_id="finish-expressive-v1",
        finish_intent="expressive",
        priorities=(
            "declared composition and focal hierarchy",
            "shape rhythm, energy, and selective simplification",
            "style consistency under preserved constraints",
        ),
        preserve=(
            "explicit reference constraints",
            "required geometry, contact, and transformation intent",
            "one authoritative history and correction core",
        ),
        mark_policy=(
            "amplify marks that carry the declared focal rhythm or energy",
            "record what is deliberately simplified instead of silently dropping it",
        ),
        value_policy=(
            "use value to support focal hierarchy and shape rhythm",
            "do not let expressive contrast override preserved geometry or reference constraints",
        ),
        edge_policy=(
            "concentrate edge contrast at the focal relation",
            "simplify subordinate edges consistently with the declared intent",
        ),
        omissions=(
            "unselected detail",
            "uniform emphasis",
            "style effects that rewrite subject geometry",
        ),
        relations=(
            _relation(
                "preserved_constraints",
                ("required geometry", "reference contacts", "declared transformation limits"),
                ("record and retain constraints before simplifying",),
                ("silent sacrifice of required structure",),
            ),
            _relation(
                "composition_and_focal",
                ("dominant shape", "focal relation", "supporting hierarchy"),
                ("allocate strongest marks and contrast to the focal relation",),
                ("equal emphasis across the canvas",),
            ),
            _relation(
                "rhythm_and_simplification",
                ("shape repetition and variation", "directional energy", "selected omissions"),
                ("simplify by a declared rule", "keep variation tied to parent structure"),
                ("accidental uniformity", "post-filter style substitution"),
            ),
        ),
        completion_questions=(
            "Do composition, focal hierarchy, rhythm, and energy match the declared intent?",
            "Are every required geometry and reference constraint still explicit and intact?",
        ),
    ),
}


def resolve_mode_guide(drawing_mode: str) -> ModeGuide:
    mode = _axis(drawing_mode, "drawing_mode", DRAWING_MODES)
    return _MODE_GUIDES[mode]


def resolve_finish_guide(finish_intent: str) -> FinishGuide:
    """Return immutable authoring guidance for one finish intent."""

    intent = _axis(finish_intent, "finish_intent", FINISH_INTENTS)
    return _FINISH_GUIDES[intent]


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
    "FINISH_GUIDE_SCHEMA",
    "FINISH_RELATION_SCHEMA",
    "INTENT_SCHEMA",
    "IntentChangeRecord",
    "IntentProvenance",
    "DrawingIntent",
    "FinishGuide",
    "FinishRelation",
    "ModeGuide",
    "REFERENCE_MODES",
    "STYLE_PROFILES",
    "STYLE_GUIDE_SCHEMA",
    "MODE_GUIDE_SCHEMA",
    "StyleGuide",
    "compatibility_intent",
    "resolve_mode_guide",
    "resolve_finish_guide",
    "resolve_style_guide",
]
