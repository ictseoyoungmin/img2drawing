"""Opt-in fixed-path opacity diagnostic; not a visual-quality or release verdict."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image
from img2drawing import DrawingSession, DrawingIntent, RenderProfile
from img2drawing.authoring import resolve_mark_for_intent, sample_catmull_rom


def run(out: Path, experimental: bool):
    out.mkdir(parents=True, exist_ok=False)
    ref = out / "reference.png"
    Image.new("RGB", (200, 100), "white").save(ref)
    profile = RenderProfile.from_dict({**RenderProfile.canonical(200, 100).to_dict(), "supersample": 3})
    expected = "11-experimental-opacity" if experimental else "11"
    if profile.renderer_version != expected:
        raise ValueError(f"Expected renderer {expected}, got {profile.renderer_version}")
    intent = DrawingIntent(drawing_mode="croquis", finish_intent="subject", style_profile="graphite_academic")
    rows = []
    for label, width, half in [("broad", 38, 5), ("thin", 3, 1)]:
        session = DrawingSession.create(subject=ref, output_dir=out / label, intent=intent, render_profile=profile)
        oid = session.observe({"scope": "analytic fixed-path opacity diagnostic", "width": width})
        points = sample_catmull_rom([(20, 50), (80, 50), (125, 50), (180, 50)], spacing=2)
        mark = resolve_mark_for_intent(intent, "value", tool_preset="broad-graphite",
                                       modifiers={"width": width, "opacity": .8, "pressure": .65})
        kw = mark.draw_kwargs()
        kw["pressure"] = [.65] * len(points)
        sid = session.draw(points, part="diagnostic", observation_id=oid, **kw)
        blank = session.render_at(0, out / f"{label}_blank.png")
        with Image.open(blank.path) as image:
            paper = np.asarray(image.convert("L"), dtype=float) / 255
        prev = .8
        for opacity in [.8, .4, .2, .096, .025, .005, 0.0]:
            if opacity != prev:
                session.soft_lift(sid, strength=1-opacity/prev, observation_id=oid,
                                  reason="fixed-path controlled opacity attenuation")
            stroke = session.current_stroke(sid)
            assert abs(stroke.opacity - opacity) < 1e-12
            assert stroke.points == points and np.allclose(stroke.pressure, .65)
            rendered = session.render_final(out / f"{label}_{opacity:.3f}.png")
            with Image.open(rendered.path) as image:
                dark = np.maximum(paper - np.asarray(image.convert("L"), dtype=float)/255, 0)
            rows.append({"stroke": label, "width": width, "opacity": stroke.opacity,
                         "mean_center_darkness": float(dark[50-half:50+half, 60:140].mean()),
                         "full_darkness_mass": float(dark.sum()), "path_pressure_equal": True})
            prev = opacity
    report = {"renderer": profile.renderer_version, "contract_digest": profile.renderer_contract_digest,
              "scope": "fixed-path controlled opacity; not independent visual evidence", "rows": rows}
    (out / "opacity_response.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if experimental:
        for label in ("broad", "thin"):
            values = [r["mean_center_darkness"] for r in rows if r["stroke"] == label]
            assert all(a >= b for a, b in zip(values, values[1:])), values
            assert values[-1] == 0
            assert next(r for r in rows if r["stroke"] == label and r["opacity"] == 0)["full_darkness_mass"] == 0
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--experimental", action="store_true")
    args = parser.parse_args()
    print(json.dumps(run(args.out, args.experimental), indent=2))
