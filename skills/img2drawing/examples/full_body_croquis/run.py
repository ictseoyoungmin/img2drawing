"""Stage-free full-body construction example.

The bundled subject is the only geometry reference.  The example writes one
agent-authored observation, one atomic initial construction, and one inspection
sheet through the public vNext API.  It intentionally has no Pn/stage runtime.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / "skills" / "img2drawing" / "src"))

from img2drawing import (  # noqa: E402
    ConstructionMark,
    DrawingSession,
    GroundGuide,
    InitialConstruct,
    PlumbLine,
    PoseObservation,
    ROI,
    author_initial_construct,
    inspect_initial_construct,
)


HERE = Path(__file__).resolve().parent
SUBJECT = HERE / "subject.png"


def _mark(
    mark_id: str,
    phase: str,
    role: str,
    part: str,
    points: tuple[tuple[float, float], ...],
    *,
    width: float = 2.3,
    opacity: float = 0.62,
    grade: str = "HB",
) -> ConstructionMark:
    """Build one subject-space mark from this fixture's observed subject."""

    return ConstructionMark(
        mark_id=mark_id,
        phase=phase,
        role=role,
        part=part,
        points=points,
        confidence=0.86 if role == "structure" else 0.92,
        grade=grade,
        tool_overrides={"pressure": 0.48, "width": width, "opacity": opacity},
    )


def build_construct() -> InitialConstruct:
    """Return a whole-pose hypothesis authored from the bundled subject only."""

    observation = PoseObservation(
        support_side="image-left leg carries weight; image-right leg opens the stance",
        flow="head-left → torso-right → pelvis-left reversal",
        head_ribcage_pelvis=(
            "head turns over a three-quarter ribcage above a counter-tilted pelvis"
        ),
        shoulder_pelvis="shoulders slope against the pelvis tilt",
        silhouette_keys=("turned head", "offset shoulders", "split boot stance"),
        negative_spaces=("arm-to-torso opening", "space between legs"),
        ground_relation="both feet land on the same ground plane",
        major_prop_axis=None,
        occluded_limb_evidence=(
            "image-right wrist is partly hidden by the pocket and sleeve",
        ),
        uncertain=("exact elbow and knee contours are hidden by clothing",),
    )

    marks = (
        _mark(
            "loa",
            "line_of_action",
            "gesture",
            "body_flow",
            ((370, 110), (364, 230), (377, 370), (390, 530), (375, 700), (365, 900)),
            width=2.6,
            opacity=0.72,
            grade="B",
        ),
        _mark(
            "head",
            "mass_blocking",
            "mass",
            "head_turn",
            ((340, 95), (375, 78), (415, 90), (442, 125), (447, 170), (430, 215), (392, 238), (352, 220), (330, 180), (340, 95)),
        ),
        _mark(
            "ribcage",
            "mass_blocking",
            "mass",
            "ribcage_turn",
            ((300, 250), (365, 230), (435, 250), (470, 380), (440, 530), (355, 545), (305, 430), (300, 250)),
        ),
        _mark(
            "pelvis",
            "mass_blocking",
            "mass",
            "pelvis_tilt",
            ((305, 525), (355, 510), (430, 525), (465, 600), (420, 655), (345, 640), (300, 585), (305, 525)),
        ),
        _mark(
            "shoulder_flow",
            "balance_plumb",
            "structure",
            "shoulder_line",
            ((295, 270), (350, 255), (410, 260), (465, 285)),
        ),
        _mark(
            "support_leg",
            "joints_limbs",
            "structure",
            "support_leg_chain",
            ((350, 610), (345, 720), (350, 845), (355, 1010)),
        ),
        _mark(
            "counter_leg",
            "joints_limbs",
            "structure",
            "counterbalance_leg_chain",
            ((420, 620), (450, 730), (475, 850), (505, 1035)),
        ),
        _mark(
            "near_arm",
            "joints_limbs",
            "structure",
            "near_arm_occluded_chain",
            ((460, 285), (500, 390), (515, 500), (490, 600)),
        ),
        _mark(
            "far_arm",
            "joints_limbs",
            "structure",
            "far_arm_occluded_chain",
            ((300, 285), (260, 390), (245, 500)),
        ),
        _mark(
            "support_foot",
            "joints_limbs",
            "mass",
            "support_foot_direction",
            ((355, 1010), (330, 1035), (295, 1042), (335, 1052), (370, 1038), (355, 1010)),
            width=2.1,
            opacity=0.58,
        ),
        _mark(
            "counter_foot",
            "joints_limbs",
            "mass",
            "counterbalance_foot_direction",
            ((505, 1035), (530, 1055), (565, 1065), (548, 1080), (505, 1070), (505, 1035)),
            width=2.1,
            opacity=0.58,
        ),
    )

    return InitialConstruct(
        observation=observation,
        marks=marks,
        plumb=PlumbLine(anchor=(365.0, 0.0)),
        ground=GroundGuide(y=1068.0, x_range=(270.0, 590.0)),
        rois=(
            ROI("head-torso", (285.0, 60.0, 480.0, 560.0)),
            ROI("pelvis-legs", (285.0, 500.0, 585.0, 1090.0)),
        ),
    )


def run_example(output_dir: str | Path, *, clean: bool = True) -> dict:
    """Run the canonical stage-free fixture and return a portable trace."""

    output = Path(output_dir).resolve()
    if clean and output.exists():
        for child in output.iterdir():
            if child.is_dir():
                import shutil

                shutil.rmtree(child)
            else:
                child.unlink()
    output.mkdir(parents=True, exist_ok=True)

    session = DrawingSession.create(
        subject=SUBJECT,
        output_dir=output,
        session_id="canonical-full-body-construction-vnext",
        metadata={"example": "full_body_croquis", "route": "stage-free"},
    )
    construct = build_construct()
    result = author_initial_construct(session, construct)
    sheet = inspect_initial_construct(session, construct)
    trace = {
        "schema": "img2drawing.stage_free_example_trace.v1",
        "example": "full_body_croquis",
        "session_id": session.session_id,
        "observation_id": result.observation_id,
        "action_ids": list(result.action_ids),
        "drawing_state_hash": sheet.drawing_state_hash,
        "checkpoint": session.checkpoint_path.name,
        "inspection_ids": [item["inspection_id"] for item in session.inspection_history],
        "route": "observe → construct → inspect → correct → repeat → finish",
    }
    (output / "stage_free_trace.json").write_text(
        json.dumps(trace, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return trace


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("img2drawing_example_output"),
        help="Output directory for the stage-free fixture.",
    )
    parser.add_argument("--no-clean", action="store_true")
    args = parser.parse_args()
    print(json.dumps(run_example(args.output, clean=not args.no_clean), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
