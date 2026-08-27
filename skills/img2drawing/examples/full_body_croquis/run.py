from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from img2drawing import DrawingRun, ObservationContract, ViewObservation


HERE=Path(__file__).resolve().parent
SUBJECT=HERE/"subject.png"


# Coordinates below were densified once, offline, through a Catmull-Rom resample
# (see dev/p1_reference_run/ for the tool and rationale) so the runtime receives the
# same literal points a real worker would have drawn -- densely enough that the
# renderer's per-point hand jitter reads as texture on a curve, not a wobble, and
# sparsely enough that no corner survives from a five-point control cage. Nothing
# in the draw path rewrites what is authored here; the runtime never silently
# changes Agent-authored stroke geometry, matching the same rule the canvas scale
# guidance states elsewhere in this skill.
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
    initial_head_outline=[[253,34], [258,35], [263,38], [267,42], [271,48], [274,54], [275,62], [275,70], [273,80],
        [270,91], [266,102], [261,110], [257,116], [255,118], [253,118], [251,118], [248,116],
        [244,110], [240,102], [237,91], [234,80], [232,71], [232,62], [233,53], [236,46],
        [240,41], [244,37], [248,35], [253,34]]

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
            [[258,32], [261,41], [264,52], [266,62], [267,71], [265,81], [263,90], [262,96],
            [262,101], [261,110], [260,118]],
            grade="B",
            pressure=.66,
            width=2.8,
            opacity=.84,
            source="Facial centreline run through the marked crown, between-eyes, nose, mouth and chin — not down the outline's midpoint.",
        ),
        _stroke(
            "EX-P1-A3",
            "eye_line",
            [[236,66], [240,67], [246,68], [251,69], [256,70], [262,71], [268,72], [274,73],
            [279,73], [285,72], [289,70]],
            grade="HB",
            pressure=0.48,
            width=2.15,
            opacity=0.6,
            source="Eye line drawn through both pupils; its downward tilt toward the image-right is what those two positions give.",
        ),
        _stroke(
            "EX-P1-A4",
            "spine_centreline",
            [[253,142], [254,147], [254,154], [255,163], [256,172], [257,181], [257,190], [257,198],
            [257,207], [257,215], [256,223], [256,232], [255,240], [254,248], [253,257], [252,265],
            [252,274], [251,282], [250,290], [249,299], [249,308], [248,317], [248,326], [248,335],
            [248,344], [249,354], [249,364], [250,372], [250,378]],
            grade="B",
            pressure=0.72,
            width=3.1,
            opacity=0.9,
            source="The body's gesture: an S-curve from the middle of the neck through ribcage and abdomen to the pelvis.",
        ),
        _stroke(
            "EX-P1-A5",
            "shoulder_line",
            [[205,163], [211,161], [219,158], [228,155], [236,153], [245,152], [253,151], [261,151],
            [269,151], [277,152], [289,155], [298,157]],
            grade="HB",
            pressure=0.52,
            width=2.2,
            opacity=0.64,
            source="Shoulder tilt: the image-left shoulder sits lower, the image-right higher.",
        ),
        _stroke(
            "EX-P1-A6",
            "pelvis_centreline",
            [[204,374], [211,374], [222,375], [232,376], [241,377], [251,378], [260,379], [270,380],
            [279,381], [286,382]],
            grade="HB",
            pressure=0.52,
            width=2.2,
            opacity=0.64,
            source="Pelvis tilt counter to the shoulders: image-left higher, image-right lower.",
        ),
        _stroke(
            "EX-P1-arm_left_a",
            "arm_left_outer",
            [[197,163], [197,168], [196,175], [195,183], [194,192], [194,201], [193,210], [192,219],
            [191,228], [190,236], [189,244], [189,252], [188,260], [187,268], [186,276], [185,284],
            [184,292], [183,300], [182,308], [181,316], [180,324], [178,333], [177,341], [176,349],
            [175,357], [174,366], [173,375], [171,384], [170,394], [169,402], [168,410], [167,417],
            [166,422]],
            grade="HB",
            pressure=0.5,
            width=2.2,
            opacity=0.62,
            source="Image-left arm hangs almost straight; shoulder, elbow and wrist nearly align.",
        ),
        _stroke(
            "EX-P1-arm_left_b",
            "arm_left_inner",
            [[213,163], [212,168], [212,175], [211,183], [210,192], [208,201], [207,210], [206,219],
            [205,228], [204,236], [203,244], [202,252], [201,260], [200,268], [198,276], [197,284],
            [196,292], [195,300], [193,308], [192,316], [191,324], [189,333], [188,341], [186,349],
            [185,357], [184,366], [182,375], [180,384], [179,394], [177,402], [176,410], [175,417],
            [174,422]],
            grade="HB",
            pressure=0.5,
            width=2.2,
            opacity=0.62,
            source="Inner edge of the arm left tube.",
        ),
        _stroke(
            "EX-P1-arm_right_a",
            "arm_right_outer",
            [[290,157], [292,162], [295,169], [298,178], [302,187], [305,196], [308,205], [311,213],
            [313,222], [316,231], [318,239], [319,247], [319,255], [317,263], [313,271], [308,278],
            [302,285], [297,292], [292,300], [286,307], [280,315], [275,321], [272,326]],
            grade="HB",
            pressure=0.5,
            width=2.2,
            opacity=0.62,
            source="Image-right arm bends at the elbow; the hand is in the pocket, so the wrist endpoint is inferred.",
        ),
        _stroke(
            "EX-P1-arm_right_b",
            "arm_right_inner",
            [[306,157], [308,162], [310,169], [313,178], [317,187], [320,196], [322,205], [324,213],
            [327,222], [329,231], [331,239], [331,247], [331,255], [328,263], [324,271], [318,278],
            [313,285], [307,292], [301,300], [295,307], [289,315], [284,321], [280,326]],
            grade="HB",
            pressure=0.5,
            width=2.2,
            opacity=0.62,
            source="Inner edge of the arm right tube.",
        ),
        _stroke(
            "EX-P1-leg_left_a",
            "leg_left_outer",
            [[193,378], [194,383], [194,389], [195,397], [196,406], [197,415], [198,424], [199,434],
            [200,444], [201,453], [202,462], [203,470], [204,479], [205,487], [205,495], [206,504],
            [207,512], [208,520], [209,529], [210,537], [211,545], [212,553], [213,561], [215,569],
            [216,577], [217,585], [218,593], [220,601], [221,609], [223,617], [224,625], [225,633],
            [227,642], [229,652], [231,661], [232,670], [234,679], [236,687], [237,694], [238,700],
            [239,705]],
            grade="HB",
            pressure=0.5,
            width=2.2,
            opacity=0.62,
            source="Image-left leg carries the weight and its lower leg angles out to the foot.",
        ),
        _stroke(
            "EX-P1-leg_left_b",
            "leg_left_inner",
            [[223,378], [223,383], [223,389], [224,397], [224,406], [224,415], [225,424], [225,434],
            [225,444], [226,453], [226,462], [226,470], [227,479], [227,487], [228,495], [228,504],
            [229,512], [229,520], [230,529], [230,537], [231,545], [232,553], [233,561], [233,569],
            [234,577], [235,585], [236,593], [237,601], [238,609], [239,617], [240,625], [241,633],
            [242,642], [243,652], [245,661], [246,670], [247,679], [248,687], [249,694], [250,700],
            [251,705]],
            grade="HB",
            pressure=0.5,
            width=2.2,
            opacity=0.62,
            source="Inner edge of the leg left tube.",
        ),
        _stroke(
            "EX-P1-leg_right_a",
            "leg_right_outer",
            [[267,378], [268,383], [269,389], [270,397], [271,405], [273,415], [274,424], [276,434],
            [277,444], [279,453], [280,462], [281,470], [283,479], [284,487], [285,496], [287,504],
            [288,513], [289,522], [291,530], [292,539], [294,548], [296,556], [297,564], [299,573],
            [301,581], [303,590], [305,598], [306,606], [308,615], [310,623], [312,632], [314,640],
            [316,649], [318,658], [320,667], [322,677], [325,686], [327,695], [329,704], [331,712],
            [332,719], [334,725], [335,730]],
            grade="HB",
            pressure=0.5,
            width=2.2,
            opacity=0.62,
            source="Image-right leg steps further out with a relaxed knee.",
        ),
        _stroke(
            "EX-P1-leg_right_b",
            "leg_right_inner",
            [[297,378], [297,383], [298,389], [298,397], [299,405], [300,415], [301,424], [301,434],
            [302,444], [303,453], [304,462], [305,470], [306,479], [307,487], [307,496], [308,504],
            [309,513], [310,522], [312,530], [313,539], [314,548], [315,556], [317,564], [318,573],
            [319,581], [321,590], [322,598], [324,606], [325,615], [327,623], [328,632], [330,640],
            [332,649], [333,658], [335,667], [337,677], [339,686], [340,695], [342,704], [344,712],
            [345,719], [346,725], [347,730]],
            grade="HB",
            pressure=0.5,
            width=2.2,
            opacity=0.62,
            source="Inner edge of the leg right tube.",
        ),
        _stroke(
            "EX-P1-J_shoulder_L",
            "joint_shoulder_L",
            [[211,163], [211,165], [210,166], [209,167], [207,168], [206,169], [204,169], [202,169],
            [201,168], [200,167], [199,165], [199,163], [199,161], [200,159], [201,158], [202,157],
            [204,157], [206,157], [207,158], [209,159], [210,160], [211,161], [211,163]],
            grade="HB",
            pressure=0.44,
            width=2.0,
            opacity=0.55,
            source="shoulder L centre read from the subject.",
        ),
        _stroke(
            "EX-P1-J_shoulder_R",
            "joint_shoulder_R",
            [[304,157], [304,159], [303,160], [302,161], [300,162], [298,163], [297,163], [295,163],
            [294,162], [293,161], [292,159], [292,157], [292,155], [293,153], [294,152], [295,151],
            [297,151], [298,151], [300,152], [302,153], [303,154], [304,155], [304,157]],
            grade="HB",
            pressure=0.44,
            width=2.0,
            opacity=0.55,
            source="shoulder R centre read from the subject.",
        ),
        _stroke(
            "EX-P1-J_elbow_L",
            "joint_elbow_L",
            [[196,292], [196,294], [195,295], [194,296], [192,297], [190,298], [189,298], [187,298],
            [186,297], [185,296], [184,294], [184,292], [184,290], [185,288], [186,287], [187,286],
            [189,286], [190,286], [192,287], [194,288], [195,289], [196,290], [196,292]],
            grade="HB",
            pressure=0.44,
            width=2.0,
            opacity=0.55,
            source="elbow L centre read from the subject.",
        ),
        _stroke(
            "EX-P1-J_elbow_R",
            "joint_elbow_R",
            [[331,255], [331,257], [330,258], [329,259], [327,260], [326,261], [324,261], [322,261],
            [321,260], [320,259], [319,257], [319,255], [319,253], [320,251], [321,250], [322,249],
            [324,249], [326,249], [327,250], [329,251], [330,252], [331,253], [331,255]],
            grade="HB",
            pressure=0.44,
            width=2.0,
            opacity=0.55,
            source="elbow R centre read from the subject.",
        ),
        _stroke(
            "EX-P1-J_wrist_L",
            "joint_wrist_L",
            [[176,422], [176,424], [175,425], [174,426], [172,427], [170,428], [169,428], [167,428],
            [166,427], [165,426], [164,424], [164,422], [164,420], [165,418], [166,417], [167,416],
            [169,416], [170,416], [172,417], [174,418], [175,419], [176,420], [176,422]],
            grade="HB",
            pressure=0.44,
            width=2.0,
            opacity=0.55,
            source="wrist L centre read from the subject.",
        ),
        _stroke(
            "EX-P1-J_wrist_R",
            "joint_wrist_R",
            [[282,326], [282,328], [281,329], [280,330], [278,331], [276,332], [275,332], [273,332],
            [272,331], [271,330], [270,328], [270,326], [270,324], [271,322], [272,321], [273,320],
            [275,320], [276,320], [278,321], [280,322], [281,323], [282,324], [282,326]],
            grade="HB",
            pressure=0.44,
            width=2.0,
            opacity=0.55,
            source="wrist R centre read from the subject.",
        ),
        _stroke(
            "EX-P1-J_hip_L",
            "joint_hip_L",
            [[214,378], [214,380], [213,381], [212,382], [210,383], [208,384], [207,384], [205,384],
            [204,383], [203,382], [202,380], [202,378], [202,376], [203,374], [204,373], [205,372],
            [207,372], [208,372], [210,373], [212,374], [213,375], [214,376], [214,378]],
            grade="HB",
            pressure=0.44,
            width=2.0,
            opacity=0.55,
            source="hip L centre read from the subject.",
        ),
        _stroke(
            "EX-P1-J_hip_R",
            "joint_hip_R",
            [[288,378], [288,380], [287,381], [286,382], [284,383], [282,384], [281,384], [279,384],
            [278,383], [277,382], [276,380], [276,378], [276,376], [277,374], [278,373], [279,372],
            [281,372], [282,372], [284,373], [286,374], [287,375], [288,376], [288,378]],
            grade="HB",
            pressure=0.44,
            width=2.0,
            opacity=0.55,
            source="hip R centre read from the subject.",
        ),
        _stroke(
            "EX-P1-J_knee_L",
            "joint_knee_L",
            [[227,545], [227,547], [226,548], [225,549], [223,550], [222,551], [220,551], [218,551],
            [217,550], [216,549], [215,547], [215,545], [215,543], [216,541], [217,540], [218,539],
            [220,539], [222,539], [223,540], [225,541], [226,542], [227,543], [227,545]],
            grade="HB",
            pressure=0.44,
            width=2.0,
            opacity=0.55,
            source="knee L centre read from the subject.",
        ),
        _stroke(
            "EX-P1-J_knee_R",
            "joint_knee_R",
            [[310,548], [310,550], [309,551], [308,552], [306,553], [304,554], [303,554], [301,554],
            [300,553], [299,552], [298,550], [298,548], [298,546], [299,544], [300,543], [301,542],
            [303,542], [304,542], [306,543], [308,544], [309,545], [310,546], [310,548]],
            grade="HB",
            pressure=0.44,
            width=2.0,
            opacity=0.55,
            source="knee R centre read from the subject.",
        ),
        _stroke(
            "EX-P1-J_ankle_L",
            "joint_ankle_L",
            [[251,705], [251,707], [250,708], [249,709], [247,710], [246,711], [244,711], [242,711],
            [241,710], [240,709], [239,707], [239,705], [239,703], [240,701], [241,700], [242,699],
            [244,699], [246,699], [247,700], [249,701], [250,702], [251,703], [251,705]],
            grade="HB",
            pressure=0.44,
            width=2.0,
            opacity=0.55,
            source="ankle L centre read from the subject.",
        ),
        _stroke(
            "EX-P1-J_ankle_R",
            "joint_ankle_R",
            [[347,730], [347,732], [346,733], [345,734], [343,735], [342,736], [340,736], [338,736],
            [337,735], [336,734], [335,732], [335,730], [335,728], [336,726], [337,725], [338,724],
            [340,724], [342,724], [343,725], [345,726], [346,727], [347,728], [347,730]],
            grade="HB",
            pressure=0.44,
            width=2.0,
            opacity=0.55,
            source="ankle R centre read from the subject.",
        ),
        _stroke(
            "EX-P1-F_link_L",
            "ankle_foot_link_left",
            [[245,705], [245,706], [246,708], [248,711], [250,713]],
            grade="HB",
            pressure=0.46,
            width=2.05,
            opacity=0.56,
            source="Link from the image-left ankle into the shoe.",
        ),
        _stroke(
            "EX-P1-F_L",
            "foot_direction_left",
            [[240,706], [249,706], [259,706], [267,708], [273,713], [275,720], [275,728], [270,736],
            [262,740], [252,744], [243,747], [232,748], [223,746], [215,742], [210,737], [208,733],
            [209,728], [212,720], [218,713], [228,708], [240,706]],
            grade="HB",
            pressure=0.5,
            width=2.2,
            opacity=0.62,
            source="Image-left shoe read from the subject: its toe swings across the body toward the image-left.",
        ),
        _stroke(
            "EX-P1-F_link_R",
            "ankle_foot_link_right",
            [[341,730], [339,731], [337,733], [335,736], [333,738]],
            grade="HB",
            pressure=0.46,
            width=2.05,
            opacity=0.56,
            source="Link from the image-right ankle into the shoe.",
        ),
        _stroke(
            "EX-P1-F_R",
            "foot_direction_right",
            [[327,739], [337,736], [350,734], [358,734], [367,735], [375,737], [386,743], [393,750],
            [395,757], [392,763], [386,768], [376,772], [367,775], [358,776], [348,776], [340,774],
            [330,769], [322,762], [319,756], [319,750], [321,744], [327,739]],
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
    corrected_head_outline=[[258,32], [265,33], [272,36], [278,40], [283,46], [287,53], [290,60], [291,68], [291,76],
        [289,86], [285,96], [280,105], [274,112], [269,117], [264,120], [258,119], [252,116],
        [246,110], [241,102], [237,93], [234,84], [232,74], [232,64], [234,54], [238,46],
        [242,40], [247,36], [252,33], [258,32]]
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
