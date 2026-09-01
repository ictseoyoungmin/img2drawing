from __future__ import annotations

import json
from pathlib import Path
import warnings

import pytest
from jsonschema import validators

from img2drawing.legacy.r23 import (
    EnvelopeStation,
    LowerBodyIntegrityError,
    LowerBodyObservation,
    RegionEnvelopeObservation,
    compare_lower_body,
)


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas" / "lower_body.schema.json"
LOCK = "d" * 64
STATE = "e" * 64


def _leg(region_id: str, surface: str, artifact: str, widths: tuple[float, ...], side: str) -> RegionEnvelopeObservation:
    stations = tuple(
        EnvelopeStation(
            t=t,
            contour_a=(0.32 if region_id == "leg_A" else 0.61, 0.55 + t * 0.35),
            contour_b=((0.32 if region_id == "leg_A" else 0.61) + width, 0.55 + t * 0.35),
        )
        for t, width in zip((0.2, 0.5, 0.8), widths)
    )
    return RegionEnvelopeObservation(
        region_id=region_id,
        side_role=side,
        axis_start=(0.32 if region_id == "leg_A" else 0.61, 0.55),
        axis_end=(0.34 if region_id == "leg_A" else 0.63, 0.90),
        stations=stations,
        visible_fraction=1.0,
        occlusion=(),
        source_surface=surface,
        observation_id=f"{surface}-lower-01",
        source_artifact_sha256=artifact,
        observation_lock_digest=LOCK,
        source_state_sha256=STATE if surface == "drawing" else None,
    )


def _lower(surface: str, artifact: str, *, rail: bool = False, support: str = "leg_A") -> LowerBodyObservation:
    return LowerBodyObservation(
        pelvis_bounds=(0.25, 0.42, 0.72, 0.57),
        pelvis_turn="right",
        leg_a_profile=_leg("leg_A", surface, artifact, (0.12, 0.09, 0.06) if not rail else (0.08, 0.08, 0.08), "near"),
        leg_b_profile=_leg("leg_B", surface, artifact, (0.10, 0.08, 0.05) if not rail else (0.08, 0.08, 0.08), "far"),
        negative_space_profile=((0.2, 0.16), (0.5, 0.12), (0.8, 0.10)) if not rail else ((0.2, 0.04), (0.5, 0.04), (0.8, 0.04)),
        support_leg=support,
        counterbalance_direction="left",
        source_surface=surface,
        observation_id=f"{surface}-lower-01",
        source_artifact_sha256=artifact,
        observation_lock_digest=LOCK,
        source_state_sha256=STATE if surface == "drawing" else None,
    )


def test_parallel_rails_and_negative_space_are_evidence():
    reference = _lower("reference", "a" * 64)
    drawing = _lower("drawing", "b" * 64, rail=True, support="leg_B")
    comparison = compare_lower_body(reference, drawing, current_drawing_state_sha256=STATE)
    assert comparison.leg_a_width_deltas[1] < 0
    assert comparison.negative_space_deltas[0] < 0
    assert comparison.support_leg_mismatch
    assert comparison.to_dict()["authority"] == "evidence_not_pass_fail"


def test_lower_body_provenance_and_state_fail_closed():
    reference = _lower("reference", "a" * 64)
    same_artifact = _lower("drawing", "a" * 64)
    with pytest.raises(LowerBodyIntegrityError, match="distinct source artifacts"):
        compare_lower_body(reference, same_artifact, current_drawing_state_sha256=STATE)
    drawing = _lower("drawing", "b" * 64)
    with pytest.raises(LowerBodyIntegrityError, match="stale"):
        compare_lower_body(reference, drawing, current_drawing_state_sha256="c" * 64)


def test_lower_body_roundtrip_schema():
    reference = _lower("reference", "a" * 64)
    restored = LowerBodyObservation.from_dict(reference.to_dict())
    assert restored == reference
    schema = json.loads(SCHEMA.read_text())
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        validator = validators.validator_for(schema)(schema)
    validator.validate(reference.to_dict())
