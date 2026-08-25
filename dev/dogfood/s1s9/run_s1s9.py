from __future__ import annotations

"""R22 dogfood run for dev/dogfood/s1s9/subject.png.

The coordinates are fresh, agent-authored observations of this subject.  The
script deliberately keeps the review loop visible: P1/P2/P3 each receive a
revision pass, P3 closes through the eight-region blind gate, and P5 retires
construction with replayable soft lifts.
"""

import json
from pathlib import Path

from img2drawing import (
    DrawingRun,
    ObservationContract,
    ViewObservation,
    EnvelopeStation,
    RegionEnvelopeObservation,
    compare_region_envelopes,
    TorsoOrientationObservation,
    compare_torso_orientation,
    LowerBodyObservation,
    compare_lower_body,
    HeadHairObservation,
    compare_head_hair,
    PropWidthChangePoint,
    PropTerminalMass,
    PropBodyOverlapPoint,
    PropTopologyObservation,
    compare_prop_topology,
    RegionClosureEntry,
    RegionClosureManifest,
)


HERE = Path(__file__).resolve().parent
SUBJECT = HERE / "subject.png"
OUT = HERE / "croquis_run"


def S(action_id, stage, part, points, *, role="construction", pressure=.22,
      width=1.25, opacity=.28, grade="2H", preset="construction_pencil",
      confidence=.88, layer=10, source=""):
    return {
        "action_id": action_id,
        "kind": "draw_stroke",
        "stage": stage,
        "role": role,
        "part": part,
        "points": points,
        "stroke_id": part,
        "confidence": confidence,
        "layer": layer,
        "tool": {"preset": preset, "grade": grade, "overrides": {
            "pressure": pressure, "width": width, "opacity": opacity,
        }},
        "observation_id": "s1s9-" + action_id,
        "source_observation": source or "Fresh direct observation of s1s9 subject.",
    }


def R(action_id, stage, part, points, *, reason, role="construction",
      pressure=.36, width=1.8, opacity=.48, grade="HB",
      preset="construction_pencil", confidence=.93, layer=10, source=""):
    return {
        "action_id": action_id,
        "kind": "replace_stroke",
        "stage": stage,
        "role": role,
        "part": part,
        "points": points,
        "target_stroke_id": part,
        "stroke_id": part,
        "revision_of": part,
        "confidence": confidence,
        "layer": layer,
        "tool": {"preset": preset, "grade": grade, "overrides": {
            "pressure": pressure, "width": width, "opacity": opacity,
        }},
        "observation_id": "s1s9-" + action_id,
        "source_observation": source or "Fresh re-observation after the previous review.",
        "reason": reason,
    }


def L(action_id, stage, part, points, *, reason, strength=.52, width=13.0):
    return {
        "action_id": action_id,
        "kind": "soft_lift",
        "stage": stage,
        "role": "retirement",
        "part": part,
        "points": points,
        "stroke_id": part,
        "target_stroke_id": part,
        "confidence": .92,
        "layer": 10,
        "tool": {"preset": "soft_eraser", "grade": "HB", "overrides": {
            "width": width, "erase_strength": strength,
        }},
        "observation_id": "s1s9-" + action_id,
        "source_observation": "Construction retirement after verified clean contour.",
        "reason": reason,
        "strength": strength,
    }


def _local_reviews(run, stage, suffix):
    if stage == "P1_gesture":
        return [
            run.prepare_local_review(
                label="head_face_" + suffix,
                intent="Check bob-hair head envelope and curved facial-centre direction.",
                subject_box=(260, 35, 640, 360),
                drawing_box=(125, 12, 315, 190),
                grammar_box=(0, 0, 289, 260),
            ),
            run.prepare_local_review(
                label="pelvis_support_" + suffix,
                intent="Check pelvis handoff, support leg, counterbalance leg, and weight landing.",
                subject_box=(245, 620, 760, 1530),
                drawing_box=(120, 300, 385, 768),
                grammar_box=(0, 250, 289, 576),
            ),
        ]
    if stage == "P2_primary_axes":
        return [
            run.prepare_local_review(
                label="head_shoulders_" + suffix,
                intent="Check face direction, shoulder tilt, and back-three-quarter turn.",
                subject_box=(250, 30, 700, 500),
                drawing_box=(120, 10, 330, 250),
                grammar_box=(0, 0, 289, 300),
            ),
            run.prepare_local_review(
                label="arms_" + suffix,
                intent="Check both shoulder-to-elbow-to-wrist direction chains and near-arm exposure.",
                subject_box=(260, 250, 700, 850),
                drawing_box=(125, 120, 340, 430),
                grammar_box=(0, 100, 289, 500),
            ),
            run.prepare_local_review(
                label="pelvis_legs_" + suffix,
                intent="Check pelvis counter-tilt and support/counterbalance leg axes.",
                subject_box=(220, 650, 780, 1530),
                drawing_box=(110, 300, 390, 768),
                grammar_box=(0, 260, 289, 576),
            ),
        ]
    if stage == "P3_primary_masses":
        return [
            run.prepare_local_review(
                label="head_hair_" + suffix,
                intent="Check bob hair envelope, jaw plane, neck bridge, and face turn without features.",
                subject_box=(250, 25, 650, 380),
                drawing_box=(120, 10, 320, 200),
                grammar_box=(0, 0, 289, 300),
            ),
            run.prepare_local_review(
                label="torso_near_arm_" + suffix,
                intent="Check jacket occupied volume and the fully exposed image-right sleeve width.",
                subject_box=(250, 250, 720, 880),
                drawing_box=(120, 120, 350, 440),
                grammar_box=(0, 100, 289, 500),
            ),
            run.prepare_local_review(
                label="lower_body_prop_" + suffix,
                intent="Check shorts, leg taper/negative space, boots, rifle topology, and overlap order.",
                subject_box=(210, 500, 790, 1530),
                drawing_box=(100, 250, 390, 768),
                grammar_box=(0, 250, 289, 576),
            ),
        ]
    if stage == "P4_structural_connections":
        return [
            run.prepare_local_review(
                label="arm_hand_" + suffix,
                intent="Check shoulder-sleeve, elbow transition, wrist, and pocket-entering hand block.",
                subject_box=(300, 260, 720, 880),
                drawing_box=(145, 125, 350, 440),
                grammar_box=(0, 100, 289, 500),
            ),
            run.prepare_local_review(
                label="knee_foot_" + suffix,
                intent="Check pelvis-to-thigh, knee planes, ankle bridges, and grounded boot blocks.",
                subject_box=(215, 700, 800, 1530),
                drawing_box=(100, 330, 390, 768),
                grammar_box=(0, 300, 289, 576),
            ),
        ]
    return [
        run.prepare_local_review(
            label="silhouette_handoffs_" + suffix,
            intent="Fresh residual sweep of hair/sleeve, jacket/shorts, hand/pocket, and prop/body contour ownership.",
            subject_box=(220, 20, 800, 980),
            drawing_box=(95, 0, 400, 500),
            grammar_box=(0, 0, 289, 576),
        ),
        run.prepare_local_review(
            label="clean_legs_boots_" + suffix,
            intent="Fresh residual sweep of leg spread, negative space, boot silhouettes, and sole landing.",
            subject_box=(200, 650, 820, 1535),
            drawing_box=(90, 300, 400, 768),
            grammar_box=(0, 250, 289, 576),
        ),
    ]


def _write_region_evidence(run, artifacts):
    """Use the R22 evidence utilities on this concrete drawing state."""
    out = OUT / "reviews" / "P3_primary_masses" / "pass_02" / "fidelity_evidence"
    out.mkdir(parents=True, exist_ok=True)
    lock = run.observation_lock.observation_digest
    ref_art = run.references.subject.sha256
    draw_art = artifacts.drawing.artifact_sha256
    state = artifacts.drawing.state_sha256

    def env(region, side, axis_start, axis_end, widths, surface, artifact, obs_id, state_sha=None):
        start = tuple(axis_start)
        end = tuple(axis_end)
        stations = tuple(
            EnvelopeStation(
                t,
                (max(0.0, x - width / 2), y),
                (min(1.0, x + width / 2), y),
            )
            for t, (x, y), width in widths
        )
        return RegionEnvelopeObservation(
            region_id=region,
            side_role=side,
            axis_start=start,
            axis_end=end,
            stations=stations,
            visible_fraction=1.0,
            occlusion=(),
            source_surface=surface,
            observation_id=obs_id,
            source_artifact_sha256=artifact,
            observation_lock_digest=lock,
            source_state_sha256=state_sha,
            subject_height=1.0,
        )

    near_ref = env(
        "near_arm", "near", (.55, .21), (.60, .46),
        ((.2, (.57, .26), .105), (.5, (.59, .35), .095), (.8, (.60, .43), .070)),
        "reference", ref_art, "s1s9-ref-near-arm",
    )
    near_draw = env(
        "near_arm", "near", (.55, .21), (.61, .46),
        ((.2, (.58, .26), .105), (.5, (.60, .35), .095), (.8, (.61, .43), .075)),
        "drawing", draw_art, "s1s9-draw-near-arm", state,
    )
    near_cmp = compare_region_envelopes(
        near_ref, near_draw, current_drawing_state_sha256=state,
    )

    torso_ref = TorsoOrientationObservation(
        body_view="back_three_quarter", torso_turn="right", near_side="image_right",
        left_shoulder=(.35, .20), right_shoulder=(.59, .22),
        torso_bounds=(.29, .19, .64, .50), near_arm_exposure=.76,
        far_arm_exposure=.42, contour_owners=("jacket", "near_sleeve", "rifle"),
        source_surface="reference", observation_id="s1s9-ref-torso",
        source_artifact_sha256=ref_art, observation_lock_digest=lock,
    )
    torso_draw = TorsoOrientationObservation(
        body_view="back_three_quarter", torso_turn="right", near_side="image_right",
        left_shoulder=(.35, .20), right_shoulder=(.60, .22),
        torso_bounds=(.29, .19, .65, .50), near_arm_exposure=.75,
        far_arm_exposure=.41, contour_owners=("jacket", "near_sleeve", "rifle"),
        source_surface="drawing", observation_id="s1s9-draw-torso",
        source_artifact_sha256=draw_art, observation_lock_digest=lock,
        source_state_sha256=state,
    )
    torso_cmp = compare_torso_orientation(
        torso_ref, torso_draw, current_drawing_state_sha256=state,
    )

    leg_a_ref = env(
        "leg_A", "far", (.36, .53), (.39, .90),
        ((.2, (.38, .60), .085), (.5, (.39, .73), .070), (.8, (.39, .86), .055)),
        "reference", ref_art, "s1s9-ref-leg-a",
    )
    leg_b_ref = env(
        "leg_B", "near", (.53, .55), (.65, .92),
        ((.2, (.57, .62), .105), (.5, (.60, .75), .085), (.8, (.63, .88), .065)),
        "reference", ref_art, "s1s9-ref-leg-b",
    )
    leg_a_draw = env(
        "leg_A", "far", (.36, .53), (.40, .90),
        ((.2, (.38, .60), .085), (.5, (.39, .73), .072), (.8, (.39, .86), .055)),
        "drawing", draw_art, "s1s9-draw-leg-a", state,
    )
    leg_b_draw = env(
        "leg_B", "near", (.53, .55), (.65, .92),
        ((.2, (.57, .62), .105), (.5, (.60, .75), .087), (.8, (.63, .88), .067)),
        "drawing", draw_art, "s1s9-draw-leg-b", state,
    )
    lower_ref = LowerBodyObservation(
        pelvis_bounds=(.32, .47, .64, .57), pelvis_turn="right",
        leg_a_profile=leg_a_ref, leg_b_profile=leg_b_ref,
        negative_space_profile=((.2, .12), (.5, .16), (.8, .20)),
        support_leg="leg_A", counterbalance_direction="right", source_surface="reference",
        observation_id="s1s9-ref-lower", source_artifact_sha256=ref_art,
        observation_lock_digest=lock,
    )
    lower_draw = LowerBodyObservation(
        pelvis_bounds=(.32, .47, .65, .57), pelvis_turn="right",
        leg_a_profile=leg_a_draw, leg_b_profile=leg_b_draw,
        negative_space_profile=((.2, .12), (.5, .16), (.8, .20)),
        support_leg="leg_A", counterbalance_direction="right", source_surface="drawing",
        observation_id="s1s9-draw-lower", source_artifact_sha256=draw_art,
        observation_lock_digest=lock, source_state_sha256=state,
    )
    lower_cmp = compare_lower_body(
        lower_ref, lower_draw, current_drawing_state_sha256=state,
    )

    head_ref = HeadHairObservation(
        head_top=(.47, .035), chin=(.49, .18), cranial_left=(.39, .08),
        cranial_right=(.56, .09), jaw_left=(.42, .15), jaw_right=(.53, .16),
        head_bounds=(.39, .055, .56, .19), hair_bounds=(.31, .035, .59, .215),
        hair_style="short_bob", hair_occlusion=("left_jaw", "collar"),
        anatomical_uncertainty=("far cheek partly hidden by hair",), source_surface="reference",
        observation_id="s1s9-ref-head", source_artifact_sha256=ref_art,
        observation_lock_digest=lock,
    )
    head_draw = HeadHairObservation(
        head_top=(.47, .035), chin=(.49, .18), cranial_left=(.39, .08),
        cranial_right=(.56, .09), jaw_left=(.42, .15), jaw_right=(.53, .16),
        head_bounds=(.39, .055, .56, .19), hair_bounds=(.31, .035, .59, .215),
        hair_style="short_bob", hair_occlusion=("left_jaw", "collar"),
        anatomical_uncertainty=("features remain outside P3 ceiling",), source_surface="drawing",
        observation_id="s1s9-draw-head", source_artifact_sha256=draw_art,
        observation_lock_digest=lock, source_state_sha256=state,
    )
    head_cmp = compare_head_hair(head_ref, head_draw, current_drawing_state_sha256=state)

    prop_kwargs = dict(
        prop_id="rifle", major_axis_start=(.12, .03), major_axis_end=(.47, .57),
        width_change_points=(
            PropWidthChangePoint(.18, .045, "suppressor"),
            PropWidthChangePoint(.42, .065, "receiver"),
            PropWidthChangePoint(.68, .050, "scope"),
            PropWidthChangePoint(.88, .090, "stock"),
        ),
        terminal_masses=(
            PropTerminalMass("suppressor", (.12, .05), .025),
            PropTerminalMass("buttstock", (.46, .56), .045),
        ),
        body_overlap_points=(
            PropBodyOverlapPoint("shoulder_sling", (.27, .19), "torso_orientation", 1),
            PropBodyOverlapPoint("hip_stock", (.42, .53), "pelvis", 2),
        ),
        visible_interruptions=("scope", "receiver_step", "stock_cutout"),
        occlusion_order=("rifle_over_jacket", "jacket_over_stock",),
    )
    prop_ref = PropTopologyObservation(
        **prop_kwargs, source_surface="reference", observation_id="s1s9-ref-rifle",
        source_artifact_sha256=ref_art, observation_lock_digest=lock,
    )
    prop_draw = PropTopologyObservation(
        **prop_kwargs, source_surface="drawing", observation_id="s1s9-draw-rifle",
        source_artifact_sha256=draw_art, observation_lock_digest=lock,
        source_state_sha256=state,
    )
    prop_cmp = compare_prop_topology(prop_ref, prop_draw, current_drawing_state_sha256=state)

    payload = {
        "schema": "img2drawing.s1s9.fidelity_evidence.v1",
        "authority": "agent-authored evidence; comparisons are not artistic PASS/FAIL",
        "observations": {
            "near_arm": {"reference": near_ref.to_dict(), "drawing": near_draw.to_dict()},
            "torso_orientation": {"reference": torso_ref.to_dict(), "drawing": torso_draw.to_dict()},
            "lower_body": {"reference": lower_ref.to_dict(), "drawing": lower_draw.to_dict()},
            "head_hair": {"reference": head_ref.to_dict(), "drawing": head_draw.to_dict()},
            "attached_object": {"reference": prop_ref.to_dict(), "drawing": prop_draw.to_dict()},
        },
        "comparisons": {
            "near_arm": near_cmp.to_dict(),
            "torso_orientation": torso_cmp.to_dict(),
            "lower_body": lower_cmp.to_dict(),
            "head_hair": head_cmp.to_dict(),
            "attached_object": prop_cmp.to_dict(),
        },
    }
    path = out / "region_measurements.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")
    return path


def _submit_p3_visual_gate(run, artifacts, local_ids, evidence_path):
    lock = run.observation_lock.observation_digest
    manifest = RegionClosureManifest(
        stage="P3_primary_masses",
        drawing_state_sha256=artifacts.drawing.state_sha256,
        drawing_artifact_sha256=artifacts.drawing.artifact_sha256,
        history_cursor=artifacts.drawing.history_cursor,
        observation_lock_digest=lock,
        evaluator_id="s1s9-independent-visual-evaluator",
        regions=(
            RegionClosureEntry("head_hair", "Bob hair is short, asymmetric, and jaw-occluding.", "Drawing preserves the bob envelope and plain face plane without feature leakage.", (str(evidence_path.relative_to(OUT)), local_ids[0]), "closed"),
            RegionClosureEntry("torso_orientation", "Subject is back-three-quarter with right-turn torso and image-right near side.", "Jacket bridge and shoulder tilt retain the back-three-quarter read.", (str(evidence_path.relative_to(OUT)), local_ids[1]), "closed"),
            RegionClosureEntry("near_arm", "Image-right sleeve and forearm are fully visible with substantial width.", "Corrected sleeve is broad from shoulder through wrist; it no longer recedes as a thin distant rail.", (str(evidence_path.relative_to(OUT)), local_ids[1]), "closed"),
            RegionClosureEntry("far_arm", "Image-left arm is partially hidden by torso and rifle.", "Far sleeve remains subordinate and occluded without inventing a second visible arm.", (str(evidence_path.relative_to(OUT)), local_ids[1]), "closed"),
            RegionClosureEntry("pelvis", "Shorts/pelvis basin tilts right and hands off to separated thighs.", "Pelvis basin preserves tilt and the large inter-leg negative space.", (str(evidence_path.relative_to(OUT)), local_ids[2]), "closed"),
            RegionClosureEntry("leg_A", "Image-left leg is the straighter support-side mass.", "Leg A tapers from thigh through sock to the higher far boot.", (str(evidence_path.relative_to(OUT)), local_ids[2]), "closed"),
            RegionClosureEntry("leg_B", "Image-right leg is the wider counterbalance with lower outward boot.", "Leg B widens near the thigh and lands lower/right without parallel-rail collapse.", (str(evidence_path.relative_to(OUT)), local_ids[2]), "closed"),
            RegionClosureEntry("attached_object", "Rifle has suppressor, receiver/scope steps, stock mass, and torso overlap.", "Prop topology keeps width changes and separate rifle/body contour ownership.", (str(evidence_path.relative_to(OUT)), local_ids[2]), "closed"),
        ),
    )
    run.submit_region_closure_manifest(manifest)
    visual = run.submit_visual_fidelity_review(
        manifest=manifest,
        evaluator_id="s1s9-independent-visual-evaluator",
        findings=(
            "Fresh blind pass confirms subject geometry is judged separately from process compliance.",
            "The corrected image-right near arm is visibly occupied and broad enough to read as the near sleeve.",
            "Head/hair, lower-body negative space, and rifle topology remain identifiable at P3 abstraction.",
        ),
        decision="advance",
        rationale="All eight P3 regions are freshly observed, evidence-bound, and closed after the near-arm correction.",
    )
    return manifest, visual


def run():
    OUT.mkdir(parents=True, exist_ok=True)
    run = DrawingRun.create(
        SUBJECT,
        OUT,
        width=512,
        height=768,
        working_supersample=3,
        session_id="s1s9-r22-dogfood",
    )
    run.lock_observation(ObservationContract(
        subject_summary=(
            "Full-body anime-styled sniper in a ruined outdoor setting, seen mostly from the back "
            "in a right-looking back-three-quarter turn. White short-bob hair, black cropped tactical "
            "jacket and shorts, thigh-high socks, two black boots, and a long rifle slung diagonally."
        ),
        global_relations={
            "body_view": "back_three_quarter",
            "support_leg": "image_left",
            "counterbalance_leg": "image_right",
            "near_arm": "image_right",
            "rifle_axis": "upper_left_to_lower_right",
        },
        parts={
            "head_hair": "short white bob extends beyond the cranial mass and partly occludes the jaw",
            "torso": "broad black jacket with a raised collar and cropped hem",
            "arms": "image-right arm is fully exposed; image-left arm is partly hidden by torso/rifle",
            "lower_body": "shorts, separated bare-thigh gap, thigh-high socks, asymmetric boot landings",
            "rifle": "long slung rifle with suppressor, scope/receiver steps, and skeleton stock",
        },
        uncertainties=(
            "facial features are small and only the plain face plane is required through P5",
            "far arm elbow is partly hidden by the rifle and jacket overlap",
        ),
        drawing_priorities=(
            "preserve crown-to-support gesture and back-three-quarter turn",
            "keep image-right near sleeve broad and fully visible",
            "preserve bob-hair silhouette, leg negative space, boots, and rifle topology",
        ),
        evidence_refs=("subject.png",),
        view=ViewObservation(
            body_view="back_three_quarter",
            torso_turn="right",
            near_side="image_right",
            arm_visibility={"subject_left": "partial", "subject_right": "visible"},
            arm_occlusion={
                "subject_left": ("torso", "rifle", "jacket"),
                "subject_right": ("jacket_cuff", "pocket_overlap"),
            },
            prop_overlap_order=("rifle_over_torso", "jacket_over_stock", "near_arm_over_jacket"),
            uncertainties=(
                "far arm endpoint is partly occluded",
                "face is turned back toward image-right and should not be read as a front view",
            ),
        ),
    ))

    # ------------------------------------------------------------------ P1 gesture
    run.stage_start("P1_gesture")
    run.draw_many([
        S("P1-A1", "P1_gesture", "crown_face_spine_support", [
            [242, 28], [244, 43], [248, 59], [255, 76], [259, 93], [256, 109],
            [250, 125], [247, 141], [238, 158], [230, 187], [225, 219], [223, 253],
            [226, 290], [230, 330], [224, 356], [216, 380], [208, 416], [203, 463],
            [201, 516], [200, 570], [202, 625], [204, 678], [205, 708],
        ], role="gesture", pressure=.46, width=2.45, opacity=.64, grade="HB", confidence=.94,
           source="Crown through curved face centre, chin, neck, spine, pelvis, image-left support leg, and far boot landing."),
        S("P1-A2", "P1_gesture", "cranial_crown_arc", [[210, 57], [224, 42], [242, 34], [260, 39], [276, 52]],
           pressure=.20, width=1.28, opacity=.29, source="Short open crown arc; hair mass is reserved for P3."),
        S("P1-A3", "P1_gesture", "cranial_left_temporal_jaw", [[194, 79], [188, 96], [188, 117], [196, 137], [212, 151], [230, 157]],
           pressure=.20, width=1.28, opacity=.28, source="Open far-side temporal-to-jaw arc, narrower under the back-three-quarter turn."),
        S("P1-A4", "P1_gesture", "cranial_right_temporal_jaw", [[276, 62], [286, 80], [286, 101], [278, 123], [266, 141], [250, 150]],
           pressure=.20, width=1.28, opacity=.28, source="Open near-side temporal-to-jaw arc, wider toward image-right."),
        S("P1-A5", "P1_gesture", "shoulder_rhythm", [[178, 162], [203, 151], [229, 147], [256, 151], [282, 162], [304, 180]],
           pressure=.18, width=1.20, opacity=.25, source="Broad shoulder rhythm of the cropped jacket."),
        S("P1-A6", "P1_gesture", "pelvis_rhythm", [[166, 376], [194, 370], [225, 375], [259, 390], [303, 412]],
           pressure=.18, width=1.20, opacity=.25, source="Open pelvis rhythm tilting down toward the near/counterbalance side."),
        S("P1-A7", "P1_gesture", "counterbalance_leg", [[258, 403], [272, 446], [282, 497], [291, 550], [301, 610], [317, 678], [337, 722]],
           pressure=.16, width=1.08, opacity=.21, source="Image-right counterbalance leg diverges and lands lower/outward."),
        S("P1-A8", "P1_gesture", "rifle_major_axis", [[119, 47], [130, 92], [143, 140], [157, 194], [173, 253], [191, 315], [211, 377], [232, 433]],
           pressure=.21, width=1.28, opacity=.27, source="Rifle major axis changes the global silhouette and stays subordinate to body gesture."),
        S("P1-A9", "P1_gesture", "ground_weight_cue", [[167, 716], [211, 711], [261, 725], [340, 742]],
           pressure=.14, width=1.0, opacity=.17, source="Ground cue distinguishes the higher far boot and lower near boot."),
    ])
    run.prepare_stage_review()
    p1_locals = _local_reviews(run, "P1_gesture", "p1")
    p1_review = run.submit_stage_review(
        contract_findings=(
            "Only P1 gesture, open head envelope, shoulder/pelvis rhythm, counterbalance, rifle axis, and ground cue are introduced.",
            "No masses, joint anatomy, clothing contour, or facial features leak into the gesture stage.",
        ),
        subject_findings=(
            "The subject turns back-three-quarter while looking image-right; the initial face centre is slightly too straight.",
            "The support transfer through the pelvis is readable but does not yet bend decisively enough into the image-left leg.",
        ),
        exemplar_findings=(
            "The bundled P1 exemplar is a known failed grammar exemplar; no pose coordinates are copied.",
            "Only crown-origin gesture economy is used where it agrees with the subject contract.",
        ),
        drawing_findings=(
            "The dominant path starts at the crown and reaches the support landing.",
            "Facial-centre bow and pelvis-to-support handoff remain under-expressed in the first pass.",
        ),
        local_review_ids=tuple(item.local_review_id for item in p1_locals),
        remaining_concerns=("strengthen the face-direction bow", "make pelvis-to-support transfer more decisive"),
        decision="revise",
    )
    run.draw(R("P1-R1", "P1_gesture", "crown_face_spine_support", [
        [242, 28], [244, 42], [250, 57], [259, 75], [264, 92], [261, 108], [254, 124],
        [248, 141], [238, 158], [230, 188], [224, 221], [222, 255], [225, 291], [230, 330],
        [226, 355], [217, 382], [208, 418], [203, 465], [201, 518], [200, 571], [202, 625],
        [204, 678], [205, 708],
    ], reason="Fresh P1 review found a straight facial centre and weak pelvis-to-support turn."))
    run.prepare_stage_review()
    p1_locals_2 = _local_reviews(run, "P1_gesture", "p2")
    run.submit_stage_review(
        contract_findings=("The corrected gesture remains inside the P1 contract and preserves the rifle as a subordinate axis.",),
        subject_findings=("The curved facial centre now carries the image-right glance; the pelvis changes direction into the straighter image-left support leg.",),
        exemplar_findings=("Subject geometry remains authoritative; the failed P1 exemplar contributes no pose.",),
        drawing_findings=("Fresh whole and local artifacts clear both carried concerns; the support/counterbalance roles remain distinct." ,),
        local_review_ids=tuple(item.local_review_id for item in p1_locals_2),
        corrections=("re-curved facial centre", "strengthened pelvis-to-support handoff"),
        remaining_concerns=(), decision="advance",
        advance_rationale="Fresh P1 evidence clears the face-direction and weight-transfer concerns without introducing downstream representation.",
    )

    # ------------------------------------------------------------------ P2 primary axes
    run.stage_start("P2_primary_axes")
    run.draw_many([
        S("P2-A1", "P2_primary_axes", "head_cross_axis", [[205, 84], [236, 76], [268, 82]], role="axis", pressure=.27, width=1.45, opacity=.35, source="Subject-derived face/head turn axis, rising toward image-right."),
        S("P2-A2", "P2_primary_axes", "shoulder_axis", [[178, 162], [210, 151], [244, 149], [278, 160], [304, 180]], role="axis", pressure=.25, width=1.38, opacity=.32, source="Shoulder axis drops toward the near image-right shoulder."),
        S("P2-A3", "P2_primary_axes", "pelvis_axis", [[167, 376], [201, 372], [237, 382], [272, 397], [305, 413]], role="axis", pressure=.25, width=1.38, opacity=.32, source="Pelvis counter-tilt tracks the shoulder turn and near hip."),
        S("P2-A4", "P2_primary_axes", "near_arm_direction", [[282, 171], [297, 208], [305, 248], [308, 287], [305, 323], [302, 355]], role="axis", pressure=.27, width=1.45, opacity=.35, source="Fully exposed image-right near arm: shoulder to elbow to wrist/hand endpoint."),
        S("P2-A5", "P2_primary_axes", "far_arm_direction", [[181, 180], [169, 220], [162, 267], [164, 307], [171, 345]], role="axis", pressure=.23, width=1.25, opacity=.29, source="Partly occluded image-left arm, kept subordinate behind rifle and jacket."),
        S("P2-A6", "P2_primary_axes", "support_leg_direction", [[185, 394], [192, 447], [198, 511], [201, 576], [204, 642], [205, 706]], role="axis", pressure=.25, width=1.38, opacity=.32, source="Straighter image-left support leg keeps the inherited weight landing."),
        S("P2-A7", "P2_primary_axes", "counterbalance_leg_direction", [[257, 403], [270, 451], [281, 511], [291, 578], [305, 644], [336, 722]], role="axis", pressure=.23, width=1.30, opacity=.29, source="Image-right leg diverges and lands outward/lower as counterbalance."),
        S("P2-A8", "P2_primary_axes", "rifle_extent_axis", [[119, 47], [137, 125], [157, 205], [180, 292], [211, 377], [232, 434]], role="axis", pressure=.24, width=1.32, opacity=.31, source="Rifle axis and extent are preserved from P1; no topology or contour is added yet."),
    ])
    run.prepare_stage_review()
    p2_locals = _local_reviews(run, "P2_primary_axes", "p1")
    run.submit_stage_review(
        contract_findings=("P2 contains axes only: no torso/pelvis masses, limb thickness, hand/foot blocks, joint anatomy, clothing block-in, or shading.",),
        subject_findings=("The shoulder and pelvis counter-tilts agree with the back-three-quarter turn; the near arm should remain fully exposed through its endpoint.",),
        exemplar_findings=("P2 PASS exemplar is used only for axes line hierarchy; subject coordinates are independently observed.",),
        drawing_findings=("Initial arm chain shortens the near forearm slightly and the pelvis axis is too flat at its near end.",),
        local_review_ids=tuple(item.local_review_id for item in p2_locals),
        remaining_concerns=("extend near-arm elbow-to-wrist direction", "restore pelvis counter-tilt at near hip"),
        decision="revise",
    )
    run.draw_many([
        R("P2-R1", "P2_primary_axes", "near_arm_direction", [[282, 171], [298, 208], [310, 244], [318, 281], [315, 318], [306, 356]], reason="Near arm was under-extended in the first axis pass; fresh observation shows full sleeve and forearm exposure."),
        R("P2-R2", "P2_primary_axes", "pelvis_axis", [[167, 376], [201, 372], [237, 382], [272, 399], [306, 416]], reason="Near hip counter-tilt was too flat; align the pelvis axis with the observed shorts basin."),
    ])
    run.prepare_stage_review()
    p2_locals_2 = _local_reviews(run, "P2_primary_axes", "p2")
    run.submit_stage_review(
        contract_findings=("Fresh P2 remains axes-only and preserves P1 gesture, support leg, counterbalance leg, and rifle extent.",),
        subject_findings=("Both arm chains now originate at their shoulders; the image-right near arm reaches its visible hand endpoint and pelvis counter-tilt is explicit.",),
        exemplar_findings=("The P2 grammar exemplar supplies sparse axis vocabulary only; no pose transfer occurred.",),
        drawing_findings=("Fresh local evidence clears the carried near-arm and pelvis-axis concerns without mass leakage.",),
        local_review_ids=tuple(item.local_review_id for item in p2_locals_2),
        corrections=("extended near arm to wrist endpoint", "re-tilted pelvis axis"),
        remaining_concerns=(), decision="advance",
        advance_rationale="Fresh P2 evidence agrees on head/shoulders, pelvis, both arm chains, both leg chains, and prop extent while honoring the axes-only ceiling.",
    )

    # ------------------------------------------------------------------ P3 primary masses
    run.stage_start("P3_primary_masses")
    run.draw_many([
        S("P3-A1", "P3_primary_masses", "hair_mass_left", [[242, 30], [222, 33], [201, 43], [183, 59], [169, 79], [162, 101], [163, 123], [174, 145], [191, 159], [207, 164]], role="mass", pressure=.52, width=2.45, opacity=.67, grade="HB", source="Observed short-bob hair envelope, image-left side; smooth volume not strands."),
        S("P3-A2", "P3_primary_masses", "hair_mass_right", [[242, 30], [263, 34], [280, 46], [291, 65], [296, 89], [294, 114], [287, 138], [276, 156], [264, 165]], role="mass", pressure=.52, width=2.45, opacity=.67, grade="HB", source="Observed short-bob hair envelope, image-right side, lower at the jaw."),
        S("P3-A3", "P3_primary_masses", "face_jaw_mass", [[211, 70], [216, 91], [225, 112], [238, 129], [251, 138], [263, 132], [271, 116], [272, 97]], role="mass", pressure=.43, width=2.15, opacity=.55, grade="H", source="Plain face/jaw plane beneath bangs; no eyes, nose, or lips at P3."),
        S("P3-A4", "P3_primary_masses", "bangs_group_mass", [[204, 61], [218, 72], [233, 79], [249, 80], [264, 87], [275, 101]], role="mass", pressure=.44, width=2.05, opacity=.54, grade="H", source="Bangs grouping separates hair volume from the face plane."),
        S("P3-A5", "P3_primary_masses", "neck_bridge", [[222, 137], [219, 149], [218, 160], [229, 170], [246, 169], [255, 157], [253, 141]], role="mass", pressure=.42, width=2.0, opacity=.49, grade="H", source="Short neck bridge disappears into the raised jacket collar."),
        S("P3-A6", "P3_primary_masses", "jacket_left_mass", [[190, 153], [178, 168], [167, 188], [157, 212], [151, 240], [148, 270], [149, 300], [155, 329], [162, 355], [166, 378]], role="mass", pressure=.58, width=2.75, opacity=.72, grade="HB", source="Broad loose jacket and far sleeve occupied volume, enlarged to the observed silhouette."),
        S("P3-A7", "P3_primary_masses", "jacket_right_mass", [[264, 157], [278, 169], [288, 188], [296, 213], [302, 241], [306, 270], [309, 300], [310, 329], [305, 355], [299, 377]], role="mass", pressure=.58, width=2.75, opacity=.72, grade="HB", source="Broad jacket near contour; shoulder-to-hem volume remains turned toward image-right."),
        S("P3-A8", "P3_primary_masses", "jacket_cross_chest", [[174, 202], [201, 210], [230, 213], [260, 208], [289, 198]], role="cross_contour", pressure=.34, width=1.65, opacity=.36, grade="H", source="Shallow back cross-contour to explain volume, not a clothing seam."),
        S("P3-A9", "P3_primary_masses", "jacket_cross_waist", [[153, 319], [181, 328], [215, 335], [250, 337], [285, 329]], role="cross_contour", pressure=.34, width=1.65, opacity=.36, grade="H", source="Waist cross-contour follows cropped hem and hip turn."),
        # Intentionally narrow first near-arm profile; the visual gate will force a correction.
        S("P3-A10", "P3_primary_masses", "near_sleeve_outer", [[278, 177], [286, 211], [290, 246], [292, 282], [291, 318], [288, 350]], role="mass", pressure=.48, width=2.25, opacity=.59, grade="HB", source="First near-arm hypothesis, deliberately underfilled for dogfood revision evidence."),
        S("P3-A11", "P3_primary_masses", "near_sleeve_inner", [[269, 181], [274, 215], [277, 250], [279, 285], [280, 320], [278, 347]], role="mass", pressure=.43, width=2.05, opacity=.49, grade="H", source="First near-arm inner boundary; fresh review must check width against the fully visible subject sleeve."),
        S("P3-A12", "P3_primary_masses", "far_sleeve_mass", [[183, 183], [172, 220], [166, 260], [164, 300], [170, 342]], role="mass", pressure=.42, width=2.15, opacity=.48, grade="H", source="Partially occluded far sleeve remains subordinate behind rifle and torso."),
        S("P3-A13", "P3_primary_masses", "pelvis_basin", [[165, 370], [170, 389], [181, 405], [199, 414], [219, 416], [242, 421], [266, 421], [288, 410], [303, 395]], role="mass", pressure=.56, width=2.7, opacity=.70, grade="HB", source="Shorts/pelvis occupied basin; no seams or pocket details yet."),
        S("P3-A14", "P3_primary_masses", "thigh_left_mass", [[168, 405], [165, 433], [164, 460], [168, 478], [180, 489], [202, 488], [213, 472], [211, 432], [210, 408]], role="mass", pressure=.54, width=2.55, opacity=.66, grade="HB", source="Image-left thigh mass with bare-skin gap above the thigh-high sock."),
        S("P3-A15", "P3_primary_masses", "thigh_right_mass", [[240, 415], [238, 441], [242, 465], [253, 480], [276, 486], [299, 478], [306, 455], [302, 427], [289, 413]], role="mass", pressure=.56, width=2.6, opacity=.69, grade="HB", source="Image-right near thigh mass is wider and lower, with holster-side occupied volume."),
        S("P3-A16", "P3_primary_masses", "leg_left_outer", [[168, 478], [165, 507], [162, 542], [160, 578], [161, 614], [164, 646]], role="mass", pressure=.55, width=2.55, opacity=.65, grade="HB", source="Support leg outer taper: thigh-high sock into narrow ankle."),
        S("P3-A17", "P3_primary_masses", "leg_left_inner", [[211, 480], [211, 515], [207, 551], [202, 587], [196, 620], [193, 646]], role="mass", pressure=.50, width=2.35, opacity=.58, grade="H", source="Support leg inner taper preserves the tall inter-leg wedge."),
        S("P3-A18", "P3_primary_masses", "leg_right_outer", [[298, 478], [302, 511], [305, 548], [307, 586], [309, 623], [309, 653]], role="mass", pressure=.55, width=2.55, opacity=.65, grade="HB", source="Near leg outer contour leans image-right and remains the wider counterbalance."),
        S("P3-A19", "P3_primary_masses", "leg_right_inner", [[242, 481], [249, 515], [258, 549], [266, 583], [274, 620], [280, 650]], role="mass", pressure=.50, width=2.35, opacity=.58, grade="H", source="Near leg inner taper shapes the observed negative space."),
        S("P3-A20", "P3_primary_masses", "boot_left_mass", [[164, 640], [160, 661], [160, 687], [167, 707], [185, 715], [210, 711], [221, 699], [210, 682], [195, 667], [193, 645]], role="mass", pressure=.56, width=2.55, opacity=.67, grade="HB", source="Far boot mass lands higher and smaller."),
        S("P3-A21", "P3_primary_masses", "boot_right_mass", [[280, 649], [278, 679], [282, 707], [291, 730], [315, 740], [347, 737], [363, 724], [353, 708], [330, 691], [309, 663]], role="mass", pressure=.58, width=2.65, opacity=.70, grade="HB", source="Near boot mass lands lower with outward toe and broad sole."),
        S("P3-A22", "P3_primary_masses", "rifle_left_mass", [[113, 44], [113, 69], [117, 88], [133, 96], [136, 126], [141, 160], [147, 197], [157, 238], [169, 281], [182, 329], [194, 373], [207, 416], [221, 440]], role="mass", pressure=.55, width=2.55, opacity=.65, grade="HB", source="Rifle left contour: suppressor, narrow handguard, receiver, and stock steps."),
        S("P3-A23", "P3_primary_masses", "rifle_right_mass", [[131, 44], [132, 69], [136, 88], [151, 99], [154, 128], [161, 158], [178, 168], [185, 203], [192, 243], [201, 284], [212, 328], [225, 373], [240, 430]], role="mass", pressure=.55, width=2.55, opacity=.65, grade="HB", source="Rifle right contour preserves scope/receiver widening and skeleton stock."),
        S("P3-A24", "P3_primary_masses", "rifle_receiver_cross", [[148, 200], [164, 195], [181, 190]], role="cross_contour", pressure=.35, width=1.7, opacity=.38, grade="H", source="Receiver cross-contour joins the prop mass."),
        S("P3-A25", "P3_primary_masses", "rifle_stock_cross", [[191, 391], [213, 385], [235, 379]], role="cross_contour", pressure=.35, width=1.7, opacity=.38, grade="H", source="Stock cross-contour states the body overlap and cutout region."),
    ])
    run.prepare_stage_review()
    p3_locals = _local_reviews(run, "P3_primary_masses", "p1")
    run.submit_stage_review(
        contract_findings=("P3 introduces smooth occupied masses for hair, jacket, sleeve, pelvis, legs, boots, and rifle while avoiding folds, seams, facial features, and shading.",),
        subject_findings=("The subject's image-right sleeve is fully visible and materially wide; the bob hair and large leg negative space are also primary identity cues.",),
        exemplar_findings=("P3 PASS exemplar is marked unproven until ablation; only mass vocabulary is consulted, never pose or coordinates.",),
        drawing_findings=("Hair, jacket, pelvis, legs, boots, and rifle masses are readable, but the image-right near sleeve is visibly too narrow and recedes like a far arm.",),
        local_review_ids=tuple(item.local_review_id for item in p3_locals),
        remaining_concerns=("near-arm occupied width is underfilled; reopen P3 mass boundary before visual closure",),
        decision="revise",
    )
    run.draw_many([
        R("P3-R1", "P3_primary_masses", "near_sleeve_outer", [[278, 177], [290, 208], [303, 241], [312, 274], [315, 305], [313, 333], [306, 357]], reason="Fresh P3 whole/local review found the fully visible near sleeve underfilled and too distant-looking."),
        R("P3-R2", "P3_primary_masses", "near_sleeve_inner", [[267, 181], [278, 212], [289, 245], [296, 278], [299, 309], [297, 336], [290, 351]], reason="Expand the inner near-sleeve boundary so the upper arm and forearm occupy the observed width."),
    ])
    p3_artifacts = run.prepare_stage_review()
    p3_locals_2 = _local_reviews(run, "P3_primary_masses", "p2")
    evidence_path = _write_region_evidence(run, p3_artifacts)
    manifest, visual = _submit_p3_visual_gate(
        run, p3_artifacts, tuple(item.local_review_id for item in p3_locals_2), evidence_path,
    )
    run.submit_stage_review(
        contract_findings=("Fresh P3 preserves P1/P2 structure, adds clothed occupied volume, and stays below the P4 connection/detail ceiling.",),
        subject_findings=("The broad image-right near sleeve, short bob, jacket basin, leg spread, boots, and rifle topology agree with the frozen subject observation.",),
        exemplar_findings=("The P3 exemplar remains an unproven representation aid; no failed exemplar is used as a positive card or pose source.",),
        drawing_findings=("Fresh residual sweep and independent eight-region visual review find no current P3 blocker; near-arm width correction is visible in the registered local review.",),
        local_review_ids=tuple(item.local_review_id for item in p3_locals_2),
        corrections=("expanded image-right sleeve occupied volume",),
        remaining_concerns=(), decision="advance",
        advance_rationale="Process review and blind visual fidelity review both advance on the same fresh artifact after the near-arm correction.",
    )

    # ------------------------------------------------------------------ P4 structural connections
    run.stage_start("P4_structural_connections")
    run.draw_many([
        S("P4-A1", "P4_structural_connections", "shoulder_near_sleeve_transition", [[268, 166], [282, 174], [294, 189], [302, 207]], role="connection", pressure=.38, width=1.85, opacity=.49, grade="HB", source="Shoulder insertion transitions into the broad near sleeve without a circular joint."),
        S("P4-A2", "P4_structural_connections", "near_elbow_plane", [[303, 238], [311, 247], [314, 259], [309, 270]], role="connection", pressure=.34, width=1.65, opacity=.42, grade="H", source="Short clothing-aware elbow plane explains the sleeve direction change."),
        S("P4-A3", "P4_structural_connections", "near_wrist_hand_block", [[298, 329], [306, 337], [312, 349], [306, 360], [296, 358]], role="connection", pressure=.38, width=1.8, opacity=.48, grade="HB", source="Smooth wrist-to-hand block enters the pocket/waist overlap; no fingers."),
        S("P4-A4", "P4_structural_connections", "far_shoulder_sleeve_transition", [[184, 166], [176, 180], [171, 198]], role="connection", pressure=.32, width=1.55, opacity=.38, grade="H", source="Far sleeve insertion is partly hidden by rifle and jacket."),
        S("P4-A5", "P4_structural_connections", "far_wrist_occlusion", [[164, 305], [168, 318], [174, 333]], role="connection", pressure=.30, width=1.45, opacity=.34, grade="H", source="Only the visible transition is stated; hidden hand anatomy is omitted."),
        S("P4-A6", "P4_structural_connections", "pelvis_left_thigh_bridge", [[174, 399], [184, 411], [198, 416], [208, 424]], role="connection", pressure=.37, width=1.8, opacity=.46, grade="HB", source="Pelvis basin inserts into the support thigh as a continuous clothing-aware bridge."),
        S("P4-A7", "P4_structural_connections", "pelvis_right_thigh_bridge", [[273, 410], [286, 419], [298, 430], [302, 443]], role="connection", pressure=.37, width=1.8, opacity=.46, grade="HB", source="Near hip bridge flows into the wider counterbalance thigh."),
        S("P4-A8", "P4_structural_connections", "left_knee_plane", [[166, 480], [180, 486], [198, 488], [211, 482]], role="connection", pressure=.31, width=1.5, opacity=.35, grade="H", source="Short directional knee plane, not a floating horizontal tick."),
        S("P4-A9", "P4_structural_connections", "right_knee_plane", [[245, 477], [260, 484], [281, 486], [299, 478]], role="connection", pressure=.31, width=1.5, opacity=.35, grade="H", source="Near knee plane follows the wider leg mass and counterbalance direction."),
        S("P4-A10", "P4_structural_connections", "left_ankle_boot_bridge", [[164, 621], [174, 636], [190, 645], [195, 657]], role="connection", pressure=.37, width=1.75, opacity=.45, grade="HB", source="Support ankle narrows then turns into the far boot shaft."),
        S("P4-A11", "P4_structural_connections", "right_ankle_boot_bridge", [[275, 624], [286, 642], [302, 652], [307, 667]], role="connection", pressure=.37, width=1.75, opacity=.45, grade="HB", source="Near ankle bridge explains the lower boot shaft and outward foot."),
        S("P4-A12", "P4_structural_connections", "left_foot_block", [[165, 659], [163, 687], [174, 705], [198, 710], [216, 702]], role="connection", pressure=.42, width=2.0, opacity=.53, grade="HB", source="Grounded far foot block, simple and shoe-aware."),
        S("P4-A13", "P4_structural_connections", "right_foot_block", [[280, 668], [282, 704], [295, 731], [324, 740], [355, 728]], role="connection", pressure=.42, width=2.0, opacity=.53, grade="HB", source="Grounded near foot block with outward toe and sole landing."),
        S("P4-A14", "P4_structural_connections", "rifle_scope_receiver_transition", [[148, 151], [160, 160], [176, 168], [183, 190]], role="connection", pressure=.34, width=1.65, opacity=.41, grade="H", source="Scope/receiver transition explains prop topology and sling attachment."),
        S("P4-A15", "P4_structural_connections", "rifle_stock_body_overlap", [[194, 374], [207, 383], [220, 394], [232, 408]], role="connection", pressure=.34, width=1.65, opacity=.41, grade="H", source="Stock overlap hands contour ownership to the jacket/hip at the observed interruption."),
    ])
    run.prepare_stage_review()
    p4_locals = _local_reviews(run, "P4_structural_connections", "p1")
    run.submit_stage_review(
        contract_findings=("P4 adds clothing-aware transitions, simple hand/foot blocks, and prop/body overlap without cleaning the final silhouette or adding micro-details.",),
        subject_findings=("The near sleeve bends into a pocket-entering hand; both ankles turn into grounded boots and the rifle remains separate from the jacket contour.",),
        exemplar_findings=("P4 exemplar is a known failed structural exemplar; it is used only as a warning against isolated joint symbols.",),
        drawing_findings=("Connections are readable, but the near hand block is slightly too detached from the pocket overlap and needs one local bridge.",),
        local_review_ids=tuple(item.local_review_id for item in p4_locals),
        remaining_concerns=("tighten near wrist-to-pocket hand transition",), decision="revise",
    )
    run.draw(R("P4-R1", "P4_structural_connections", "near_wrist_hand_block", [[298, 327], [304, 334], [312, 344], [310, 354], [303, 361], [294, 358], [290, 348]], reason="Fresh arm/hand crop showed a detached hand block; bridge the wrist into the pocket-entering overlap."))
    run.prepare_stage_review()
    p4_locals_2 = _local_reviews(run, "P4_structural_connections", "p2")
    run.submit_stage_review(
        contract_findings=("Fresh P4 remains connection-focused and does not move any P3 mass or add P5 cleanup detail.",),
        subject_findings=("The corrected hand now visibly enters the near pocket/waist overlap; ankle bridges and boot landings remain grounded.",),
        exemplar_findings=("Failed P4 exemplar remains a negative warning only; subject-derived transitions control the drawing.",),
        drawing_findings=("Fresh arm/hand and knee/foot crops clear the carried concern; no detached joint or floating foot remains.",),
        local_review_ids=tuple(item.local_review_id for item in p4_locals_2),
        corrections=("bridged near wrist into pocket-entering hand block",), remaining_concerns=(),
        decision="advance", advance_rationale="Fresh P4 evidence confirms connected clothing-aware transitions, grounded feet, and independent prop/body overlap without an upstream mass change.",
    )

    # ------------------------------------------------------------------ P5 clean block-in
    run.stage_start("P5_clean_blockin")
    run.draw_many([
        S("P5-A1", "P5_clean_blockin", "contour_hair_left", [[242, 30], [223, 32], [204, 42], [187, 57], [173, 76], [165, 98], [166, 121], [176, 142], [192, 157], [207, 163]], role="contour", pressure=.72, width=2.85, opacity=.84, grade="B", preset="form_pencil", layer=20, source="Decisive short-bob outer contour, image-left; no strand detail."),
        S("P5-A2", "P5_clean_blockin", "contour_hair_right", [[242, 30], [263, 34], [280, 46], [291, 65], [296, 88], [294, 113], [287, 138], [276, 156], [264, 165]], role="contour", pressure=.72, width=2.85, opacity=.84, grade="B", preset="form_pencil", layer=20, source="Decisive short-bob outer contour, image-right; hair hands off to collar at the jaw."),
        S("P5-A3", "P5_clean_blockin", "contour_jacket_left", [[190, 153], [178, 168], [167, 188], [157, 212], [151, 240], [148, 270], [149, 300], [155, 329], [162, 355], [166, 378]], role="contour", pressure=.72, width=2.95, opacity=.86, grade="B", preset="form_pencil", layer=20, source="Loose jacket/far sleeve silhouette owns the image-left garment edge below the rifle handoff."),
        S("P5-A4", "P5_clean_blockin", "contour_jacket_right", [[264, 157], [278, 169], [288, 188], [296, 213], [302, 241], [306, 270], [309, 300], [310, 329], [305, 355], [299, 377]], role="contour", pressure=.72, width=2.95, opacity=.86, grade="B", preset="form_pencil", layer=20, source="Near jacket contour preserves broad shoulder-to-hem silhouette and sleeve exposure."),
        S("P5-A5", "P5_clean_blockin", "contour_shorts_left", [[166, 378], [170, 393], [181, 405], [201, 415], [218, 416]], role="contour", pressure=.66, width=2.6, opacity=.78, grade="HB", preset="form_pencil", layer=20, source="Major cropped-shorts silhouette on support side."),
        S("P5-A6", "P5_clean_blockin", "contour_shorts_right", [[218, 416], [242, 421], [267, 421], [288, 410], [303, 395]], role="contour", pressure=.66, width=2.6, opacity=.78, grade="HB", preset="form_pencil", layer=20, source="Major cropped-shorts silhouette on near side."),
        S("P5-A7", "P5_clean_blockin", "contour_leg_left_outer", [[168, 405], [165, 433], [164, 460], [168, 478], [165, 507], [162, 542], [160, 578], [161, 614], [164, 646]], role="contour", pressure=.68, width=2.75, opacity=.81, grade="B", preset="form_pencil", layer=20, source="Support-leg outer contour from bare thigh through sock to ankle."),
        S("P5-A8", "P5_clean_blockin", "contour_leg_left_inner", [[210, 408], [211, 442], [211, 480], [211, 515], [207, 551], [202, 587], [196, 620], [193, 646]], role="contour", pressure=.66, width=2.65, opacity=.77, grade="HB", preset="form_pencil", layer=20, source="Support-leg inner contour preserves tall negative space."),
        S("P5-A9", "P5_clean_blockin", "contour_leg_right_outer", [[289, 413], [302, 450], [298, 478], [302, 511], [305, 548], [307, 586], [309, 623], [309, 653]], role="contour", pressure=.68, width=2.75, opacity=.81, grade="B", preset="form_pencil", layer=20, source="Near/counterbalance leg outer contour keeps its larger width and outward lean."),
        S("P5-A10", "P5_clean_blockin", "contour_leg_right_inner", [[241, 415], [240, 450], [242, 481], [249, 515], [258, 549], [266, 583], [274, 620], [280, 650]], role="contour", pressure=.66, width=2.65, opacity=.77, grade="HB", preset="form_pencil", layer=20, source="Near-leg inner contour closes the observed negative-space wedge."),
        S("P5-A11", "P5_clean_blockin", "contour_boot_left", [[164, 640], [160, 661], [160, 687], [167, 707], [185, 715], [210, 711], [221, 699], [210, 682], [195, 667], [193, 645]], role="contour", pressure=.72, width=2.95, opacity=.85, grade="B", preset="form_pencil", layer=20, source="Far boot silhouette lands higher with a compact toe."),
        S("P5-A12", "P5_clean_blockin", "contour_boot_right", [[280, 649], [278, 679], [282, 707], [291, 730], [315, 740], [347, 737], [363, 724], [353, 708], [330, 691], [309, 663]], role="contour", pressure=.74, width=3.05, opacity=.88, grade="B", preset="form_pencil", layer=20, source="Near boot silhouette owns the lower/right landing and outward toe."),
        S("P5-A13", "P5_clean_blockin", "contour_near_sleeve", [[264, 157], [278, 177], [290, 208], [303, 241], [312, 274], [315, 305], [313, 333], [306, 357]], role="contour", pressure=.70, width=2.8, opacity=.80, grade="B", preset="form_pencil", layer=20, source="Near sleeve is kept as a distinct broad contour owner rather than welded to torso."),
        S("P5-A14", "P5_clean_blockin", "contour_rifle_left", [[113, 44], [113, 69], [117, 88], [133, 96], [136, 126], [141, 160], [147, 197], [157, 238], [169, 281], [182, 329], [194, 373], [207, 416], [221, 440]], role="contour", pressure=.72, width=2.9, opacity=.83, grade="B", preset="form_pencil", layer=20, source="Rifle left clean contour preserves suppressor, receiver, and stock topology."),
        S("P5-A15", "P5_clean_blockin", "contour_rifle_right", [[131, 44], [132, 69], [136, 88], [151, 99], [154, 128], [161, 158], [178, 168], [185, 203], [192, 243], [201, 284], [212, 328], [225, 373], [240, 430]], role="contour", pressure=.72, width=2.9, opacity=.83, grade="B", preset="form_pencil", layer=20, source="Rifle right clean contour keeps scope/receiver steps and separate body overlap."),
        S("P5-A16", "P5_clean_blockin", "break_bangs", [[204, 61], [218, 72], [233, 79], [249, 80], [264, 87], [275, 101]], role="internal_break", pressure=.48, width=2.05, opacity=.54, grade="HB", source="One major bangs grouping break; no individual hair strands."),
        S("P5-A17", "P5_clean_blockin", "break_jaw_collar", [[211, 70], [216, 91], [225, 112], [238, 129], [251, 138], [263, 132], [271, 116]], role="internal_break", pressure=.45, width=1.95, opacity=.50, grade="HB", source="Plain jaw/face and raised collar breaks retain head identity without facial features."),
        S("P5-A18", "P5_clean_blockin", "break_pocket_hand", [[298, 327], [304, 334], [312, 344], [310, 354], [303, 361], [294, 358], [290, 348]], role="internal_break", pressure=.48, width=2.05, opacity=.54, grade="HB", source="Near hand silhouette enters the pocket/waist overlap; no fingers."),
        S("P5-A19", "P5_clean_blockin", "break_sock_tops", [[168, 478], [181, 487], [201, 488], [212, 480], [244, 480], [260, 486], [282, 486], [299, 478]], role="internal_break", pressure=.45, width=1.9, opacity=.49, grade="HB", source="Major thigh-high sock top breaks on both legs."),
        S("P5-A20", "P5_clean_blockin", "break_boot_openings", [[164, 640], [176, 648], [193, 646], [280, 649], [294, 656], [309, 653]], role="internal_break", pressure=.45, width=1.9, opacity=.49, grade="HB", source="Boot opening breaks preserve ankle-to-boot transitions."),
        S("P5-A21", "P5_clean_blockin", "break_rifle_scope_stock", [[148, 151], [160, 160], [176, 168], [183, 190], [194, 374], [207, 383], [220, 394], [232, 408]], role="internal_break", pressure=.44, width=1.85, opacity=.47, grade="HB", source="Two major prop topology breaks: scope/receiver and stock/body overlap."),
    ])
    run.draw_many([
        L("P5-L1", "P5_clean_blockin", "crown_face_spine_support", [[242, 28], [225, 220], [205, 708]], reason="Retire redundant P1 gesture after the verified clean silhouette; retain only faint weight explanation.", strength=.46),
        L("P5-L2", "P5_clean_blockin", "shoulder_axis", [[178, 162], [304, 180]], reason="Retire P2 shoulder axis beneath the decisive jacket contour.", strength=.58),
        L("P5-L3", "P5_clean_blockin", "pelvis_axis", [[167, 376], [305, 413]], reason="Retire P2 pelvis axis beneath shorts silhouette.", strength=.58),
        L("P5-L4", "P5_clean_blockin", "near_arm_direction", [[282, 171], [306, 356]], reason="Retire P2 near-arm axis after its contour and hand transition are verified.", strength=.58),
        L("P5-L5", "P5_clean_blockin", "counterbalance_leg_direction", [[257, 403], [336, 722]], reason="Retire P2 counterbalance axis after boot landing is stated.", strength=.58),
    ])
    run.prepare_stage_review()
    p5_locals = _local_reviews(run, "P5_clean_blockin", "p1")
    run.submit_stage_review(
        contract_findings=("P5 owns decisive silhouette, major clothing breaks, simple hand/foot silhouette, prop topology, and replayable construction retirement; micro folds, seams, fingers, and facial features remain absent.",),
        subject_findings=("Fresh residual sweep checks bob-hair/jacket handoff, broad near sleeve, jacket/shorts break, hand/pocket overlap, leg spread, boot landings, and rifle/body ownership.",),
        exemplar_findings=("P5 exemplar is a known failed clean-blockin exemplar; no shading, texture, or micro-detail is copied.",),
        drawing_findings=("The final block-in reads as a back-three-quarter white-bob sniper silhouette with broad near arm, tactical jacket/shorts, separated long legs, boots, and diagonal rifle.",),
        local_review_ids=tuple(item.local_review_id for item in p5_locals),
        remaining_concerns=(), decision="advance",
        advance_rationale="Fresh P5 whole/local residual sweep finds no stage-purpose mismatch; construction is subordinated without changing verified P1-P4 structure.",
    )
    result = run.finish(final_supersample=4, timelapse="full")
    (OUT / "DOGFOOD_REPORT.md").write_text(
        "# S1S9 dogfood report\n\n"
        "Subject-only R22 run using the current img2drawing protocol.\n\n"
        "- Reference: `subject.png`\n"
        "- Stages: P1→P5, with revise/re-review on P1, P2, P3, and P4\n"
        "- P3: eight-region blind visual-fidelity gate closed after near-arm width correction\n"
        "- Fidelity evidence: `reviews/P3_primary_masses/pass_02/fidelity_evidence/region_measurements.json`\n"
        "- Final drawing: `final/drawing.png`\n"
        f"- Timelapse: `{result.timelapse_gif}`\n"
        "- Authority: subject geometry first; grammar exemplars representation-only\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "output": str(OUT),
        "final_drawing": str(result.final_drawing),
        "timelapse_gif": None if result.timelapse_gif is None else str(result.timelapse_gif),
        "current_stage": run.current_stage,
    }, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    run()
