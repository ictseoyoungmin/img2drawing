"""Atomic explicit stroke edits over the existing action/history contract."""
from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, dataclass
import math
from pathlib import Path
from collections.abc import Mapping
from types import MappingProxyType
from typing import Sequence

from ..core.action import AgentDrawingSession, DrawingAction
from ..core.digest import sha256_obj
from ..inspection import drawing_state_hash
from ..render.artifact import render_history_at
from .retune import _TOOL_OVERRIDE_FIELDS


@dataclass(frozen=True)
class StrokeEdit:
    """One current stroke's explicit points and optional pressure/split/material."""
    stroke_id: str
    points: tuple[tuple[float,float],...]
    pressure: tuple[float,...] | None = None
    split_at: int | None = None
    new_stroke_id: str | None = None
    material_overrides: Mapping[str, float] | None = None

    def __post_init__(self):
        if not isinstance(self.stroke_id,str) or not self.stroke_id.strip():
            raise ValueError("current stroke id required")
        points=tuple(tuple(map(float,p)) for p in self.points)
        if len(points)<2 or any(len(p)!=2 or not all(math.isfinite(v) for v in p) for p in points):
            raise ValueError("at least two finite xy points required")
        if any(a==b for a,b in zip(points,points[1:])):
            raise ValueError("consecutive duplicate points lose pressure alignment")
        object.__setattr__(self,"points",points)
        if self.pressure is not None:
            q=tuple(map(float,self.pressure))
            if len(q)!=len(points) or any(not math.isfinite(v) or not 0<=v<=1 for v in q):
                raise ValueError("pressure must align with points and lie in [0,1]")
            object.__setattr__(self,"pressure",q)
        if self.material_overrides is not None:
            if not isinstance(self.material_overrides, Mapping):
                raise ValueError("material_overrides requires a mapping")
            material = {}
            for key, value in self.material_overrides.items():
                if key not in {"width", "opacity", "hardness", "grain"}:
                    raise ValueError(f"unsupported material edit field: {key}")
                if isinstance(value, bool):
                    raise ValueError(f"invalid material edit: {key}")
                try:
                    v = float(value)
                except (TypeError, ValueError) as exc:
                    raise ValueError(f"invalid material edit: {key}") from exc
                if not math.isfinite(v) or (v <= 0 if key == "width" else not 0 <= v <= 1):
                    raise ValueError(f"invalid material edit: {key}")
                material[key] = v
            object.__setattr__(self, "material_overrides", MappingProxyType(material))
        if self.split_at is None:
            if self.new_stroke_id is not None:
                raise ValueError("new stroke id requires split_at")
        elif (type(self.split_at) is not int or not 1<=self.split_at<len(points)-1
              or not isinstance(self.new_stroke_id,str) or not self.new_stroke_id.strip()
              or self.new_stroke_id==self.stroke_id):
            raise ValueError("split requires interior point and distinct explicit new stroke id")


def _current(session):
    return {s.stroke_id:s for s in session.current_ir().strokes}


def _actions(session, edits, reason, observation_id, *, retire_ids=(), additions=(), erasures=()):
    if not isinstance(reason,str) or not reason.strip():
        raise ValueError("edit reason required")
    if not isinstance(observation_id,str) or not observation_id.strip():
        raise ValueError("explicit observation_id required")
    edits=tuple(edits)
    if any(not isinstance(e,StrokeEdit) for e in edits):
        raise ValueError("StrokeEdit sequence required")
    if isinstance(retire_ids, str):
        raise ValueError("retire_ids must be a sequence of current stroke IDs")
    retire_ids=tuple(retire_ids)
    additions=tuple(additions)
    erasures=tuple(erasures)
    if not (edits or retire_ids or additions or erasures):
        raise ValueError("nonempty explicit stroke edit batch required")
    if any(not isinstance(i,str) or not i.strip() for i in retire_ids):
        raise ValueError("retire_ids must contain current stroke IDs")
    if len(set(retire_ids))!=len(retire_ids):
        raise ValueError("duplicate retirement ID")
    current=_current(session)
    ids=[e.stroke_id for e in edits]
    if len(set(ids))!=len(ids):
        raise ValueError("duplicate current stroke edit")
    if any(i not in current for i in (*ids,*retire_ids)):
        raise ValueError("edit or retirement requires current stroke IDs")
    if set(ids)&set(retire_ids):
        raise ValueError("a stroke cannot be edited and retired in the same batch")
    new_ids=[e.new_stroke_id for e in edits if e.split_at is not None]
    if len(set(new_ids))!=len(new_ids) or any(i in current for i in new_ids):
        raise ValueError("duplicate or existing split stroke ID")
    actions=[]
    def aid():
        return f"vnext-{len(session._agent.history.actions)+len(actions)+1:06d}"
    for e in edits:
        s=current[e.stroke_id]
        state=s.tool_state or {}
        if not state.get("tool"):
            raise ValueError("current stroke lacks recoverable material")
        pressure=e.pressure
        if pressure is None:
            if s.pressure is not None:
                if len(s.pressure)!=len(e.points):
                    raise ValueError("different point count requires explicit pressure")
                pressure=tuple(s.pressure)
            else:
                raise ValueError("missing current pressure; provide explicit pressure")
        overrides={k:float(state[k]) for k in _TOOL_OVERRIDE_FIELDS if k in state}
        # Preserve visible material, including global soft-lift and local pressure.
        overrides["opacity"]=float(s.opacity)
        overrides["width"]=float(s.width)
        overrides.update(e.material_overrides or {})
        meta=deepcopy((state.get("provenance") or {}).get("metadata") or {})
        meta["geometry_edited_from"]=e.stroke_id
        if e.material_overrides:
            meta["explicit_material_edit_fields"] = sorted(e.material_overrides)
        common=dict(role=s.role,part=s.part,confidence=s.confidence,layer=s.layer,
                    tool=state["tool"],grade=state.get("pencil_grade"),
                    tool_overrides=overrides,observation_id=observation_id,
                    source_observation="explicit stroke geometry edit",reason=reason)
        i=e.split_at
        points=e.points if i is None else e.points[:i+1]
        pressures=pressure if i is None else pressure[:i+1]
        first_meta=deepcopy(meta)
        if i is not None:
            first_meta["split_fragment"]="first"
        actions.append(session._draw_action(points,action_id=aid(),stroke_id=e.stroke_id,
            target_stroke_id=e.stroke_id,revision_of=e.stroke_id,kind="replace_stroke",
            pressure=pressures,metadata=first_meta,**common))
        if i is not None:
            second_meta=deepcopy(meta)
            second_meta["split_fragment"]="second"
            actions.append(session._draw_action(e.points[i:],action_id=aid(),
                stroke_id=e.new_stroke_id,pressure=pressure[i:],metadata=second_meta,**common))
    from ..session.drawing_session import _COMPAT_STAGE, _tool_payload
    oid, source, why = session._provenance(observation_id=observation_id,
        source_observation="explicit stroke family rewrite", reason=reason)
    for sid in retire_ids:
        actions.append(DrawingAction(action_id=aid(),kind="delete_stroke",stage=_COMPAT_STAGE,
            target_stroke_id=sid,tool=_tool_payload("hard_eraser",None,None),
            observation_id=oid,source_observation=source,reason=why))
    # Only the ordinary draw kwargs are accepted, not arbitrary action kinds,
    # provenance overrides or implicit identity assignment.
    allowed={"points","stroke_id","role","part","confidence","layer","pressure",
             "tool","grade","tool_overrides","metadata"}
    occupied=set(current)|set(new_ids)
    for spec in additions:
        if not isinstance(spec,Mapping) or set(spec)-allowed or not {"points","stroke_id","role","tool"}<=set(spec):
            raise ValueError("addition requires explicit draw kwargs, ID, role and tool")
        values=deepcopy(dict(spec))
        sid=values["stroke_id"]
        if not isinstance(sid,str) or not sid.strip() or sid in occupied:
            raise ValueError("addition requires a distinct new stroke ID")
        occupied.add(sid)
        actions.append(session._draw_action(action_id=aid(),observation_id=oid,
            source_observation=source,reason=why,**values))
    allowed_erase={"points","stroke_id","width","strength","tool","layer","part"}
    for spec in erasures:
        if not isinstance(spec,Mapping) or set(spec)-allowed_erase or not {"points","stroke_id","width"}<=set(spec):
            raise ValueError("erasure requires explicit path, ID and width")
        values=deepcopy(dict(spec))
        sid=values["stroke_id"]
        if not isinstance(sid,str) or not sid.strip() or sid in occupied:
            raise ValueError("erasure requires a distinct fresh stroke ID")
        occupied.add(sid)
        actions.append(session._erase_path_action(action_id=aid(),observation_id=oid,reason=why,**values))
    return actions


def _action_digest(actions):
    return sha256_obj([asdict(a) for a in actions])


def _guard(session, expected_cursor, expected_state_hash):
    if expected_cursor is not None and session.history_cursor!=expected_cursor:
        raise ValueError("stale stroke edit cursor")
    if expected_state_hash is not None and session.drawing_state_hash()!=expected_state_hash:
        raise ValueError("stale stroke edit state")


def apply_stroke_edits(session, edits: Sequence[StrokeEdit], *, reason,
                       observation_id, expected_cursor=None, expected_state_hash=None,
                       retire_ids=(), additions=(), erasures=(), expected_action_digest=None):
    """Atomically apply explicit replacements, retirements and new authored marks."""
    with session._lock:
        _guard(session,expected_cursor,expected_state_hash)
        actions=_actions(session,edits,reason,observation_id,retire_ids=retire_ids,additions=additions,erasures=erasures)
        if expected_action_digest is not None and _action_digest(actions)!=expected_action_digest:
            raise ValueError("stroke edit proposal differs from preview")
        session._commit(actions)
        return tuple(a.action_id for a in actions)


def preview_stroke_edits(session, edits: Sequence[StrokeEdit], out, *, reason, observation_id,
                         retire_ids=(), additions=(), erasures=()):
    """Render the exact prospective action batch on a detached history clone.

    No observations, session history or checkpoint are modified. The preview is
    explicitly noncanonical evidence until the same edit is committed.
    """
    path=Path(out)
    if path.suffix.lower()!=".png" or path.exists() or path.with_suffix(".render.json").exists():
        raise ValueError("preview requires a new PNG and manifest path")
    with session._lock:
        cursor=session.history_cursor
        state=session.drawing_state_hash()
        profile=session._require_render_profile()
        actions=_actions(session,edits,reason,observation_id,retire_ids=retire_ids,additions=additions,erasures=erasures)
        clone=AgentDrawingSession.from_dict(session._agent.to_dict())
        clone.execute_many_atomic(actions,label="prospective stroke edit")
        artifact=render_history_at(clone.history,clone.history.cursor,path,profile)
        return {"preview_only":True,"base_cursor":cursor,"base_state_hash":state,
                "prospective_state_hash":artifact.drawing_state_hash,
                "pixel_sha256":artifact.pixel_sha256,"action_ids":[a.action_id for a in actions],
                "action_digest":_action_digest(actions)}


def transform_strokes(session, stroke_ids, matrix):
    """Prepare affine geometry edits for selected current IDs, not material scaling.

    Matrix is (a,b,c,d,tx,ty) with x'=a*x+b*y+tx and y'=c*x+d*y+ty.
    Width and pressure are unchanged; the caller decides whether to commit.
    """
    a,b,c,d,tx,ty=map(float,matrix)
    if not all(math.isfinite(x) for x in (a,b,c,d,tx,ty)) or a*d-b*c==0:
        raise ValueError("finite nonsingular affine transform required")
    ids=tuple(stroke_ids)
    if not ids or len(set(ids))!=len(ids):
        raise ValueError("unique current stroke IDs required")
    with session._lock:
        current=_current(session)
        if any(i not in current for i in ids):
            raise ValueError("unknown current stroke")
        return tuple(StrokeEdit(i,tuple((a*x+b*y+tx,c*x+d*y+ty) for x,y in current[i].points))
                     for i in ids)
