from __future__ import annotations

"""Agent-authored region envelope evidence.

The module deliberately compares geometry without deciding whether a drawing is
artistically acceptable.  A region evaluator supplies an axis and paired contour
samples for each surface; this module validates provenance and reports measurable
differences such as arm width and visible-fraction drift.
"""

from dataclasses import dataclass
import math
import re
from typing import Any, Mapping, Sequence


Point = tuple[float, float]
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_SURFACES = frozenset({"reference", "drawing"})
_SIDE_ROLES = frozenset({"near", "far", "unknown"})
_VISIBILITY = frozenset({"visible", "partial", "occluded", "unknown"})
_MAX_STATIONS = 16


def _point(value: Sequence[float], *, label: str) -> Point:
    if len(value) != 2:
        raise ValueError(f"{label} requires x,y")
    x, y = map(float, value)
    if not (0.0 <= x <= 1.0 and 0.0 <= y <= 1.0):
        raise ValueError(f"{label} must lie inside normalized canvas [0,1]")
    return x, y


def _sha256(value: str, *, label: str) -> str:
    digest = str(value).lower()
    if not _SHA256.fullmatch(digest):
        raise ValueError(f"{label} must be a 64-character lowercase hex digest")
    return digest


def _distance(a: Point, b: Point) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


@dataclass(frozen=True)
class EnvelopeStation:
    """One normalized cross-section along a region axis.

    ``contour_a`` and ``contour_b`` are intentionally not called left/right:
    the evaluator may be observing a turned body, and the pair is a geometric
    width evidence rather than a semantic side claim.
    """

    t: float
    contour_a: Point
    contour_b: Point
    visibility: str = "visible"
    occlusion: tuple[str, ...] = ()
    uncertainty_radius: float = 0.0

    def __post_init__(self) -> None:
        t = float(self.t)
        if not 0.0 <= t <= 1.0:
            raise ValueError("station t must be in [0,1]")
        a = _point(self.contour_a, label="contour_a")
        b = _point(self.contour_b, label="contour_b")
        if _distance(a, b) <= 1e-9:
            raise ValueError("station contour pair must have positive width")
        visibility = str(self.visibility)
        if visibility not in _VISIBILITY:
            raise ValueError(f"visibility must be one of {sorted(_VISIBILITY)}")
        uncertainty = float(self.uncertainty_radius)
        if not 0.0 <= uncertainty <= 1.0:
            raise ValueError("uncertainty_radius must be in [0,1]")
        object.__setattr__(self, "t", t)
        object.__setattr__(self, "contour_a", a)
        object.__setattr__(self, "contour_b", b)
        object.__setattr__(self, "visibility", visibility)
        object.__setattr__(self, "occlusion", tuple(map(str, self.occlusion)))
        object.__setattr__(self, "uncertainty_radius", uncertainty)

    @property
    def width_canvas(self) -> float:
        return _distance(self.contour_a, self.contour_b)

    def width_local_axis(self, axis_length: float) -> float:
        if float(axis_length) <= 0.0:
            raise ValueError("axis length must be positive")
        return self.width_canvas / float(axis_length)

    def to_dict(self) -> dict[str, Any]:
        return {
            "t": self.t,
            "contour_a": list(self.contour_a),
            "contour_b": list(self.contour_b),
            "visibility": self.visibility,
            "occlusion": list(self.occlusion),
            "uncertainty_radius": self.uncertainty_radius,
        }

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "EnvelopeStation":
        return cls(
            t=float(raw["t"]),
            contour_a=tuple(raw["contour_a"]),
            contour_b=tuple(raw["contour_b"]),
            visibility=str(raw.get("visibility", "visible")),
            occlusion=tuple(map(str, raw.get("occlusion", ()))),
            uncertainty_radius=float(raw.get("uncertainty_radius", 0.0)),
        )


@dataclass(frozen=True)
class RegionEnvelopeObservation:
    """Independent region evidence from one concrete source surface."""

    region_id: str
    side_role: str
    axis_start: Point
    axis_end: Point
    stations: tuple[EnvelopeStation, ...]
    visible_fraction: float
    occlusion: tuple[str, ...]
    source_surface: str
    observation_id: str
    source_artifact_sha256: str
    observation_lock_digest: str
    source_state_sha256: str | None = None
    subject_height: float | None = None

    def __post_init__(self) -> None:
        region_id = str(self.region_id).strip()
        if not region_id:
            raise ValueError("region_id must be non-empty")
        side_role = str(self.side_role)
        if side_role not in _SIDE_ROLES:
            raise ValueError(f"side_role must be one of {sorted(_SIDE_ROLES)}")
        start = _point(self.axis_start, label="axis_start")
        end = _point(self.axis_end, label="axis_end")
        axis_length = _distance(start, end)
        if axis_length <= 1e-9:
            raise ValueError("region axis must have positive length")
        stations = tuple(
            item if isinstance(item, EnvelopeStation) else EnvelopeStation.from_dict(item)
            for item in self.stations
        )
        if not 2 <= len(stations) <= _MAX_STATIONS:
            raise ValueError(f"stations must contain 2..{_MAX_STATIONS} entries")
        previous_t = -1.0
        for item in stations:
            if item.t <= previous_t:
                raise ValueError("station t values must be strictly increasing")
            previous_t = item.t
        visible_fraction = float(self.visible_fraction)
        if not 0.0 <= visible_fraction <= 1.0:
            raise ValueError("visible_fraction must be in [0,1]")
        surface = str(self.source_surface)
        if surface not in _SURFACES:
            raise ValueError(f"source_surface must be one of {sorted(_SURFACES)}")
        observation_id = str(self.observation_id).strip()
        if not observation_id:
            raise ValueError("observation_id must be non-empty")
        source_artifact = _sha256(self.source_artifact_sha256, label="source_artifact_sha256")
        lock_digest = _sha256(self.observation_lock_digest, label="observation_lock_digest")
        state_digest = None
        if self.source_state_sha256 is not None:
            state_digest = _sha256(self.source_state_sha256, label="source_state_sha256")
        if surface == "drawing" and state_digest is None:
            raise ValueError("drawing region evidence requires source_state_sha256")
        subject_height = None if self.subject_height is None else float(self.subject_height)
        if subject_height is not None and subject_height <= 0.0:
            raise ValueError("subject_height must be positive when supplied")
        object.__setattr__(self, "region_id", region_id)
        object.__setattr__(self, "side_role", side_role)
        object.__setattr__(self, "axis_start", start)
        object.__setattr__(self, "axis_end", end)
        object.__setattr__(self, "stations", stations)
        object.__setattr__(self, "visible_fraction", visible_fraction)
        object.__setattr__(self, "occlusion", tuple(map(str, self.occlusion)))
        object.__setattr__(self, "source_surface", surface)
        object.__setattr__(self, "observation_id", observation_id)
        object.__setattr__(self, "source_artifact_sha256", source_artifact)
        object.__setattr__(self, "observation_lock_digest", lock_digest)
        object.__setattr__(self, "source_state_sha256", state_digest)
        object.__setattr__(self, "subject_height", subject_height)

    @property
    def axis_length(self) -> float:
        return _distance(self.axis_start, self.axis_end)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "img2drawing.region_envelope.v1",
            "region_id": self.region_id,
            "side_role": self.side_role,
            "axis_start": list(self.axis_start),
            "axis_end": list(self.axis_end),
            "stations": [item.to_dict() for item in self.stations],
            "visible_fraction": self.visible_fraction,
            "occlusion": list(self.occlusion),
            "source_surface": self.source_surface,
            "observation_id": self.observation_id,
            "source_artifact_sha256": self.source_artifact_sha256,
            "observation_lock_digest": self.observation_lock_digest,
            "source_state_sha256": self.source_state_sha256,
            "subject_height": self.subject_height,
        }

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "RegionEnvelopeObservation":
        if raw.get("schema") not in (None, "img2drawing.region_envelope.v1"):
            raise ValueError(f"unsupported region envelope schema: {raw.get('schema')!r}")
        return cls(
            region_id=str(raw["region_id"]),
            side_role=str(raw.get("side_role", "unknown")),
            axis_start=tuple(raw["axis_start"]),
            axis_end=tuple(raw["axis_end"]),
            stations=tuple(EnvelopeStation.from_dict(item) for item in raw["stations"]),
            visible_fraction=float(raw["visible_fraction"]),
            occlusion=tuple(map(str, raw.get("occlusion", ()))),
            source_surface=str(raw["source_surface"]),
            observation_id=str(raw["observation_id"]),
            source_artifact_sha256=str(raw["source_artifact_sha256"]),
            observation_lock_digest=str(raw["observation_lock_digest"]),
            source_state_sha256=raw.get("source_state_sha256"),
            subject_height=raw.get("subject_height"),
        )


class RegionEnvelopeIntegrityError(ValueError):
    """Raised when region evidence cannot be compared without provenance drift."""


@dataclass(frozen=True)
class EnvelopeIntegrity:
    valid: bool
    errors: tuple[str, ...]
    warnings: tuple[str, ...]
    distinct_observation_ids: bool
    distinct_source_artifacts: bool
    lock_digest_matches: bool
    drawing_state_current: bool | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "valid": self.valid,
            "errors": list(self.errors),
            "warnings": list(self.warnings),
            "distinct_observation_ids": self.distinct_observation_ids,
            "distinct_source_artifacts": self.distinct_source_artifacts,
            "lock_digest_matches": self.lock_digest_matches,
            "drawing_state_current": self.drawing_state_current,
        }


@dataclass(frozen=True)
class AxisEnvelopeEvidence:
    start_delta: float
    end_delta: float
    reference_length: float
    drawing_length: float
    length_ratio: float

    def to_dict(self) -> dict[str, float]:
        return {
            "start_delta": self.start_delta,
            "end_delta": self.end_delta,
            "reference_length": self.reference_length,
            "drawing_length": self.drawing_length,
            "length_ratio": self.length_ratio,
        }


@dataclass(frozen=True)
class StationEnvelopeEvidence:
    t: float
    reference_width_canvas: float
    drawing_width_canvas: float
    reference_width_local_axis: float
    drawing_width_local_axis: float
    reference_width_subject_height: float | None
    drawing_width_subject_height: float | None
    width_delta: float
    width_ratio: float
    visible_disagreement: bool
    reference_visibility: str
    drawing_visibility: str

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__.copy()


@dataclass(frozen=True)
class RegionGeometryComparison:
    """Measured region discrepancy; it has no artistic PASS/FAIL decision."""

    region_id: str
    axis: AxisEnvelopeEvidence
    stations: tuple[StationEnvelopeEvidence, ...]
    visible_fraction_reference: float
    visible_fraction_drawing: float
    visible_fraction_delta: float
    occlusion_order_changed: bool
    integrity: EnvelopeIntegrity

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "img2drawing.region_geometry_comparison.v1",
            "authority": "evidence_not_pass_fail",
            "region_id": self.region_id,
            "integrity": self.integrity.to_dict(),
            "axis": self.axis.to_dict(),
            "stations": [item.to_dict() for item in self.stations],
            "visible_fraction_reference": self.visible_fraction_reference,
            "visible_fraction_drawing": self.visible_fraction_drawing,
            "visible_fraction_delta": self.visible_fraction_delta,
            "occlusion_order_changed": self.occlusion_order_changed,
        }


def _integrity(
    reference: RegionEnvelopeObservation,
    drawing: RegionEnvelopeObservation,
    *,
    current_drawing_state_sha256: str | None,
) -> EnvelopeIntegrity:
    errors: list[str] = []
    warnings: list[str] = []
    distinct_ids = reference.observation_id != drawing.observation_id
    distinct_artifacts = reference.source_artifact_sha256 != drawing.source_artifact_sha256
    lock_matches = reference.observation_lock_digest == drawing.observation_lock_digest
    state_current: bool | None = None
    if reference.source_surface != "reference":
        errors.append("reference region must use source_surface='reference'")
    if drawing.source_surface != "drawing":
        errors.append("drawing region must use source_surface='drawing'")
    if not distinct_ids:
        errors.append("reference and drawing region observations must have distinct observation_id values")
    if not distinct_artifacts:
        errors.append("reference and drawing region evidence must use distinct source artifacts")
    if not lock_matches:
        errors.append("reference and drawing region evidence must share the frozen observation lock digest")
    if current_drawing_state_sha256 is not None:
        current = _sha256(current_drawing_state_sha256, label="current_drawing_state_sha256")
        state_current = drawing.source_state_sha256 == current
        if not state_current:
            errors.append("drawing region evidence is stale for the current drawing state")
    elif drawing.source_state_sha256 is None:
        errors.append("drawing region evidence requires a drawing state digest")
    else:
        warnings.append("current drawing state was not supplied; staleness could not be checked")
    if reference.region_id != drawing.region_id:
        errors.append("reference and drawing region ids must match")
    if len(reference.stations) != len(drawing.stations):
        errors.append("reference and drawing must use the same station count")
    else:
        for index, (ref_station, drw_station) in enumerate(zip(reference.stations, drawing.stations)):
            if abs(ref_station.t - drw_station.t) > 1e-6:
                errors.append(f"station t mismatch at index {index}")
                break
    return EnvelopeIntegrity(
        valid=not errors,
        errors=tuple(errors),
        warnings=tuple(warnings),
        distinct_observation_ids=distinct_ids,
        distinct_source_artifacts=distinct_artifacts,
        lock_digest_matches=lock_matches,
        drawing_state_current=state_current,
    )


def compare_region_envelopes(
    reference: RegionEnvelopeObservation,
    drawing: RegionEnvelopeObservation,
    *,
    current_drawing_state_sha256: str | None = None,
    require_independent: bool = True,
) -> RegionGeometryComparison:
    """Compare paired region envelopes in linear time over at most 16 stations.

    ``current_drawing_state_sha256`` should be the hash of the drawing cursor
    being reviewed.  Supplying it turns stale drawing evidence into a hard
    integrity error.  The returned values are measurements and hints only.
    """
    reference = reference if isinstance(reference, RegionEnvelopeObservation) else RegionEnvelopeObservation.from_dict(reference)
    drawing = drawing if isinstance(drawing, RegionEnvelopeObservation) else RegionEnvelopeObservation.from_dict(drawing)
    integrity = _integrity(
        reference, drawing, current_drawing_state_sha256=current_drawing_state_sha256
    )
    if require_independent and not integrity.valid:
        raise RegionEnvelopeIntegrityError("; ".join(integrity.errors))

    axis = AxisEnvelopeEvidence(
        start_delta=_distance(reference.axis_start, drawing.axis_start),
        end_delta=_distance(reference.axis_end, drawing.axis_end),
        reference_length=reference.axis_length,
        drawing_length=drawing.axis_length,
        length_ratio=drawing.axis_length / reference.axis_length,
    )
    stations: list[StationEnvelopeEvidence] = []
    for ref_station, drw_station in zip(reference.stations, drawing.stations):
        ref_local = ref_station.width_local_axis(reference.axis_length)
        drw_local = drw_station.width_local_axis(drawing.axis_length)
        ref_subject = (
            None
            if reference.subject_height is None
            else ref_station.width_canvas / reference.subject_height
        )
        drw_subject = (
            None
            if drawing.subject_height is None
            else drw_station.width_canvas / drawing.subject_height
        )
        stations.append(
            StationEnvelopeEvidence(
                t=ref_station.t,
                reference_width_canvas=ref_station.width_canvas,
                drawing_width_canvas=drw_station.width_canvas,
                reference_width_local_axis=ref_local,
                drawing_width_local_axis=drw_local,
                reference_width_subject_height=ref_subject,
                drawing_width_subject_height=drw_subject,
                width_delta=drw_local - ref_local,
                width_ratio=drw_local / ref_local if ref_local else math.inf,
                visible_disagreement=ref_station.visibility != drw_station.visibility,
                reference_visibility=ref_station.visibility,
                drawing_visibility=drw_station.visibility,
            )
        )
    return RegionGeometryComparison(
        region_id=reference.region_id,
        axis=axis,
        stations=tuple(stations),
        visible_fraction_reference=reference.visible_fraction,
        visible_fraction_drawing=drawing.visible_fraction,
        visible_fraction_delta=drawing.visible_fraction - reference.visible_fraction,
        occlusion_order_changed=reference.occlusion != drawing.occlusion,
        integrity=integrity,
    )


__all__ = [
    "EnvelopeStation",
    "RegionEnvelopeObservation",
    "RegionEnvelopeIntegrityError",
    "EnvelopeIntegrity",
    "AxisEnvelopeEvidence",
    "StationEnvelopeEvidence",
    "RegionGeometryComparison",
    "compare_region_envelopes",
]
