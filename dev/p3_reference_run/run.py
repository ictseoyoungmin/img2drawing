from __future__ import annotations

"""Canonical P1 -> P3 primary-masses reference run.

The P2 reference runner is deliberately reused as a predecessor.  This file owns
only the P3 volume construction, the six-pass hardening loop, and the independent
eight-region visual-fidelity gate.
"""

import argparse
import importlib.util
import json
import shutil
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parents[1]
SKILL = PROJECT_ROOT / "skills" / "img2drawing"
sys.path.insert(0, str(SKILL / "src"))

from img2drawing import (  # noqa: E402
    DrawingRun,
    RegionClosureEntry,
    RegionClosureManifest,
    REQUIRED_P3_REGIONS,
)


def _load_p2_runner():
    path = PROJECT_ROOT / "dev" / "p2_reference_run" / "run.py"
    spec = importlib.util.spec_from_file_location("img2drawing_p2_reference_runner", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load predecessor runner: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _mass(
    action_id: str,
    part: str,
    points,
    source: str,
    *,
    role: str = "mass",
    grade: str = "H",
    pressure: float = .46,
    width: float = 2.15,
    opacity: float = .52,
):
    return {
        "action_id": action_id,
        "kind": "draw_stroke",
        "stage": "P3_primary_masses",
        "role": role,
        "part": part,
        "points": points,
        "stroke_id": part,
        "confidence": .88,
        "layer": 20,
        "tool": {
            "preset": "construction_pencil",
            "grade": grade,
            "overrides": {
                "pressure": pressure,
                "width": width,
                "opacity": opacity,
            },
        },
        "observation_id": "p3-observation-locked",
        "source_observation": source,
    }


def _replace(
    action_id: str,
    target: str,
    points,
    reason: str,
    *,
    role: str = "mass",
    grade: str = "H",
    pressure: float = .46,
    width: float = 2.15,
    opacity: float = .52,
):
    action = _mass(
        action_id,
        target,
        points,
        "Fresh P3 subject re-observation after the previous pass.",
        role=role,
        grade=grade,
        pressure=pressure,
        width=width,
        opacity=opacity,
    )
    action.update({
        "kind": "replace_stroke",
        "target_stroke_id": target,
        "revision_of": target,
        "reason": reason,
    })
    return action


def _delete(action_id: str, target: str, reason: str):
    return {
        "action_id": action_id,
        "kind": "delete_stroke",
        "stage": "P3_primary_masses",
        "target_stroke_id": target,
        "confidence": .96,
        "tool": {"preset": "hard_eraser", "grade": "HB"},
        "observation_id": "p3-observation-locked",
        "source_observation": "Fresh P3 hand/foot volume review after the incoming mass was drawn.",
        "reason": reason,
        "revision_of": target,
    }


def _cross(action_id: str, part: str, points, source: str):
    return _mass(
        action_id,
        part,
        points,
        source,
        role="cross_contour",
        grade="2H",
        pressure=.36,
        width=1.55,
        opacity=.38,
    )


def _subject_box(box: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    sx = 735 / 512
    sy = 1152 / 802
    left, top, right, bottom = box
    return round(left * sx), round(top * sy), round(right * sx), round(bottom * sy)


def _prepare_local_reviews(run: DrawingRun, *, pass_index: int):
    prefix = "Fresh independent re-check" if pass_index > 1 else "Independent check"
    specs = (
        ("head_hair", f"{prefix}: head volume, jaw plane and asymmetric hair envelope.", (215, 10, 315, 145)),
        ("torso_orientation", f"{prefix}: ribcage thickness, turn, shoulder bridge and torso-to-pelvis overlap.", (175, 125, 325, 410)),
        ("near_arm", f"{prefix}: near arm width profile, taper and front/back relation to the torso.", (275, 135, 380, 360)),
        ("far_arm", f"{prefix}: far arm occupied volume, visibility and occlusion order.", (135, 145, 220, 455)),
        ("pelvis_legs", f"{prefix}: pelvis basin, both leg tapers, knee depth and inter-leg negative space.", (175, 325, 400, 760)),
        ("attached_object", f"{prefix}: attached-object volume; confirm the frozen subject records no prop.", (5, 5, 430, 430)),
    )
    reviews = []
    for label, intent, drawing_box in specs:
        reviews.append(
            run.prepare_local_review(
                label=label,
                intent=intent,
                subject_box=_subject_box(drawing_box),
                drawing_box=drawing_box,
            )
        )
    return reviews


def _initial_masses():
    """Pass-1 volumes: intentionally under-width torso/arm and rail-like legs."""
    return [
        _mass("P3-P1-HEAD-L", "head_mass_left", [[246, 31], [238, 44], [233, 63], [234, 84], [242, 103], [254, 116]], "Observed cranium envelope around the locked crown, face and chin stations."),
        _mass("P3-P1-HEAD-R", "head_mass_right", [[266, 31], [281, 42], [292, 61], [295, 81], [287, 101], [274, 116]], "Observed turned-side cranium envelope; the jaw remains a plain P3 plane."),
        _cross("P3-P1-HEAD-CROSS", "head_cross_contour", [[237, 70], [253, 73], [270, 77], [291, 82]], "Cross-contour states the head turn without adding facial features."),
        _mass("P3-P1-NECK-L", "neck_mass_left", [[247, 112], [245, 128], [246, 145], [249, 161]], "Short visible neck bridge below the jaw."),
        _mass("P3-P1-NECK-R", "neck_mass_right", [[273, 114], [275, 131], [273, 148], [270, 162]], "Far neck bridge meeting the ribcage."),
        _mass("P3-P1-TORSO-L", "torso_mass_left", [[190, 174], [194, 205], [197, 240], [198, 275], [200, 310], [201, 346], [204, 365]], "Initial left torso envelope around the P2 ribcage and pelvis axes."),
        _mass("P3-P1-TORSO-R", "torso_mass_right", [[304, 156], [302, 190], [301, 225], [299, 260], [297, 295], [295, 330], [292, 368]], "Initial right torso envelope; deliberately too parallel for the first visual check."),
        _cross("P3-P1-RIB-CROSS", "ribcage_cross_contour", [[196, 195], [220, 202], [247, 205], [276, 200], [301, 190]], "Upper ribcage cross-contour wraps the turned box."),
        _cross("P3-P1-WAIST-CROSS", "waist_cross_contour", [[199, 279], [222, 284], [246, 286], [271, 282], [296, 273]], "Lower torso cross-contour marks thickness without drawing a garment seam."),
        _mass("P3-P1-SHOULDER-L", "shoulder_mass_left", [[181, 174], [187, 163], [201, 161], [214, 169], [205, 181], [190, 183], [181, 174]], "Simple image-left shoulder volume."),
        _mass("P3-P1-SHOULDER-R", "shoulder_mass_right", [[303, 153], [315, 144], [328, 148], [334, 159], [321, 169], [307, 165], [303, 153]], "Simple image-right shoulder volume."),
        _mass("P3-P1-NEAR-OUT", "near_arm_outer", [[318, 160], [333, 188], [347, 221], [352, 255], [347, 279], [329, 304], [302, 329]], "Near arm outer volume; the deliberately narrow first pass will be checked for lost occupied width."),
        _mass("P3-P1-NEAR-IN", "near_arm_inner", [[305, 167], [316, 196], [329, 228], [334, 257], [329, 278], [313, 299], [291, 327]], "Near arm inner volume around the P2 centre path."),
        _mass("P3-P1-FAR-OUT", "far_arm_outer", [[181, 181], [178, 218], [174, 257], [170, 297], [166, 338], [162, 378], [159, 413]], "Far arm outer volume, respecting the visible hanging-arm endpoint."),
        _mass("P3-P1-FAR-IN", "far_arm_inner", [[193, 183], [190, 220], [186, 259], [182, 300], [178, 340], [174, 380], [169, 413]], "Far arm inner volume; the crop will test its occlusion against the jacket."),
        _mass("P3-P1-HAND-A", "hand_mass_A", [[151, 409], [163, 410], [169, 422], [165, 439], [153, 444], [147, 431], [151, 409]], "Simple image-left hand volume attached to the measured wrist; no finger detail."),
        _mass("P3-P1-HAND-B", "hand_mass_B", [[291, 327], [303, 331], [308, 343], [300, 353], [286, 347], [283, 335], [291, 327]], "Simple pocket-hand volume attached to the inferred wrist; occlusion remains explicit."),
        _mass("P3-P1-PELVIS-L", "pelvis_mass_left", [[198, 333], [190, 348], [192, 369], [201, 388], [215, 397]], "Left pelvis basin around the measured hip station."),
        _mass("P3-P1-PELVIS-R", "pelvis_mass_right", [[287, 341], [296, 350], [294, 370], [285, 389], [270, 401]], "Right pelvis basin around the measured hip station."),
        _cross("P3-P1-PELVIS-CROSS", "pelvis_cross_contour", [[191, 350], [216, 356], [243, 359], [270, 358], [295, 352]], "Pelvis cross-contour states the counter-tilted basin."),
        _mass("P3-P1-LEG-A-OUT", "leg_A_outer", [[185, 394], [184, 435], [187, 476], [190, 520], [194, 563], [199, 610], [207, 658], [224, 695]], "Support-leg outer mass; first pass is intentionally close to a parallel rail."),
        _mass("P3-P1-LEG-A-IN", "leg_A_inner", [[216, 397], [217, 438], [218, 480], [219, 522], [220, 565], [224, 612], [230, 660], [237, 696]], "Support-leg inner mass around the P2 axis."),
        _mass("P3-P1-LEG-B-OUT", "leg_B_outer", [[278, 402], [283, 442], [289, 482], [296, 523], [304, 564], [314, 610], [328, 665], [351, 722]], "Counterbalance-leg outer mass; the first pass under-states its outward taper."),
        _mass("P3-P1-LEG-B-IN", "leg_B_inner", [[246, 402], [249, 443], [252, 483], [258, 524], [264, 566], [274, 610], [286, 665], [337, 722]], "Counterbalance-leg inner mass; its lower endpoint is intentionally too close to the outer rail."),
        _cross("P3-P1-KNEE-A", "leg_A_knee_cross", [[188, 520], [202, 526], [218, 527]], "Support-knee cross-contour."),
        _cross("P3-P1-KNEE-B", "leg_B_knee_cross", [[289, 521], [304, 526], [319, 524]], "Counterbalance-knee cross-contour."),
        _mass("P3-P1-FOOT-A", "foot_mass_A", [[224, 693], [216, 706], [214, 724], [228, 735], [250, 733], [241, 711], [224, 693]], "Simple support-foot wedge, preserving the P2 toe direction."),
        _mass("P3-P1-FOOT-B", "foot_mass_B", [[349, 721], [350, 741], [363, 760], [392, 772], [398, 786], [370, 790], [348, 774], [338, 742], [349, 721]], "Simple stepped-out foot volume, larger and lower in projection."),
    ]


def _manifest(run: DrawingRun, local_reviews):
    artifacts = run._prepared["P3_primary_masses"]
    local_by_label = {item.label: item for item in local_reviews}
    region_review = {
        "head_hair": "head_hair",
        "torso_orientation": "torso_orientation",
        "near_arm": "near_arm",
        "far_arm": "far_arm",
        "pelvis": "pelvis_legs",
        "leg_A": "pelvis_legs",
        "leg_B": "pelvis_legs",
        "attached_object": "attached_object",
    }
    findings = {
        "head_hair": ("Locked crown, chin and slight head turn; the subject's hair is visible but its large seated mass is deferred to P4 by the current contract.", "P3 closes the head volume and turn only; no hair mass or strand detail is smuggled into this stage."),
        "torso_orientation": ("Shoulder line rises toward image-right; ribcage turns over a counter-tilted pelvis.", "Ribcage and pelvis are wrapped by opposing cross-contours with visible torso thickness and bridge."),
        "near_arm": ("Image-right arm is the broader visible sleeve/forearm chain into the pocket wrist.", "Near arm has a wider upper envelope, taper and a clear torso overlap."),
        "far_arm": ("Image-left arm hangs visibly but is partly occluded by sleeve/cuff; wrist remains the endpoint.", "Far arm stays narrower, attached at the shoulder and behind the torso where occluded."),
        "pelvis": ("Pelvis breadth sits below the measured crest and rotates opposite the shoulders.", "Pelvis basin wraps both hip centres and bridges cleanly into the two thigh roots."),
        "leg_A": ("Image-left chain carries weight through hip, knee and compact support shoe.", "Leg A tapers from thigh to calf with a quiet support sweep and non-parallel sides."),
        "leg_B": ("Image-right chain steps outward and lower, with a distinct nearer foot projection.", "Leg B is broader through the thigh and turns outward into the lower foot mass."),
        "attached_object": ("The frozen observation records prop=none; no attached object occupies the subject frame.", "No prop mass is drawn; the empty region is intentionally closed rather than invented."),
    }
    entries = []
    for region_id in REQUIRED_P3_REGIONS:
        local = local_by_label[region_review[region_id]]
        subject_finding, drawing_finding = findings[region_id]
        entries.append(RegionClosureEntry(
            region_id=region_id,
            subject_finding=subject_finding,
            drawing_finding=drawing_finding,
            evidence_refs=(
                f"reviews/P3_primary_masses/{artifacts.drawing.path.parent.name}/local_reviews/{local.label}/local_review.json",
                f"reviews/P3_primary_masses/{artifacts.drawing.path.parent.name}/blind_visual_packet.json",
            ),
            decision="closed",
        ))
    return RegionClosureManifest(
        stage="P3_primary_masses",
        drawing_state_sha256=artifacts.drawing.state_sha256,
        drawing_artifact_sha256=artifacts.drawing.artifact_sha256,
        history_cursor=artifacts.drawing.history_cursor,
        observation_lock_digest=run.observation_lock.observation_digest,
        regions=tuple(entries),
        evaluator_id="p3-blind-visual-evaluator",
    )


def _submit_process_review(run: DrawingRun, local_reviews, *, pass_index: int, concerns, decision, corrections=(), advance_rationale=""):
    return run.submit_stage_review(
        subject_findings=(
            "Fresh whole-view and region crops preserve the locked front-three-quarter pose, counter-tilted shoulder/pelvis rhythm and asymmetric leg depth.",
        ),
        grammar_findings=(
            "P3 uses simple volumes, taper, cross-contours, overlap and perspective cues; it does not smuggle in facial, hair-strand, seam or shading detail.",
        ),
        contract_findings=(
            "The artifact stays inside full_body_croquis.P3.v2 and preserves P1 centrelines plus P2 segment endpoints underneath.",
        ),
        drawing_findings=(
            "Pass %d was inspected as a raw pencil render in whole view and selected local crops." % pass_index,
            "The independent region review remains separate from the process review; no prior verdict is used as visual evidence.",
        ),
        local_review_ids=[item.local_review_id for item in local_reviews],
        corrections=corrections,
        remaining_concerns=concerns,
        decision=decision,
        advance_rationale=advance_rationale,
    )


def run_example(output_dir: str | Path, *, clean: bool = True) -> dict:
    output = Path(output_dir).resolve()
    if clean and output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)

    # Build a fresh P1/P2 predecessor in this run directory; never mutate the
    # committed P2 reference run.
    p2 = _load_p2_runner()
    p2_trace = p2.run_example(output, clean=False)
    (output / "p2_trace.json").write_text(
        json.dumps(p2_trace, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (output / "canonical_trace.json").unlink(missing_ok=True)

    run = DrawingRun.resume(output)
    if run.current_stage != "P3_primary_masses":
        raise RuntimeError(f"P2 predecessor did not leave P3 active: {run.current_stage}")
    run.stage_start("P3_primary_masses")

    pass_records = []
    corrections_by_pass = []

    run.draw_many(_initial_masses())
    run.prepare_stage_review()
    locals_1 = _prepare_local_reviews(run, pass_index=1)
    pass_records.append(_submit_process_review(
        run, locals_1, pass_index=1,
        concerns=(
            "torso envelope is too narrow and nearly parallel through the ribcage",
            "near arm width is under-stated relative to its visible sleeve volume",
            "both legs read as rails with insufficient taper and depth difference",
            "P2 hand/foot placement blocks are still visible beneath the incoming P3 endpoint volumes",
        ),
        decision="revise",
    ))
    corrections_by_pass.append(())

    run.draw_many([
        _delete("P3-P2-DELETE-HAND-A", "hand_left_block", "P3 simple hand volume now owns the image-left endpoint; retire the superseded P2 placement block from the active canvas while retaining its history."),
        _delete("P3-P2-DELETE-HAND-B", "hand_right_block", "P3 simple hand volume now owns the pocket endpoint; retire the superseded P2 placement block from the active canvas while retaining its history."),
        _delete("P3-P2-DELETE-FOOT-A", "foot_left_block", "P3 simple support-foot volume now owns placement; retire the superseded P2 block from the active canvas while retaining its history."),
        _delete("P3-P2-DELETE-FOOT-B", "foot_right_block", "P3 simple stepped-out foot volume now owns placement; retire the superseded P2 block from the active canvas while retaining its history."),
        _replace("P3-P2-TORSO-L", "torso_mass_left", [[183, 174], [180, 207], [177, 240], [176, 274], [178, 308], [184, 340], [193, 366]], "Fresh envelope check widens the image-left torso and lets the ribcage turn instead of forming a parallel tube."),
        _replace("P3-P2-TORSO-R", "torso_mass_right", [[310, 155], [316, 185], [320, 216], [321, 248], [318, 280], [311, 317], [299, 366]], "Fresh envelope check preserves the elevated shoulder and widens the near torso before the pelvis bridge."),
        _replace("P3-P2-NEAR-OUT", "near_arm_outer", [[322, 158], [340, 187], [355, 219], [365, 251], [362, 277], [345, 303], [304, 332]], "Near sleeve volume is visible in the subject; the corrected outer envelope is broader through upper and mid arm."),
        _replace("P3-P2-NEAR-IN", "near_arm_inner", [[305, 165], [320, 195], [337, 226], [345, 255], [340, 280], [322, 305], [291, 329]], "Near arm inner envelope now keeps a visible tapered cylinder rather than a thin axis echo."),
        _replace("P3-P2-HEAD-L", "head_mass_left", [[244, 31], [235, 44], [230, 63], [231, 84], [240, 104], [254, 118]], "Head volume is kept close to the locked crown/chin stations instead of enlarging into a generic egg."),
    ])
    run.prepare_stage_review()
    locals_2 = _prepare_local_reviews(run, pass_index=2)
    pass_records.append(_submit_process_review(
        run, locals_2, pass_index=2,
        concerns=(
            "pelvis basin still has insufficient rotation and breadth",
            "support leg taper is too uniform from thigh to ankle",
            "counterbalance leg does not yet show enough outward depth change",
        ),
        corrections=(
            "Widened the turned torso and near-arm envelopes after a fresh crop review.",
            "Reduced the head mass to the locked crown/chin volume; hair mass remains a P4 responsibility.",
            "Transferred endpoint ownership from P2 placement blocks to P3 hand/foot volumes and deleted the superseded active marks.",
        ),
        decision="revise",
    ))
    corrections_by_pass.append(("P3-P2-DELETE-HAND-A", "P3-P2-DELETE-HAND-B", "P3-P2-DELETE-FOOT-A", "P3-P2-DELETE-FOOT-B", "P3-P2-TORSO-L", "P3-P2-TORSO-R", "P3-P2-NEAR-OUT", "P3-P2-NEAR-IN", "P3-P2-HEAD-L"))

    run.draw_many([
        _replace("P3-P3-PELVIS-L", "pelvis_mass_left", [[191, 332], [183, 348], [187, 369], [198, 391], [215, 401]], "Fresh pelvis crop restores the broad left basin around the lateral hip and support thigh root."),
        _replace("P3-P3-PELVIS-R", "pelvis_mass_right", [[297, 339], [305, 353], [301, 374], [289, 394], [270, 406]], "Fresh pelvis crop restores the turned right basin and its narrowing into the stepped-out thigh."),
        _replace("P3-P3-PELVIS-CROSS", "pelvis_cross_contour", [[184, 347], [213, 355], [243, 360], [273, 357], [303, 349]], "The pelvis cross-contour now spans the measured hip breadth and counter-tilt."),
        _replace("P3-P3-LEG-A-OUT", "leg_A_outer", [[181, 397], [176, 425], [175, 455], [180, 482], [177, 510], [171, 540], [168, 572], [171, 603], [177, 634], [224, 696]], "Support-leg outer envelope now swells through the knee/calf and tapers toward the support shoe."),
        _replace("P3-P3-LEG-A-IN", "leg_A_inner", [[216, 399], [218, 428], [220, 456], [216, 482], [211, 512], [204, 542], [200, 574], [199, 606], [202, 636], [237, 696]], "Support-leg inner envelope is no longer a parallel rail; its negative-space edge follows the observed chain."),
        _replace("P3-P3-LEG-B-OUT", "leg_B_outer", [[281, 405], [286, 435], [292, 463], [300, 483], [308, 510], [312, 540], [316, 575], [324, 612], [337, 663], [353, 722]], "Counterbalance outer envelope gains the subject's broader thigh and outward lower sweep."),
        _replace("P3-P3-LEG-B-IN", "leg_B_inner", [[242, 405], [243, 434], [247, 463], [255, 486], [264, 512], [270, 541], [276, 575], [285, 612], [299, 662], [337, 722]], "Counterbalance inner envelope restores the tall inter-leg wedge and distinct taper."),
    ])
    run.prepare_stage_review()
    locals_3 = _prepare_local_reviews(run, pass_index=3)
    pass_records.append(_submit_process_review(
        run, locals_3, pass_index=3,
        concerns=(
            "far arm still merges too quietly into the torso and needs an explicit occlusion edge",
            "feet need to read as volume rather than inherited flat placement blocks",
            "head cross-contour and ribcage cross-contour need a final depth sweep",
        ),
        corrections=(
            "Expanded pelvis breadth and rotation around the measured hip centres.",
            "Rebuilt both leg envelopes with asymmetric taper and inter-leg negative space.",
        ),
        decision="revise",
    ))
    corrections_by_pass.append(("P3-P3-PELVIS-L", "P3-P3-PELVIS-R", "P3-P3-PELVIS-CROSS", "P3-P3-LEG-A-OUT", "P3-P3-LEG-A-IN", "P3-P3-LEG-B-OUT", "P3-P3-LEG-B-IN"))

    run.draw_many([
        _replace("P3-P4-FAR-OUT", "far_arm_outer", [[181, 179], [175, 213], [169, 250], [166, 288], [164, 326], [161, 365], [158, 413]], "Fresh far-arm crop clarifies the visible hanging sleeve volume and its occlusion against the torso."),
        _replace("P3-P4-FAR-IN", "far_arm_inner", [[194, 182], [188, 215], [182, 250], [179, 288], [176, 327], [172, 367], [169, 413]], "Fresh far-arm crop keeps the hidden side behind the torso while preserving the wrist endpoint."),
        _replace("P3-P4-FOOT-A", "foot_mass_A", [[224, 693], [214, 706], [211, 723], [222, 738], [244, 741], [255, 731], [244, 713], [224, 693]], "Support shoe is rebuilt as a compact wedge volume on the P2 ground contact."),
        _replace("P3-P4-FOOT-B", "foot_mass_B", [[349, 721], [349, 741], [360, 761], [389, 775], [399, 787], [371, 793], [347, 777], [337, 742], [349, 721]], "Stepped-out shoe is rebuilt as the larger nearer block with a lower sole landing."),
        _replace("P3-P4-HEAD-CROSS", "head_cross_contour", [[235, 69], [253, 72], [271, 77], [293, 83]], "The head cross-contour is re-checked against the turned pupils/nose axis and remains shallow."),
        _replace("P3-P4-RIB-CROSS", "ribcage_cross_contour", [[188, 193], [217, 202], [247, 207], [278, 201], [313, 187]], "The ribcage cross-contour now drops toward the viewer and agrees with the shoulder turn."),
    ])
    run.prepare_stage_review()
    locals_4 = _prepare_local_reviews(run, pass_index=4)
    pass_records.append(_submit_process_review(
        run, locals_4, pass_index=4,
        concerns=(
            "near arm and torso overlap needs one residual depth check",
            "pelvis-to-thigh transitions are slightly abrupt at the basin edge",
            "whole-figure proportion needs a final quiet sweep before visual closure",
        ),
        corrections=(
            "Clarified far-arm visibility/occlusion and rebuilt both feet as simple volumes.",
            "Re-wrapped head and ribcage cross-contours to their observed turns.",
        ),
        decision="revise",
    ))
    corrections_by_pass.append(("P3-P4-FAR-OUT", "P3-P4-FAR-IN", "P3-P4-FOOT-A", "P3-P4-FOOT-B", "P3-P4-HEAD-CROSS", "P3-P4-RIB-CROSS"))

    run.draw_many([
        _replace("P3-P5-NEAR-OUT", "near_arm_outer", [[323, 159], [340, 187], [357, 220], [367, 252], [363, 278], [344, 305], [304, 333]], "Residual near-arm review preserves the broad visible upper arm and a clean taper into the pocket wrist."),
        _replace("P3-P5-NEAR-IN", "near_arm_inner", [[305, 166], [320, 195], [338, 225], [347, 254], [341, 280], [322, 305], [291, 330]], "Residual near-arm review restores the inner overlap edge without tracing a finished sleeve seam."),
        _replace("P3-P5-PELVIS-L", "pelvis_mass_left", [[190, 333], [181, 349], [185, 371], [197, 392], [215, 402]], "Pelvis-to-thigh transition is softened at the left basin while preserving the hip centre."),
        _replace("P3-P5-PELVIS-R", "pelvis_mass_right", [[298, 339], [306, 353], [302, 375], [289, 396], [269, 407]], "Pelvis-to-thigh transition is softened at the right basin while preserving the stepped-out chain."),
    ])
    run.prepare_stage_review()
    locals_5 = _prepare_local_reviews(run, pass_index=5)
    pass_records.append(_submit_process_review(
        run, locals_5, pass_index=5,
        concerns=("one final independent residual sweep is required before the P3 dual gate can advance",),
        corrections=(
            "Rechecked near-arm occupied width and torso overlap.",
            "Smoothed both pelvis-to-thigh mass transitions without adding clothing detail.",
        ),
        decision="revise",
    ))
    corrections_by_pass.append(("P3-P5-NEAR-OUT", "P3-P5-NEAR-IN", "P3-P5-PELVIS-L", "P3-P5-PELVIS-R"))

    # Pass 6 is a fresh process artifact.  The blind packet and region manifest
    # are bound to this exact state/cursor, then the independent visual decision
    # is recorded before the process review is allowed to advance.
    run.draw_many([
        _replace("P3-P6-WHOLE-RIB", "ribcage_cross_contour", [[187, 193], [216, 202], [247, 207], [279, 201], [314, 187]], "Final residual sweep confirms the ribcage depth cue remains subordinate to the P1 spine."),
        _replace("P3-P6-WHOLE-LEG-A", "leg_A_knee_cross", [[177, 516], [199, 525], [220, 526]], "Final residual sweep aligns the support knee cross-contour to the measured knee station."),
        _replace("P3-P6-WHOLE-LEG-B", "leg_B_knee_cross", [[289, 520], [306, 526], [322, 522]], "Final residual sweep aligns the counterbalance knee cross-contour to the measured knee station."),
    ])
    run.prepare_stage_review()
    locals_6 = _prepare_local_reviews(run, pass_index=6)
    manifest = _manifest(run, locals_6)
    run.submit_region_closure_manifest(manifest)
    visual = run.submit_visual_fidelity_review(
        evaluator_id="p3-blind-visual-evaluator",
        findings=(
            "All eight required regions were inspected from the frozen subject projection and current raw drawing.",
            "Head volume, torso orientation, both arm envelopes, pelvis, both leg tapers and the no-prop condition show no unresolved blocker; hair mass is intentionally deferred to P4.",
            "The final pass preserves P1/P2 pose evidence while adding only P3 volumes, taper and overlap cues.",
        ),
        decision="advance",
        rationale="Independent blind visual review finds the current P3 mass construction coherent enough to unlock structural connections.",
    )
    pass_records.append(_submit_process_review(
        run, locals_6, pass_index=6,
        concerns=(),
        corrections=(
            "Completed a final ribcage-depth and knee-station residual sweep.",
            "Submitted the eight-region closure manifest and independent blind visual review for this exact artifact.",
        ),
        decision="advance",
        advance_rationale=(
            "Six-pass P3 hardening is complete. The process contract review and the independent eight-region blind visual review "
            "agree that simple head, torso, pelvis, limb, hand/foot and overlap volumes now preserve the P1 pose and P2 axes "
            "without smuggling in downstream surface detail."
        ),
    ))

    trace = {
        "schema": "img2drawing.p3_hardening_regression.v1",
        "version": __import__("img2drawing").__version__,
        "stage": "P3_primary_masses",
        "predecessor": {
            "trace": "p2_trace.json",
            "stage": "P2_primary_axes",
            "current_stage_before_p3": "P3_primary_masses",
        },
        "pass1": {"decision": pass_records[0].decision, "remaining_concerns": list(pass_records[0].remaining_concerns), "local_review_ids": list(pass_records[0].local_review_ids), "worker_packet": "reviews/P3_primary_masses/pass_01/worker_packet.md"},
        "pass2": {"decision": pass_records[1].decision, "remaining_concerns": list(pass_records[1].remaining_concerns), "local_review_ids": list(pass_records[1].local_review_ids), "worker_packet": "reviews/P3_primary_masses/pass_02/worker_packet.md"},
        "pass3": {"decision": pass_records[2].decision, "remaining_concerns": list(pass_records[2].remaining_concerns), "local_review_ids": list(pass_records[2].local_review_ids), "worker_packet": "reviews/P3_primary_masses/pass_03/worker_packet.md"},
        "pass4": {"decision": pass_records[3].decision, "remaining_concerns": list(pass_records[3].remaining_concerns), "local_review_ids": list(pass_records[3].local_review_ids), "worker_packet": "reviews/P3_primary_masses/pass_04/worker_packet.md"},
        "pass5": {"decision": pass_records[4].decision, "remaining_concerns": list(pass_records[4].remaining_concerns), "local_review_ids": list(pass_records[4].local_review_ids), "worker_packet": "reviews/P3_primary_masses/pass_05/worker_packet.md"},
        "pass6": {"decision": pass_records[5].decision, "remaining_concerns": list(pass_records[5].remaining_concerns), "advance_rationale": pass_records[5].advance_rationale, "local_review_ids": list(pass_records[5].local_review_ids), "worker_packet": "reviews/P3_primary_masses/pass_06/worker_packet.md"},
        "pass2_memory": json.loads((output / "reviews/P3_primary_masses/pass_02/pass_memory.json").read_text(encoding="utf-8")),
        "pass3_memory": json.loads((output / "reviews/P3_primary_masses/pass_03/pass_memory.json").read_text(encoding="utf-8")),
        "pass4_memory": json.loads((output / "reviews/P3_primary_masses/pass_04/pass_memory.json").read_text(encoding="utf-8")),
        "pass5_memory": json.loads((output / "reviews/P3_primary_masses/pass_05/pass_memory.json").read_text(encoding="utf-8")),
        "pass6_memory": json.loads((output / "reviews/P3_primary_masses/pass_06/pass_memory.json").read_text(encoding="utf-8")),
        "inter_pass_corrections": [list(items) for items in corrections_by_pass[1:]],
        "review_chain": {"pass1_digest": pass_records[0].digest(), "pass2_digest": pass_records[1].digest(), "pass3_digest": pass_records[2].digest(), "pass4_digest": pass_records[3].digest(), "pass5_digest": pass_records[4].digest(), "pass6_digest": pass_records[5].digest(), "manifest_digest": manifest.digest(), "visual_fidelity_digest": visual.digest()},
        "visual_fidelity": {"manifest": "reviews/P3_primary_masses/pass_06/region_closure_manifest.json", "blind_packet": "reviews/P3_primary_masses/pass_06/blind_visual_packet.json", "review": "reviews/P3_primary_masses/pass_06/visual_fidelity_review.json", "decision": visual.decision},
        "current_stage": run.current_stage,
        "autonomy_note": "No user approval was requested between revise, correction, fresh review, blind visual closure and advance.",
        "visual_qa_note": "The independent visual decision is bound to the pass-06 state, artifact, history cursor and frozen observation lock.",
    }
    (output / "canonical_trace.json").write_text(json.dumps(trace, indent=2, ensure_ascii=False), encoding="utf-8")
    return trace


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=HERE / "run")
    parser.add_argument("--no-clean", action="store_true")
    args = parser.parse_args()
    print(json.dumps(run_example(args.output, clean=not args.no_clean), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
