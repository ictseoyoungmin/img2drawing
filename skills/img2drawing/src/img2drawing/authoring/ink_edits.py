"""Explicit, atomic ink edits in the same DrawingSession history."""
from __future__ import annotations

from pathlib import Path

from ..core.action import AgentDrawingSession
from ..core.digest import sha256_obj
from ..core.material import InkAction
from ..render.artifact import render_history_at


def _validated(session, actions):
    actions = tuple(actions)
    if not 1 <= len(actions) <= 256 or any(not isinstance(a, InkAction) for a in actions):
        raise ValueError("expected 1–256 typed InkAction records")
    for action in actions:
        session._validate_ink_action(action)
    return actions


def _digest(actions):
    return sha256_obj([a.to_dict() for a in actions])


def apply_ink_actions(session, actions, *, expected_cursor=None, expected_state_hash=None,
                      expected_action_digest=None, expected_profile_digest=None):
    """Commit a typed batch atomically, optionally binding to an exact preview."""
    with session._lock:
        if expected_cursor is not None and session.history_cursor != expected_cursor:
            raise ValueError("stale ink edit cursor")
        if expected_state_hash is not None and session.drawing_state_hash() != expected_state_hash:
            raise ValueError("stale ink edit state")
        if expected_profile_digest is not None and session._require_render_profile().digest() != expected_profile_digest:
            raise ValueError("stale ink edit profile")
        actions = _validated(session, actions)
        if expected_action_digest is not None and _digest(actions) != expected_action_digest:
            raise ValueError("ink action proposal differs from preview")
        session._commit(actions)
        return tuple(a.action_id for a in actions)


def preview_ink_actions(session, actions, out):
    """Render prospective typed actions without mutating session or checkpoint."""
    path = Path(out)
    if path.suffix.lower() != ".png" or path.exists() or path.with_suffix(".render.json").exists():
        raise ValueError("preview requires a new PNG and manifest path")
    with session._lock:
        actions = _validated(session, actions)
        cursor = session.history_cursor
        state = session.drawing_state_hash()
        profile = session._require_render_profile()
        clone = AgentDrawingSession.from_dict(session._agent.to_dict())
        clone.execute_many_atomic(actions, label="prospective ink edit")
        artifact = render_history_at(clone.history, clone.history.cursor, path, profile)
        return {"preview_only": True, "base_cursor": cursor, "base_state_hash": state,
                "profile_digest": profile.digest(), "action_digest": _digest(actions),
                "prospective_state_hash": artifact.drawing_state_hash,
                "pixel_sha256": artifact.pixel_sha256,
                "action_ids": [a.action_id for a in actions]}
