"""B07 one-sheet evidence-budget and cost-control dogfood.

The fixture uses one deliberately bad near-arm premise, reads the quick sheet,
repairs the premise, then reads one focused sheet with two Agent-selected ROIs.
It compares observable evidence work with the preserved R23 stage-review fixture;
it does not score likeness or turn telemetry into acceptance.
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
LEGACY_REVIEWS = ROOT / "dev" / "dogfood" / "croquis-sniper-girl" / "03_stage_reviews"


def _load_b05_fixture():
    spec = importlib.util.spec_from_file_location("img2drawing_b05_fixture_b07", B05_RUN)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load B05 fixture: {B05_RUN}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _legacy_counts() -> dict[str, int]:
    files = [path for path in LEGACY_REVIEWS.rglob("*") if path.is_file()]
    images = [path for path in files if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}]
    stage_dirs = [path for path in LEGACY_REVIEWS.iterdir() if path.is_dir()]
    # The preserved fixture has five stage-review ceremonies (P1 through P5);
    # P2 contains two pass folders but remains one stage ceremony.
    return {
        "generated_files": len(files),
        "visual_images": len(images),
        "review_ceremonies": len(stage_dirs),
    }


def run_fixture(output_dir: str | Path, *, clean: bool = True) -> dict:
    import sys

    if str(SRC) not in sys.path:
        sys.path.insert(0, str(SRC))
    from img2drawing import DrawingSession, author_initial_construct

    b05 = _load_b05_fixture()
    output = Path(output_dir).resolve()
    if clean and output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)

    construct = b05.build_construct()
    session = DrawingSession.create(
        subject=SUBJECT,
        output_dir=output,
        session_id="vnext-b07-evidence-budget",
        metadata={"example": "vnext-b07", "route": "observe-draw-inspect-correct-finish"},
    )
    authored = author_initial_construct(session, construct)
    marks = {mark.mark_id: mark for mark in construct.marks}
    arm = marks["arm-near-center"]
    bad_arm = ((610.0, 410.0), (612.0, 650.0), (614.0, 900.0), (616.0, 1150.0))
    bad_id = session.replace_stroke(
        arm.mark_id,
        bad_arm,
        role=arm.role,
        part=arm.part,
        confidence=arm.confidence,
        layer=arm.layer,
        reason="fixture: expose an over-vertical near-arm premise",
        observation_id=authored.observation_id,
        tool_overrides=arm.tool_overrides,
    )

    quick = session.inspect(mode="quick", supersample=2)
    quick_id = session.inspection_history[-1]["inspection_id"]
    quick_reads = [
        session.record_evidence_read(quick_id, artifact="sheet"),
        session.record_evidence_read(quick_id, artifact="contrast_overlay"),
    ]
    residual_id = session.record_residual(
        observation_id=authored.observation_id,
        observation="near arm has lost its bent foreground overlap and reads as a vertical pole",
        scope="global",
        severity="high",
        impact_rationale="the dominant arm silhouette contradicts the observed near-side depth",
        responsible_premise="near arm bent chain",
        responsible_stroke_ids=(arm.mark_id,),
        planned_edit="restore the authored bent arm premise and inspect the relation again",
        before_inspection_id=quick_id,
    )
    corrected_id = session.replace_stroke(
        bad_id,
        arm.points,
        role=arm.role,
        part=arm.part,
        confidence=arm.confidence,
        layer=arm.layer,
        reason="restore the bent foreground arm premise",
        observation_id=authored.observation_id,
        tool_overrides=arm.tool_overrides,
    )
    focused = session.inspect(
        mode="focused",
        rois=construct.rois[:2],
        escalation_reason="quick whole view leaves the arm-to-torso overlap ambiguous",
        supersample=2,
    )
    focused_id = session.inspection_history[-1]["inspection_id"]
    focused_reads = [
        session.record_evidence_read(focused_id, artifact="sheet"),
        session.record_evidence_read(focused_id, artifact="contrast_overlay"),
    ]
    correction = session.resolve_residual(
        residual_id,
        action_ids=(corrected_id,),
        after_inspection_id=focused_id,
        rationale="focused whole/arm relation inspection restores the bent overlap",
    )
    session.finish({"agent_decision": "correction accepted after quick then focused inspection"})
    resumed = DrawingSession.resume(session.checkpoint_path, subject=SUBJECT)
    telemetry = resumed.evidence_telemetry
    legacy = _legacy_counts()
    trace = {
        "schema": "img2drawing.vnext.b07_evidence_trace.v1",
        "session_id": session.session_id,
        "subject": SUBJECT.name,
        "route": "observe → draw → inspect → correct → inspect → finish",
        "inspections": {
            "quick": {"inspection_id": quick_id, "policy": quick.evidence_policy},
            "focused": {"inspection_id": focused_id, "policy": focused.evidence_policy},
        },
        "correction": {
            "residual_id": residual_id,
            "correction_id": correction.correction_id,
            "action_ids": list(correction.action_ids),
            "before_inspection_id": quick_id,
            "after_inspection_id": focused_id,
        },
        "reads": [event.to_dict() for event in (*quick_reads, *focused_reads)],
        "telemetry": telemetry.to_dict(),
        "comparison": {
            "vnext": {
                "review_turns": telemetry.review_turns,
                "visual_artifacts": telemetry.visual_artifacts,
                "generated_artifacts": telemetry.generated_artifacts,
                "image_reads": telemetry.image_reads,
                "custom_helper_scripts": 0,
            },
            "legacy_r23_fixture": {
                **legacy,
                "source": str(LEGACY_REVIEWS.relative_to(ROOT)),
                "custom_helper_scripts": "not isolated in stage-review directory",
            },
        },
        "resumed": {
            "history_cursor": resumed.history_cursor,
            "telemetry_digest": resumed.evidence_telemetry.digest(),
        },
        "visual_review": {
            "quick": f"inspections/{quick_id}/inspection_sheet.png",
            "focused": f"inspections/{focused_id}/inspection_sheet.png",
        },
    }
    (output / "b07_evidence_trace.json").write_text(
        json.dumps(trace, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8"
    )
    return trace


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path(__file__).parent / "run")
    args = parser.parse_args()
    print(json.dumps(run_fixture(args.output), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
