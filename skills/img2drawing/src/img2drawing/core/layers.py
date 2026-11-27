"""Opt-in document layers derived from the existing canvas action history.

Membership and paint order are independent of the legacy numeric ``Stroke.layer``
field. Locks protect content and structure; name, visibility and opacity remain
explicit display edits. A node's lock can change only without a locked ancestor.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, replace
import math


LAYER_DOCUMENT_SCHEMA = "img2drawing.layer_document.v1"
LAYER_ACTION_SCHEMA = "img2drawing.layer_action.v1"
LAYER_COMPOSITING = "normal-isolated-rgba8-v1"
MAX_LAYERS = 256
MAX_LAYER_DEPTH = 32
LAYER_ACTION_KINDS = frozenset({
    "layer.enable", "layer.create", "layer.update", "layer.move",
    "layer.assign", "layer.delete", "layer.active",
})


def _text(value, field, maximum=128):
    if (not isinstance(value, str) or not value.strip() or value != value.strip()
            or len(value) > maximum):
        raise ValueError(f"{field} requires a nonempty bounded canonical string")
    return value


def _index(value, field="layer order"):
    if type(value) is not int or value < 0:
        raise ValueError(f"{field} must be a nonnegative integer")
    return value


def _plain(value):
    if isinstance(value, Mapping):
        return {k: _plain(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [_plain(v) for v in value]
    return value


def _immutable(*args, **kwargs):
    raise TypeError("layer values are immutable; author a layer action")


class _FrozenDict(dict):
    __setitem__ = __delitem__ = clear = pop = popitem = setdefault = update = __ior__ = _immutable

    def __deepcopy__(self, memo):
        return self


def _freeze(value):
    if isinstance(value, Mapping):
        return _FrozenDict((k, _freeze(v)) for k, v in value.items())
    if isinstance(value, (tuple, list)):
        return tuple(_freeze(v) for v in value)
    return value


@dataclass(frozen=True)
class LayerNode:
    layer_id: str
    name: str
    kind: str = "paint"
    parent_id: str | None = None
    order: int = 0
    visible: bool = True
    locked: bool = False
    opacity: float = 1.0
    blend_mode: str = "normal"

    def __post_init__(self):
        _text(self.layer_id, "layer_id")
        _text(self.name, "layer name", 256)
        if self.kind not in ("paint", "group"):
            raise ValueError("layer kind must be paint or group")
        if self.parent_id is not None:
            _text(self.parent_id, "parent_id")
        _index(self.order)
        if type(self.visible) is not bool or type(self.locked) is not bool:
            raise ValueError("layer visibility and lock must be boolean")
        if (type(self.opacity) not in (int, float) or not math.isfinite(self.opacity)
                or not 0.0 <= self.opacity <= 1.0):
            raise ValueError("layer opacity must be finite and in [0,1]")
        object.__setattr__(self, "opacity", float(self.opacity))
        if self.blend_mode != "normal":
            raise ValueError("only normal layer compositing is supported")

    def to_dict(self):
        return {"layer_id": self.layer_id, "name": self.name, "kind": self.kind,
                "parent_id": self.parent_id, "order": self.order,
                "visible": self.visible, "locked": self.locked,
                "opacity": self.opacity, "blend_mode": self.blend_mode}

    @classmethod
    def from_dict(cls, raw):
        fields = {"layer_id", "name", "kind", "parent_id", "order", "visible",
                  "locked", "opacity", "blend_mode"}
        if not isinstance(raw, Mapping) or set(raw) != fields:
            raise ValueError("unsupported layer node fields")
        return cls(**dict(raw))


@dataclass(frozen=True)
class LayerDocument:
    layers: tuple[LayerNode, ...]
    members: Mapping[str, tuple[str, ...]]
    active_layer_id: str
    compositing: str = LAYER_COMPOSITING

    def __post_init__(self):
        nodes = tuple(self.layers)
        if not 1 <= len(nodes) <= MAX_LAYERS or any(not isinstance(n, LayerNode) for n in nodes):
            raise ValueError(f"layer document requires 1–{MAX_LAYERS} typed nodes")
        by_id = {n.layer_id: n for n in nodes}
        if len(by_id) != len(nodes):
            raise ValueError("duplicate layer identity")
        siblings = {}
        for node in nodes:
            if node.parent_id is not None:
                parent = by_id.get(node.parent_id)
                if parent is None or parent.kind != "group":
                    raise ValueError("layer parent must be an existing group")
            siblings.setdefault(node.parent_id, []).append(node.order)
            visited, current = set(), node
            while current is not None:
                if current.layer_id in visited:
                    raise ValueError("cyclic layer hierarchy")
                visited.add(current.layer_id)
                if len(visited) > MAX_LAYER_DEPTH:
                    raise ValueError("layer hierarchy depth budget exceeded")
                current = by_id.get(current.parent_id)
        if any(sorted(indices) != list(range(len(indices))) for indices in siblings.values()):
            raise ValueError("sibling layer orders must be contiguous and unique")
        if not isinstance(self.members, Mapping):
            raise ValueError("layer members must be a mapping")
        paints = {n.layer_id for n in nodes if n.kind == "paint"}
        if set(self.members) != paints:
            raise ValueError("every paint layer, and no group, must have a membership list")
        members, seen = {}, set()
        for lid in sorted(paints):
            raw = self.members[lid]
            if not isinstance(raw, (tuple, list)):
                raise ValueError("paint membership requires an ordered sequence of IDs")
            ids = tuple(_text(sid, "element_id") for sid in raw)
            if len(set(ids)) != len(ids) or seen.intersection(ids):
                raise ValueError("each current element must belong to exactly one layer")
            seen.update(ids)
            members[lid] = ids
        _text(self.active_layer_id, "active_layer_id")
        if self.active_layer_id not in paints:
            raise ValueError("active layer must be an existing paint layer")
        if self.compositing != LAYER_COMPOSITING:
            raise ValueError("unsupported layer compositing contract")
        object.__setattr__(self, "layers", tuple(sorted(nodes, key=lambda n: (n.parent_id or "", n.order, n.layer_id))))
        object.__setattr__(self, "members", _freeze(members))

    def node(self, layer_id):
        for node in self.layers:
            if node.layer_id == layer_id:
                return node
        raise ValueError(f"unknown layer: {layer_id}")

    def children(self, parent_id=None):
        return tuple(sorted((n for n in self.layers if n.parent_id == parent_id), key=lambda n: n.order))

    def ancestors(self, layer_id):
        result, node = [], self.node(layer_id)
        while node.parent_id is not None:
            node = self.node(node.parent_id)
            result.append(node)
        return tuple(result)

    def effective_locked(self, layer_id):
        return any(n.locked for n in (self.node(layer_id), *self.ancestors(layer_id)))

    def effective_visible(self, layer_id):
        return all(n.visible for n in (self.node(layer_id), *self.ancestors(layer_id)))

    def layer_for(self, element_id):
        for lid, ids in self.members.items():
            if element_id in ids:
                return lid
        raise ValueError(f"element has no current layer membership: {element_id}")

    def validate_elements(self, element_ids):
        ids = tuple(element_ids)
        members = tuple(sid for values in self.members.values() for sid in values)
        if len(set(ids)) != len(ids) or set(ids) != set(members):
            raise ValueError("layer membership must contain every current element exactly once")

    def assert_editable(self, layer_id, *, descendants=False):
        if self.effective_locked(layer_id):
            raise ValueError(f"layer is locked: {layer_id}")
        if descendants and any(n.locked and any(a.layer_id == layer_id for a in self.ancestors(n.layer_id))
                               for n in self.layers):
            raise ValueError(f"layer subtree contains a locked layer: {layer_id}")

    def assert_element_editable(self, element_id):
        self.assert_editable(self.layer_for(element_id))

    def add_element(self, element_id, layer_id=None):
        sid = _text(element_id, "element_id")
        lid = self.active_layer_id if layer_id is None else layer_id
        if self.node(lid).kind != "paint":
            raise ValueError("new elements require a paint layer")
        self.assert_editable(lid)
        if any(sid in ids for ids in self.members.values()):
            raise ValueError(f"duplicate layer element identity: {sid}")
        members = dict(self.members)
        members[lid] = (*members[lid], sid)
        return replace(self, members=members)

    def replace_element(self, old_id, new_id):
        lid = self.layer_for(old_id)
        self.assert_editable(lid)
        _text(new_id, "replacement element_id")
        if new_id != old_id and any(new_id in ids for ids in self.members.values()):
            raise ValueError("replacement element already has layer membership")
        members = dict(self.members)
        members[lid] = tuple(new_id if sid == old_id else sid for sid in members[lid])
        return replace(self, members=members)

    def remove_element(self, element_id):
        lid = self.layer_for(element_id)
        self.assert_editable(lid)
        members = dict(self.members)
        members[lid] = tuple(sid for sid in members[lid] if sid != element_id)
        return replace(self, members=members)

    def to_dict(self):
        return {"schema": LAYER_DOCUMENT_SCHEMA, "compositing": self.compositing,
                "layers": [n.to_dict() for n in self.layers],
                "members": {lid: list(ids) for lid, ids in self.members.items()},
                "active_layer_id": self.active_layer_id}

    @classmethod
    def from_dict(cls, raw):
        fields = {"schema", "compositing", "layers", "members", "active_layer_id"}
        if (not isinstance(raw, Mapping) or set(raw) != fields
                or raw["schema"] != LAYER_DOCUMENT_SCHEMA):
            raise ValueError("unsupported layer document schema or fields")
        if not isinstance(raw["layers"], (list, tuple)):
            raise ValueError("layer nodes require a sequence")
        return cls(tuple(LayerNode.from_dict(n) for n in raw["layers"]), raw["members"],
                   raw["active_layer_id"], raw["compositing"])


def _action_data(kind, data):
    if not isinstance(data, Mapping):
        raise ValueError("layer action data must be a mapping")
    data = _plain(data)
    fields = {
        "layer.enable": {"layer_id", "name"}, "layer.create": {"layer"},
        "layer.update": {"layer_id", "changes"},
        "layer.move": {"layer_id", "parent_id", "index"},
        "layer.assign": {"element_ids", "layer_id", "index"},
        "layer.delete": {"layer_id"}, "layer.active": {"layer_id"},
    }
    if set(data) != fields[kind]:
        raise ValueError(f"unsupported {kind} fields")
    if "layer_id" in data:
        _text(data["layer_id"], "layer_id")
    if kind == "layer.enable":
        _text(data["name"], "layer name", 256)
    elif kind == "layer.create":
        data["layer"] = LayerNode.from_dict(data["layer"]).to_dict()
    elif kind == "layer.update":
        changes = data["changes"]
        allowed = {"name", "visible", "locked", "opacity", "blend_mode"}
        if not isinstance(changes, Mapping) or not changes or set(changes) - allowed:
            raise ValueError("layer update requires supported explicit property changes")
        checked = replace(LayerNode(data["layer_id"], "Layer"), **changes)
        data["changes"] = {key: checked.to_dict()[key] for key in changes}
    elif kind == "layer.move":
        if data["parent_id"] is not None:
            _text(data["parent_id"], "parent_id")
        _index(data["index"], "layer insertion index")
    elif kind == "layer.assign":
        ids = data["element_ids"]
        if not isinstance(ids, (list, tuple)) or not ids:
            raise ValueError("layer assignment requires explicit current element IDs")
        ids = tuple(_text(sid, "element_id") for sid in ids)
        if len(set(ids)) != len(ids):
            raise ValueError("duplicate assigned element identity")
        data["element_ids"] = list(ids)
        if data["index"] is not None:
            _index(data["index"], "element insertion index")
    return data


@dataclass(frozen=True)
class LayerAction:
    action_id: str
    kind: str
    data: Mapping
    observation_id: str
    source_observation: str
    reason: str

    def __post_init__(self):
        for field in ("action_id", "observation_id"):
            _text(getattr(self, field), field)
        for field in ("source_observation", "reason"):
            _text(getattr(self, field), field, 2048)
        if not isinstance(self.kind, str) or self.kind not in LAYER_ACTION_KINDS:
            raise ValueError("unsupported layer action")
        object.__setattr__(self, "data", _freeze(_action_data(self.kind, self.data)))

    def payload(self):
        return _plain(self.data)

    def provenance(self):
        return {"action_id": self.action_id, "observation_id": self.observation_id,
                "source_observation": self.source_observation, "reason": self.reason}

    def to_dict(self):
        return {"schema": LAYER_ACTION_SCHEMA, "kind": self.kind,
                "data": self.payload(), **self.provenance()}

    @classmethod
    def from_dict(cls, raw):
        fields = {"schema", "kind", "data", "action_id", "observation_id",
                  "source_observation", "reason"}
        if (not isinstance(raw, Mapping) or set(raw) != fields
                or raw["schema"] != LAYER_ACTION_SCHEMA):
            raise ValueError("unsupported layer action schema or fields")
        return cls(**{key: raw[key] for key in fields - {"schema"}})


def element_id(element):
    return getattr(element, "element_id", getattr(element, "stroke_id", None))


def _renumber(nodes, parent_id, ordered_ids):
    ranks = {lid: i for i, lid in enumerate(ordered_ids)}
    return tuple(replace(n, order=ranks[n.layer_id]) if n.parent_id == parent_id else n for n in nodes)


def apply_layer_action(document, action, elements):
    """Reduce one typed layer event against current authoritative elements."""
    if not isinstance(action, LayerAction):
        raise ValueError("typed LayerAction required")
    elements = tuple(elements)
    ids = tuple(element_id(e) for e in elements)
    kind, data = action.kind, action.data
    if kind == "layer.enable":
        if document is not None:
            raise ValueError("document layers are already enabled")
        ordered = tuple(element_id(e) for e in sorted(elements, key=lambda e: e.layer))
        node = LayerNode(data["layer_id"], data["name"])
        result = LayerDocument((node,), {node.layer_id: ordered}, node.layer_id)
    else:
        if not isinstance(document, LayerDocument):
            raise ValueError("document layers must be enabled first")
        document.validate_elements(ids)
        nodes, members = list(document.layers), dict(document.members)
        active = document.active_layer_id
        if kind == "layer.create":
            node = LayerNode.from_dict(data["layer"])
            if any(n.layer_id == node.layer_id for n in nodes):
                raise ValueError("duplicate layer identity")
            if node.parent_id is not None:
                if document.node(node.parent_id).kind != "group":
                    raise ValueError("layer parent must be a group")
                document.assert_editable(node.parent_id)
            siblings = [n.layer_id for n in document.children(node.parent_id)]
            if node.order > len(siblings):
                raise ValueError("layer insertion index exceeds sibling count")
            siblings.insert(node.order, node.layer_id)
            nodes.append(node)
            nodes = _renumber(nodes, node.parent_id, siblings)
            if node.kind == "paint":
                members[node.layer_id] = ()
        elif kind == "layer.update":
            node = document.node(data["layer_id"])
            changes = dict(data["changes"])
            if "locked" in changes and any(n.locked for n in document.ancestors(node.layer_id)):
                raise ValueError("cannot change a layer lock under a locked ancestor")
            nodes = [replace(n, **changes) if n.layer_id == node.layer_id else n for n in nodes]
        elif kind == "layer.move":
            node = document.node(data["layer_id"])
            document.assert_editable(node.layer_id, descendants=True)
            parent = data["parent_id"]
            if parent is not None:
                if document.node(parent).kind != "group":
                    raise ValueError("layer parent must be a group")
                document.assert_editable(parent)
                if parent == node.layer_id or any(n.layer_id == node.layer_id for n in document.ancestors(parent)):
                    raise ValueError("cyclic layer hierarchy")
            old_siblings = [n.layer_id for n in document.children(node.parent_id) if n.layer_id != node.layer_id]
            nodes = [n for n in nodes if n.layer_id != node.layer_id]
            nodes = list(_renumber(nodes, node.parent_id, old_siblings))
            target = [n.layer_id for n in sorted(nodes, key=lambda n: n.order) if n.parent_id == parent]
            index = data["index"]
            if index > len(target):
                raise ValueError("layer insertion index exceeds sibling count")
            target.insert(index, node.layer_id)
            nodes.append(replace(node, parent_id=parent, order=index))
            nodes = _renumber(nodes, parent, target)
        elif kind == "layer.assign":
            lid, selected = data["layer_id"], tuple(data["element_ids"])
            if document.node(lid).kind != "paint":
                raise ValueError("element assignment requires a paint layer")
            document.assert_editable(lid)
            for sid in selected:
                document.assert_element_editable(sid)
            selected_set = set(selected)
            members = {key: tuple(sid for sid in values if sid not in selected_set)
                       for key, values in members.items()}
            index = len(members[lid]) if data["index"] is None else data["index"]
            if index > len(members[lid]):
                raise ValueError("element insertion index exceeds membership count")
            members[lid] = (*members[lid][:index], *selected, *members[lid][index:])
        elif kind == "layer.delete":
            node = document.node(data["layer_id"])
            document.assert_editable(node.layer_id, descendants=True)
            if document.children(node.layer_id) or members.get(node.layer_id):
                raise ValueError("only empty layers can be deleted")
            if node.layer_id == active:
                raise ValueError("select another active layer before deleting this layer")
            nodes = [n for n in nodes if n.layer_id != node.layer_id]
            members.pop(node.layer_id, None)
            siblings = [n.layer_id for n in document.children(node.parent_id) if n.layer_id != node.layer_id]
            nodes = _renumber(nodes, node.parent_id, siblings)
        elif kind == "layer.active":
            active = data["layer_id"]
            if document.node(active).kind != "paint":
                raise ValueError("active layer must be a paint layer")
        result = LayerDocument(tuple(nodes), members, active)
    result.validate_elements(ids)
    return result


__all__ = ["LayerNode", "LayerDocument", "LayerAction", "LAYER_ACTION_KINDS",
           "LAYER_ACTION_SCHEMA", "LAYER_DOCUMENT_SCHEMA", "LAYER_COMPOSITING",
           "MAX_LAYERS", "MAX_LAYER_DEPTH", "apply_layer_action"]
