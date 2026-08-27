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
        width=512,
        height=802,
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
    # Every coordinate here was read off the subject at canvas scale. The
    # annotated construction reference supplies the grammar — which lines exist
    # and what each states — never the coordinates.
    #
    # Two distinct lines are never merged: the facial centreline explains face
    # rotation, the spine centreline explains body gesture. Weights follow a
    # completed run: an early stage is not a faint stage.
    #
    # Pass 1 deliberately runs the facial centreline dead down the cranium
    # midline — a contract-forbidden form — so the example demonstrates a real
    # revise cycle instead of a cosmetic one.
    # ------------------------------------------------------------------
    # Pass 1's error, and a real one: a borrowed narrow ellipse standing in for
    # this subject's cranium. The P1 contract forbids exactly this.
    initial_head_outline=[[253,34], [263,38], [271,48], [275,62], [273,80], [266,102], [257,116], [253,118],
             [248,116], [240,102], [234,80], [232,62], [236,46], [244,37], [253,34]]

    run.draw_many([
        _stroke(
            "EX-P1-A1",
            "head_outline",
            initial_head_outline,
            grade="HB",
            pressure=0.52,
            width=2.3,
            opacity=0.66,
            source="Head outline read from the subject: full cranium narrowing to the jaw. Not an ellipse.",
        ),
        _stroke(
            "EX-P1-A2",
            "facial_centreline",
            [[263,30], [266,50], [267,71], [263,90], [262,101], [260,118]],
            grade="B",
            pressure=.66,
            width=2.8,
            opacity=.84,
            source="Facial centreline run through the marked crown, between-eyes, nose, mouth and chin — not down the outline's midpoint.",
        ),
        _stroke(
            "EX-P1-A3",
            "eye_line",
            [[236,66], [246,68], [256,70], [268,72], [279,73], [289,70]],
            grade="HB",
            pressure=0.48,
            width=2.15,
            opacity=0.6,
            source="Eye line drawn through both pupils; its downward tilt toward the image-right is what those two positions give.",
        ),
        _stroke(
            "EX-P1-A4",
            "spine_centreline",
            [[253,142], [257,190], [255,240], [250,290], [248,335], [250,378]],
            grade="B",
            pressure=0.72,
            width=3.1,
            opacity=0.9,
            source="The body's gesture: an S-curve from the middle of the neck through ribcage and abdomen to the pelvis.",
        ),
        _stroke(
            "EX-P1-A5",
            "shoulder_line",
            [[194,152], [222,146], [253,143], [284,144], [313,148]],
            grade="HB",
            pressure=0.52,
            width=2.2,
            opacity=0.64,
            source="Shoulder tilt: the image-left shoulder sits lower, the image-right higher.",
        ),
        _stroke(
            "EX-P1-A6",
            "pelvis_centreline",
            [[204,374], [232,376], [260,379], [286,382]],
            grade="HB",
            pressure=0.52,
            width=2.2,
            opacity=0.64,
            source="Pelvis tilt counter to the shoulders: image-left higher, image-right lower.",
        ),
        _stroke(
            "EX-P1-arm_left_a",
            "arm_left_outer",
            [[186,152], [180,222], [176,288], [172,356], [166,422]],
            grade="HB",
            pressure=0.5,
            width=2.2,
            opacity=0.62,
            source="Image-left arm hangs almost straight; shoulder, elbow and wrist nearly align.",
        ),
        _stroke(
            "EX-P1-arm_left_b",
            "arm_left_inner",
            [[202,152], [196,222], [192,288], [186,356], [174,422]],
            grade="HB",
            pressure=0.5,
            width=2.2,
            opacity=0.62,
            source="Inner edge of the arm left tube.",
        ),
        _stroke(
            "EX-P1-arm_right_a",
            "arm_right_outer",
            [[305,148], [335,192], [346,228], [313,282], [272,326]],
            grade="HB",
            pressure=0.5,
            width=2.2,
            opacity=0.62,
            source="Image-right arm bends at the elbow; the hand is in the pocket, so the wrist endpoint is inferred.",
        ),
        _stroke(
            "EX-P1-arm_right_b",
            "arm_right_inner",
            [[321,148], [349,192], [358,228], [323,282], [280,326]],
            grade="HB",
            pressure=0.5,
            width=2.2,
            opacity=0.62,
            source="Inner edge of the arm right tube.",
        ),
        _stroke(
            "EX-P1-leg_left_a",
            "leg_left_outer",
            [[193,378], [202,462], [211,545], [224,625], [239,705]],
            grade="HB",
            pressure=0.5,
            width=2.2,
            opacity=0.62,
            source="Image-left leg carries the weight and its lower leg angles out to the foot.",
        ),
        _stroke(
            "EX-P1-leg_left_b",
            "leg_left_inner",
            [[223,378], [226,462], [231,545], [240,625], [251,705]],
            grade="HB",
            pressure=0.5,
            width=2.2,
            opacity=0.62,
            source="Inner edge of the leg left tube.",
        ),
        _stroke(
            "EX-P1-leg_right_a",
            "leg_right_outer",
            [[267,378], [280,462], [294,548], [314,640], [335,730]],
            grade="HB",
            pressure=0.5,
            width=2.2,
            opacity=0.62,
            source="Image-right leg steps further out with a relaxed knee.",
        ),
        _stroke(
            "EX-P1-leg_right_b",
            "leg_right_inner",
            [[297,378], [304,462], [314,548], [330,640], [347,730]],
            grade="HB",
            pressure=0.5,
            width=2.2,
            opacity=0.62,
            source="Inner edge of the leg right tube.",
        ),
        _stroke(
            "EX-P1-J_shoulder_L",
            "joint_shoulder_L",
            [[200,152], [199,156], [196,158], [192,158], [189,156], [188,152], [189,148], [192,146], [196,146], [199,148], [200,152]],
            grade="HB",
            pressure=0.44,
            width=2.0,
            opacity=0.55,
            source="shoulder L centre read from the subject.",
        ),
        _stroke(
            "EX-P1-J_shoulder_R",
            "joint_shoulder_R",
            [[319,148], [318,152], [315,154], [311,154], [308,152], [307,148], [308,144], [311,142], [315,142], [318,144], [319,148]],
            grade="HB",
            pressure=0.44,
            width=2.0,
            opacity=0.55,
            source="shoulder R centre read from the subject.",
        ),
        _stroke(
            "EX-P1-J_elbow_L",
            "joint_elbow_L",
            [[190,288], [189,292], [186,294], [182,294], [179,292], [178,288], [179,284], [182,282], [186,282], [189,284], [190,288]],
            grade="HB",
            pressure=0.44,
            width=2.0,
            opacity=0.55,
            source="elbow L centre read from the subject.",
        ),
        _stroke(
            "EX-P1-J_elbow_R",
            "joint_elbow_R",
            [[358,228], [357,232], [354,234], [350,234], [347,232], [346,228], [347,224], [350,222], [354,222], [357,224], [358,228]],
            grade="HB",
            pressure=0.44,
            width=2.0,
            opacity=0.55,
            source="elbow R centre read from the subject.",
        ),
        _stroke(
            "EX-P1-J_wrist_L",
            "joint_wrist_L",
            [[176,422], [175,425], [172,427], [169,428], [166,427], [164,424], [164,420], [166,417],
             [169,416], [172,417], [175,419], [176,422]],
            grade="HB",
            pressure=0.44,
            width=2.0,
            opacity=0.55,
            source="wrist L centre read from the subject.",
        ),
        _stroke(
            "EX-P1-J_wrist_R",
            "joint_wrist_R",
            [[282,326], [281,329], [278,331], [275,332], [272,331], [270,328], [270,324], [272,321],
             [275,320], [278,321], [281,323], [282,326]],
            grade="HB",
            pressure=0.44,
            width=2.0,
            opacity=0.55,
            source="wrist R centre read from the subject.",
        ),
        _stroke(
            "EX-P1-J_hip_L",
            "joint_hip_L",
            [[214,378], [213,381], [210,383], [207,384], [204,383], [202,380], [202,376], [204,373],
             [207,372], [210,373], [213,375], [214,378]],
            grade="HB",
            pressure=0.44,
            width=2.0,
            opacity=0.55,
            source="hip L centre read from the subject.",
        ),
        _stroke(
            "EX-P1-J_hip_R",
            "joint_hip_R",
            [[288,378], [287,381], [284,383], [281,384], [278,383], [276,380], [276,376], [278,373],
             [281,372], [284,373], [287,375], [288,378]],
            grade="HB",
            pressure=0.44,
            width=2.0,
            opacity=0.55,
            source="hip R centre read from the subject.",
        ),
        _stroke(
            "EX-P1-J_knee_L",
            "joint_knee_L",
            [[227,545], [226,548], [223,550], [220,551], [217,550], [215,547], [215,543], [217,540],
             [220,539], [223,540], [226,542], [227,545]],
            grade="HB",
            pressure=0.44,
            width=2.0,
            opacity=0.55,
            source="knee L centre read from the subject.",
        ),
        _stroke(
            "EX-P1-J_knee_R",
            "joint_knee_R",
            [[310,548], [309,551], [306,553], [303,554], [300,553], [298,550], [298,546], [300,543],
             [303,542], [306,543], [309,545], [310,548]],
            grade="HB",
            pressure=0.44,
            width=2.0,
            opacity=0.55,
            source="knee R centre read from the subject.",
        ),
        _stroke(
            "EX-P1-J_ankle_L",
            "joint_ankle_L",
            [[251,705], [250,708], [247,710], [244,711], [241,710], [239,707], [239,703], [241,700],
             [244,699], [247,700], [250,702], [251,705]],
            grade="HB",
            pressure=0.44,
            width=2.0,
            opacity=0.55,
            source="ankle L centre read from the subject.",
        ),
        _stroke(
            "EX-P1-J_ankle_R",
            "joint_ankle_R",
            [[347,730], [346,733], [343,735], [340,736], [337,735], [335,732], [335,728], [337,725],
             [340,724], [343,725], [346,727], [347,730]],
            grade="HB",
            pressure=0.44,
            width=2.0,
            opacity=0.55,
            source="ankle R centre read from the subject.",
        ),
        _stroke(
            "EX-P1-F_link_L",
            "ankle_foot_link_left",
            [[245,705], [246,708], [250,713]],
            grade="HB",
            pressure=0.46,
            width=2.05,
            opacity=0.56,
            source="Link from the image-left ankle into the shoe.",
        ),
        _stroke(
            "EX-P1-F_L",
            "foot_direction_left",
            [[266,716], [263,722], [254,728], [242,731], [231,729], [226,724], [229,718], [238,712], [250,709], [261,711], [266,716]],
            grade="HB",
            pressure=0.5,
            width=2.2,
            opacity=0.62,
            source="Image-left shoe read from the subject: its toe swings across the body toward the image-left.",
        ),
        _stroke(
            "EX-P1-F_link_R",
            "ankle_foot_link_right",
            [[341,730], [337,733], [333,738]],
            grade="HB",
            pressure=0.46,
            width=2.05,
            opacity=0.56,
            source="Link from the image-right ankle into the shoe.",
        ),
        _stroke(
            "EX-P1-F_R",
            "foot_direction_right",
            [[378,760], [372,765], [361,765], [349,761], [340,754], [338,748], [344,743], [355,743], [367,747], [376,754], [378,760]],
            grade="HB",
            pressure=0.5,
            width=2.2,
            opacity=0.62,
            source="Image-right shoe read from the subject: it steps out and its toe points further from the body.",
        ),
        _stroke(
            "EX-P1-G_L",
            "ground_contact_left",
            [[210,750], [272,752]],
            grade="2H",
            pressure=0.36,
            width=1.7,
            opacity=0.42,
            source="Image-left foot contact; this foot carries the weight.",
        ),
        _stroke(
            "EX-P1-G_R",
            "ground_contact_right",
            [[318,779], [393,781]],
            grade="2H",
            pressure=0.36,
            width=1.7,
            opacity=0.42,
            source="Image-right foot contact; it lands lower and further out.",
        ),
    ])

    pass1_artifacts=run.prepare_stage_review()

    # Agent-selected local evidence. Runtime does not locate anatomy.
    head1=run.prepare_local_review(
        label="head_face",
        intent="Check cranium width, crown position and the nose pass against the subject.",
        subject_box=(300,20,450,200),
        drawing_box=(222,20,288,132),
    )
    pelvis1=run.prepare_local_review(
        label="pelvis_support",
        intent="Check pelvis tilt, hip joint centres and where both feet land.",
        subject_box=(190,430,570,1145),
        drawing_box=(132,299,398,800),
    )

    pass1=run.submit_stage_review(
        contract_findings=[
            "The drawing stays inside the P1.v3 representation boundary.",
            "No facial features beyond the centreline and eye line, no hair, clothing, muscle or closed volume.",
            "Face centreline, spine centreline and line of action are three separate strokes.",
        ],
        subject_findings=[
            "The subject's cranium is measurably wider than the ellipse drawn in pass 1 and sits further image-right.",
            "The subject's weight sits on the image-left leg; the image-right foot lands lower and further out.",
        ],
        grammar_findings=[
            "P1 is being judged against the frozen contract, not against an example drawing.",
            "Joint centres were read from the subject rather than copied from the pipeline overview sheet.",
        ],
        drawing_findings=[
            "The cranium was drawn as a narrow ellipse: it is about a third too narrow and sits left of the subject's head.",
            "Its left edge cuts through the subject's eye, and its lower end stops at the mouth rather than the chin.",
            "Spine, shoulder and pelvis centrelines, both arm and leg tubes, twelve joint centres, both foot direction ovals and both ground contacts are present and register.",
        ],
        local_review_ids=[head1.local_review_id,pelvis1.local_review_id],
        corrections=[],
        remaining_concerns=[
            "cranium outline is a borrowed ellipse, not this head's measured width",
            "eye line and facial centreline therefore sit inside the face instead of across the head",
        ],
        decision="revise",
    )

    # ------------------------------------------------------------------
    # CORRECTION BETWEEN PASSES
    #
    # A forbidden representation was found, not a small inaccuracy: the fix
    # replaces the structure rather than nudging it.
    # ------------------------------------------------------------------
    corrected_head_outline=[
        [263,30], [275,35], [285,46], [291,61], [291,77], [284,97], [273,113], [263,120],
        [251,116], [240,102], [233,84], [232,63], [239,45], [250,34], [263,30]
    ]
    run.draw(_replace(
        "EX-P1-R1",
        "head_outline",
        corrected_head_outline,
        reason=(
            "Pass 1 stood a borrowed narrow ellipse in for the cranium, which the P1 "
            "contract forbids. Replaced with the head outline measured on the subject: "
            "wider, centred right of where the ellipse sat, and asymmetric."
        ),
        pressure=.52,
        width=2.3,
        opacity=.66,
        grade="HB",
    ))

    # ------------------------------------------------------------------
    # P1 / PASS 2 — pass memory is generated automatically here.
    # ------------------------------------------------------------------
    pass2_artifacts=run.prepare_stage_review()

    head2=run.prepare_local_review(
        label="head_face",
        intent="Re-check the carried cranium-width concern after EX-P1-R1.",
        subject_box=(300,20,450,200),
        drawing_box=(222,20,288,132),
    )
    pelvis2=run.prepare_local_review(
        label="pelvis_support",
        intent="Re-check pelvis tilt and joint centres on the corrected artifact.",
        subject_box=(190,430,570,1145),
        drawing_box=(132,299,398,800),
    )

    pass2_memory=json.loads(
        (output/"reviews/P1_gesture/pass_02/pass_memory.json").read_text(encoding="utf-8")
    )

    # The worker reads carried concerns and action provenance before deciding.
    assert pass2_memory["state"]=="revision_continuation"
    assert pass2_memory["previous_decision"]=="revise"
    assert pass2_memory["carried_concerns"]==[
        "cranium outline is a borrowed ellipse, not this head's measured width",
        "eye line and facial centreline therefore sit inside the face instead of across the head",
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
            "The head outline now matches the subject's measured cranium width and position.",
            "The eye line and facial centreline now cross the whole head rather than sitting inside the face.",
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
            "Replaced the borrowed ellipse with the head outline measured on the subject.",
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
        "initial_dominant_path_start":initial_head_outline[0],
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
                "target":"head_outline",
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
