"""Agent-authored observation and initial figure construction.

This module deliberately stays small.  It gives a worker a vocabulary for
making the first whole figure readable, while ``DrawingSession`` remains the
single history/checkpoint authority and ``DrawingSession.inspect`` remains the
single inspection implementation.

The phase names here describe drawing intent, not runtime state.  A worker may
correct an earlier mark after inspection; B06 will add correction policy on
top of this initial construction surface.
"""

from __future__ import annotations

import math
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from ..core.session import sha256_obj
from ..inspection import GroundGuide, Grid, PlumbLine, ROI, Registration
from .session import DrawingSession


CONSTRUCTION_PHASES = (
    "line_of_action",
    "mass_blocking",
    "balance_plumb",
    "joints_limbs",
)


def _text(value: Any, field: str, *, required: bool = True) -> str:
    result = str(value or "").strip()
    if required and not result:
        raise ValueError(f"{field} must be non-empty")
    return result


def _text_tuple(values: Sequence[Any], field: str) -> tuple[str, ...]:
    result = tuple(_text(value, field) for value in values)
    return result


def _points(values: Sequence[Sequence[float]]) -> tuple[tuple[float, float], ...]:
    if len(values) < 2:
        raise ValueError("construction mark requires at least two points")
    result: list[tuple[float, float]] = []
    for value in values:
        if len(value) != 2:
            raise ValueError("construction points require x,y")
        point = (float(value[0]), float(value[1]))
        if not all(math.isfinite(item) for item in point):
            raise ValueError("construction point coordinates must be finite")
        result.append(point)
    return tuple(result)


@dataclass(frozen=True)
class PoseObservation:
    """A concise, agent-authored read of the subject before drawing."""

    support_side: str
    flow: str
    head_ribcage_pelvis: str
    shoulder_pelvis: str
    silhouette_keys: tuple[str, ...] = ()
    negative_spaces: tuple[str, ...] = ()
    ground_relation: str = ""
    major_prop_axis: str | None = None
    occluded_limb_evidence: tuple[str, ...] = ()
    uncertain: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "support_side", _text(self.support_side, "support_side"))
        object.__setattr__(self, "flow", _text(self.flow, "flow"))
        object.__setattr__(
            self,
            "head_ribcage_pelvis",
            _text(self.head_ribcage_pelvis, "head_ribcage_pelvis"),
        )
        object.__setattr__(self, "shoulder_pelvis", _text(self.shoulder_pelvis, "shoulder_pelvis"))
        object.__setattr__(self, "silhouette_keys", _text_tuple(self.silhouette_keys, "silhouette_keys"))
        object.__setattr__(self, "negative_spaces", _text_tuple(self.negative_spaces, "negative_spaces"))
        object.__setattr__(self, "occluded_limb_evidence", _text_tuple(self.occluded_limb_evidence, "occluded_limb_evidence"))
        object.__setattr__(self, "uncertain", _text_tuple(self.uncertain, "uncertain"))
        object.__setattr__(self, "ground_relation", _text(self.ground_relation, "ground_relation", required=False))
        if self.major_prop_axis is not None:
            object.__setattr__(self, "major_prop_axis", _text(self.major_prop_axis, "major_prop_axis"))

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "PoseObservation":
        return cls(
            support_side=payload.get("support_side", ""),
            flow=payload.get("flow", ""),
            head_ribcage_pelvis=payload.get("head_ribcage_pelvis", ""),
            shoulder_pelvis=payload.get("shoulder_pelvis", ""),
            silhouette_keys=tuple(payload.get("silhouette_keys", ())),
            negative_spaces=tuple(payload.get("negative_spaces", ())),
            ground_relation=payload.get("ground_relation", ""),
            major_prop_axis=payload.get("major_prop_axis"),
            occluded_limb_evidence=tuple(payload.get("occluded_limb_evidence", ())),
            uncertain=tuple(payload.get("uncertain", ())),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "format": "pose-observation/v1",
            "support_side": self.support_side,
            "flow": self.flow,
            "head_ribcage_pelvis": self.head_ribcage_pelvis,
            "shoulder_pelvis": self.shoulder_pelvis,
            "silhouette_keys": list(self.silhouette_keys),
            "negative_spaces": list(self.negative_spaces),
            "ground_relation": self.ground_relation,
            "major_prop_axis": self.major_prop_axis,
            "occluded_limb_evidence": list(self.occluded_limb_evidence),
            "uncertain": list(self.uncertain),
        }


@dataclass(frozen=True)
class ConstructionMark:
    """One explicit mark in the initial construction, in subject coordinates."""

    mark_id: str
    phase: str
    role: str
    part: str
    points: tuple[tuple[float, float], ...]
    confidence: float = 1.0
    layer: int = 0
    pressure: tuple[float, ...] | None = None
    tool: str | Mapping[str, Any] = "construction_pencil"
    grade: str | None = None
    tool_overrides: Mapping[str, Any] | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "mark_id", _text(self.mark_id, "mark_id"))
        phase = _text(self.phase, "phase")
        if phase not in CONSTRUCTION_PHASES:
            raise ValueError(f"unknown construction phase: {phase}")
        object.__setattr__(self, "phase", phase)
        object.__setattr__(self, "role", _text(self.role, "role"))
        object.__setattr__(self, "part", _text(self.part, "part"))
        object.__setattr__(self, "points", _points(self.points))
        confidence = float(self.confidence)
        if not 0.0 <= confidence <= 1.0:
            raise ValueError("construction confidence must be in [0,1]")
        object.__setattr__(self, "confidence", confidence)
        object.__setattr__(self, "layer", int(self.layer))
        if self.pressure is not None:
            pressure = tuple(float(value) for value in self.pressure)
            if len(pressure) != len(self.points):
                raise ValueError("construction pressure count must match points")
            if any(not 0.0 <= value <= 1.0 for value in pressure):
                raise ValueError("construction pressure values must be in [0,1]")
            object.__setattr__(self, "pressure", pressure)
        if isinstance(self.tool, Mapping):
            tool = deepcopy(dict(self.tool))
            if not str(tool.get("preset", "")).strip():
                raise ValueError("construction tool mapping requires a preset")
            object.__setattr__(self, "tool", tool)
        else:
            object.__setattr__(self, "tool", _text(self.tool, "tool"))
        if self.grade is not None:
            object.__setattr__(self, "grade", _text(self.grade, "grade"))
        if self.tool_overrides is not None:
            object.__setattr__(self, "tool_overrides", deepcopy(dict(self.tool_overrides)))

    def to_draw_spec(self, registration: Registration) -> dict[str, Any]:
        """Return stage-free ``DrawingSession.draw_many`` input."""

        return {
            "action_id": self.mark_id,
            "stroke_id": self.mark_id,
            "role": self.role,
            "part": self.part,
            "points": [registration.map_subject_to_canvas(point) for point in self.points],
            "confidence": self.confidence,
            "layer": self.layer,
            "pressure": None if self.pressure is None else list(self.pressure),
            "tool": deepcopy(self.tool),
            "grade": self.grade,
            "tool_overrides": None if self.tool_overrides is None else deepcopy(dict(self.tool_overrides)),
        }


@dataclass(frozen=True)
class InitialConstruct:
    """The authored initial whole-figure hypothesis supplied by the Agent."""

    observation: PoseObservation
    marks: tuple[ConstructionMark, ...]
    plumb: PlumbLine | None = None
    ground: GroundGuide | None = None
    rois: tuple[ROI, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.observation, PoseObservation):
            raise TypeError("initial construct requires a PoseObservation")
        marks = tuple(self.marks)
        if not marks:
            raise ValueError("initial construct requires at least one construction mark")
        if any(not isinstance(mark, ConstructionMark) for mark in marks):
            raise TypeError("initial construct marks must be ConstructionMark values")
        ids = [mark.mark_id for mark in marks]
        if len(set(ids)) != len(ids):
            raise ValueError("construction mark IDs must be unique")
        object.__setattr__(self, "marks", marks)
        object.__setattr__(self, "rois", tuple(self.rois))

    @property
    def guides(self) -> tuple[PlumbLine | GroundGuide, ...]:
        return tuple(guide for guide in (self.plumb, self.ground) if guide is not None)

    def to_dict(self) -> dict[str, Any]:
        return {
            "format": "initial-construct/v1",
            "observation": self.observation.to_dict(),
            "marks": [
                {
                    "mark_id": mark.mark_id,
                    "phase": mark.phase,
                    "role": mark.role,
                    "part": mark.part,
                    "points": [list(point) for point in mark.points],
                    "confidence": mark.confidence,
                    "layer": mark.layer,
                }
                for mark in self.marks
            ],
            "guides": [guide.to_dict() for guide in self.guides],
            "rois": [roi.to_dict() for roi in self.rois],
        }


@dataclass(frozen=True)
class InitialConstructResult:
    observation_id: str
    action_ids: tuple[str, ...]


def _registration_for(session: DrawingSession, registration: Registration | None) -> Registration:
    if registration is None:
        return Registration.identity((session.width, session.height))
    if registration.canvas_size != (session.width, session.height):
        raise ValueError(
            f"registration canvas {registration.canvas_size} does not match session {(session.width, session.height)}"
        )
    return registration


def observe_pose(
    session: DrawingSession,
    observation: PoseObservation,
    *,
    observation_id: str | None = None,
) -> str:
    """Record the short whole-pose read before any initial marks."""

    if not isinstance(observation, PoseObservation):
        raise TypeError("observe_pose requires a PoseObservation")
    return session.observe(observation.to_dict(), observation_id=observation_id)


def author_initial_construct(
    session: DrawingSession,
    construct: InitialConstruct,
    *,
    observation_id: str | None = None,
    registration: Registration | None = None,
    source_observation: str | None = None,
) -> InitialConstructResult:
    """Observe, then commit the authored mark tuple as one drawing batch."""

    if not isinstance(construct, InitialConstruct):
        raise TypeError("author_initial_construct requires an InitialConstruct")
    registration = _registration_for(session, registration)
    if observation_id is None:
        observation_id = observe_pose(session, construct.observation)
    else:
        matching = [
            record
            for record in session.observation_history
            if record.get("observation_id") == str(observation_id)
        ]
        if not matching:
            raise ValueError(f"unknown observation_id: {observation_id}")
        expected_digest = matching[0].get("digest")
        if expected_digest != sha256_obj(construct.observation.to_dict()):
            raise ValueError(f"observation_id does not match construct observation: {observation_id}")
    source = source_observation or "agent-authored whole-pose construction"
    action_ids = tuple(
        str(action_id)
        for action_id in session.draw_many(
            [mark.to_draw_spec(registration) for mark in construct.marks],
            observation_id=observation_id,
            source_observation=source,
        )
    )
    return InitialConstructResult(observation_id=observation_id, action_ids=action_ids)


def inspect_initial_construct(
    session: DrawingSession,
    construct: InitialConstruct,
    *,
    registration: Registration | None = None,
    rois: Sequence[ROI] | None = None,
    grid: Grid | None = None,
    out_dir: str | Path | None = None,
    supersample: int = 3,
):
    """Use the existing inspection path for the first whole-figure comparison."""

    if not isinstance(construct, InitialConstruct):
        raise TypeError("inspect_initial_construct requires an InitialConstruct")
    registration = _registration_for(session, registration)
    selected_rois = construct.rois if rois is None else tuple(rois)
    if construct.guides or grid is not None:
        mode = "deep"
        escalation_reason = (
            "initial construct includes authored balance guides for uncertainty review"
            if construct.guides
            else "initial construct requests a balance grid for uncertainty review"
        )
    elif selected_rois:
        mode = "focused"
        escalation_reason = None
    else:
        mode = "quick"
        escalation_reason = None
    return session.inspect(
        registration=registration,
        rois=selected_rois,
        grid=grid,
        guides=construct.guides,
        out_dir=out_dir,
        supersample=int(supersample),
        mode=mode,
        escalation_reason=escalation_reason,
    )


__all__ = [
    "CONSTRUCTION_PHASES",
    "ConstructionMark",
    "InitialConstruct",
    "InitialConstructResult",
    "PoseObservation",
    "author_initial_construct",
    "inspect_initial_construct",
    "observe_pose",
]
