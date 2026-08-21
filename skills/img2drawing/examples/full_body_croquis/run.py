from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from img2drawing import DrawingRun


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
    crown-origin gesture → fresh artifact review → local evidence → REVISE →
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

    # ------------------------------------------------------------------
    # P1 / PASS 1
    # ------------------------------------------------------------------
    run.stage_start("P1_gesture")

    # Non-negotiable: the dominant centre gesture starts at the crown, passes
    # through a curved facial centre, then continues through chin/neck/spine/
    # pelvis/support leg. Pass 1 is intentionally under-curved at face/pelvis
    # so the example demonstrates a real revise cycle.
    initial_dominant=[
        [190,8],      # crown
        [192,30],
        [193,53],     # facial centre: deliberately too straight in pass 1
        [188,78],
        [182,98],     # chin / neck handoff
        [178,142],
        [174,192],
        [174,238],
        [172,266],    # pelvis handoff: deliberately weak
        [165,306],
        [159,358],
        [160,415],
        [166,482],
        [173,548],    # support landing
    ]

    run.draw_many([
        _stroke(
            "EX-P1-A1",
            "crown_face_spine_support",
            initial_dominant,
            role="gesture",
            pressure=.40,
            width=1.85,
            opacity=.58,
            grade="HB",
            confidence=.92,
            source=(
                "Observed crown→facial-centre→chin→neck→spine→pelvis→"
                "image-left support-leg path."
            ),
        ),
        _stroke(
            "EX-P1-A2",
            "head_left_envelope",
            [[190,8],[165,9],[151,30],[152,60],[161,82],[182,98]],
            pressure=.20,
            width=1.12,
            opacity=.27,
            source="Open image-left cranial/jaw envelope; subordinate to facial centre.",
        ),
        _stroke(
            "EX-P1-A3",
            "head_right_envelope",
            [[190,8],[213,11],[223,34],[219,63],[207,84],[182,98]],
            pressure=.20,
            width=1.12,
            opacity=.27,
            source="Open image-right cranial/jaw envelope; not a closed oval.",
        ),
        _stroke(
            "EX-P1-A4",
            "shoulder_rhythm",
            [[120,137],[151,122],[186,112],[222,108],[258,118]],
            pressure=.17,
            width=1.05,
            opacity=.21,
            source="Broad shoulder rhythm only; no ribcage mass.",
        ),
        _stroke(
            "EX-P1-A5",
            "pelvis_rhythm",
            [[130,250],[151,242],[176,241],[201,248],[226,266]],
            pressure=.17,
            width=1.05,
            opacity=.21,
            source="Open pelvis rhythm indicating tilt without closing a pelvis mass.",
        ),
        _stroke(
            "EX-P1-A6",
            "counterbalance_leg",
            [[191,276],[210,331],[232,405],[255,486],[278,560]],
            pressure=.15,
            width=1.02,
            opacity=.18,
            source="Image-right counterbalance leg stays subordinate to support path.",
        ),
    ])

    pass1_artifacts=run.prepare_stage_review()

    # Agent-selected local evidence. Runtime does not locate anatomy.
    head1=run.prepare_local_review(
        label="head_face",
        intent="Check facial-centre curvature and unequal left/right head masses.",
        subject_box=(235,0,495,250),
        drawing_box=(115,0,248,126),
        grammar_box=(25,20,255,285),
    )
    pelvis1=run.prepare_local_review(
        label="pelvis_support",
        intent="Check pelvis-to-support-leg directional handoff and weight transfer.",
        subject_box=(190,430,570,1145),
        drawing_box=(95,215,286,575),
        grammar_box=(15,390,275,1070),
    )

    pass1=run.submit_stage_review(
        contract_findings=[
            "The drawing stays inside the P1 gesture/weight-path contract.",
            "No ribcage/pelvis mass closure, joint anatomy, clothing contour, or final silhouette leaked in.",
        ],
        subject_findings=[
            "The subject shows a more curved face-direction centre than pass 1.",
            "The subject's pelvis-to-image-left support transfer changes direction more decisively than pass 1.",
        ],
        exemplar_findings=[
            "The bundled P1 grammar exemplar is a known failed exemplar; its pose is not copied.",
            "Only its broad gesture economy is used where it does not conflict with the frozen P1 contract.",
        ],
        drawing_findings=[
            "The dominant line correctly starts at the crown and remains continuous to the support landing.",
            "Its facial-centre segment is too straight, weakening face direction.",
            "Its pelvis-to-support segment is too vertical/soft, weakening weight transfer.",
        ],
        local_review_ids=[head1.local_review_id,pelvis1.local_review_id],
        corrections=[],
        remaining_concerns=[
            "facial-centre curve is too straight to carry face direction clearly",
            "pelvis-to-support transfer is too weak",
        ],
        decision="revise",
    )

    # ------------------------------------------------------------------
    # CORRECTION BETWEEN PASSES
    # ------------------------------------------------------------------
    corrected_dominant=[
        [190,8],
        [192,27],
        [197,47],     # stronger face-direction bow
        [195,67],
        [188,84],
        [181,99],
        [177,143],
        [172,193],
        [173,238],
        [178,255],
        [171,276],    # clearer directional break into support side
        [160,302],
        [154,352],
        [156,410],
        [164,482],
        [173,548],
    ]
    run.draw(_replace(
        "EX-P1-R1",
        "crown_face_spine_support",
        corrected_dominant,
        reason=(
            "Pass 1 carried two concerns: strengthen the facial-centre bow and "
            "make the pelvis→support-leg handoff more decisive."
        ),
    ))

    # ------------------------------------------------------------------
    # P1 / PASS 2 — pass memory is generated automatically here.
    # ------------------------------------------------------------------
    pass2_artifacts=run.prepare_stage_review()

    head2=run.prepare_local_review(
        label="head_face",
        intent="Re-check the carried face-direction concern after EX-P1-R1.",
        subject_box=(235,0,495,250),
        drawing_box=(115,0,248,126),
        grammar_box=(25,20,255,285),
    )
    pelvis2=run.prepare_local_review(
        label="pelvis_support",
        intent="Re-check the carried pelvis/support concern after EX-P1-R1.",
        subject_box=(190,430,570,1145),
        drawing_box=(95,215,286,575),
        grammar_box=(15,390,275,1070),
    )

    pass2_memory=json.loads(
        (output/"reviews/P1_gesture/pass_02/pass_memory.json").read_text(encoding="utf-8")
    )

    # The worker reads carried concerns and action provenance before deciding.
    assert pass2_memory["state"]=="revision_continuation"
    assert pass2_memory["previous_decision"]=="revise"
    assert pass2_memory["carried_concerns"]==[
        "facial-centre curve is too straight to carry face direction clearly",
        "pelvis-to-support transfer is too weak",
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
            "The facial-centre bow now communicates the subject's face direction at P1 abstraction.",
            "The pelvis-to-support path now changes direction clearly enough to communicate weight transfer.",
        ],
        exemplar_findings=[
            "The known-defect P1 exemplar remains subordinate to the frozen contract and subject geometry.",
        ],
        drawing_findings=[
            "Both carried pass-1 concerns were re-checked against fresh whole/local artifacts.",
            "The crown→face→chin→neck→spine→pelvis→support intention remains continuous and dominant.",
            "No P1-purpose concern remains before introducing P2 axes.",
        ],
        local_review_ids=[head2.local_review_id,pelvis2.local_review_id],
        corrections=[
            "Re-curved the facial-centre segment.",
            "Strengthened the pelvis-to-support directional handoff.",
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
                "target":"crown_face_spine_support",
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
        default=HERE/"output",
        help="Output directory for canonical example artifacts.",
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
