"""Canonical PNG render of one history cursor, with a manifest binding it to its inputs."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from PIL import Image

from ..core.digest import sha256_file, sha256_obj
from ..inspection import drawing_state_hash
from .pencil import render
from .profile import RenderProfile

RENDER_ARTIFACT_SCHEMA = "img2drawing.render_artifact.v2"


@dataclass(frozen=True)
class RenderArtifact:
    path: Path
    manifest_path: Path
    cursor: int
    png_sha256: str
    pixel_sha256: str
    drawing_state_hash: str
    render_profile_digest: str


def pixel_sha256(path: str | Path) -> str:
    with Image.open(path) as image:
        return hashlib.sha256(image.convert("RGBA").tobytes()).hexdigest()


def rgb_sha256(image: Image.Image) -> str:
    return hashlib.sha256(image.convert("RGB").tobytes()).hexdigest()


def action_log_sha256(history) -> str:
    return sha256_obj([action.to_dict() for action in history.actions])


def render_history_at(history, cursor: int, path: str | Path, profile: RenderProfile) -> RenderArtifact:
    """Render ``history`` at ``cursor`` through ``profile`` and write ``<path>.render.json``."""

    requested = int(cursor)
    if requested < 0 or requested > history.cursor:
        raise ValueError("replay cursor is outside the authoritative history")
    path = Path(path)
    if path.suffix.lower() != ".png":
        raise ValueError("canonical render output must use .png")
    profile.validate_canvas(history.width, history.height)
    before_history = history.to_dict()
    ir = history.state_at(requested)
    state_hash = drawing_state_hash(ir)
    path.parent.mkdir(parents=True, exist_ok=True)
    render(profile.prepared_ir(ir), path, **profile.renderer_kwargs())
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
        "action_log_sha256": action_log_sha256(history),
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


__all__ = [
    "RENDER_ARTIFACT_SCHEMA",
    "RenderArtifact",
    "action_log_sha256",
    "pixel_sha256",
    "render_history_at",
    "rgb_sha256",
]
