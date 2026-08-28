"""Build the P3 reference run and its compact comparison boards."""
from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
SKILL = ROOT / "skills" / "img2drawing"

import sys
sys.path.insert(0, str(SKILL / "src"))
sys.path.insert(0, str(OUT))

from img2drawing import DrawingRun  # noqa: E402
from run import run_example  # noqa: E402
from reopen import reopen_example  # noqa: E402


def _relativize_public_paths(tree: Path, *, checkout_root: Path) -> None:
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
    subject = subject.convert("RGB").resize(drawing.size, Image.Resampling.LANCZOS)
    white = Image.new("RGB", drawing.size, (255, 255, 255))
    base = Image.blend(subject, white, paper)
    return ImageChops.multiply(base, drawing.convert("L").convert("RGB"))


def _sheet(tiles, out: Path, *, height=900, pad=16, label_height=30) -> Path:
    def fit(image):
        return image.resize(
            (max(1, int(image.width * height / image.height)), height),
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
    run_example(work, clean=True)
    trace = reopen_example(work)
    run = DrawingRun.resume(work)
    result = run.finish(
        allow_incomplete=True,
        # Timelapse is optional evidence; keep the public reference build
        # bounded while preserving the final drawing/session/review artifacts.
        timelapse="none",
        timelapse_mode="stage",
    )
    (OUT / "canonical_trace.json").write_text(
        json.dumps(trace, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    subject = Image.open(SKILL / "examples/full_body_croquis/subject.png")
    p1 = Image.open(work / "reviews/P1_gesture/pass_02/current_drawing.png")
    p2 = Image.open(work / "reviews/P2_primary_axes/pass_02/current_drawing.png")
    p3_1 = Image.open(work / "reviews/P3_primary_masses/pass_01/current_drawing.png")
    p3_3 = Image.open(work / "reviews/P3_primary_masses/pass_03/current_drawing.png")
    p3_6 = Image.open(work / "reviews/P3_primary_masses/pass_06/current_drawing.png")
    final_overlay = _overlay(subject, p3_6)
    _sheet(
        [
            ("SUBJECT", subject),
            ("P1 final", p1),
            ("P2 final", p2),
            ("P3 pass 1", p3_1),
            ("P3 pass 3", p3_3),
            ("P3 pass 6", p3_6),
            ("P3 final over subject", final_overlay),
        ],
        OUT / "compare.png",
    )
    final_overlay.save(OUT / "overlay.png")

    shutil.rmtree(work / "timelapse" / "frames", ignore_errors=True)
    _relativize_public_paths(OUT, checkout_root=ROOT)

    print(json.dumps({
        "final_drawing": str(result.final_drawing.relative_to(ROOT)),
        "session": str((work / "session" / "session.json").relative_to(ROOT)),
        "checkpoint": str((work / "session" / "checkpoint.json").relative_to(ROOT)),
        "current_stage": trace["current_stage"],
    }, indent=1))


if __name__ == "__main__":
    main()
