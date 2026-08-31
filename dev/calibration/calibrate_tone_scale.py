"""Regenerate the cached tone scale by probing the canonical renderer.

Calibration is renderer capability, not the provenance of any one drawing. It runs
here, once, and is cached in ``img2drawing/data/tone_scale.json`` so an agent never
has to discover deposition behaviour inside a drawing session again.

    python dev/calibration/calibrate_tone_scale.py --write
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "skills" / "img2drawing" / "src"))

import numpy as np  # noqa: E402
from PIL import Image  # noqa: E402

from img2drawing.core.ir import Stroke, StrokeIR  # noqa: E402
from img2drawing.core.tools import get_tool  # noqa: E402
from img2drawing.render.pillow_pencil_contact import render  # noqa: E402

PATCH = 220
INSET = 45
TARGET_VALUES = (235, 215, 195, 170, 145, 120, 95, 70, 50, 35)
CANDIDATE_GRADES = ("2H", "HB", "B", "2B", "4B", "6B", "8B")


def measure(grade: str, opacity: float, pressure: float, width: float, spacing: float,
            out: Path) -> float:
    ir = StrokeIR(width=PATCH, height=PATCH)
    y = 6.0
    while y < PATCH - 6:
        ts = replace(get_tool("form_pencil"), opacity=opacity, pressure=pressure, width=width)
        state = ts.to_dict()
        state["pencil_grade"] = grade
        ir.add(Stroke(points=[(6.0, y), (PATCH - 6.0, y)], width=width, opacity=opacity,
                      tool_state=state, role="value"))
        y += spacing
    render(ir, out, supersample=2)
    a = np.asarray(Image.open(out).convert("L")).astype(float)
    return float(a[INSET:PATCH - INSET, INSET:PATCH - INSET].mean())


def sweep(tmp: Path) -> list[dict]:
    rows = []
    for grade in CANDIDATE_GRADES:
        for opacity, pressure in ((0.30, 0.42), (0.45, 0.55), (0.60, 0.68), (0.72, 0.78),
                                  (0.85, 0.88), (0.94, 0.94), (1.0, 0.97)):
            for spacing, width in ((9.0, 3.0), (6.5, 3.6), (5.0, 4.4), (4.0, 5.5), (3.0, 6.5)):
                v = measure(grade, opacity, pressure, width, spacing, tmp)
                rows.append({"grade": grade, "opacity": opacity, "pressure": pressure,
                             "width": width, "spacing": spacing, "value": round(v, 1)})
                print(f"  {grade:3s} op{opacity:<5} pr{pressure:<5} w{width:<4} sp{spacing:<4} -> {v:6.1f}")
    return rows


def build(rows: list[dict]) -> dict:
    steps = []
    for target in TARGET_VALUES:
        # prefer the lightest touch that reaches the target: fewer, softer strokes
        best = min(rows, key=lambda r: (abs(r["value"] - target), -r["spacing"], r["opacity"]))
        steps.append({
            "value": target,
            "measured": best["value"],
            "grade": best["grade"],
            "opacity": best["opacity"],
            "pressure": best["pressure"],
            "width": best["width"],
            "spacing": best["spacing"],
        })
    return {
        "schema": "img2drawing.tone_scale/v1",
        "renderer": "pillow_pencil_contact",
        "tool": "form_pencil",
        "note": "mean rendered value of a flat single-direction hatch patch; "
                "regenerate with dev/calibration/calibrate_tone_scale.py",
        "steps": steps,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--tmp", type=Path, default=Path("/tmp/tone_probe.png"))
    args = ap.parse_args()
    rows = sweep(args.tmp)
    table = build(rows)
    print(json.dumps(table["steps"], indent=2))
    if args.write:
        dest = ROOT / "skills" / "img2drawing" / "src" / "img2drawing" / "data" / "tone_scale.json"
        dest.write_text(json.dumps(table, indent=2) + "\n", encoding="utf-8")
        print("wrote", dest)


if __name__ == "__main__":
    main()
