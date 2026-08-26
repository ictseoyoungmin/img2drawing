"""Build the P1 reference run: the canonical example carried through the skill's
own closeout so the folder holds session/checkpoint/final/timelapse, not just
the review artifacts.

    python3 dev/p1_reference_run/build.py
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / "skills" / "img2drawing"
sys.path.insert(0, str(SKILL / "src"))
sys.path.insert(0, str(SKILL / "examples" / "full_body_croquis"))
sys.path.insert(0, str(ROOT / "temp" / "dev"))

from img2drawing import DrawingRun                      # noqa: E402
from run import run_example                             # noqa: E402

OUT = Path(__file__).resolve().parent


def main() -> None:
    work = OUT / "run"
    trace = run_example(work, clean=True)

    run = DrawingRun.resume(work)
    result = run.finish(allow_incomplete=True, timelapse="full",
                        timelapse_mode="action")
    (OUT / "canonical_trace.json").write_text(
        json.dumps(trace, indent=2, ensure_ascii=False), encoding="utf-8")

    # comparison sheets, raw + translucent-paper overlay
    try:
        from compare import overlay, sheet
        from PIL import Image
        sub = Image.open(SKILL / "examples/full_body_croquis/subject.png")
        R = work / "reviews/P1_gesture"
        p1 = Image.open(R / "pass_01/current_drawing.png")
        p2 = Image.open(R / "pass_02/current_drawing.png")
        sheet([("SUBJECT", sub), ("PASS 1 raw", p1), ("PASS 2 raw", p2),
               ("PASS 2 over subject", overlay(sub, p2))],
              OUT / "compare.png")
        overlay(sub, p2).save(OUT / "overlay.png")
    except Exception as exc:                             # pragma: no cover
        print("comparison sheets skipped:", exc)

    # the individual timelapse frames are regenerable from the checkpoint
    shutil.rmtree(work / "timelapse" / "frames", ignore_errors=True)

    print(json.dumps({
        "final_drawing": str(result.final_drawing),
        "timelapse": str(getattr(result, "timelapse", "") or ""),
        "session": str(work / "session" / "session.json"),
        "checkpoint": str(work / "session" / "checkpoint.json"),
    }, indent=1))


if __name__ == "__main__":
    main()
