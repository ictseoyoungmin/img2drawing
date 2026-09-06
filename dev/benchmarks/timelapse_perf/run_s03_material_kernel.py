from __future__ import annotations

import argparse
import hashlib
import json
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
from cached_pencil_renderer import StrokeRasterCache
from incremental_pencil_renderer import IncrementalAddOnlyPencilCanvas
from material_kernel_pencil_renderer import KernelStrokeRasterCache


def pixel_sha(path: Path) -> str:
    with Image.open(path) as image:
        return hashlib.sha256(image.convert("RGBA").tobytes()).hexdigest()


def run(session, out: Path, *, every_n: int, kernel: bool, write_gif: bool) -> dict:
    shutil.rmtree(out, ignore_errors=True)
    out.mkdir(parents=True, exist_ok=True)
    profile = session.render_profile
    cursors = select_cursors(session._agent, "every_n", every_n=every_n)
    cache = KernelStrokeRasterCache() if kernel else StrokeRasterCache()
    initial = profile.prepared_ir(session._agent.history.state_at(cursors[0]))
    canvas = IncrementalAddOnlyPencilCanvas(initial, cache, **profile.renderer_kwargs())
    paths: list[Path] = []
    hashes: list[str] = []
    durations: list[int] = []
    advance_s = 0.0
    snapshot_s = 0.0
    t_all = time.perf_counter()
    for index, cursor in enumerate(cursors):
        ir = profile.prepared_ir(session._agent.history.state_at(cursor))
        t = time.perf_counter()
        canvas.advance_to(ir)
        advance_s += time.perf_counter() - t
        path = out / f"frame_{index:04d}_cursor_{cursor:04d}.png"
        t = time.perf_counter()
        canvas.snapshot_dirty(path)
        snapshot_s += time.perf_counter() - t
        paths.append(path)
        hashes.append(pixel_sha(path))
        durations.append(900 if index == len(cursors) - 1 else 120)
    gif_s = 0.0
    if write_gif:
        t = time.perf_counter()
        save_gif(
            paths, durations, out / "timelapse.gif",
            colors=profile.gif_palette_colors,
            loop=profile.gif_loop,
            disposal=profile.gif_disposal,
        )
        gif_s = time.perf_counter() - t
    result = {
        "frames": len(cursors),
        "wall_s": time.perf_counter() - t_all,
        "advance_s": advance_s,
        "snapshot_s": snapshot_s,
        "gif_s": gif_s,
        "materialize_s": cache.materialize_seconds,
        "mask_cache_bytes": cache.bytes_estimate,
        "stage_seconds": getattr(cache, "stage_seconds", None),
        "frame_hashes": hashes,
        "dirty_output_pixels": canvas.dirty_output_pixels,
    }
    canvas.close()
    cache.close()
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--supersample", type=int, default=4)
    parser.add_argument("--every-n", type=int, default=4)
    parser.add_argument("--gif", action="store_true")
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    session = make_session(build_fixture(), args.out / "fixture", args.supersample)
    baseline = run(session, args.out / "s04", every_n=args.every_n, kernel=False, write_gif=args.gif)
    kernel = run(session, args.out / "s03_kernel", every_n=args.every_n, kernel=True, write_gif=args.gif)
    result = {
        "schema": "img2drawing.timelapse_s03_material_kernel.v1",
        "s04": baseline,
        "s03_kernel": kernel,
        "parity": {"all_frames_pixel_identical": baseline["frame_hashes"] == kernel["frame_hashes"]},
        "speedup": {
            "wall": baseline["wall_s"] / kernel["wall_s"],
            "materialize": baseline["materialize_s"] / kernel["materialize_s"],
        },
    }
    baseline.pop("frame_hashes")
    kernel.pop("frame_hashes")
    (args.out / "s03_metrics.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
