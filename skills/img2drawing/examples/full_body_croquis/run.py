from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from img2drawing import DrawingRun, ObservationContract, ViewObservation


HERE=Path(__file__).resolve().parent
SUBJECT=HERE/"subject.png"


def _stroke(
    action_id,
    part,
    points,
    *,
    role="construction",
    pressure=.18,
    width=1.1,
    opacity=.22,
    grade="2H",
    confidence=.84,
    source="Canonical-example visual observation.",
):
    return {
        "action_id":action_id,
        "kind":"draw_stroke",
        "stage":"P1_gesture",
        "role":role,
        "part":part,
        "points":points,
        "stroke_id":part,
        "confidence":confidence,
        "layer":10,
        "tool":{
            "preset":"construction_pencil",
            "grade":grade,
            "overrides":{
                "pressure":pressure,
                "width":width,
                "opacity":opacity,
            },
        },
        "observation_id":"canonical-"+action_id,
        "source_observation":source,
    }


def _replace(
    action_id,
    part,
    points,
    *,
    reason,
    pressure=.42,
    width=1.9,
    opacity=.62,
    grade="HB",
):
    return {
        "action_id":action_id,
        "kind":"replace_stroke",
        "stage":"P1_gesture",
        "role":"gesture",
        "part":part,
        "points":points,
        "target_stroke_id":part,
        "stroke_id":part,
        "confidence":.94,
        "layer":10,
        "tool":{
            "preset":"construction_pencil",
            "grade":grade,
            "overrides":{
                "pressure":pressure,
                "width":width,
                "opacity":opacity,
            },
        },
        "observation_id":"canonical-"+action_id,
        "source_observation":"Fresh re-observation after the previous review.",
        "reason":reason,
        "revision_of":part,
    }


def run_example(output_dir: str|Path, *, clean=True) -> dict:
    """Canonical P1 hardening example.

    Demonstrates:
    P1 gesture → fresh artifact review → local evidence → REVISE →
    explicit correction → pass-memory continuation → fresh review → ADVANCE.

    It intentionally stops with P2 as the current stage. It is a workflow example,
    not a claim that the entire figure is finished.
    """
    output=Path(output_dir).resolve()
    if clean and output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True,exist_ok=True)

    run=DrawingRun.create(
        SUBJECT,
        output,
        width=368,
        height=576,
        working_supersample=3,
        session_id="canonical-full-body-croquis-r07",
    )
    run.lock_observation(ObservationContract(
        subject_summary="Full-body subject reference for the canonical stage workflow.",
        view=ViewObservation(
            body_view="unknown",
            torso_turn="unknown",
            near_side="unknown",
            arm_visibility={
                "subject_left":"unknown",
                "subject_right":"unknown",
            },
            arm_occlusion={
                "subject_left":(),
                "subject_right":(),
            },
            uncertainties=(
                "The canonical example demonstrates review lifecycle; pose-side labels remain subject-observation inputs.",
            ),
        ),
    ))

    # ------------------------------------------------------------------
    # P1 / PASS 1
    # ------------------------------------------------------------------
    run.stage_start("P1_gesture")

    # ------------------------------------------------------------------
    # P1 / PASS 1 — a whole-body pose hypothesis, per the P1.v3 contract.
    #
    # Coordinates come from the subject, proportioned against the annotated
    # construction reference for this same subject. Three distinct lines are
    # never merged: the facial centreline explains face rotation, the spine
    # centreline explains body gesture, and the line of action carries the
    # figure's flow to the ground — drawn faint so it cannot dominate.
    #
    # Pass 1 deliberately draws the facial centreline as a plain vertical line
    # — a contract-forbidden failure mode — so the example demonstrates a real
    # revise cycle instead of a cosmetic one.
    # ------------------------------------------------------------------
    initial_face_centreline=[[186,24],[186,40],[186,56],[186,71],[186,86]]

    run.draw_many([
        _stroke(
            "EX-P1-A1",
            "line_of_action",
            [[179,10], [186,70], [189,113], [184,170], [182,222], [178,278], [175,331], [173,422],
             [169,520]],
            role="gesture",
            grade="HB",
            confidence=.92,
            pressure=0.12,
            width=0.9,
            opacity=0.14,
            source="Whole-figure flow from above the head to the weight-bearing foot. Kept faint so it never competes with the head.",
        ),
        _stroke(
            "EX-P1-A2",
            "head_ovoid",
            [[181,23], [192,26], [201,36], [207,52], [206,68], [201,81], [191,87], [180,84], [171,74], [165,58], [166,42], [171,29], [181,23]],
            pressure=0.2,
            width=1.12,
            opacity=0.27,
            source="Cranial ovoid sized from the skull and tilted with the head, not traced from the hair silhouette.",
        ),
        _stroke(
            "EX-P1-A3",
            "facial_centreline",
            initial_face_centreline,
            pressure=.26,
            width=1.25,
            opacity=.34,
            source="Facial centreline crown -> nose -> chin. Pass 1 draws it flat on purpose.",
        ),
        _stroke(
            "EX-P1-A4",
            "eye_line",
            [[166,60], [178,58], [190,56], [199,55], [205,55]],
            pressure=0.16,
            width=1.02,
            opacity=0.2,
            source="Eye line wrapping the head; the image-right side sits higher with the head tilt.",
        ),
        _stroke(
            "EX-P1-A5",
            "spine_centreline",
            [[182,88], [186,124], [183,161], [179,193], [178,222], [179,255]],
            pressure=0.26,
            width=1.25,
            opacity=0.34,
            source="Separate S-curve from the middle of the neck through ribcage and abdomen to the pelvis.",
        ),
        _stroke(
            "EX-P1-A6",
            "shoulder_line",
            [[130,132], [158,124], [190,118], [212,113], [227,111]],
            pressure=0.19,
            width=1.1,
            opacity=0.24,
            source="Shoulder tilt: the image-left shoulder sits lower, the image-right higher.",
        ),
        _stroke(
            "EX-P1-A7",
            "pelvis_centreline",
            [[132,251], [164,254], [196,258], [226,261]],
            pressure=0.19,
            width=1.1,
            opacity=0.24,
            source="Pelvis tilt counter to the shoulders: image-left higher, image-right lower.",
        ),
        _stroke(
            "EX-P1-arm_left_a",
            "arm_left_outer",
            [[125,132], [122,173], [121,214], [118,249], [116,283]],
            pressure=0.17,
            width=1.05,
            opacity=0.21,
            source="Image-left arm hangs almost straight: shoulder, elbow and wrist nearly aligned.",
        ),
        _stroke(
            "EX-P1-arm_left_b",
            "arm_left_inner",
            [[135,132], [132,173], [129,214], [126,249], [122,283]],
            pressure=0.17,
            width=1.05,
            opacity=0.21,
            source="Inner edge of the arm left tube.",
        ),
        _stroke(
            "EX-P1-arm_right_a",
            "arm_right_outer",
            [[222,111], [236,150], [247,190], [228,214], [209,236]],
            pressure=0.17,
            width=1.05,
            opacity=0.21,
            source="Image-right arm bends at the elbow; the hand is in the pocket, so the wrist endpoint is inferred.",
        ),
        _stroke(
            "EX-P1-arm_right_b",
            "arm_right_inner",
            [[232,111], [246,150], [255,190], [236,214], [215,236]],
            pressure=0.17,
            width=1.05,
            opacity=0.21,
            source="Inner edge of the arm right tube.",
        ),
        _stroke(
            "EX-P1-leg_left_a",
            "leg_left_outer",
            [[135,263], [141,318], [148,374], [157,430], [167,485]],
            pressure=0.17,
            width=1.05,
            opacity=0.21,
            source="Image-left leg carries the weight: hip, knee and ankle stack under the pelvis.",
        ),
        _stroke(
            "EX-P1-leg_left_b",
            "leg_left_inner",
            [[149,263], [153,318], [158,374], [165,430], [173,485]],
            pressure=0.17,
            width=1.05,
            opacity=0.21,
            source="Inner edge of the leg left tube.",
        ),
        _stroke(
            "EX-P1-leg_right_a",
            "leg_right_outer",
            [[201,266], [212,320], [223,375], [240,437], [258,499]],
            pressure=0.17,
            width=1.05,
            opacity=0.21,
            source="Image-right leg steps slightly out with a relaxed knee.",
        ),
        _stroke(
            "EX-P1-leg_right_b",
            "leg_right_inner",
            [[215,266], [224,320], [233,375], [248,437], [264,499]],
            pressure=0.17,
            width=1.05,
            opacity=0.21,
            source="Inner edge of the leg right tube.",
        ),
        _stroke(
            "EX-P1-J_shoulder_L",
            "joint_shoulder_L",
            [[134,132], [133,135], [131,136], [128,135], [126,133], [126,131], [128,129], [131,128],
             [133,129], [134,132]],
            pressure=0.14,
            width=1.0,
            opacity=0.17,
            source="shoulder L centre read from the subject.",
        ),
        _stroke(
            "EX-P1-J_shoulder_R",
            "joint_shoulder_R",
            [[231,111], [230,114], [228,115], [225,114], [223,112], [223,110], [225,108], [228,107],
             [230,108], [231,111]],
            pressure=0.14,
            width=1.0,
            opacity=0.17,
            source="shoulder R centre read from the subject.",
        ),
        _stroke(
            "EX-P1-J_elbow_L",
            "joint_elbow_L",
            [[129,214], [128,217], [126,218], [123,217], [121,215], [121,213], [123,211], [126,210],
             [128,211], [129,214]],
            pressure=0.14,
            width=1.0,
            opacity=0.17,
            source="elbow L centre read from the subject.",
        ),
        _stroke(
            "EX-P1-J_elbow_R",
            "joint_elbow_R",
            [[255,190], [254,193], [252,194], [249,193], [247,191], [247,189], [249,187], [252,186],
             [254,187], [255,190]],
            pressure=0.14,
            width=1.0,
            opacity=0.17,
            source="elbow R centre read from the subject.",
        ),
        _stroke(
            "EX-P1-J_wrist_L",
            "joint_wrist_L",
            [[123,283], [122,286], [120,287], [117,286], [115,284], [115,282], [117,280], [120,279],
             [122,280], [123,283]],
            pressure=0.14,
            width=1.0,
            opacity=0.17,
            source="wrist L centre read from the subject.",
        ),
        _stroke(
            "EX-P1-J_wrist_R",
            "joint_wrist_R",
            [[216,236], [215,239], [213,240], [210,239], [208,237], [208,235], [210,233], [213,232],
             [215,233], [216,236]],
            pressure=0.14,
            width=1.0,
            opacity=0.17,
            source="wrist R centre read from the subject.",
        ),
        _stroke(
            "EX-P1-J_hip_L",
            "joint_hip_L",
            [[146,263], [145,266], [143,267], [140,266], [138,264], [138,262], [140,260], [143,259],
             [145,260], [146,263]],
            pressure=0.14,
            width=1.0,
            opacity=0.17,
            source="hip L centre read from the subject.",
        ),
        _stroke(
            "EX-P1-J_hip_R",
            "joint_hip_R",
            [[212,266], [211,269], [209,270], [206,269], [204,267], [204,265], [206,263], [209,262],
             [211,263], [212,266]],
            pressure=0.14,
            width=1.0,
            opacity=0.17,
            source="hip R centre read from the subject.",
        ),
        _stroke(
            "EX-P1-J_knee_L",
            "joint_knee_L",
            [[157,374], [156,377], [154,378], [151,377], [149,375], [149,373], [151,371], [154,370],
             [156,371], [157,374]],
            pressure=0.14,
            width=1.0,
            opacity=0.17,
            source="knee L centre read from the subject.",
        ),
        _stroke(
            "EX-P1-J_knee_R",
            "joint_knee_R",
            [[232,375], [231,378], [229,379], [226,378], [224,376], [224,374], [226,372], [229,371],
             [231,372], [232,375]],
            pressure=0.14,
            width=1.0,
            opacity=0.17,
            source="knee R centre read from the subject.",
        ),
        _stroke(
            "EX-P1-J_ankle_L",
            "joint_ankle_L",
            [[174,485], [173,488], [171,489], [168,488], [166,486], [166,484], [168,482], [171,481],
             [173,482], [174,485]],
            pressure=0.14,
            width=1.0,
            opacity=0.17,
            source="ankle L centre read from the subject.",
        ),
        _stroke(
            "EX-P1-J_ankle_R",
            "joint_ankle_R",
            [[265,499], [264,502], [262,503], [259,502], [257,500], [257,498], [259,496], [262,495],
             [264,496], [265,499]],
            pressure=0.14,
            width=1.0,
            opacity=0.17,
            source="ankle R centre read from the subject.",
        ),
        _stroke(
            "EX-P1-F_link_L",
            "ankle_foot_link_left",
            [[170,485], [172,504], [173,518]],
            pressure=0.15,
            width=1.02,
            opacity=0.19,
            source="Link from the image-left ankle into the foot.",
        ),
        _stroke(
            "EX-P1-F_L",
            "foot_direction_left",
            [[198,525], [195,530], [187,534], [176,536], [164,536], [156,533], [152,529], [155,524],
             [163,520], [174,518], [186,518], [194,521], [198,525]],
            pressure=0.17,
            width=1.05,
            opacity=0.22,
            source="Image-left foot as one oval; it points slightly across the body and carries the weight.",
        ),
        _stroke(
            "EX-P1-F_link_R",
            "ankle_foot_link_right",
            [[261,499], [261,520], [261,535]],
            pressure=0.15,
            width=1.02,
            opacity=0.19,
            source="Link from the image-right ankle into the foot.",
        ),
        _stroke(
            "EX-P1-F_R",
            "foot_direction_right",
            [[287,549], [282,553], [272,556], [259,555], [247,552], [238,546], [235,541], [240,537],
             [250,534], [263,535], [275,538], [284,544], [287,549]],
            pressure=0.17,
            width=1.05,
            opacity=0.22,
            source="Image-right foot as one oval; it steps out and points further from the body.",
        ),
        _stroke(
            "EX-P1-G_L",
            "ground_contact_left",
            [[152,536], [198,539]],
            pressure=0.17,
            width=1.05,
            opacity=0.22,
            source="Image-left foot contact; this foot carries the weight.",
        ),
        _stroke(
            "EX-P1-G_R",
            "ground_contact_right",
            [[235,554], [288,557]],
            pressure=0.17,
            width=1.05,
            opacity=0.22,
            source="Image-right foot contact; it lands lower and further out.",
        ),
    ])

    pass1_artifacts=run.prepare_stage_review()

    # Agent-selected local evidence. Runtime does not locate anatomy.
    head1=run.prepare_local_review(
        label="head_face",
        intent="Check crown, facial-centreline curvature and the nose pass against the subject.",
        subject_box=(300,20,450,200),
        drawing_box=(150,10,225,100),
    )
    pelvis1=run.prepare_local_review(
        label="pelvis_support",
        intent="Check pelvis tilt, hip joint centres and where both feet land.",
        subject_box=(190,430,570,1145),
        drawing_box=(95,215,286,575),
    )

    pass1=run.submit_stage_review(
        contract_findings=[
            "The drawing stays inside the P1.v3 representation boundary.",
            "No facial features beyond the centreline and eye line, no hair, clothing, muscle or closed volume.",
            "Face centreline, spine centreline and line of action are three separate strokes.",
        ],
        subject_findings=[
            "The subject's facial centreline curves across the head and passes the nose off the head's geometric centre.",
            "The subject's weight sits on the image-left leg; the image-right foot lands lower and further out.",
        ],
        grammar_findings=[
            "P1 is being judged against the frozen contract, not against an example drawing.",
            "Joint centres were read from the subject rather than copied from the pipeline overview sheet.",
        ],
        drawing_findings=[
            "The facial centreline was drawn as a plain vertical line, so it carries no face rotation.",
            "Because of that, the head reads as facing straight ahead while the subject's is turned.",
            "Spine, shoulder and pelvis centrelines, both arm and leg tubes, twelve joint centres, both foot direction ovals and both ground contacts are present and register.",
        ],
        local_review_ids=[head1.local_review_id,pelvis1.local_review_id],
        corrections=[],
        remaining_concerns=[
            "facial centreline is a plain vertical line and states no face rotation",
            "head therefore reads as frontal while the subject's head is turned",
        ],
        decision="revise",
    )

    # ------------------------------------------------------------------
    # CORRECTION BETWEEN PASSES
    #
    # A forbidden representation was found, not a small inaccuracy: the fix
    # replaces the structure rather than nudging it.
    # ------------------------------------------------------------------
    corrected_face_centreline=[
        [185,24],     # crown
        [190,40],
        [192,56],     # brow
        [191,71],     # nose: off the ovoid's geometric centre, toward the head's turn
        [189,80],
        [187,87],     # chin
    ]
    run.draw(_replace(
        "EX-P1-R1",
        "facial_centreline",
        corrected_face_centreline,
        reason=(
            "Pass 1 drew the facial centreline flat, which the P1 contract forbids. "
            "Replaced with a curve that passes the nose and exits toward the chin."
        ),
        pressure=.26,
        width=1.25,
        opacity=.34,
    ))

    # ------------------------------------------------------------------
    # P1 / PASS 2 — pass memory is generated automatically here.
    # ------------------------------------------------------------------
    pass2_artifacts=run.prepare_stage_review()

    head2=run.prepare_local_review(
        label="head_face",
        intent="Re-check the carried facial-centreline concern after EX-P1-R1.",
        subject_box=(300,20,450,200),
        drawing_box=(150,10,225,100),
    )
    pelvis2=run.prepare_local_review(
        label="pelvis_support",
        intent="Re-check pelvis tilt and joint centres on the corrected artifact.",
        subject_box=(190,430,570,1145),
        drawing_box=(95,215,286,575),
    )

    pass2_memory=json.loads(
        (output/"reviews/P1_gesture/pass_02/pass_memory.json").read_text(encoding="utf-8")
    )

    # The worker reads carried concerns and action provenance before deciding.
    assert pass2_memory["state"]=="revision_continuation"
    assert pass2_memory["previous_decision"]=="revise"
    assert pass2_memory["carried_concerns"]==[
        "facial centreline is a plain vertical line and states no face rotation",
        "head therefore reads as frontal while the subject's head is turned",
    ]
    assert [
        a["action_id"] for a in pass2_memory["inter_pass_correction_actions"]
    ]==["EX-P1-R1"]

    pass2=run.submit_stage_review(
        contract_findings=[
            "The corrected artifact still stays inside the P1.v3 representation boundary.",
            "The correction replaced the facial centreline only; no downstream vocabulary was introduced.",
            "Face centreline, spine centreline and line of action remain three separate strokes.",
        ],
        subject_findings=[
            "The facial centreline now curves across the head and passes the nose where the subject's does.",
            "Head direction now agrees with the subject at P1 abstraction.",
        ],
        grammar_findings=[
            "Stage grammar stays subordinate to the frozen contract and subject geometry.",
        ],
        drawing_findings=[
            "Both carried pass-1 concerns were re-checked against fresh whole and local artifacts.",
            "A fresh residual sweep beyond the carried list found no joint drifting, no straight limb join and no missing occluded limb.",
            "With the subject hidden, the drawing reads as this subject in this pose rather than as a generic figure.",
        ],
        local_review_ids=[head2.local_review_id,pelvis2.local_review_id],
        corrections=[
            "Replaced the flat facial centreline with a curve through crown, nose and chin.",
        ],
        remaining_concerns=[],
        decision="advance",
        advance_rationale=(
            "Fresh pass-2 evidence clears both carried P1 concerns and a residual sweep "
            "found nothing new; the pose hypothesis registers against the subject, so P2 "
            "measurement may begin."
        ),
    )

    trace={
        "schema":"img2drawing.canonical_example_trace.v1",
        "version":__import__("img2drawing").__version__,
        "example":"full_body_croquis",
        "stage":"P1_gesture",
        "initial_dominant_path_start":initial_face_centreline[0],
        "initial_dominant_path_start_semantics":"crown",
        "pass1":{
            "decision":pass1.decision,
            "remaining_concerns":list(pass1.remaining_concerns),
            "local_review_ids":list(pass1.local_review_ids),
            "worker_packet":str(
                output/"reviews/P1_gesture/pass_01/worker_packet.md"
            ),
        },
        "inter_pass_corrections":[
            {
                "action_id":"EX-P1-R1",
                "kind":"replace_stroke",
                "target":"facial_centreline",
            }
        ],
        "pass2":{
            "memory_state":pass2_memory["state"],
            "parent_review_digest":pass2_memory["previous_review_digest"],
            "carried_concerns":pass2_memory["carried_concerns"],
            "inter_pass_correction_action_ids":[
                a["action_id"]
                for a in pass2_memory["inter_pass_correction_actions"]
            ],
            "decision":pass2.decision,
            "remaining_concerns":list(pass2.remaining_concerns),
            "advance_rationale":pass2.advance_rationale,
            "local_review_ids":list(pass2.local_review_ids),
            "worker_packet":str(
                output/"reviews/P1_gesture/pass_02/worker_packet.md"
            ),
        },
        "review_chain":{
            "pass1_digest":pass1.digest(),
            "pass2_parent_review_digest":pass2.parent_review_digest,
            "pass2_digest":pass2.digest(),
        },
        "current_stage":run.current_stage,
        "autonomy_note":"No user approval is requested between revise, correction, re-review, and advance.",
    }
    (output/"canonical_trace.json").write_text(
        json.dumps(trace,indent=2,ensure_ascii=False),
        encoding="utf-8",
    )
    return trace


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        # ponytail: cwd-relative so the example never writes 13MB into the installed skill
        default=Path("img2drawing_example_output"),
        help="Output directory for canonical example artifacts (default: ./img2drawing_example_output).",
    )
    parser.add_argument(
        "--no-clean",
        action="store_true",
        help="Do not delete an existing output directory before running.",
    )
    args=parser.parse_args()

    trace=run_example(args.output,clean=not args.no_clean)
    print(json.dumps(trace,indent=2,ensure_ascii=False))


if __name__=="__main__":
    main()
