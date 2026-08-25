from __future__ import annotations
from copy import deepcopy
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping


_BODY_VIEWS = frozenset({
    "front", "back", "side", "three_quarter", "back_three_quarter",
    "front_three_quarter", "unknown",
})
_TORSO_TURNS = frozenset({"left", "right", "none", "unknown"})
_SIDE_ROLES = frozenset({
    "subject_left", "subject_right", "image_left", "image_right", "unknown",
})
_ARM_VISIBILITY = frozenset({"visible", "partial", "occluded", "unknown"})
_ARM_KEYS = frozenset({"subject_left", "subject_right"})


@dataclass(frozen=True)
class ViewObservation:
    """Typed pre-draw view facts used to anchor later visual evidence.

    This is still agent-authored observation, not automatic pose inference.  The
    immutable mappings prevent a caller from mutating a locked view through a
    shared input dictionary.
    """

    body_view: str = "unknown"
    torso_turn: str = "unknown"
    near_side: str = "unknown"
    arm_visibility: Mapping[str, str] = field(default_factory=dict)
    arm_occlusion: Mapping[str, tuple[str, ...]] = field(default_factory=dict)
    prop_overlap_order: tuple[str, ...] = ()
    uncertainties: tuple[str, ...] = ()

    def __post_init__(self):
        body_view = str(self.body_view)
        torso_turn = str(self.torso_turn)
        near_side = str(self.near_side)
        if body_view not in _BODY_VIEWS:
            raise ValueError(f"body_view must be one of {sorted(_BODY_VIEWS)}")
        if torso_turn not in _TORSO_TURNS:
            raise ValueError(f"torso_turn must be one of {sorted(_TORSO_TURNS)}")
        if near_side not in _SIDE_ROLES:
            raise ValueError(f"near_side must be one of {sorted(_SIDE_ROLES)}")

        visibility = {str(k): str(v) for k, v in dict(self.arm_visibility).items()}
        unknown_visibility = set(visibility) - _ARM_KEYS
        if unknown_visibility:
            raise ValueError(f"unknown arm_visibility key(s): {sorted(unknown_visibility)}")
        invalid_visibility = set(visibility.values()) - _ARM_VISIBILITY
        if invalid_visibility:
            raise ValueError(
                f"arm_visibility values must be one of {sorted(_ARM_VISIBILITY)}"
            )

        occlusion = {
            str(k): tuple(str(item) for item in values)
            for k, values in dict(self.arm_occlusion).items()
        }
        unknown_occlusion = set(occlusion) - _ARM_KEYS
        if unknown_occlusion:
            raise ValueError(f"unknown arm_occlusion key(s): {sorted(unknown_occlusion)}")

        object.__setattr__(self, "body_view", body_view)
        object.__setattr__(self, "torso_turn", torso_turn)
        object.__setattr__(self, "near_side", near_side)
        object.__setattr__(self, "arm_visibility", MappingProxyType(visibility))
        object.__setattr__(self, "arm_occlusion", MappingProxyType(occlusion))
        object.__setattr__(self, "prop_overlap_order", tuple(map(str, self.prop_overlap_order)))
        object.__setattr__(self, "uncertainties", tuple(map(str, self.uncertainties)))

    def to_dict(self) -> dict[str, Any]:
        return {
            "body_view": self.body_view,
            "torso_turn": self.torso_turn,
            "near_side": self.near_side,
            "arm_visibility": dict(self.arm_visibility),
            "arm_occlusion": {
                key: list(value) for key, value in self.arm_occlusion.items()
            },
            "prop_overlap_order": list(self.prop_overlap_order),
            "uncertainties": list(self.uncertainties),
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "ViewObservation":
        return cls(
            body_view=str(data.get("body_view", "unknown")),
            torso_turn=str(data.get("torso_turn", "unknown")),
            near_side=str(data.get("near_side", "unknown")),
            arm_visibility=dict(data.get("arm_visibility") or {}),
            arm_occlusion={
                str(key): tuple(map(str, value))
                for key, value in (data.get("arm_occlusion") or {}).items()
            },
            prop_overlap_order=tuple(map(str, data.get("prop_overlap_order", ()))),
            uncertainties=tuple(map(str, data.get("uncertainties", ()))),
        )

@dataclass(frozen=True)
class ObservationContract:
    """Agent-authored semantic memory.

    The runtime validates shape only. It never infers pose, anatomy, or correctness.
    """
    subject_summary: str
    global_relations: dict[str, Any] = field(default_factory=dict)
    parts: dict[str, Any] = field(default_factory=dict)
    uncertainties: tuple[str, ...] = ()
    drawing_priorities: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()
    view: ViewObservation | None = None

    def __post_init__(self):
        if not self.subject_summary.strip():
            raise ValueError("subject_summary must be non-empty")
        if not isinstance(self.global_relations, dict):
            raise TypeError("global_relations must be a dict")
        if not isinstance(self.parts, dict):
            raise TypeError("parts must be a dict")
        if self.view is not None and not isinstance(self.view, ViewObservation):
            raise TypeError("view must be a ViewObservation or None")

    def to_dict(self) -> dict[str, Any]:
        data = {
            "schema": "img2drawing.observation.v3" if self.view is not None else "img2drawing.observation.v2",
            "semantic_authority": "agent",
            "automatic_semantic_inference": False,
            "subject_summary": self.subject_summary,
            "global_relations": deepcopy(self.global_relations),
            "parts": deepcopy(self.parts),
            "uncertainties": list(self.uncertainties),
            "drawing_priorities": list(self.drawing_priorities),
            "evidence_refs": list(self.evidence_refs),
        }
        if self.view is not None:
            data["view"] = self.view.to_dict()
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ObservationContract":
        return cls(
            subject_summary=str(data["subject_summary"]),
            global_relations=deepcopy(data.get("global_relations", {})),
            parts=deepcopy(data.get("parts", {})),
            uncertainties=tuple(map(str, data.get("uncertainties", ()))),
            drawing_priorities=tuple(map(str, data.get("drawing_priorities", ()))),
            evidence_refs=tuple(map(str, data.get("evidence_refs", ()))),
            view=None if data.get("view") is None else ViewObservation.from_dict(data["view"]),
        )
