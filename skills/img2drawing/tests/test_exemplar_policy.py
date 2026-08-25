from __future__ import annotations

import json
from pathlib import Path

from img2drawing import DrawingRun, ObservationContract, ViewObservation


ROOT = Path(__file__).resolve().parents[1]
SUBJECT = ROOT / "examples" / "full_body_croquis" / "subject.png"


def _run(tmp_path: Path, stage_index: int, suffix: str) -> DrawingRun:
    run = DrawingRun.create(
        SUBJECT,
        tmp_path / suffix,
        width=96,
        height=144,
        working_supersample=2,
        session_id=f"test-exemplar-{suffix}",
    )
    run.lock_observation(
        ObservationContract(
            subject_summary="Exemplar policy test subject.",
            view=ViewObservation(
                body_view="unknown",
                torso_turn="unknown",
                near_side="unknown",
                arm_visibility={"subject_left": "unknown", "subject_right": "unknown"},
                arm_occlusion={"subject_left": (), "subject_right": ()},
            ),
        )
    )
    run.progress.current_index = stage_index
    run.stage_start(run.stage_specs[stage_index].stage_id)
    run.prepare_stage_review()
    return run


def _packet(run: DrawingRun) -> dict:
    return json.loads(
        next((run.output_dir / "reviews").glob("*/pass_01/worker_packet.json")).read_text()
    )


def test_fail_exemplar_is_negative_warning_only(tmp_path: Path):
    run = _run(tmp_path, 0, "p1")
    packet = _packet(run)
    artifacts = run._prepared["P1_gesture"]
    assert artifacts.grammar_vs_drawing is None
    assert packet["references"]["grammar_exemplar"]["mandatory_path_policy"] == "negative_reference_warning_only"
    assert "grammar_vs_drawing" not in packet["mandatory_review_views"]
    assert "grammar_exemplar_negative_warning" in packet["mandatory_review_views"]
    assert packet["artifacts"]["grammar_vs_drawing"] is None


def test_p2_pass_exemplar_remains_positive_control(tmp_path: Path):
    run = _run(tmp_path, 1, "p2")
    packet = _packet(run)
    artifacts = run._prepared["P2_primary_axes"]
    assert artifacts.grammar_vs_drawing is not None
    assert packet["references"]["grammar_exemplar"]["mandatory_path_policy"] == "mandatory_positive_reference"
    assert "grammar_vs_drawing" in packet["mandatory_review_views"]


def test_p3_exemplar_is_marked_unproven_until_ablation(tmp_path: Path):
    run = _run(tmp_path, 2, "p3")
    packet = _packet(run)
    audit = json.loads(
        next((run.output_dir / "reviews").glob("*/pass_01/grammar_exemplar_audit.json")).read_text()
    )
    assert packet["references"]["grammar_exemplar"]["mandatory_path_policy"] == "unproven_until_ablation"
    assert packet["artifacts"]["grammar_exemplar_policy"] == "unproven_until_ablation"
    assert audit["mandatory_path_policy"] == "unproven_until_ablation"
    assert "grammar_vs_drawing" not in packet["mandatory_review_views"]
    assert "grammar_exemplar_unproven_warning" in packet["mandatory_review_views"]
