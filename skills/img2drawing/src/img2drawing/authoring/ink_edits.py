"""Explicit, atomic ink edits in the same DrawingSession history."""
from __future__ import annotations

from pathlib import Path
from dataclasses import replace
import math

from ..core.action import AgentDrawingSession
from ..core.digest import sha256_obj
from ..core.material import InkAction, InkArea, InkPath, Screentone, _number, _identity_text
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


def current_ink_element(session, element_id):
    """Return the detached current typed element by stable ID; never a retired mark."""
    _identity_text(element_id,"element_id")
    with session._lock:
        for element in session.current_ir().ink_elements:
            if element.element_id==element_id:
                return element
    raise ValueError(f"unknown current ink element: {element_id}")


def _ids(values, name):
    if not isinstance(values,(list,tuple)) or not 1<=len(values)<=256:
        raise ValueError(f"{name} requires 1–256 explicit identities")
    ids=tuple(_identity_text(v,name) for v in values)
    if len(set(ids))!=len(ids):
        raise ValueError(f"{name} requires unique identities")
    return ids


def _matrix(matrix):
    if not isinstance(matrix,(tuple,list)) or len(matrix)!=6:
        raise ValueError("affine matrix requires six finite numbers")
    a,b,c,d,tx,ty=(_number(v,"affine matrix",-1e9,1e9) for v in matrix)
    det=a*d-b*c
    if det==0. or not math.isfinite(det):
        raise ValueError("affine matrix must be nonsingular")
    return a,b,c,d,tx,ty


def _transformed_mark(mark, matrix):
    a,b,c,d,tx,ty=matrix
    def point(p):
        x,y=p
        return a*x+b*y+tx,c*x+d*y+ty
    if isinstance(mark,Screentone):
        sx,sy=math.hypot(a,c),math.hypot(b,d)
        if (not sx or not sy or abs(sx-sy)>1e-10*max(sx,sy)
                or abs((a/sx)*(b/sy)+(c/sx)*(d/sy))>1e-10):
            raise ValueError("screentone transform requires a similarity; page pattern stays fixed")
        # Only authored boundaries move. Pitch, angle, phase and gradient axis
        # remain page-anchored, even under rotation or uniform scale.
        return replace(mark,outer=tuple(map(point,mark.outer)),
                       holes=tuple(tuple(map(point,ring)) for ring in mark.holes))
    if isinstance(mark,InkArea):
        return replace(mark,outer=tuple(map(point,mark.outer)),
                       holes=tuple(tuple(map(point,ring)) for ring in mark.holes))
    if isinstance(mark,InkPath):
        sx,sy=math.hypot(a,c),math.hypot(b,d)
        # A round contact or normal-strip diameter remains scalar under a
        # similarity (rotation/reflection + uniform scale) only.
        if (not sx or not sy or abs(sx-sy)>1e-10*max(sx,sy)
                or abs((a/sx)*(b/sy)+(c/sx)*(d/sy))>1e-10):
            raise ValueError("ink path transform requires a similarity (uniform scale/rotation/reflection)")
        return replace(mark,points=tuple(map(point,mark.points)),
                       min_width=mark.min_width*sx,max_width=mark.max_width*sx)
    raise ValueError("unsupported current ink geometry")


def prepare_ink_transform(session, element_ids, matrix, *, action_ids,
                          observation_id, reason,
                          source_observation="explicit ink geometry transform"):
    """Prepare guarded same-ID replacements; no mutation or implicit selection.

    Solid areas support nonsingular affine maps. Screentone boundaries support
    similarity transforms with unchanged page-space pattern/gradient. Paths
    support similarity transforms, including uniform width scaling. Explicit resolved geometry is transformed
    exactly; a raw replacement intentionally retires any optional pen recipe
    from the current element (the original recipe remains in earlier history).
    Commit via preview_ink_actions/apply_ink_actions with returned guards.
    """
    ids=_ids(element_ids,"element_ids")
    aids=_ids(action_ids,"action_ids")
    if len(ids)!=len(aids):
        raise ValueError("one explicit action ID per transformed element required")
    mat=_matrix(matrix)
    with session._lock:
        profile=session._require_render_profile()
        if not profile.is_mixed_media:
            raise ValueError("ink transform requires mixed-media profile")
        current={e.element_id:e for e in session.current_ir().ink_elements}
        if not set(ids)<=set(current):
            raise ValueError("transform requires current ink element IDs")
        actions=[]
        for sid,aid in zip(ids,aids):
            old=current[sid]
            new=replace(old,mark=_transformed_mark(old.mark,mat))
            actions.append(InkAction(aid,"ink.replace",sid,new,observation_id,
                                     source_observation,reason))
        actions=_validated(session,actions)
        # Validate target IDs and the entire batch on a detached history before
        # returning a proposal. No parallel mutable state is retained.
        clone=AgentDrawingSession.from_dict(session._agent.to_dict())
        clone.execute_many_atomic(actions,label="prospective ink transform")
        return {"actions":actions,"base_cursor":session.history_cursor,
                "base_state_hash":session.drawing_state_hash(),
                "profile_digest":profile.digest(),"action_digest":_digest(actions)}


def prepare_ink_group_transform(session, plan_id, group_id, matrix, *,
                                action_ids, observation_id, reason):
    """Use existing semantic membership; ink-only groups, not implicit mixed edits."""
    from .semantic_groups import inspect_semantic_groups
    with session._lock:
        report=inspect_semantic_groups(session,plan_id)
        row=report["groups"].get(group_id)
        if row is None:
            raise ValueError("unknown semantic group")
        if row["missing_ids"] or row["unassigned_split_ids"]:
            raise ValueError("redeclare group membership before editing")
        ids=tuple(row["current_ids"])
        if not ids or not set(ids)<={e.element_id for e in session.current_ir().ink_elements}:
            raise ValueError("ink group transform requires an ink-only current group")
        return prepare_ink_transform(session,ids,matrix,action_ids=action_ids,
                                     observation_id=observation_id,reason=reason,
                                     source_observation="explicit semantic ink group transform")
