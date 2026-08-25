from __future__ import annotations

"""Pelvis, leg-envelope, and negative-space evidence."""

from dataclasses import dataclass
import re
from typing import Any, Mapping, Sequence

from .envelope import RegionEnvelopeObservation


_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_TURNS = frozenset({"left", "right", "none", "unknown"})
_SUPPORT = frozenset({"leg_A", "leg_B", "unknown"})


def _digest(value: str, label: str) -> str:
    value = str(value).lower()
    if not _SHA256.fullmatch(value):
        raise ValueError(f"{label} must be a 64-character lowercase hex digest")
    return value


def _profile(value: RegionEnvelopeObservation | Mapping[str, Any]) -> RegionEnvelopeObservation:
    return value if isinstance(value, RegionEnvelopeObservation) else RegionEnvelopeObservation.from_dict(value)


def _negative_space(value: Sequence[Sequence[float]]) -> tuple[tuple[float, float], ...]:
    out = tuple((float(t), float(width)) for t, width in value)
    if not 2 <= len(out) <= 16:
        raise ValueError("negative_space_profile must contain 2..16 stations")
    previous = -1.0
    for t, width in out:
        if not 0.0 <= t <= 1.0 or t <= previous:
            raise ValueError("negative-space station t values must be strictly increasing in [0,1]")
        if width < 0.0:
            raise ValueError("negative-space widths must be >= 0")
        previous = t
    return out


@dataclass(frozen=True)
class LowerBodyObservation:
    pelvis_bounds: tuple[float, float, float, float]
    pelvis_turn: str
    leg_a_profile: RegionEnvelopeObservation
    leg_b_profile: RegionEnvelopeObservation
    negative_space_profile: tuple[tuple[float, float], ...]
    support_leg: str
    counterbalance_direction: str
    source_surface: str
    observation_id: str
    source_artifact_sha256: str
    observation_lock_digest: str
    source_state_sha256: str | None = None
    uncertainty_notes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        bounds = tuple(map(float, self.pelvis_bounds))
        if len(bounds) != 4 or not (0.0 <= bounds[0] < bounds[2] <= 1.0 and 0.0 <= bounds[1] < bounds[3] <= 1.0):
            raise ValueError("pelvis_bounds must be ordered inside normalized canvas")
        turn = str(self.pelvis_turn)
        if turn not in _TURNS:
            raise ValueError(f"pelvis_turn must be one of {sorted(_TURNS)}")
        a = _profile(self.leg_a_profile)
        b = _profile(self.leg_b_profile)
        if a.region_id != "leg_A" or b.region_id != "leg_B":
            raise ValueError("lower body profiles must be region_id leg_A and leg_B")
        surface = str(self.source_surface)
        if surface not in {"reference", "drawing"}:
            raise ValueError("source_surface must be reference or drawing")
        if a.source_surface != surface or b.source_surface != surface:
            raise ValueError("leg profiles must use the lower-body source surface")
        parent_artifact = _digest(self.source_artifact_sha256, "source_artifact_sha256")
        parent_lock = _digest(self.observation_lock_digest, "observation_lock_digest")
        if a.source_artifact_sha256 != parent_artifact or b.source_artifact_sha256 != parent_artifact:
            raise ValueError("leg profiles must share the lower-body source artifact")
        if a.observation_lock_digest != parent_lock or b.observation_lock_digest != parent_lock:
            raise ValueError("leg profiles must share the lower-body observation lock digest")
        state = None if self.source_state_sha256 is None else _digest(self.source_state_sha256, "source_state_sha256")
        if surface == "drawing" and state is None:
            raise ValueError("drawing lower-body evidence requires source_state_sha256")
        support = str(self.support_leg)
        if support not in _SUPPORT:
            raise ValueError(f"support_leg must be one of {sorted(_SUPPORT)}")
        counterbalance = str(self.counterbalance_direction)
        if counterbalance not in {"left", "right", "center", "unknown"}:
            raise ValueError("counterbalance_direction must be left, right, center, or unknown")
        object.__setattr__(self, "pelvis_bounds", bounds)
        object.__setattr__(self, "pelvis_turn", turn)
        object.__setattr__(self, "leg_a_profile", a)
        object.__setattr__(self, "leg_b_profile", b)
        object.__setattr__(self, "negative_space_profile", _negative_space(self.negative_space_profile))
        object.__setattr__(self, "support_leg", support)
        object.__setattr__(self, "counterbalance_direction", counterbalance)
        object.__setattr__(self, "source_surface", surface)
        object.__setattr__(self, "observation_id", str(self.observation_id).strip())
        if not self.observation_id:
            raise ValueError("observation_id must be non-empty")
        object.__setattr__(self, "source_artifact_sha256", parent_artifact)
        object.__setattr__(self, "observation_lock_digest", parent_lock)
        object.__setattr__(self, "source_state_sha256", state)
        object.__setattr__(self, "uncertainty_notes", tuple(map(str, self.uncertainty_notes)))

    @property
    def pelvis_width(self) -> float:
        return self.pelvis_bounds[2] - self.pelvis_bounds[0]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "img2drawing.lower_body.v1",
            "pelvis_bounds": list(self.pelvis_bounds),
            "pelvis_turn": self.pelvis_turn,
            "leg_a_profile": self.leg_a_profile.to_dict(),
            "leg_b_profile": self.leg_b_profile.to_dict(),
            "negative_space_profile": [list(item) for item in self.negative_space_profile],
            "support_leg": self.support_leg,
            "counterbalance_direction": self.counterbalance_direction,
            "source_surface": self.source_surface,
            "observation_id": self.observation_id,
            "source_artifact_sha256": self.source_artifact_sha256,
            "observation_lock_digest": self.observation_lock_digest,
            "source_state_sha256": self.source_state_sha256,
            "uncertainty_notes": list(self.uncertainty_notes),
        }

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "LowerBodyObservation":
        if raw.get("schema") not in (None, "img2drawing.lower_body.v1"):
            raise ValueError(f"unsupported lower body schema: {raw.get('schema')!r}")
        return cls(
            pelvis_bounds=tuple(raw["pelvis_bounds"]),
            pelvis_turn=str(raw["pelvis_turn"]),
            leg_a_profile=RegionEnvelopeObservation.from_dict(raw["leg_a_profile"]),
            leg_b_profile=RegionEnvelopeObservation.from_dict(raw["leg_b_profile"]),
            negative_space_profile=tuple(tuple(item) for item in raw["negative_space_profile"]),
            support_leg=str(raw["support_leg"]),
            counterbalance_direction=str(raw["counterbalance_direction"]),
            source_surface=str(raw["source_surface"]),
            observation_id=str(raw["observation_id"]),
            source_artifact_sha256=str(raw["source_artifact_sha256"]),
            observation_lock_digest=str(raw["observation_lock_digest"]),
            source_state_sha256=raw.get("source_state_sha256"),
            uncertainty_notes=tuple(map(str, raw.get("uncertainty_notes", ()))),
        )


class LowerBodyIntegrityError(ValueError):
    pass


@dataclass(frozen=True)
class LowerBodyComparison:
    pelvis_turn_mismatch: bool
    pelvis_width_delta: float
    leg_a_width_deltas: tuple[float, ...]
    leg_b_width_deltas: tuple[float, ...]
    negative_space_deltas: tuple[float, ...]
    support_leg_mismatch: bool
    counterbalance_mismatch: bool
    side_role_mismatch: bool
    integrity: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "img2drawing.lower_body_comparison.v1",
            "authority": "evidence_not_pass_fail",
            "pelvis_turn_mismatch": self.pelvis_turn_mismatch,
            "pelvis_width_delta": self.pelvis_width_delta,
            "leg_a_width_deltas": list(self.leg_a_width_deltas),
            "leg_b_width_deltas": list(self.leg_b_width_deltas),
            "negative_space_deltas": list(self.negative_space_deltas),
            "support_leg_mismatch": self.support_leg_mismatch,
            "counterbalance_mismatch": self.counterbalance_mismatch,
            "side_role_mismatch": self.side_role_mismatch,
            "integrity": dict(self.integrity),
        }


def compare_lower_body(
    reference: LowerBodyObservation,
    drawing: LowerBodyObservation,
    *,
    current_drawing_state_sha256: str | None = None,
    require_independent: bool = True,
) -> LowerBodyComparison:
    reference = reference if isinstance(reference, LowerBodyObservation) else LowerBodyObservation.from_dict(reference)
    drawing = drawing if isinstance(drawing, LowerBodyObservation) else LowerBodyObservation.from_dict(drawing)
    errors: list[str] = []
    warnings: list[str] = []
    if reference.source_surface != "reference" or drawing.source_surface != "drawing":
        errors.append("lower-body observations must use reference and drawing surfaces")
    distinct_ids = reference.observation_id != drawing.observation_id
    distinct_artifacts = reference.source_artifact_sha256 != drawing.source_artifact_sha256
    lock_match = reference.observation_lock_digest == drawing.observation_lock_digest
    if not distinct_ids:
        errors.append("lower-body observations must use distinct observation_id values")
    if not distinct_artifacts:
        errors.append("lower-body observations must use distinct source artifacts")
    if not lock_match:
        errors.append("lower-body observations must share the frozen observation lock digest")
    state_current: bool | None = None
    if current_drawing_state_sha256 is None:
        warnings.append("current drawing state was not supplied; staleness could not be checked")
    else:
        state_current = drawing.source_state_sha256 == _digest(current_drawing_state_sha256, "current_drawing_state_sha256")
        if not state_current:
            errors.append("drawing lower-body evidence is stale for the current drawing state")
    if len(reference.negative_space_profile) != len(drawing.negative_space_profile):
        errors.append("lower-body negative-space profiles must use the same station count")
    if len(reference.leg_a_profile.stations) != len(drawing.leg_a_profile.stations) or len(reference.leg_b_profile.stations) != len(drawing.leg_b_profile.stations):
        errors.append("lower-body leg profiles must use matching station counts")
    if require_independent and errors:
        raise LowerBodyIntegrityError("; ".join(errors))
    leg_a = tuple(
        drawing.leg_a_profile.stations[i].width_local_axis(drawing.leg_a_profile.axis_length)
        - reference.leg_a_profile.stations[i].width_local_axis(reference.leg_a_profile.axis_length)
        for i in range(min(len(reference.leg_a_profile.stations), len(drawing.leg_a_profile.stations)))
    )
    leg_b = tuple(
        drawing.leg_b_profile.stations[i].width_local_axis(drawing.leg_b_profile.axis_length)
        - reference.leg_b_profile.stations[i].width_local_axis(reference.leg_b_profile.axis_length)
        for i in range(min(len(reference.leg_b_profile.stations), len(drawing.leg_b_profile.stations)))
    )
    negative = tuple(
        drawing.negative_space_profile[i][1] - reference.negative_space_profile[i][1]
        for i in range(min(len(reference.negative_space_profile), len(drawing.negative_space_profile)))
    )
    return LowerBodyComparison(
        pelvis_turn_mismatch=reference.pelvis_turn != drawing.pelvis_turn,
        pelvis_width_delta=drawing.pelvis_width - reference.pelvis_width,
        leg_a_width_deltas=leg_a,
        leg_b_width_deltas=leg_b,
        negative_space_deltas=negative,
        support_leg_mismatch=reference.support_leg != drawing.support_leg,
        counterbalance_mismatch=reference.counterbalance_direction != drawing.counterbalance_direction,
        side_role_mismatch=reference.leg_a_profile.side_role != drawing.leg_a_profile.side_role or reference.leg_b_profile.side_role != drawing.leg_b_profile.side_role,
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


__all__ = ["LowerBodyObservation", "LowerBodyIntegrityError", "LowerBodyComparison", "compare_lower_body"]
