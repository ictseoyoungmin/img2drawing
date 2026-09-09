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


def _export_session_timelapse_canonical(
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


def _annotate_backend(result: ReplayExport, *, backend: str, reason: str | None = None) -> ReplayExport:
    """Record the selected execution backend without changing the canonical artifact contract."""
    result.manifest["backend"] = {"selected": backend, "fallback_reason": reason}
    result.manifest_path.write_text(
        json.dumps(result.manifest, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8"
    )
    return result


def _fast_pixel_work(session, cursors: list[int]) -> int:
    profile = session.render_profile
    assert profile is not None
    return (
        len(cursors)
        * profile.canvas_width
        * profile.canvas_height
        * profile.output_scale
        * profile.output_scale
        * profile.supersample
        * profile.supersample
    )


def _rgb_sha256_path(path: Path) -> str:
    import hashlib
    with Image.open(path) as image:
        return hashlib.sha256(image.convert("RGB").tobytes()).hexdigest()


def _materialize_pack_frames(pack_path: Path, frame_dir: Path, cursors: list[int]) -> list[str]:
    from ..provenance.fast_timelapse.delta_pack import iter_frames
    frame_dir.mkdir(parents=True, exist_ok=True)
    files: list[str] = []
    for index, (cursor, image) in enumerate(zip(cursors, iter_frames(pack_path))):
        path = frame_dir / f"frame_{index:04d}_cursor_{cursor:04d}.png"
        try:
            image.save(path)
        finally:
            image.close()
        files.append(path.name)
    return files


def export_session_timelapse(
    session,
    out_dir: str | Path,
    *,
    mode: str = "every_n",
    every_n: int = 4,
    max_pixel_work: int = 20_000_000,
    max_gif_bytes: int = 25_000_000,
    clean: bool = True,
    backend: str = "auto",
    materialize_frames: bool = False,
    cache_dir: str | Path | None = None,
    fps: int = 12,
    rectangle: bool = True,
) -> ReplayExport:
    """Export replay with the v1.0.2 local-first fast engine as the default backend.

    ``backend='auto'`` selects the exact incremental fast path when the action surface is
    eligible and ffmpeg is available. Unsupported semantics or a missing encoder fail closed
    to the preserved v1.0.1 canonical exporter for the *whole export*. ``backend='canonical'``
    forces that legacy-safe path explicitly. Full PNG frame spooling is opt-in in the fast path.
    """
    if backend not in {"auto", "fast", "canonical"}:
        raise ValueError("backend must be 'auto', 'fast', or 'canonical'")
    if mode not in {"action", "every_n"}:
        raise ValueError("vNext replay mode must be 'action' or 'every_n'")
    if backend == "canonical":
        return _annotate_backend(
            _export_session_timelapse_canonical(
                session, out_dir, mode=mode, every_n=every_n,
                max_pixel_work=max_pixel_work, max_gif_bytes=max_gif_bytes, clean=clean,
            ),
            backend="canonical",
        )

    profile = session.render_profile
    if profile is None:
        raise ValueError("checkpoint has no RenderProfile; call migrate_render_profile() explicitly")
    history = session._agent.history
    profile.validate_canvas(history.width, history.height)

    from ..provenance.fast_timelapse.exporter import export_fast_timelapse, sampled_cursors
    from ..provenance.fast_timelapse.frame_source import inspect_fast_path_eligibility
    eligibility = inspect_fast_path_eligibility(history)
    ffmpeg = shutil.which("ffmpeg")
    fallback_reason = None
    if not eligibility.eligible:
        fallback_reason = "; ".join(eligibility.reasons)
    elif ffmpeg is None:
        fallback_reason = "ffmpeg is unavailable"
    if fallback_reason is not None:
        return _annotate_backend(
            _export_session_timelapse_canonical(
                session, out_dir, mode=mode, every_n=every_n,
                max_pixel_work=max_pixel_work, max_gif_bytes=max_gif_bytes, clean=clean,
            ),
            backend="canonical-fallback",
            reason=fallback_reason,
        )

    step = 1 if mode == "action" else int(every_n)
    cursors = sampled_cursors(history.cursor, step)
    pixel_work = _fast_pixel_work(session, cursors)
    if pixel_work > int(max_pixel_work):
        raise ValueError("replay pixel-work budget exceeded")
    if int(max_gif_bytes) < 1:
        raise ValueError("max_gif_bytes must be >= 1")

    output = Path(out_dir)
    output.mkdir(parents=True, exist_ok=True)
    frame_dir = output / "frames"
    if clean:
        if frame_dir.exists():
            shutil.rmtree(frame_dir)
        for name in ("canonical_final.png", "canonical_final.render.json", "replay_manifest.json"):
            (output / name).unlink(missing_ok=True)
    frame_dir.mkdir(parents=True, exist_ok=True)

    before_history = history.to_dict()
    fast = export_fast_timelapse(
        session,
        output,
        every_n=step,
        fps=int(fps),
        supersample=profile.supersample,
        cache_dir=cache_dir,
        gif=True,
        clean=clean,
        rectangle=bool(rectangle),
        verify_final=False,
    )
    summary = fast.summary
    frame_hashes = list(summary.get("frame_rgb_sha256", []))
    if len(frame_hashes) != len(cursors):
        raise RuntimeError("fast replay did not report one frame hash per sampled cursor")

    final_path = output / "canonical_final.png"
    final_artifact = _render_at(history, history.cursor, final_path, profile)
    final_rgb = _rgb_sha256_path(final_path)
    final_frame_pixel_match = frame_hashes[-1] == final_rgb
    if not final_frame_pixel_match:
        raise RuntimeError("fast replay final frame does not match independently rendered final PNG")

    materialized = _materialize_pack_frames(fast.pack_path, frame_dir, cursors) if materialize_frames else []
    frame_duration = max(1, int(round(1000.0 / float(fps))))
    frames: list[dict[str, Any]] = []
    for index, cursor in enumerate(cursors):
        action = None if cursor == 0 else history.actions[cursor - 1]
        frames.append({
            "frame_index": index,
            "cursor": cursor,
            "action_seq": None if action is None else action.seq,
            "action": None if action is None else action.action,
            "part": None if action is None else action.part,
            "role": None if action is None else action.role,
            "duration_ms": frame_duration,
            "file": None if not materialize_frames else f"frames/{materialized[index]}",
            "png_sha256": None,
            "pixel_sha256": frame_hashes[index],
            "pixel_hash_mode": "RGB",
            "drawing_state_hash": None,
        })

    gif_path = fast.gif_path
    if gif_path is None:
        raise RuntimeError("fast GIF backend did not produce an artifact")
    gif_bytes = gif_path.stat().st_size
    if gif_bytes > int(max_gif_bytes):
        raise ValueError("replay GIF size budget exceeded")
    gif_max_error, gif_mean_error = _gif_error(gif_path, final_path)
    tolerance = {"max_channel_error": 32, "mean_channel_error": 4.0}
    gif_within_tolerance = (
        gif_max_error <= tolerance["max_channel_error"]
        and gif_mean_error <= tolerance["mean_channel_error"]
    )
    if not gif_within_tolerance:
        raise RuntimeError("encoded GIF final frame exceeds documented fast-backend color tolerance")
    if history.to_dict() != before_history:
        raise RuntimeError("replay export mutated authoritative history")

    manifest = {
        "schema": REPLAY_EXPORT_SCHEMA,
        "session_id": session.session_id,
        "backend": {
            "selected": "fast",
            "engine": "local-first-exact-delta-pack-v1",
            "canonical_fallback_preserved": True,
            "materialize_frames": bool(materialize_frames),
            "rectangle_gif": bool(rectangle),
            "fps": int(fps),
            "cache_state": summary["performance"]["cache_state"],
        },
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
            "region_action_frame_policy": "unsupported region actions use whole-export canonical fallback",
        },
        "timing": {
            "policy": "constant-fps-fast-backend",
            "fps": int(fps),
            "frame_ms": frame_duration,
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
            "rgb_sha256": final_rgb,
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
        "fast_summary": summary,
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
