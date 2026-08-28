from __future__ import annotations

"""Reopen and rebuild P3 after a downstream visual audit finds a weak mass read."""

import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "skills" / "img2drawing" / "src"))
sys.path.insert(0, str(HERE))

from img2drawing import DrawingRun  # noqa: E402
from run import (  # noqa: E402
    REQUIRED_P3_REGIONS,
    _cross,
    _delete,
    _manifest,
    _mass,
    _prepare_local_reviews,
    _replace,
    _submit_process_review,
)


def _corrected_initial_masses():
    """Rewritten P3 plan: volume direction and occupied width are explicit."""
    return [
        _mass("P3R-P1-HEAD-L", "head_mass_left", [[247, 31], [238, 44], [234, 63], [236, 84], [244, 103], [255, 117]], "Re-observed cranium and jaw plane around the locked crown/chin stations."),
        _mass("P3R-P1-HEAD-R", "head_mass_right", [[267, 32], [279, 44], [288, 62], [289, 82], [282, 101], [271, 115]], "Re-observed turned-side cranium; the narrower side preserves head direction."),
        _cross("P3R-P1-HEAD-CROSS", "head_cross_contour", [[236, 68], [253, 72], [271, 77], [290, 84]], "Slanted head cross-contour states the turn without facial detail."),
        _cross("P3R-P1-HEAD-JAW", "head_jaw_cross_contour", [[241, 100], [258, 105], [276, 102]], "Short jaw-plane cross-contour separates volume from a generic egg."),
        _mass("P3R-P1-NECK-L", "neck_mass_left", [[247, 112], [245, 129], [246, 146], [249, 162]], "Short visible neck bridge below the jaw."),
        _mass("P3R-P1-NECK-R", "neck_mass_right", [[273, 114], [275, 131], [273, 148], [270, 162]], "Far neck bridge meeting the turned ribcage."),
        _mass("P3R-P1-TORSO-L", "torso_mass_left", [[185, 175], [180, 205], [175, 238], [172, 272], [176, 306], [184, 339], [201, 367]], "Image-left torso envelope widens and reverses gently around the turned ribcage."),
        _mass("P3R-P1-TORSO-R", "torso_mass_right", [[309, 156], [317, 185], [322, 216], [323, 248], [319, 281], [311, 316], [299, 367]], "Image-right torso envelope keeps the elevated shoulder and nearer depth."),
        _cross("P3R-P1-RIB-CROSS", "ribcage_cross_contour", [[184, 191], [215, 201], [248, 205], [283, 198], [316, 183]], "Upper cross-contour visibly wraps the ribcage instead of lying flat."),
        _cross("P3R-P1-WAIST-CROSS", "waist_cross_contour", [[173, 258], [208, 270], [246, 276], [286, 267], [322, 247]], "Middle cross-contour turns around the waist volume."),
        _cross("P3R-P1-LOWER-CROSS", "lower_torso_cross_contour", [[180, 323], [214, 335], [247, 339], [284, 329], [312, 313]], "Lower torso cross-contour bridges the ribcage to the pelvis."),
        _mass("P3R-P1-SHOULDER-L", "shoulder_mass_left", [[181, 174], [187, 163], [201, 161], [214, 169], [205, 181], [190, 183], [181, 174]], "Simple image-left shoulder volume."),
        _mass("P3R-P1-SHOULDER-R", "shoulder_mass_right", [[303, 153], [315, 144], [328, 148], [334, 159], [321, 169], [307, 165], [303, 153]], "Simple image-right shoulder volume."),
        _mass("P3R-P1-NEAR-OUT", "near_arm_outer", [[320, 158], [338, 187], [354, 219], [364, 251], [361, 277], [344, 304], [304, 332]], "Near arm outer volume follows the visible broad sleeve and tapers to the pocket wrist."),
        _mass("P3R-P1-NEAR-IN", "near_arm_inner", [[305, 166], [319, 195], [336, 226], [345, 255], [340, 280], [322, 305], [291, 330]], "Near arm inner volume keeps a clear torso overlap."),
        _mass("P3R-P1-FAR-OUT", "far_arm_outer", [[181, 180], [175, 214], [169, 251], [165, 289], [163, 327], [160, 366], [158, 413]], "Far arm outer volume occupies the visible hanging sleeve."),
        _mass("P3R-P1-FAR-IN", "far_arm_inner", [[194, 182], [188, 216], [182, 251], [178, 289], [176, 328], [172, 368], [169, 413]], "Far arm inner volume remains behind the torso."),
        _mass("P3R-P1-HAND-A", "hand_mass_A", [[151, 409], [163, 410], [169, 422], [165, 439], [153, 444], [147, 431], [151, 409]], "Simple image-left hand volume, no finger detail."),
        _mass("P3R-P1-HAND-B", "hand_mass_B", [[291, 327], [303, 331], [308, 343], [300, 353], [286, 347], [283, 335], [291, 327]], "Simple pocket-hand volume, with occlusion explicit."),
        _mass("P3R-P1-PELVIS-L", "pelvis_mass_left", [[190, 333], [182, 349], [185, 371], [204, 393], [240, 402]], "Left pelvis basin wraps the lateral hip into the support thigh root instead of stopping at the inner thigh midpoint."),
        _mass("P3R-P1-PELVIS-R", "pelvis_mass_right", [[298, 339], [306, 353], [302, 375], [289, 396], [269, 407]], "Right pelvis basin turns into the stepped-out thigh."),
        _cross("P3R-P1-PELVIS-CROSS", "pelvis_cross_contour", [[183, 347], [213, 355], [244, 360], [275, 357], [304, 349]], "Pelvis cross-contour states breadth and counter-tilt."),
        _mass("P3R-P1-LEG-A-OUT", "leg_A_outer", [[180, 397], [179, 425], [181, 454], [183, 482], [186, 511], [190, 541], [194, 573], [198, 604], [202, 635], [215, 696]], "Support-leg outer envelope follows the photo's left jeans edge, swelling through knee/calf before tapering."),
        _mass("P3R-P1-LEG-A-IN", "leg_A_inner", [[240, 399], [246, 428], [248, 456], [249, 483], [252, 512], [254, 542], [256, 574], [261, 606], [266, 637], [271, 696]], "Support-leg inner envelope follows the photo's center-side jeans edge and preserves the narrow inter-leg gap."),
        _cross("P3R-P1-LEG-A-THIGH", "leg_A_thigh_cross", [[179, 425], [246, 428]], "Support thigh cross-contour spans the observed jeans width instead of a narrow centerline."),
        _cross("P3R-P1-LEG-A-KNEE", "leg_A_knee_cross", [[186, 512], [252, 513]], "Support knee cross-contour spans the measured outer and inner edges."),
        _mass("P3R-P1-LEG-B-OUT", "leg_B_outer", [[281, 405], [286, 435], [292, 463], [300, 483], [308, 511], [313, 541], [317, 576], [325, 613], [338, 664], [353, 722]], "Counterbalance outer envelope broadens through the nearer thigh and steps outward."),
        _mass("P3R-P1-LEG-B-IN", "leg_B_inner", [[242, 405], [243, 435], [247, 463], [255, 486], [264, 512], [270, 542], [276, 576], [285, 613], [299, 663], [337, 722]], "Counterbalance inner envelope leaves a tall asymmetric inter-leg wedge."),
        _cross("P3R-P1-LEG-B-THIGH", "leg_B_thigh_cross", [[286, 435], [244, 435]], "Counterbalance thigh cross-contour establishes its different depth."),
        _cross("P3R-P1-LEG-B-KNEE", "leg_B_knee_cross", [[313, 541], [270, 542]], "Counterbalance knee cross-contour keeps the outward direction."),
        _mass("P3R-P1-FOOT-A", "foot_mass_A", [[224, 693], [214, 706], [211, 723], [222, 738], [244, 741], [255, 731], [244, 713], [224, 693]], "Simple support-foot volume on the inherited ground contact."),
        _mass("P3R-P1-FOOT-B", "foot_mass_B", [[349, 721], [349, 741], [360, 761], [389, 775], [399, 787], [371, 793], [347, 777], [337, 742], [349, 721]], "Simple nearer stepped-out foot volume."),
    ]


def _review(run, locals_, index, concerns, *, corrections=(), decision="revise", rationale=""):
    return _submit_process_review(
        run,
        locals_,
        pass_index=index,
        concerns=concerns,
        corrections=corrections,
        decision=decision,
        advance_rationale=rationale,
    )


def reopen_example(output_dir: str | Path) -> dict:
    output = Path(output_dir).resolve()
    # Public reference-run artifacts may have their checkpoint paths
    # relativized for checkout portability.  Always bind resume to the
    # repository subject rather than trusting a stale absolute checkpoint
    # path (or a path relative to a temporary copy used for auditing).
    reference = ROOT / "skills" / "img2drawing" / "examples" / "full_body_croquis" / "subject.png"
    run = DrawingRun.resume(output, reference=reference)
    if run.current_stage != "P4_structural_connections":
        raise RuntimeError(f"expected downstream P4 discovery point, got {run.current_stage}")

    reopen = run.reopen_stage(
        "P3_primary_masses",
        reason="Fresh whole/crop/overlay audit found that the active P3 masses were a flat torso and rail-like legs, so P4 could only compensate for an upstream volume error.",
        discovered_in_stage="P4_structural_connections",
        findings=(
            "FAIL — torso orientation crop shows a rectangular mass with nearly horizontal depth cues.",
            "FAIL — pelvis/legs crop shows insufficient asymmetric taper and inter-leg negative space.",
            "FAIL — the head volume reads as a generic egg rather than a turned primary mass.",
            "FAIL — P3 must be rebuilt before any P4 connection or surface detail is allowed.",
        ),
    )
    run.stage_start("P3_primary_masses")

    records = []
    corrections = []
    run.draw_many(_corrected_initial_masses())
    run.prepare_stage_review()
    locals_1 = _prepare_local_reviews(run, pass_index=1)
    records.append(_review(
        run, locals_1, 1,
        (
            "whole figure still needs a final proportion sweep after the rewritten volume plan",
            "near arm and pelvis overlap require fresh comparison after the torso rewrite",
        ),
    ))
    corrections.append(())

    run.draw_many([
        _delete("P3R-P2-DELETE-HAND-A", "hand_left_block", "P3 hand mass now owns the image-left endpoint; delete the superseded P2 placement block from the active canvas while retaining history."),
        _delete("P3R-P2-DELETE-HAND-B", "hand_right_block", "P3 hand mass now owns the pocket endpoint; delete the superseded P2 placement block from the active canvas while retaining history."),
        _delete("P3R-P2-DELETE-FOOT-A", "foot_left_block", "P3 support-foot mass now owns placement; delete the superseded P2 block from the active canvas while retaining history."),
        _delete("P3R-P2-DELETE-FOOT-B", "foot_right_block", "P3 stepped-out foot mass now owns placement; delete the superseded P2 block from the active canvas while retaining history."),
        _replace("P3R-P2-TORSO-L", "torso_mass_left", [[184, 175], [179, 205], [173, 238], [170, 272], [175, 307], [183, 340], [201, 367]], "Fresh torso crop confirms the image-left volume must widen then turn into the pelvis bridge."),
        _replace("P3R-P2-TORSO-R", "torso_mass_right", [[309, 156], [318, 185], [324, 216], [325, 248], [321, 281], [312, 316], [299, 367]], "Fresh torso crop confirms the near side is broader and higher at the shoulder."),
        _replace("P3R-P2-RIB", "ribcage_cross_contour", [[183, 190], [215, 201], [248, 206], [284, 198], [318, 181]], "Fresh overlay changes the ribcage cross-contour from a flat shelf to a turned wrap."),
        _replace("P3R-P2-WAIST", "waist_cross_contour", [[171, 258], [208, 271], [247, 277], [287, 267], [324, 246]], "Fresh overlay changes the waist cross-contour to the observed depth turn."),
        _replace("P3R-P2-HEAD", "head_cross_contour", [[235, 68], [253, 72], [271, 77], [291, 84]], "Fresh head overlay keeps the cross-axis slanted through the locked facial centreline."),
    ])
    run.prepare_stage_review()
    locals_2 = _prepare_local_reviews(run, pass_index=2)
    records.append(_review(
        run, locals_2, 2,
        (
            "support and counterbalance leg widths need a measured station sweep",
            "pelvis breadth and thigh insertion still need clearer asymmetry",
        ),
        corrections=(
            "Rebuilt torso envelopes and ribcage/waist cross-contours around the observed turn.",
            "Retired the superseded P2 hand/foot placement blocks after P3 endpoint volumes took ownership.",
            "Reoriented the head cross-contour without introducing facial detail.",
        ),
    ))
    corrections.append(("P3R-P2-DELETE-HAND-A", "P3R-P2-DELETE-HAND-B", "P3R-P2-DELETE-FOOT-A", "P3R-P2-DELETE-FOOT-B", "P3R-P2-TORSO-L", "P3R-P2-TORSO-R", "P3R-P2-RIB", "P3R-P2-WAIST", "P3R-P2-HEAD"))

    run.draw_many([
        _replace("P3R-P3-PELVIS-L", "pelvis_mass_left", [[189, 333], [181, 349], [184, 371], [204, 394], [240, 403]], "Fresh pelvis crop widens the support-side basin into the measured inner thigh root."),
        _replace("P3R-P3-PELVIS-R", "pelvis_mass_right", [[299, 339], [307, 354], [303, 375], [289, 397], [269, 408]], "Fresh pelvis crop keeps the stepped-out side lower and narrower into the thigh."),
        _replace("P3R-P3-PELVIS-CROSS", "pelvis_cross_contour", [[181, 347], [213, 355], [245, 361], [276, 357], [306, 348]], "Fresh pelvis overlay makes the counter-tilted basin legible."),
        _replace("P3R-P3-LEG-A-OUT", "leg_A_outer", [[180, 397], [179, 425], [181, 454], [183, 482], [186, 511], [190, 541], [194, 573], [198, 604], [202, 635], [215, 696]], "Fresh station sweep aligns the support-leg outer envelope to the photo's jeans edge while retaining calf swell and taper."),
        _replace("P3R-P3-LEG-A-IN", "leg_A_inner", [[240, 399], [246, 428], [248, 456], [249, 483], [252, 512], [254, 542], [256, 574], [261, 606], [266, 637], [271, 696]], "Fresh station sweep aligns the support-leg inner envelope to the photo's center-side jeans edge and preserves the inter-leg gap."),
        _replace("P3R-P3-LEG-B-OUT", "leg_B_outer", [[282, 405], [288, 435], [294, 463], [302, 483], [310, 511], [315, 541], [319, 576], [327, 613], [339, 664], [353, 722]], "Fresh station sweep broadens the nearer counterbalance thigh and lower sweep."),
        _replace("P3R-P3-LEG-B-IN", "leg_B_inner", [[241, 405], [242, 435], [246, 463], [254, 486], [263, 512], [269, 542], [275, 576], [284, 613], [298, 663], [337, 722]], "Fresh station sweep preserves the distinct inter-leg wedge."),
        _replace("P3R-P3-LEG-A-THIGH", "leg_A_thigh_cross", [[179, 425], [246, 428]], "Support thigh cross-contour follows the full observed jeans width."),
        _replace("P3R-P3-LEG-B-THIGH", "leg_B_thigh_cross", [[288, 435], [242, 435]], "Counterbalance thigh cross-contour follows its different depth."),
    ])
    run.prepare_stage_review()
    locals_3 = _prepare_local_reviews(run, pass_index=3)
    records.append(_review(
        run, locals_3, 3,
        (
            "far-arm occlusion edge needs one explicit overlap check",
            "feet and hands need a final volume read after P2 block deletion",
        ),
        corrections=(
            "Rebuilt pelvis breadth/turn and both leg station profiles with explicit asymmetric taper.",
        ),
    ))
    corrections.append(("P3R-P3-PELVIS-L", "P3R-P3-PELVIS-R", "P3R-P3-PELVIS-CROSS", "P3R-P3-LEG-A-OUT", "P3R-P3-LEG-A-IN", "P3R-P3-LEG-B-OUT", "P3R-P3-LEG-B-IN", "P3R-P3-LEG-A-THIGH", "P3R-P3-LEG-B-THIGH"))

    run.draw_many([
        _replace("P3R-P4-FAR-OUT", "far_arm_outer", [[180, 179], [174, 214], [168, 251], [164, 289], [162, 327], [159, 366], [158, 413]], "Fresh far-arm crop clarifies visible sleeve volume and its torso occlusion."),
        _replace("P3R-P4-FAR-IN", "far_arm_inner", [[195, 182], [189, 216], [183, 251], [179, 289], [177, 328], [173, 368], [169, 413]], "Fresh far-arm crop keeps the hidden side behind the torso."),
        _replace("P3R-P4-HAND-A", "hand_mass_A", [[151, 409], [164, 410], [170, 422], [166, 439], [153, 445], [147, 431], [151, 409]], "Fresh endpoint crop keeps the simple hand volume attached without fingers."),
        _replace("P3R-P4-HAND-B", "hand_mass_B", [[291, 327], [304, 331], [309, 343], [301, 354], [286, 348], [283, 335], [291, 327]], "Fresh endpoint crop keeps pocket-hand volume and occlusion explicit."),
        _replace("P3R-P4-FOOT-A", "foot_mass_A", [[224, 693], [213, 706], [210, 723], [221, 739], [245, 742], [256, 731], [244, 713], [224, 693]], "Fresh support-foot crop confirms a compact wedge on the ground contact."),
        _replace("P3R-P4-FOOT-B", "foot_mass_B", [[349, 721], [349, 741], [360, 761], [390, 775], [400, 788], [371, 794], [347, 777], [337, 742], [349, 721]], "Fresh counterbalance-foot crop confirms the lower nearer wedge."),
        _replace("P3R-P4-HEAD-JAW", "head_jaw_cross_contour", [[240, 100], [258, 105], [277, 102]], "Fresh head crop retains a short jaw-plane cross-contour, not a facial feature."),
    ])
    run.prepare_stage_review()
    locals_4 = _prepare_local_reviews(run, pass_index=4)
    records.append(_review(
        run, locals_4, 4,
        (
            "whole-figure overlay needs a residual sweep for shoulder/pelvis rhythm",
            "head and torso must remain readable without downstream surface detail",
        ),
        corrections=(
            "Clarified far-arm overlap and refreshed simple hand/foot volumes after retiring P2 blocks.",
        ),
    ))
    corrections.append(("P3R-P4-FAR-OUT", "P3R-P4-FAR-IN", "P3R-P4-HAND-A", "P3R-P4-HAND-B", "P3R-P4-FOOT-A", "P3R-P4-FOOT-B", "P3R-P4-HEAD-JAW"))

    run.draw_many([
        _replace("P3R-P5-SHOULDER-L", "shoulder_mass_left", [[181, 174], [187, 162], [202, 160], [215, 169], [205, 182], [190, 184], [181, 174]], "Residual shoulder crop preserves the lower image-left shoulder and torso bridge."),
        _replace("P3R-P5-SHOULDER-R", "shoulder_mass_right", [[303, 153], [315, 143], [329, 148], [335, 160], [321, 170], [307, 165], [303, 153]], "Residual shoulder crop preserves the elevated image-right shoulder."),
        _replace("P3R-P5-LOWER-CROSS", "lower_torso_cross_contour", [[179, 323], [214, 335], [247, 340], [285, 329], [313, 313]], "Residual sweep keeps the torso-to-pelvis bridge turned and subordinate."),
    ])
    run.prepare_stage_review()
    locals_5 = _prepare_local_reviews(run, pass_index=5)
    records.append(_review(
        run, locals_5, 5,
        ("one final blind residual sweep is required before P3 closure",),
        corrections=(
            "Rechecked shoulder counter-tilt and the lower torso bridge without adding garment seams.",
        ),
    ))
    corrections.append(("P3R-P5-SHOULDER-L", "P3R-P5-SHOULDER-R", "P3R-P5-LOWER-CROSS"))

    run.draw_many([
        _replace("P3R-P6-HEAD-L", "head_mass_left", [[247, 31], [237, 44], [233, 63], [235, 84], [243, 103], [255, 117]], "Final blind sweep keeps the head mass close to the locked crown/chin while preserving turn."),
        _replace("P3R-P6-LEG-A-KNEE", "leg_A_knee_cross", [[186, 511], [252, 513]], "Final blind sweep aligns the support knee cross-contour to the measured outer and inner edges."),
        _replace("P3R-P6-LEG-B-KNEE", "leg_B_knee_cross", [[315, 541], [269, 542]], "Final blind sweep aligns the counterbalance knee cross-contour to its measured station."),
    ])
    run.prepare_stage_review()
    locals_6 = _prepare_local_reviews(run, pass_index=6)
    manifest = _manifest(run, locals_6)
    run.submit_region_closure_manifest(manifest)
    visual = run.submit_visual_fidelity_review(
        evaluator_id="p3-blind-visual-evaluator-reopen-01",
        findings=(
            "Blind whole-view, same-coordinate overlay and all eight region crops were inspected before reading prior process rationale.",
            "PASS — torso turn and pelvic counter-tilt are visibly supported in the whole view and torso/pelvis crops.",
            "PASS — asymmetric leg taper and inter-leg negative space are visible in the same-coordinate overlay and leg crop.",
            "PASS — near/far arm exposure and endpoint ownership are visible without inventing hidden detail.",
            "PASS — head mass states a turn without becoming a generic egg; hair mass, surface connections and detail remain deferred to P4.",
        ),
        decision="advance",
        rationale="The reopened P3 branch clears the structural mismatch that was exposed at the downstream visual audit; no critical assertion remains uncertain.",
    )
    records.append(_review(
        run, locals_6, 6, (),
        corrections=(
            "Completed the final blind residual sweep and aligned both knee cross-contours.",
            "Submitted a fresh eight-region closure manifest and blind visual review bound to the reopened branch.",
        ),
        decision="advance",
        rationale=(
            "P3 was reopened at the earliest responsible stage after the whole/crop/overlay audit found a flat torso and rail-like legs. "
            "The rebuilt branch now passes the process contract and independent blind visual gate with no remaining stage-purpose concern."
        ),
    ))

    trace = {
        "schema": "img2drawing.p3_hardening_regression.v1",
        "version": __import__("img2drawing").__version__,
        "stage": "P3_primary_masses",
        "predecessor": {"trace": "p2_trace.json", "stage": "P2_primary_axes"},
        "reopen": {
            "reopen_id": reopen.reopen_id,
            "target_stage": reopen.target_stage,
            "discovered_in_stage": reopen.discovered_in_stage,
            "reason": reopen.reason,
            "findings": list(reopen.findings),
            "archive_dir": "reopen_archive/reopen_01/reviews",
        },
    }
    for idx, record in enumerate(records, start=1):
        trace[f"pass{idx}"] = {
            "decision": record.decision,
            "remaining_concerns": list(record.remaining_concerns),
            "local_review_ids": list(record.local_review_ids),
            "worker_packet": f"reviews/P3_primary_masses/pass_{idx:02d}/worker_packet.md",
        }
    trace["pass6"]["advance_rationale"] = records[-1].advance_rationale
    for idx in range(2, 7):
        trace[f"pass{idx}_memory"] = json.loads((output / f"reviews/P3_primary_masses/pass_{idx:02d}/pass_memory.json").read_text(encoding="utf-8"))
    trace["inter_pass_corrections"] = [list(items) for items in corrections[1:]]
    trace["review_chain"] = {
        **{f"pass{idx}_digest": record.digest() for idx, record in enumerate(records, start=1)},
        "manifest_digest": manifest.digest(),
        "visual_fidelity_digest": visual.digest(),
    }
    trace["visual_fidelity"] = {
        "manifest": "reviews/P3_primary_masses/pass_06/region_closure_manifest.json",
        "blind_packet": "reviews/P3_primary_masses/pass_06/blind_visual_packet.json",
        "review": "reviews/P3_primary_masses/pass_06/visual_fidelity_review.json",
        "decision": visual.decision,
    }
    trace["current_stage"] = run.current_stage
    trace["autonomy_note"] = "P3 was reopened and rebuilt autonomously after the visual audit; no user approval was requested between correction passes."
    trace["visual_qa_note"] = "The pass-06 visual decision is blind to prior worker rationale and bound to the reopened branch's current state, artifact, cursor and observation lock."
    (output / "canonical_trace.json").write_text(json.dumps(trace, indent=2, ensure_ascii=False), encoding="utf-8")
    return trace


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=HERE / "run")
    args = parser.parse_args()
    print(json.dumps(reopen_example(args.output), indent=2, ensure_ascii=False))
