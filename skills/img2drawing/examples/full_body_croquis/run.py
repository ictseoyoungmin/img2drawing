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
    initial_face_centreline=[[253,34],[253,55],[253,76],[253,97],[253,118]]

    run.draw_many([
        _stroke(
            "EX-P1-A1",
            "head_outline",
            [[253,34], [263,38], [271,48], [275,62], [273,80], [266,102], [257,116], [253,118],
             [248,116], [240,102], [234,80], [232,62], [236,46], [244,37], [253,34]],
            grade="HB",
            pressure=0.52,
            width=2.3,
            opacity=0.66,
            source="Head outline read from the subject: full cranium narrowing to the jaw. Not an ellipse.",
        ),
        _stroke(
            "EX-P1-A2",
            "facial_centreline",
            initial_face_centreline,
            grade="B",
            pressure=.66,
            width=2.8,
            opacity=.84,
            source="Facial centreline crown -> nose -> chin. Pass 1 runs it dead down the cranium midline on purpose.",
        ),
        _stroke(
            "EX-P1-A3",
            "eye_line",
            [[233,71], [243,73], [253,74], [264,73], [275,70]],
            grade="HB",
            pressure=0.48,
            width=2.15,
            opacity=0.6,
            source="Eye line dipping in the middle: this head is seen slightly from above, tilted down rather than up.",
        ),
        _stroke(
            "EX-P1-A4",
            "spine_centreline",
            [[253,142], [256,180], [254,220], [250,262], [248,300], [250,332]],
            grade="B",
            pressure=0.72,
            width=3.1,
            opacity=0.9,
            source="The body's gesture: an S-curve from the middle of the neck through ribcage and abdomen to the pelvis.",
        ),
        _stroke(
            "EX-P1-A5",
            "shoulder_line",
            [[212,156], [232,150], [253,147], [276,147], [297,150]],
            grade="HB",
            pressure=0.52,
            width=2.2,
            opacity=0.64,
            source="Shoulder tilt: the image-left shoulder sits lower, the image-right higher.",
        ),
        _stroke(
            "EX-P1-A6",
            "pelvis_centreline",
            [[214,326], [238,329], [262,332], [286,334]],
            grade="HB",
            pressure=0.52,
            width=2.2,
            opacity=0.64,
            source="Pelvis tilt counter to the shoulders: image-left higher, image-right lower.",
        ),
        _stroke(
            "EX-P1-arm_left_a",
            "arm_left_outer",
            [[206,156], [198,206], [192,258], [184,306], [175,350]],
            grade="HB",
            pressure=0.5,
            width=2.2,
            opacity=0.62,
            source="Image-left arm hangs almost straight; shoulder, elbow and wrist nearly align.",
        ),
        _stroke(
            "EX-P1-arm_left_b",
            "arm_left_inner",
            [[218,156], [210,206], [202,258], [192,306], [181,350]],
            grade="HB",
            pressure=0.5,
            width=2.2,
            opacity=0.62,
            source="Inner edge of the arm left tube.",
        ),
        _stroke(
            "EX-P1-arm_right_a",
            "arm_right_outer",
            [[292,150], [307,198], [312,252], [302,284], [284,308]],
            grade="HB",
            pressure=0.5,
            width=2.2,
            opacity=0.62,
            source="Image-right arm bends at the elbow; the hand is in the pocket, so the wrist endpoint is inferred.",
        ),
        _stroke(
            "EX-P1-arm_right_b",
            "arm_right_inner",
            [[304,150], [319,198], [324,252], [312,284], [292,308]],
            grade="HB",
            pressure=0.5,
            width=2.2,
            opacity=0.62,
            source="Inner edge of the arm right tube.",
        ),
        _stroke(
            "EX-P1-leg_left_a",
            "leg_left_outer",
            [[208,330], [212,412], [219,500], [227,600], [236,700]],
            grade="HB",
            pressure=0.5,
            width=2.2,
            opacity=0.62,
            source="Image-left leg carries the weight and its lower leg angles out to the foot.",
        ),
        _stroke(
            "EX-P1-leg_left_b",
            "leg_left_inner",
            [[228,330], [228,412], [233,500], [239,600], [246,700]],
            grade="HB",
            pressure=0.5,
            width=2.2,
            opacity=0.62,
            source="Inner edge of the leg left tube.",
        ),
        _stroke(
            "EX-P1-leg_right_a",
            "leg_right_outer",
            [[272,330], [280,412], [291,500], [305,610], [324,728]],
            grade="HB",
            pressure=0.5,
            width=2.2,
            opacity=0.62,
            source="Image-right leg steps further out with a relaxed knee.",
        ),
        _stroke(
            "EX-P1-leg_right_b",
            "leg_right_inner",
            [[292,330], [296,412], [305,500], [317,610], [334,728]],
            grade="HB",
            pressure=0.5,
            width=2.2,
            opacity=0.62,
            source="Inner edge of the leg right tube.",
        ),
        _stroke(
            "EX-P1-J_shoulder_L",
            "joint_shoulder_L",
            [[218,156], [213,161], [210,163], [207,164], [204,163], [202,160], [202,156], [204,153],
             [207,152], [210,153], [213,155], [214,158]],
            grade="HB",
            pressure=0.44,
            width=2.0,
            opacity=0.55,
            source="shoulder L centre read from the subject.",
        ),
        _stroke(
            "EX-P1-J_shoulder_R",
            "joint_shoulder_R",
            [[304,151], [303,154], [300,156], [297,157], [294,156], [292,153], [292,149], [294,146],
             [297,145], [300,146], [303,148], [304,151]],
            grade="HB",
            pressure=0.44,
            width=2.0,
            opacity=0.55,
            source="shoulder R centre read from the subject.",
        ),
        _stroke(
            "EX-P1-J_elbow_L",
            "joint_elbow_L",
            [[203,258], [191,265], [188,267], [185,268], [182,267], [180,264], [180,260], [182,257],
             [185,256], [188,257], [191,259], [192,262]],
            grade="HB",
            pressure=0.44,
            width=2.0,
            opacity=0.55,
            source="elbow L centre read from the subject.",
        ),
        _stroke(
            "EX-P1-J_elbow_R",
            "joint_elbow_R",
            [[324,252], [337,259], [334,261], [331,262], [328,261], [326,258], [326,254], [328,251],
             [331,250], [334,251], [337,253], [338,256]],
            grade="HB",
            pressure=0.44,
            width=2.0,
            opacity=0.55,
            source="elbow R centre read from the subject.",
        ),
        _stroke(
            "EX-P1-J_wrist_L",
            "joint_wrist_L",
            [[182,352], [181,355], [178,357], [175,358], [172,357], [170,354], [170,350], [172,347],
             [175,346], [178,347], [181,349], [182,352]],
            grade="HB",
            pressure=0.44,
            width=2.0,
            opacity=0.55,
            source="wrist L centre read from the subject.",
        ),
        _stroke(
            "EX-P1-J_wrist_R",
            "joint_wrist_R",
            [[294,310], [293,313], [290,315], [287,316], [284,315], [282,312], [282,308], [284,305],
             [287,304], [290,305], [293,307], [294,310]],
            grade="HB",
            pressure=0.44,
            width=2.0,
            opacity=0.55,
            source="wrist R centre read from the subject.",
        ),
        _stroke(
            "EX-P1-J_hip_L",
            "joint_hip_L",
            [[224,330], [223,333], [220,335], [217,336], [214,335], [212,332], [212,328], [214,325],
             [217,324], [220,325], [223,327], [224,330]],
            grade="HB",
            pressure=0.44,
            width=2.0,
            opacity=0.55,
            source="hip L centre read from the subject.",
        ),
        _stroke(
            "EX-P1-J_hip_R",
            "joint_hip_R",
            [[288,330], [287,333], [284,335], [281,336], [278,335], [276,332], [276,328], [278,325],
             [281,324], [284,325], [287,327], [288,330]],
            grade="HB",
            pressure=0.44,
            width=2.0,
            opacity=0.55,
            source="hip R centre read from the subject.",
        ),
        _stroke(
            "EX-P1-J_knee_L",
            "joint_knee_L",
            [[232,500], [231,503], [228,505], [225,506], [222,505], [220,502], [220,498], [222,495],
             [225,494], [228,495], [231,497], [232,500]],
            grade="HB",
            pressure=0.44,
            width=2.0,
            opacity=0.55,
            source="knee L centre read from the subject.",
        ),
        _stroke(
            "EX-P1-J_knee_R",
            "joint_knee_R",
            [[304,500], [303,503], [300,505], [297,506], [294,505], [292,502], [292,498], [294,495],
             [297,494], [300,495], [303,497], [304,500]],
            grade="HB",
            pressure=0.44,
            width=2.0,
            opacity=0.55,
            source="knee R centre read from the subject.",
        ),
        _stroke(
            "EX-P1-J_ankle_L",
            "joint_ankle_L",
            [[247,700], [250,703], [247,705], [244,706], [241,705], [239,702], [239,698], [241,695],
             [244,694], [247,695], [250,697], [251,700]],
            grade="HB",
            pressure=0.44,
            width=2.0,
            opacity=0.55,
            source="ankle L centre read from the subject.",
        ),
        _stroke(
            "EX-P1-J_ankle_R",
            "joint_ankle_R",
            [[335,728], [340,731], [337,733], [334,734], [331,733], [329,730], [329,726], [331,723],
             [334,722], [337,723], [340,725], [341,728]],
            grade="HB",
            pressure=0.44,
            width=2.0,
            opacity=0.55,
            source="ankle R centre read from the subject.",
        ),
        _stroke(
            "EX-P1-F_link_L",
            "ankle_foot_link_left",
            [[245,700], [246,703], [250,708]],
            grade="HB",
            pressure=0.46,
            width=2.05,
            opacity=0.56,
            source="Link from the image-left ankle into the shoe.",
        ),
        _stroke(
            "EX-P1-F_L",
            "foot_direction_left",
            [[240,706], [267,708], [275,720], [270,736], [243,747], [223,746], [210,737], [209,728],
             [218,713], [240,706]],
            grade="HB",
            pressure=0.5,
            width=2.2,
            opacity=0.62,
            source="Image-left shoe read from the subject: its toe swings across the body toward the image-left.",
        ),
        _stroke(
            "EX-P1-F_link_R",
            "ankle_foot_link_right",
            [[335,728], [331,731], [327,736]],
            grade="HB",
            pressure=0.46,
            width=2.05,
            opacity=0.56,
            source="Link from the image-right ankle into the shoe.",
        ),
        _stroke(
            "EX-P1-F_R",
            "foot_direction_right",
            [[327,739], [350,734], [375,737], [393,750], [392,763], [367,775], [340,774], [322,762],
             [319,750], [327,739]],
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
        intent="Check crown, facial-centreline curvature and the nose pass against the subject.",
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
        [252,34],     # crown
        [256,54],
        [258,73],     # brow, sitting right of the cranium midline
        [258,90],     # nose
        [256,106],
        [254,118],    # chin, on the observed jaw
    ]
    run.draw(_replace(
        "EX-P1-R1",
        "facial_centreline",
        corrected_face_centreline,
        reason=(
            "Pass 1 drew the facial centreline flat, which the P1 contract forbids. "
            "Replaced with a curve that passes the nose and exits toward the chin."
        ),
        pressure=.66,
        width=2.8,
        opacity=.84,
        grade="B",
    ))

    # ------------------------------------------------------------------
    # P1 / PASS 2 — pass memory is generated automatically here.
    # ------------------------------------------------------------------
    pass2_artifacts=run.prepare_stage_review()

    head2=run.prepare_local_review(
        label="head_face",
        intent="Re-check the carried facial-centreline concern after EX-P1-R1.",
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
