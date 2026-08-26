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

    # P1 settles how the figure stands: one dominant line of action plus head
    # tilt, shoulder/pelvis tilt, limb directions and ground contact. Pass 1 is
    # intentionally weak at the head tilt and the pelvis transfer so the example
    # demonstrates a real revise cycle.
    initial_dominant=[
        [187,90],     # neck
        [184,112],
        [181,142],
        [179,192],    # lower-torso lean: deliberately too straight in pass 1
        [177,238],
        [175,266],    # pelvis transfer: deliberately weak
        [170,306],
        [166,358],
        [166,415],
        [169,482],
        [172,536],    # image-left foot contact
    ]

    run.draw_many([
        _stroke(
            "EX-P1-A1",
            "line_of_action",
            initial_dominant,
            role="gesture",
            pressure=.40,
            width=1.85,
            opacity=.58,
            grade="HB",
            confidence=.92,
            source=(
                "Observed line of action from the head through the pelvis to the "
                "image-left weight-bearing foot."
            ),
        ),
        _stroke(
            "EX-P1-A2",
            "head_ovoid",
            [[189,16],[199,20],[206,30],[210,45],[210,61],[206,76],[199,86],
             [189,90],[179,86],[172,76],[168,61],[168,45],[172,30],[179,20],[189,16]],
            pressure=.20,
            width=1.12,
            opacity=.27,
            source="Simple head ovoid sized from the subject's head bounds.",
        ),
        _stroke(
            "EX-P1-A3",
            "head_tilt_mark",
            [[176,44],[203,41]],
            pressure=.16,
            width=1.02,
            opacity=.20,
            source="Light cross mark stating head tilt only; no facial features.",
        ),
        _stroke(
            "EX-P1-A4",
            "shoulder_tilt",
            [[148,111],[186,106],[228,104]],
            pressure=.19,
            width=1.10,
            opacity=.24,
            source="Shoulder line as a tilt cue; the subject's image-right shoulder sits higher.",
        ),
        _stroke(
            "EX-P1-A5",
            "pelvis_tilt",
            [[152,224],[184,222],[216,226]],
            pressure=.19,
            width=1.10,
            opacity=.24,
            source="Pelvis line as a tilt cue; no pelvis mass.",
        ),
        _stroke(
            "EX-P1-A6",
            "arm_direction_left",
            [[148,111],[131,152],[128,195],[125,248],[123,300]],
            pressure=.15,
            width=1.02,
            opacity=.19,
            source="Image-left arm hangs and travels slightly inward to the hand.",
        ),
        _stroke(
            "EX-P1-A7",
            "arm_direction_right",
            [[228,104],[247,145],[252,187],[238,210],[224,220]],
            pressure=.15,
            width=1.02,
            opacity=.19,
            source="Image-right arm bends forward; the hand meets the waistband.",
        ),
        _stroke(
            "EX-P1-A8",
            "leg_direction_right",
            [[209,227],[214,292],[220,362],[236,452],[250,548]],
            pressure=.15,
            width=1.02,
            opacity=.18,
            source="Image-right leg direction path; it carries less weight than the image-left leg.",
        ),
        _stroke(
            "EX-P1-A9",
            "ground_contact_left",
            [[150,536],[199,539]],
            pressure=.17,
            width=1.05,
            opacity=.22,
            source="Where the image-left foot meets the ground.",
        ),
        _stroke(
            "EX-P1-A10",
            "ground_contact_right",
            [[229,554],[285,557]],
            pressure=.17,
            width=1.05,
            opacity=.22,
            source="Where the image-right foot meets the ground; it lands lower and further out.",
        ),
    ])

    pass1_artifacts=run.prepare_stage_review()

    # Agent-selected local evidence. Runtime does not locate anatomy.
    head1=run.prepare_local_review(
        label="head_face",
        intent="Check head position, tilt and size against the subject.",
        subject_box=(235,0,495,250),
        drawing_box=(115,0,248,126),
    )
    pelvis1=run.prepare_local_review(
        label="pelvis_support",
        intent="Check pelvis tilt, weight transfer and where both feet land.",
        subject_box=(190,430,570,1145),
        drawing_box=(95,215,286,575),
    )

    pass1=run.submit_stage_review(
        contract_findings=[
            "The drawing stays inside the P1 gesture/weight-path contract.",
            "No facial features, hair, clothing or muscle definition leaked in; P2 joints stay downstream.",
        ],
        subject_findings=[
            "The subject's weight sits on the image-left leg; the pelvis turns into it decisively.",
            "The subject's upper body leans slightly image-left of the pelvis centre.",
        ],
        grammar_findings=[
            "P1 has no example image of its own; the frozen P1 contract is the representation authority.",
            "Stage grammar is judged against that contract rather than against a reference image.",
        ],
        drawing_findings=[
            "The line of action is continuous from the head to the ground contact.",
            "Its pelvis segment is too vertical, so the weight transfer does not read.",
            "Through the lower torso it runs straighter than the subject's own lean.",
        ],
        local_review_ids=[head1.local_review_id,pelvis1.local_review_id],
        corrections=[],
        remaining_concerns=[
            "pelvis segment is too vertical to show which leg carries the weight",
            "lower-torso lean is straighter than the subject's",
        ],
        decision="revise",
    )

    # ------------------------------------------------------------------
    # CORRECTION BETWEEN PASSES
    # ------------------------------------------------------------------
    corrected_dominant=[
        [187,90],     # neck
        [184,113],
        [183,143],
        [184,193],    # lower-torso lean corrected toward the subject
        [181,240],
        [175,262],
        [166,282],    # clearer directional break into the weight-bearing leg
        [159,312],
        [156,362],
        [158,418],
        [165,484],
        [172,536],
    ]
    run.draw(_replace(
        "EX-P1-R1",
        "line_of_action",
        corrected_dominant,
        reason=(
            "Pass 1 carried two concerns: follow the subject's lower-torso lean and "
            "make the pelvis handoff into the weight-bearing leg decisive."
        ),
    ))

    # ------------------------------------------------------------------
    # P1 / PASS 2 — pass memory is generated automatically here.
    # ------------------------------------------------------------------
    pass2_artifacts=run.prepare_stage_review()

    head2=run.prepare_local_review(
        label="head_face",
        intent="Re-check the carried lower-torso lean after EX-P1-R1.",
        subject_box=(235,0,495,250),
        drawing_box=(115,0,248,126),
    )
    pelvis2=run.prepare_local_review(
        label="pelvis_support",
        intent="Re-check the carried pelvis handoff after EX-P1-R1.",
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
        "pelvis segment is too vertical to show which leg carries the weight",
        "lower-torso lean is straighter than the subject's",
    ]
    assert [
        a["action_id"] for a in pass2_memory["inter_pass_correction_actions"]
    ]==["EX-P1-R1"]

    pass2=run.submit_stage_review(
        contract_findings=[
            "The corrected artifact still stays inside the P1 representation boundary.",
            "The correction changed the dominant gesture only; no downstream vocabulary was introduced.",
        ],
        subject_findings=[
            "The lower-torso lean now follows the subject at P1 abstraction.",
            "The pelvis now turns into the weight-bearing leg clearly enough to read.",
        ],
        grammar_findings=[
            "Stage grammar stays subordinate to the frozen contract and subject geometry.",
        ],
        drawing_findings=[
            "Both carried pass-1 concerns were re-checked against fresh whole/local artifacts.",
            "The line of action remains continuous and dominant from head to ground contact.",
            "No P1-purpose concern remains before introducing P2 axes.",
        ],
        local_review_ids=[head2.local_review_id,pelvis2.local_review_id],
        corrections=[
            "Re-drew the lower-torso lean of the line of action.",
            "Strengthened the pelvis handoff into the weight-bearing leg.",
        ],
        remaining_concerns=[],
        decision="advance",
        advance_rationale=(
            "Fresh pass-2 evidence clears both carried P1 concerns while preserving "
            "the frozen P1 contract; P2 primary axes may now be introduced."
        ),
    )

    trace={
        "schema":"img2drawing.canonical_example_trace.v1",
        "version":__import__("img2drawing").__version__,
        "example":"full_body_croquis",
        "stage":"P1_gesture",
        "initial_dominant_path_start":initial_dominant[0],
        "initial_dominant_path_start_semantics":"neck",
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
                "target":"line_of_action",
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
