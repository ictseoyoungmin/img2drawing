from __future__ import annotations

from typing import Any

from ..render.renderer_dispatch import render_by_profile_authority

_BOUND_FLAG = "_img2drawing_renderer_registry_bound"


def bind_vnext_renderer_runtime() -> None:
    """Bind existing vNext render hooks without widening the public worker API.

    v1.0.3 keeps the large stage-free session implementation stable while renderer
    identity becomes profile-owned.  The bridge only redirects internal render hooks
    and makes checkpoint renderer headers follow an existing RenderProfile.  A
    profile-less historical session remains v9 and therefore preserves old replay.
    """
    from . import output as output_module
    from . import session as session_module

    session_cls = session_module.DrawingSession
    if getattr(session_cls, _BOUND_FLAG, False):
        return

    # Existing vNext call sites can keep their signatures.  Prepared IR carries only
    # the selected profile identity, and the dispatcher resolves the frozen backend.
    session_module.render = render_by_profile_authority
    output_module.render = render_by_profile_authority

    original_checkpoint_payload = session_cls._checkpoint_payload

    def _checkpoint_payload(self) -> dict[str, Any]:
        payload = original_checkpoint_payload(self)
        profile = self.render_profile
        if profile is not None:
            payload["renderer"] = {
                "id": profile.renderer_id,
                "version": profile.renderer_version,
                "seed_domain": profile.seed_domain,
            }
        return payload

    session_cls._checkpoint_payload = _checkpoint_payload
    setattr(session_cls, _BOUND_FLAG, True)


__all__ = ["bind_vnext_renderer_runtime"]
