"""Build deterministic B16 authored-element navigation and correction evidence."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "skills" / "img2drawing" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from img2drawing import DrawingSession  # noqa: E402


def run_fixture(output_dir: str | Path) -> dict:
    output = Path(output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)
    subject = output / "synthetic-subject.png"
    Image.new("RGB", (96, 72), (243, 241, 237)).save(subject)
    session = DrawingSession.create(
        subject=subject,
        output_dir=output / "run",
        session_id="b16-edit-navigation",
    )
    observation_id = session.observe(
        {
            "near_arm": "shoulder-to-elbow contour must retain observed thickness",
            "coat": "one connected middle-dark value family",
        },
        observation_id="body-read",
    )
    session.draw(
        ((10, 12), (31, 24), (52, 44)),
        stroke_id="near-arm-v1",
        action_id="draw-near-arm-v1",
        part="near_arm",
        role="contour",
        observation_id=observation_id,
    )
    session.draw(
        ((50, 10), (68, 28), (78, 52)),
        stroke_id="torso-edge",
        action_id="draw-torso-edge",
        part="torso",
        role="contour",
        observation_id=observation_id,
    )
    session.fill_region(
        ((20, 17), (72, 17), (72, 61), (20, 61)),
        value=160,
        fill_id="coat-value",
        action_id="fill-coat",
        part="coat",
        observation_id=observation_id,
    )
    session.inspect()
    residual_id = session.record_residual(
        observation_id=observation_id,
        observation="near arm reads too narrow through the elbow turn",
        scope="near_arm",
        severity="high",
        impact_rationale="the half-turned body loses shoulder and arm weight",
        responsible_premise="initial near-arm envelope",
        responsible_stroke_ids=("near-arm-v1",),
        planned_edit="replace the current arm contour with observed thickness",
        before_inspection_id=session.inspection_history[-1]["inspection_id"],
    )
    located_before = session.authored_elements(
        element_type="stroke", part="near_arm", observation_id=observation_id
    )
    arm_action = session.replace_stroke(
        "near-arm-v1",
        ((10, 12), (34, 22), (57, 44)),
        stroke_id="near-arm-v2",
        action_id="replace-near-arm-v2",
        part="near_arm",
        role="contour",
        reason="restore observed shoulder, upper-arm, and elbow thickness",
        observation_id=observation_id,
    )
    fill_action = session.replace_fill_region(
        "coat-value",
        value=120,
        action_id="revise-coat-value",
        reason="connect the darker coat family without stacking another fill",
        observation_id=observation_id,
    )
    session.inspect()
    correction = session.resolve_residual(
        residual_id,
        action_ids=(arm_action,),
        after_inspection_id=session.inspection_history[-1]["inspection_id"],
        rationale="fresh evidence carries the thicker arm contour through the elbow",
    )

    before_stale_cursor = session.history_cursor
    stale_error = None
    try:
        session.soft_lift("near-arm-v1", reason="this identity is superseded")
    except ValueError as exc:
        stale_error = str(exc)
    summary = session.authoring_summary(limit=2)
    resolved = session.resolve_authored_element("near-arm-v1", element_type="stroke")
    all_elements = session.authored_elements(status=None)
    render = session.render_final(output / "run" / "final.png")
    resumed = DrawingSession.resume(session.checkpoint_path, subject=subject)
    checkpoint = json.loads(session.checkpoint_path.read_text(encoding="utf-8"))
    trace = {
        "schema": "img2drawing.vnext.b16_fixture.v1",
        "quality_claim": "mechanical-only",
        "located_before": [element.to_dict() for element in located_before],
        "all_elements": [element.to_dict() for element in all_elements],
        "resolved_old_arm_id": None if resolved is None else resolved.element_id,
        "current_arm_id": session.current_stroke("near-arm-v1").stroke_id,
        "current_fill_id": session.current_fill_region("coat-value").fill_id,
        "fill_action_id": fill_action,
        "correction_action_ids": list(correction.action_ids),
        "stale_edit_error": stale_error,
        "stale_edit_preserved_cursor": session.history_cursor == before_stale_cursor,
        "summary": summary.to_dict(),
        "generated_contacts_excluded": len(session.current_ir().strokes) > summary.current_strokes,
        "checkpoint_has_no_derived_index": all(
            key not in checkpoint for key in ("authoring_summary", "authored_elements")
        ),
        "resume_state_match": resumed.drawing_state_hash() == session.drawing_state_hash(),
        "resume_summary_match": resumed.authoring_summary(limit=2).to_dict() == summary.to_dict(),
        "final_png": render.path.name,
    }
    (output / "b16_trace.json").write_text(
        json.dumps(trace, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8"
    )
    return trace


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(run_fixture(args.output), indent=2, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
