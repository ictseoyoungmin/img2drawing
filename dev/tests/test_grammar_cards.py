from __future__ import annotations

import json
from pathlib import Path

import pytest

from img2drawing.legacy.r23 import DrawingRun, ModularGrammarCard, ObservationContract, ViewObservation


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT.parent / "skills" / "img2drawing"
SUBJECT = SKILL_ROOT / "examples" / "full_body_croquis" / "subject.png"

CARDS = tuple(
    ModularGrammarCard(
        card_id=f"test-{stage}",
        stage=stage,
        polarity="positive",
        scope=("representation",),
        transfer_mapping=("subject endpoints",),
        source_audit_status="pass",
    )
    for stage in ("P1_gesture", "P2_primary_axes", "P3_primary_masses", "P4_structural_connections", "P5_clean_blockin")
)


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


def test_modular_cards_bind_to_action_provenance_and_worker_packet(tmp_path: Path):
    run = DrawingRun.create(
        SUBJECT,
        tmp_path / "cards",
        width=96,
        height=144,
        working_supersample=2,
        session_id="test-modular-card-binding",
        grammar_cards=CARDS,
        require_grammar_card_bindings=True,
    )
    run.lock_observation(
        ObservationContract(
            subject_summary="Card binding test subject.",
            view=ViewObservation(
                body_view="unknown",
                torso_turn="unknown",
                near_side="unknown",
                arm_visibility={"subject_left": "unknown", "subject_right": "unknown"},
                arm_occlusion={"subject_left": (), "subject_right": ()},
            ),
        )
    )
    run.stage_start("P1_gesture")
    run.draw({
        "action_id": "card-bound-stroke",
        "kind": "draw_stroke",
        "stage": "P1_gesture",
        "role": "gesture",
        "part": "card_test",
        "points": [[20, 20], [32, 48], [44, 80]],
        "stroke_id": "card_test",
        "tool": {"preset": "construction_pencil", "grade": "HB", "overrides": {"pressure": 0.3, "width": 1.2, "opacity": 0.4}},
        "observation_id": "card-test-observation",
        "source_observation": "Card binding test observation.",
    })
    event = run.session.history.to_dict()["actions"][-1]
    binding = event["provenance"]["metadata"]
    assert binding["grammar_card_ids"] == ["test-P1_gesture"]
    assert binding["grammar_card"]["stage"] == "P1_gesture"
    run.prepare_stage_review()
    packet = _packet(run)
    assert packet["grammar_cards"][0]["card_id"] == "test-P1_gesture"
    resumed = DrawingRun.resume(run.output_dir)
    assert resumed.require_grammar_card_bindings is True
    assert resumed.grammar_cards[0]["card_id"] == "test-P1_gesture"


def test_run_exposes_explicit_card_stroke_plan_consumption(tmp_path: Path):
    run = DrawingRun.create(
        SUBJECT,
        tmp_path / "card-plan",
        width=96,
        height=144,
        working_supersample=2,
        session_id="test-card-stroke-plan",
        grammar_cards=CARDS,
        require_grammar_card_bindings=True,
    )
    card = run.grammar_card_for_stage("P3_primary_masses")
    assert card["card_id"] == "test-P3_primary_masses"
    card["transfer_mapping"].append("caller annotation")
    assert run.grammar_card_for_stage("P3_primary_masses")["transfer_mapping"] == ["subject endpoints"]

    plan = run.consume_grammar_card("P3_primary_masses", part="torso", role="mass")
    assert plan["card_id"] == "test-P3_primary_masses"
    assert plan["transfer_tokens"][0]["mapping"] == "subject endpoints"
    assert all("points" not in token for token in plan["transfer_tokens"])

    with pytest.raises(RuntimeError, match="no grammar card"):
        _run(tmp_path, 0, "unbound-card-plan").consume_grammar_card("P1_gesture")


def test_strict_modular_card_binding_requires_one_card_per_stage(tmp_path: Path):
    with pytest.raises(ValueError, match="exactly one card per stage"):
        DrawingRun.create(
            SUBJECT,
            tmp_path / "missing",
            width=96,
            height=144,
            working_supersample=2,
            session_id="test-modular-card-missing-stage",
            grammar_cards=CARDS[:1],
            require_grammar_card_bindings=True,
        )
