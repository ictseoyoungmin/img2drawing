from __future__ import annotations

"""Head and hair primary-mass evidence."""

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


def _bounds(value: Sequence[float], label: str) -> tuple[float, float, float, float]:
    if len(value) != 4:
        raise ValueError(f"{label} requires u0,v0,u1,v1")
    u0, v0, u1, v1 = map(float, value)
    if not (0.0 <= u0 < u1 <= 1.0 and 0.0 <= v0 < v1 <= 1.0):
        raise ValueError(f"{label} must be ordered inside normalized canvas")
    return u0, v0, u1, v1


def _digest(value: str, label: str) -> str:
    value = str(value).lower()
    if not _SHA256.fullmatch(value):
        raise ValueError(f"{label} must be a 64-character lowercase hex digest")
    return value


@dataclass(frozen=True)
class HeadHairObservation:
    head_top: Point
    chin: Point
    cranial_left: Point
    cranial_right: Point
    jaw_left: Point
    jaw_right: Point
    head_bounds: tuple[float, float, float, float]
    hair_bounds: tuple[float, float, float, float]
    hair_style: str
    hair_occlusion: tuple[str, ...]
    anatomical_uncertainty: tuple[str, ...]
    source_surface: str
    observation_id: str
    source_artifact_sha256: str
    observation_lock_digest: str
    source_state_sha256: str | None = None

    def __post_init__(self) -> None:
        points = {
            "head_top": _point(self.head_top, "head_top"),
            "chin": _point(self.chin, "chin"),
            "cranial_left": _point(self.cranial_left, "cranial_left"),
            "cranial_right": _point(self.cranial_right, "cranial_right"),
            "jaw_left": _point(self.jaw_left, "jaw_left"),
            "jaw_right": _point(self.jaw_right, "jaw_right"),
        }
        head_bounds = _bounds(self.head_bounds, "head_bounds")
        hair_bounds = _bounds(self.hair_bounds, "hair_bounds")
        style = str(self.hair_style).strip()
        if not style:
            raise ValueError("hair_style must be non-empty")
        surface = str(self.source_surface)
        if surface not in {"reference", "drawing"}:
            raise ValueError("source_surface must be reference or drawing")
        state = None if self.source_state_sha256 is None else _digest(self.source_state_sha256, "source_state_sha256")
        if surface == "drawing" and state is None:
            raise ValueError("drawing head/hair evidence requires source_state_sha256")
        for name, value in points.items():
            object.__setattr__(self, name, value)
        object.__setattr__(self, "head_bounds", head_bounds)
        object.__setattr__(self, "hair_bounds", hair_bounds)
        object.__setattr__(self, "hair_style", style)
        object.__setattr__(self, "hair_occlusion", tuple(map(str, self.hair_occlusion)))
        object.__setattr__(self, "anatomical_uncertainty", tuple(map(str, self.anatomical_uncertainty)))
        object.__setattr__(self, "source_surface", surface)
        object.__setattr__(self, "observation_id", str(self.observation_id).strip())
        if not self.observation_id:
            raise ValueError("observation_id must be non-empty")
        object.__setattr__(self, "source_artifact_sha256", _digest(self.source_artifact_sha256, "source_artifact_sha256"))
        object.__setattr__(self, "observation_lock_digest", _digest(self.observation_lock_digest, "observation_lock_digest"))
        object.__setattr__(self, "source_state_sha256", state)

    @property
    def head_width(self) -> float:
        return self.head_bounds[2] - self.head_bounds[0]

    @property
    def head_height(self) -> float:
        return self.head_bounds[3] - self.head_bounds[1]

    @property
    def hair_width(self) -> float:
        return self.hair_bounds[2] - self.hair_bounds[0]

    @property
    def hair_height(self) -> float:
        return self.hair_bounds[3] - self.hair_bounds[1]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "img2drawing.head_hair.v1",
            "head_top": list(self.head_top),
            "chin": list(self.chin),
            "cranial_left": list(self.cranial_left),
            "cranial_right": list(self.cranial_right),
            "jaw_left": list(self.jaw_left),
            "jaw_right": list(self.jaw_right),
            "head_bounds": list(self.head_bounds),
            "hair_bounds": list(self.hair_bounds),
            "hair_style": self.hair_style,
            "hair_occlusion": list(self.hair_occlusion),
            "anatomical_uncertainty": list(self.anatomical_uncertainty),
            "source_surface": self.source_surface,
            "observation_id": self.observation_id,
            "source_artifact_sha256": self.source_artifact_sha256,
            "observation_lock_digest": self.observation_lock_digest,
            "source_state_sha256": self.source_state_sha256,
        }

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "HeadHairObservation":
        if raw.get("schema") not in (None, "img2drawing.head_hair.v1"):
            raise ValueError(f"unsupported head/hair schema: {raw.get('schema')!r}")
        return cls(
            head_top=tuple(raw["head_top"]),
            chin=tuple(raw["chin"]),
            cranial_left=tuple(raw["cranial_left"]),
            cranial_right=tuple(raw["cranial_right"]),
            jaw_left=tuple(raw["jaw_left"]),
            jaw_right=tuple(raw["jaw_right"]),
            head_bounds=tuple(raw["head_bounds"]),
            hair_bounds=tuple(raw["hair_bounds"]),
            hair_style=str(raw["hair_style"]),
            hair_occlusion=tuple(map(str, raw.get("hair_occlusion", ()))),
            anatomical_uncertainty=tuple(map(str, raw.get("anatomical_uncertainty", ()))),
            source_surface=str(raw["source_surface"]),
            observation_id=str(raw["observation_id"]),
            source_artifact_sha256=str(raw["source_artifact_sha256"]),
            observation_lock_digest=str(raw["observation_lock_digest"]),
            source_state_sha256=raw.get("source_state_sha256"),
        )


class HeadHairIntegrityError(ValueError):
    pass


@dataclass(frozen=True)
class HeadHairComparison:
    head_width_delta: float
    head_height_delta: float
    hair_width_delta: float
    hair_height_delta: float
    cranial_asymmetry_delta: float
    jaw_asymmetry_delta: float
    hair_style_mismatch: bool
    hair_occlusion_changed: bool
    integrity: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "img2drawing.head_hair_comparison.v1",
            "authority": "evidence_not_pass_fail",
            "head_width_delta": self.head_width_delta,
            "head_height_delta": self.head_height_delta,
            "hair_width_delta": self.hair_width_delta,
            "hair_height_delta": self.hair_height_delta,
            "cranial_asymmetry_delta": self.cranial_asymmetry_delta,
            "jaw_asymmetry_delta": self.jaw_asymmetry_delta,
            "hair_style_mismatch": self.hair_style_mismatch,
            "hair_occlusion_changed": self.hair_occlusion_changed,
            "integrity": dict(self.integrity),
        }


def compare_head_hair(
    reference: HeadHairObservation,
    drawing: HeadHairObservation,
    *,
    current_drawing_state_sha256: str | None = None,
    require_independent: bool = True,
) -> HeadHairComparison:
    reference = reference if isinstance(reference, HeadHairObservation) else HeadHairObservation.from_dict(reference)
    drawing = drawing if isinstance(drawing, HeadHairObservation) else HeadHairObservation.from_dict(drawing)
    errors: list[str] = []
    warnings: list[str] = []
    if reference.source_surface != "reference" or drawing.source_surface != "drawing":
        errors.append("head/hair observations must use reference and drawing surfaces")
    distinct_ids = reference.observation_id != drawing.observation_id
    distinct_artifacts = reference.source_artifact_sha256 != drawing.source_artifact_sha256
    lock_match = reference.observation_lock_digest == drawing.observation_lock_digest
    if not distinct_ids:
        errors.append("head/hair observations must use distinct observation_id values")
    if not distinct_artifacts:
        errors.append("head/hair observations must use distinct source artifacts")
    if not lock_match:
        errors.append("head/hair observations must share the frozen observation lock digest")
    state_current: bool | None = None
    if current_drawing_state_sha256 is None:
        warnings.append("current drawing state was not supplied; staleness could not be checked")
    else:
        state_current = drawing.source_state_sha256 == _digest(current_drawing_state_sha256, "current_drawing_state_sha256")
        if not state_current:
            errors.append("drawing head/hair evidence is stale for the current drawing state")
    if require_independent and errors:
        raise HeadHairIntegrityError("; ".join(errors))
    cranial_ref = abs(reference.cranial_right[0] - reference.cranial_left[0])
    cranial_drw = abs(drawing.cranial_right[0] - drawing.cranial_left[0])
    jaw_ref = abs(reference.jaw_right[0] - reference.jaw_left[0])
    jaw_drw = abs(drawing.jaw_right[0] - drawing.jaw_left[0])
    return HeadHairComparison(
        head_width_delta=drawing.head_width - reference.head_width,
        head_height_delta=drawing.head_height - reference.head_height,
        hair_width_delta=drawing.hair_width - reference.hair_width,
        hair_height_delta=drawing.hair_height - reference.hair_height,
        cranial_asymmetry_delta=(cranial_drw - drawing.head_width / 2) - (cranial_ref - reference.head_width / 2),
        jaw_asymmetry_delta=(jaw_drw - drawing.head_width / 2) - (jaw_ref - reference.head_width / 2),
        hair_style_mismatch=reference.hair_style != drawing.hair_style,
        hair_occlusion_changed=reference.hair_occlusion != drawing.hair_occlusion,
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


__all__ = ["HeadHairObservation", "HeadHairIntegrityError", "HeadHairComparison", "compare_head_hair"]
