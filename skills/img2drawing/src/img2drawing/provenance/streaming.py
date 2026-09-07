from __future__ import annotations

import hashlib
import json
import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from PIL import GifImagePlugin, Image, ImageChops

from ..core.session import DrawingSession, sha256_file
from ..render.pillow_pencil_contact import render as pencil_render
from .timelapse import _debug_overlay, _frame_duration_ms, pixel_sha256, select_cursors


STREAMING_SCHEMA = "img2drawing.timelapse.streaming.v1"
CHECKPOINT_SCHEMA = "img2drawing.timelapse.checkpoint.v1"


class ResumeMismatchError(RuntimeError):
    """The durable partial export belongs to a different replay contract."""


class SimulatedInterruption(RuntimeError):
    """Test-only interruption raised after a committed frame boundary."""


@dataclass
class StreamingTimelapseExport:
    manifest: dict[str, Any]
    manifest_path: Path
    gif_path: Path
    checkpoint_path: Path
    resumed: bool


def _atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    with open(tmp, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False, sort_keys=True)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp, path)
    try:
        fd = os.open(path.parent, os.O_RDONLY)
    except OSError:
        return
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _flatten_rgb(path: Path) -> Image.Image:
    source = Image.open(path).convert("RGBA")
    try:
        background = Image.new("RGBA", source.size, (255, 255, 255, 255))
        background.alpha_composite(source)
        rgb = background.convert("RGB")
        background.close()
        return rgb
    finally:
        source.close()


def _palette_from_path(path: Path, colors: int) -> list[int]:
    rgb = _flatten_rgb(path)
    try:
        paletted = rgb.quantize(colors=int(colors), method=Image.Quantize.MAXCOVERAGE)
        try:
            palette = list(paletted.getpalette() or [])
        finally:
            paletted.close()
    finally:
        rgb.close()
    if len(palette) < 768:
        palette.extend([0] * (768 - len(palette)))
    return palette[:768]


def _quantize_path(path: Path, palette: list[int]) -> Image.Image:
    rgb = _flatten_rgb(path)
    template = Image.new("P", (1, 1))
    template.putpalette(palette)
    try:
        return rgb.quantize(palette=template, dither=Image.Dither.NONE)
    finally:
        rgb.close()
        template.close()


def _compatibility_key(
    session: DrawingSession,
    *,
    mode: str,
    every_n: int,
    renderer_id: str,
    renderer_kwargs: dict[str, Any],
    final_renderer_kwargs: dict[str, Any],
    colors: int,
    delta_bbox: bool,
    debug_overlay: bool,
) -> dict[str, Any]:
    return {
        "session_id": session.session_id,
        "action_log_sha256": session.action_hash(),
        "state_sha256": session.state_hash(),
        "cursor": session.history.cursor,
        "mode": mode,
        "every_n": every_n if mode == "every_n" else None,
        "renderer_id": renderer_id,
        "renderer_kwargs": renderer_kwargs,
        "final_renderer_kwargs": final_renderer_kwargs,
        "colors": int(colors),
        "delta_bbox": bool(delta_bbox),
        "debug_overlay": bool(debug_overlay),
    }


def _checkpoint(
    *,
    compatibility: dict[str, Any],
    frame_count: int,
    cursor: int,
    gif_offset: int,
    journal_offset: int,
    palette: list[int],
    expected_final_pixel_sha256: str,
    completed: bool = False,
) -> dict[str, Any]:
    return {
        "schema": CHECKPOINT_SCHEMA,
        "compatibility": compatibility,
        "committed_frame_count": int(frame_count),
        "committed_cursor": int(cursor),
        "gif_byte_offset": int(gif_offset),
        "journal_byte_offset": int(journal_offset),
        "palette": palette,
        "palette_sha256": hashlib.sha256(bytes(palette)).hexdigest(),
        "expected_final_pixel_sha256": expected_final_pixel_sha256,
        "completed": bool(completed),
    }


def _write_global_header(handle, frame: Image.Image, *, loop: int) -> None:
    for chunk in GifImagePlugin._get_global_header(frame, {"loop": int(loop)}):
        handle.write(chunk)


def _write_frame(
    handle,
    current: Image.Image,
    previous: Image.Image | None,
    *,
    duration_ms: int,
    delta_bbox: bool,
) -> tuple[tuple[int, int, int, int], Image.Image]:
    if previous is None or not delta_bbox:
        bbox = (0, 0, current.width, current.height)
        frame = current
        disposal = 1 if delta_bbox else 2
    else:
        diff = ImageChops.difference(previous, current)
        try:
            bbox = diff.getbbox()
        finally:
            diff.close()
        if bbox is None:
            bbox = (0, 0, 1, 1)
        frame = current.crop(bbox)
        disposal = 1
    GifImagePlugin._write_frame_data(
        handle,
        frame,
        (bbox[0], bbox[1]),
        {
            "duration": int(duration_ms),
            "disposal": int(disposal),
            "include_color_table": False,
        },
    )
    if frame is not current:
        frame.close()
    return bbox, current.copy()


def _truncate(path: Path, size: int) -> None:
    with open(path, "r+b") as handle:
        handle.truncate(int(size))
        handle.flush()
        os.fsync(handle.fileno())


def _load_journal(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows = []
    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def export_timelapse_streaming(
    session_path: str | Path,
    out_dir: str | Path,
    *,
    mode: str = "every_n",
    every_n: int = 8,
    resume: bool = False,
    clean: bool = True,
    colors: int = 64,
    delta_bbox: bool = True,
    debug_overlay: bool = False,
    renderer: Callable[..., None] | None = None,
    renderer_kwargs: dict[str, Any] | None = None,
    renderer_id: str | None = None,
    expected_final_path: str | Path | None = None,
    final_renderer_kwargs: dict[str, Any] | None = None,
    loop: int = 0,
    _stop_after_frames: int | None = None,
) -> StreamingTimelapseExport:
    """Write a GIF one frame at a time with crash-safe resume checkpoints.

    A committed frame boundary is durable only after both GIF bytes and the frame journal are
    fsynced and checkpoint.json has been atomically replaced. On resume, any uncommitted tail is
    truncated before appending. The function intentionally keeps only one staging PNG and two
    palette-indexed frames in memory; it never retains the full frame set.

    The renderer is still the canonical renderer supplied by the caller (pencil by default). The
    exact incremental compositor from the S02-S08 performance work can be plugged in behind this
    writer without changing the checkpoint contract.
    """
    session_path = Path(session_path)
    out_dir = Path(out_dir)
    checkpoint_path = out_dir / "checkpoint.json"
    journal_path = out_dir / "frames.journal.jsonl"
    tmp_gif = out_dir / "timelapse.tmp.gif"
    gif_path = out_dir / ("debug_timelapse.gif" if debug_overlay else "timelapse.gif")
    manifest_path = out_dir / "manifest.json"
    staging = out_dir / ".frame.png"
    palette_source = out_dir / ".palette_source.png"

    render_fn = renderer or pencil_render
    render_kwargs = dict(renderer_kwargs or {})
    final_kwargs = dict(render_kwargs if final_renderer_kwargs is None else final_renderer_kwargs)
    effective_renderer_id = renderer_id or getattr(render_fn, "__module__", "renderer")

    session = DrawingSession.load(session_path, verify=True)
    cursors = select_cursors(session, mode, every_n=every_n)
    compatibility = _compatibility_key(
        session,
        mode=mode,
        every_n=every_n,
        renderer_id=effective_renderer_id,
        renderer_kwargs=render_kwargs,
        final_renderer_kwargs=final_kwargs,
        colors=colors,
        delta_bbox=delta_bbox,
        debug_overlay=debug_overlay,
    )

    checkpoint = None
    resumed = False
    if resume and checkpoint_path.exists():
        checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
        if checkpoint.get("schema") != CHECKPOINT_SCHEMA:
            raise ResumeMismatchError("unsupported timelapse checkpoint schema")
        if checkpoint.get("compatibility") != compatibility:
            raise ResumeMismatchError("timelapse checkpoint does not match session/export contract")
        resumed = True
    elif clean and out_dir.exists():
        shutil.rmtree(out_dir)

    out_dir.mkdir(parents=True, exist_ok=True)

    if checkpoint is None:
        final_ir = session.history.state_at(session.history.cursor)
        render_fn(final_ir, str(palette_source), **final_kwargs)
        expected_final_hash = pixel_sha256(palette_source)
        palette = _palette_from_path(palette_source, colors)
        palette_source.unlink(missing_ok=True)
        journal_path.write_bytes(b"")
        tmp_gif.write_bytes(b"")
        checkpoint = _checkpoint(
            compatibility=compatibility,
            frame_count=0,
            cursor=0,
            gif_offset=0,
            journal_offset=0,
            palette=palette,
            expected_final_pixel_sha256=expected_final_hash,
        )
        _atomic_json(checkpoint_path, checkpoint)
    else:
        palette = [int(v) for v in checkpoint["palette"]]
        expected_final_hash = str(checkpoint["expected_final_pixel_sha256"])
        if checkpoint.get("completed"):
            if not manifest_path.exists():
                raise ResumeMismatchError("completed checkpoint exists but manifest.json is missing")
            if not gif_path.exists():
                if tmp_gif.exists():
                    os.replace(tmp_gif, gif_path)
                else:
                    raise ResumeMismatchError("completed checkpoint has neither final nor temporary GIF")
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            return StreamingTimelapseExport(manifest, manifest_path, gif_path, checkpoint_path, True)
        if not tmp_gif.exists():
            raise ResumeMismatchError("checkpoint exists but timelapse.tmp.gif is missing")
        if not journal_path.exists():
            raise ResumeMismatchError("checkpoint exists but frame journal is missing")
        _truncate(tmp_gif, int(checkpoint["gif_byte_offset"]))
        _truncate(journal_path, int(checkpoint["journal_byte_offset"]))

    committed = int(checkpoint["committed_frame_count"])
    if committed > len(cursors):
        raise ResumeMismatchError("checkpoint frame count exceeds selected cursor count")
    if committed and int(checkpoint["committed_cursor"]) != cursors[committed - 1]:
        raise ResumeMismatchError("checkpoint cursor does not match selected replay frame")

    previous: Image.Image | None = None
    if committed > 0 and delta_bbox:
        cursor = cursors[committed - 1]
        ir = session.history.state_at(cursor)
        kwargs = final_kwargs if cursor == session.history.cursor else render_kwargs
        render_fn(ir, str(staging), **kwargs)
        action = None if cursor == 0 else session.history.actions[cursor - 1]
        info = {
            "frame_index": committed - 1,
            "cursor": cursor,
            "action": None if action is None else action.action,
        }
        if debug_overlay:
            _debug_overlay(staging, info)
        previous = _quantize_path(staging, palette)

    with open(tmp_gif, "r+b") as gif_handle, open(journal_path, "ab") as journal:
        gif_handle.seek(0, os.SEEK_END)
        journal.seek(0, os.SEEK_END)
        for i in range(committed, len(cursors)):
            cursor = cursors[i]
            ir = session.history.state_at(cursor)
            kwargs = final_kwargs if cursor == session.history.cursor else render_kwargs
            render_fn(ir, str(staging), **kwargs)
            action = None if cursor == 0 else session.history.actions[cursor - 1]
            info = {
                "frame_index": i,
                "cursor": cursor,
                "action_seq": None if action is None else action.seq,
                "logical_time": None if action is None else action.logical_time,
                "stage": None if action is None else action.stage,
                "action": None if action is None else action.action,
                "part": None if action is None else action.part,
                "role": None if action is None else action.role,
                "duration_ms": _frame_duration_ms(cursors, i, session),
                "pixel_sha256": pixel_sha256(staging),
            }
            if debug_overlay:
                _debug_overlay(staging, info)
                info["debug_pixel_sha256"] = pixel_sha256(staging)
            current = _quantize_path(staging, palette)
            if i == 0 and gif_handle.tell() == 0:
                _write_global_header(gif_handle, current, loop=loop)
            bbox, next_previous = _write_frame(
                gif_handle,
                current,
                previous,
                duration_ms=info["duration_ms"],
                delta_bbox=delta_bbox,
            )
            current.close()
            if previous is not None:
                previous.close()
            previous = next_previous
            info["gif_bbox"] = list(map(int, bbox))

            gif_handle.flush()
            os.fsync(gif_handle.fileno())
            gif_offset = gif_handle.tell()
            journal.write((json.dumps(info, ensure_ascii=False, sort_keys=True) + "\n").encode("utf-8"))
            journal.flush()
            os.fsync(journal.fileno())
            journal_offset = journal.tell()
            checkpoint = _checkpoint(
                compatibility=compatibility,
                frame_count=i + 1,
                cursor=cursor,
                gif_offset=gif_offset,
                journal_offset=journal_offset,
                palette=palette,
                expected_final_pixel_sha256=expected_final_hash,
            )
            _atomic_json(checkpoint_path, checkpoint)
            if _stop_after_frames is not None and i + 1 >= int(_stop_after_frames):
                raise SimulatedInterruption(f"simulated interruption after {i + 1} committed frames")

        gif_handle.write(b";")
        gif_handle.flush()
        os.fsync(gif_handle.fileno())

    if previous is not None:
        previous.close()
    staging.unlink(missing_ok=True)

    frames = _load_journal(journal_path)
    final_native_match = bool(frames) and frames[-1]["pixel_sha256"] == expected_final_hash
    external_final_match = None
    if expected_final_path is not None:
        external_final_match = pixel_sha256(Path(expected_final_path)) == expected_final_hash

    manifest = {
        "schema": STREAMING_SCHEMA,
        "session": {
            "path": str(session_path),
            "session_id": session.session_id,
            "action_log_sha256": session.action_hash(),
            "state_sha256": session.state_hash(),
            "action_count": len(session.history.actions),
            "cursor": session.history.cursor,
        },
        "export": {
            "mode": mode,
            "every_n": every_n if mode == "every_n" else None,
            "frame_count": len(frames),
            "streaming": True,
            "resume_supported": True,
            "resumed": resumed,
            "delta_bbox": bool(delta_bbox),
            "colors": int(colors),
            "renderer_id": effective_renderer_id,
            "renderer_kwargs": render_kwargs,
            "final_renderer_kwargs": final_kwargs,
            "final_frame_matches_session_state": final_native_match,
            "external_final_matches_session_state": external_final_match,
            "frame_spool_used": False,
        },
        "frames": frames,
        "gif": {"file": gif_path.name, "sha256": sha256_file(tmp_gif)},
    }
    _atomic_json(manifest_path, manifest)
    checkpoint = _checkpoint(
        compatibility=compatibility,
        frame_count=len(frames),
        cursor=cursors[-1],
        gif_offset=tmp_gif.stat().st_size,
        journal_offset=journal_path.stat().st_size,
        palette=palette,
        expected_final_pixel_sha256=expected_final_hash,
        completed=True,
    )
    _atomic_json(checkpoint_path, checkpoint)
    os.replace(tmp_gif, gif_path)
    return StreamingTimelapseExport(manifest, manifest_path, gif_path, checkpoint_path, resumed)
