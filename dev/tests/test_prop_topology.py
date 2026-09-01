from __future__ import annotations

import json
from pathlib import Path
import warnings

import pytest
from jsonschema import validators

from img2drawing.legacy.r23 import (
    PropBodyOverlapPoint,
    PropTerminalMass,
    PropTopologyIntegrityError,
    PropTopologyObservation,
    PropWidthChangePoint,
    compare_prop_topology,
)


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas" / "prop_topology.schema.json"
LOCK = "d" * 64
STATE = "e" * 64


def _prop(surface: str, artifact: str, *, prop_id: str = "rifle", narrow: bool = False, state: str | None = None) -> PropTopologyObservation:
    widths = (0.10, 0.06, 0.03) if not narrow else (0.10, 0.10, 0.10)
    return PropTopologyObservation(
        prop_id=prop_id,
        major_axis_start=(0.20, 0.10),
        major_axis_end=(0.75, 0.72),
        width_change_points=tuple(PropWidthChangePoint(t, width, label) for t, width, label in ((0.1, widths[0], "front"), (0.5, widths[1], "body"), (0.9, widths[2], "terminal"))),
        terminal_masses=(
            PropTerminalMass("front_mass", (0.20, 0.10), 0.04),
            PropTerminalMass("rear_mass", (0.75, 0.72), 0.03),
        ),
        body_overlap_points=(PropBodyOverlapPoint("body_overlap", (0.48, 0.42), "torso", 1),),
        visible_interruptions=("torso_occlusion",),
        occlusion_order=("prop", "torso", "near_arm"),
        source_surface=surface,
        observation_id=f"{surface}-prop-01",
        source_artifact_sha256=artifact,
        observation_lock_digest=LOCK,
        source_state_sha256=state if surface == "drawing" else None,
    )


def test_rifle_and_non_rifle_share_generic_topology_api():
    rifle = _prop("reference", "a" * 64, prop_id="rifle")
    guitar = _prop("reference", "b" * 64, prop_id="guitar")
    assert rifle.to_dict()["schema"] == guitar.to_dict()["schema"]
    assert rifle.to_dict()["width_change_points"]


def test_gross_axis_match_but_width_and_overlap_drift_are_evidence():
    reference = _prop("reference", "a" * 64)
    drawing = _prop("drawing", "b" * 64, narrow=True, state=STATE)
    comparison = compare_prop_topology(reference, drawing, current_drawing_state_sha256=STATE)
    assert comparison.axis_start_delta == 0.0
    assert comparison.width_deltas[1] > 0.0
    assert comparison.to_dict()["authority"] == "evidence_not_pass_fail"


def test_prop_provenance_and_stale_state_fail_closed():
    reference = _prop("reference", "a" * 64)
    same_artifact = _prop("drawing", "a" * 64, state=STATE)
    with pytest.raises(PropTopologyIntegrityError, match="distinct source artifacts"):
        compare_prop_topology(reference, same_artifact, current_drawing_state_sha256=STATE)
    drawing = _prop("drawing", "b" * 64, state=STATE)
    with pytest.raises(PropTopologyIntegrityError, match="stale"):
        compare_prop_topology(reference, drawing, current_drawing_state_sha256="c" * 64)


def test_prop_roundtrip_schema():
    reference = _prop("reference", "a" * 64)
    assert PropTopologyObservation.from_dict(reference.to_dict()) == reference
    schema = json.loads(SCHEMA.read_text())
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        validator = validators.validator_for(schema)(schema)
    validator.validate(reference.to_dict())
