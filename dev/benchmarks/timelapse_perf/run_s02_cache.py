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
from img2drawing.render.pillow_pencil_contact import render as canonical_render
from img2drawing.vnext.session import DrawingSession
from make_fixture import build_fixture
from run_baseline import make_session
from cached_pencil_renderer import StrokeRasterCache, render_cached


def pixel_sha(path: Path) -> str:
    with Image.open(path) as im:
        return hashlib.sha256(im.convert("RGBA").tobytes()).hexdigest()


def render_one(ir, profile, path: Path, *, cache: StrokeRasterCache | None) -> None:
    prepared = profile.prepared_ir(ir)
    kwargs = profile.renderer_kwargs()
    if cache is None:
        canonical_render(prepared, path, **kwargs)
    else:
        render_cached(prepared, path, cache, **kwargs)


def run_frames(session: DrawingSession, out: Path, *, every_n: int, cached: bool, write_gif: bool) -> dict:
    shutil.rmtree(out, ignore_errors=True)
    out.mkdir(parents=True, exist_ok=True)
    profile = session.render_profile
    if profile is None:
        raise ValueError("session has no RenderProfile")
    cursors = select_cursors(session._agent, "every_n", every_n=every_n)
    cache = StrokeRasterCache() if cached else None
    paths: list[Path] = []
    durations: list[int] = []
    frame_times: list[float] = []
    hashes: list[str] = []
    t_all = time.perf_counter()
    for i, cursor in enumerate(cursors):
        path = out / f"frame_{i:04d}_cursor_{cursor:04d}.png"
        ir = session._agent.history.state_at(cursor)
        t0 = time.perf_counter()
        render_one(ir, profile, path, cache=cache)
        frame_times.append(time.perf_counter() - t0)
        paths.append(path)
        durations.append(900 if i == len(cursors)-1 else (180 if cursor == 0 else 120))
        hashes.append(pixel_sha(path))
    # Mirror the current exporter contract: independently render the final state
    # once more after the sampled final frame. With S02 cache this must be a pure
    # cache-hit/composition pass rather than another materialization pass.
    final_path = out / "canonical_final.png"
    final_ir = session._agent.history.state_at(session.history_cursor)
    t0 = time.perf_counter()
    render_one(final_ir, profile, final_path, cache=cache)
    independent_final_s = time.perf_counter() - t0
    independent_final_hash = pixel_sha(final_path)

    gif_s = 0.0
    gif_path = None
    if write_gif:
        gif_path = out / "timelapse.gif"
        t0 = time.perf_counter()
        save_gif(paths, durations, gif_path, colors=profile.gif_palette_colors, loop=profile.gif_loop, disposal=profile.gif_disposal)
        gif_s = time.perf_counter() - t0
    total = time.perf_counter() - t_all
    result = {
        "cached": bool(cached),
        "resolution": [profile.canvas_width, profile.canvas_height],
        "supersample": profile.supersample,
        "actions": session.history_cursor,
        "every_n": every_n,
        "frames": len(paths),
        "render_total_s": sum(frame_times),
        "render_mean_s": sum(frame_times) / max(1, len(frame_times)),
        "independent_final_render_s": independent_final_s,
        "independent_final_pixel_sha256": independent_final_hash,
        "independent_final_matches_last_frame": independent_final_hash == hashes[-1],
        "gif_encode_s": gif_s,
        "wall_s": total,
        "full_render_calls": len(paths) + 1,
        "frame_pixel_sha256": hashes,
        "final_pixel_sha256": hashes[-1],
        "maxrss_kb": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "cache": None if cache is None else {
            "entries": cache.entries,
            "hits": cache.hits,
            "misses": cache.misses,
            "hit_rate": cache.hits / max(1, cache.hits + cache.misses),
            "bytes_estimate": cache.bytes_estimate,
            "materialize_seconds": cache.materialize_seconds,
        },
        "gif": None if gif_path is None else {"path": str(gif_path), "bytes": gif_path.stat().st_size},
    }
    if cache is not None:
        cache.close()
    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--session", type=Path, default=None, help="Existing vNext session/checkpoint; otherwise uses generated 48-stroke fixture")
    ap.add_argument("--supersample", type=int, default=4, help="Generated fixture only")
    ap.add_argument("--every-n", type=int, default=4)
    ap.add_argument("--baseline", action="store_true", help="Also render uncached canonical frames for exact frame-by-frame parity/timing")
    ap.add_argument("--gif", action="store_true")
    args = ap.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    if args.session is None:
        session = make_session(build_fixture(), args.out / "fixture_work", args.supersample)
    else:
        session = DrawingSession.resume(args.session)

    cached = run_frames(session, args.out / "cached", every_n=args.every_n, cached=True, write_gif=args.gif)
    result = {"schema": "img2drawing.timelapse_s02_stroke_cache.v1", "cached": cached}
    if args.baseline:
        baseline = run_frames(session, args.out / "canonical", every_n=args.every_n, cached=False, write_gif=args.gif)
        same = baseline["frame_pixel_sha256"] == cached["frame_pixel_sha256"]
        result["canonical"] = baseline
        result["parity"] = {
            "all_frame_pixels_identical": same,
            "final_pixel_identical": baseline["final_pixel_sha256"] == cached["final_pixel_sha256"],
        }
        result["speedup"] = {
            "render": baseline["render_total_s"] / max(1e-9, cached["render_total_s"]),
            "wall": baseline["wall_s"] / max(1e-9, cached["wall_s"]),
        }
    (args.out / "s02_metrics.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
