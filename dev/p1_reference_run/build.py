"""Build the P1 reference run: the canonical example carried through the skill's
own closeout so the folder holds session/checkpoint/final/timelapse, not just
the review artifacts.

    python3 dev/p1_reference_run/build.py
"""
from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / "skills" / "img2drawing"
sys.path.insert(0, str(SKILL / "src"))
sys.path.insert(0, str(SKILL / "examples" / "full_body_croquis"))
sys.path.insert(0, str(ROOT / "temp" / "dev"))

from img2drawing import DrawingRun                      # noqa: E402
from run import run_example                             # noqa: E402

OUT = Path(__file__).resolve().parent


def _relativize_public_paths(tree: Path, *, checkout_root: Path) -> None:
    """Remove checkout-specific absolute paths from committed text evidence.

    Each replacement is relative to the file containing it, so copied evidence
    remains meaningful without publishing a contributor's machine layout.
    """
    checkout = str(checkout_root.resolve())
    for path in tree.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".json", ".md"}:
            continue
        text = path.read_text(encoding="utf-8")
        if checkout not in text:
            continue
        relative_root = os.path.relpath(checkout_root, path.parent)
        path.write_text(text.replace(checkout, relative_root), encoding="utf-8")


def _overlay(subject: Image.Image, drawing: Image.Image, *, paper=.62) -> Image.Image:
    """Lay raw graphite over a translucent-paper subject without contrast gain."""
    sub = subject.convert("RGB").resize(drawing.size, Image.Resampling.LANCZOS)
    white = Image.new("RGB", drawing.size, (255, 255, 255))
    base = Image.blend(sub, white, paper)
    return ImageChops.multiply(base, drawing.convert("L").convert("RGB"))


def _sheet(tiles, out: Path, *, height=900, pad=16, label_height=30) -> Path:
    def fit(im):
        return im.resize(
            (max(1, int(im.width * height / im.height)), height),
            Image.Resampling.LANCZOS,
        )

    fitted = [(label, fit(image)) for label, image in tiles]
    width = sum(image.width for _, image in fitted) + pad * (len(fitted) + 1)
    canvas = Image.new("RGB", (width, height + label_height + pad), (248, 247, 244))
    draw = ImageDraw.Draw(canvas)
    x = pad
    for label, image in fitted:
        draw.text((x, 9), label, fill=(30, 30, 30))
        canvas.paste(image, (x, label_height))
        x += image.width + pad
    canvas.save(out)
    return out


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
        sub = Image.open(SKILL / "examples/full_body_croquis/subject.png")
        R = work / "reviews/P1_gesture"
        p1 = Image.open(R / "pass_01/current_drawing.png")
        p2 = Image.open(R / "pass_02/current_drawing.png")
        _sheet([("SUBJECT", sub), ("PASS 1 raw", p1), ("PASS 2 raw", p2),
                ("PASS 2 over subject", _overlay(sub, p2))],
               OUT / "compare.png")
        _overlay(sub, p2).save(OUT / "overlay.png")
    except Exception as exc:                             # pragma: no cover
        print("comparison sheets skipped:", exc)

    # the individual timelapse frames are regenerable from the checkpoint
    shutil.rmtree(work / "timelapse" / "frames", ignore_errors=True)

    _relativize_public_paths(OUT, checkout_root=ROOT)

    print(json.dumps({
        "final_drawing": str(result.final_drawing.relative_to(ROOT)),
        "timelapse": "",
        "session": str((work / "session" / "session.json").relative_to(ROOT)),
        "checkpoint": str((work / "session" / "checkpoint.json").relative_to(ROOT)),
    }, indent=1))


if __name__ == "__main__":
    main()
