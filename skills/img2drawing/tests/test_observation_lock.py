from __future__ import annotations

import json
import warnings
from pathlib import Path

import pytest
from jsonschema import RefResolver, validators

from img2drawing import (
    DrawingRun,
    FrozenObservationRecord,
    ObservationContract,
    ViewObservation,
)


ROOT = Path(__file__).resolve().parents[1]
SUBJECT = ROOT / "examples" / "full_body_croquis" / "subject.png"
SCHEMA_DIR = ROOT / "schemas"


def _observation(*, body_view="back_three_quarter") -> ObservationContract:
    return ObservationContract(
        subject_summary="A subject-only observation used to test the run lock.",
        global_relations={"torso_to_pelvis": "turns"},
        view=ViewObservation(
            body_view=body_view,
            torso_turn="right",
            near_side="image_right",
            arm_visibility={
                "subject_left": "visible",
                "subject_right": "partial",
            },
            arm_occlusion={
                "subject_left": (),
                "subject_right": ("prop",),
            },
            prop_overlap_order=("prop", "torso", "near_arm"),
            uncertainties=("far arm boundary is partly occluded",),
        ),
    )


def _run(tmp_path: Path) -> DrawingRun:
    return DrawingRun.create(
        SUBJECT,
        tmp_path / "run",
        width=128,
        height=192,
        working_supersample=2,
        session_id="test-observation-lock",
    )


def _draw_action() -> dict:
    return {
        "action_id": "test-p1-stroke",
        "kind": "draw_stroke",
        "stage": "P1_gesture",
        "role": "gesture",
        "part": "test_gesture",
        "points": [[20, 20], [32, 48], [44, 80]],
        "stroke_id": "test_gesture",
        "confidence": 0.9,
        "layer": 10,
        "tool": {
            "preset": "construction_pencil",
            "grade": "HB",
            "overrides": {"pressure": 0.3, "width": 1.2, "opacity": 0.4},
        },
        "observation_id": "test-observation",
        "source_observation": "Test subject observation.",
    }


def test_frozen_record_clones_nested_observation_input():
    arm_visibility = {"subject_left": "visible", "subject_right": "partial"}
    observation = ObservationContract(
        subject_summary="copy test",
        view=ViewObservation(
            arm_visibility=arm_visibility,
            arm_occlusion={"subject_left": (), "subject_right": ()},
        ),
    )
    record = FrozenObservationRecord.create(
        observation,
        subject_reference_sha256="a" * 64,
        observation_id="copy-test",
        locked_at_cursor=0,
        locked_at_stage="P1_gesture",
    )
    arm_visibility["subject_left"] = "occluded"
    assert record.observation.view is not None
    assert record.observation.view.arm_visibility["subject_left"] == "visible"
    assert record.observation_digest == FrozenObservationRecord.from_dict(record.to_dict()).observation_digest


def test_stage_start_requires_a_pre_draw_lock(tmp_path: Path):
    run = _run(tmp_path)
    with pytest.raises(RuntimeError, match="observation lock"):
        run.stage_start("P1_gesture")


def test_lock_requires_complete_arm_visibility_and_occlusion(tmp_path: Path):
    run = _run(tmp_path)
    incomplete = ObservationContract(
        subject_summary="incomplete view",
        view=ViewObservation(),
    )
    with pytest.raises(ValueError, match="visibility"):
        run.lock_observation(incomplete)


def test_malformed_view_role_is_rejected():
    with pytest.raises(ValueError, match="body_view"):
        ViewObservation(body_view="rear-ish")


def test_subject_hash_mismatch_is_rejected():
    observation = _observation()
    with pytest.raises(ValueError, match="observation_digest"):
        FrozenObservationRecord(
            observation=observation,
            subject_reference_sha256="a" * 64,
            observation_id="hash-mismatch",
            locked_at_cursor=0,
            locked_at_stage="P1_gesture",
            observation_digest="b" * 64,
        )


def test_duplicate_lock_requires_explicit_reopen(tmp_path: Path):
    run = _run(tmp_path)
    run.lock_observation(_observation())
    with pytest.raises(RuntimeError, match="already locked"):
        run.lock_observation(_observation())


def test_lock_persists_and_resumes(tmp_path: Path):
    run = _run(tmp_path)
    record = run.lock_observation(_observation())
    persisted = json.loads(
        (run.output_dir / "observation" / "pre_draw_observation.json").read_text()
    )
    assert persisted["observation_digest"] == record.observation_digest

    resumed = DrawingRun.resume(run.output_dir)
    assert resumed.observation_lock is not None
    assert resumed.observation_lock.observation_digest == record.observation_digest
    assert resumed.observation_lock.observation.view == record.observation.view
    checkpoint = json.loads((run.output_dir / "session" / "checkpoint.json").read_text())
    assert checkpoint["schema"] in {
        "img2drawing.run_checkpoint.v2",
        "img2drawing.run_checkpoint.v3",
    }
    assert len(json.dumps(record.to_dict(), ensure_ascii=False).encode("utf-8")) <= 64 * 1024


def test_stale_checkpoint_lock_is_rejected_on_resume(tmp_path: Path):
    run = _run(tmp_path)
    run.lock_observation(_observation())
    checkpoint_path = run.output_dir / "session" / "checkpoint.json"
    checkpoint = json.loads(checkpoint_path.read_text())
    checkpoint["observation_lock"]["observation_digest"] = "c" * 64
    checkpoint_path.write_text(json.dumps(checkpoint), encoding="utf-8")
    with pytest.raises(ValueError, match="observation_digest"):
        DrawingRun.resume(run.output_dir)


def test_observation_replacement_reopens_p1_and_invalidates_branch(tmp_path: Path):
    run = _run(tmp_path)
    first = run.lock_observation(_observation())
    run.stage_start("P1_gesture")
    run.draw(_draw_action())

    replacement = _observation(body_view="side")
    reopen = run.reopen_observation(
        reason="fresh observation changes the body-view classification",
        replacement=replacement,
    )

    assert reopen.previous_observation_digest == first.observation_digest
    assert reopen.replacement_observation_digest == run.observation_lock.observation_digest
    assert "P1_gesture" in reopen.invalidated_stages
    assert run.current_stage == "P1_gesture"
    assert run.observation_reopens == (reopen,)
    assert (run.output_dir / "observation" / "observation_reopens.json").exists()


def test_legacy_checkpoint_requires_explicit_p1_adoption(tmp_path: Path):
    run = _run(tmp_path)
    run.lock_observation(_observation())
    run.stage_start("P1_gesture")
    checkpoint_path = run.output_dir / "session" / "checkpoint.json"
    legacy = json.loads(checkpoint_path.read_text())
    legacy.pop("observation_lock", None)
    legacy.pop("observation_reopens", None)
    legacy["schema"] = "img2drawing.run_checkpoint.v1"
    checkpoint_path.write_text(json.dumps(legacy), encoding="utf-8")

    resumed = DrawingRun.resume(run.output_dir)
    assert resumed.observation_lock is None
    with pytest.raises(RuntimeError, match="observation lock"):
        resumed.stage_start("P1_gesture")

    resumed.reopen_stage(
        "P1_gesture",
        reason="adopt a legacy run into the frozen observation protocol",
    )
    adopted = resumed.lock_observation(_observation())
    assert "legacy-adoption" in adopted.observation_id


def test_lock_and_observation_schemas_validate(tmp_path: Path):
    run = _run(tmp_path)
    record = run.lock_observation(_observation())
    observation_schema = json.loads((SCHEMA_DIR / "observation.schema.json").read_text())
    lock_schema = json.loads((SCHEMA_DIR / "observation_lock.schema.json").read_text())
    resolver = RefResolver.from_schema(
        lock_schema,
        store={
            "observation.schema.json": observation_schema,
            observation_schema["$id"]: observation_schema,
        },
    )
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        validator_type = validators.validator_for(lock_schema)
    validator_type.check_schema(lock_schema)
    validator_type(lock_schema, resolver=resolver).validate(record.to_dict())
