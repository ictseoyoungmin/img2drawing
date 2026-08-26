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
    # Three distinct lines, never merged: the facial centreline explains face
    # rotation, the spine centreline explains body gesture, and the line of
    # action carries the whole figure's energy to the ground.
    #
    # Pass 1 deliberately draws the facial centreline as a plain vertical line
    # — a contract-forbidden failure mode — so the example demonstrates a real
    # revise cycle instead of a cosmetic one.
    # ------------------------------------------------------------------
    initial_face_centreline=[[186,23],[186,40],[186,56],[186,73],[186,90]]

    run.draw_many([
        _stroke(
            "EX-P1-A1",
            "line_of_action",
            [[208,12],[199,58],[190,120],[180,196],[171,276],[167,360],[170,450],[176,548]],
            role="gesture",
            pressure=.26,
            width=1.35,
            opacity=.36,
            grade="HB",
            confidence=.92,
            source=(
                "Whole-figure energy: enters above the head, crosses the body and lands "
                "ahead of the image-left weight-bearing foot. Not the spine."
            ),
        ),
        _stroke(
            "EX-P1-A2",
            "head_ovoid",
            [[186,22],[194,25],[201,36],[204,56],[201,76],[194,87],[186,90],[178,87],[171,76],
             [168,56],[171,36],[178,25],[186,22]],
            role="construction",
            pressure=0.2,
            width=1.12,
            opacity=0.27,
            source="Cranial ovoid sized from the skull, not from the hair silhouette.",
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
            "eye_line_cross",
            [[169,55],[176,52],[183,51],[192,52],[202,55]],
            role="construction",
            pressure=0.16,
            width=1.02,
            opacity=0.2,
            source="Eye line stating head tilt; no facial features.",
        ),
        _stroke(
            "EX-P1-A5",
            "spine_centreline",
            [[185,94],[182,120],[179,155],[178,192],[181,226]],
            role="construction",
            pressure=0.24,
            width=1.2,
            opacity=0.3,
            source="Separate S-curve starting behind the neck, through mid-back, waist and sacrum.",
        ),
        _stroke(
            "EX-P1-A6",
            "shoulder_line",
            [[150,112],[168,107],[188,105],[208,104],[226,107]],
            role="construction",
            pressure=0.19,
            width=1.1,
            opacity=0.24,
            source="Shoulder line stating tilt and rotation.",
        ),
        _stroke(
            "EX-P1-A7",
            "pelvis_centreline",
            [[156,227],[172,224],[188,223],[209,225]],
            role="construction",
            pressure=0.19,
            width=1.1,
            opacity=0.24,
            source="Pelvis centreline stating tilt.",
        ),
        _stroke(
            "EX-P1-A8",
            "arm_flow_left",
            [[150,113],[144,140],[137,168],[134,196],[131,230],[128,266],[126,300]],
            role="construction",
            pressure=0.17,
            width=1.05,
            opacity=0.21,
            source="Image-left arm flow following observed curvature, not a straight join.",
        ),
        _stroke(
            "EX-P1-A9",
            "arm_flow_right",
            [[226,108],[240,132],[248,158],[250,187],[240,208],[226,222],[215,231]],
            role="construction",
            pressure=0.17,
            width=1.05,
            opacity=0.21,
            source="Image-right arm flow; the hand is in the pocket, so its endpoint is inferred.",
        ),
        _stroke(
            "EX-P1-A10",
            "leg_flow_left",
            [[156,228],[153,270],[151,310],[151,350],[153,400],[156,455],[159,506]],
            role="construction",
            pressure=0.17,
            width=1.05,
            opacity=0.21,
            source="Image-left leg flow to the ankle; this leg carries the weight.",
        ),
        _stroke(
            "EX-P1-A11",
            "leg_flow_right",
            [[209,226],[211,270],[213,315],[214,357],[221,410],[230,465],[239,517]],
            role="construction",
            pressure=0.17,
            width=1.05,
            opacity=0.21,
            source="Image-right leg flow to the ankle.",
        ),
        _stroke(
            "EX-P1-A12",
            "torso_mass_left",
            [[152,116],[145,150],[146,185],[153,213],[157,227]],
            role="construction",
            pressure=0.15,
            width=1.02,
            opacity=0.18,
            source="Loose image-left torso extent; no closed ribcage volume.",
        ),
        _stroke(
            "EX-P1-A13",
            "torso_mass_right",
            [[224,111],[230,145],[228,182],[218,208],[210,225]],
            role="construction",
            pressure=0.15,
            width=1.02,
            opacity=0.18,
            source="Loose image-right torso extent; no closed ribcage volume.",
        ),
        _stroke(
            "EX-P1-A14",
            "ground_contact_left",
            [[150,536],[199,539]],
            role="construction",
            pressure=0.17,
            width=1.05,
            opacity=0.22,
            source="Image-left foot contact and landing direction.",
        ),
        _stroke(
            "EX-P1-A15",
            "ground_contact_right",
            [[229,554],[285,557]],
            role="construction",
            pressure=0.17,
            width=1.05,
            opacity=0.22,
            source="Image-right foot contact; it lands lower and further out.",
        ),
        _stroke(
            "EX-P1-A16",
            "joint_shoulder_L",
            [[154,111],[153,114],[151,115],[148,114],[146,112],[146,110],[148,108],[151,107],
             [153,108],[154,111]],
            role="construction",
            pressure=0.14,
            width=1.0,
            opacity=0.17,
            source="shoulder L centre read from the subject.",
        ),
        _stroke(
            "EX-P1-A17",
            "joint_shoulder_R",
            [[230,106],[229,109],[227,110],[224,109],[222,107],[222,105],[224,103],[227,102],
             [229,103],[230,106]],
            role="construction",
            pressure=0.14,
            width=1.0,
            opacity=0.17,
            source="shoulder R centre read from the subject.",
        ),
        _stroke(
            "EX-P1-A18",
            "joint_elbow_L",
            [[138,195],[137,198],[135,199],[132,198],[130,196],[130,194],[132,192],[135,191],
             [137,192],[138,195]],
            role="construction",
            pressure=0.14,
            width=1.0,
            opacity=0.17,
            source="elbow L centre read from the subject.",
        ),
        _stroke(
            "EX-P1-A19",
            "joint_elbow_R",
            [[254,186],[253,189],[251,190],[248,189],[246,187],[246,185],[248,183],[251,182],
             [253,183],[254,186]],
            role="construction",
            pressure=0.14,
            width=1.0,
            opacity=0.17,
            source="elbow R centre read from the subject.",
        ),
        _stroke(
            "EX-P1-A20",
            "joint_wrist_L",
            [[130,300],[129,303],[127,304],[124,303],[122,301],[122,299],[124,297],[127,296],
             [129,297],[130,300]],
            role="construction",
            pressure=0.14,
            width=1.0,
            opacity=0.17,
            source="wrist L centre read from the subject.",
        ),
        _stroke(
            "EX-P1-A21",
            "joint_wrist_R",
            [[218,231],[217,234],[215,235],[212,234],[210,232],[210,230],[212,228],[215,227],
             [217,228],[218,231]],
            role="construction",
            pressure=0.14,
            width=1.0,
            opacity=0.17,
            source="wrist R centre read from the subject.",
        ),
        _stroke(
            "EX-P1-A22",
            "joint_hip_L",
            [[160,226],[159,229],[157,230],[154,229],[152,227],[152,225],[154,223],[157,222],
             [159,223],[160,226]],
            role="construction",
            pressure=0.14,
            width=1.0,
            opacity=0.17,
            source="hip L centre read from the subject.",
        ),
        _stroke(
            "EX-P1-A23",
            "joint_hip_R",
            [[213,224],[212,227],[210,228],[207,227],[205,225],[205,223],[207,221],[210,220],
             [212,221],[213,224]],
            role="construction",
            pressure=0.14,
            width=1.0,
            opacity=0.17,
            source="hip R centre read from the subject.",
        ),
        _stroke(
            "EX-P1-A24",
            "joint_knee_L",
            [[155,350],[154,353],[152,354],[149,353],[147,351],[147,349],[149,347],[152,346],
             [154,347],[155,350]],
            role="construction",
            pressure=0.14,
            width=1.0,
            opacity=0.17,
            source="knee L centre read from the subject.",
        ),
        _stroke(
            "EX-P1-A25",
            "joint_knee_R",
            [[218,357],[217,360],[215,361],[212,360],[210,358],[210,356],[212,354],[215,353],
             [217,354],[218,357]],
            role="construction",
            pressure=0.14,
            width=1.0,
            opacity=0.17,
            source="knee R centre read from the subject.",
        ),
        _stroke(
            "EX-P1-A26",
            "joint_ankle_L",
            [[163,506],[162,509],[160,510],[157,509],[155,507],[155,505],[157,503],[160,502],
             [162,503],[163,506]],
            role="construction",
            pressure=0.14,
            width=1.0,
            opacity=0.17,
            source="ankle L centre read from the subject.",
        ),
        _stroke(
            "EX-P1-A27",
            "joint_ankle_R",
            [[243,517],[242,520],[240,521],[237,520],[235,518],[235,516],[237,514],[240,513],
             [242,514],[243,517]],
            role="construction",
            pressure=0.14,
            width=1.0,
            opacity=0.17,
            source="ankle R centre read from the subject.",
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
            "Spine, shoulder, pelvis, both arms, both legs, joint centres and both ground contacts are present and register.",
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
        [187,23],     # crown
        [183,38],
        [180,53],     # brow
        [179,68],     # nose: off the ovoid's geometric centre, toward the subject's turn
        [181,81],
        [184,91],     # chin
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
