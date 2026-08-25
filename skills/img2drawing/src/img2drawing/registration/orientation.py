from __future__ import annotations

"""Evidence for torso orientation and near/far arm dominance."""

from dataclasses import dataclass
import math
import re
from typing import Any, Mapping, Sequence


Point = tuple[float, float]
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_SURFACES = frozenset({"reference", "drawing"})
_BODY_VIEWS = frozenset({"front", "back", "side", "three_quarter", "back_three_quarter", "front_three_quarter", "unknown"})
_TORSO_TURNS = frozenset({"left", "right", "none", "unknown"})
_NEAR_SIDES = frozenset({"subject_left", "subject_right", "image_left", "image_right", "unknown"})


def _point(value: Sequence[float], label: str) -> Point:
    if len(value) != 2:
        raise ValueError(f"{label} requires x,y")
    point = tuple(map(float, value))
    if not all(0.0 <= item <= 1.0 for item in point):
        raise ValueError(f"{label} must lie inside normalized canvas")
    return point  # type: ignore[return-value]


def _bounds(value: Sequence[float]) -> tuple[float, float, float, float]:
    if len(value) != 4:
        raise ValueError("torso_bounds requires u0,v0,u1,v1")
    u0, v0, u1, v1 = map(float, value)
    if not (0.0 <= u0 < u1 <= 1.0 and 0.0 <= v0 < v1 <= 1.0):
        raise ValueError("torso_bounds must be ordered inside normalized canvas")
    return u0, v0, u1, v1


def _digest(value: str, label: str) -> str:
    value = str(value).lower()
    if not _SHA256.fullmatch(value):
        raise ValueError(f"{label} must be a 64-character lowercase hex digest")
    return value


@dataclass(frozen=True)
class TorsoOrientationObservation:
    body_view: str
    torso_turn: str
    near_side: str
    left_shoulder: Point
    right_shoulder: Point
    torso_bounds: tuple[float, float, float, float]
    near_arm_exposure: float
    far_arm_exposure: float
    contour_owners: tuple[str, ...]
    source_surface: str
    observation_id: str
    source_artifact_sha256: str
    observation_lock_digest: str
    source_state_sha256: str | None = None
    uncertainty_notes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        body_view = str(self.body_view)
        torso_turn = str(self.torso_turn)
        near_side = str(self.near_side)
        if body_view not in _BODY_VIEWS:
            raise ValueError(f"body_view must be one of {sorted(_BODY_VIEWS)}")
        if torso_turn not in _TORSO_TURNS:
            raise ValueError(f"torso_turn must be one of {sorted(_TORSO_TURNS)}")
        if near_side not in _NEAR_SIDES:
            raise ValueError(f"near_side must be one of {sorted(_NEAR_SIDES)}")
        left = _point(self.left_shoulder, "left_shoulder")
        right = _point(self.right_shoulder, "right_shoulder")
        if left == right:
            raise ValueError("shoulder envelope requires two distinct points")
        bounds = _bounds(self.torso_bounds)
        for value, label in ((self.near_arm_exposure, "near_arm_exposure"), (self.far_arm_exposure, "far_arm_exposure")):
            if not 0.0 <= float(value) <= 1.0:
                raise ValueError(f"{label} must be in [0,1]")
        owners = tuple(str(item).strip() for item in self.contour_owners if str(item).strip())
        if len(owners) != len(set(owners)):
            raise ValueError("contour_owners must not contain duplicates")
        surface = str(self.source_surface)
        if surface not in _SURFACES:
            raise ValueError(f"source_surface must be one of {sorted(_SURFACES)}")
        observation_id = str(self.observation_id).strip()
        if not observation_id:
            raise ValueError("observation_id must be non-empty")
        artifact = _digest(self.source_artifact_sha256, "source_artifact_sha256")
        lock = _digest(self.observation_lock_digest, "observation_lock_digest")
        state = None if self.source_state_sha256 is None else _digest(self.source_state_sha256, "source_state_sha256")
        if surface == "drawing" and state is None:
            raise ValueError("drawing orientation evidence requires source_state_sha256")
        object.__setattr__(self, "body_view", body_view)
        object.__setattr__(self, "torso_turn", torso_turn)
        object.__setattr__(self, "near_side", near_side)
        object.__setattr__(self, "left_shoulder", left)
        object.__setattr__(self, "right_shoulder", right)
        object.__setattr__(self, "torso_bounds", bounds)
        object.__setattr__(self, "near_arm_exposure", float(self.near_arm_exposure))
        object.__setattr__(self, "far_arm_exposure", float(self.far_arm_exposure))
        object.__setattr__(self, "contour_owners", owners)
        object.__setattr__(self, "source_surface", surface)
        object.__setattr__(self, "observation_id", observation_id)
        object.__setattr__(self, "source_artifact_sha256", artifact)
        object.__setattr__(self, "observation_lock_digest", lock)
        object.__setattr__(self, "source_state_sha256", state)
        object.__setattr__(self, "uncertainty_notes", tuple(map(str, self.uncertainty_notes)))

    @property
    def shoulder_width(self) -> float:
        return math.hypot(
            self.right_shoulder[0] - self.left_shoulder[0],
            self.right_shoulder[1] - self.left_shoulder[1],
        )

    @property
    def torso_width(self) -> float:
        return self.torso_bounds[2] - self.torso_bounds[0]

    @property
    def torso_height(self) -> float:
        return self.torso_bounds[3] - self.torso_bounds[1]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "img2drawing.torso_orientation.v1",
            "body_view": self.body_view,
            "torso_turn": self.torso_turn,
            "near_side": self.near_side,
            "left_shoulder": list(self.left_shoulder),
            "right_shoulder": list(self.right_shoulder),
            "torso_bounds": list(self.torso_bounds),
            "near_arm_exposure": self.near_arm_exposure,
            "far_arm_exposure": self.far_arm_exposure,
            "contour_owners": list(self.contour_owners),
            "source_surface": self.source_surface,
            "observation_id": self.observation_id,
            "source_artifact_sha256": self.source_artifact_sha256,
            "observation_lock_digest": self.observation_lock_digest,
            "source_state_sha256": self.source_state_sha256,
            "uncertainty_notes": list(self.uncertainty_notes),
        }

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "TorsoOrientationObservation":
        if raw.get("schema") not in (None, "img2drawing.torso_orientation.v1"):
            raise ValueError(f"unsupported torso orientation schema: {raw.get('schema')!r}")
        return cls(
            body_view=str(raw["body_view"]),
            torso_turn=str(raw["torso_turn"]),
            near_side=str(raw["near_side"]),
            left_shoulder=tuple(raw["left_shoulder"]),
            right_shoulder=tuple(raw["right_shoulder"]),
            torso_bounds=tuple(raw["torso_bounds"]),
            near_arm_exposure=float(raw["near_arm_exposure"]),
            far_arm_exposure=float(raw["far_arm_exposure"]),
            contour_owners=tuple(map(str, raw.get("contour_owners", ()))),
            source_surface=str(raw["source_surface"]),
            observation_id=str(raw["observation_id"]),
            source_artifact_sha256=str(raw["source_artifact_sha256"]),
            observation_lock_digest=str(raw["observation_lock_digest"]),
            source_state_sha256=raw.get("source_state_sha256"),
            uncertainty_notes=tuple(map(str, raw.get("uncertainty_notes", ()))),
        )


class TorsoOrientationIntegrityError(ValueError):
    pass


@dataclass(frozen=True)
class TorsoOrientationComparison:
    body_view_mismatch: bool
    torso_turn_mismatch: bool
    near_side_mismatch: bool
    shoulder_width_delta: float
    torso_width_delta: float
    torso_height_delta: float
    near_arm_exposure_delta: float
    far_arm_exposure_delta: float
    contour_owner_overlap: tuple[str, ...]
    integrity: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "img2drawing.torso_orientation_comparison.v1",
            "authority": "evidence_not_pass_fail",
            "body_view_mismatch": self.body_view_mismatch,
            "torso_turn_mismatch": self.torso_turn_mismatch,
            "near_side_mismatch": self.near_side_mismatch,
            "shoulder_width_delta": self.shoulder_width_delta,
            "torso_width_delta": self.torso_width_delta,
            "torso_height_delta": self.torso_height_delta,
            "near_arm_exposure_delta": self.near_arm_exposure_delta,
            "far_arm_exposure_delta": self.far_arm_exposure_delta,
            "contour_owner_overlap": list(self.contour_owner_overlap),
            "integrity": dict(self.integrity),
        }


def compare_torso_orientation(
    reference: TorsoOrientationObservation,
    drawing: TorsoOrientationObservation,
    *,
    current_drawing_state_sha256: str | None = None,
    require_independent: bool = True,
) -> TorsoOrientationComparison:
    reference = reference if isinstance(reference, TorsoOrientationObservation) else TorsoOrientationObservation.from_dict(reference)
    drawing = drawing if isinstance(drawing, TorsoOrientationObservation) else TorsoOrientationObservation.from_dict(drawing)
    errors: list[str] = []
    warnings: list[str] = []
    if reference.source_surface != "reference":
        errors.append("reference orientation must use source_surface='reference'")
    if drawing.source_surface != "drawing":
        errors.append("drawing orientation must use source_surface='drawing'")
    distinct_ids = reference.observation_id != drawing.observation_id
    distinct_artifacts = reference.source_artifact_sha256 != drawing.source_artifact_sha256
    lock_match = reference.observation_lock_digest == drawing.observation_lock_digest
    if not distinct_ids:
        errors.append("orientation observations must use distinct observation_id values")
    if not distinct_artifacts:
        errors.append("orientation observations must use distinct source artifacts")
    if not lock_match:
        errors.append("orientation observations must share the frozen observation lock digest")
    state_current: bool | None = None
    if current_drawing_state_sha256 is None:
        warnings.append("current drawing state was not supplied; staleness could not be checked")
    else:
        current = _digest(current_drawing_state_sha256, "current_drawing_state_sha256")
        state_current = drawing.source_state_sha256 == current
        if not state_current:
            errors.append("drawing orientation evidence is stale for the current drawing state")
    overlap = tuple(sorted(set(reference.contour_owners) & set(drawing.contour_owners)))
    integrity = {
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "distinct_observation_ids": distinct_ids,
        "distinct_source_artifacts": distinct_artifacts,
        "lock_digest_matches": lock_match,
        "drawing_state_current": state_current,
    }
    if require_independent and errors:
        raise TorsoOrientationIntegrityError("; ".join(errors))
    return TorsoOrientationComparison(
        body_view_mismatch=reference.body_view != drawing.body_view,
        torso_turn_mismatch=reference.torso_turn != drawing.torso_turn,
        near_side_mismatch=reference.near_side != drawing.near_side,
        shoulder_width_delta=drawing.shoulder_width - reference.shoulder_width,
        torso_width_delta=drawing.torso_width - reference.torso_width,
        torso_height_delta=drawing.torso_height - reference.torso_height,
        near_arm_exposure_delta=drawing.near_arm_exposure - reference.near_arm_exposure,
        far_arm_exposure_delta=drawing.far_arm_exposure - reference.far_arm_exposure,
        contour_owner_overlap=overlap,
        integrity=integrity,
    )


__all__ = [
    "TorsoOrientationObservation",
    "TorsoOrientationIntegrityError",
    "TorsoOrientationComparison",
    "compare_torso_orientation",
]
