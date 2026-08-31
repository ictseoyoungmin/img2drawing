"""B06 residual-driven correction fixture on the accepted B05 subject.

The fixture deliberately seeds a visibly over-vertical near-arm premise so the
before/after inspection pair demonstrates an Agent-selected global repair.  It
then smooths one cross-contour segment as a local repair.  Both edits use the
normal history and inspection paths; no stage/reopen runtime is involved.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "skills" / "img2drawing" / "src"
B05_RUN = ROOT / "dev" / "dogfood" / "vnext-b05" / "run.py"
SUBJECT = ROOT / "dev" / "dogfood" / "target-subject" / "subject.png"


def _load_b05_fixture():
    spec = importlib.util.spec_from_file_location("img2drawing_b05_fixture", B05_RUN)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load B05 fixture: {B05_RUN}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_fixture(output_dir: str | Path, *, clean: bool = True) -> dict:
    import sys

    if str(SRC) not in sys.path:
        sys.path.insert(0, str(SRC))
    from img2drawing import DrawingSession, author_initial_construct, inspect_initial_construct

    b05 = _load_b05_fixture()
    output = Path(output_dir).resolve()
    if clean and output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)

    construct = b05.build_construct()
    session = DrawingSession.create(
        subject=SUBJECT,
        output_dir=output,
        session_id="vnext-b06-residual-correction",
        metadata={"example": "vnext-b06", "route": "observe-draw-inspect-correct-finish"},
    )
    authored = author_initial_construct(session, construct)
    inspect_initial_construct(session, construct, supersample=2)
    initial = session.inspection_history[-1]

    marks = {mark.mark_id: mark for mark in construct.marks}
    global_mark = marks["arm-near-center"]
    local_mark = marks["arm-near-cross-upper"]

    # Seed an obvious residual without changing the subject or introducing a
    # second renderer.  The next inspection is the current state judged by the
    # Agent, and the correction below restores the authored B05 premise.
    bad_arm = ((610.0, 410.0), (612.0, 650.0), (614.0, 900.0), (616.0, 1150.0))
    seeded_id = session.replace_stroke(
        global_mark.mark_id,
        bad_arm,
        role=global_mark.role,
        part=global_mark.part,
        confidence=global_mark.confidence,
        layer=global_mark.layer,
        reason="fixture: expose an over-vertical near-arm premise for review",
        observation_id=authored.observation_id,
        tool_overrides={"pressure": 0.48, "width": 2.2, "opacity": 0.72},
    )
    session.inspect(rois=construct.rois, supersample=2)
    bad = session.inspection_history[-1]
    residual_id = session.record_residual(
        observation_id=authored.observation_id,
        observation="near arm has lost its bent foreground overlap and reads as a vertical pole",
        scope="global",
        severity="high",
        impact_rationale="the dominant arm silhouette contradicts the observed near-side depth",
        responsible_premise="near arm bent chain",
        responsible_stroke_ids=(global_mark.mark_id,),
        planned_edit="restore the authored bent arm premise, then inspect whole figure and ROI",
        before_inspection_id=bad["inspection_id"],
    )
    restored_id = session.replace_stroke(
        seeded_id,
        global_mark.points,
        role=global_mark.role,
        part=global_mark.part,
        confidence=global_mark.confidence,
        layer=global_mark.layer,
        reason="restore the bent foreground arm premise from the residual",
        observation_id=authored.observation_id,
        tool_overrides={"pressure": 0.48, "width": 2.2, "opacity": 0.72},
    )
    session.inspect(rois=construct.rois, supersample=2)
    global_after = session.inspection_history[-1]
    global_correction = session.resolve_residual(
        residual_id,
        action_ids=(restored_id,),
        after_inspection_id=global_after["inspection_id"],
        rationale="fresh whole and near-arm ROI inspection restores the bent overlap",
    )

    local_residual_id = session.record_residual(
        observation_id=authored.observation_id,
        observation="upper near-arm cross-contour is slightly kinked at its middle",
        scope="local",
        severity="medium",
        impact_rationale="smoothing this small relation keeps the foreground mass readable",
        responsible_premise=None,
        responsible_stroke_ids=(local_mark.mark_id,),
        planned_edit="replace only the middle cross-contour segment",
        before_inspection_id=global_after["inspection_id"],
    )
    local_before = session.inspection_history[-1]
    local_action = session.replace_segment(
        local_mark.mark_id,
        1,
        3,
        (local_mark.points[1], (550.0, 522.0), local_mark.points[2]),
        reason="smooth the near-arm cross-contour locally",
        observation_id=authored.observation_id,
    )
    session.inspect(rois=construct.rois, supersample=2)
    local_after = session.inspection_history[-1]
    local_correction = session.resolve_residual(
        local_residual_id,
        action_ids=(local_action,),
        after_inspection_id=local_after["inspection_id"],
        rationale="the local contour is smoother while its boundary endpoints remain fixed",
    )
    session.finish({"agent_decision": "corrections accepted after whole and ROI inspection"})
    resumed = DrawingSession.resume(session.checkpoint_path, subject=SUBJECT)

    trace = {
        "schema": "img2drawing.vnext.b06_correction_trace.v1",
        "session_id": session.session_id,
        "subject": SUBJECT.name,
        "observation_id": authored.observation_id,
        "initial_inspection_id": initial["inspection_id"],
        "seeded_action_id": seeded_id,
        "global": {
            "residual_id": residual_id,
            "before_inspection_id": bad["inspection_id"],
            "after_inspection_id": global_after["inspection_id"],
            "correction_id": global_correction.correction_id,
            "action_ids": list(global_correction.action_ids),
            "before_drawing_state_hash": bad["drawing_state_hash"],
            "after_drawing_state_hash": global_after["drawing_state_hash"],
        },
        "local": {
            "residual_id": local_residual_id,
            "before_inspection_id": local_before["inspection_id"],
            "after_inspection_id": local_after["inspection_id"],
            "correction_id": local_correction.correction_id,
            "action_ids": list(local_correction.action_ids),
        },
        "inspection_ids": [item["inspection_id"] for item in session.inspection_history],
        "resumed": {
            "history_cursor": resumed.history_cursor,
            "residual_statuses": [record.status for record in resumed.residual_history],
            "correction_ids": [record.correction_id for record in resumed.correction_history],
        },
        "route": "observe → draw → inspect → choose residual → edit → inspect → keep → finish",
        "visual_review": {
            "initial": "inspections/000001/inspection_sheet.png",
            "seeded_residual": "inspections/000002/inspection_sheet.png",
            "global_before": "inspections/000002/inspection_sheet.png",
            "global_after": "inspections/000003/inspection_sheet.png",
            "local_before": "inspections/000003/inspection_sheet.png",
            "local_after": "inspections/000004/inspection_sheet.png",
        },
    }
    (output / "b06_correction_trace.json").write_text(
        json.dumps(trace, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return trace


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path(__file__).parent / "run")
    args = parser.parse_args()
    trace = run_fixture(args.output)
    print(json.dumps(trace, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
