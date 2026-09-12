from __future__ import annotations

from typing import Any

from .renderer_registry import resolve_renderer

RENDER_AUTHORITY_METADATA_KEY = "_img2drawing_renderer_authority"
_HISTORICAL_DEFAULT = ("pillow-pencil-contact-v9", "1")


def renderer_identity_from_ir(ir) -> tuple[str, str]:
    """Read render-only authority stamped by RenderProfile.

    Authoritative drawing geometry/history never depends on this metadata.  Missing
    authority intentionally falls back to historical v9 so profile-less legacy paths
    preserve their published behavior.
    """
    metadata = getattr(ir, "metadata", None)
    if isinstance(metadata, dict):
        raw = metadata.get(RENDER_AUTHORITY_METADATA_KEY)
        if isinstance(raw, dict):
            renderer_id = str(raw.get("id", "")).strip()
            renderer_version = str(raw.get("version", "")).strip()
            if renderer_id and renderer_version:
                return renderer_id, renderer_version
    return _HISTORICAL_DEFAULT


def render_by_profile_authority(ir, path, *args: Any, **kwargs: Any) -> None:
    renderer_id, renderer_version = renderer_identity_from_ir(ir)
    resolve_renderer(renderer_id, renderer_version).render(ir, path, *args, **kwargs)


__all__ = [
    "RENDER_AUTHORITY_METADATA_KEY",
    "renderer_identity_from_ir",
    "render_by_profile_authority",
]
