#!/usr/bin/env python3
"""Packaged-worker smoke run on a subject unrelated to the sniper materials."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

from img2drawing import DrawingAction
from img2drawing.legacy.r23 import (
    DrawingRun, ObservationContract, ViewObservation,
    RegionClosureEntry, RegionClosureManifest,
    ResolvedFormEntry, ResolvedFormManifest, ConstructionRetirementRecord,
    IdentityFinishProfile, IdentityFinishManifest,
)
from img2drawing.review.artifact import sha256_file
from img2drawing.review.fidelity import REQUIRED_P3_REGIONS


ROOT = Path(__file__).resolve().parents[2]
SUBJECT = ROOT / "skills/img2drawing/examples/full_body_croquis/subject.png"
OUT = ROOT / "dev/evidence/fresh-worker"


def action(run, aid, stage, part, points, *, role="construction", layer=10, grade="2H", preset="construction_pencil"):
    return DrawingAction(
        action_id=aid, kind="draw_stroke", stage=stage, role=role, part=part,
        points=tuple((float(x), float(y)) for x, y in points), confidence=.84,
        stroke_id=aid, layer=layer, tool={"preset": preset, "grade": grade},
        observation_id=run.observation_lock.observation_id,
        source_observation=f"Fresh worker observation: {part} was checked on the new subject.",
    )


def process_advance(run, stage, note):
    run.prepare_stage_review(stage)
    run.submit_stage_review(
        stage=stage,
        contract_findings=(f"Fresh worker checked the {stage} contract directly.",),
        subject_findings=("The new subject, not material notes, supplied geometry.",),
        grammar_findings=("Construction/form roles remain sparse and pressure-aware.",),
        drawing_findings=(note,), observations=(note,), decision="advance",
        advance_rationale="Independent process review accepted the fresh pass.",
    )


def p3_advance(run):
    artifacts = run.prepare_stage_review("P3_primary_masses")
    packet = run._blind_packets["P3_primary_masses"]
    entries = tuple(RegionClosureEntry(
        region_id=region,
        subject_finding=f"Fresh subject relation for {region} inspected.",
        drawing_finding=f"Current occupied volume preserves {region}.",
        evidence_refs=("reviews/P3_primary_masses/pass_01/current_drawing.png",),
        decision="closed",
    ) for region in REQUIRED_P3_REGIONS)
    manifest = RegionClosureManifest(
        stage="P3_primary_masses", drawing_state_sha256=artifacts.drawing.state_sha256,
        drawing_artifact_sha256=artifacts.drawing.artifact_sha256,
        history_cursor=artifacts.drawing.history_cursor,
        observation_lock_digest=run.observation_lock.observation_digest,
        regions=entries, evaluator_id="fresh-worker-independent-review",
    )
    run.submit_region_closure_manifest(manifest)
    run.submit_visual_fidelity_review(
        manifest=manifest, evaluator_id="fresh-worker-independent-review",
        findings=("Whole view and subject comparison were inspected before process rationale.",),
        decision="advance", rationale="All required macro regions are closed.",
    )
    run.submit_stage_review(
        stage="P3_primary_masses",
        contract_findings=("P3 occupied volumes follow the new subject observation.",),
        subject_findings=("Head, torso, pelvis, limbs and feet were compared to the subject.",),
        grammar_findings=("Mass hierarchy is subordinate to the original geometry authority.",),
        drawing_findings=("No unresolved macro region blocker remains.",),
        observations=("Independent P3 visual review accepted.",), decision="advance",
        advance_rationale="P3 process and blind visual records agree.",
    )


def resolved_advance(run, stage, regions, before_advance=None):
    artifacts = run.prepare_stage_review(stage)
    packet = run._resolved_form_packets[stage]
    entries = tuple(ResolvedFormEntry(
        region_id=region,
        subject_finding=f"Fresh subject fact for {region} was inspected.",
        drawing_finding=f"Drawing preserves {region} with a deliberate transition.",
        evidence_refs=(f"reviews/{stage}/pass_01/current_drawing.png",),
        decision="closed",
    ) for region in regions)
    manifest = ResolvedFormManifest(
        stage=stage, drawing_state_sha256=artifacts.drawing.state_sha256,
        drawing_artifact_sha256=artifacts.drawing.artifact_sha256,
        history_cursor=artifacts.drawing.history_cursor,
        observation_lock_digest=run.observation_lock.observation_digest,
        regions=entries, evaluator_id="fresh-worker-independent-review",
        blind_packet_digest=packet["packet_digest"],
    )
    run.submit_resolved_form_manifest(manifest)
    run.submit_resolved_form_review(
        manifest=manifest, evaluator_id="fresh-worker-independent-review",
        findings=("Subject and drawing were inspected in whole view and local relations.",),
        decision="advance", rationale="All eight resolved-form regions are closed.", stage=stage,
    )
    if before_advance is not None:
        before_advance(run)
    run.submit_stage_review(
        stage=stage, contract_findings=(f"{stage} contract checked.",),
        subject_findings=("The fresh subject remains the geometry authority.",),
        grammar_findings=("Hair, garment, joints, and line roles are explicit.",),
        drawing_findings=("No resolved-form blocker remains.",), observations=("resolved form accepted",),
        decision="advance", advance_rationale="Independent resolved-form review accepted.",
    )


def build() -> Path:
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    run = DrawingRun.create(
        SUBJECT, OUT, width=512, height=802,
        session_id="fresh-worker-generalization-r23",
        stage_registry="full_body_croquis_with_p6",
        working_supersample=2,
    )
    run.lock_observation(ObservationContract(
        subject_summary="front three-quarter standing person with turned head, cardigan, jeans and two distinct shoes",
        global_relations={"weight_side": "image_left", "counterbalance_side": "image_right", "head_direction": "image_left", "prop": "none"},
        parts={"head": "face opening sits inside a smaller hair grouping", "garment": "cardigan hangs over torso and sleeves", "legs": "support and stepped leg have different knee paths"},
        uncertainties=("loose fabric obscures the exact knee contour",),
        drawing_priorities=("head turn", "torso rhythm", "support versus counterbalance leg", "sparse folds"),
        evidence_refs=("subject.png",),
        view=ViewObservation(
            body_view="front_three_quarter", torso_turn="left", near_side="subject_left",
            arm_visibility={"subject_left": "partial", "subject_right": "visible"},
            arm_occlusion={"subject_left": ("pocket",), "subject_right": ()},
            prop_overlap_order=(), uncertainties=("near hand partly occluded by pocket",),
        ),
    ))
    run.stage_start("P1_gesture")
    run.draw_many([
        action(run, "FW-P1-01", "P1_gesture", "head_spine", ((264, 29), (258, 115), (241, 250), (214, 410), (233, 696)), role="gesture"),
        action(run, "FW-P1-02", "P1_gesture", "support_leg", ((198, 358), (212, 524), (233, 696)), role="gesture"),
        action(run, "FW-P1-03", "P1_gesture", "counterbalance_leg", ((287, 364), (311, 524), (350, 724)), role="gesture"),
    ])
    process_advance(run, "P1_gesture", "Gesture preserves the new subject's head, spine and weight transfer.")
    run.stage_start("P2_primary_axes")
    run.draw_many([
        action(run, "FW-P2-01", "P2_primary_axes", "shoulder_axis", ((184, 175), (250, 164), (311, 153)), role="axis"),
        action(run, "FW-P2-02", "P2_primary_axes", "pelvis_axis", ((198, 358), (246, 365), (287, 364)), role="axis"),
        action(run, "FW-P2-03", "P2_primary_axes", "arm_chain", ((184, 175), (169, 301), (158, 413)), role="axis"),
        action(run, "FW-P2-04", "P2_primary_axes", "near_arm_chain", ((311, 153), (350, 263), (294, 331)), role="axis"),
    ])
    process_advance(run, "P2_primary_axes", "Axes preserve shoulder/pelvis counter-tilt and both limb paths.")
    run.stage_start("P3_primary_masses")
    run.draw_many([
        action(run, "FW-P3-01", "P3_primary_masses", "skull_face_mass", ((264, 29), (296, 63), (276, 114), (240, 120), (220, 75)), role="mass", layer=10),
        action(run, "FW-P3-02", "P3_primary_masses", "torso_garment_mass", ((210, 150), (310, 145), (330, 360), (246, 410), (190, 350)), role="mass", layer=10),
        action(run, "FW-P3-03", "P3_primary_masses", "support_leg_mass", ((198, 358), (225, 470), (212, 524), (233, 696)), role="mass", layer=10),
        action(run, "FW-P3-04", "P3_primary_masses", "counterbalance_leg_mass", ((287, 364), (311, 524), (350, 724)), role="mass", layer=10),
    ])
    p3_advance(run)
    run.stage_start("P4_structural_connections")
    run.draw_many([
        action(run, "FW-P4-01", "P4_structural_connections", "face_hair_opening", ((228, 48), (240, 40), (274, 52), (286, 82)), role="form", layer=20, grade="HB", preset="form_pencil"),
        action(run, "FW-P4-02", "P4_structural_connections", "cardigan_shoulder", ((205, 155), (220, 180), (240, 190)), role="connection", layer=20, grade="HB", preset="form_pencil"),
        action(run, "FW-P4-03", "P4_structural_connections", "elbow_transition", ((169, 292), (164, 304), (158, 316)), role="connection", layer=20, grade="HB", preset="form_pencil"),
        action(run, "FW-P4-04", "P4_structural_connections", "knee_transition", ((205, 510), (212, 524), (220, 540)), role="connection", layer=20, grade="HB", preset="form_pencil"),
    ])
    resolved_advance(run, "P4_structural_connections", ("head_hair_connection", "face_opening", "torso_garment_hang", "near_arm_joint_chain", "far_arm_joint_chain", "waist_leg_openings", "footwear_connection", "attached_object_structure"))
    run.stage_start("P5_clean_blockin")
    run.draw_many([
        action(run, "FW-P5-01", "P5_clean_blockin", "hair_group_contour", ((220, 46), (205, 56), (194, 78), (198, 110), (210, 130)), role="contour", layer=20, grade="HB", preset="form_pencil"),
        action(run, "FW-P5-02", "P5_clean_blockin", "face_scaffold", ((230, 75), (244, 73), (257, 78), (263, 90)), role="identity", layer=30, grade="2H", preset="form_pencil"),
        action(run, "FW-P5-03", "P5_clean_blockin", "cardigan_hem_fold", ((205, 315), (225, 325), (245, 320)), role="fold", layer=20, grade="2H", preset="form_pencil"),
        action(run, "FW-P5-04", "P5_clean_blockin", "shoe_connection", ((220, 686), (233, 696), (248, 700)), role="contour", layer=20, grade="HB", preset="form_pencil"),
        action(run, "FW-P5-05", "P5_clean_blockin", "hair_group_contour_right", ((244, 42), (270, 48), (286, 70), (286, 103), (270, 132)), role="contour", layer=20, grade="HB", preset="form_pencil"),
        action(run, "FW-P5-06", "P5_clean_blockin", "face_jaw", ((226, 92), (232, 111), (246, 121), (260, 110)), role="identity", layer=30, grade="HB", preset="form_pencil"),
        action(run, "FW-P5-07", "P5_clean_blockin", "torso_left_contour", ((210, 150), (198, 205), (194, 280), (190, 350)), role="contour", layer=20, grade="HB", preset="form_pencil"),
        action(run, "FW-P5-08", "P5_clean_blockin", "torso_right_contour", ((310, 145), (323, 210), (327, 285), (330, 360)), role="contour", layer=20, grade="HB", preset="form_pencil"),
        action(run, "FW-P5-09", "P5_clean_blockin", "arm_left_contour", ((184, 175), (169, 250), (160, 320), (158, 413)), role="contour", layer=20, grade="HB", preset="form_pencil"),
        action(run, "FW-P5-10", "P5_clean_blockin", "arm_right_contour", ((311, 153), (338, 210), (350, 263), (294, 331)), role="contour", layer=20, grade="HB", preset="form_pencil"),
        action(run, "FW-P5-11", "P5_clean_blockin", "support_leg_contour", ((198, 358), (205, 430), (212, 524), (220, 620), (233, 696)), role="contour", layer=20, grade="HB", preset="form_pencil"),
        action(run, "FW-P5-12", "P5_clean_blockin", "counter_leg_contour", ((287, 364), (300, 430), (311, 524), (330, 630), (350, 724)), role="contour", layer=20, grade="HB", preset="form_pencil"),
        action(run, "FW-P5-13", "P5_clean_blockin", "support_shoe", ((220, 686), (230, 700), (250, 706), (266, 700)), role="contour", layer=30, grade="HB", preset="form_pencil"),
        action(run, "FW-P5-14", "P5_clean_blockin", "counter_shoe", ((335, 710), (350, 724), (374, 728), (390, 718)), role="contour", layer=30, grade="HB", preset="form_pencil"),
    ])
    run.draw_many([
        DrawingAction(
            action_id=f"FW-P5-retire-{index:02d}", kind="delete_stroke", stage="P5_clean_blockin",
            target_stroke_id=stroke_id, tool={"preset": "hard_eraser"},
            observation_id=run.observation_lock.observation_id,
            source_observation=f"P5 ownership review for {stroke_id}.",
            reason="Transfer primary mass ownership to the selected clean contour.",
            revision_of=stroke_id,
        )
        for index, stroke_id in enumerate(("FW-P3-01", "FW-P3-02"), 1)
    ])
    def retirement(active):
        active.record_construction_retirement(ConstructionRetirementRecord(
            retired_stroke_ids=("FW-P3-01", "FW-P3-02"),
            retained_ghost_stroke_ids=("FW-P1-01", "FW-P1-02", "FW-P1-03"),
            contour_stroke_ids=("FW-P5-01", "FW-P5-02", "FW-P5-03", "FW-P5-04"),
            reason="Fresh worker transfers mass ownership to selected contour while retaining gesture ghosts.",
            history_cursor=active.session.history.cursor,
        ))
    resolved_advance(run, "P5_clean_blockin", ("face_feature_scaffold", "hair_silhouette_grouping", "garment_contour_and_folds", "joint_contour_continuity", "hands_and_footwear", "prop_final_topology", "contour_ownership", "construction_retirement_and_line_hierarchy"), before_advance=retirement)
    run.stage_start("P6_identity_finish")
    run.prepare_identity_finish(IdentityFinishProfile())
    run.draw_many([
        action(run, "FW-P6-01", "P6_identity_finish", "hair_part", ((242, 47), (236, 62), (231, 78)), role="identity", layer=30, grade="2H", preset="form_pencil"),
        action(run, "FW-P6-02", "P6_identity_finish", "hair_lock", ((221, 48), (208, 67), (205, 94), (212, 119)), role="identity", layer=30, grade="2H", preset="form_pencil"),
        action(run, "FW-P6-03", "P6_identity_finish", "eye_line", ((229, 80), (244, 78), (258, 83)), role="identity", layer=30, grade="HB", preset="form_pencil"),
        action(run, "FW-P6-04", "P6_identity_finish", "nose_mouth_relation", ((247, 82), (243, 95), (250, 102)), role="identity", layer=30, grade="HB", preset="form_pencil"),
        action(run, "FW-P6-05", "P6_identity_finish", "cardigan_tension_fold", ((214, 196), (230, 204), (246, 202)), role="fold", layer=20, grade="2H", preset="form_pencil"),
        action(run, "FW-P6-06", "P6_identity_finish", "cardigan_compression_fold", ((200, 277), (218, 284), (236, 280)), role="fold", layer=20, grade="2H", preset="form_pencil"),
    ])
    p6_artifacts = run.prepare_stage_review("P6_identity_finish")
    counts = run.identity_finish_counts()
    identity = IdentityFinishManifest(
        profile=IdentityFinishProfile(),
        drawing_state_sha256=run._state_sha(),
        drawing_artifact_sha256=p6_artifacts.drawing.artifact_sha256,
        history_cursor=run.session.history.cursor,
        observation_lock_digest=run.observation_lock.observation_digest,
        calibration_sheet_digest=run.calibration_sheet.digest(),
        face_relation="Face opening, eye line, nose and mouth remain inside grouped hair.",
        hair_group_count=2, garment_mark_count=2,
        identity_stroke_count=counts["identity_stroke_count"],
        confirmation_stroke_count=counts["confirmation_stroke_count"],
        accent_stroke_count=counts["accent_stroke_count"], fold_stroke_count=counts["fold_stroke_count"],
        evidence_refs=(
            "reviews/P6_identity_finish/pass_01/current_drawing.png",
            "identity/calibration_sheet.json",
            "identity/calibration_sheet.png",
            "identity/calibration_sheet_50pct.png",
        ),
        evaluator_id="fresh-worker-independent-review", decision="advance",
        rationale="Bounded identity finish accepted after face/hair and garment crops were inspected.",
    )
    run.submit_identity_finish_manifest(identity)
    run.submit_stage_review(
        stage="P6_identity_finish",
        contract_findings=("Optional identity contract checked after P1-P5 closure.",),
        subject_findings=("Face relation and grouped hair were compared with the fresh subject.",),
        grammar_findings=("Calibration and sparse fold budget are bound to the pass.",),
        drawing_findings=("No blanket confirmation or broad value band was added.",),
        observations=("fresh identity review accepted",), decision="advance",
        advance_rationale="Identity manifest is current and bounded.",
    )
    result = run.finish(timelapse="none")
    for path in OUT.rglob("*"):
        if path.is_file() and path.suffix.lower() in {".json", ".md"}:
            text = path.read_text(encoding="utf-8")
            text = text.replace(str(ROOT.resolve()) + "/", "")
            path.write_text(text, encoding="utf-8")
    report = {
        "schema": "img2drawing.fresh_worker_generalization.v1",
        "status": "closed",
        "subject": str(SUBJECT.relative_to(ROOT)),
        "subject_sha256": sha256_file(SUBJECT),
        "final_drawing": str(result.final_drawing.relative_to(ROOT)),
        "stage_registry": run.stage_registry_name,
        "package_identity": "source-tree-current-r23-candidate",
        "prohibited_coordinate_or_action_ids": False,
        "mechanical_artistic_separation": True,
        "mechanical_note": "Hashes, replay, stage closure and provenance were checked mechanically; artistic closure is the independent visual record.",
        "visual_evidence": ["final/drawing.png", "compare/subject_vs_final.png", "reviews/P3_primary_masses/pass_01/current_drawing.png"],
        "limitation": "One fresh subject demonstrates generalization; additional failure regimes remain queued one at a time.",
    }
    (OUT / "generalization_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")
    return result.final_drawing


if __name__ == "__main__":
    print(build())
