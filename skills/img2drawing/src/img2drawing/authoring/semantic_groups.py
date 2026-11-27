"""Explicit group definitions and review evidence in the existing observation log.

Group membership is agent-declared. Latest element versions, replacements and
retirements are derived from authoritative actions, never a second edit history.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Sequence

from ..core import DrawingAction
from ..core.digest import sha256_obj
from ..core.material import InkAction, InkElement
from .stroke_edits import transform_strokes, _guard

GROUP_PLAN_SCHEMA = "img2drawing.observation.semantic_groups.v1"
GROUP_REVIEW_SCHEMA = "img2drawing.observation.semantic_group_review.v1"


def _text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a nonempty string")
    return value.strip()


def _ids(values, label, *, required=False):
    if isinstance(values, str):
        raise ValueError(f"{label} requires a sequence of IDs")
    out = tuple(_text(v, label) for v in values)
    if (required and not out) or len(set(out)) != len(out):
        raise ValueError(f"{label} requires unique IDs")
    return out


@dataclass(frozen=True)
class SemanticGroup:
    group_id: str
    member_ids: tuple[str, ...]
    guide_ids: tuple[str, ...] = ()
    depends_on: tuple[str, ...] = ()

    def __post_init__(self):
        object.__setattr__(self, "group_id", _text(self.group_id, "group_id"))
        for field in ("member_ids", "guide_ids", "depends_on"):
            object.__setattr__(self, field, _ids(getattr(self, field), field,
                                                required=field == "member_ids"))
        if not set(self.guide_ids) <= set(self.member_ids):
            raise ValueError("guide IDs must belong to the group")
        if self.group_id in self.depends_on:
            raise ValueError("group cannot depend on itself")

    def to_dict(self):
        return {"group_id": self.group_id, "member_ids": list(self.member_ids),
                "guide_ids": list(self.guide_ids), "depends_on": list(self.depends_on)}


def _validate_graph(groups):
    groups = tuple(groups)
    if not 1 <= len(groups) <= 128 or any(not isinstance(g, SemanticGroup) for g in groups):
        raise ValueError("expected 1–128 SemanticGroup records")
    by_id = {g.group_id:g for g in groups}
    if len(by_id) != len(groups):
        raise ValueError("duplicate group ID")
    members = [i for g in groups for i in g.member_ids]
    if len(members) > 4096 or len(set(members)) != len(members):
        raise ValueError("group memberships must be disjoint and bounded")
    visiting, done, order = set(), set(), []
    def visit(gid):
        if gid in visiting:
            raise ValueError("cyclic group dependencies")
        if gid in done:
            return
        if gid not in by_id:
            raise ValueError(f"unknown group dependency: {gid}")
        visiting.add(gid)
        for p in by_id[gid].depends_on:
            visit(p)
        visiting.remove(gid)
        done.add(gid)
        order.append(gid)
    for g in groups:
        visit(g.group_id)
    return by_id, order


def _resolve(index, sid):
    """Follow exact existing authored-element ancestry in a single index."""
    item = index.get(sid)
    seen = set()
    while item is not None and item.status == "superseded":
        if item.element_id in seen:
            raise ValueError("cyclic stroke ancestry")
        seen.add(item.element_id)
        item = index.get(item.superseded_by)
    return item


def _plan(session, plan_id):
    records = session.observation_history
    for record in records:
        if record["observation_id"] == plan_id:
            raw = record["payload"]
            if not isinstance(raw, dict) or raw.get("schema") != GROUP_PLAN_SCHEMA:
                raise ValueError("observation is not a semantic group plan")
            groups = tuple(SemanticGroup(**g) for g in raw["groups"])
            return groups, records
    raise ValueError("unknown semantic group plan")


def _derive(session, groups, records=(), plan_id=None):
    by_id, order = _validate_graph(groups)
    elements = session.authored_elements(status=None)
    index = {e.element_id:e for e in elements}
    snapshot = session.current_ir()
    ir = {s.stroke_id:s for s in snapshot.strokes}
    ir.update({e.element_id:e for e in snapshot.ink_elements})
    reviews = {}
    for rec in records:
        raw = rec["payload"]
        if (isinstance(raw, dict) and raw.get("schema") == GROUP_REVIEW_SCHEMA
                and raw.get("plan_id") == plan_id):
            reviews[raw["group_id"]] = raw
    output, owner = {}, {}
    for gid in order:
        g = by_id[gid]
        current, guides, missing, retired, versions = [], [], [], [], []
        for sid in g.member_ids:
            element = _resolve(index, sid)
            if element is None or element.status != "current":
                if sid in g.guide_ids and element is not None and element.status == "deleted":
                    retired.append(sid)
                else:
                    missing.append(sid)
                versions.append([sid, None if element is None else element.to_dict()])
                continue
            cid = element.element_id
            if cid in owner:
                raise ValueError(f"members resolve to duplicate current stroke: {cid}")
            owner[cid] = gid
            current.append(cid)
            if sid in g.guide_ids:
                guides.append(cid)
            current_mark = ir[cid]
            payload = current_mark.to_dict() if isinstance(current_mark, InkElement) else asdict(current_mark)
            version = [sid, element.to_dict(), sha256_obj(payload)]
            if snapshot.layer_document is not None:
                document = snapshot.layer_document
                layer_id = document.layer_for(cid)
                context = {"member_index": document.members[layer_id].index(cid), "ancestors": []}
                while layer_id is not None:
                    node = document.node(layer_id)
                    context["ancestors"].append({key: getattr(node, key) for key in (
                        "layer_id", "parent_id", "order", "visible", "opacity", "blend_mode")})
                    layer_id = node.parent_id
                version.append(context)
            versions.append(version)
        parents = [output[p] for p in g.depends_on]
        signature = sha256_obj({"definition":g.to_dict(), "members":versions,
                                "parents":[p["signature"] for p in parents]})
        review = reviews.get(gid)
        reasons = []
        if missing:
            reasons.append("missing_descriptive_or_unresolved_member")
        if review is None:
            reasons.append("unreviewed")
        elif review.get("signature") != signature:
            reasons.append("changed_member_or_dependency")
        if any(p["review_required"] for p in parents):
            reasons.append("dependency_review_required")
        output[gid] = {"group_id":gid, "current_ids":current, "current_guide_ids":guides,
                       "retired_guide_ids":retired, "missing_ids":missing,
                       "latest_action_ids":[index[c].latest_action_id for c in current],
                       "depends_on":list(g.depends_on), "signature":signature,
                       "review_required":bool(reasons), "reasons":reasons,
                       "unassigned_split_ids":[]}
    # A split creates a new explicit stroke. Do not silently inherit membership.
    # Flag unassigned fragments of grouped strokes until the agent redeclares them.
    actions_by_seq = {a.seq:a for a in session._agent.history.actions[:session.history_cursor]}
    for cid, stroke in ir.items():
        if isinstance(stroke, InkElement):
            continue
        # Use creation provenance, not the latest mutable tool metadata. A split
        # fragment can itself be edited without losing its original declaration.
        creation = actions_by_seq[index[cid].created_seq]
        metadata = (creation.provenance or {}).get("metadata") or {}
        if cid in owner or metadata.get("split_fragment") != "second":
            continue
        source = metadata.get("geometry_edited_from")
        parent = _resolve(index, source) if isinstance(source, str) else None
        if parent is not None and parent.element_id in owner:
            row = output[owner[parent.element_id]]
            row["unassigned_split_ids"].append(cid)
    # Fold split issues into the fingerprint and propagate invalidation in order.
    for gid in order:
        row = output[gid]
        row["signature"] = sha256_obj({"members_and_dependencies":row["signature"],
            "unassigned_split_ids":sorted(row["unassigned_split_ids"]),
            "parent_signatures":[output[p]["signature"] for p in row["depends_on"]]})
        review = reviews.get(gid)
        reasons = []
        if row["missing_ids"]:
            reasons.append("missing_descriptive_or_unresolved_member")
        if row["unassigned_split_ids"]:
            reasons.append("explicit_split_membership_required")
        if review is None:
            reasons.append("unreviewed")
        elif review.get("signature") != row["signature"]:
            reasons.append("changed_member_or_dependency")
        if any(output[p]["review_required"] for p in row["depends_on"]):
            reasons.append("dependency_review_required")
        row["reasons"] = reasons
        row["review_required"] = bool(reasons)
    return {"plan_id":plan_id, "cursor":session.history_cursor,
            "drawing_state_hash":session.drawing_state_hash(),
            "groups":output, "artistic_verdict":"NOT_EVALUATED"}


def record_semantic_groups(session, groups: Sequence[SemanticGroup], *, evidence: str):
    """Persist an immutable declaration via the existing session.observe path.

    A changed group definition requires a new plan observation; no old plan is
    rewritten. All members must resolve to current strokes at declaration.
    """
    groups = tuple(groups)
    with session._lock:
        report = _derive(session, groups)
        if any(g["missing_ids"] or g["retired_guide_ids"] for g in report["groups"].values()):
            raise ValueError("group declaration requires current members")
        return session.observe({"schema":GROUP_PLAN_SCHEMA, "evidence":_text(evidence,"evidence"),
                                "groups":[g.to_dict() for g in groups]})


def inspect_semantic_groups(session, plan_id: str):
    """Read current membership, revisions, missing marks and dependent review needs."""
    with session._lock:
        groups, records = _plan(session, plan_id)
        return _derive(session, groups, records, plan_id)


def _row(report, group_id):
    try:
        return report["groups"][group_id]
    except KeyError as exc:
        raise ValueError(f"unknown group: {group_id}") from exc


def review_semantic_group(session, plan_id, group_id, *, inspection_id, evidence):
    """Record agent review of a current group, not artistic acceptance.

    A current whole/ROI inspection and recorded image read are required.
    Unresolved member identity or stale parent review cannot be acknowledged away.
    """
    with session._lock:
        report = inspect_semantic_groups(session, plan_id)
        row = _row(report, group_id)
        blockers = set(row["reasons"]) - {"unreviewed","changed_member_or_dependency"}
        if blockers:
            raise ValueError("group review blocked: " + ", ".join(sorted(blockers)))
        inspections = session.inspection_history
        if (not inspections or inspections[-1]["inspection_id"] != str(inspection_id)
                or inspections[-1]["drawing_state_hash"] != report["drawing_state_hash"]
                or inspections[-1]["history_cursor"] != report["cursor"]):
            raise ValueError("group review requires current inspection")
        if not any(e.inspection_id == str(inspection_id) and not e.stale
                   and e.artifact not in {"measurements", "manifest", "inspection_json", "measurements.json", "inspection.json"}
                   for e in session.evidence_telemetry.read_events):
            raise ValueError("group review requires recorded current evidence read")
        return session.observe({"schema":GROUP_REVIEW_SCHEMA, "plan_id":plan_id,
            "group_id":group_id, "signature":row["signature"], "inspection_id":str(inspection_id),
            "evidence":_text(evidence,"evidence"), "artistic_verdict":"NOT_EVALUATED"})


def prepare_group_transform(session, plan_id, group_id, matrix):
    """Prepare only the selected group's current strokes for existing preview/apply."""
    with session._lock:
        report = inspect_semantic_groups(session, plan_id)
        row = _row(report, group_id)
        if row["missing_ids"] or row["unassigned_split_ids"]:
            raise ValueError("redeclare group membership before editing")
        if set(row["current_ids"]) & {e.element_id for e in session.current_ir().ink_elements}:
            raise ValueError("mixed group transforms require explicit per-element ink edits")
        return {"edits":transform_strokes(session, row["current_ids"], matrix),
                "base_cursor":report["cursor"], "base_state_hash":report["drawing_state_hash"]}


def retire_group_guides(session, plan_id, group_id, guide_ids, *, reason, observation_id,
                        expected_cursor=None, expected_state_hash=None):
    """Atomically retire explicitly selected current guides using normal delete actions.

    No descriptive member or dependent group is erased implicitly.
    """
    selected = _ids(guide_ids, "guide_ids", required=True)
    reason = _text(reason, "reason")
    observation_id = _text(observation_id, "observation_id")
    with session._lock:
        _guard(session, expected_cursor, expected_state_hash)
        report = inspect_semantic_groups(session, plan_id)
        row = _row(report, group_id)
        if not set(selected) <= set(row["current_guide_ids"]):
            raise ValueError("retirement accepts only explicitly declared current guides")
        oid, source, why = session._provenance(observation_id=observation_id,
                         source_observation="explicit semantic group guide retirement", reason=reason)
        from ..session.drawing_session import _COMPAT_STAGE, _tool_payload, _action_id
        ink_ids = {e.element_id for e in session.current_ir().ink_elements}
        actions = []
        for sid in selected:
            aid = _action_id(session._agent.history, None,
                             session._agent.executed_action_ids | {a.action_id for a in actions})
            if sid in ink_ids:
                actions.append(InkAction(aid, "ink.delete", sid, None, oid, source, why))
            else:
                actions.append(DrawingAction(action_id=aid, kind="delete_stroke",
                    stage=_COMPAT_STAGE, target_stroke_id=sid,
                    tool=_tool_payload("hard_eraser",None,None), observation_id=oid,
                    source_observation=source, reason=why,
                    metadata={"semantic_group_plan":plan_id,"semantic_group_id":group_id}))
        session._commit(actions)
        return tuple(a.action_id for a in actions)


__all__ = ["SemanticGroup", "record_semantic_groups", "inspect_semantic_groups",
           "review_semantic_group", "prepare_group_transform", "retire_group_guides"]
