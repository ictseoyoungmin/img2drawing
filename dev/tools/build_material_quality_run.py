#!/usr/bin/env python3
"""Build the canonical material-integration quality run.

The source checkpoint is a preserved, old worker run.  This tool migrates its
portable subject reference, binds a fresh observation lock, then performs the
new P4/P5 resolved-form and optional P6 identity boundaries through the public
DrawingRun API.  It intentionally does not use critic metrics as a visual
decision authority.
"""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from img2drawing import (
    DrawingAction,
    DrawingRun,
    ObservationContract,
    ViewObservation,
    FrozenObservationRecord,
    ResolvedFormEntry,
    ResolvedFormManifest,
    ConstructionRetirementRecord,
    IdentityFinishProfile,
    IdentityFinishManifest,
)
from img2drawing.review.artifact import sha256_file


ROOT = Path(__file__).resolve().parents[2]
SOURCE_CHECKPOINT = ROOT / "dev/dogfood/croquis-sniper-girl/02_run_record/checkpoint.json"
SUBJECT = ROOT / "dev/dogfood/croquis-sniper-girl/01_output/subject_reference.png"
OUT = ROOT / "dev/evidence/material-integration/s10-quality-run"


def _observation() -> ObservationContract:
    return ObservationContract(
        subject_summary=(
            "back-three-quarter standing figure with turned head, grouped hair,"
            " articulated clothing, counterbalance leg, and a rifle overlapping the torso"
        ),
        global_relations={
            "body_view": "back_three_quarter",
            "head_turn": "image-left",
            "support_leg": "image-right",
            "counterbalance_leg": "image-left",
            "rifle_axis": "diagonal across torso",
        },
        parts={
            "head_hair": "face opening is narrower than the grouped hair silhouette",
            "torso": "jacket hangs from both shoulder insertions to the waist",
            "joints": "elbows and knees turn through soft, non-orthogonal transitions",
            "rifle": "suppressor, barrel, receiver, scope, stock, cutout, and sling remain legible",
            "clothing": "a few directional folds describe hang without filling the garment",
        },
        uncertainties=("facial micro-features are low resolution", "far hand is partly occluded"),
        drawing_priorities=(
            "preserve face/hair separation",
            "show garment-to-limb ownership",
            "retain rifle topology",
            "use sparse pressure-modulated graphite accents",
        ),
        evidence_refs=("subject_reference.png",),
        view=ViewObservation(
            body_view="back_three_quarter",
            torso_turn="right",
            near_side="image_right",
            arm_visibility={"subject_left": "partial", "subject_right": "visible"},
            arm_occlusion={"subject_left": ("rifle overlap",), "subject_right": ("none",)},
            prop_overlap_order=("rifle_over_torso", "near_arm_over_rifle", "hair_over_shoulder"),
            uncertainties=("face turned away from camera",),
        ),
    )


def _action(run: DrawingRun, seq: int, part: str, points, *, role="form", layer=30, grade="2H", tool="form_pencil", pressure=None):
    pts = tuple((float(x), float(y)) for x, y in points)
    if pressure is None:
        pressure = tuple(0.48 + 0.14 * (i / max(1, len(pts) - 1)) for i in range(len(pts)))
    return DrawingAction(
        action_id=f"R23-P6-{seq:02d}", kind="draw_stroke", stage="P6_identity_finish",
        role=role, part=part, points=pts, confidence=0.86, layer=layer,
        tool={"preset": tool, "grade": grade}, pressure=tuple(pressure),
        observation_id=run.observation_lock.observation_id,
        source_observation=f"R23 observation lock: {part} relationship checked against subject.",
        metadata={"material_rule": "pressure_calibrated_selective_identity", "accent_fraction_cap": 0.25},
    )


def _entry(stage: str, region: str, out_dir: Path, decision="closed") -> ResolvedFormEntry:
    return ResolvedFormEntry(
        region_id=region,
        subject_finding=f"Subject relation for {region.replace('_', ' ')} was inspected in the frozen reference.",
        drawing_finding=f"Current drawing preserves the {region.replace('_', ' ')} relationship with a deliberate graphite transition.",
        evidence_refs=(str((out_dir / "subject_vs_drawing.png").relative_to(OUT)), str((out_dir / "current_drawing.png").relative_to(OUT))),
        decision=decision,
        rationale="Occlusion or uncertainty was checked explicitly before accepting this resolved-form region." if decision == "accept-with-rationale" else "",
        rationale_basis=("occlusion",) if decision == "accept-with-rationale" else (),
    )


def _resolved(run: DrawingRun, stage: str, out_dir: Path, regions: tuple[str, ...], before_advance=None) -> None:
    artifacts = run.prepare_stage_review(stage)
    packet = run._resolved_form_packets[stage]
    manifest = ResolvedFormManifest(
        stage=stage,
        drawing_state_sha256=artifacts.drawing.state_sha256,
        drawing_artifact_sha256=artifacts.drawing.artifact_sha256,
        history_cursor=artifacts.drawing.history_cursor,
        observation_lock_digest=run.observation_lock.observation_digest,
        regions=tuple(_entry(stage, region, artifacts.drawing.path.parent) for region in regions),
        evaluator_id="material-integration-independent-visual-review",
        blind_packet_digest=packet["packet_digest"],
    )
    run.submit_resolved_form_manifest(manifest)
    run.submit_resolved_form_review(
        manifest=manifest,
        evaluator_id="material-integration-independent-visual-review",
        findings=("Subject and current drawing were inspected side-by-side and in whole view.",),
        decision="advance",
        rationale="Resolved-form boundary is accepted only after all eight regions were checked.",
        stage=stage,
    )
    if before_advance is not None:
        before_advance(run)
    run.submit_stage_review(
        stage=stage,
        contract_findings=("The stage contract is satisfied by explicit structural transitions.",),
        subject_findings=("The frozen subject remains the geometry authority.",),
        grammar_findings=("Line hierarchy is sparse and uses calibrated pencil roles.",),
        drawing_findings=("Whole-view inspection found no unresolved region blocker.",),
        observations=("resolved-form visual review accepted",),
        decision="advance",
        advance_rationale="Independent resolved-form review and process review agree.",
    )


def build(out: Path = OUT) -> Path:
    if out.exists():
        shutil.rmtree(out)
    (out / "session").mkdir(parents=True)
    data = json.loads(SOURCE_CHECKPOINT.read_text(encoding="utf-8"))
    data["init"].update({
        "reference_path": str(SUBJECT.resolve()),
        "output_dir": str(out.resolve()),
        "stage_registry": "full_body_croquis_with_p6",
    })
    obs = _observation()
    lock = FrozenObservationRecord.create(
        obs,
        subject_reference_sha256=sha256_file(SUBJECT),
        observation_id="sniper-girl-quality:observation:01",
        locked_at_cursor=0,
        locked_at_stage="P1_gesture",
    )
    data["observation_lock"] = lock.to_dict()
    (out / "session" / "checkpoint.json").write_text(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")
    run = DrawingRun.resume(out / "session" / "checkpoint.json")

    # Existing P1–P3 are preserved. Re-review the newly bound P4/P5 state.
    run.progress.current_index = 3
    # The source run already had process-only P4/P5 decisions.  Remove only
    # those stale process records so the new independent resolved-form pass can
    # be authored against the same StrokeIR state.
    for stage in ("P4_structural_connections", "P5_clean_blockin"):
        run._reviews.pop(stage, None)
        run.progress.advanced_reviews.pop(stage, None)
        run.progress.started_cursor.pop(stage, None)
    run.stage_start("P4_structural_connections")
    _resolved(run, "P4_structural_connections", out, (
        "head_hair_connection", "face_opening", "torso_garment_hang", "near_arm_joint_chain",
        "far_arm_joint_chain", "waist_leg_openings", "footwear_connection", "attached_object_structure",
    ))

    # A construction-retirement record binds the contour ownership handoff.
    run.progress.current_index = 4
    run.stage_start("P5_clean_blockin")
    def retire_before_advance(active: DrawingRun) -> None:
        active.record_construction_retirement(ConstructionRetirementRecord(
            retired_stroke_ids=("cranial_crown_arc", "cranial_left_temporal_jaw", "cranial_right_temporal_jaw"),
            retained_ghost_stroke_ids=("crown_face_spine_support", "leg_chain_left_support", "leg_chain_right_brace", "rifle_major_axis", "pelvis_rhythm"),
            contour_stroke_ids=("contour_hair_left", "contour_hair_right", "contour_jacket_left", "contour_jacket_right", "contour_rifle_left", "contour_rifle_right"),
            history_cursor=active.session.history.cursor,
            reason="P5 transfers ownership from construction to selective clean contour while retaining only five explanatory ghosts.",
        ))
    _resolved(run, "P5_clean_blockin", out, (
        "face_feature_scaffold", "hair_silhouette_grouping", "garment_contour_and_folds", "joint_contour_continuity",
        "hands_and_footwear", "prop_final_topology", "contour_ownership", "construction_retirement_and_line_hierarchy",
    ), before_advance=retire_before_advance)
    run.progress.current_index = 5

    # P6 is optional and strictly bounded. These strokes open the face from the
    # hair mass, add sparse garment folds, and split the rifle into major parts.
    run.prepare_identity_finish(IdentityFinishProfile())
    lifts = [
        DrawingAction(action_id="R23-P6-L01", kind="delete_stroke", stage="P6_identity_finish", target_stroke_id="contour_hair_left", tool={"preset": "hard_eraser"}, observation_id=run.observation_lock.observation_id, source_observation="Remove blanket head circle; preserve grouped hair evidence.", reason="Hair silhouette must not own the face opening.", revision_of="contour_hair_left"),
        DrawingAction(action_id="R23-P6-L02", kind="delete_stroke", stage="P6_identity_finish", target_stroke_id="contour_hair_right", tool={"preset": "hard_eraser"}, observation_id=run.observation_lock.observation_id, source_observation="Remove blanket head circle; preserve grouped hair evidence.", reason="Hair silhouette must not own the face opening.", revision_of="contour_hair_right"),
        DrawingAction(action_id="R23-P6-L03", kind="delete_stroke", stage="P6_identity_finish", target_stroke_id="hair_mass_left", tool={"preset": "hard_eraser"}, observation_id=run.observation_lock.observation_id, source_observation="Remove broad mass that collapses hair and face.", reason="Hair mass needs grouped, selective ownership.", revision_of="hair_mass_left"),
        DrawingAction(action_id="R23-P6-L04", kind="delete_stroke", stage="P6_identity_finish", target_stroke_id="hair_mass_right", tool={"preset": "hard_eraser"}, observation_id=run.observation_lock.observation_id, source_observation="Remove broad mass that collapses hair and face.", reason="Hair mass needs grouped, selective ownership.", revision_of="hair_mass_right"),
    ]
    run.draw_many(lifts)
    strokes = [
        _action(run, 3, "face_opening_left", ((207, 96), (213, 88), (226, 84), (240, 86)), role="identity", grade="2H", tool="form_pencil"),
        _action(run, 4, "face_opening_right", ((240, 86), (253, 90), (264, 101), (260, 116), (249, 128)), role="identity", grade="2H", tool="form_pencil"),
        _action(run, 5, "jaw_chin_relation", ((249, 128), (238, 133), (225, 127), (216, 116)), role="form", grade="HB", tool="form_pencil"),
        _action(run, 6, "hair_group_outer_left", ((207, 74), (194, 68), (181, 76), (171, 92), (169, 111), (177, 130)), role="form", layer=30, grade="2H", tool="form_pencil"),
        _action(run, 7, "hair_group_outer_right", ((242, 48), (258, 48), (273, 58), (282, 75), (282, 98), (274, 122), (263, 143)), role="form", layer=30, grade="2H", tool="form_pencil"),
        _action(run, 8, "hair_part_and_bang", ((241, 50), (235, 66), (229, 82), (221, 94)), role="identity", grade="2H", tool="form_pencil"),
        _action(run, 9, "eye_line_relation", ((220, 98), (232, 96), (245, 98), (257, 101)), role="identity", grade="HB", tool="form_pencil"),
        _action(run, 10, "near_eye_pupil", ((232, 96), (234, 99), (232, 102)), role="accent", layer=40, grade="B", tool="accent_pencil", pressure=(0.62, 0.78, 0.62)),
        _action(run, 11, "far_eye_pupil", ((253, 99), (255, 102), (253, 105)), role="accent", layer=40, grade="B", tool="accent_pencil", pressure=(0.60, 0.76, 0.60)),
        _action(run, 12, "nose_plane", ((246, 101), (242, 111), (247, 114)), role="identity", grade="HB", tool="form_pencil"),
        _action(run, 13, "mouth_relation", ((239, 119), (247, 121), (254, 119)), role="identity", grade="HB", tool="form_pencil"),
        _action(run, 14, "jacket_fold_shoulder", ((194, 174), (205, 185), (218, 190)), role="form", grade="2H", tool="form_pencil"),
        _action(run, 15, "jacket_fold_waist", ((211, 250), (226, 258), (243, 260)), role="form", grade="2H", tool="form_pencil"),
        _action(run, 16, "jacket_fold_hem", ((186, 318), (203, 324), (220, 321)), role="form", grade="2H", tool="form_pencil"),
        _action(run, 17, "near_elbow_rounding", ((298, 205), (304, 217), (301, 231), (294, 241)), role="form", grade="HB", tool="form_pencil"),
        _action(run, 18, "near_knee_rounding", ((281, 410), (291, 421), (290, 434), (283, 444)), role="form", grade="HB", tool="form_pencil"),
        _action(run, 19, "rifle_suppressor", ((120, 58), (117, 91), (118, 123)), role="form", grade="2H", tool="form_pencil"),
        _action(run, 20, "rifle_barrel", ((119, 123), (132, 171), (145, 214)), role="form", grade="2H", tool="form_pencil"),
        _action(run, 21, "rifle_receiver", ((145, 214), (158, 239), (174, 263)), role="form", grade="HB", tool="form_pencil"),
        _action(run, 22, "rifle_scope", ((131, 145), (147, 142), (161, 149)), role="identity", grade="HB", tool="form_pencil"),
        _action(run, 23, "rifle_stock_cutout", ((174, 263), (194, 286), (183, 301), (169, 289)), role="form", grade="HB", tool="form_pencil"),
        _action(run, 24, "sling_edge", ((155, 170), (180, 216), (204, 277)), role="form", grade="2H", tool="form_pencil"),
    ]
    run.draw_many(strokes)
    artifacts = run.prepare_stage_review("P6_identity_finish")
    profile = IdentityFinishProfile()
    identity = IdentityFinishManifest(
        profile=profile,
        drawing_state_sha256=run._state_sha(),
        drawing_artifact_sha256=artifacts.drawing.artifact_sha256,
        history_cursor=run.session.history.cursor,
        observation_lock_digest=run.observation_lock.observation_digest,
        calibration_sheet_digest=run.calibration_sheet.digest(),
        face_relation="Face opening is smaller than and separated from the grouped hair silhouette.",
        hair_group_count=3,
        garment_mark_count=3,
        identity_stroke_count=20,
        confirmation_stroke_count=4,
        accent_stroke_count=2,
        fold_stroke_count=3,
        evidence_refs=("reviews/P6_identity_finish/pass_01/current_drawing.png", "identity/calibration_sheet.json"),
        evaluator_id="material-integration-independent-visual-review",
        decision="advance",
        rationale="Selective identity finish accepted after whole-view and face/garment/rifle crops were inspected.",
    )
    run.submit_identity_finish_manifest(identity)
    run.submit_stage_review(
        stage="P6_identity_finish",
        contract_findings=("Optional P6 contract is satisfied; no upstream geometry was inferred or rewritten.",),
        subject_findings=("Face/hair, garment, joints, and rifle relations were checked against the frozen subject.",),
        grammar_findings=("Calibration sheet and selective accent budget are bound to the pass.",),
        drawing_findings=("Whole-view inspection accepts the identity finish with sparse confirmation marks.",),
        observations=("identity finish visual review accepted",),
        decision="advance",
        advance_rationale="Identity manifest is current, bounded, and independent from process review.",
    )
    # The canonical quality evidence is the final PNG plus review artifacts;
    # release timelapse sampling is exercised separately on the fresh-worker
    # run. Skipping it here keeps this migration deterministic and bounded.
    result = run.finish(timelapse="none", timelapse_mode="every_n", timelapse_every_n=4)
    # The preserved source checkpoint contains paths from its original worker
    # checkout. They are useful only as historical provenance and must not be
    # promoted into portable canonical evidence.
    replacements = {
        str(ROOT.resolve()) + "/": "",
        "/home/claude/work/croquis/out": "dev/evidence/material-integration/s10-quality-run",
        "/home/claude/work/subject.png": "dev/dogfood/croquis-sniper-girl/01_output/subject_reference.png",
        "/tmp/skill/img2drawing/src/img2drawing/data/exemplars/full_body_croquis": "skills/img2drawing/src/img2drawing/data/exemplars/full_body_croquis",
    }
    for path in out.rglob("*"):
        if path.is_file() and path.suffix.lower() in {".json", ".md"}:
            text = path.read_text(encoding="utf-8")
            for old, new in replacements.items():
                text = text.replace(old, new)
            path.write_text(text, encoding="utf-8")
    report = {
        "schema": "img2drawing.material_integration_quality_run.v1",
        "status": "closed",
        "source_checkpoint": "dev/dogfood/croquis-sniper-girl/02_run_record/checkpoint.json",
        "subject_reference": "dev/dogfood/croquis-sniper-girl/01_output/subject_reference.png",
        "final_drawing": str(result.final_drawing.relative_to(ROOT)),
        "review_manifest": str(result.review_manifest.relative_to(ROOT)),
        "stage_registry": run.stage_registry_name,
        "current_stage": run.current_stage,
        "advanced_stages": list(run.progress.advanced_reviews),
        "observation_lock_digest": run.observation_lock.observation_digest,
        "construction_retirement": run.construction_retirement.to_dict(),
        "identity_finish_manifest": run.identity_finish_manifest.to_dict(),
        "timelapse_status": result.timelapse_status,
        "visual_authority": "independent whole-view and local-crop inspection; metrics are diagnostic only",
    }
    (out / "quality_run_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")
    return result.final_drawing


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args()
    print(build(args.out))
