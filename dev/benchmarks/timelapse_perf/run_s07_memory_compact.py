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
from img2drawing.provenance.timelapse import select_cursors
from img2drawing.vnext.session import DrawingSession
from forward_history_replay import ForwardHistoryReplay
from alpha_active_pencil_renderer import AlphaActiveEditAwareCanvas


def prepared_view(profile, ir: StrokeIR) -> StrokeIR:
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


def pixel_sha(im: Image.Image) -> str:
    return hashlib.sha256(im.convert("RGBA").tobytes()).hexdigest()


def run(session: DrawingSession, out: Path, *, every_n: int = 4, write_png: bool = False) -> dict:
    shutil.rmtree(out, ignore_errors=True)
    out.mkdir(parents=True, exist_ok=True)
    profile = session.render_profile
    cursors = select_cursors(session._agent, "every_n", every_n=every_n)
    replay = ForwardHistoryReplay(session._agent.history)
    initial = prepared_view(profile, replay.snapshot(copy_strokes=False))
    canvas = AlphaActiveEditAwareCanvas(initial, **profile.renderer_kwargs())

    hashes = []
    traversal_s = 0.0
    advance_s = 0.0
    snapshot_s = 0.0
    png_s = 0.0
    transition_totals = {"added": 0, "changed": 0, "removed": 0, "regions": 0}
    t_all = time.perf_counter()

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
        hashes.append(pixel_sha(canvas.output_canvas))

        if write_png:
            path = out / f"frame_{index:04d}_cursor_{cursor:04d}.png"
            t = time.perf_counter()
            canvas.output_canvas.save(path)
            png_s += time.perf_counter() - t

    result = {
        "schema": "img2drawing.timelapse_s07_memory_compact.v1",
        "actions": session._agent.history.cursor,
        "frames": len(cursors),
        "cursors": cursors,
        "wall_s": time.perf_counter() - t_all,
        "traversal_s": traversal_s,
        "advance_s": advance_s,
        "snapshot_update_s": snapshot_s,
        "png_save_s": png_s,
        "materialize_s": canvas.materializer.materialize_seconds,
        "materializations": canvas.materializer.materializations,
        "active_material_bytes_final": canvas.active_material_bytes,
        "peak_active_material_bytes": canvas.peak_active_material_bytes,
        "alpha_canvas_bytes_estimate": canvas.canvas_bytes_estimate,
        "output_canvas_bytes_estimate": canvas.out_size[0] * canvas.out_size[1] * 4,
        "live_raster_bytes_final_estimate": canvas.total_live_raster_bytes_estimate,
        "dirty_output_pixels": canvas.dirty_output_pixels,
        "transition_totals": transition_totals,
        "canvas_stats": canvas.stats.__dict__,
        "final_pixel_sha256": hashes[-1],
        "frame_pixel_sha256": hashes,
    }
    canvas.close()
    return result


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--session", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--every-n", type=int, default=4)
    ap.add_argument("--png", action="store_true")
    args = ap.parse_args()

    session = DrawingSession.resume(args.session)
    result = run(session, args.out / "frames", every_n=args.every_n, write_png=args.png)
    expected = args.session.parent / "lucy-croquis.png"
    if expected.exists():
        with Image.open(expected) as image:
            result["expected_final_pixel_sha256"] = pixel_sha(image)
        result["final_pixel_parity"] = result["expected_final_pixel_sha256"] == result["final_pixel_sha256"]
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "s07_metrics.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k not in {"frame_pixel_sha256", "cursors"}}, indent=2))


if __name__ == "__main__":
    main()
