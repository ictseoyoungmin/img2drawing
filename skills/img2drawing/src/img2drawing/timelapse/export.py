"""The single timelapse export: action-ordered frames and GIF from one history and profile.

``backend="auto"`` (the default) uses the exact incremental fast path whenever the history is
eligible and ffmpeg is available, and otherwise renders every frame canonically for the whole
export. Both paths render an independent canonical final PNG and refuse to finish unless the
last frame matches it pixel-for-pixel.
"""

from __future__ import annotations

import json
import shutil
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from PIL import Image

from .._version import __version__
from ..core.digest import sha256_file
from ..render.artifact import action_log_sha256, render_history_at, rgb_sha256
from ..render.profile import RenderProfile
from .delta_pack import DeltaPackWriter, iter_frames, read_info
from .frames import FastFrameSource, inspect_fast_path_eligibility
from .gif import encode_gif, gif_final_frame_error, save_gif

REPLAY_EXPORT_SCHEMA = "img2drawing.replay_export.v2"
BACKENDS = ("auto", "fast", "canonical")
SAMPLING_MODES = ("action", "every_n")

_CANONICAL_GIF_TOLERANCE = {"max_channel_error": 24, "mean_channel_error": 2.0}
_FAST_GIF_TOLERANCE = {"max_channel_error": 32, "mean_channel_error": 4.0}


@dataclass(frozen=True)
class ReplayExport:
    manifest: dict[str, Any]
    manifest_path: Path
    gif_path: Path
    final_path: Path
    frame_dir: Path


def sample_cursors(final_cursor: int, mode: str = "every_n", every_n: int = 4) -> list[int]:
    """Cursors ``0, n, 2n, …, final``; cursor N is the state after the first N actions."""

    if mode not in SAMPLING_MODES:
        raise ValueError("timelapse mode must be 'action' or 'every_n'")
    step = 1 if mode == "action" else every_n
    if int(step) != step or step < 1:
        raise ValueError("every_n must be a positive integer")
    cursors = list(range(0, int(final_cursor) + 1, int(step)))
    if cursors[-1] != int(final_cursor):
        cursors.append(int(final_cursor))
    return cursors


def _pixel_work(profile: RenderProfile, frame_count: int) -> int:
    return (
        frame_count
        * profile.canvas_width
        * profile.canvas_height
        * profile.output_scale
        * profile.output_scale
        * profile.supersample
        * profile.supersample
    )


def _frame_record(history, index: int, cursor: int, **fields: Any) -> dict[str, Any]:
    action = None if cursor == 0 else history.actions[cursor - 1]
    return {
        "frame_index": index,
        "cursor": cursor,
        "action_seq": None if action is None else action.seq,
        "action": None if action is None else action.action,
        "part": None if action is None else action.part,
        "role": None if action is None else action.role,
        **fields,
    }


def _canonical_duration_ms(history, cursor: int, *, final: bool) -> int:
    if final:
        return 900
    if cursor == 0:
        return 180
    if history.actions[cursor - 1].action in {
        "stroke.delete", "stroke.soft_lift", "stroke.segment_replace", "stroke.segment_soft_lift",
    }:
        return 180
    return 120


def _check_gif(gif_path: Path, final_path: Path, tolerance: dict, max_gif_bytes: int) -> dict[str, Any]:
    gif_bytes = gif_path.stat().st_size
    if gif_bytes > int(max_gif_bytes):
        raise ValueError("replay GIF size budget exceeded")
    max_error, mean_error = gif_final_frame_error(gif_path, final_path)
    within = max_error <= tolerance["max_channel_error"] and mean_error <= tolerance["mean_channel_error"]
    if not within:
        raise RuntimeError("encoded GIF final frame exceeds documented color tolerance")
    return {
        "file": gif_path.name,
        "sha256": sha256_file(gif_path),
        "bytes": gif_bytes,
        "final_frame_max_channel_error": max_error,
        "final_frame_mean_channel_error": mean_error,
        "tolerance": tolerance,
        "within_tolerance": within,
    }


def _export_canonical(history, profile: RenderProfile, output: Path, cursors: list[int]) -> tuple[list, Path, dict]:
    frame_dir = output / "frames"
    frame_dir.mkdir(parents=True, exist_ok=True)
    frames: list[dict[str, Any]] = []
    frame_paths: list[Path] = []
    durations: list[int] = []
    for index, cursor in enumerate(cursors):
        path = frame_dir / f"frame_{index:04d}_cursor_{cursor:04d}.png"
        artifact = render_history_at(history, cursor, path, profile)
        duration = _canonical_duration_ms(history, cursor, final=index == len(cursors) - 1)
        frames.append(_frame_record(
            history, index, cursor,
            duration_ms=duration,
            file=path.relative_to(output).as_posix(),
            png_sha256=artifact.png_sha256,
            pixel_sha256=artifact.pixel_sha256,
            pixel_hash_mode="RGBA",
            drawing_state_hash=artifact.drawing_state_hash,
        ))
        frame_paths.append(path)
        durations.append(duration)
    gif_path = output / "timelapse.gif"
    save_gif(frame_paths, durations, gif_path, colors=profile.gif_palette_colors,
             loop=profile.gif_loop, disposal=profile.gif_disposal)
    timing = {"policy": "per-action", "initial_ms": 180, "ordinary_action_ms": 120,
              "edit_action_ms": 180, "final_hold_ms": 900}
    return frames, gif_path, timing


def _export_fast(history, profile: RenderProfile, output: Path, cursors: list[int], *, fps: int,
                 cache_dir: Path, materialize_frames: bool, rectangle: bool) -> tuple[list, Path, dict, dict]:
    source = FastFrameSource(history, profile, persistent_cache_dir=cache_dir / "patches")
    out_size = (profile.canvas_width * profile.output_scale, profile.canvas_height * profile.output_scale)
    pack_path = output / "frames.idp"
    frame_hashes: list[str] = []
    t0 = time.perf_counter()
    try:
        with DeltaPackWriter(pack_path, width=out_size[0], height=out_size[1], frame_count=len(cursors), level=1) as writer:
            for index, cursor in enumerate(cursors):
                info = source.advance_to(cursor)
                frame = source.image()
                try:
                    rects = [(0, 0, frame.width, frame.height)] if index == 0 else info["output_regions"]
                    writer.write_frame(frame, rects)
                    frame_hashes.append(rgb_sha256(frame))
                finally:
                    frame.close()
        render_pack_sec = time.perf_counter() - t0
        source_stats = dict(source.stats)
        cache_stats = dict(source.renderer.stats)
        persistent = dict(source.renderer.persistent)
    finally:
        source.close()

    encode = encode_gif(pack_path, output, int(fps), palette_cache_dir=cache_dir / "palettes", rectangle=bool(rectangle))

    files: list[str | None] = [None] * len(cursors)
    if materialize_frames:
        frame_dir = output / "frames"
        frame_dir.mkdir(parents=True, exist_ok=True)
        for index, (cursor, image) in enumerate(zip(cursors, iter_frames(pack_path))):
            path = frame_dir / f"frame_{index:04d}_cursor_{cursor:04d}.png"
            try:
                image.save(path)
            finally:
                image.close()
            files[index] = f"frames/{path.name}"

    frame_ms = max(1, int(round(1000.0 / float(fps))))
    frames = [
        _frame_record(
            history, index, cursor,
            duration_ms=frame_ms, file=files[index], png_sha256=None,
            pixel_sha256=frame_hashes[index], pixel_hash_mode="RGB", drawing_state_hash=None,
        )
        for index, cursor in enumerate(cursors)
    ]
    pack_info = read_info(pack_path)
    hits, misses, builds = persistent["disk_hits"], persistent["disk_misses"], cache_stats["cache_misses"]
    cache_state = (
        "warm" if hits > 0 and misses == 0 and builds == 0
        else "cold" if hits == 0 and builds > 0
        else "not-applicable" if hits == 0 and builds == 0
        else "mixed"
    )
    fast = {
        "engine": "local-first-exact-delta-pack-v1",
        "img2drawing_version": __version__,
        "cache_state": cache_state,
        "performance": {
            "render_pack_sec": render_pack_sec,
            "encode_sec": float(encode["total_encode_sec"]),
            "pipeline_sec": render_pack_sec + float(encode["total_encode_sec"]),
        },
        "pack": {
            "file": pack_path.name,
            "bytes": pack_path.stat().st_size,
            "patches": pack_info.patches_total,
            "compressed_patch_bytes": pack_info.compressed_patch_bytes,
        },
        "frame_source_stats": source_stats,
        "patch_cache_stats": cache_stats,
        "persistent_patch_cache": persistent,
        "encode": encode,
    }
    timing = {"policy": "constant-fps", "fps": int(fps), "frame_ms": frame_ms}
    return frames, Path(encode["gif"]), timing, fast


def _clean(output: Path) -> None:
    """Remove generated artifacts while preserving the persistent ``.cache`` directory."""

    frame_dir = output / "frames"
    if frame_dir.exists():
        shutil.rmtree(frame_dir)
    for name in (
        "canonical_final.png", "canonical_final.render.json", "replay_manifest.json",
        "timelapse.gif", "frames.idp", "frames.idp.partial", "palette.png",
    ):
        (output / name).unlink(missing_ok=True)


def export_timelapse(
    history,
    profile: RenderProfile,
    out_dir: str | Path,
    *,
    session_id: str,
    mode: str = "every_n",
    every_n: int = 4,
    backend: str = "auto",
    max_pixel_work: int = 20_000_000,
    max_gif_bytes: int = 25_000_000,
    clean: bool = True,
    materialize_frames: bool = False,
    cache_dir: str | Path | None = None,
    fps: int = 12,
    rectangle: bool = True,
) -> ReplayExport:
    """Export ``history`` action 0 → latest as ``timelapse.gif`` plus a replay manifest.

    ``backend``: ``"auto"`` picks the exact fast path when eligible and ffmpeg exists,
    ``"fast"`` requires it, ``"canonical"`` re-renders every frame as PNG. Frame PNGs are
    always written by the canonical path and only on request (``materialize_frames``) by
    the fast path.
    """

    if backend not in BACKENDS:
        raise ValueError(f"backend must be one of {BACKENDS}")
    if int(fps) != fps or fps < 1:
        raise ValueError("fps must be a positive integer")
    if int(max_gif_bytes) < 1:
        raise ValueError("max_gif_bytes must be >= 1")
    profile.validate_canvas(history.width, history.height)
    cursors = sample_cursors(history.cursor, mode, every_n)
    pixel_work = _pixel_work(profile, len(cursors))
    if pixel_work > int(max_pixel_work):
        raise ValueError("replay pixel-work budget exceeded")

    selected, fallback_reason = backend, None
    if backend != "canonical":
        eligibility = inspect_fast_path_eligibility(history)
        if not eligibility.eligible:
            fallback_reason = "; ".join(eligibility.reasons)
        elif shutil.which("ffmpeg") is None:
            fallback_reason = "ffmpeg is unavailable"
        if fallback_reason is not None and backend == "fast":
            raise ValueError(f"fast timelapse backend unavailable: {fallback_reason}")
        selected = "canonical" if fallback_reason is not None else "fast"

    output = Path(out_dir)
    output.mkdir(parents=True, exist_ok=True)
    if clean:
        _clean(output)
    before_history = history.to_dict()

    fast_summary = None
    if selected == "fast":
        cache_root = Path(cache_dir) if cache_dir is not None else output / ".cache"
        frames, gif_path, timing, fast_summary = _export_fast(
            history, profile, output, cursors, fps=int(fps), cache_dir=cache_root,
            materialize_frames=materialize_frames, rectangle=rectangle,
        )
        tolerance = _FAST_GIF_TOLERANCE
    else:
        frames, gif_path, timing = _export_canonical(history, profile, output, cursors)
        tolerance = _CANONICAL_GIF_TOLERANCE

    final_path = output / "canonical_final.png"
    final_artifact = render_history_at(history, history.cursor, final_path, profile)
    with Image.open(final_path) as image:
        final_rgb = rgb_sha256(image)
    last = frames[-1]
    last_match = last["pixel_sha256"] == (final_rgb if last["pixel_hash_mode"] == "RGB" else final_artifact.pixel_sha256)
    if not last_match:
        raise RuntimeError("final timelapse frame does not match the independently rendered final PNG")
    gif = _check_gif(gif_path, final_path, tolerance, max_gif_bytes)
    if history.to_dict() != before_history:
        raise RuntimeError("timelapse export mutated authoritative history")

    manifest = {
        "schema": REPLAY_EXPORT_SCHEMA,
        "session_id": session_id,
        "backend": {"requested": backend, "selected": selected, "fallback_reason": fallback_reason},
        "history": {
            "action_log_sha256": action_log_sha256(history),
            "action_count": len(history.actions),
            "latest_cursor": history.cursor,
        },
        "render_profile": profile.to_dict(),
        "render_profile_digest": profile.digest(),
        "sampling": {
            "mode": mode,
            "every_n": every_n if mode == "every_n" else None,
            "action_zero_included": cursors[0] == 0,
            "latest_included": cursors[-1] == history.cursor,
            "cursor_semantics": "cursor N is state after the first N authored actions",
        },
        "timing": timing,
        "budget": {
            "max_pixel_work": int(max_pixel_work),
            "pixel_work": pixel_work,
            "max_gif_bytes": int(max_gif_bytes),
            "gif_bytes": gif["bytes"],
        },
        "frames": frames,
        "final": {
            "file": final_path.name,
            "png_sha256": final_artifact.png_sha256,
            "pixel_sha256": final_artifact.pixel_sha256,
            "rgb_sha256": final_rgb,
            "last_frame_pixel_match": last_match,
        },
        "gif": gif,
    }
    if fast_summary is not None:
        manifest["fast"] = fast_summary
    manifest_path = output / "replay_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")
    return ReplayExport(manifest, manifest_path, gif_path, final_path, output / "frames")


__all__ = ["BACKENDS", "REPLAY_EXPORT_SCHEMA", "ReplayExport", "export_timelapse", "sample_cursors"]
