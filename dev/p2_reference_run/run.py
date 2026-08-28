from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from img2drawing import DrawingRun, ObservationContract, ViewObservation


HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parents[1]
SUBJECT = PROJECT_ROOT / "skills" / "img2drawing" / "examples" / "full_body_croquis" / "subject.png"
TARGET = PROJECT_ROOT / "skills" / "img2drawing" / "examples" / "full_body_croquis" / "p1_target.png"
CANVAS_SIZE = (512, 802)
SUBJECT_SIZE = (735, 1152)
TARGET_SIZE = (1002, 1570)


def _subject_box(drawing_box: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    """Map a canvas ROI to the same normalized region in the source image."""
    sx = SUBJECT_SIZE[0] / CANVAS_SIZE[0]
    sy = SUBJECT_SIZE[1] / CANVAS_SIZE[1]
    left, top, right, bottom = drawing_box
    return (
        round(left * sx),
        round(top * sy),
        round(right * sx),
        round(bottom * sy),
    )


def _target_box(drawing_box: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    """Map a canvas ROI into the user-approved P1 target overlay."""
    sx = TARGET_SIZE[0] / CANVAS_SIZE[0]
    sy = TARGET_SIZE[1] / CANVAS_SIZE[1]
    left, top, right, bottom = drawing_box
    return (
        round(left * sx),
        round(top * sy),
        round(right * sx),
        round(bottom * sy),
    )


def _stroke(
    action_id,
    part,
    points,
    *,
    stage="P1_gesture",
    role="construction",
    pressure=.18,
    width=1.1,
    opacity=.22,
    grade="2H",
    confidence=.84,
    source="Canonical-example visual observation.",
):
    return {
        "action_id": action_id,
        "kind": "draw_stroke",
        "stage": stage,
        "role": role,
        "part": part,
        "points": points,
        "stroke_id": part,
        "confidence": confidence,
        "layer": 10,
        "tool": {
            "preset": "construction_pencil",
            "grade": grade,
            "overrides": {
                "pressure": pressure,
                "width": width,
                "opacity": opacity,
            },
        },
        "observation_id": "canonical-" + action_id,
        "source_observation": source,
    }


def _replace(
    action_id,
    part,
    points,
    *,
    stage="P1_gesture",
    reason,
    role="gesture",
    pressure=.42,
    width=1.9,
    opacity=.62,
    grade="HB",
):
    return {
        "action_id": action_id,
        "kind": "replace_stroke",
        "stage": stage,
        "role": role,
        "part": part,
        "points": points,
        "target_stroke_id": part,
        "stroke_id": part,
        "confidence": .94,
        "layer": 10,
        "tool": {
            "preset": "construction_pencil",
            "grade": grade,
            "overrides": {
                "pressure": pressure,
                "width": width,
                "opacity": opacity,
            },
        },
        "observation_id": "canonical-" + action_id,
        "source_observation": "Fresh re-observation after the previous review.",
        "reason": reason,
        "revision_of": part,
    }


def _joint_points(centre):
    cx, cy = centre
    return [
        [cx + 5, cy], [cx + 4, cy + 3], [cx + 2, cy + 5],
        [cx - 2, cy + 5], [cx - 4, cy + 3], [cx - 5, cy],
        [cx - 4, cy - 3], [cx - 2, cy - 5], [cx + 2, cy - 5],
        [cx + 4, cy - 3], [cx + 5, cy],
    ]


def _joint(action_id, part, centre, *, source):
    return _stroke(
        action_id,
        part,
        _joint_points(centre),
        grade="HB",
        pressure=.44,
        width=2.0,
        opacity=.55,
        source=source,
    )


def _p2_axis(
    action_id,
    part,
    points,
    *,
    role="axis",
    pressure=.42,
    width=1.8,
    opacity=.52,
    grade="HB",
    source="Fresh subject measurement for P2 primary axes.",
):
    return _stroke(
        action_id,
        part,
        points,
        stage="P2_primary_axes",
        role=role,
        pressure=pressure,
        width=width,
        opacity=opacity,
        grade=grade,
        confidence=.91,
        source=source,
    )


def _delete_stroke(
    action_id,
    target_stroke_id,
    *,
    reason,
):
    """Retire a fully superseded stroke while keeping its history event."""
    return {
        "action_id": action_id,
        "kind": "delete_stroke",
        "stage": "P2_primary_axes",
        "target_stroke_id": target_stroke_id,
        "confidence": .96,
        "tool": {
            "preset": "hard_eraser",
            "grade": "HB",
        },
        "observation_id": "canonical-" + action_id,
        "source_observation": "Fresh P2 review after the placement block was drawn.",
        "reason": reason,
        "revision_of": target_stroke_id,
    }


def _prepare_local_reviews(run: DrawingRun, *, fresh: bool):
    prefix = "Re-check" if fresh else "Check"
    specs = (
        ("head_face", f"{prefix} crown, observed head shape, pupil line and nose pass.", (220, 10, 310, 140)),
        ("torso_rhythm", f"{prefix} the subordinate cervical-to-sacral spine curve, shoulder/pelvis counter-tilt and torso rhythm.", (185, 120, 330, 430)),
        ("pelvis_support", f"{prefix} pelvis counter-tilt, both hip centres and weight transfer into the image-left support foot.", (195, 355, 410, 802)),
        ("arm_left_flow", f"{prefix} image-left shoulder, elbow, visible wrist and curved hanging-arm flow.", (140, 140, 220, 455)),
        ("arm_right_flow", f"{prefix} image-right shoulder, elbow and partly occluded pocket-hand flow.", (280, 125, 380, 355)),
        ("legs_chain", f"{prefix} each single hip-knee-ankle centre-path curve, shoe direction and ground contact.", (195, 390, 410, 802)),
    )
    reviews = []
    for label, intent, drawing_box in specs:
        reviews.append(run.prepare_local_review(
            label=label,
            intent=intent,
            subject_box=_subject_box(drawing_box),
            drawing_box=drawing_box,
            task_target_box=_target_box(drawing_box),
        ))
    return reviews


def _prepare_p2_local_reviews(run: DrawingRun, *, fresh: bool):
    """Select P2 crops that test measured axes, boxes and endpoint blocks."""
    prefix = "Re-check" if fresh else "Check"
    specs = (
        ("neck_ribcage", f"{prefix} the independently measured neck axis and turned ribcage box.", (180, 115, 320, 335)),
        ("ribcage_pelvis", f"{prefix} ribcage-to-pelvis axis continuity and box turns without clothing contour.", (175, 155, 315, 405)),
        ("arm_segments", f"{prefix} both shoulder→elbow→wrist segment lengths and the pocket-hand placement.", (135, 135, 375, 435)),
        ("leg_segments", f"{prefix} hip→knee→ankle measured spans and foreshortening on both legs.", (185, 335, 395, 750)),
        ("hand_blocks", f"{prefix} both hand placement blocks, including the partly occluded pocket hand.", (135, 300, 320, 455)),
        ("foot_blocks", f"{prefix} foot blocks, toe directions and ground contact inherited from P1.", (195, 670, 410, 802)),
    )
    reviews = []
    for label, intent, drawing_box in specs:
        reviews.append(run.prepare_local_review(
            label=label,
            intent=intent,
            subject_box=_subject_box(drawing_box),
            drawing_box=drawing_box,
        ))
    return reviews


def run_example(output_dir: str | Path, *, clean=True) -> dict:
    """Canonical P1→P2 hardening example for the bundled subject."""
    output = Path(output_dir).resolve()
    if clean and output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)

    run = DrawingRun.create(
        SUBJECT,
        output,
        width=CANVAS_SIZE[0],
        height=CANVAS_SIZE[1],
        working_supersample=3,
        session_id="canonical-full-body-croquis-r10-target-rebuild",
        task_stage_targets={"P1_gesture": TARGET},
    )
    run.lock_observation(ObservationContract(
        subject_summary=(
            "Full-body front three-quarter standing subject. The image-left leg carries "
            "the weight; the image-right leg steps out. The image-left arm hangs while "
            "the image-right arm bends into the trouser pocket."
        ),
        global_relations={
            "canvas_basis": "All listed coordinates were observed on the 512x802 working canvas.",
            "weight_side": "image_left",
            "counterbalance_side": "image_right",
            "shoulder_tilt": "image-left shoulder lower; image-right shoulder higher",
            "pelvis_tilt": "image-left hip higher; image-right hip lower",
            "head_direction": "slight turn toward image-left with a small downward tilt",
            "prop": "none",
        },
        parts={
            "head_landmarks": {
                "crown": [264, 29],
                "pupils": [[251, 70], [275, 74]],
                "nose": [263, 87],
                "chin": [258, 118],
            },
            "joint_centres": {
                "image_left": {
                    "shoulder": [184, 175], "elbow": [169, 301],
                    "wrist": [158, 413], "hip": [198, 358],
                    "knee": [212, 524], "ankle": [233, 696],
                },
                "image_right": {
                    "shoulder": [311, 153], "elbow": [350, 263],
                    "wrist": [294, 331], "hip": [287, 364],
                    "knee": [311, 524], "ankle": [350, 724],
                },
            },
            "feet": {
                "image_left": "weight-bearing shoe points across the body toward image-left",
                "image_right": "lower stepped-out shoe points toward the viewer and image-right",
            },
        },
        uncertainties=(
            "Loose denim obscures exact knee contours; knee centres are inferred from each hip-to-ankle chain.",
            "The pocket and sleeve partly hide the image-right wrist and hand endpoint.",
        ),
        drawing_priorities=(
            "head direction from pupils and nose",
            "balanced face, spine, shoulder and pelvis line hierarchy",
            "support versus counterbalance leg",
            "one centre-path curve per limb through its joint centres",
            "subject-specific foot landing",
        ),
        evidence_refs=(
            "subject.png whole view normalized to 512x802",
            "p1_target.png user-approved task-stage target normalized to 512x802",
        ),
        view=ViewObservation(
            body_view="front_three_quarter",
            torso_turn="left",
            near_side="subject_left",
            arm_visibility={"subject_left": "partial", "subject_right": "visible"},
            arm_occlusion={
                "subject_left": (
                    "wrist partly covered by cardigan cuff",
                    "hand partly inside trouser pocket",
                ),
                "subject_right": (),
            },
            uncertainties=(
                "Near-side assignment follows the larger image-right sleeve and shoulder exposure.",
            ),
        ),
    ))

    run.stage_start("P1_gesture")

    # The subject supplies every coordinate. The stage reference supplies only
    # vocabulary, hierarchy and the P1 detail boundary.
    initial_head_outline = [
        [264, 29], [276, 31], [286, 38], [293, 49], [296, 63],
        [295, 78], [291, 91], [284, 104], [276, 114], [266, 120],
        [258, 118], [249, 111], [242, 102], [236, 91], [232, 78],
        [231, 65], [234, 52], [240, 42], [250, 34], [260, 30], [264, 29],
    ]
    facial_centreline = [
        [264, 29], [265, 45], [265, 61], [264, 74],
        [263, 87], [261, 100], [259, 111], [258, 118],
    ]
    eye_line = [
        [215, 66], [232, 67], [251, 70], [263, 72],
        [275, 74], [287, 77], [294, 79],
    ]

    # Pass 1 is a fresh target-registered centre-path construction. Its review
    # deliberately tests the uncertain pelvis/hip separation before advancing.

    strokes = [
        _stroke(
            "EX-P1-A1", "head_outline", initial_head_outline,
            grade="HB", pressure=.52, width=2.3, opacity=.66,
            source="Pass-1 cranium and jaw hypothesis; retained for review because it may be too symmetric.",
        ),
        _stroke(
            "EX-P1-A2", "facial_centreline", facial_centreline,
            grade="B", pressure=.62, width=2.65, opacity=.80,
            source="Curved facial centreline through crown, between the pupils, nose, mouth and chin.",
        ),
        _stroke(
            "EX-P1-A3", "eye_line", eye_line,
            grade="HB", pressure=.48, width=2.15, opacity=.60,
            source="Wrapped eye line anchored independently on both pupils.",
        ),
        _stroke(
            "EX-P1-NECK-L", "neck_connection_left",
            [[249, 109], [247, 116], [245, 123]],
            grade="HB", pressure=.38, width=1.8, opacity=.46,
            source="Short visible image-left jaw-to-neck attachment; it stops before the clavicle and shoulder.",
        ),
        *(
            _stroke(
                f"EX-P1-SPINE-{index:02d}", f"spine_centreline_dash_{index:02d}", dash,
                grade="HB", pressure=.40, width=1.9, opacity=.54,
                source="Dashed subordinate cervical-to-sacral S-curve registered to the approved P1 target.",
            )
            for index, dash in enumerate((
                [[255, 116], [252, 135]],
                [[249, 148], [245, 169]],
                [[242, 182], [241, 204]],
                [[242, 217], [246, 239]],
                [[250, 251], [254, 271]],
                [[254, 284], [251, 306]],
                [[248, 319], [244, 341]],
                [[242, 350], [241, 362]],
            ), start=1)
        ),
        _stroke(
            "EX-P1-SHOULDER", "shoulder_line",
            [[184, 175], [212, 170], [245, 164], [278, 158], [311, 153]],
            grade="HB", pressure=.52, width=2.2, opacity=.64,
            source="Observed shoulder rhythm: image-left lower and image-right higher.",
        ),
        _stroke(
            "EX-P1-PELVIS", "pelvis_centreline",
            [[207, 370], [226, 368], [246, 369], [266, 371], [284, 374]],
            grade="HB", pressure=.52, width=2.2, opacity=.64,
            source="Pelvis counter-tilt through femoral-head centres inferred just above the crotch, below the waistband.",
        ),
        _stroke(
            "EX-P1-ARM-L", "arm_left_flow",
            [[184, 175], [180, 209], [176, 251], [169, 301], [166, 342], [162, 382], [158, 413]],
            grade="HB", pressure=.56, width=2.45, opacity=.70,
            source="Single centre-path curve through the image-left shoulder, elbow and visible wrist; it does not trace sleeve width.",
        ),
        _stroke(
            "EX-P1-ARM-R", "arm_right_flow",
            [[311, 153], [323, 174], [337, 204], [347, 235], [350, 263], [342, 283], [327, 302], [310, 318], [294, 331]],
            grade="HB", pressure=.56, width=2.45, opacity=.70,
            source="Single centre-path curve through the image-right shoulder, inferred elbow and pocket wrist; it ignores the cardigan's outer bulge.",
        ),
        _stroke(
            "EX-P1-LEG-L", "leg_left_flow",
            [[207, 370], [207, 409], [208, 451], [210, 492], [214, 532], [220, 574], [225, 616], [229, 658], [233, 696]],
            grade="HB", pressure=.58, width=2.5, opacity=.72,
            source="Single centre-path curve through the image-left weight-bearing hip, knee and ankle; it is independent of both trouser edges.",
        ),
        _stroke(
            "EX-P1-LEG-R", "leg_right_flow",
            [[284, 374], [291, 408], [298, 448], [305, 488], [311, 524], [320, 567], [330, 611], [340, 668], [350, 724]],
            grade="HB", pressure=.58, width=2.5, opacity=.72,
            source="Single centre-path curve through the image-right hip, knee and ankle, preserving the stepped-out sweep without tracing trouser width.",
        ),
    ]

    joint_specs = (
        ("EX-P1-J-SHOULDER-L", "joint_shoulder_L", (184, 175), "Image-left shoulder centre."),
        ("EX-P1-J-SHOULDER-R", "joint_shoulder_R", (311, 153), "Image-right shoulder centre."),
        ("EX-P1-J-ELBOW-L", "joint_elbow_L", (169, 301), "Image-left elbow centre."),
        ("EX-P1-J-ELBOW-R", "joint_elbow_R", (350, 263), "Image-right elbow inferred inside the cardigan, not at its outer bulge."),
        ("EX-P1-J-WRIST-L", "joint_wrist_L", (158, 413), "Visible image-left wrist below the cuff."),
        ("EX-P1-J-WRIST-R", "joint_wrist_R", (294, 331), "Inferred image-right wrist at the pocket hand."),
        ("EX-P1-J-HIP-L", "joint_hip_L", (207, 370), "Pass-1 image-left femoral-head estimate for target review."),
        ("EX-P1-J-HIP-R", "joint_hip_R", (284, 374), "Pass-1 image-right femoral-head estimate for target review."),
        ("EX-P1-J-PELVIS-C", "joint_pelvis_centre", (241, 362), "Sacral centre at the end of the subordinate spine cue."),
        ("EX-P1-J-KNEE-L", "joint_knee_L", (214, 532), "Pass-1 image-left knee estimate along the support chain."),
        ("EX-P1-J-KNEE-R", "joint_knee_R", (311, 524), "Image-right knee centre inferred along the counterbalance chain."),
        ("EX-P1-J-ANKLE-L", "joint_ankle_L", (233, 696), "Image-left ankle at the jean hem."),
        ("EX-P1-J-ANKLE-R", "joint_ankle_R", (350, 724), "Image-right ankle at the jean hem."),
    )
    strokes.extend(_joint(action_id, part, centre, source=source)
                   for action_id, part, centre, source in joint_specs)
    strokes.extend([
        _stroke(
            "EX-P1-FOOT-LINK-L", "ankle_foot_link_left", [[233, 696], [230, 702], [226, 708]],
            grade="HB", pressure=.46, width=2.05, opacity=.56,
            source="Connection from the support ankle into its observed shoe direction.",
        ),
        _stroke(
            "EX-P1-FOOT-L", "foot_direction_left",
            [[233, 696], [226, 707], [214, 724], [227, 730], [233, 696]],
            grade="HB", pressure=.50, width=2.2, opacity=.62,
            source="Observed support shoe: a compact wedge pointing across the body toward image-left.",
        ),
        _stroke(
            "EX-P1-FOOT-LINK-R", "ankle_foot_link_right", [[350, 724], [351, 732], [354, 739]],
            grade="HB", pressure=.46, width=2.05, opacity=.56,
            source="Connection from the counterbalance ankle into its observed shoe direction.",
        ),
        _stroke(
            "EX-P1-FOOT-R", "foot_direction_right",
            [[350, 724], [354, 739], [362, 756], [379, 751], [374, 743],
             [364, 735], [350, 724]],
            grade="HB", pressure=.50, width=2.2, opacity=.62,
            source="Observed stepped-out shoe: broader and more frontal than the support shoe.",
        ),
        _stroke(
            "EX-P1-GROUND-L", "ground_contact_left", [[205, 740], [239, 741]],
            grade="2H", pressure=.36, width=1.7, opacity=.42,
            source="Ground contact under the image-left weight-bearing shoe.",
        ),
        _stroke(
            "EX-P1-GROUND-R", "ground_contact_right", [[350, 783], [392, 783]],
            grade="2H", pressure=.36, width=1.7, opacity=.42,
            source="Lower ground contact under the image-right stepped-out shoe.",
        ),
    ])
    run.draw_many(strokes)

    run.prepare_stage_review()
    pass1_locals = _prepare_local_reviews(run, fresh=False)
    pass1 = run.submit_stage_review(
        task_target_findings=[
            "The approved target fixes the intended P1 geometry: asymmetric head, subordinate spine, counter-tilted shoulder/pelvis lines, lateral hip markers, one path per limb and wedge-like foot directions.",
            "Registered pelvis and leg crops show that the pass-1 pelvis/hip row does not yet match the target separation.",
        ],
        contract_findings=[
            "The artifact stays inside P1.v6: centrelines, joint evidence, exactly one centre-path curve per limb, foot direction and ground contact only.",
            "No limb is bracketed by paired lines that could read as sleeve, trouser or body width.",
            "No hair, garment structure, facial detail, resolved mass or footwear detail was introduced.",
        ],
        subject_findings=[
            "The subject transfers weight through the image-left hip, knee and compact cross-body shoe; the image-right leg steps lower and outward.",
            "The torso is not a single diagonal: it reverses gently from head and ribcage through pelvis before settling into the support side.",
            "The anatomical spine shows a cervical-to-thoracic-to-lumbar reversal even though clothing hides its literal contour.",
        ],
        grammar_findings=[
            "Each arm and leg should read as one curved centre path through its three joint centres.",
            "Face, spine, shoulder, pelvis and limb flows should remain mutually readable; the spine is not a dominant black pole.",
        ],
        drawing_findings=[
            "The fresh head, face, shoulder and arm construction agrees with the approved target overlay.",
            "The pass-1 pelvis line was mistakenly placed through the hip joints instead of across the observed pelvic crest.",
            "Both pass-1 femoral heads are too medial and too low relative to the target, so the leg paths start inside the trousers rather than at the lateral hip centres.",
            "The image-left knee is also slightly low; the lower chain consequently misses the target's support-leg sweep.",
        ],
        local_review_ids=[item.local_review_id for item in pass1_locals],
        corrections=[],
        remaining_concerns=[
            "pelvis line is too low and incorrectly passes through the hip markers",
            "both femoral-head markers and leg origins are too medial and low",
            "image-left knee and support-leg curvature do not match the approved target",
        ],
        decision="revise",
    )

    corrected_pelvis = [
        [187, 332], [213, 335], [241, 339], [270, 343], [299, 347],
    ]
    corrected_leg_left = [
        [198, 358], [200, 399], [204, 442], [208, 484], [212, 524],
        [216, 567], [222, 612], [228, 657], [233, 696],
    ]
    corrected_leg_right = [
        [287, 364], [293, 404], [299, 447], [305, 488], [311, 524],
        [319, 566], [329, 611], [340, 668], [350, 724],
    ]
    run.draw_many([
        _replace(
            "EX-P1-R1-PELVIS", "pelvis_centreline", corrected_pelvis,
            reason=(
                "The target separates the pelvic crest from the femoral heads. The replacement moves the pelvis line upward to the observed counter-tilted crest."
            ),
            grade="HB", pressure=.52, width=2.2, opacity=.64,
        ),
        _replace(
            "EX-P1-R1-HIP-L", "joint_hip_L", _joint_points((198, 358)),
            reason=(
                "Fresh target registration places the image-left femoral head laterally below the waistband and above the crotch."
            ),
            role="construction", grade="HB", pressure=.44, width=2.0, opacity=.55,
        ),
        _replace(
            "EX-P1-R1-HIP-R", "joint_hip_R", _joint_points((287, 364)),
            reason="Fresh target registration places the image-right femoral head laterally below the waistband and above the crotch.",
            role="construction", grade="HB", pressure=.44, width=2.0, opacity=.55,
        ),
        _replace(
            "EX-P1-R1-KNEE-L", "joint_knee_L", _joint_points((212, 524)),
            reason="The support knee is raised to the target-registered centre before redrawing the leg path.",
            role="construction", grade="HB", pressure=.44, width=2.0, opacity=.55,
        ),
        _replace(
            "EX-P1-R1-LEG-L", "leg_left_flow", corrected_leg_left,
            reason=(
                "The replacement begins at the corrected lateral hip, passes through the raised knee, and preserves the target's quiet support-leg sweep."
            ),
            grade="HB", pressure=.58, width=2.5, opacity=.72,
        ),
        _replace(
            "EX-P1-R1-LEG-R", "leg_right_flow", corrected_leg_right,
            reason=(
                "The replacement begins at the corrected lateral hip and preserves the target's outward counterbalance sweep through knee and ankle."
            ),
            grade="HB", pressure=.58, width=2.5, opacity=.72,
        ),
    ])

    run.prepare_stage_review()
    pass2_locals = _prepare_local_reviews(run, fresh=True)
    pass2_memory = json.loads(
        (output / "reviews/P1_gesture/pass_02/pass_memory.json").read_text(encoding="utf-8")
    )
    carried_concerns = [
        "pelvis line is too low and incorrectly passes through the hip markers",
        "both femoral-head markers and leg origins are too medial and low",
        "image-left knee and support-leg curvature do not match the approved target",
    ]
    correction_ids = [
        "EX-P1-R1-PELVIS", "EX-P1-R1-HIP-L", "EX-P1-R1-HIP-R", "EX-P1-R1-KNEE-L",
        "EX-P1-R1-LEG-L", "EX-P1-R1-LEG-R",
    ]
    assert pass2_memory["state"] == "revision_continuation"
    assert pass2_memory["previous_decision"] == "revise"
    assert pass2_memory["carried_concerns"] == carried_concerns
    assert [item["action_id"] for item in pass2_memory["inter_pass_correction_actions"]] == correction_ids

    pass2 = run.submit_stage_review(
        task_target_findings=[
            "Fresh three-way reviews align the corrected pelvic crest, lateral femoral heads, knees, ankles and foot directions with the approved target overlay.",
            "The final drawing keeps the target's sparse P1 vocabulary without copying the photograph's garment contours.",
        ],
        contract_findings=[
            "The corrected artifact remains inside the P1.v6 representation boundary.",
            "Only the pelvis line, three joint markers and two leg centre paths were replaced; no downstream vocabulary was introduced.",
            "Every limb remains one centre-path curve through its joint centres, with no garment-width pair.",
        ],
        subject_findings=[
            "The head outline places unequal jaw turns around the nose-anchored centreline and preserves the subject's slight downward three-quarter turn.",
            "The subordinate spine starts behind the neck and remains readable through the shoulder/pelvis counter-tilt without becoming the pose itself.",
            "The image-left leg stacks hip-knee-ankle over the support shoe while the image-right chain sweeps outward into the lower frontal shoe.",
        ],
        grammar_findings=[
            "The face, spine, shoulder, pelvis and limb flows now share a readable construction hierarchy.",
            "Single limb centre paths communicate curvature without being mistaken for sleeve, trouser or limb width.",
            "Observed head and shoe shapes remain subject-specific rather than generic ellipses.",
        ],
        drawing_findings=[
            "All three carried concerns were checked against fresh whole and registered local evidence and are visibly resolved.",
            "The three-way pelvis crop now agrees on a high counter-tilted pelvis line with separate lateral femoral-head markers below it.",
            "The leg crop shows exactly one curve passing through each hip, knee and ankle marker rather than two lines following the jeans.",
            "Each leg curve changes tangent across the knee instead of behaving like a measured P2 segment axis.",
            "A residual sweep found no new P1-purpose mismatch in crown, face direction, joint placement, limb presence, foot landing or weight side.",
            "With the subject hidden, the asymmetrical shoulders, pocket arm, hanging arm, support leg and stepped-out leg identify this specific pose.",
        ],
        local_review_ids=[item.local_review_id for item in pass2_locals],
        corrections=[
            "Raised the pelvis line from the hip row to the observed pelvic crest.",
            "Moved both femoral heads laterally and raised the image-left knee from fresh target registration.",
            "Redrew both legs as single curves through the corrected joint centres.",
        ],
        remaining_concerns=[],
        decision="advance",
        advance_rationale=(
            "Fresh pass-2 whole and coordinate-registered local evidence clears all "
            "carried concerns. A separate residual sweep finds the subject's "
            "head direction, weight side, joint chains, limb flows and foot landings "
            "specific enough for independent P2 measurement."
        ),
    )

    # P2 starts only after the P1 review has advanced.  These are measured axes,
    # not a second copy of the P1 gesture: the P1 curves stay visible underneath
    # as pose evidence while P2 states span, foreshortening and turn.
    run.stage_start("P2_primary_axes")
    p2_strokes = [
        _p2_axis(
            "EX-P2-A1", "neck_axis",
            [[258, 118], [258, 131], [255, 147], [250, 164]],
            source="Fresh subject measurement from the chin base into the upper ribcage; independent of the short P1 jaw cue.",
        ),
        _p2_axis(
            "EX-P2-A2", "ribcage_centre_axis",
            [[250, 164], [250, 201], [250, 240], [250, 280], [250, 319]],
            role="construction", pressure=.36, width=1.6, opacity=.42, grade="H",
            source="Initial measured ribcage centre axis; the first pass tests the torso turn before correction.",
        ),
        _p2_axis(
            "EX-P2-A3", "ribcage_box_top",
            [[202, 176], [229, 171], [260, 165], [297, 160]],
            role="construction", pressure=.28, width=1.25, opacity=.34, grade="2H",
            source="Open upper ribcage cross-axis registered to the shoulder span, not a jacket edge.",
        ),
        _p2_axis(
            "EX-P2-A4", "ribcage_box_left",
            [[202, 176], [198, 215], [195, 258], [194, 311]],
            role="construction", pressure=.24, width=1.15, opacity=.29, grade="2H",
            source="Left side of the open ribcage box, stopping at the measured lower station before the garment contour.",
        ),
        _p2_axis(
            "EX-P2-A5", "ribcage_box_right",
            [[297, 160], [298, 204], [296, 250], [291, 327]],
            role="construction", pressure=.24, width=1.15, opacity=.29, grade="2H",
            source="Right side of the open ribcage box, turned toward the near shoulder without tracing the cardigan.",
        ),
        _p2_axis(
            "EX-P2-A6", "ribcage_box_bottom",
            [[194, 311], [222, 317], [255, 322], [291, 327]],
            role="construction", pressure=.28, width=1.25, opacity=.34, grade="2H",
            source="Lower ribcage cross-axis, stating the box turn above the pelvic crest.",
        ),
        _p2_axis(
            "EX-P2-A7", "pelvis_axis",
            [[241, 339], [240, 356], [239, 374], [238, 388]],
            role="construction", pressure=.38, width=1.6, opacity=.43, grade="H",
            source="Measured pelvic centre axis through the corrected P1 crest and toward the crotch station.",
        ),
        _p2_axis(
            "EX-P2-A8", "pelvis_box_top",
            [[192, 335], [220, 338], [252, 342], [292, 348]],
            role="construction", pressure=.27, width=1.2, opacity=.33, grade="2H",
            source="Open pelvic crest axis; its down-image-right tilt agrees with the subject and P1 rhythm.",
        ),
        _p2_axis(
            "EX-P2-A9", "pelvis_box_left",
            [[192, 335], [198, 354], [204, 371], [210, 384]],
            role="construction", pressure=.22, width=1.1, opacity=.27, grade="2H",
            source="Left pelvic side station, ending before the thigh mass or jeans contour.",
        ),
        _p2_axis(
            "EX-P2-A10", "pelvis_box_right",
            [[292, 348], [288, 364], [284, 379], [280, 390]],
            role="construction", pressure=.22, width=1.1, opacity=.27, grade="2H",
            source="Right pelvic side station, shortened for the nearer turned side.",
        ),
        _p2_axis(
            "EX-P2-A11", "pelvis_box_bottom",
            [[210, 384], [234, 387], [258, 389], [280, 390]],
            role="construction", pressure=.27, width=1.2, opacity=.32, grade="2H",
            source="Lower pelvic cross-axis; an open placement box, not a finished trouser contour.",
        ),
        _p2_axis(
            "EX-P2-A12", "arm_left_upper_axis",
            [[184, 175], [169, 301]],
            source="Measured image-left upper-arm span from shoulder centre to elbow centre.",
        ),
        _p2_axis(
            "EX-P2-A13", "arm_left_forearm_axis",
            [[169, 301], [158, 413]],
            source="Measured image-left forearm span from elbow to the visible wrist below the cuff.",
        ),
        _p2_axis(
            "EX-P2-A14", "arm_right_upper_axis",
            [[311, 153], [350, 263]],
            source="Measured image-right upper-arm span; the elbow sits at the sleeve's bend, not its outermost bulge.",
        ),
        _p2_axis(
            "EX-P2-A15", "arm_right_forearm_axis",
            [[350, 263], [294, 331]],
            source="Measured image-right foreshortened forearm into the pocket-hand endpoint.",
        ),
        _p2_axis(
            "EX-P2-A16", "leg_left_thigh_axis",
            [[198, 358], [212, 524]],
            source="Measured image-left support thigh span from lateral femoral head to knee centre.",
        ),
        _p2_axis(
            "EX-P2-A17", "leg_left_shin_axis",
            [[212, 524], [233, 696]],
            source="Measured image-left support shin span to the ankle/hem station.",
        ),
        _p2_axis(
            "EX-P2-A18", "leg_right_thigh_axis",
            [[287, 364], [315, 532]],
            source="Initial measured image-right thigh span; the first pass intentionally checks the low knee registration.",
        ),
        _p2_axis(
            "EX-P2-A19", "leg_right_shin_axis",
            [[311, 524], [350, 724]],
            source="Measured image-right shin span from the subject's knee to the lower stepped-out ankle.",
        ),
        _p2_axis(
            "EX-P2-A20", "hand_left_block",
            [[155, 409], [164, 416], [162, 435], [153, 445], [148, 429], [155, 409]],
            role="construction", pressure=.30, width=1.35, opacity=.38, grade="2H",
            source="Small image-left hand placement block attached to the measured wrist; no finger detail.",
        ),
        _p2_axis(
            "EX-P2-A21", "hand_right_block",
            [[294, 327], [305, 333], [299, 349], [284, 344], [285, 333], [294, 327]],
            role="construction", pressure=.30, width=1.35, opacity=.38, grade="2H",
            source="Small pocket-hand placement block at the inferred wrist endpoint; the pocket occlusion remains explicit.",
        ),
        _p2_axis(
            "EX-P2-A22", "foot_left_block",
            [[233, 696], [223, 705], [213, 724], [215, 739], [236, 742], [251, 733], [245, 715], [233, 696]],
            role="construction", pressure=.31, width=1.4, opacity=.40, grade="2H",
            source="Image-left support-foot placement block; its toe wedge points image-left as observed in P1.",
        ),
        _p2_axis(
            "EX-P2-A23", "foot_right_block",
            [[350, 724], [354, 737], [369, 753], [392, 771], [398, 785], [372, 791], [351, 779], [344, 752], [350, 724]],
            role="construction", pressure=.31, width=1.4, opacity=.40, grade="2H",
            source="Image-right lower foot placement block; its longer toe wedge points toward image-right and the viewer.",
        ),
    ]
    run.draw_many(p2_strokes)
    run.prepare_stage_review()
    p2_pass1_locals = _prepare_p2_local_reviews(run, fresh=False)
    p2_pass1 = run.submit_stage_review(
        subject_findings=[
            "The subject's ribcage sits beneath the elevated image-right shoulder and turns gently back toward the image-left pelvis.",
            "The image-left leg is the support chain; the image-right thigh is shorter in the visible projection before its lower outward step.",
            "The pocket hand and both shoes are partially occluded placement problems, not opportunities for finished detail.",
        ],
        grammar_findings=[
            "P2 adds measured spans and open axis boxes while preserving the P1 flow and joint circles underneath.",
            "Hand and foot marks are placement blocks only; no clothing, hair, facial detail or finished contour is introduced.",
        ],
        drawing_findings=[
            "The neck, ribcage, pelvis, arms and support leg are registered to the observed joint chain.",
            "The first ribcage centre axis reads too vertical through the lower torso and needs a small image-left turn to agree with the subject's rotation.",
            "The first image-right thigh axis ends below the observed knee centre, weakening the measured foreshortening relationship.",
            "The P1 foot-direction wedges and the new P2 foot blocks overlap, creating a doubled shoe read that should be retired after the block takes over placement.",
        ],
        contract_findings=[
            "The artifact stays inside P2.v3: measured segment axes, open ribcage/pelvis axis volumes and hand/foot placement blocks only.",
            "P1 face, spine, pelvis rhythm, joint evidence and ground contact remain visible and unchanged; P1 foot-direction evidence remains in the prior/history while P2 blocks own the visible placement.",
            "No finished limb contour, clothing, hair, surface detail or shading was added.",
        ],
        local_review_ids=[item.local_review_id for item in p2_pass1_locals],
        corrections=[],
        remaining_concerns=[
            "ribcage centre axis is too vertical through the lower torso",
            "image-right thigh axis ends below the observed knee centre",
            "P1 foot-direction wedges and ankle links remain visible beneath the P2 foot blocks",
        ],
        decision="revise",
    )

    corrected_ribcage_axis = [[249, 164], [248, 201], [246, 240], [244, 280], [243, 319]]
    run.draw_many([
        _delete_stroke(
            "EX-P2-R1-DELETE-FOOT-LINK-L", "ankle_foot_link_left",
            reason="The P2 left-foot placement block now carries the ankle-to-foot connection; delete the superseded P1 link from the active canvas while retaining it in history.",
        ),
        _delete_stroke(
            "EX-P2-R1-DELETE-FOOT-L", "foot_direction_left",
            reason="The P2 left-foot block now carries the observed image-left toe direction; delete the superseded P1 wedge rather than displaying two shoe outlines.",
        ),
        _delete_stroke(
            "EX-P2-R1-DELETE-FOOT-LINK-R", "ankle_foot_link_right",
            reason="The P2 right-foot placement block now carries the ankle-to-foot connection; delete the superseded P1 link from the active canvas while retaining it in history.",
        ),
        _delete_stroke(
            "EX-P2-R1-DELETE-FOOT-R", "foot_direction_right",
            reason="The P2 right-foot block now carries the observed outward toe direction; delete the superseded P1 wedge rather than displaying two shoe outlines.",
        ),
        _replace(
            "EX-P2-R1-RIBCAGE", "ribcage_centre_axis", corrected_ribcage_axis,
            stage="P2_primary_axes",
            reason="Fresh neck-to-pelvis re-observation shows the ribcage centre drifting image-left as the torso turns; the vertical first pass was compensating for the P1 spine rather than measuring the box.",
            role="construction", pressure=.40, width=1.7, opacity=.46, grade="H",
        ),
        _replace(
            "EX-P2-R1-THIGH-R", "leg_right_thigh_axis", [[287, 364], [311, 524]],
            stage="P2_primary_axes",
            reason="The measured axis must terminate at the existing image-right knee centre; the first pass extended below that landmark and understated the lower-leg span.",
            role="axis", pressure=.44, width=1.9, opacity=.55, grade="HB",
        ),
    ])
    run.prepare_stage_review()
    p2_pass2_locals = _prepare_p2_local_reviews(run, fresh=True)
    p2_memory = json.loads(
        (output / "reviews/P2_primary_axes/pass_02/pass_memory.json").read_text(encoding="utf-8")
    )
    assert p2_memory["state"] == "revision_continuation"
    assert p2_memory["previous_decision"] == "revise"
    assert p2_memory["carried_concerns"] == [
        "ribcage centre axis is too vertical through the lower torso",
        "image-right thigh axis ends below the observed knee centre",
        "P1 foot-direction wedges and ankle links remain visible beneath the P2 foot blocks",
    ]
    assert [item["action_id"] for item in p2_memory["inter_pass_correction_actions"]] == [
        "EX-P2-R1-DELETE-FOOT-LINK-L",
        "EX-P2-R1-DELETE-FOOT-L",
        "EX-P2-R1-DELETE-FOOT-LINK-R",
        "EX-P2-R1-DELETE-FOOT-R",
        "EX-P2-R1-RIBCAGE",
        "EX-P2-R1-THIGH-R",
    ]
    p2_pass2 = run.submit_stage_review(
        subject_findings=[
            "Fresh whole and local views keep the P1 head, spine, shoulder and pelvis rhythm while the new axes measure the subject's turned ribcage and asymmetric leg spans.",
            "The corrected image-right thigh ends at the observed knee centre; the lower shin remains the longer outward chain into the nearer shoe.",
            "Both hand blocks and both foot blocks sit at the visible or inferred endpoints without inventing anatomy or garment detail.",
        ],
        grammar_findings=[
            "P2 axes are subordinate to the P1 gesture and are visibly straight/segmental where measurement is the question.",
            "The ribcage and pelvis boxes stay open and lightweight; they do not become finished torso or trouser contours.",
        ],
        drawing_findings=[
            "The carried ribcage-turn and low-thigh concerns are cleared in fresh registered crops.",
            "Segment endpoints agree with the P1 joint centres and the subject's projected foreshortening.",
            "The P2 foot blocks now read as the active placement marks; the superseded P1 wedges and ankle links are deleted from the active canvas while remaining replayable in history.",
            "No new axis-level mismatch was found in the neck, boxes, arms, legs, hands or feet during the residual sweep.",
        ],
        contract_findings=[
            "The corrected artifact remains inside P2.v3 and adds no downstream mass, clothing or surface vocabulary.",
            "P1 remains the pose prior: its centrelines, joint circles and ground contacts are preserved underneath; the retired foot-direction evidence remains available in the P1 artifact and history.",
            "The two replacements are explicitly tied to fresh subject re-observation rather than convenience edits.",
        ],
        local_review_ids=[item.local_review_id for item in p2_pass2_locals],
        corrections=[
            "Turned the ribcage centre axis slightly image-left through the lower torso.",
            "Shortened the image-right thigh axis to the observed knee centre, restoring the shin's measured span.",
            "Deleted the superseded P1 foot-direction wedges and ankle links from the active canvas after the P2 placement blocks took over.",
        ],
        remaining_concerns=[],
        decision="advance",
        advance_rationale=(
            "Fresh pass-2 whole and registered local evidence clears the two carried axis concerns. "
            "The subject's neck, ribcage and pelvis turn, limb spans, foreshortening and endpoint blocks "
            "are now specific enough to unlock P3 volume construction without altering the P1 pose hypothesis."
        ),
    )

    trace = {
        "schema": "img2drawing.p2_reference_trace.v1",
        "version": __import__("img2drawing").__version__,
        "example": "full_body_croquis",
        "stage": "P1_gesture",
        "initial_dominant_path_start": initial_head_outline[0],
        "initial_dominant_path_start_semantics": "crown",
        "pass1": {
            "decision": pass1.decision,
            "remaining_concerns": list(pass1.remaining_concerns),
            "local_review_ids": list(pass1.local_review_ids),
            "worker_packet": "reviews/P1_gesture/pass_01/worker_packet.md",
        },
        "inter_pass_corrections": [
            {"action_id": action_id, "kind": "replace_stroke", "target": target}
            for action_id, target in (
                ("EX-P1-R1-PELVIS", "pelvis_centreline"),
                ("EX-P1-R1-HIP-L", "joint_hip_L"),
                ("EX-P1-R1-HIP-R", "joint_hip_R"),
                ("EX-P1-R1-KNEE-L", "joint_knee_L"),
                ("EX-P1-R1-LEG-L", "leg_left_flow"),
                ("EX-P1-R1-LEG-R", "leg_right_flow"),
            )
        ],
        "pass2": {
            "memory_state": pass2_memory["state"],
            "parent_review_digest": pass2_memory["previous_review_digest"],
            "carried_concerns": pass2_memory["carried_concerns"],
            "inter_pass_correction_action_ids": [
                item["action_id"] for item in pass2_memory["inter_pass_correction_actions"]
            ],
            "decision": pass2.decision,
            "remaining_concerns": list(pass2.remaining_concerns),
            "advance_rationale": pass2.advance_rationale,
            "local_review_ids": list(pass2.local_review_ids),
            "worker_packet": "reviews/P1_gesture/pass_02/worker_packet.md",
        },
        "p2": {
            "stage": "P2_primary_axes",
            "pass1": {
                "decision": p2_pass1.decision,
                "remaining_concerns": list(p2_pass1.remaining_concerns),
                "local_review_ids": list(p2_pass1.local_review_ids),
                "worker_packet": "reviews/P2_primary_axes/pass_01/worker_packet.md",
            },
            "inter_pass_corrections": [
                {"action_id": action_id, "kind": kind, "target": target}
                for action_id, kind, target in (
                    ("EX-P2-R1-DELETE-FOOT-LINK-L", "delete_stroke", "ankle_foot_link_left"),
                    ("EX-P2-R1-DELETE-FOOT-L", "delete_stroke", "foot_direction_left"),
                    ("EX-P2-R1-DELETE-FOOT-LINK-R", "delete_stroke", "ankle_foot_link_right"),
                    ("EX-P2-R1-DELETE-FOOT-R", "delete_stroke", "foot_direction_right"),
                    ("EX-P2-R1-RIBCAGE", "replace_stroke", "ribcage_centre_axis"),
                    ("EX-P2-R1-THIGH-R", "replace_stroke", "leg_right_thigh_axis"),
                )
            ],
            "pass2": {
                "memory_state": p2_memory["state"],
                "parent_review_digest": p2_memory["previous_review_digest"],
                "carried_concerns": p2_memory["carried_concerns"],
                "inter_pass_correction_action_ids": [
                    item["action_id"] for item in p2_memory["inter_pass_correction_actions"]
                ],
                "decision": p2_pass2.decision,
                "remaining_concerns": list(p2_pass2.remaining_concerns),
                "advance_rationale": p2_pass2.advance_rationale,
                "local_review_ids": list(p2_pass2.local_review_ids),
                "worker_packet": "reviews/P2_primary_axes/pass_02/worker_packet.md",
            },
            "review_chain": {
                "pass1_digest": p2_pass1.digest(),
                "pass2_parent_review_digest": p2_pass2.parent_review_digest,
                "pass2_digest": p2_pass2.digest(),
            },
        },
        "review_chain": {
            "pass1_digest": pass1.digest(),
            "pass2_parent_review_digest": pass2.parent_review_digest,
            "pass2_digest": pass2.digest(),
            "p2_pass1_digest": p2_pass1.digest(),
            "p2_pass2_parent_review_digest": p2_pass2.parent_review_digest,
            "p2_pass2_digest": p2_pass2.digest(),
        },
        "current_stage": run.current_stage,
        "autonomy_note": "No user approval is requested between revise, correction, re-review, and advance.",
    }
    (output / "canonical_trace.json").write_text(
        json.dumps(trace, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return trace


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("img2drawing_example_output"),
        help="Output directory for canonical example artifacts (default: ./img2drawing_example_output).",
    )
    parser.add_argument(
        "--no-clean",
        action="store_true",
        help="Do not delete an existing output directory before running.",
    )
    args = parser.parse_args()

    trace = run_example(args.output, clean=not args.no_clean)
    print(json.dumps(trace, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
