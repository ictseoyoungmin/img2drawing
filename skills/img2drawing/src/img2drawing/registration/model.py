from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any, Mapping, Sequence

Visibility = str
_VALID_VISIBILITY = {"visible", "occluded", "inferred", "unknown"}
_VALID_SURFACES = {"reference", "drawing", "generic", "unspecified"}


def _norm_bounds(value: Sequence[float] | None) -> tuple[float, float, float, float] | None:
    if value is None:
        return None
    if len(value) != 4:
        raise ValueError("bounds require u0,v0,u1,v1")
    u0, v0, u1, v1 = map(float, value)
    if not (0.0 <= u0 < u1 <= 1.0 and 0.0 <= v0 < v1 <= 1.0):
        raise ValueError("bounds must be ordered inside [0,1]")
    return u0, v0, u1, v1


@dataclass(frozen=True)
class RegistrationLandmark:
    """Agent-observed normalized landmark; never an automatic truth claim."""

    name: str
    u: float
    v: float
    confidence: float = 1.0
    visibility: Visibility = "visible"
    uncertainty_radius: float = 0.0
    source_observation: str = ""
    evidence_roi: tuple[float, float, float, float] | None = None
    provenance: Mapping[str, Any] = field(default_factory=dict)

    def validated(self) -> "RegistrationLandmark":
        if not str(self.name).strip():
            raise ValueError("landmark name must be non-empty")
        if not (0.0 <= float(self.u) <= 1.0 and 0.0 <= float(self.v) <= 1.0):
            raise ValueError(f"landmark {self.name!r} must lie inside normalized canvas")
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be in [0,1]")
        if str(self.visibility) not in _VALID_VISIBILITY:
            raise ValueError(f"visibility must be one of {sorted(_VALID_VISIBILITY)}")
        if not 0.0 <= float(self.uncertainty_radius) <= 1.0:
            raise ValueError("uncertainty_radius must be in [0,1]")
        _norm_bounds(self.evidence_roi)
        return self

    def to_dict(self) -> dict[str, Any]:
        self.validated()
        out: dict[str, Any] = {
            "name": self.name,
            "u": float(self.u),
            "v": float(self.v),
            "confidence": float(self.confidence),
            "visibility": self.visibility,
            "uncertainty_radius": float(self.uncertainty_radius),
            "source_observation": self.source_observation,
            "provenance": dict(self.provenance),
        }
        if self.evidence_roi is not None:
            out["evidence_roi"] = list(self.evidence_roi)
        return out

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "RegistrationLandmark":
        roi = raw.get("evidence_roi")
        return cls(
            name=str(raw["name"]), u=float(raw["u"]), v=float(raw["v"]),
            confidence=float(raw.get("confidence", 1.0)),
            visibility=str(raw.get("visibility", "visible")),
            uncertainty_radius=float(raw.get("uncertainty_radius", 0.0)),
            source_observation=str(raw.get("source_observation", "")),
            evidence_roi=None if roi is None else tuple(map(float, roi)),
            provenance=dict(raw.get("provenance") or {}),
        ).validated()


@dataclass(frozen=True)
class RegistrationConnection:
    a: str
    b: str
    role: str = "skeleton"
    provenance: Mapping[str, Any] = field(default_factory=dict)

    @property
    def id(self) -> str:
        return f"{self.a}->{self.b}"

    def validated(self) -> "RegistrationConnection":
        if not self.a or not self.b or self.a == self.b:
            raise ValueError("connection endpoints must be distinct non-empty landmark names")
        return self

    def to_dict(self) -> dict[str, Any]:
        self.validated()
        return {"a": self.a, "b": self.b, "role": self.role, "provenance": dict(self.provenance)}

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "RegistrationConnection":
        return cls(str(raw["a"]), str(raw["b"]), str(raw.get("role", "skeleton")), dict(raw.get("provenance") or {})).validated()


@dataclass(frozen=True)
class RegistrationGraph:
    """Canonical normalized observation graph shared by reference and drawing review.

    `source_surface`, `observation_id` and `source_artifact_sha256` are provenance-integrity
    fields. They let the public DrawingRun path prove that reference and drawing registrations
    came from distinct observed surfaces. Coordinates remain evidence, never an artistic
    pass/fail authority.
    """

    source_size: tuple[int, int]
    landmarks: Mapping[str, RegistrationLandmark]
    connections: tuple[RegistrationConnection, ...] = ()
    subject_bounds: tuple[float, float, float, float] | None = None
    graph_type: str = "generic"
    source_surface: str = "unspecified"
    observation_id: str | None = None
    source_artifact_sha256: str | None = None
    provenance: Mapping[str, Any] = field(default_factory=dict)

    def validated(self) -> "RegistrationGraph":
        w, h = map(int, self.source_size)
        if w <= 0 or h <= 0:
            raise ValueError("source_size must be positive")
        _norm_bounds(self.subject_bounds)
        if self.source_surface not in _VALID_SURFACES:
            raise ValueError(f"source_surface must be one of {sorted(_VALID_SURFACES)}")
        if self.observation_id is not None and not str(self.observation_id).strip():
            raise ValueError("observation_id must be non-empty when supplied")
        if self.source_artifact_sha256 is not None:
            digest = str(self.source_artifact_sha256).lower()
            if len(digest) != 64 or any(ch not in "0123456789abcdef" for ch in digest):
                raise ValueError("source_artifact_sha256 must be a 64-character hex digest")
        if not self.landmarks:
            raise ValueError("registration graph requires at least one landmark")
        for name, landmark in self.landmarks.items():
            landmark.validated()
            if str(name) != landmark.name:
                raise ValueError("landmark mapping key must equal landmark.name")
        seen: set[tuple[str, str, str]] = set()
        for edge in self.connections:
            edge.validated()
            if edge.a not in self.landmarks or edge.b not in self.landmarks:
                raise KeyError(f"connection endpoint missing from graph: {edge.id}")
            key = (edge.a, edge.b, edge.role)
            if key in seen:
                raise ValueError(f"duplicate connection: {edge.id}")
            seen.add(key)
        return self

    def bind_observation(
        self,
        *,
        source_surface: str,
        observation_id: str,
        source_artifact_sha256: str,
        provenance: Mapping[str, Any] | None = None,
    ) -> "RegistrationGraph":
        """Return a graph bound to one concrete observed surface/artifact.

        Binding is intentionally explicit and immutable so the same graph object cannot
        silently masquerade as both reference and drawing evidence.
        """
        merged = dict(self.provenance)
        merged.update(dict(provenance or {}))
        return replace(
            self,
            source_surface=str(source_surface),
            observation_id=str(observation_id),
            source_artifact_sha256=str(source_artifact_sha256).lower(),
            provenance=merged,
        ).validated()

    def landmark(self, name: str) -> RegistrationLandmark:
        try:
            return self.landmarks[str(name)]
        except KeyError as exc:
            raise KeyError(f"unknown registration landmark: {name}") from exc

    def point_px(self, name: str) -> tuple[float, float]:
        lm = self.landmark(name)
        return lm.u * self.source_size[0], lm.v * self.source_size[1]

    def subject_point(self, name: str) -> tuple[float, float]:
        if self.subject_bounds is None:
            raise ValueError("subject_point requires subject_bounds")
        lm = self.landmark(name)
        u0, v0, u1, v1 = self.subject_bounds
        return ((lm.u-u0)/(u1-u0), (lm.v-v0)/(v1-v0))

    def to_dict(self) -> dict[str, Any]:
        self.validated()
        return {
            "schema": "img2drawing.registration_graph.v2",
            "source_size": list(map(int, self.source_size)),
            "graph_type": self.graph_type,
            "source_surface": self.source_surface,
            "observation_id": self.observation_id,
            "source_artifact_sha256": self.source_artifact_sha256,
            "subject_bounds": None if self.subject_bounds is None else list(self.subject_bounds),
            "landmarks": [self.landmarks[name].to_dict() for name in sorted(self.landmarks)],
            "connections": [edge.to_dict() for edge in self.connections],
            "provenance": dict(self.provenance),
        }

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "RegistrationGraph":
        landmarks = {lm.name: lm for lm in (RegistrationLandmark.from_dict(v) for v in raw.get("landmarks", []))}
        bounds = raw.get("subject_bounds")
        return cls(
            source_size=tuple(map(int, raw["source_size"])),
            landmarks=landmarks,
            connections=tuple(RegistrationConnection.from_dict(v) for v in raw.get("connections", [])),
            subject_bounds=None if bounds is None else tuple(map(float, bounds)),
            graph_type=str(raw.get("graph_type", "generic")),
            source_surface=str(raw.get("source_surface", "unspecified")),
            observation_id=None if raw.get("observation_id") is None else str(raw.get("observation_id")),
            source_artifact_sha256=None if raw.get("source_artifact_sha256") is None else str(raw.get("source_artifact_sha256")),
            provenance=dict(raw.get("provenance") or {}),
        ).validated()
