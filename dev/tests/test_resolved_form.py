from __future__ import annotations

import json
from pathlib import Path

import pytest
from jsonschema import validators

from img2drawing import (
    DrawingAction, DrawingRun, ObservationContract, ViewObservation,
    ResolvedFormEntry, ResolvedFormManifest, IdentityFinishProfile,
    IdentityFinishManifest, ConstructionRetirementRecord,
    AssistiveROIProposal, ExcludedRegion, AcceptedResidual, AdaptiveEvidencePolicy,
)


ROOT = Path(__file__).resolve().parents[1]
SUBJECT = ROOT.parent / "skills" / "img2drawing" / "examples" / "full_body_croquis" / "subject.png"


def _obs() -> ObservationContract:
    return ObservationContract(
        subject_summary="Resolved-form fixture subject.",
        view=ViewObservation(
            body_view="front_three_quarter", torso_turn="right", near_side="image_right",
            arm_visibility={"subject_left": "visible", "subject_right": "visible"},
            arm_occlusion={"subject_left": (), "subject_right": ()},
        ),
    )


def _action(stage: str, aid: str) -> dict:
    return {
        "action_id": aid, "kind": "draw_stroke", "stage": stage,
        "role": "form", "part": aid, "points": [[20, 20], [42, 38], [64, 24]],
        "stroke_id": aid, "tool": {"preset": "form_pencil", "grade": "HB", "overrides": {"pressure": .58, "width": 1.8, "opacity": .62, "taper_in": .4, "taper_out": .5}},
        "pressure": [.22, .58, .18], "observation_id": "fixture-observation", "source_observation": "Fresh fixture observation.",
    }


def _run(tmp_path: Path) -> DrawingRun:
    run = DrawingRun.create(SUBJECT, tmp_path / "run", width=96, height=144, working_supersample=2, stage_registry="full_body_croquis_with_p6")
    run.lock_observation(_obs())
    return run


def _resolved_manifest(run: DrawingRun, stage: str) -> ResolvedFormManifest:
    artifacts = run._prepared[stage]
    regions = tuple(
        ResolvedFormEntry(
            region_id=region, subject_finding=f"subject fact {region}", drawing_finding=f"drawing fact {region}",
            evidence_refs=(f"reviews/{stage}/{region}.json",), decision="closed",
        )
        for region in (run._resolved_form_packets[stage]["stage_contract"].get("owns") and (
            ("head_hair_connection", "face_opening", "torso_garment_hang", "near_arm_joint_chain", "far_arm_joint_chain", "waist_leg_openings", "footwear_connection", "attached_object_structure")
            if stage.startswith("P4") else
            ("face_feature_scaffold", "hair_silhouette_grouping", "garment_contour_and_folds", "joint_contour_continuity", "hands_and_footwear", "prop_final_topology", "contour_ownership", "construction_retirement_and_line_hierarchy")
        ))
    )
    return ResolvedFormManifest(
        stage=stage, drawing_state_sha256=artifacts.drawing.state_sha256,
        drawing_artifact_sha256=artifacts.drawing.artifact_sha256, history_cursor=artifacts.drawing.history_cursor,
        observation_lock_digest=run.observation_lock.observation_digest, regions=regions,
        evaluator_id="fresh-blind-fixture", blind_packet_digest=run._resolved_form_packets[stage]["packet_digest"],
    )


def _advance_stage(run: DrawingRun, stage: str) -> None:
    run.stage_start(stage)
    run.draw(_action(stage, f"draw-{stage}"))
    run.prepare_stage_review()
    manifest = _resolved_manifest(run, stage)
    run.submit_resolved_form_manifest(manifest)
    run.submit_resolved_form_review(manifest=manifest, evaluator_id="fresh-blind-fixture", findings=("fresh whole-view and crop inspection",), decision="advance", rationale="all resolved-form regions are closed")
    run.submit_stage_review(observations=(f"{stage} process contract is complete",), decision="advance", advance_rationale="process and independent visual gates agree")


def test_resolved_form_requires_visual_gate_and_roundtrips(tmp_path: Path):
    run = _run(tmp_path)
    run.progress.current_index = 3
    _advance_stage(run, "P4_structural_connections")
    assert run.current_stage == "P5_clean_blockin"
    run.draw(_action("P5_clean_blockin", "draw-p5"))
    run.prepare_stage_review()
    manifest = _resolved_manifest(run, "P5_clean_blockin")
    run.submit_resolved_form_manifest(manifest)
    retirement = ConstructionRetirementRecord(("old-construction",), ("gesture-ghost",), ("draw-p5",), "selected contour owns the resolved form", run.session.history.cursor)
    run.record_construction_retirement(retirement)
    run.submit_resolved_form_review(manifest=manifest, evaluator_id="fresh-blind-fixture", findings=("hair, garment, joints and topology inspected",), decision="advance", rationale="no resolved-form blocker remains")
    run.submit_stage_review(observations=("P5 process contract is complete",), decision="advance", advance_rationale="P5 process and visual gates agree")
    assert run.current_stage == "P6_identity_finish"
    profile = IdentityFinishProfile(max_identity_strokes=4, max_confirmation_strokes=1, max_micro_fold_strokes=1)
    preflight = run.prepare_identity_finish(profile)
    assert preflight["allowed"]
    run.draw(_action("P6_identity_finish", "draw-p6"))
    manifest6 = IdentityFinishManifest(
        drawing_state_sha256=run._state_sha(), drawing_artifact_sha256=run._state_sha(), history_cursor=run.session.history.cursor,
        observation_lock_digest=run.observation_lock.observation_digest, profile=profile,
        calibration_sheet_digest=run.calibration_sheet.digest(), face_relation="eye-line, nose and mouth follow the locked head turn",
        hair_group_count=2, garment_mark_count=2, identity_stroke_count=2, confirmation_stroke_count=0,
        accent_stroke_count=0, fold_stroke_count=1, evidence_refs=("identity/calibration_sheet.json", "identity/whole_view.png"), evaluator_id="fresh-blind-fixture", decision="advance", rationale="bounded identity marks preserve the resolved block-in",
    )
    run.submit_identity_finish_manifest(manifest6)
    run.prepare_stage_review()
    run.submit_stage_review(observations=("P6 optional identity process is complete",), decision="advance", advance_rationale="identity visual manifest is current")
    assert run.current_stage is None
    resumed = DrawingRun.resume(run.output_dir)
    assert resumed.identity_finish_manifest is not None
    assert resumed.construction_retirement is not None
    assert resumed.resolved_form_reviews["P5_clean_blockin"].decision == "advance"


def test_p6_preflight_blocks_upstream_revise():
    from img2drawing import preflight_identity_finish
    result = preflight_identity_finish({"P3_primary_masses": {"decision": "revise", "blockers": ("head_hair",)}})
    assert not result.allowed
    assert "P3_primary_masses" in result.required_reopens


def test_adaptive_evidence_cannot_hide_owned_mismatch():
    digest = "a" * 64
    proposal = AssistiveROIProposal("roi-1", "face", (0.1, 0.1, 0.4, 0.4), "edge-preview", .7, digest, True, "agent confirmed the face crop")
    excluded = ExcludedRegion("far_arm", "occluded by the prop", ("occlusion",), digest)
    with pytest.raises(ValueError, match="owned"):
        AcceptedResidual("face", "P5_clean_blockin", "face is wrong", "skip it", stage_owned=True)
    policy = AdaptiveEvidencePolicy(digest, (proposal,), (excluded,), ())
    assert policy.to_dict()["preview_only"]


def test_resolved_schema_roundtrip(tmp_path: Path):
    run = _run(tmp_path)
    run.progress.current_index = 3
    run.stage_start("P4_structural_connections")
    run.prepare_stage_review()
    manifest = _resolved_manifest(run, "P4_structural_connections")
    schema = json.loads((ROOT / "schemas" / "resolved_form.schema.json").read_text())
    validators.validator_for(schema)(schema).validate(manifest.to_dict())
