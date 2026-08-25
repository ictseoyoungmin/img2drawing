from __future__ import annotations

import json
from pathlib import Path
import time
import warnings

import pytest
from jsonschema import validators

from img2drawing import (
    TorsoOrientationIntegrityError,
    TorsoOrientationObservation,
    compare_torso_orientation,
)


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas" / "torso_orientation.schema.json"
LOCK = "d" * 64
STATE = "e" * 64


def _orientation(*, surface: str, view: str, near_exposure: float, artifact: str, state: str | None = None) -> TorsoOrientationObservation:
    return TorsoOrientationObservation(
        body_view=view,
        torso_turn="right",
        near_side="image_right",
        left_shoulder=(0.30, 0.28),
        right_shoulder=(0.62, 0.31),
        torso_bounds=(0.28, 0.28, 0.66, 0.62),
        near_arm_exposure=near_exposure,
        far_arm_exposure=0.35,
        contour_owners=("torso_orientation", "near_arm", "far_arm"),
        source_surface=surface,
        observation_id=f"{surface}-torso-01",
        source_artifact_sha256=artifact,
        observation_lock_digest=LOCK,
        source_state_sha256=state if surface == "drawing" else None,
        uncertainty_notes=("shoulder contour partly merges with jacket",),
    )


def test_width_match_but_orientation_and_near_arm_drift_are_evidence():
    reference = _orientation(surface="reference", view="side", near_exposure=0.90, artifact="a" * 64)
    drawing = _orientation(surface="drawing", view="back_three_quarter", near_exposure=0.22, artifact="b" * 64, state=STATE)
    comparison = compare_torso_orientation(reference, drawing, current_drawing_state_sha256=STATE)
    assert comparison.body_view_mismatch
    assert comparison.near_arm_exposure_delta < -0.6
    assert abs(comparison.torso_width_delta) < 1e-9
    assert comparison.to_dict()["authority"] == "evidence_not_pass_fail"


def test_orientation_provenance_and_stale_state_fail_closed():
    reference = _orientation(surface="reference", view="side", near_exposure=0.9, artifact="a" * 64)
    drawing = _orientation(surface="drawing", view="side", near_exposure=0.9, artifact="a" * 64, state=STATE)
    with pytest.raises(TorsoOrientationIntegrityError, match="distinct source artifacts"):
        compare_torso_orientation(reference, drawing, current_drawing_state_sha256=STATE)
    drawing = _orientation(surface="drawing", view="side", near_exposure=0.9, artifact="b" * 64, state=STATE)
    with pytest.raises(TorsoOrientationIntegrityError, match="stale"):
        compare_torso_orientation(reference, drawing, current_drawing_state_sha256="c" * 64)


def test_orientation_roundtrip_schema_and_budget():
    reference = _orientation(surface="reference", view="side", near_exposure=0.9, artifact="a" * 64)
    drawing = _orientation(surface="drawing", view="side", near_exposure=0.9, artifact="b" * 64, state=STATE)
    restored = TorsoOrientationObservation.from_dict(reference.to_dict())
    assert restored == reference
    schema = json.loads(SCHEMA.read_text())
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        validator = validators.validator_for(schema)(schema)
    validator.validate(reference.to_dict())
    start = time.perf_counter()
    for _ in range(1000):
        compare_torso_orientation(reference, drawing, current_drawing_state_sha256=STATE)
    assert time.perf_counter() - start < 0.1
