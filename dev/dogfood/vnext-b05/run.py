"""Canonical B05 dogfood rebuilt from the Imagen ideal-stroke reference.

The subject-space landmarks are authored once in x/y/z and projected into the
existing DrawingSession. The runtime still receives ordinary 2D strokes; it
does not infer pose, invent joints, or add a second renderer.
"""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "skills" / "img2drawing" / "src"))

from img2drawing import (  # noqa: E402
    ConstructionMark,
    DrawingSession,
    InitialConstruct,
    PoseObservation,
    ROI,
    author_initial_construct,
    inspect_initial_construct,
)


SUBJECT = ROOT / "dev" / "dogfood" / "target-subject" / "subject.png"
IDEAL_REFERENCE = ROOT / "dev" / "dogfood" / "vnext-b05" / "ideal-stroke-reference.png"
OUTPUT = ROOT / "dev" / "dogfood" / "vnext-b05" / "run-from-ideal-stroke"


# One simple orthographic projection is enough for this 2D graphite renderer.
# x is image-left/right, y is down the figure, and positive z moves a part
# toward the viewer. z changes are expressed through overlap, foreshortening,
# and oblique cross-contours rather than metadata or joint dots.
def project(point):
    x, y, z = point
    return (455.0 + 190.0 * x + 60.0 * z, 300.0 + 170.0 * y - 20.0 * z)


def chain(points):
    return tuple(project(point) for point in points)


def mark(
    mark_id: str,
    phase: str,
    role: str,
    part: str,
    points,
    *,
    confidence: float | None = None,
    width: float = 2.2,
    opacity: float = 0.72,
):
    return ConstructionMark(
        mark_id=mark_id,
        phase=phase,
        role=role,
        part=part,
        points=tuple(points),
        confidence=(0.78 if phase == "joints_limbs" else 0.9) if confidence is None else confidence,
        layer=0,
        grade="HB",
        tool_overrides={"pressure": 0.48, "width": width, "opacity": opacity},
    )


# The near arm is not a straight 2D drop. Its elbow comes forward, the
# forearm turns out toward image-right, and the hand returns toward the waist.
NEAR_ARM_CENTER = chain(
    (
        (0.30, 0.43, 0.30),  # shoulder on the near side plane
        (0.14, 1.28, 0.68),  # elbow: forward, down, and inward in x
        (0.42, 2.30, 0.42),  # wrist: forearm changes direction outward
        (0.65, 2.62, 0.25),  # hand returns toward the waist
    )
)
NEAR_ARM_OUTER = chain(
    (
        (0.48, 0.40, 0.30),
        (0.32, 1.22, 0.58),
        (0.78, 2.18, 0.30),
        (0.84, 2.55, 0.18),
    )
)
NEAR_ARM_INNER = chain(
    (
        (0.16, 0.50, 0.28),
        (-0.06, 1.20, 0.78),
        (0.04, 2.18, 0.50),
        (0.57, 2.58, 0.24),
    )
)

# The far arm stops at the elbow because the rifle/back occludes the rest. Its
# visible elbow still projects decisively toward image-left.
FAR_ARM_CENTER = chain(
    (
        (-0.73, 0.37, -0.05),  # far shoulder behind the rifle
        (-1.10, 1.26, -0.10),  # left-projecting elbow
    )
)
FAR_ARM_OUTER = chain(
    (
        (-0.78, 0.39, -0.04),
        (-1.18, 1.24, -0.08),
    )
)
FAR_ARM_INNER = chain(
    (
        (-0.62, 0.43, -0.08),
        (-1.02, 1.30, -0.12),
    )
)


def build_construct() -> InitialConstruct:
    observation = PoseObservation(
        support_side="image-left leg carries slightly more weight; image-right leg opens the stance",
        flow="head turns image-right while the back/spine leans image-left and the pelvis reverses image-right",
        head_ribcage_pelvis=(
            "turned head over an asymmetrical back-three-quarter ribcage and a counter-tilted pelvis; "
            "the image-right shoulder/arm is nearer to the viewer than the rifle-side back"
        ),
        shoulder_pelvis=(
            "shoulders recede from image-left back to the image-right side plane; the near arm folds "
            "through a real elbow angle and overlaps the torso before the pelvis opens away"
        ),
        silhouette_keys=(
            "turned bobbed head",
            "rifle rising behind the image-left shoulder",
            "large image-right bent arm over the side of the torso",
            "short rear-facing torso over two offset booted legs",
        ),
        negative_spaces=(
            "rifle-to-left-elbow wedge",
            "compressed gap beneath the near forearm at the waist",
            "dark gap between the offset legs",
        ),
        ground_relation="both boots land on one broken ground plane; image-right toe opens outward",
        major_prop_axis="rifle rises from the lower center behind the back toward image-left",
        occluded_limb_evidence=(
            "image-left far arm disappears behind the rifle after its elbow projects left",
            "image-right near forearm is a broad foreground mass over the right/front torso",
            "far leg remains visible below the shorts despite dark overlap",
        ),
        uncertain=("the far forearm and hand are fully hidden behind the rifle and jacket",),
    )

    return InitialConstruct(
        observation=observation,
        marks=(
            # 1. Gesture: follow the back/spine, not a frontal center pole. The
            # rifle has its own axis because it controls far-arm occlusion.
            mark("loa-back-flow", "line_of_action", "gesture", "back_flow", chain(
                ((0.10, -0.20, 0.05), (-0.05, 0.35, -0.02), (-0.20, 0.95, -0.08),
                 (-0.12, 1.55, -0.04), (-0.16, 2.30, -0.08)),
            )),
            mark("loa-rifle", "line_of_action", "gesture", "major_prop_axis", (
                (286, 150), (304, 280), (334, 430), (367, 590), (408, 790),
            )),

            # 2. Mass blocking: turned head, asymmetric back/side ribcage, and
            # a pelvis that does not face the viewer squarely.
            mark("head-cranium-left", "mass_blocking", "mass", "head_cranium", (
                (440, 80), (395, 98), (355, 140), (330, 190), (338, 238), (370, 276),
            )),
            mark("head-cranium-right", "mass_blocking", "mass", "head_cranium", (
                (440, 80), (492, 75), (540, 98), (582, 135), (603, 180), (596, 226), (575, 270),
            )),
            mark("head-jaw-turn", "mass_blocking", "mass", "head_jaw", (
                (370, 276), (410, 306), (458, 325), (510, 315), (550, 285),
            )),
            mark("head-turn-axis", "mass_blocking", "construction", "head_turn_axis", chain(
                ((0.18, -1.08, 0.12), (0.34, -0.72, 0.26), (0.42, -0.38, 0.22)),
            )),
            mark("ribcage-back-left", "mass_blocking", "mass", "back_ribcage", chain(
                ((-0.65, 0.35, -0.10), (-0.80, 0.82, -0.12), (-0.78, 1.32, -0.08),
                 (-0.55, 1.78, -0.08), (-0.25, 2.02, -0.05)),
            )),
            mark("ribcage-near-side", "mass_blocking", "mass", "near_ribcage_side", chain(
                ((0.45, 0.35, 0.25), (0.65, 0.78, 0.40), (0.65, 1.20, 0.35),
                 (0.45, 1.70, 0.30), (0.20, 2.00, 0.20)),
            )),
            mark("ribcage-depth-upper", "mass_blocking", "construction", "back_depth_contour", chain(
                ((-0.60, 0.70, -0.10), (-0.20, 0.64, 0.00), (0.20, 0.80, 0.20), (0.48, 1.00, 0.30)),
            )),
            mark("ribcage-depth-lower", "mass_blocking", "construction", "back_depth_contour", chain(
                ((-0.65, 1.32, -0.08), (-0.25, 1.38, 0.00), (0.15, 1.54, 0.20), (0.42, 1.66, 0.30)),
            )),
            mark("pelvis-back-left", "mass_blocking", "mass", "pelvis_back", chain(
                ((-0.55, 2.20, -0.10), (-0.42, 2.55, -0.08), (-0.28, 2.95, -0.05)),
            )),
            mark("pelvis-near-right", "mass_blocking", "mass", "pelvis_near_side", chain(
                ((0.20, 2.18, 0.20), (0.55, 2.52, 0.28), (0.48, 2.92, 0.18)),
            )),
            mark("pelvis-depth-contour", "mass_blocking", "construction", "pelvis_depth_contour", chain(
                ((-0.45, 2.52, -0.06), (-0.08, 2.48, 0.04), (0.28, 2.62, 0.20), (0.50, 2.66, 0.24)),
            )),

            # 3. No permanent plumb stroke. Offset leg origins and the broken
            # ground relation carry balance without a distracting vertical.

            # 4. Limbs: no joint circles. The bend is carried by spatial chains
            # and tapered boundaries; the far arm terminates at the visible elbow.
            mark("arm-far-center", "joints_limbs", "structure", "far_arm_occluded_chain", FAR_ARM_CENTER),
            mark("arm-far-outer", "joints_limbs", "mass", "far_arm_occluded_outer", FAR_ARM_OUTER),
            mark("arm-far-inner", "joints_limbs", "mass", "far_elbow_inner_boundary", FAR_ARM_INNER),
            mark("arm-near-center", "joints_limbs", "structure", "near_arm_bent_chain", NEAR_ARM_CENTER),
            mark("arm-near-outer", "joints_limbs", "mass", "near_arm_outer_boundary", NEAR_ARM_OUTER, width=3.0, opacity=0.86),
            mark("arm-near-inner", "joints_limbs", "mass", "near_arm_inner_boundary", NEAR_ARM_INNER, width=3.0, opacity=0.86),
            mark("arm-near-cross-upper", "joints_limbs", "construction", "near_arm_depth_contour", (
                (530, 555), (590, 565), (638, 555),
            ), width=2.3, opacity=0.76),
            mark("arm-near-cross-lower", "joints_limbs", "construction", "near_arm_depth_contour", (
                (515, 650), (585, 662), (645, 650),
            ), width=2.3, opacity=0.76),
            mark("leg-left-chain", "joints_limbs", "structure", "support_leg_chain", chain(
                ((-0.35, 2.82, -0.08), (-0.50, 3.85, -0.05), (-0.48, 5.25, -0.02), (-0.42, 6.72, 0.00)),
            )),
            mark("leg-right-chain", "joints_limbs", "structure", "counterbalance_leg_chain", chain(
                ((0.25, 2.82, 0.10), (0.45, 3.88, 0.20), (0.56, 5.25, 0.18), (0.76, 6.72, 0.20)),
            )),
            mark("leg-left-outer", "joints_limbs", "mass", "support_leg_outer", chain(
                ((-0.52, 2.85, -0.08), (-0.72, 3.85, -0.05), (-0.70, 5.25, -0.02), (-0.62, 6.72, 0.00)),
            )),
            mark("leg-right-outer", "joints_limbs", "mass", "counterbalance_leg_outer", chain(
                ((0.42, 2.85, 0.12), (0.72, 3.88, 0.20), (0.86, 5.25, 0.18), (1.02, 6.72, 0.20)),
            )),
            mark("leg-left-inner", "joints_limbs", "mass", "support_leg_inner", chain(
                ((-0.18, 2.85, -0.04), (-0.32, 3.85, -0.02), (-0.28, 5.25, 0.00), (-0.24, 6.72, 0.00)),
            )),
            mark("leg-right-inner", "joints_limbs", "mass", "counterbalance_leg_inner", chain(
                ((0.05, 2.85, 0.06), (0.20, 3.88, 0.12), (0.30, 5.25, 0.10), (0.48, 6.72, 0.16)),
            )),
            mark("foot-left", "joints_limbs", "mass", "support_foot", (
                (374, 1325), (360, 1370), (370, 1415), (410, 1430), (449, 1418),
            )),
            mark("foot-right", "joints_limbs", "mass", "counterbalance_foot", (
                (590, 1324), (580, 1370), (600, 1415), (652, 1435), (708, 1422),
            )),

            # Prop/body relationship: the rifle is a depth anchor, not a front-facing accessory.
            mark("rifle-body", "joints_limbs", "mass", "prop_body_extent", (
                (278, 152), (294, 260), (315, 365), (341, 490), (370, 620),
                (402, 760), (433, 872),
            )),
            mark("rifle-contact", "joints_limbs", "structure", "prop_body_contact", (
                (335, 420), (366, 455), (394, 520), (420, 600), (445, 690),
            )),
            mark("rifle-receiver-mass", "joints_limbs", "mass", "prop_receiver", (
                (304, 318), (338, 300), (365, 330), (370, 382), (345, 420), (312, 404), (304, 318),
            )),
            mark("rifle-stock-mass", "joints_limbs", "mass", "prop_stock", (
                (344, 600), (365, 630), (390, 690), (418, 758), (440, 810),
            )),
        ),
        # The ideal reference has no permanent plumb line or node markers.
        plumb=None,
        ground=None,
        rois=(
            ROI("head-ribcage", (285, 55, 700, 650), scale=1.8),
            ROI("pelvis-legs", (285, 630, 760, 1470), scale=1.25),
            ROI("prop-and-left-elbow", (225, 100, 470, 900), scale=1.8),
        ),
    )


def main() -> None:
    if not SUBJECT.is_file():
        raise FileNotFoundError(SUBJECT)
    if not IDEAL_REFERENCE.is_file():
        raise FileNotFoundError(IDEAL_REFERENCE)
    if OUTPUT.exists():
        raise FileExistsError(f"refusing to overwrite existing dogfood output: {OUTPUT}")
    construct = build_construct()
    session = DrawingSession.create(subject=SUBJECT, output_dir=OUTPUT, session_id="vnext-b05-ideal-stroke")
    result = author_initial_construct(session, construct)
    sheet = inspect_initial_construct(session, construct, supersample=2)
    print(f"observation_id={result.observation_id}")
    print(f"marks={len(result.action_ids)}")
    print(f"drawing={sheet.drawing}")
    print(f"inspection={OUTPUT / 'inspections' / '000001' / 'inspection_sheet.png'}")


if __name__ == "__main__":
    main()
