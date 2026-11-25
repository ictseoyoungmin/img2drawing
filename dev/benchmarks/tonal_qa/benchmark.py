#!/usr/bin/env python3
"""Opt-in synthetic QA, not independent portrait/dogfood evidence.

All final marks are ordinary DrawingSession actions. No source pixels are
converted to geometry. The fixture is deliberately analytic and non-artistic.
"""
from __future__ import annotations

import argparse
import importlib
import json
import math
import os
import platform
import resource
import subprocess
import sys
import threading
import time
from pathlib import Path

import numpy as np
from PIL import Image

from img2drawing import DrawingIntent, DrawingSession, RenderProfile
from img2drawing.authoring import TonalAreaPlan, reshape_stroke, resolve_mark_for_intent


def save_report(path, report):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True, allow_nan=False), flush=True)


def gray(path):
    with Image.open(path) as image:
        return np.asarray(image.convert("L"), dtype=np.int16)


def new_session(root, size, name):
    root.mkdir(parents=True, exist_ok=True)
    reference = root / "reference.png"
    Image.new("RGB", (size, size), "white").save(reference)
    return DrawingSession.create(subject=reference, output_dir=root / "session",
                                 session_id=name, intent=DrawingIntent(drawing_mode="croquis"))


def swatch(root):
    """Compare two authored control fixtures using actual v11 deposition."""
    rows = []
    for name, width, opacity, pressure in (
        ("reserved", 8.0, 0.48, 0.42),
        ("overdraw", 32.0, 0.9, 0.85),
    ):
        folder = root / name
        session = new_session(folder, 256, name)
        blank = folder / "blank.png"
        session.render_final(blank)
        area = TonalAreaPlan(
            area_id="analytic-band", part="swatch",
            reference_evidence="synthetic test specification; not a portrait",
            boundary=((48, 32), (208, 32), (208, 224), (48, 224)),
            direction_degrees=90, target_density=0.5, target_value=0.5,
            pressure_range=(0.2, 0.6),
            highlight_reserves=(((48, 112), (208, 112), (208, 144), (48, 144)),),
        )
        mark = resolve_mark_for_intent(session.intent, "value", tool_preset="broad-graphite")
        specs = []
        # Shared centerlines isolate the effect of width, pressure and opacity.
        # Centerlines are fixed test inputs, not extracted from reference pixels.
        for x in range(56, 201, 8):
            for points in (
                [(x, 42), (x + 3, 68), (x - 2, 103)],
                [(x - 2, 153), (x + 3, 186), (x, 214)],
            ):
                specs.append(dict(points=points, part="swatch",
                    tool_overrides={"width": width, "opacity": opacity, "pressure": pressure},
                    **mark.draw_kwargs(metadata=area.stroke_metadata(stroke_family="vertical"))))
        ids = session.draw_many(specs)
        for sid in ids:
            actual = session.current_stroke(sid).tool_state
            assert math.isclose(actual["hardness"], 0.48) and math.isclose(actual["grain"], 0.58)
            assert actual["pencil_grade"] == "4B"
            recorded = actual["provenance"]["metadata"]["markmaking"]
            assert recorded["resolved_tool_state"]["width"] == actual["width"]
        final = folder / "final.png"
        session.render_final(final)
        darkness = np.maximum(gray(blank) - gray(final), 0) / 255.0
        inside = np.zeros(darkness.shape, dtype=bool)
        inside[32:224, 48:208] = True
        highlight = np.zeros_like(inside)
        highlight[112:144, 48:208] = True
        dark_target = inside & ~highlight
        mass = float(darkness.sum())
        rows.append({
            "name": name, "width": width, "pressure": pressure, "opacity": opacity,
            "action_count": session.history_cursor,
            "target_mean_darkness": float(darkness[dark_target].mean()),
            "target_coverage_delta_gt_8": float((darkness[dark_target] > 8/255).mean()),
            "highlight_mean_darkness": float(darkness[highlight].mean()),
            "highlight_coverage_delta_gt_8": float((darkness[highlight] > 8/255).mean()),
            "outside_darkness_mass_fraction": float(darkness[~inside].sum() / mass) if mass else 0.0,
            "target_saturated_delta_gt_0_65": float((darkness[dark_target] > 0.65).mean()),
        })
    safe, bad = rows
    report = {"scope": "synthetic shared-centerline swatch; not independent visual proof",
              "metrics": rows,
              "checks": {"target_has_marks": safe["target_mean_darkness"] > 0,
                         "highlight_loss_detected": bad["highlight_mean_darkness"] > safe["highlight_mean_darkness"],
                         "boundary_leakage_detected": bad["outside_darkness_mass_fraction"] > safe["outside_darkness_mass_fraction"]}}
    save_report(root / "swatch.json", report)
    if not all(report["checks"].values()):
        raise RuntimeError("controlled swatch did not separate the intended failure")


def build_stress(root, size, actions):
    """Build a deterministic long history, including actual corrective actions."""
    session = new_session(root, size, "synthetic-stress")
    observation = session.observe({"scope": "synthetic stress; not artwork", "geometry": "short curves on a grid"})
    count = actions - 4
    columns = math.ceil(math.sqrt(count))
    cell = size / (columns + 2)
    specs = []
    for i in range(count):
        x = (1 + i % columns) * cell
        y = (1 + i // columns) * cell
        specs.append(dict(points=[(x, y), (x + cell*.20, y - cell*.14),
                                  (x + cell*.48, y + cell*.10), (x + cell*.7, y)],
                          role="contour", part="synthetic-grid", tool="continuous_pencil",
                          observation_id=observation, tool_overrides={"width": max(1.0, size/512)}))
    ids = session.draw_many(specs)
    sid = ids[0]
    p = specs[0]["points"]
    session.replace_segment(sid, 1, 2, [p[1], (p[1][0]+1, p[1][1]+1), p[2]],
                            observation_id=observation, reason="synthetic local geometry correction")
    session.soft_lift(sid, strength=0.5, observation_id=observation, reason="synthetic partial attenuation")
    previous = session.current_stroke(sid)
    reshape_stroke(session, sid, [(float(x)+1, float(y)+1) for x,y in previous.points],
                   observation_id=observation, reason="synthetic reshape after attenuation")
    session.delete_stroke(ids[1], observation_id=observation, reason="synthetic removal")
    assert session.history_cursor == actions
    checkpoint = session.checkpoint()
    before = session.drawing_state_hash()
    resumed = DrawingSession.resume(checkpoint, subject=session.subject)
    assert resumed.drawing_state_hash() == before
    assert resumed.history_cursor == actions
    return checkpoint, session.subject, before


def rss_kib(pid):
    try:
        for line in (Path("/proc") / str(pid) / "status").read_text().splitlines():
            if line.startswith("VmRSS:"):
                return int(line.split()[1])
    except (FileNotFoundError, ProcessLookupError, PermissionError):
        pass
    return 0


def descendants(pid):
    pending, seen = [pid], set()
    while pending:
        p = pending.pop()
        if p in seen:
            continue
        seen.add(p)
        try:
            childfile = Path("/proc") / str(p) / "task" / str(p) / "children"
            pending.extend(int(x) for x in childfile.read_text().split())
        except (FileNotFoundError, ProcessLookupError, PermissionError):
            pass
    return seen


def run_replay(root, size, actions, every_n, force_retry):
    checkpoint, subject, state = build_stress(root, size, actions)
    # Use a new interpreter for each export so the peak is not inherited
    # from the history construction or a prior export.
    cmd = [sys.executable, str(Path(__file__).resolve()), "_export",
           "--out", str(root), "--checkpoint", str(checkpoint.resolve()),
           "--subject", str(subject.resolve()), "--every-n", str(every_n)]
    if force_retry:
        cmd.append("--force-retry")
    start = time.perf_counter()
    proc = subprocess.Popen(cmd)
    peak = 0
    while proc.poll() is None:
        peak = max(peak, sum(rss_kib(pid) for pid in descendants(proc.pid)))
        time.sleep(0.05)
    elapsed = time.perf_counter() - start
    report_path = root / "replay.json"
    report = json.loads(report_path.read_text()) if report_path.exists() else {}
    report.update({"canvas_size": size, "requested_actions": actions, "every_n": every_n,
                   "force_retry": force_retry, "export_subprocess_exit": proc.returncode,
                   "sampled_process_tree_peak_rss_kib": peak, "rss_sample_interval_seconds": 0.05,
                   "export_subprocess_elapsed_seconds": elapsed,
                   "expected_state_hash": state, "platform": platform.platform(),
                   "python": sys.version.split()[0]})
    save_report(report_path, report)
    if proc.returncode != 0 or report.get("state_hash") != state:
        raise RuntimeError("replay failed or checkpoint changed")


def export_child(root, checkpoint, subject, every_n, force_retry):
    session = DrawingSession.resume(checkpoint, subject=subject)
    initial_state = session.drawing_state_hash()
    # This is framework QA only: inject one failure after the real fast encode
    # to exercise the exact existing retry path without changing tolerances.
    module = importlib.import_module("img2drawing.timelapse.export")
    if force_retry:
        original = module._check_gif
        calls = 0
        def inject_once(*args, **kwargs):
            nonlocal calls
            calls += 1
            if calls == 1:
                raise module.GifFidelityError("intentional QA fault: exercise local palettes")
            return original(*args, **kwargs)
        module._check_gif = inject_once
    events = {}
    def progress(event):
        phase = event["phase"]
        events[phase] = dict(event)
        if event["completed"] == event["total"]:
            print("phase:", phase, event["completed"], flush=True)
    profile = session.render_profile
    # Budget explicitly allows the chosen experiment, with no fidelity relaxation.
    frames = math.ceil(session.history_cursor / every_n) + 1
    pixel_work = frames * profile.canvas_width * profile.canvas_height * profile.supersample**2 * profile.output_scale**2
    started = time.perf_counter()
    result = session.export_timelapse(root / "export", backend="fast", every_n=every_n,
                                      max_pixel_work=pixel_work, max_gif_bytes=250_000_000,
                                      progress=progress)
    elapsed = time.perf_counter() - started
    m = result.manifest
    assert m["sampling"]["action_zero_included"] and m["sampling"]["latest_included"]
    assert m["frames"][0]["cursor"] == 0 and m["frames"][-1]["cursor"] == session.history_cursor
    assert m["final"]["last_frame_pixel_match"] and m["gif"]["within_tolerance"]
    assert session.drawing_state_hash() == initial_state
    if force_retry:
        assert m["gif"]["encoding_fallback"] == "local-frame-palettes"
    report = {
        "scope": "synthetic long-history benchmark; not visual portrait QA",
        "state_hash": initial_state, "history": m["history"], "sampling": m["sampling"],
        "frame_count": len(m["frames"]), "profile": m["render_profile"],
        "profile_digest": m["render_profile_digest"], "final": m["final"], "gif": m["gif"],
        "timing": m["timing"], "budget": m["budget"], "progress": events,
        "export_seconds": elapsed,
        "python_peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "largest_child_peak_rss_kib": resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
    }
    save_report(root / "replay.json", report)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("mode", choices=("swatch", "replay", "_export"))
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--size", type=int, default=2048)
    p.add_argument("--actions", type=int, default=511)
    p.add_argument("--every-n", type=int, default=4)
    p.add_argument("--force-retry", action="store_true")
    p.add_argument("--checkpoint", type=Path)
    p.add_argument("--subject", type=Path)
    args = p.parse_args()
    if args.size < 64 or args.actions < 6 or args.every_n < 1:
        p.error("size >= 64, actions >= 6, every-n >= 1 required")
    if args.mode == "swatch":
        swatch(args.out)
    elif args.mode == "replay":
        run_replay(args.out, args.size, args.actions, args.every_n, args.force_retry)
    else:
        export_child(args.out, args.checkpoint, args.subject, args.every_n, args.force_retry)


if __name__ == "__main__":
    main()
