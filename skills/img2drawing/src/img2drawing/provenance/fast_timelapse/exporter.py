from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from PIL import Image

from ..._version import __version__
from ...render.renderer_registry import resolve_renderer
from ...vnext.session import DrawingSession
from .delta_pack import DeltaPackWriter, read_info
from .frame_source import (
    CanonicalFrameSource,
    make_frame_source_from_vnext_session,
)
from .gif_backend import encode_gif
from .persistent_patch_cache import PersistentPatchCacheRenderer

FAST_TIMELAPSE_SCHEMA = "img2drawing.fast-timelapse.export.v1"


@dataclass(frozen=True)
class FastTimelapseExport:
    """Result of an opt-in fast timelapse export."""

    summary: dict[str, Any]
    summary_path: Path
    gif_path: Path | None
    pack_path: Path
    cache_dir: Path


def sampled_cursors(final_cursor: int, every_n: int) -> list[int]:
    if int(every_n) != every_n or every_n < 1:
        raise ValueError("every_n must be a positive integer")
    out = list(range(0, int(final_cursor) + 1, int(every_n)))
    if not out or out[-1] != int(final_cursor):
        out.append(int(final_cursor))
    return out


def _rgb_hash(image: Image.Image) -> str:
    return hashlib.sha256(image.convert("RGB").tobytes()).hexdigest()


def _clean_outputs(out_dir: Path) -> None:
    """Remove generated artifacts while preserving the persistent cache directory."""
    for name in ("frames.idp", "frames.idp.partial", "palette.png", "timelapse.gif", "summary.json"):
        path = out_dir / name
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink(missing_ok=True)


def _canonical_final_hash(session: DrawingSession, supersample: int) -> tuple[str, float]:
    profile = session.render_profile
    if profile is None:
        raise ValueError("session has no render profile")
    t0 = time.perf_counter()
    with tempfile.TemporaryDirectory(prefix="img2drawing-fast-final-check-") as tmp:
        path = Path(tmp) / "final.png"
        ir = session._agent.history.state_at(session.history_cursor)
        prepared = profile.prepared_ir(ir)
        resolve_renderer(profile.renderer_id, profile.renderer_version).render(
            prepared,
            path,
            background=tuple(profile.background_rgba),
            scale=int(profile.output_scale),
            supersample=int(supersample),
            graphite=tuple(profile.graphite_rgb),
            contact_profile=None,
        )
        with Image.open(path) as image:
            digest = _rgb_hash(image)
    return digest, time.perf_counter() - t0


def _cache_state(persistent: dict[str, Any], renderer_stats: dict[str, Any]) -> str:
    hits = int(persistent.get("disk_hits", 0))
    misses = int(persistent.get("disk_misses", 0))
    builds = int(renderer_stats.get("cache_misses", 0))
    if hits > 0 and misses == 0 and builds == 0:
        return "warm"
    if hits == 0 and builds > 0:
        return "cold"
    if hits == 0 and builds == 0:
        return "not-applicable"
    return "mixed"


def export_fast_timelapse(
    session_path: str | Path | DrawingSession,
    out_dir: str | Path,
    *,
    every_n: int = 2,
    fps: int = 12,
    supersample: int | None = None,
    cache_dir: str | Path | None = None,
    gif: bool = True,
    clean: bool = True,
    rectangle: bool = True,
    verify_final: bool = False,
) -> FastTimelapseExport:
    """Export an exact every-N timelapse using the local-first fast path.

    The API is deliberately opt-in and does not replace ``export_timelapse``.
    Unsupported history semantics fail closed to the canonical P9 frame source.
    Persistent caches are disposable acceleration state, never source of truth.
    """

    supplied_session = session_path if isinstance(session_path, DrawingSession) else None
    session_path = supplied_session.checkpoint_path if supplied_session is not None else Path(session_path)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    cache_root = Path(cache_dir) if cache_dir is not None else out_dir / ".cache"
    cache_root.mkdir(parents=True, exist_ok=True)
    if clean:
        _clean_outputs(out_dir)

    if int(fps) != fps or fps < 1:
        raise ValueError("fps must be a positive integer")

    session = supplied_session if supplied_session is not None else DrawingSession.resume(session_path)
    profile = session.render_profile
    if profile is None:
        raise ValueError("session has no render profile")
    effective_ss = int(profile.supersample if supersample is None else supersample)
    cursors = sampled_cursors(session.history_cursor, every_n)

    source = make_frame_source_from_vnext_session(
        session,
        supersample=effective_ss,
        renderer_cls=PersistentPatchCacheRenderer,
        renderer_kwargs={"persistent_cache_dir": cache_root / "patches"},
    )
    source_kind = "canonical-fallback" if isinstance(source, CanonicalFrameSource) else "fast"
    fallback_reasons = list(getattr(source, "reasons", ()))
    out_size = (int(session.width * profile.output_scale), int(session.height * profile.output_scale))
    pack_path = out_dir / "frames.idp"

    final_frame_hash: str | None = None
    frame_rgb_sha256: list[str] = []
    t_render = time.perf_counter()
    with DeltaPackWriter(
        pack_path,
        width=out_size[0],
        height=out_size[1],
        frame_count=len(cursors),
        level=1,
    ) as writer:
        for index, cursor in enumerate(cursors):
            info = source.advance_to(cursor)
            frame = source.image()
            try:
                rects = [(0, 0, frame.width, frame.height)] if index == 0 else info["output_regions"]
                writer.write_frame(frame, rects)
                frame_hash = _rgb_hash(frame)
                frame_rgb_sha256.append(frame_hash)
                if index == len(cursors) - 1:
                    final_frame_hash = frame_hash
            finally:
                frame.close()
    render_pack_sec = time.perf_counter() - t_render

    source_stats = dict(getattr(source, "stats", {}))
    renderer = getattr(source, "renderer", None)
    renderer_stats = dict(getattr(renderer, "stats", {})) if renderer is not None else {}
    persistent = dict(getattr(renderer, "persistent", {})) if renderer is not None else {}
    source.close()

    encode: dict[str, Any] | None = None
    if gif:
        encode = encode_gif(
            pack_path,
            out_dir,
            int(fps),
            palette_cache_dir=cache_root / "palettes",
            rectangle=bool(rectangle),
        )

    verification: dict[str, Any] = {"checked": False}
    if verify_final:
        expected_hash, verify_sec = _canonical_final_hash(session, effective_ss)
        verification = {
            "checked": True,
            "canonical_rgb_sha256": expected_hash,
            "fast_rgb_sha256": final_frame_hash,
            "pixel_exact": final_frame_hash == expected_hash,
            "sec": verify_sec,
        }
        if not verification["pixel_exact"]:
            raise RuntimeError("fast timelapse final frame does not match canonical renderer")

    pack_info = read_info(pack_path)
    encode_sec = 0.0 if encode is None else float(encode["total_encode_sec"])
    summary: dict[str, Any] = {
        "schema": FAST_TIMELAPSE_SCHEMA,
        "img2drawing_version": __version__,
        "session": str(session_path),
        "actions": session.history_cursor,
        "sampling": {"mode": "every_n", "every_n": int(every_n), "frames": len(cursors), "cursors": cursors},
        "frame_rgb_sha256": frame_rgb_sha256,
        "render": {
            "fps": int(fps),
            "supersample": effective_ss,
            "output_size": list(out_size),
            "source": source_kind,
            "fallback_reasons": fallback_reasons,
        },
        "performance": {
            "render_pack_sec": render_pack_sec,
            "encode_sec": encode_sec,
            "pipeline_sec": render_pack_sec + encode_sec,
            "cache_state": _cache_state(persistent, renderer_stats),
        },
        "pack": {
            "path": str(pack_path),
            "bytes": pack_path.stat().st_size,
            "patches": pack_info.patches_total,
            "compressed_patch_bytes": pack_info.compressed_patch_bytes,
        },
        "frame_source_stats": source_stats,
        "renderer_stats": renderer_stats,
        "persistent_patch_cache": persistent,
        "encode": encode,
        "verification": verification,
    }
    summary_path = out_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return FastTimelapseExport(
        summary=summary,
        summary_path=summary_path,
        gif_path=None if encode is None else Path(encode["gif"]),
        pack_path=pack_path,
        cache_dir=cache_root,
    )
