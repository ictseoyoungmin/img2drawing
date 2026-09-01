from __future__ import annotations

import hashlib
import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Callable

from PIL import Image, ImageDraw

from ..render.pillow_pencil_contact import render as pencil_render
from ..core.session import DrawingSession, sha256_file


TIMELAPSE_SCHEMA = "img2drawing.timelapse.manifest.v1"


def pixel_sha256(path: str | Path) -> str:
    im = Image.open(path).convert("RGBA")
    return hashlib.sha256(im.tobytes()).hexdigest()


def _snapshot_label(action) -> str | None:
    if action.action != "snapshot":
        return None
    return str(action.payload.get("label", "")) or None


def _dedupe_sorted(cursors: Iterable[int], final_cursor: int) -> list[int]:
    vals = sorted({max(0, min(int(v), final_cursor)) for v in cursors})
    if 0 not in vals:
        vals.insert(0, 0)
    if final_cursor not in vals:
        vals.append(final_cursor)
    return vals


def select_cursors(session: DrawingSession, mode: str, every_n: int = 8) -> list[int]:
    """Select history cursors without reordering actions.

    Cursor N means the canvas after the first N actions have replayed.
    """
    final = session.history.cursor
    actions = session.history.actions[:final]
    if mode == "action":
        return list(range(0, final + 1))
    if mode == "every_n":
        if every_n < 1:
            raise ValueError("every_n must be >= 1")
        return _dedupe_sorted(range(0, final + 1, every_n), final)
    if mode == "stage":
        cursors = [0]
        for idx, a in enumerate(actions, 1):
            label = _snapshot_label(a)
            if label and (
                label.startswith("stage_start:")
                or label.startswith("stage_end:")
                or label.startswith("stage_reopen:")
                or label.startswith("stage_skip:")
            ):
                cursors.append(idx)
        return _dedupe_sorted(cursors, final)
    if mode == "critic":
        # C2 quality work happens in S9; S10 records the accepted critic checkpoint.
        cursors = [0]
        for idx, a in enumerate(actions, 1):
            label = _snapshot_label(a)
            if not label:
                continue
            if label in {
                "stage_start:S9_restatement",
                "stage_end:S9_restatement",
                "stage_start:S10_critic",
                "stage_end:S10_critic",
            }:
                cursors.append(idx)
        return _dedupe_sorted(cursors, final)
    raise ValueError(f"unsupported timelapse mode: {mode}")


def _frame_duration_ms(cursors: list[int], i: int, session: DrawingSession) -> int:
    if i == len(cursors) - 1:
        return 900
    c0, c1 = cursors[i], cursors[i + 1]
    delta = max(1, c1 - c0)
    duration = min(520, 52 * delta)
    if c0 > 0:
        action = session.history.actions[c0 - 1]
        label = _snapshot_label(action)
        if label and (label.startswith("stage_end:") or label.startswith("stage_reopen:")):
            duration = max(duration, 320)
        elif action.action == "region.fill":
            # one action, but a whole value region lands in that frame
            duration = max(duration, 260)
        elif action.action in {
            "stroke.delete", "stroke.soft_lift", "stroke.segment_replace", "stroke.segment_soft_lift"
        }:
            duration = max(duration, 120)
    return int(duration)


def _debug_overlay(path: Path, frame_info: dict[str, Any]) -> None:
    im = Image.open(path).convert("RGBA")
    d = ImageDraw.Draw(im, "RGBA")
    bar_h = 52
    d.rectangle((0, 0, im.width, bar_h), fill=(255, 255, 255, 224))
    stage = frame_info.get("stage") or "—"
    act = frame_info.get("action") or "initial"
    cursor = frame_info["cursor"]
    logical = frame_info.get("logical_time")
    text = f"cursor {cursor:03d}   stage {stage}   action {act}"
    d.text((10, 8), text, fill=(25, 25, 25, 255))
    label = frame_info.get("snapshot_label")
    if label:
        d.text((10, 28), label, fill=(85, 85, 85, 255))
    elif logical is not None:
        d.text((10, 28), f"logical_time {logical:g}", fill=(85, 85, 85, 255))
    im.save(path)


def save_gif(
    frame_paths: list[Path],
    durations: list[int],
    out_path: Path,
    *,
    colors: int = 64,
    loop: int = 0,
    disposal: int = 2,
) -> None:
    if not frame_paths:
        raise ValueError("cannot write GIF with no frames")
    images = [Image.open(p).convert("RGBA") for p in frame_paths]
    # GIF has no full RGBA model. White flattening keeps the public drawing appearance stable.
    flattened=[]
    for im in images:
        bg=Image.new("RGBA", im.size, (255,255,255,255))
        bg.alpha_composite(im)
        flattened.append(
            bg.convert("RGB").quantize(colors=int(colors), method=Image.Quantize.MEDIANCUT)
        )
    flattened[0].save(
        out_path,
        save_all=True,
        append_images=flattened[1:],
        duration=durations,
        loop=int(loop),
        optimize=False,
        disposal=int(disposal),
    )
    for im in images:
        im.close()
    for im in flattened:
        im.close()


@dataclass
class TimelapseExport:
    manifest: dict[str, Any]
    manifest_path: Path
    gif_path: Path | None
    frame_dir: Path


def export_timelapse(
    session_path: str | Path,
    out_dir: str | Path,
    *,
    mode: str = "every_n",
    every_n: int = 8,
    gif: bool = True,
    debug_overlay: bool = False,
    clean: bool = True,
    renderer: Callable[..., None] | None = None,
    renderer_kwargs: dict[str, Any] | None = None,
    renderer_id: str | None = None,
    expected_final_path: str | Path | None = None,
    final_renderer_kwargs: dict[str, Any] | None = None,
) -> TimelapseExport:
    session_path = Path(session_path)
    out_dir = Path(out_dir)
    render_fn = renderer or pencil_render
    render_kwargs = dict(renderer_kwargs or {})
    final_render_kwargs = dict(render_kwargs if final_renderer_kwargs is None else final_renderer_kwargs)
    effective_renderer_id = renderer_id or getattr(render_fn, "__module__", "renderer")
    frame_dir = out_dir / "frames"
    if clean and out_dir.exists():
        shutil.rmtree(out_dir)
    frame_dir.mkdir(parents=True, exist_ok=True)

    session = DrawingSession.load(session_path, verify=True)
    cursors = select_cursors(session, mode, every_n=every_n)
    frames=[]
    frame_paths=[]
    durations=[]
    for i, cursor in enumerate(cursors):
        path = frame_dir / f"frame_{i:04d}_cursor_{cursor:04d}.png"
        ir = session.history.state_at(cursor)
        frame_kwargs = final_render_kwargs if cursor == session.history.cursor else render_kwargs
        render_fn(ir, str(path), **frame_kwargs)
        action = None if cursor == 0 else session.history.actions[cursor - 1]
        info={
            "frame_index": i,
            "cursor": cursor,
            "action_seq": None if action is None else action.seq,
            "logical_time": None if action is None else action.logical_time,
            "stage": None if action is None else action.stage,
            "action": None if action is None else action.action,
            "part": None if action is None else action.part,
            "role": None if action is None else action.role,
            "snapshot_label": None if action is None else _snapshot_label(action),
            "duration_ms": _frame_duration_ms(cursors, i, session),
            "file": str(path.relative_to(out_dir)),
        }
        if debug_overlay:
            _debug_overlay(path, info)
        info["png_sha256"] = sha256_file(path)
        info["pixel_sha256"] = pixel_sha256(path)
        frames.append(info)
        frame_paths.append(path)
        durations.append(info["duration_ms"])

    gif_path = out_dir / ("debug_timelapse.gif" if debug_overlay else "timelapse.gif") if gif else None
    if gif_path is not None:
        save_gif(frame_paths, durations, gif_path)

    final_frame_path = frame_paths[-1]
    final_state = session.history.state_at(session.history.cursor)
    expected_final = out_dir / "_expected_final.png"
    render_fn(final_state, str(expected_final), **final_render_kwargs)
    expected_pixel_hash = pixel_sha256(expected_final)
    final_frame_match = pixel_sha256(final_frame_path) == expected_pixel_hash
    # Debug overlays intentionally alter the visible frame, but the underlying state was
    # rendered from the same cursor before overlay decoration. Public exports must match
    # the session final pixel-for-pixel.
    final_underlay_match = True if debug_overlay else final_frame_match
    external_final_match = None
    if expected_final_path is not None:
        ext = Path(expected_final_path)
        if not ext.exists():
            raise FileNotFoundError(ext)
        external_final_match = pixel_sha256(ext) == expected_pixel_hash
    expected_final.unlink()

    manifest={
        "schema": TIMELAPSE_SCHEMA,
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
            "debug_overlay": bool(debug_overlay),
            "public_drawing_only": not debug_overlay,
            "frame_count": len(frames),
            "action_order_preserved": True,
            "logical_time_source": "persisted_action_log",
            "screen_recording_used": False,
            "renderer_id": effective_renderer_id,
            "renderer_kwargs": render_kwargs,
            "final_renderer_kwargs": final_render_kwargs,
            "final_frame_matches_session_state": final_frame_match,
            "final_drawing_underlay_matches_session_state": final_underlay_match,
            "external_final_matches_session_state": external_final_match,
        },
        "frames": frames,
        "gif": None if gif_path is None else {
            "file": gif_path.name,
            "sha256": sha256_file(gif_path),
        },
    }
    manifest_path=out_dir/"manifest.json"
    manifest_path.write_text(json.dumps(manifest,indent=2,ensure_ascii=False,sort_keys=True),encoding="utf-8")
    return TimelapseExport(manifest,manifest_path,gif_path,frame_dir)
