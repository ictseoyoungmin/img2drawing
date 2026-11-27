"""Guarded, atomic edits and transforms across authored drawing materials.

Proposals are transient receipts over the one authoritative action history.
Existing stroke-only and ink-only helpers retain their original policies.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, dataclass, replace
import math
from pathlib import Path

from ..core.action import AgentDrawingSession, DrawingAction, _stroke_from_action
from ..core.digest import sha256_obj
from ..core.material import InkAction, InkArea, InkPath, Screentone
from ..render.artifact import render_history_at
from .ink_edits import _ids, _matrix
from .stroke_edits import StrokeEdit, _actions as _stroke_actions


def _action_digest(actions):
    return sha256_obj([a.to_dict() if isinstance(a, InkAction) else asdict(a)
                       for a in actions])


def _typed_actions(actions):
    actions = tuple(actions)
    if not 1 <= len(actions) <= 256 or any(
            not isinstance(a, (DrawingAction, InkAction)) for a in actions):
        raise ValueError("expected 1–256 typed DrawingAction or InkAction records")
    return actions


@dataclass(frozen=True)
class ElementEditProposal:
    """Detached action batch bound to its exact drawing and render profile.

The receipt fields are immutable. Nested legacy DrawingAction dictionaries
are detached, and their digest is rechecked before preview or application.
"""
    actions: tuple[DrawingAction | InkAction, ...]
    base_cursor: int
    base_state_hash: str
    profile_digest: str
    action_digest: str

    def __post_init__(self):
        object.__setattr__(self, "actions", deepcopy(_typed_actions(self.actions)))
        if type(self.base_cursor) is not int or self.base_cursor < 0:
            raise ValueError("proposal requires a nonnegative history cursor")
        for name in ("base_state_hash", "profile_digest", "action_digest"):
            value = getattr(self, name)
            if (not isinstance(value, str) or len(value) != 64
                    or any(c not in "0123456789abcdef" for c in value)):
                raise ValueError(f"proposal requires a canonical {name}")


def _validate_actions(session, actions):
    profile = session._require_render_profile()
    observations = {r["observation_id"] for r in session.observation_history}
    for action in actions:
        if action.observation_id not in observations:
            raise ValueError("element edit requires a recorded observation_id")
        if isinstance(action, InkAction):
            session._validate_ink_action(action)
        else:
            action.validate()
            if action.kind == "erase_path":
                session._require_path_eraser_profile(action.pressure)
            if profile.is_mixed_media and action.kind in {
                    "draw_stroke", "replace_stroke", "erase_path"}:
                from ..render.mixed import validate_mixed_stroke
                validate_mixed_stroke(_stroke_from_action(action))
    return profile


def _preflight(session, actions):
    session._assert_branchable_history()
    profile = _validate_actions(session, actions)
    clone = AgentDrawingSession.from_dict(session._agent.to_dict())
    clone.execute_many_atomic(actions, label="prospective element edit")
    profile.validate_history(clone.history)
    return clone


def _guard(session, proposal):
    if not isinstance(proposal, ElementEditProposal):
        raise ValueError("ElementEditProposal required")
    actions = deepcopy(_typed_actions(proposal.actions))
    if _action_digest(actions) != proposal.action_digest:
        raise ValueError("element edit proposal differs from prepared actions")
    if session.history_cursor != proposal.base_cursor:
        raise ValueError("stale element edit cursor")
    if session.drawing_state_hash() != proposal.base_state_hash:
        raise ValueError("stale element edit state")
    if session._require_render_profile().digest() != proposal.profile_digest:
        raise ValueError("stale element edit profile")
    return actions


def prepare_element_edits(session, actions):
    """Validate a bounded mixed batch without changing history or checkpoint.

Every action must cite a recorded observation. The authoritative reducer
checks identities, sequential dependencies and inherited layer locks on a
    detached history before this receipt is returned. New marks use the active
    paint layer; use the drawing facade to specify another destination layer.
"""
    actions = deepcopy(_typed_actions(actions))
    with session._lock:
        _preflight(session, actions)
        return ElementEditProposal(actions, session.history_cursor,
                                   session.drawing_state_hash(),
                                   session._require_render_profile().digest(),
                                   _action_digest(actions))


def preview_element_edits(session, proposal, out):
    """Render the exact guarded proposal as noncanonical, detached evidence."""
    path = Path(out)
    if (path.suffix.lower() != ".png" or path.exists()
            or path.with_suffix(".render.json").exists()):
        raise ValueError("preview requires a new PNG and manifest path")
    with session._lock:
        actions = _guard(session, proposal)
        clone = _preflight(session, actions)
        artifact = render_history_at(clone.history, clone.history.cursor, path,
                                     session._require_render_profile())
        return {"preview_only": True, "base_cursor": proposal.base_cursor,
                "base_state_hash": proposal.base_state_hash,
                "profile_digest": proposal.profile_digest,
                "action_digest": proposal.action_digest,
                "prospective_state_hash": artifact.drawing_state_hash,
                "pixel_sha256": artifact.pixel_sha256,
                "action_ids": [a.action_id for a in actions]}


def apply_element_edits(session, proposal):
    """Apply a guarded batch once through the session's atomic commit path."""
    with session._lock:
        actions = _guard(session, proposal)
        _validate_actions(session, actions)
        session._commit(actions)
        return tuple(a.action_id for a in actions)


def _similarity_scale(matrix):
    a, b, c, d, _, _ = matrix
    sx, sy = math.hypot(a, c), math.hypot(b, d)
    if (not sx or not sy or abs(sx - sy) > 1e-10 * max(sx, sy)
            or abs((a / sx) * (b / sy) + (c / sx) * (d / sy)) > 1e-10):
        raise ValueError("paths and object-following tone require a similarity transform")
    return sx


def _point(point, matrix):
    a, b, c, d, tx, ty = matrix
    x, y = point
    return a * x + b * y + tx, c * x + d * y + ty


def _transform_ink(mark, matrix, width_policy, tone_policy):
    def point(p):
        return _point(p, matrix)

    if isinstance(mark, InkPath):
        scale = _similarity_scale(matrix) if width_policy == "scale" else 1.
        return replace(mark, points=tuple(map(point, mark.points)),
                       min_width=mark.min_width * scale, max_width=mark.max_width * scale)
    if isinstance(mark, InkArea):
        changes = {"outer": tuple(map(point, mark.outer)),
                   "holes": tuple(tuple(map(point, ring)) for ring in mark.holes)}
        if isinstance(mark, Screentone) and tone_policy == "object":
            scale = _similarity_scale(matrix)
            a, b, c, d, _, _ = matrix
            theta = math.radians(mark.angle_degrees)
            ux, uy = math.cos(theta), math.sin(theta)
            changes.update(pitch=mark.pitch * scale, phase_origin=point(mark.phase_origin),
                           angle_degrees=math.degrees(math.atan2(c * ux + d * uy,
                                                                a * ux + b * uy)))
            if mark.gradient is not None:
                changes["gradient"] = replace(mark.gradient, start=point(mark.gradient.start),
                                               end=point(mark.gradient.end))
        return replace(mark, **changes)
    raise ValueError("unsupported current ink geometry")


def prepare_element_transform(session, element_ids, matrix, *, action_ids,
                              observation_id, reason, width_policy="preserve",
                              tone_policy="page"):
    """Prepare one mixed, same-ID transform with explicit material policies.

Matrix is (a,b,c,d,tx,ty), with x'=a*x+b*y+tx and y'=c*x+d*y+ty.
``preserve`` keeps all path widths; ``scale`` scales graphite and ink widths
uniformly. Pressure and relative graphite contact-width factors are unchanged.
Paths require a similarity (including reflection), since scalar widths cannot
represent an affine deformation of their contact. Solid areas and page-fixed
tone boundaries accept any nonsingular affine map.

``page`` keeps tone pitch, angle, phase and gradient fixed. ``object`` moves
these with the boundary under a similarity, compiling the result into existing
page-space tone fields. Pitch and all geometry/render limits still apply.
Optional curve and pen recipes are retired when resolved geometry is replaced;
earlier recipes remain in history. Path erasers require separate re-authoring.
"""
    ids = _ids(element_ids, "element_ids")
    aids = _ids(action_ids, "action_ids")
    if len(ids) != len(aids):
        raise ValueError("one explicit action ID per transformed element required")
    matrix = _matrix(matrix)
    if width_policy not in ("preserve", "scale"):
        raise ValueError("width_policy must be 'preserve' or 'scale'")
    if tone_policy not in ("page", "object"):
        raise ValueError("tone_policy must be 'page' or 'object'")
    if not isinstance(reason, str) or not reason.strip():
        raise ValueError("edit reason required")
    if not isinstance(observation_id, str) or not observation_id.strip():
        raise ValueError("explicit observation_id required")
    with session._lock:
        snapshot = session.current_ir()
        strokes = {s.stroke_id: s for s in snapshot.strokes}
        ink = {e.element_id: e for e in snapshot.ink_elements}
        if not set(ids) <= strokes.keys() | ink.keys():
            raise ValueError("transform requires current element IDs")
        selected_strokes = [sid for sid in ids if sid in strokes]
        if selected_strokes:
            from ..render.eraser import is_eraser
            if any(is_eraser(strokes[sid]) for sid in selected_strokes):
                raise ValueError("path eraser transform requires explicit re-authoring")
        needs_similarity = bool(selected_strokes) or any(
            isinstance(ink[sid].mark, InkPath)
            or (isinstance(ink[sid].mark, Screentone) and tone_policy == "object")
            for sid in ids if sid in ink)
        scale = _similarity_scale(matrix) if needs_similarity else 1.
        stroke_actions = {}
        if selected_strokes:
            edits = [StrokeEdit(sid, tuple(_point(p, matrix) for p in strokes[sid].points),
                        material_overrides=({"width": strokes[sid].width * scale}
                                            if width_policy == "scale" else None))
                     for sid in selected_strokes]
            stroke_actions = {a.stroke_id: a for a in
                              _stroke_actions(session, edits, reason, observation_id)}
        source = f"explicit element transform; width={width_policy}; tone={tone_policy}"
        actions = []
        for sid, aid in zip(ids, aids):
            if sid in strokes:
                actions.append(replace(stroke_actions[sid], action_id=aid,
                                       source_observation=source))
            else:
                old = ink[sid]
                new = replace(old, mark=_transform_ink(old.mark, matrix, width_policy, tone_policy))
                actions.append(InkAction(aid, "ink.replace", sid, new,
                                         observation_id, source, reason))
        return prepare_element_edits(session, actions)


def prepare_element_group_transform(session, plan_id, group_id, matrix, *,
                                    action_ids, observation_id, reason,
                                    width_policy="preserve", tone_policy="page"):
    """Prepare the selected semantic group's exact current mixed membership."""
    from .semantic_groups import inspect_semantic_groups
    with session._lock:
        report = inspect_semantic_groups(session, plan_id)
        row = report["groups"].get(group_id)
        if row is None:
            raise ValueError("unknown semantic group")
        if row["missing_ids"] or row["unassigned_split_ids"]:
            raise ValueError("redeclare group membership before editing")
        return prepare_element_transform(session, tuple(row["current_ids"]), matrix,
            action_ids=action_ids, observation_id=observation_id, reason=reason,
            width_policy=width_policy, tone_policy=tone_policy)


__all__ = ["ElementEditProposal", "prepare_element_edits", "prepare_element_transform",
           "prepare_element_group_transform", "preview_element_edits", "apply_element_edits"]
