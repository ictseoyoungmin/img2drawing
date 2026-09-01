from __future__ import annotations

import json
from pathlib import Path
import warnings

import pytest
from jsonschema import validators

from img2drawing.legacy.r23 import (
    DrawingRun,
    ObservationContract,
    RegionClosureEntry,
    RegionClosureManifest,
    ViewObservation,
)


ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT.parent / "skills" / "img2drawing"
SUBJECT = SKILL_ROOT / "examples" / "full_body_croquis" / "subject.png"
SCHEMAS = ROOT / "schemas"


def _observation() -> ObservationContract:
    return ObservationContract(
        subject_summary="P3 fidelity test subject.",
        view=ViewObservation(
            body_view="back_three_quarter",
            torso_turn="right",
            near_side="image_right",
            arm_visibility={"subject_left": "visible", "subject_right": "partial"},
            arm_occlusion={"subject_left": (), "subject_right": ("prop",)},
        ),
    )


def _run(tmp_path: Path) -> DrawingRun:
    run = DrawingRun.create(
        SUBJECT,
        tmp_path / "run",
        width=96,
        height=144,
        working_supersample=2,
        session_id="test-fidelity",
    )
    run.lock_observation(_observation())
    return run


def _manifest(run: DrawingRun, *, blocker: str | None = None) -> RegionClosureManifest:
    artifacts = run._prepared["P3_primary_masses"]
    regions = []
    for region_id in (
        "head_hair",
        "torso_orientation",
        "near_arm",
        "far_arm",
        "pelvis",
        "leg_A",
        "leg_B",
        "attached_object",
    ):
        revise = region_id == blocker
        regions.append(
            RegionClosureEntry(
                region_id=region_id,
                subject_finding=f"fresh subject finding for {region_id}",
                drawing_finding=f"fresh drawing finding for {region_id}",
                evidence_refs=(f"evidence/{region_id}.json",),
                decision="revise" if revise else "closed",
                blocker=revise,
            )
        )
    return RegionClosureManifest(
        stage="P3_primary_masses",
        drawing_state_sha256=artifacts.drawing.state_sha256,
        drawing_artifact_sha256=artifacts.drawing.artifact_sha256,
        history_cursor=artifacts.drawing.history_cursor,
        observation_lock_digest=run.observation_lock.observation_digest,
        regions=tuple(regions),
        evaluator_id="blind-evaluator-01",
    )


def _start_p3(run: DrawingRun) -> None:
    run.progress.current_index = 2
    run.stage_start("P3_primary_masses")
    run.prepare_stage_review()


def test_manifest_requires_all_regions_and_rationale_basis():
    with pytest.raises(ValueError, match="exactly eight"):
        RegionClosureManifest(
            stage="P3_primary_masses",
            drawing_state_sha256="a" * 64,
            drawing_artifact_sha256="b" * 64,
            history_cursor=0,
            observation_lock_digest="c" * 64,
            regions=(),
            evaluator_id="evaluator",
        )
    with pytest.raises(ValueError, match="uncertainty or occlusion"):
        RegionClosureEntry(
            region_id="near_arm",
            subject_finding="subject",
            drawing_finding="drawing",
            evidence_refs=("evidence.json",),
            decision="accept-with-rationale",
            rationale="not enough detail",
            rationale_basis=("preference",),
        )


def test_p3_dual_gate_blocks_without_visual_pass_and_then_advances(tmp_path: Path):
    run = _run(tmp_path)
    _start_p3(run)
    manifest = _manifest(run, blocker="near_arm")
    with pytest.raises(RuntimeError, match="independent region closure"):
        run.submit_stage_review(
            contract_findings=("process contract is complete",),
            subject_findings=("subject was observed",),
            grammar_findings=("exemplar is not a visual authority",),
            drawing_findings=("drawing process is complete",),
            decision="advance",
            advance_rationale="process only",
        )

    run.submit_region_closure_manifest(manifest)
    packet = run.blind_visual_packet
    assert packet is not None
    assert "worker_rationale" not in packet
    assert "exemplar_verdict" not in packet
    with pytest.raises(RuntimeError, match="region blockers"):
        run.submit_visual_fidelity_review(
            evaluator_id="blind-evaluator-01",
            findings=("near arm remains too thin",),
            decision="advance",
            rationale="visual check",
        )

    # A fresh pass is required after the visual revision; the old manifest is not
    # silently promoted to an advance decision.
    run.prepare_stage_review()
    valid_manifest = _manifest(run)
    run.submit_region_closure_manifest(valid_manifest)
    visual = run.submit_visual_fidelity_review(
        evaluator_id="blind-evaluator-02",
        findings=("all eight regions independently reviewed",),
        decision="advance",
        rationale="No unresolved region blocker remains in this fixture.",
    )
    assert visual.decision == "advance"
    run.submit_stage_review(
        contract_findings=("P3 process contract is complete",),
        subject_findings=("fresh subject findings are present for all regions",),
        grammar_findings=("exemplar verdict is excluded from visual packet",),
        drawing_findings=("drawing artifact is bound to the current cursor",),
        decision="advance",
        advance_rationale="Process PASS and independent visual PASS are both present.",
    )
    assert run.current_stage == "P4_structural_connections"


def test_non_p3_stage_progression_is_unchanged(tmp_path: Path):
    run = _run(tmp_path)
    run.stage_start("P1_gesture")
    run.prepare_stage_review()
    run.submit_stage_review(
        observations=("P1 gesture contract and fresh drawing evidence are complete",),
        decision="advance",
        advance_rationale="P1 process review is complete.",
    )
    assert run.current_stage == "P2_primary_axes"


def test_fidelity_records_checkpoint_and_schema_roundtrip(tmp_path: Path):
    run = _run(tmp_path)
    _start_p3(run)
    manifest = _manifest(run)
    run.submit_region_closure_manifest(manifest)
    visual = run.submit_visual_fidelity_review(
        evaluator_id="blind-evaluator-01",
        findings=("visual record roundtrip",),
        decision="advance",
        rationale="fixture is complete",
    )
    resumed = DrawingRun.resume(run.output_dir)
    assert resumed.region_closure_manifest is not None
    assert resumed.region_closure_manifest.digest() == manifest.digest()
    assert resumed.visual_fidelity_review is not None
    assert resumed.visual_fidelity_review.digest() == visual.digest()
    checkpoint = json.loads((run.output_dir / "session" / "checkpoint.json").read_text())
    assert checkpoint["schema"] == "img2drawing.run_checkpoint.v3"

    schemas = [
        ("region_closure.schema.json", manifest.to_dict()),
        ("visual_fidelity_review.schema.json", visual.to_dict()),
        ("blind_visual_packet.schema.json", run.blind_visual_packet),
    ]
    for filename, payload in schemas:
        schema = json.loads((SCHEMAS / filename).read_text())
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            validator = validators.validator_for(schema)(schema)
        validator.validate(payload)
