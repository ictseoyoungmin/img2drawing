from __future__ import annotations

"""Generic attached-prop topology evidence for tools, weapons, bags, and instruments."""

from dataclasses import dataclass
import math
import re
from typing import Any, Mapping, Sequence


Point = tuple[float, float]
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def _point(value: Sequence[float], label: str) -> Point:
    if len(value) != 2:
        raise ValueError(f"{label} requires x,y")
    point = tuple(map(float, value))
    if not all(0.0 <= item <= 1.0 for item in point):
        raise ValueError(f"{label} must lie inside normalized canvas")
    return point  # type: ignore[return-value]


def _digest(value: str, label: str) -> str:
    value = str(value).lower()
    if not _SHA256.fullmatch(value):
        raise ValueError(f"{label} must be a 64-character lowercase hex digest")
    return value


@dataclass(frozen=True)
class PropWidthChangePoint:
    t: float
    width: float
    label: str = ""

    def __post_init__(self) -> None:
        t = float(self.t)
        width = float(self.width)
        if not 0.0 <= t <= 1.0 or width <= 0.0:
            raise ValueError("prop width-change point requires t in [0,1] and width > 0")
        object.__setattr__(self, "t", t)
        object.__setattr__(self, "width", width)
        object.__setattr__(self, "label", str(self.label))

    def to_dict(self) -> dict[str, Any]:
        return {"t": self.t, "width": self.width, "label": self.label}

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "PropWidthChangePoint":
        return cls(float(raw["t"]), float(raw["width"]), str(raw.get("label", "")))


@dataclass(frozen=True)
class PropTerminalMass:
    label: str
    center: Point
    radius: float

    def __post_init__(self) -> None:
        label = str(self.label).strip()
        if not label:
            raise ValueError("terminal mass label must be non-empty")
        radius = float(self.radius)
        if radius <= 0.0:
            raise ValueError("terminal mass radius must be > 0")
        object.__setattr__(self, "label", label)
        object.__setattr__(self, "center", _point(self.center, "terminal mass center"))
        object.__setattr__(self, "radius", radius)

    def to_dict(self) -> dict[str, Any]:
        return {"label": self.label, "center": list(self.center), "radius": self.radius}

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "PropTerminalMass":
        return cls(str(raw["label"]), tuple(raw["center"]), float(raw["radius"]))


@dataclass(frozen=True)
class PropBodyOverlapPoint:
    label: str
    point: Point
    body_region: str
    occlusion_order: int

    def __post_init__(self) -> None:
        label = str(self.label).strip()
        body = str(self.body_region).strip()
        if not label or not body:
            raise ValueError("prop overlap point requires label and body_region")
        if int(self.occlusion_order) < 0:
            raise ValueError("occlusion_order must be >= 0")
        object.__setattr__(self, "label", label)
        object.__setattr__(self, "point", _point(self.point, "prop overlap point"))
        object.__setattr__(self, "body_region", body)
        object.__setattr__(self, "occlusion_order", int(self.occlusion_order))

    def to_dict(self) -> dict[str, Any]:
        return {"label": self.label, "point": list(self.point), "body_region": self.body_region, "occlusion_order": self.occlusion_order}

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "PropBodyOverlapPoint":
        return cls(str(raw["label"]), tuple(raw["point"]), str(raw["body_region"]), int(raw["occlusion_order"]))


@dataclass(frozen=True)
class PropTopologyObservation:
    prop_id: str
    major_axis_start: Point
    major_axis_end: Point
    width_change_points: tuple[PropWidthChangePoint, ...]
    terminal_masses: tuple[PropTerminalMass, ...]
    body_overlap_points: tuple[PropBodyOverlapPoint, ...]
    visible_interruptions: tuple[str, ...]
    occlusion_order: tuple[str, ...]
    source_surface: str
    observation_id: str
    source_artifact_sha256: str
    observation_lock_digest: str
    source_state_sha256: str | None = None

    def __post_init__(self) -> None:
        prop_id = str(self.prop_id).strip()
        if not prop_id:
            raise ValueError("prop_id must be non-empty")
        axis_start = _point(self.major_axis_start, "major_axis_start")
        axis_end = _point(self.major_axis_end, "major_axis_end")
        if math.dist(axis_start, axis_end) <= 1e-9:
            raise ValueError("major axis must have positive length")
        points = tuple(item if isinstance(item, PropWidthChangePoint) else PropWidthChangePoint.from_dict(item) for item in self.width_change_points)
        if not 1 <= len(points) <= 16:
            raise ValueError("width_change_points must contain 1..16 entries")
        previous = -1.0
        for item in points:
            if item.t <= previous:
                raise ValueError("width-change t values must be strictly increasing")
            previous = item.t
        terminals = tuple(item if isinstance(item, PropTerminalMass) else PropTerminalMass.from_dict(item) for item in self.terminal_masses)
        overlaps = tuple(item if isinstance(item, PropBodyOverlapPoint) else PropBodyOverlapPoint.from_dict(item) for item in self.body_overlap_points)
        surface = str(self.source_surface)
        if surface not in {"reference", "drawing"}:
            raise ValueError("source_surface must be reference or drawing")
        state = None if self.source_state_sha256 is None else _digest(self.source_state_sha256, "source_state_sha256")
        if surface == "drawing" and state is None:
            raise ValueError("drawing prop evidence requires source_state_sha256")
        object.__setattr__(self, "prop_id", prop_id)
        object.__setattr__(self, "major_axis_start", axis_start)
        object.__setattr__(self, "major_axis_end", axis_end)
        object.__setattr__(self, "width_change_points", points)
        object.__setattr__(self, "terminal_masses", terminals)
        object.__setattr__(self, "body_overlap_points", overlaps)
        object.__setattr__(self, "visible_interruptions", tuple(map(str, self.visible_interruptions)))
        object.__setattr__(self, "occlusion_order", tuple(map(str, self.occlusion_order)))
        object.__setattr__(self, "source_surface", surface)
        object.__setattr__(self, "observation_id", str(self.observation_id).strip())
        if not self.observation_id:
            raise ValueError("observation_id must be non-empty")
        object.__setattr__(self, "source_artifact_sha256", _digest(self.source_artifact_sha256, "source_artifact_sha256"))
        object.__setattr__(self, "observation_lock_digest", _digest(self.observation_lock_digest, "observation_lock_digest"))
        object.__setattr__(self, "source_state_sha256", state)

    @property
    def major_axis_length(self) -> float:
        return math.dist(self.major_axis_start, self.major_axis_end)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "img2drawing.prop_topology.v1",
            "prop_id": self.prop_id,
            "major_axis_start": list(self.major_axis_start),
            "major_axis_end": list(self.major_axis_end),
            "width_change_points": [item.to_dict() for item in self.width_change_points],
            "terminal_masses": [item.to_dict() for item in self.terminal_masses],
            "body_overlap_points": [item.to_dict() for item in self.body_overlap_points],
            "visible_interruptions": list(self.visible_interruptions),
            "occlusion_order": list(self.occlusion_order),
            "source_surface": self.source_surface,
            "observation_id": self.observation_id,
            "source_artifact_sha256": self.source_artifact_sha256,
            "observation_lock_digest": self.observation_lock_digest,
            "source_state_sha256": self.source_state_sha256,
        }

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "PropTopologyObservation":
        if raw.get("schema") not in (None, "img2drawing.prop_topology.v1"):
            raise ValueError(f"unsupported prop topology schema: {raw.get('schema')!r}")
        return cls(
            prop_id=str(raw["prop_id"]),
            major_axis_start=tuple(raw["major_axis_start"]),
            major_axis_end=tuple(raw["major_axis_end"]),
            width_change_points=tuple(PropWidthChangePoint.from_dict(item) for item in raw["width_change_points"]),
            terminal_masses=tuple(PropTerminalMass.from_dict(item) for item in raw.get("terminal_masses", ())),
            body_overlap_points=tuple(PropBodyOverlapPoint.from_dict(item) for item in raw.get("body_overlap_points", ())),
            visible_interruptions=tuple(map(str, raw.get("visible_interruptions", ()))),
            occlusion_order=tuple(map(str, raw.get("occlusion_order", ()))),
            source_surface=str(raw["source_surface"]),
            observation_id=str(raw["observation_id"]),
            source_artifact_sha256=str(raw["source_artifact_sha256"]),
            observation_lock_digest=str(raw["observation_lock_digest"]),
            source_state_sha256=raw.get("source_state_sha256"),
        )


class PropTopologyIntegrityError(ValueError):
    pass


@dataclass(frozen=True)
class PropTopologyComparison:
    axis_start_delta: float
    axis_end_delta: float
    width_deltas: tuple[float, ...]
    terminal_mass_count_delta: int
    overlap_point_deltas: tuple[float, ...]
    visible_interruptions_changed: bool
    occlusion_order_changed: bool
    integrity: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "img2drawing.prop_topology_comparison.v1",
            "authority": "evidence_not_pass_fail",
            "axis_start_delta": self.axis_start_delta,
            "axis_end_delta": self.axis_end_delta,
            "width_deltas": list(self.width_deltas),
            "terminal_mass_count_delta": self.terminal_mass_count_delta,
            "overlap_point_deltas": list(self.overlap_point_deltas),
            "visible_interruptions_changed": self.visible_interruptions_changed,
            "occlusion_order_changed": self.occlusion_order_changed,
            "integrity": dict(self.integrity),
        }


def compare_prop_topology(
    reference: PropTopologyObservation,
    drawing: PropTopologyObservation,
    *,
    current_drawing_state_sha256: str | None = None,
    require_independent: bool = True,
) -> PropTopologyComparison:
    reference = reference if isinstance(reference, PropTopologyObservation) else PropTopologyObservation.from_dict(reference)
    drawing = drawing if isinstance(drawing, PropTopologyObservation) else PropTopologyObservation.from_dict(drawing)
    errors: list[str] = []
    warnings: list[str] = []
    if reference.source_surface != "reference" or drawing.source_surface != "drawing":
        errors.append("prop topology observations must use reference and drawing surfaces")
    if reference.prop_id != drawing.prop_id:
        errors.append("reference and drawing prop_id must match for topology comparison")
    distinct_ids = reference.observation_id != drawing.observation_id
    distinct_artifacts = reference.source_artifact_sha256 != drawing.source_artifact_sha256
    lock_match = reference.observation_lock_digest == drawing.observation_lock_digest
    if not distinct_ids:
        errors.append("prop topology observations must use distinct observation_id values")
    if not distinct_artifacts:
        errors.append("prop topology observations must use distinct source artifacts")
    if not lock_match:
        errors.append("prop topology observations must share the frozen observation lock digest")
    if len(reference.width_change_points) != len(drawing.width_change_points):
        errors.append("prop topology observations must use matching width-change station counts")
    state_current: bool | None = None
    if current_drawing_state_sha256 is None:
        warnings.append("current drawing state was not supplied; staleness could not be checked")
    else:
        state_current = drawing.source_state_sha256 == _digest(current_drawing_state_sha256, "current_drawing_state_sha256")
        if not state_current:
            errors.append("drawing prop topology evidence is stale for the current drawing state")
    if require_independent and errors:
        raise PropTopologyIntegrityError("; ".join(errors))
    width_deltas = tuple(
        drawing.width_change_points[i].width - reference.width_change_points[i].width
        for i in range(min(len(reference.width_change_points), len(drawing.width_change_points)))
    )
    overlap_deltas = tuple(
        math.dist(drawing.body_overlap_points[i].point, reference.body_overlap_points[i].point)
        for i in range(min(len(reference.body_overlap_points), len(drawing.body_overlap_points)))
    )
    return PropTopologyComparison(
        axis_start_delta=math.dist(reference.major_axis_start, drawing.major_axis_start),
        axis_end_delta=math.dist(reference.major_axis_end, drawing.major_axis_end),
        width_deltas=width_deltas,
        terminal_mass_count_delta=len(drawing.terminal_masses) - len(reference.terminal_masses),
        overlap_point_deltas=overlap_deltas,
        visible_interruptions_changed=reference.visible_interruptions != drawing.visible_interruptions,
        occlusion_order_changed=reference.occlusion_order != drawing.occlusion_order,
        integrity={
            "valid": not errors,
            "errors": errors,
            "warnings": warnings,
            "distinct_observation_ids": distinct_ids,
            "distinct_source_artifacts": distinct_artifacts,
            "lock_digest_matches": lock_match,
            "drawing_state_current": state_current,
        },
    )


__all__ = [
    "PropWidthChangePoint", "PropTerminalMass", "PropBodyOverlapPoint",
    "PropTopologyObservation", "PropTopologyIntegrityError",
    "PropTopologyComparison", "compare_prop_topology",
]
