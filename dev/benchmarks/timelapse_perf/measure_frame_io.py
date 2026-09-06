from __future__ import annotations

import argparse
import json
import shutil
import time
from pathlib import Path

from PIL import Image

from img2drawing.core.session import sha256_file
from img2drawing.provenance.timelapse import pixel_sha256, save_gif


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--frames", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    src = Path(args.frames)
    paths = sorted(src.glob("*.png"))
    if not paths:
        raise ValueError("no PNG frames found")
    output = Path(args.out)
    shutil.rmtree(output, ignore_errors=True)
    output.mkdir(parents=True)

    total_bytes = sum(p.stat().st_size for p in paths)
    t0 = time.perf_counter(); [sha256_file(p) for p in paths]; byte_hash_s = time.perf_counter() - t0
    t0 = time.perf_counter(); [pixel_sha256(p) for p in paths]; pixel_hash_s = time.perf_counter() - t0

    png_save_s = 0.0
    for index, path in enumerate(paths):
        with Image.open(path) as image:
            image.load()
            t0 = time.perf_counter()
            image.save(output / f"frame_{index:04d}.png")
            png_save_s += time.perf_counter() - t0

    tiny = {"schema": "bench", "png_sha256": "a" * 64, "pixel_sha256": "b" * 64}
    t0 = time.perf_counter()
    for index in range(len(paths)):
        (output / f"frame_{index:04d}.render.json").write_text(json.dumps(tiny), encoding="utf-8")
    json_write_s = time.perf_counter() - t0

    gif_path = output / "timelapse.gif"
    t0 = time.perf_counter()
    save_gif(paths, [120] * len(paths), gif_path, colors=128, loop=0, disposal=2)
    gif_s = time.perf_counter() - t0

    metrics = {
        "schema": "img2drawing.timelapse_s05_frame_io.v1",
        "frames": len(paths),
        "png_bytes_total": total_bytes,
        "byte_hash_s": byte_hash_s,
        "pixel_hash_s": pixel_hash_s,
        "png_save_s": png_save_s,
        "per_frame_json_write_s": json_write_s,
        "gif_encode_s": gif_s,
        "measured_artifact_work_s": byte_hash_s + pixel_hash_s + png_save_s + json_write_s + gif_s,
        "gif_bytes": gif_path.stat().st_size,
    }
    (output / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
