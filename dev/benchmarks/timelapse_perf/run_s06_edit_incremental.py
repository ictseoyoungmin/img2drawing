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
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from img2drawing.core.ir import StrokeIR
from img2drawing.provenance.timelapse import save_gif, select_cursors
from img2drawing.vnext.session import DrawingSession
from edit_aware_pencil_renderer import EditAwareIncrementalPencilCanvas
from forward_history_replay import ForwardHistoryReplay
from material_kernel_pencil_renderer import KernelStrokeRasterCache


def prepared_view(profile, ir: StrokeIR) -> StrokeIR:
    """Profile-owned paper metadata without copying immutable stroke geometry."""
    profile.validate_canvas(ir.width, ir.height)
    metadata = dict(ir.metadata if isinstance(ir.metadata, dict) else {})
    metadata["paper"] = {
        "tooth": profile.paper_tooth,
        "scale": profile.paper_scale,
        "seed": profile.paper_seed,
    }
    out = StrokeIR(ir.width, ir.height, strokes=ir.strokes, metadata=metadata)
    if getattr(ir, "_legacy_inline_pressure", False):
        setattr(out, "_legacy_inline_pressure", True)
    return out


def pixel_sha_image(image: Image.Image) -> str:
    rgba = image.convert("RGBA")
    try:
        return hashlib.sha256(rgba.tobytes()).hexdigest()
    finally:
        rgba.close()


def pixel_sha_path(path: Path) -> str:
    with Image.open(path) as image:
        return pixel_sha_image(image)


def run(
    session: DrawingSession,
    out: Path,
    *,
    every_n: int = 4,
    write_png: bool = True,
    write_gif: bool = False,
) -> dict:
    shutil.rmtree(out, ignore_errors=True)
    out.mkdir(parents=True, exist_ok=True)
    profile = session.render_profile
    cursors = select_cursors(session._agent, "every_n", every_n=every_n)
    replay = ForwardHistoryReplay(session._agent.history)
    cache = KernelStrokeRasterCache()
    initial = prepared_view(profile, replay.snapshot(copy_strokes=False))
    canvas = EditAwareIncrementalPencilCanvas(initial, cache, **profile.renderer_kwargs())

    frame_paths: list[Path] = []
    hashes: list[str] = []
    durations: list[int] = []
    traversal_s = advance_s = snapshot_s = png_s = gif_s = 0.0
    transition_totals = {"added": 0, "changed": 0, "removed": 0, "regions": 0}
    t_all = time.perf_counter()
    try:
        for index, cursor in enumerate(cursors):
            t = time.perf_counter()
            replay.advance_to(cursor)
            ir = prepared_view(profile, replay.snapshot(copy_strokes=False))
            traversal_s += time.perf_counter() - t

            t = time.perf_counter()
            delta = canvas.advance_to(ir)
            advance_s += time.perf_counter() - t
            for key in transition_totals:
                transition_totals[key] += int(delta[key])

            t = time.perf_counter()
            canvas.snapshot_dirty(None)
            snapshot_s += time.perf_counter() - t
            hashes.append(pixel_sha_image(canvas.output_canvas))
            durations.append(900 if index == len(cursors) - 1 else 120)

            if write_png:
                path = out / f"frame_{index:04d}_cursor_{cursor:04d}.png"
                t = time.perf_counter()
                canvas.output_canvas.save(path)
                png_s += time.perf_counter() - t
                frame_paths.append(path)

        if write_gif:
            if not frame_paths:
                raise ValueError("GIF path currently requires PNG frames")
            t = time.perf_counter()
            save_gif(
                frame_paths,
                durations,
                out / "timelapse.gif",
                colors=profile.gif_palette_colors,
                loop=profile.gif_loop,
                disposal=profile.gif_disposal,
            )
            gif_s = time.perf_counter() - t

        return {
            "schema": "img2drawing.timelapse_s06_edit_incremental.v1",
            "actions": session._agent.history.cursor,
            "frames": len(cursors),
            "cursors": cursors,
            "wall_s": time.perf_counter() - t_all,
            "traversal_s": traversal_s,
            "advance_s": advance_s,
            "snapshot_update_s": snapshot_s,
            "png_save_s": png_s,
            "gif_encode_s": gif_s,
            "materialize_s": cache.materialize_seconds,
            "material_cache_entries": cache.entries,
            "material_cache_bytes": cache.bytes_estimate,
            "dirty_output_pixels": canvas.dirty_output_pixels,
            "canvas_bytes_estimate": canvas.canvas_bytes_estimate,
            "transition_totals": transition_totals,
            "canvas_stats": canvas.stats.__dict__,
            "final_pixel_sha256": hashes[-1],
            "frame_pixel_sha256": hashes,
        }
    finally:
        canvas.close()
        cache.close()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--session", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--every-n", type=int, default=4)
    parser.add_argument("--png", action="store_true")
    parser.add_argument("--gif", action="store_true")
    args = parser.parse_args()

    session = DrawingSession.resume(args.session)
    result = run(
        session,
        args.out / "frames",
        every_n=args.every_n,
        write_png=args.png or args.gif,
        write_gif=args.gif,
    )
    expected = args.session.parent / "lucy-croquis.png"
    if expected.exists():
        result["expected_final_png"] = str(expected)
        result["expected_final_pixel_sha256"] = pixel_sha_path(expected)
        result["final_pixel_parity"] = (
            result["expected_final_pixel_sha256"] == result["final_pixel_sha256"]
        )
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "s06_metrics.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "frame_pixel_sha256"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
