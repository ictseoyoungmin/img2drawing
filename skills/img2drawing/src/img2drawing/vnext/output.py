"""Canonical vNext PNG, cursor replay, and GIF export from one history/profile."""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from PIL import Image, ImageChops

from ..core.session import sha256_file, sha256_obj
from ..inspection import drawing_state_hash
from ..provenance.timelapse import pixel_sha256, save_gif, select_cursors
from ..render.pillow_pencil_contact import render
from .render_profile import RenderProfile


RENDER_ARTIFACT_SCHEMA = "img2drawing.vnext.render_artifact.v1"
REPLAY_EXPORT_SCHEMA = "img2drawing.vnext.replay_export.v1"


@dataclass(frozen=True)
class RenderArtifact:
    path: Path
    manifest_path: Path
    cursor: int
    png_sha256: str
    pixel_sha256: str
    drawing_state_hash: str
    render_profile_digest: str


@dataclass(frozen=True)
class ReplayExport:
    manifest: dict[str, Any]
    manifest_path: Path
    gif_path: Path
    final_path: Path
    frame_dir: Path


def _action_hash(history) -> str:
    return sha256_obj([action.to_dict() for action in history.actions])


def _render_at(
    history,
    cursor: int,
    path: Path,
    profile: RenderProfile,
) -> RenderArtifact:
    requested = int(cursor)
    if requested < 0 or requested > history.cursor:
        raise ValueError("replay cursor is outside the authoritative history")
    if path.suffix.lower() != ".png":
        raise ValueError("canonical render output must use .png")
    profile.validate_canvas(history.width, history.height)
    before_history = history.to_dict()
    ir = history.state_at(requested)
    state_hash = drawing_state_hash(ir)
    prepared = profile.prepared_ir(ir)
    path.parent.mkdir(parents=True, exist_ok=True)
    render(prepared, path, **profile.renderer_kwargs())
    if history.to_dict() != before_history:
        raise RuntimeError("renderer mutated authoritative history")
    with Image.open(path) as image:
        if image.mode != profile.png_mode:
            raise ValueError("renderer output mode does not match RenderProfile")
        expected_size = (
            profile.canvas_width * profile.output_scale,
            profile.canvas_height * profile.output_scale,
        )
        if image.size != expected_size:
            raise ValueError("renderer output size does not match RenderProfile")
    manifest = {
        "schema": RENDER_ARTIFACT_SCHEMA,
        "cursor": requested,
        "drawing_state_hash": state_hash,
        "action_log_sha256": _action_hash(history),
        "render_profile": profile.to_dict(),
        "render_profile_digest": profile.digest(),
        "artifact": {
            "file": path.name,
            "png_sha256": sha256_file(path),
            "pixel_sha256": pixel_sha256(path),
        },
    }
    manifest_path = path.with_suffix(".render.json")
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8"
    )
    return RenderArtifact(
        path=path,
        manifest_path=manifest_path,
        cursor=requested,
        png_sha256=manifest["artifact"]["png_sha256"],
        pixel_sha256=manifest["artifact"]["pixel_sha256"],
        drawing_state_hash=state_hash,
        render_profile_digest=profile.digest(),
    )


def render_session_at(session, cursor: int, out: str | Path) -> RenderArtifact:
    profile = session.render_profile
    if profile is None:
        raise ValueError("checkpoint has no RenderProfile; call migrate_render_profile() explicitly")
    return _render_at(session._agent.history, cursor, Path(out), profile)


def _duration_ms(history, cursor: int, *, final: bool) -> int:
    if final:
        return 900
    if cursor == 0:
        return 180
    action = history.actions[cursor - 1]
    if action.action in {"region.fill", "region.replace"}:
        return 320
    if action.action in {
        "stroke.delete",
        "stroke.soft_lift",
        "stroke.segment_replace",
        "stroke.segment_soft_lift",
    }:
        return 180
    return 120


def _gif_error(gif_path: Path, final_png: Path) -> tuple[int, float]:
    with Image.open(gif_path) as gif:
        gif.seek(gif.n_frames - 1)
        actual = gif.convert("RGB")
    with Image.open(final_png) as png:
        expected = png.convert("RGB")
    difference = ImageChops.difference(actual, expected)
    extrema = difference.getextrema()
    max_error = max(channel[1] for channel in extrema)
    histogram = difference.histogram()
    total = sum(value * count for value in range(256) for count in histogram[value::256])
    mean_error = total / float(expected.width * expected.height * 3)
    return int(max_error), float(mean_error)


def export_session_timelapse(
    session,
    out_dir: str | Path,
    *,
    mode: str = "every_n",
    every_n: int = 4,
    max_pixel_work: int = 20_000_000,
    max_gif_bytes: int = 25_000_000,
    clean: bool = True,
) -> ReplayExport:
    profile = session.render_profile
    if profile is None:
        raise ValueError("checkpoint has no RenderProfile; call migrate_render_profile() explicitly")
    if mode not in {"action", "every_n"}:
        raise ValueError("vNext replay mode must be 'action' or 'every_n'")
    history = session._agent.history
    profile.validate_canvas(history.width, history.height)
    cursors = select_cursors(session._agent, mode, every_n=every_n)
    pixel_work = (
        len(cursors)
        * profile.canvas_width
        * profile.canvas_height
        * profile.output_scale
        * profile.output_scale
        * profile.supersample
        * profile.supersample
    )
    if pixel_work > int(max_pixel_work):
        raise ValueError("replay pixel-work budget exceeded")
    if int(max_gif_bytes) < 1:
        raise ValueError("max_gif_bytes must be >= 1")
    output = Path(out_dir)
    if clean and output.exists():
        shutil.rmtree(output)
    frame_dir = output / "frames"
    frame_dir.mkdir(parents=True, exist_ok=True)
    before_history = history.to_dict()
    frames: list[dict[str, Any]] = []
    frame_paths: list[Path] = []
    durations: list[int] = []
    for index, cursor in enumerate(cursors):
        path = frame_dir / f"frame_{index:04d}_cursor_{cursor:04d}.png"
        artifact = _render_at(history, cursor, path, profile)
        action = None if cursor == 0 else history.actions[cursor - 1]
        duration = _duration_ms(history, cursor, final=index == len(cursors) - 1)
        frames.append(
            {
                "frame_index": index,
                "cursor": cursor,
                "action_seq": None if action is None else action.seq,
                "action": None if action is None else action.action,
                "part": None if action is None else action.part,
                "role": None if action is None else action.role,
                "duration_ms": duration,
                "file": path.relative_to(output).as_posix(),
                "png_sha256": artifact.png_sha256,
                "pixel_sha256": artifact.pixel_sha256,
                "drawing_state_hash": artifact.drawing_state_hash,
            }
        )
        frame_paths.append(path)
        durations.append(duration)

    final_path = output / "canonical_final.png"
    final_artifact = _render_at(history, history.cursor, final_path, profile)
    final_frame_pixel_match = frames[-1]["pixel_sha256"] == final_artifact.pixel_sha256
    if not final_frame_pixel_match:
        raise RuntimeError("final replay frame does not match independently rendered final PNG")
    gif_path = output / "timelapse.gif"
    save_gif(
        frame_paths,
        durations,
        gif_path,
        colors=profile.gif_palette_colors,
        loop=profile.gif_loop,
        disposal=profile.gif_disposal,
    )
    gif_bytes = gif_path.stat().st_size
    if gif_bytes > int(max_gif_bytes):
        raise ValueError("replay GIF size budget exceeded")
    gif_max_error, gif_mean_error = _gif_error(gif_path, final_path)
    tolerance = {"max_channel_error": 24, "mean_channel_error": 2.0}
    gif_within_tolerance = (
        gif_max_error <= tolerance["max_channel_error"]
        and gif_mean_error <= tolerance["mean_channel_error"]
    )
    if not gif_within_tolerance:
        raise RuntimeError("encoded GIF final frame exceeds documented color tolerance")
    if history.to_dict() != before_history:
        raise RuntimeError("replay export mutated authoritative history")
    manifest = {
        "schema": REPLAY_EXPORT_SCHEMA,
        "session_id": session.session_id,
        "history": {
            "action_log_sha256": _action_hash(history),
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
            "region_action_frame_policy": "one authored region action produces one cursor/frame",
        },
        "timing": {
            "initial_ms": 180,
            "ordinary_action_ms": 120,
            "edit_action_ms": 180,
            "region_action_ms": 320,
            "final_hold_ms": 900,
        },
        "budget": {
            "max_pixel_work": int(max_pixel_work),
            "pixel_work": pixel_work,
            "max_gif_bytes": int(max_gif_bytes),
            "gif_bytes": gif_bytes,
        },
        "frames": frames,
        "final": {
            "file": final_path.name,
            "png_sha256": final_artifact.png_sha256,
            "pixel_sha256": final_artifact.pixel_sha256,
            "last_frame_pixel_match": final_frame_pixel_match,
        },
        "gif": {
            "file": gif_path.name,
            "sha256": sha256_file(gif_path),
            "bytes": gif_bytes,
            "final_frame_max_channel_error": gif_max_error,
            "final_frame_mean_channel_error": gif_mean_error,
            "tolerance": tolerance,
            "within_tolerance": gif_within_tolerance,
        },
    }
    manifest_path = output / "replay_manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8"
    )
    return ReplayExport(manifest, manifest_path, gif_path, final_path, frame_dir)


__all__ = [
    "RENDER_ARTIFACT_SCHEMA",
    "REPLAY_EXPORT_SCHEMA",
    "RenderArtifact",
    "ReplayExport",
    "export_session_timelapse",
    "render_session_at",
]
