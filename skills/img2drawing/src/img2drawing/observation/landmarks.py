"""Explicit 2D landmarks; no feature detection or correspondence inference."""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Sequence

from ..inspection import Measurement, Point, Registration, distance

LANDMARK_SCHEMA = "img2drawing.observation.landmarks.v1"


def _text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be nonempty")
    return value.strip()


def _xy(value):
    if len(value) != 2 or any(isinstance(v, bool) for v in value):
        raise ValueError("position requires two coordinates")
    p = tuple(map(float, value))
    if not all(math.isfinite(v) for v in p):
        raise ValueError("position must be finite")
    return p


@dataclass(frozen=True)
class Landmark:
    name: str
    position: Point | None
    evidence: str
    visibility: str = "observed"

    def __post_init__(self):
        object.__setattr__(self, "name", _text(self.name, "landmark name"))
        object.__setattr__(self, "evidence", _text(self.evidence, "landmark evidence"))
        if self.visibility not in ("observed", "uncertain", "inferred"):
            raise ValueError("unknown landmark visibility")
        if self.position is not None:
            object.__setattr__(self, "position", _xy(self.position))
        elif self.visibility == "observed":
            raise ValueError("observed landmark requires a position")

    def to_dict(self):
        return {"name": self.name, "position": None if self.position is None else list(self.position),
                "evidence": self.evidence, "visibility": self.visibility}


@dataclass(frozen=True)
class LandmarkSet:
    """An agent-authored observation of a specific subject or drawing image.

    Coordinates are continuous geometric image coordinates (inclusive outer
    edges), not integer pixel indices. Inferred/uncertain landmarks remain
    records and cannot enter geometric measurements.
    """
    space: str
    size: tuple[int, int]
    landmarks: tuple[Landmark, ...]

    def __post_init__(self):
        if self.space not in ("subject", "canvas"):
            raise ValueError("landmark space must be subject or canvas")
        size = tuple(self.size)
        if len(size) != 2 or any(type(v) is not int or v <= 0 for v in size):
            raise ValueError("size requires positive integer width and height")
        items = tuple(self.landmarks)
        if not items or any(not isinstance(v, Landmark) for v in items):
            raise ValueError("landmarks must contain Landmark records")
        if len({v.name for v in items}) != len(items):
            raise ValueError("duplicate landmark name")
        for v in items:
            if v.position is not None and not all(0 <= x <= n for x, n in zip(v.position, size)):
                raise ValueError(f"landmark outside {self.space}: {v.name}")
        object.__setattr__(self, "size", size)
        object.__setattr__(self, "landmarks", items)

    def observed(self, name: str) -> Point:
        for item in self.landmarks:
            if item.name == name:
                if item.visibility != "observed":
                    raise ValueError(f"not an observed landmark: {name}")
                return item.position
        raise ValueError(f"unknown landmark: {name}")

    def to_dict(self):
        return {"schema": LANDMARK_SCHEMA, "space": self.space, "size": list(self.size),
                "landmarks": [v.to_dict() for v in self.landmarks]}

    def ratio(self, numerator: Sequence[str], denominator: Sequence[str]) -> Measurement:
        """Ratio of two explicitly selected visible projected distances."""
        a, b = _segment(self, numerator)
        c, d = _segment(self, denominator)
        n = distance(a, b, space=self.space).value
        den = distance(c, d, space=self.space).value
        if den == 0:
            raise ValueError("ratio denominator is zero")
        return Measurement("landmark_ratio", n/den, self.space,
                           {"numerator": list(numerator), "denominator": list(denominator),
                            "numerator_length": n, "denominator_length": den},
                           {"operation": "explicit visible landmark distances", "inference": False})


def _segment(points: LandmarkSet, labels: Sequence[str]) -> tuple[Point, Point]:
    if isinstance(labels, str) or len(labels) != 2 or labels[0] == labels[1]:
        raise ValueError("segment requires two distinct landmark names")
    return points.observed(labels[0]), points.observed(labels[1])


def _registered(reference, drawing, registration):
    if reference.space != "subject" or drawing.space != "canvas":
        raise ValueError("comparison requires subject reference and canvas drawing")
    if not isinstance(registration, Registration):
        raise TypeError("explicit Registration required")
    if (reference.size != registration.subject_size or drawing.size != registration.canvas_size):
        raise ValueError("registration sizes do not match landmark sets")


def _mapped(reference, name, registration):
    return registration.map_subject_to_canvas(reference.observed(name))


def compare_landmarks(reference: LandmarkSet, drawing: LandmarkSet, *,
                      registration: Registration, labels: Sequence[str],
                      normalizer: Sequence[str]) -> Measurement:
    """Compare independently declared matching visible landmarks in canvas units.

    Normalization is the explicitly chosen reference span after registration.
    No automatic alignment, correspondence, weighting or likeness verdict.
    """
    _registered(reference, drawing, registration)
    if isinstance(labels, str):
        raise ValueError("labels must be a sequence of names")
    labels = tuple(labels)
    if not labels or len(set(labels)) != len(labels):
        raise ValueError("comparison requires unique landmark labels")
    a, b = _segment(reference, normalizer)
    span = distance(a, b, space="canvas", registration=registration).value
    if span == 0:
        raise ValueError("reference normalizer has zero length")
    rows = []
    for name in labels:
        expected = _mapped(reference, name, registration)
        actual = drawing.observed(name)
        delta = tuple(y-x for x,y in zip(expected, actual))
        error = math.hypot(*delta)
        rows.append({"name": name, "reference_canvas": list(expected), "drawing_canvas": list(actual),
                     "delta": list(delta), "distance": error, "normalized_distance": error/span})
    rms = math.sqrt(math.fsum(v["normalized_distance"]**2 for v in rows)/len(rows))
    return Measurement("landmark_comparison", {"landmarks": rows, "normalized_rms": rms,
                         "normalizer_length_canvas": span}, "canvas",
                       {"labels": list(labels), "normalizer": list(normalizer),
                        "registration": registration.to_dict()},
                       {"operation": "agent-declared correspondence", "inference": False,
                        "artistic_verdict": "NOT_EVALUATED"})


def compare_ratios(reference: LandmarkSet, drawing: LandmarkSet, *,
                   registration: Registration, numerator: Sequence[str],
                   denominator: Sequence[str]) -> Measurement:
    """Compare projected relative distances after applying the same registration."""
    _registered(reference, drawing, registration)
    a, b = _segment(reference, numerator)
    c, d = _segment(reference, denominator)
    n = distance(a, b, space="canvas", registration=registration).value
    den = distance(c, d, space="canvas", registration=registration).value
    if den == 0:
        raise ValueError("reference ratio denominator is zero")
    expected = n/den
    actual = drawing.ratio(numerator, denominator).value
    return Measurement("landmark_ratio_comparison", {"reference": expected, "drawing": actual,
                         "delta": actual-expected, "relative_delta": None if expected == 0 else (actual-expected)/expected},
                       "canvas", {"numerator": list(numerator), "denominator": list(denominator),
                                  "registration": registration.to_dict()},
                       {"operation": "registered explicit visible distances", "inference": False})
