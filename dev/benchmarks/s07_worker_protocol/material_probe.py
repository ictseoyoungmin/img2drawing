"""Public, subjectless S07 material probe; run with separately installed wheels.

The paired modes share exact authored centreline points, pressure samples and
nominal maximum widths. Graphite deposition and opaque pen widths deliberately
have different semantics. Capability panels have no graphite equivalent.
"""
from __future__ import annotations

import argparse
from dataclasses import replace
import hashlib
import json
import math
from pathlib import Path
import platform
import time

import numpy
import PIL
import img2drawing
from img2drawing import DrawingIntent, DrawingSession, ReferenceAuthority, RenderProfile


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def geometry():
    paths = []
    for column in range(2):
        for row, width in enumerate((1.2, 2.4, 5.0, 10.0)):
            points = [(24 + column * 320 + 272 * i / 40,
                       58 + row * 105 + 25 * math.sin(2 * math.pi * i / 40))
                      for i in range(41)]
            distances = [0.0]
            for a, b in zip(points, points[1:]):
                distances.append(distances[-1] + math.dist(a, b))
            positions = [d / distances[-1] for d in distances]
            pressure = [1.0 if column == 0 else .15 + .85 * math.sin(math.pi * t)
                        for t in positions]
            paths.append(dict(points=points, pressure=pressure, width=width,
                              pressure_knots=list(zip(positions, pressure)), constant=column == 0))
    return paths


def rect(x0, y0, x1, y1):
    return ((x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0))


def run(medium, output):
    output.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    profile = (replace(RenderProfile.canonical(640, 480), supersample=2)
               if medium == "graphite" else RenderProfile.mixed_media(640, 480, supersample=2))
    session = DrawingSession.create(
        canvas=(640, 480), output_dir=output / "drawing", render_profile=profile,
        intent=DrawingIntent(reference_mode="imaginative", drawing_mode="line_study",
                             finish_intent="expressive"),
        reference_authority=ReferenceAuthority.imaginative(("synthetic material comparison",)),
    )
    observation = session.observe({"authority": "explicit subjectless geometry; no reference image"})
    paths = geometry()
    if medium == "graphite":
        for index, path in enumerate(paths):
            session.draw(path["points"], stroke_id=f"path-{index}", role="contour",
                         part="material-probe", pressure=path["pressure"], tool="continuous_pencil",
                         grade="2B", tool_overrides={"width": path["width"], "opacity": 1., "grain": .15},
                         observation_id=observation, source_observation="sealed synthetic paths")
    else:
        from img2drawing.authoring import (
            InkAction, InkElement, ToneGradient, apply_ink_actions, dot_screentone,
            fineliner, g_pen, solid_ink,
        )
        actions = []

        def add(mark, name, role="contour", layer=0):
            actions.append(InkAction(f"add-{name}", "ink.add", name,
                                    InkElement(name, mark, role, "material-probe", layer),
                                    observation, "sealed synthetic paths", "material comparison"))

        if medium == "ink":
            for index, path in enumerate(paths):
                pen = (fineliner(path["points"], width=path["width"])
                       if path["constant"] else g_pen(path["points"], pressure_knots=path["pressure_knots"],
                                                       max_width=path["width"], gamma=1.))
                add(pen.resolve(), f"path-{index}")
        else:
            add(solid_ink(rect(24, 24, 300, 220), holes=(rect(64, 64, 140, 176),)), "black-reserve", "value")
            add(fineliner(((170, 165), (220, 80), (270, 160)), width=8, paint="white").resolve(),
                "white-over-black", "highlight", 1)
            for index, coverage in enumerate((.15, .35, .65)):
                add(dot_screentone(rect(330 + 95 * index, 24, 410 + 95 * index, 220),
                                  pitch=8, coverage=coverage, angle_degrees=30), f"density-{index}", "value")
            add(dot_screentone(rect(24, 260, 616, 452), holes=(rect(260, 310, 350, 400),),
                              pitch=8, gradient=ToneGradient((24, 260), (616, 260), .1, .8)),
                "gradient-reserve", "value")
            add(fineliner(((80, 415), (220, 285), (520, 410)), width=7, paint="white").resolve(),
                "white-over-tone", "highlight", 1)
        apply_ink_actions(session, actions)
    final = session.render_final(output / "final.png")
    resumed = DrawingSession.resume(session.checkpoint())
    assert resumed.render_final(output / "resumed.png").pixel_sha256 == final.pixel_sha256
    replay = resumed.export_timelapse(output / "timelapse", every_n=2, backend="auto")
    assert replay.manifest["frames"][0]["cursor"] == 0
    assert replay.manifest["frames"][-1]["cursor"] == resumed.history_cursor
    assert replay.manifest["final"]["pixel_sha256"] == final.pixel_sha256
    assert replay.manifest["gif"]["within_tolerance"]
    result = dict(schema="img2drawing.v1.4.s07.material_probe.v1", medium=medium,
                  package_version=img2drawing.__version__, python=platform.python_version(),
                  numpy=numpy.__version__, pillow=PIL.__version__,
                  geometry_sha256=digest(paths) if medium != "capabilities" else None,
                  authored_paths=paths if medium != "capabilities" else None,
                  profile=profile.to_dict(), profile_sha256=digest(profile.to_dict()),
                  actions=resumed.history_cursor, sampled_frames=len(replay.manifest["frames"]),
                  final_pixel_sha256=final.pixel_sha256, resume_exact=True,
                  gif_within_tolerance=True, elapsed_sec=time.monotonic() - started,
                  artistic_verdict="REVIEWER_ONLY", scope="synthetic; not a reference reproduction")
    (output / "metrics.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k not in ("authored_paths", "profile")}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--medium", choices=("graphite", "ink", "capabilities"), required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    run(args.medium, args.out)
