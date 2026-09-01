from __future__ import annotations

import json
from pathlib import Path
import warnings

import pytest
from jsonschema import validators

from img2drawing.legacy.r23 import HeadHairIntegrityError, HeadHairObservation, compare_head_hair


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas" / "head_hair.schema.json"
LOCK = "d" * 64
STATE = "e" * 64


def _head(surface: str, artifact: str, *, large: bool = False, state: str | None = None) -> HeadHairObservation:
    return HeadHairObservation(
        head_top=(0.50, 0.08),
        chin=(0.50, 0.25),
        cranial_left=(0.42, 0.14),
        cranial_right=(0.58, 0.14),
        jaw_left=(0.45, 0.22),
        jaw_right=(0.55, 0.22),
        head_bounds=(0.40, 0.08, 0.60, 0.27) if not large else (0.33, 0.05, 0.67, 0.32),
        hair_bounds=(0.38, 0.06, 0.62, 0.30) if not large else (0.30, 0.02, 0.70, 0.36),
        hair_style="bob",
        hair_occlusion=("left_jaw", "right_jaw"),
        anatomical_uncertainty=("chin partly hidden by hair",),
        source_surface=surface,
        observation_id=f"{surface}-head-01",
        source_artifact_sha256=artifact,
        observation_lock_digest=LOCK,
        source_state_sha256=state if surface == "drawing" else None,
    )


def test_bob_fixture_surfaces_overlarge_head_without_features():
    reference = _head("reference", "a" * 64)
    drawing = _head("drawing", "b" * 64, large=True, state=STATE)
    comparison = compare_head_hair(reference, drawing, current_drawing_state_sha256=STATE)
    assert comparison.head_width_delta > 0.1
    assert comparison.hair_width_delta > 0.1
    assert comparison.to_dict()["authority"] == "evidence_not_pass_fail"


def test_head_hair_provenance_and_stale_state_fail_closed():
    reference = _head("reference", "a" * 64)
    same_artifact = _head("drawing", "a" * 64, state=STATE)
    with pytest.raises(HeadHairIntegrityError, match="distinct source artifacts"):
        compare_head_hair(reference, same_artifact, current_drawing_state_sha256=STATE)
    drawing = _head("drawing", "b" * 64, state=STATE)
    with pytest.raises(HeadHairIntegrityError, match="stale"):
        compare_head_hair(reference, drawing, current_drawing_state_sha256="c" * 64)


def test_head_hair_roundtrip_schema():
    reference = _head("reference", "a" * 64)
    assert HeadHairObservation.from_dict(reference.to_dict()) == reference
    schema = json.loads(SCHEMA.read_text())
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        validator = validators.validator_for(schema)(schema)
    validator.validate(reference.to_dict())
