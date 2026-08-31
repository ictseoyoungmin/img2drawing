"""B08 dogfood: two orthogonal intent selections on one shared session core.

The same B05 construction is authored once.  A later intent change records
provenance at the existing action cursor; it does not create a second session,
rewrite geometry, or select a different renderer.
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
    spec = importlib.util.spec_from_file_location("img2drawing_b05_fixture_b08", B05_RUN)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load B05 fixture: {B05_RUN}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_fixture(output_dir: str | Path, *, clean: bool = True) -> dict:
    import sys

    if str(SRC) not in sys.path:
        sys.path.insert(0, str(SRC))
    from img2drawing import (
        DrawingIntent,
        DrawingSession,
        IntentProvenance,
        author_initial_construct,
        resolve_mode_guide,
        resolve_style_guide,
    )

    b05 = _load_b05_fixture()
    output = Path(output_dir).resolve()
    if clean and output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)

    construct = b05.build_construct()
    first_intent = DrawingIntent(
        reference_mode="observed",
        drawing_mode="croquis",
        finish_intent="pose",
        style_profile="pencil_loose",
        provenance=IntentProvenance(source="B08 dogfood", reason="read the subject as observed gesture"),
    )
    session = DrawingSession.create(
        subject=SUBJECT,
        output_dir=output,
        session_id="vnext-b08-intent-scaffold",
        metadata={"example": "vnext-b08", "route": "observe-draw-inspect-correct-finish"},
        intent=first_intent,
    )
    authored = author_initial_construct(session, construct)
    before_hash = session.drawing_state_hash()
    before_cursor = session.history_cursor
    sheet = b05.inspect_initial_construct(session, construct, supersample=2)
    inspection_id = session.inspection_history[-1]["inspection_id"]

    second_intent = DrawingIntent(
        reference_mode="hybrid",
        drawing_mode="figure_drawing",
        finish_intent="subject",
        style_profile="graphite_academic",
        provenance=IntentProvenance(source="B08 dogfood", reason="inspection shifts emphasis to landmarks"),
    )
    change = session.set_intent(second_intent, reason="inspection shifts emphasis to landmarks")
    assert session.drawing_state_hash() == before_hash
    assert session.history_cursor == before_cursor
    resumed = DrawingSession.resume(session.checkpoint_path, subject=SUBJECT)
    session.finish({"agent_decision": "intent guidance changed without geometry rewrite"})
    trace = {
        "schema": "img2drawing.vnext.b08_intent_trace.v1",
        "session_id": session.session_id,
        "subject": SUBJECT.name,
        "route": "observe → draw → inspect → correct → finish",
        "selection": {
            "initial": first_intent.to_dict(),
            "changed": second_intent.to_dict(),
            "provenance_event": change.to_dict(),
        },
        "guides": {
            "croquis": resolve_mode_guide("croquis").to_dict(),
            "figure_drawing": resolve_mode_guide("figure_drawing").to_dict(),
            "pencil_loose": resolve_style_guide("pencil_loose").to_dict(),
            "graphite_academic": resolve_style_guide("graphite_academic").to_dict(),
        },
        "inspection": {
            "inspection_id": inspection_id,
            "drawing_state_hash": sheet.drawing_state_hash,
            "policy": sheet.evidence_policy,
        },
        "geometry_invariant": {
            "before_hash": before_hash,
            "after_hash": session.drawing_state_hash(),
            "before_cursor": before_cursor,
            "after_cursor": session.history_cursor,
            "unchanged": session.drawing_state_hash() == before_hash and session.history_cursor == before_cursor,
        },
        "resumed": {
            "intent": resumed.intent.to_dict() if resumed.intent else None,
            "intent_event_count": len(resumed.intent_history),
            "history_cursor": resumed.history_cursor,
        },
    }
    (output / "b08_intent_trace.json").write_text(
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
