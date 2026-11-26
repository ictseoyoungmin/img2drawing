"""GIF encoding: ffmpeg palette pipeline for delta packs, Pillow for canonical frame files."""

from __future__ import annotations

import hashlib
import os
import shutil
import struct
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Callable, Iterable

from PIL import GifImagePlugin, Image, ImageChops

from ..core.digest import sha256_file
from .delta_pack import iter_rgb_views, read_info

ENCODER_SCHEMA="img2drawing.local.ffmpeg-rectangle-gif.v1"


def _feed(proc,pack:Path):
    assert proc.stdin is not None
    try:
        for view in iter_rgb_views(pack): proc.stdin.write(view)
    finally:
        proc.stdin.close()
    return proc.wait()


def _palette_key(pack_hash: str, *, colors: int, reserve_transparent: bool) -> str:
    # Palette settings are part of cache identity, not the drawing's render contract.
    return hashlib.sha256(
        f"{ENCODER_SCHEMA}|{pack_hash}|diff|max_colors={colors}|reserve={int(reserve_transparent)}".encode()
    ).hexdigest()


def gif_rgb(image: Image.Image) -> Image.Image:
    """Shared GIF display policy: preserve opaque RGB, composite RGBA over white."""
    if image.mode == "RGB":
        return image.copy()
    with image.convert("RGBA") as rgba:
        with Image.new("RGBA", image.size, (255, 255, 255, 255)) as paper:
            paper.alpha_composite(rgba)
            return paper.convert("RGB")


def _set_full_frame_disposal(path: Path, *, disposal: int, size: tuple[int, int], frame_count: int) -> None:
    """Set disposal on independently decodable opaque full GIF frames only.

    FFmpeg does not expose disposal 2/3. Its rectangle/transparency optimization
    relies on disposal 1, so changing the flags on a delta GIF would corrupt replay.
    This bounded-memory block walk rejects any partial/transparent frame before
    publishing the staged output. No pixel data, palettes or durations are changed.
    """
    with path.open("r+b") as stream:
        def read(n):
            data = stream.read(n)
            if len(data) != n:
                raise ValueError("truncated GIF block")
            return data

        def subblocks():
            while True:
                n = read(1)[0]
                if not n:
                    return
                read(n)

        def table(flags):
            if flags & 0x80:
                read(3 * (2 ** ((flags & 7) + 1)))

        if read(6) not in (b"GIF87a", b"GIF89a"):
            raise ValueError("invalid GIF header")
        width, height, flags, _, _ = struct.unpack("<HHBBB", read(7))
        if (width, height) != size:
            raise ValueError("GIF logical screen differs from render size")
        table(flags)
        control = None
        count = 0
        while True:
            block = read(1)
            if block == b";":
                if control is not None or count != frame_count or stream.read(1):
                    raise ValueError("GIF frame count or trailer differs from staged frames")
                return
            if block == b"!":
                label = read(1)[0]
                if label == 0xF9:
                    if control is not None or read(1) != b"\x04":
                        raise ValueError("invalid GIF graphics control extension")
                    offset = stream.tell()
                    packed, _, _ = struct.unpack("<BHB", read(4))
                    if packed & 1 or read(1) != b"\x00":
                        raise ValueError("disposal override requires opaque GIF frames")
                    control = (offset, packed)
                elif label in (0xFF, 0xFE):  # application or comment extension
                    subblocks()
                else:
                    raise ValueError("unexpected GIF extension in staged encoder output")
                continue
            if block != b"," or control is None:
                raise ValueError("GIF frame lacks an explicit graphics control extension")
            x, y, w, h, flags = struct.unpack("<HHHHB", read(9))
            if (x, y, w, h) != (0, 0, *size):
                raise ValueError("disposal override requires independent full GIF frames")
            table(flags)
            read(1)  # LZW minimum code size
            subblocks()
            end = stream.tell()
            offset, packed = control
            stream.seek(offset)
            stream.write(bytes([(packed & ~0x1C) | (disposal << 2)]))
            stream.seek(end)
            control = None
            count += 1


def encode_gif(pack: Path, out_dir: Path, fps: int = 12, *, palette_cache_dir: Path | None = None,
               rectangle: bool = True, colors: int = 256, loop: int = 0, disposal: int = 1):
    pack = Path(pack)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    info = read_info(pack)
    w, h = info.width, info.height
    palette, gif = out_dir / "palette.png", out_dir / "timelapse.gif"
    # Only disposal 1 permits rectangle/transparency deltas without changing later frames.
    rectangle = bool(rectangle) and disposal == 1 and colors > 2
    reserve = rectangle
    pack_hash = sha256_file(pack)
    key = _palette_key(pack_hash, colors=colors, reserve_transparent=reserve)
    cache_hit = False
    cache_palette = None if palette_cache_dir is None else Path(palette_cache_dir) / f"{key}.png"
    if cache_palette is not None:
        cache_palette.parent.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    if cache_palette is not None and cache_palette.exists():
        shutil.copy2(cache_palette, palette)
        cache_hit = True
    else:
        p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
            "-s", f"{w}x{h}", "-r", str(fps), "-i", "-", "-vf",
            f"palettegen=stats_mode=diff:max_colors={colors}:reserve_transparent={int(reserve)}", str(palette)],
            stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        rc = _feed(p, pack)
        if rc != 0:
            raise RuntimeError(f"palettegen failed {rc}")
        if cache_palette is not None:
            tmp = cache_palette.with_name(cache_palette.name + f".{os.getpid()}.tmp")
            shutil.copy2(palette, tmp)
            os.replace(tmp, cache_palette)
    palette_sec = time.perf_counter() - t0
    filt = "[0:v][1:v]paletteuse=dither=bayer" + (":diff_mode=rectangle" if rectangle else "")
    t1 = time.perf_counter()
    # Publish only after the encoder and policy check succeed. Unique temp name
    # also avoids corrupting an existing export on encoding failure.
    with tempfile.NamedTemporaryFile(dir=out_dir, suffix=".gif", prefix=".timelapse-", delete=False) as fp:
        staged = Path(fp.name)
    try:
        p2 = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
            "-s", f"{w}x{h}", "-r", str(fps), "-i", "-", "-i", str(palette), "-filter_complex", filt,
            "-gifflags", "offsetting+transdiff" if rectangle else "0", "-loop", str(loop), str(staged)],
            stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        rc = _feed(p2, pack)
        if rc != 0:
            raise RuntimeError(f"gif encode failed {rc}")
        if disposal != 1:
            _set_full_frame_disposal(staged, disposal=disposal, size=(w, h), frame_count=info.frame_count)
        os.replace(staged, gif)
    finally:
        staged.unlink(missing_ok=True)
    encode_sec = time.perf_counter() - t1
    return {"gif": str(gif), "gif_sha256": sha256_file(gif), "palette": str(palette), "palette_cache_hit": cache_hit,
            "palette_sec": palette_sec, "gif_encode_sec": encode_sec, "total_encode_sec": palette_sec + encode_sec,
            "pack_sha256": pack_hash, "palette_key": key, "rectangle": rectangle,
            "colors": colors, "loop": loop, "disposal": disposal}


def save_gif_frames(
    frame_images: Iterable[Image.Image],
    durations: list[int],
    out_path: Path,
    *,
    colors: int = 64,
    loop: int = 0,
    disposal: int = 2,
    progress: Callable[[int, int], None] | None = None,
) -> None:
    """Write locally paletted GIF frames one at a time, with bounded peak RAM.

    No decoded-frame list, indexed-frame list, or temporary PNG frame spool is
    accumulated. Every source image is closed before the next one is requested.
    The GIF is atomically published only after its trailer has been written.
    """
    if not durations:
        raise ValueError("cannot write GIF with no frames")
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    frames = iter(frame_images)
    temporary: Path | None = None
    count = 0
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb", dir=out_path.parent, prefix=f".{out_path.name}.",
            suffix=".tmp", delete=False,
        ) as stream:
            temporary = Path(stream.name)
            for index, image in enumerate(frames):
                try:
                    if index >= len(durations):
                        raise ValueError("GIF has more frames than durations")
                    rgb = gif_rgb(image)
                    try:
                        indexed = rgb.quantize(
                            colors=int(colors), method=Image.Quantize.MAXCOVERAGE,
                        )
                    finally:
                        rgb.close()
                    try:
                        if index == 0:
                            header, _ = GifImagePlugin.getheader(
                                indexed, info={"loop": int(loop)},
                            )
                            for chunk in header:
                                stream.write(chunk)
                        for chunk in GifImagePlugin.getdata(
                            indexed, duration=int(durations[index]),
                            disposal=int(disposal), include_color_table=True,
                        ):
                            stream.write(chunk)
                    finally:
                        indexed.close()
                    count += 1
                    if progress is not None:
                        progress(count, len(durations))
                finally:
                    image.close()
            if count != len(durations):
                raise ValueError("GIF has fewer frames than durations")
            stream.write(b";")
        os.replace(temporary, out_path)
    finally:
        if callable(getattr(frames, "close", None)):
            frames.close()
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def save_gif(
    frame_paths: list[Path],
    durations: list[int],
    out_path: Path,
    *,
    colors: int = 64,
    loop: int = 0,
    disposal: int = 2,
) -> None:
    """Stream canonical PNG inputs with local frame palettes and bounded RAM."""
    save_gif_frames(
        (Image.open(path) for path in frame_paths),
        durations, out_path, colors=colors, loop=loop, disposal=disposal,
    )


def gif_final_frame_error(gif_path: Path, final_png: Path) -> tuple[int, float]:
    """Return ``(max, mean)`` channel error between the GIF's last frame and the final PNG."""

    with Image.open(gif_path) as gif, Image.open(final_png) as png:
        gif.seek(gif.n_frames - 1)
        with gif_rgb(gif) as actual, gif_rgb(png) as expected:
            with ImageChops.difference(actual, expected) as difference:
                max_error = max(channel[1] for channel in difference.getextrema())
                histogram = difference.histogram()
                total = sum(value * count for value in range(256) for count in histogram[value::256])
                mean_error = total / float(expected.width * expected.height * 3)
    return int(max_error), float(mean_error)
