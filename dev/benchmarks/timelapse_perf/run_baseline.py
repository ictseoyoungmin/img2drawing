from __future__ import annotations

import argparse
import dataclasses
import hashlib
import json
import os
import resource
import shutil
import sys
import time
from pathlib import Path

from PIL import Image

# This benchmark is intentionally kept outside package runtime. It instruments the
# current canonical renderer without changing persisted history or renderer output.
REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from img2drawing.vnext.session import DrawingSession
from img2drawing.vnext.intent import DrawingIntent
from img2drawing.vnext.reference_authority import ReferenceAuthority
from img2drawing.vnext.render_profile import RenderProfile
import img2drawing.vnext.output as output

from make_fixture import build_fixture


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def pixel_sha256(path: Path) -> str:
    with Image.open(path) as im:
        return hashlib.sha256(im.convert("RGBA").tobytes()).hexdigest()


def make_session(fixture: dict, out: Path, supersample: int) -> DrawingSession:
    width, height = int(fixture["width"]), int(fixture["height"])
    profile = dataclasses.replace(
        RenderProfile.canonical(width, height),
        profile_id=f"timelapse-baseline-ss{supersample}",
        supersample=int(supersample),
    )
    intent = DrawingIntent(
        reference_mode="imaginative",
        drawing_mode="free_draw",
        finish_intent="expressive",
        style_profile="pencil_loose",
    )
    authority = ReferenceAuthority.imaginative(["timelapse performance fixture"])
    session = DrawingSession.create(
        canvas=(width, height),
        output_dir=out / "session",
        session_id=f"timelapse-baseline-ss{supersample}",
        intent=intent,
        reference_authority=authority,
        render_profile=profile,
    )
    tool_map = {
        "construction": "construction_pencil",
        "hatch": "construction_pencil",
        "form": "form_pencil",
        "continuous": "continuous_pencil",
        "accent": "accent_pencil",
    }
    for idx, spec in enumerate(fixture["strokes"]):
        points = [p[:2] for p in spec["points"]]
        pressure = [p[2] for p in spec["points"]]
        session.draw(
            points,
            pressure=pressure,
            tool=tool_map[spec["kind"]],
            role=spec["kind"],
            part=spec["label"],
            layer=idx,
        )
    session.checkpoint()
    return session


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fixture", type=Path, default=None, help="Optional frozen fixture JSON; defaults to deterministic make_fixture.build_fixture()")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--supersample", type=int, default=4)
    ap.add_argument("--every-n", type=int, default=4)
    ap.add_argument("--repeat", type=int, default=2)
    args = ap.parse_args()

    fixture = json.loads(args.fixture.read_text(encoding="utf-8")) if args.fixture is not None else build_fixture()
    shutil.rmtree(args.out, ignore_errors=True)
    args.out.mkdir(parents=True, exist_ok=True)

    repeat_rows = []
    for repeat_idx in range(args.repeat):
        run_out = args.out / f"run_{repeat_idx+1:02d}"
        run_out.mkdir(parents=True, exist_ok=True)
        session = make_session(fixture, run_out, args.supersample)

        render_at_times = []
        gif_times = []

        orig_render_at = output._render_at
        orig_save_gif = output.save_gif

        def timed_render_at(*a, **kw):
            t0 = time.perf_counter()
            try:
                return orig_render_at(*a, **kw)
            finally:
                render_at_times.append(time.perf_counter() - t0)

        def timed_save_gif(*a, **kw):
            t0 = time.perf_counter()
            try:
                return orig_save_gif(*a, **kw)
            finally:
                gif_times.append(time.perf_counter() - t0)

        output._render_at = timed_render_at
        output.save_gif = timed_save_gif
        try:
            t0 = time.perf_counter()
            final_artifact = session.render_final(run_out / "final.png")
            final_render_s = time.perf_counter() - t0

            render_at_times.clear(); gif_times.clear()
            t0 = time.perf_counter()
            export = output.export_session_timelapse(
                session,
                run_out / "timelapse",
                mode="every_n",
                every_n=args.every_n,
                max_pixel_work=10**12,
                max_gif_bytes=250_000_000,
            )
            timelapse_s = time.perf_counter() - t0
        finally:
            output._render_at = orig_render_at
            output.save_gif = orig_save_gif

        # S01 instrumentation is derived from the authoritative states that the
        # canonical renderer actually iterates. The renderer performs exactly one
        # stroke material pass for every active stroke in each _render_at call.
        # Include the independent canonical-final render performed by the exporter.
        from img2drawing.provenance.timelapse import select_cursors
        cursors = select_cursors(session._agent, "every_n", every_n=args.every_n)
        exposure_counts = {}
        for cursor in cursors + [session.history_cursor]:
            ir = session._agent.history.state_at(cursor)
            for stroke in ir.strokes:
                sid = str(stroke.stroke_id or "<no-id>")
                exposure_counts[sid] = exposure_counts.get(sid, 0) + 1
        unique_deposited = len(exposure_counts)
        total_deposits = sum(exposure_counts.values())
        duplicated_deposits = total_deposits - unique_deposited
        top = [
            {"stroke_id": sid, "count": count}
            for sid, count in sorted(exposure_counts.items(), key=lambda kv: (-kv[1], kv[0]))[:12]
        ]
        frame_paths = sorted((run_out / "timelapse" / "frames").glob("*.png"))
        frame_json = sorted((run_out / "timelapse" / "frames").glob("*.render.json"))
        row = {
            "repeat": repeat_idx + 1,
            "resolution": [fixture["width"], fixture["height"]],
            "supersample": args.supersample,
            "actions": session.history_cursor,
            "every_n": args.every_n,
            "sampled_frames": len(frame_paths),
            "render_artifact_calls": len(render_at_times),
            "render_artifact_sum_s": sum(render_at_times),
            "render_artifact_mean_s": sum(render_at_times) / max(1, len(render_at_times)),
            "gif_encode_s": sum(gif_times),
            "final_render_s": final_render_s,
            "timelapse_total_s": timelapse_s,
            "maxrss_kb": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            "unique_strokes_deposited": unique_deposited,
            "total_stroke_depositions": total_deposits,
            "duplicate_stroke_depositions": duplicated_deposits,
            "deposition_duplication_factor": total_deposits / max(1, unique_deposited),
            "per_frame_json_count": len(frame_json),
            "per_frame_json_bytes": sum(p.stat().st_size for p in frame_json),
            "frame_png_bytes": sum(p.stat().st_size for p in frame_paths),
            "gif_bytes": export.gif_path.stat().st_size,
            "pixel_work_manifest": export.manifest["budget"]["pixel_work"],
            "final_png_sha256": file_sha256(final_artifact.path),
            "final_pixel_sha256": pixel_sha256(final_artifact.path),
            "replay_final_pixel_sha256": export.manifest["final"]["pixel_sha256"],
            "final_pixel_parity": pixel_sha256(final_artifact.path) == export.manifest["final"]["pixel_sha256"],
            "top_repeated_strokes": top,
        }
        (run_out / "metrics.json").write_text(json.dumps(row, indent=2), encoding="utf-8")
        repeat_rows.append(row)

    times = [r["timelapse_total_s"] for r in repeat_rows]
    final_times = [r["final_render_s"] for r in repeat_rows]
    summary = {
        "schema": "img2drawing.timelapse_perf_baseline.v1",
        "status": "CLOSED_ON_REPRESENTATIVE_FIXTURE",
        "note": "Real Lucy archive/checkpoint can be supplied via the same harness when mounted; this slice freezes a same-pixel-count representative workload without altering runtime behavior.",
        "fixture": {
            "path": str(args.fixture) if args.fixture is not None else "generated:make_fixture.build_fixture",
            "resolution": [fixture["width"], fixture["height"]],
            "stroke_count": len(fixture["strokes"]),
        },
        "config": {
            "supersample": args.supersample,
            "every_n": args.every_n,
            "repeat": args.repeat,
        },
        "timelapse_total_s": {
            "values": times,
            "mean": sum(times) / len(times),
            "min": min(times),
            "max": max(times),
            "spread_pct_of_mean": ((max(times)-min(times)) / (sum(times)/len(times)) * 100.0) if len(times) > 1 else 0.0,
        },
        "final_render_s": {
            "values": final_times,
            "mean": sum(final_times) / len(final_times),
        },
        "instrumentation": {
            "unique_strokes_deposited": repeat_rows[-1]["unique_strokes_deposited"],
            "total_stroke_depositions": repeat_rows[-1]["total_stroke_depositions"],
            "duplicate_stroke_depositions": repeat_rows[-1]["duplicate_stroke_depositions"],
            "deposition_duplication_factor": repeat_rows[-1]["deposition_duplication_factor"],
            "render_artifact_calls": repeat_rows[-1]["render_artifact_calls"],
            "per_frame_json_count": repeat_rows[-1]["per_frame_json_count"],
        },
        "parity": {
            "all_final_pixel_parity": all(r["final_pixel_parity"] for r in repeat_rows),
            "all_repeat_final_pixels_identical": len({r["final_pixel_sha256"] for r in repeat_rows}) == 1,
        },
        "runs": repeat_rows,
    }
    (args.out / "baseline.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
