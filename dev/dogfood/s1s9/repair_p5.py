from __future__ import annotations

import json
from pathlib import Path

from img2drawing import DrawingRun
from run_s1s9 import S, L, OUT


def repair():
    run = DrawingRun.resume(OUT)
    run.reopen_stage(
        "P5_clean_blockin",
        reason=(
            "Fresh final residual sweep found two P5-purpose mismatches: the fully visible "
            "near sleeve lacked a decisive inner contour, and rifle scope/receiver/stock "
            "topology still read as two generic rails."
        ),
        discovered_in_stage="P5_clean_blockin",
        findings=(
            "near-arm contour ownership is under-explained at clean-block-in scale",
            "attached-object topology needs stronger width-change and stock-cutout breaks",
        ),
    )
    run.stage_start("P5_clean_blockin")
    run.draw_many([
        S("P5R-A1", "P5_clean_blockin", "repair_hair_left_open", [[242, 30], [225, 33], [207, 42], [191, 56], [178, 74], [170, 94], [170, 115], [178, 135], [191, 151]], role="contour", pressure=.74, width=2.9, opacity=.86, grade="B", preset="form_pencil", layer=20, source="Reopened P5: segmented bob contour keeps hair from reading as a closed generic egg."),
        S("P5R-A2", "P5_clean_blockin", "repair_hair_right_open", [[242, 30], [261, 34], [278, 46], [290, 64], [295, 86], [293, 110], [286, 134], [274, 153], [263, 163]], role="contour", pressure=.74, width=2.9, opacity=.86, grade="B", preset="form_pencil", layer=20, source="Reopened P5: asymmetric short-bob contour hands off to the collar at the jaw."),
        S("P5R-A3", "P5_clean_blockin", "repair_hair_jaw_overlap", [[205, 63], [216, 75], [230, 81], [246, 82], [261, 88], [273, 101]], role="internal_break", pressure=.50, width=2.15, opacity=.59, grade="HB", source="Major hair-to-face break preserves the back-three-quarter head turn without facial features."),
        S("P5R-A4", "P5_clean_blockin", "repair_near_sleeve_outer", [[264, 157], [279, 177], [291, 207], [303, 239], [312, 272], [316, 303], [314, 332], [307, 358]], role="contour", pressure=.74, width=3.0, opacity=.87, grade="B", preset="form_pencil", layer=20, source="Reopened P5: near sleeve outer silhouette is fully visible and broad."),
        S("P5R-A5", "P5_clean_blockin", "repair_near_sleeve_inner", [[270, 166], [281, 194], [291, 224], [300, 254], [304, 284], [304, 313], [300, 337], [293, 352]], role="overlap_contour", pressure=.62, width=2.45, opacity=.69, grade="HB", preset="form_pencil", layer=20, source="Reopened P5: inner sleeve contour makes the exposed upper arm/forearm width explicit instead of a thin distant line."),
        S("P5R-A6", "P5_clean_blockin", "repair_pocket_hand", [[296, 327], [303, 334], [311, 344], [310, 354], [303, 361], [294, 358], [290, 348]], role="internal_break", pressure=.52, width=2.1, opacity=.58, grade="HB", source="Reopened P5: hand enters the pocket/waist overlap, no fingers."),
        S("P5R-A7", "P5_clean_blockin", "repair_rifle_left", [[113, 44], [113, 69], [117, 88], [133, 96], [136, 126], [141, 160], [147, 197], [157, 238], [169, 281], [182, 329], [194, 373], [207, 416], [221, 440]], role="contour", pressure=.74, width=3.0, opacity=.86, grade="B", preset="form_pencil", layer=20, source="Reopened P5: rifle left contour retains suppressor-to-stock width changes."),
        S("P5R-A8", "P5_clean_blockin", "repair_rifle_right", [[131, 44], [132, 69], [136, 88], [151, 99], [154, 128], [161, 158], [178, 168], [185, 203], [192, 243], [201, 284], [212, 328], [225, 373], [240, 430]], role="contour", pressure=.74, width=3.0, opacity=.86, grade="B", preset="form_pencil", layer=20, source="Reopened P5: rifle right contour keeps scope, receiver, and skeleton stock steps."),
        S("P5R-A9", "P5_clean_blockin", "repair_rifle_scope_break", [[149, 149], [160, 153], [177, 160], [184, 174], [182, 194], [162, 198]], role="internal_break", pressure=.56, width=2.25, opacity=.63, grade="HB", source="Reopened P5: scope/receiver mass break prevents the prop from becoming generic rails."),
        S("P5R-A10", "P5_clean_blockin", "repair_rifle_stock_cutout", [[193, 374], [207, 370], [221, 378], [233, 395], [226, 409], [211, 401], [199, 389]], role="internal_break", pressure=.56, width=2.25, opacity=.63, grade="HB", source="Reopened P5: major stock cutout and body overlap are stated without micro-detail."),
        S("P5R-A11", "P5_clean_blockin", "repair_collar_break", [[216, 151], [225, 158], [239, 162], [254, 160], [264, 153]], role="internal_break", pressure=.47, width=2.0, opacity=.54, grade="HB", source="Reopened P5: raised collar separates neck from jacket and strengthens the back view."),
    ])
    run.draw_many([
        L("P5R-L1", "P5_clean_blockin", "crown_face_spine_support", [[242, 28], [225, 220], [205, 708]], reason="Retire the original dominant construction after P5 repair.", strength=.55),
        L("P5R-L2", "P5_clean_blockin", "shoulder_axis", [[178, 162], [304, 180]], reason="Retire shoulder axis beneath reopened clean contour.", strength=.62),
        L("P5R-L3", "P5_clean_blockin", "pelvis_axis", [[167, 376], [305, 413]], reason="Retire pelvis axis beneath reopened clean contour.", strength=.62),
        L("P5R-L4", "P5_clean_blockin", "near_arm_direction", [[282, 171], [306, 356]], reason="Retire near-arm axis after inner and outer clean contours are explicit.", strength=.62),
    ])
    artifacts = run.prepare_stage_review()
    locals_ = [
        run.prepare_local_review(
            label="repaired_silhouette_handoffs",
            intent="Freshly inspect bob-hair/jacket, broad near sleeve, hand/pocket, and rifle/body contour ownership after P5 reopen.",
            subject_box=(220, 20, 800, 980), drawing_box=(95, 0, 400, 500), grammar_box=(0, 0, 289, 576),
        ),
        run.prepare_local_review(
            label="repaired_prop_arms",
            intent="Freshly inspect near-arm width and rifle scope/receiver/stock topology against the subject.",
            subject_box=(220, 100, 760, 900), drawing_box=(95, 40, 370, 470), grammar_box=(0, 0, 289, 576),
        ),
    ]
    run.submit_stage_review(
        contract_findings=("P5 repair remains clean-block-in scope: decisive silhouette, major overlap breaks, simple hand silhouette, and construction retirement only.",),
        subject_findings=("Fresh final sweep confirms the subject's short bob, fully visible image-right sleeve, and rifle topology require separate contour ownership.",),
        exemplar_findings=("Failed P5 exemplar remains warning-only; repair uses no shading, texture, seams, fingers, or facial features.",),
        drawing_findings=("The reopened P5 now shows a broad near sleeve with an explicit inner contour and rifle scope/stock breaks rather than two generic rails.",),
        local_review_ids=tuple(item.local_review_id for item in locals_),
        corrections=("added near-sleeve inner contour", "strengthened rifle topology breaks", "segmented bob hair handoff"),
        remaining_concerns=(), decision="advance",
        advance_rationale="Fresh post-reopen local reviews clear the two P5 residual mismatches without moving any upstream mass or axis.",
    )
    result = run.finish(final_supersample=4, timelapse="full")
    report = OUT / "DOGFOOD_REPORT.md"
    report.write_text(
        report.read_text(encoding="utf-8")
        + "\n## P5 residual recovery\n\n"
        "The first final sweep kept P5 open conceptually because near-arm contour ownership and rifle topology were under-explained. "
        "P5 was reopened, the clean contour rebuilt, and a fresh review advanced the repaired branch.\n"
        f"- Repaired final: `{result.final_drawing}`\n"
        f"- Repaired timelapse: `{result.timelapse_gif}`\n",
        encoding="utf-8",
    )
    print(json.dumps({"output": str(OUT), "final": str(result.final_drawing), "gif": str(result.timelapse_gif)}, indent=2))


if __name__ == "__main__":
    repair()
