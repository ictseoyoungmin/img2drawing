"""Build the deterministic B10 intent-aware completion fixture."""

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

from img2drawing import DrawingIntent, DrawingSession


def _rejected(author) -> str:
    try:
        author()
    except (TypeError, ValueError) as exc:
        return str(exc)
    raise AssertionError("fixture expected completion to be rejected")


def run_fixture(output_dir: str | Path) -> dict:
    output = Path(output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)
    subject = output / "synthetic-subject.png"
    Image.new("RGB", (64, 64), (242, 241, 236)).save(subject)

    premature = DrawingSession.create(
        subject=subject,
        output_dir=output / "premature-session",
        session_id="vnext-b10-premature",
        intent=DrawingIntent(finish_intent="pose"),
    )
    premature_error = _rejected(
        lambda: premature.finish(
            final_inspection_id="000001",
            rationale="no inspection exists",
        )
    )

    session = DrawingSession.create(
        subject=subject,
        output_dir=output / "session",
        session_id="vnext-b10-completion",
        intent=DrawingIntent(finish_intent="pose"),
    )
    session.draw(((8, 8), (28, 30), (40, 54)), part="whole_pose/weight_path")
    session.inspect()
    first = session.finish(
        final_inspection_id="000001",
        rationale="Agent finds no material pose residual in the synthetic inspection",
        accepted_limitations=("identity detail is outside pose finish",),
    )
    first_current = session.finish_is_current

    session.draw(((42, 12), (50, 28)), part="pose/correction")
    stale_after_mutation = not session.finish_is_current
    stale_inspection_error = _rejected(
        lambda: session.finish(
            final_inspection_id="000001",
            rationale="old evidence must not be reusable",
        )
    )
    resumed_stale = not DrawingSession.resume(
        session.checkpoint_path, subject=subject
    ).finish_is_current

    session.inspect()
    second = session.finish(
        final_inspection_id="000002",
        rationale="Agent reviewed the corrected state with fresh inspection",
    )
    second_current = session.finish_is_current

    session.set_intent(
        DrawingIntent(finish_intent="subject"),
        reason="subject recognition becomes material",
    )
    stale_after_intent_change = not session.finish_is_current
    old_intent_error = _rejected(
        lambda: session.finish(
            final_inspection_id="000002",
            rationale="old intent evidence must not be reusable",
        )
    )

    trace = {
        "schema": "img2drawing.vnext.b10_completion_fixture.v1",
        "quality_claim": "mechanical-only",
        "session_id": session.session_id,
        "premature_error": premature_error,
        "first_finish": first.to_dict(),
        "first_current": first_current,
        "stale_after_mutation": stale_after_mutation,
        "stale_inspection_error": stale_inspection_error,
        "resumed_stale": resumed_stale,
        "second_finish": second.to_dict(),
        "second_current": second_current,
        "stale_after_intent_change": stale_after_intent_change,
        "old_intent_error": old_intent_error,
    }
    (output / "b10_completion_trace.json").write_text(
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
