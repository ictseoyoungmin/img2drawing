from __future__ import annotations

import argparse
import hashlib
import json
import resource
import shutil
import sys
import time
from pathlib import Path

from PIL import Image

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from img2drawing.provenance.timelapse import save_gif, select_cursors
from make_fixture import build_fixture
from run_baseline import make_session
from cached_pencil_renderer import StrokeRasterCache, render_cached
from incremental_pencil_renderer import IncrementalAddOnlyPencilCanvas


def pixel_sha(path: Path) -> str:
    with Image.open(path) as im:
        return hashlib.sha256(im.convert("RGBA").tobytes()).hexdigest()


def run_s02_shape(session, out: Path, *, every_n: int) -> dict:
    """Cache-only full-frame recomposition baseline from S02, no GIF."""
    shutil.rmtree(out, ignore_errors=True)
    out.mkdir(parents=True, exist_ok=True)
    profile = session.render_profile
    if profile is None:
        raise ValueError("session has no RenderProfile")
    cursors = select_cursors(session._agent, "every_n", every_n=every_n)
    cache = StrokeRasterCache()
    hashes: list[str] = []
    times: list[float] = []
    t_all = time.perf_counter()
    for i, cursor in enumerate(cursors):
        path = out / f"frame_{i:04d}_cursor_{cursor:04d}.png"
        ir = profile.prepared_ir(session._agent.history.state_at(cursor))
        t0 = time.perf_counter()
        render_cached(ir, path, cache, **profile.renderer_kwargs())
        times.append(time.perf_counter() - t0)
        hashes.append(pixel_sha(path))
    wall = time.perf_counter() - t_all
    result = {
        "frames": len(cursors),
        "render_total_s": sum(times),
        "wall_s": wall,
        "hashes": hashes,
        "cache_entries": cache.entries,
        "cache_hits": cache.hits,
        "cache_misses": cache.misses,
        "cache_bytes": cache.bytes_estimate,
        "materialize_s": cache.materialize_seconds,
    }
    cache.close()
    return result


def run_incremental(
    session,
    out: Path,
    *,
    every_n: int,
    write_gif: bool,
    dirty_snapshot: bool = True,
) -> dict:
    shutil.rmtree(out, ignore_errors=True)
    out.mkdir(parents=True, exist_ok=True)
    profile = session.render_profile
    if profile is None:
        raise ValueError("session has no RenderProfile")
    cursors = select_cursors(session._agent, "every_n", every_n=every_n)
    cache = StrokeRasterCache()
    initial = profile.prepared_ir(session._agent.history.state_at(cursors[0]))
    canvas = IncrementalAddOnlyPencilCanvas(initial, cache, **profile.renderer_kwargs())

    paths: list[Path] = []
    hashes: list[str] = []
    advance_s: list[float] = []
    snapshot_s: list[float] = []
    dirty_rects = []
    new_counts = []
    durations = []
    t_all = time.perf_counter()
    for i, cursor in enumerate(cursors):
        ir = profile.prepared_ir(session._agent.history.state_at(cursor))
        t0 = time.perf_counter()
        new_counts.append(canvas.advance_to(ir))
        advance_s.append(time.perf_counter() - t0)

        path = out / f"frame_{i:04d}_cursor_{cursor:04d}.png"
        t0 = time.perf_counter()
        dirty_rects.append(
            canvas.snapshot_dirty(path)
            if dirty_snapshot
            else (canvas.snapshot(path) or None)
        )
        snapshot_s.append(time.perf_counter() - t0)
        paths.append(path)
        hashes.append(pixel_sha(path))
        durations.append(900 if i == len(cursors) - 1 else (180 if cursor == 0 else 120))

    gif_s = 0.0
    gif_path = None
    if write_gif:
        gif_path = out / "timelapse.gif"
        t0 = time.perf_counter()
        save_gif(
            paths,
            durations,
            gif_path,
            colors=profile.gif_palette_colors,
            loop=profile.gif_loop,
            disposal=profile.gif_disposal,
        )
        gif_s = time.perf_counter() - t0

    wall = time.perf_counter() - t_all
    stats = canvas.stats
    result = {
        "resolution": [profile.canvas_width, profile.canvas_height],
        "supersample": profile.supersample,
        "actions": session.history_cursor,
        "every_n": every_n,
        "frames": len(cursors),
        "new_strokes_per_frame": new_counts,
        "advance_total_s": sum(advance_s),
        "snapshot_total_s": sum(snapshot_s),
        "dirty_snapshot": bool(dirty_snapshot),
        "dirty_rects": dirty_rects,
        "dirty_output_pixels_total": canvas.dirty_output_pixels,
        "full_output_pixels_if_every_frame": profile.canvas_width * profile.canvas_height * len(cursors),
        "gif_encode_s": gif_s,
        "wall_s": wall,
        "frame_pixel_sha256": hashes,
        "cache": {
            "entries": cache.entries,
            "hits": cache.hits,
            "misses": cache.misses,
            "bytes_estimate": cache.bytes_estimate,
            "materialize_seconds": cache.materialize_seconds,
        },
        "persistent_canvas_bytes_estimate": canvas.canvas_bytes_estimate,
        "incremental": {
            "advances": stats.advances,
            "strokes_composited": stats.strokes_composited,
            "snapshots": stats.snapshots,
        },
        "maxrss_kb": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "gif": None if gif_path is None else {"path": str(gif_path), "bytes": gif_path.stat().st_size},
    }
    canvas.close()
    cache.close()
    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--supersample", type=int, default=4)
    ap.add_argument("--every-n", type=int, default=4)
    ap.add_argument("--s02-baseline", action="store_true", help="Also run S02 cache-only full-frame recomposition")
    ap.add_argument("--gif", action="store_true")
    ap.add_argument("--full-snapshot", action="store_true", help="Use full native snapshot resize instead of dirty-region snapshot")
    args = ap.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    session = make_session(build_fixture(), args.out / "fixture_work", args.supersample)
    incremental = run_incremental(
        session,
        args.out / "incremental",
        every_n=args.every_n,
        write_gif=args.gif,
        dirty_snapshot=not args.full_snapshot,
    )
    result = {"schema": "img2drawing.timelapse_s04_incremental.v1", "incremental": incremental}
    if args.s02_baseline:
        s02 = run_s02_shape(session, args.out / "s02_full_recompose", every_n=args.every_n)
        result["s02_full_recompose"] = s02
        result["parity"] = {
            "all_frames_pixel_identical": s02["hashes"] == incremental["frame_pixel_sha256"],
            "final_pixel_identical": s02["hashes"][-1] == incremental["frame_pixel_sha256"][-1],
        }
        result["speedup_vs_s02_full_recompose"] = {
            "wall": s02["wall_s"] / max(1e-9, incremental["wall_s"] - incremental["gif_encode_s"]),
            "render_vs_advance_snapshot": s02["render_total_s"] / max(1e-9, incremental["advance_total_s"] + incremental["snapshot_total_s"]),
        }

    (args.out / "s04_metrics.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
