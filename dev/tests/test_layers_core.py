"""Document ownership, lock enforcement and legacy-safe authoritative replay."""
from copy import deepcopy
from dataclasses import FrozenInstanceError, asdict

import pytest

from img2drawing.core.action import AgentDrawingSession, DrawingAction
from img2drawing.core.history import CanvasHistory
from img2drawing.core.ir import StrokeIR
from img2drawing.core.layers import (
    LAYER_COMPOSITING, LayerAction, LayerDocument, LayerNode,
)
from img2drawing.core.material import InkAction, InkElement, InkPath, MIXED_HISTORY_CONTRACT
from img2drawing.inspection import drawing_state_hash
from img2drawing.render.hand import grain_seed, hand_seed


def agent(mixed=False):
    return AgentDrawingSession(64, 48, media_contract=MIXED_HISTORY_CONTRACT if mixed else None)


def pencil(sid, aid, *, layer=0, target=None, metadata=None):
    return DrawingAction(aid, "draw_stroke" if target is None else "replace_stroke",
        "unspecified", role="form", part="study", points=((4., 8.), (28., 20.)),
        stroke_id=sid, target_stroke_id=target, revision_of=target, layer=layer,
        tool={"preset": "form_pencil", "grade": "HB"}, observation_id="o1",
        source_observation="explicit fixture", reason="edit study", metadata=metadata)


def ink(sid, aid, kind="ink.add", layer=0):
    mark = InkPath(((5., 9.), (30., 19.)), (.4, .7), .5, 3.)
    return InkAction(aid, kind, sid,
        None if kind == "ink.delete" else InkElement(sid, mark, "contour", "study", layer),
        "o1", "explicit fixture", "edit study")


def event(session, kind, data):
    return LayerAction(f"layer-{len(session.history.actions) + 1}", "layer." + kind,
                       data, "o1", "explicit fixture", "organize study")


def enable(session):
    session.execute(event(session, "enable", {"layer_id": "base", "name": "Imported Drawing"}))


def create(session, lid, *, parent=None, kind="paint", locked=False):
    order = len(session.history.layer_document.children(parent))
    node = LayerNode(lid, lid.title(), kind=kind, parent_id=parent, order=order, locked=locked)
    session.execute(event(session, "create", {"layer": node.to_dict()}))


def update(session, lid, **changes):
    session.execute(event(session, "update", {"layer_id": lid, "changes": changes}))


def assign(session, ids, lid, index=None):
    session.execute(event(session, "assign", {"element_ids": list(ids), "layer_id": lid, "index": index}))


@pytest.mark.parametrize("mixed", [False, True])
def test_no_layer_document_keeps_legacy_serialized_shape(mixed):
    session = agent(mixed)
    action = pencil("g", "g-add", layer=7)
    session.execute(action)
    raw = session.to_dict()
    ir = session.current_ir()
    assert "layer_document" not in ir.to_dict()
    assert "layer_id" not in asdict(action)
    assert set(raw["history"]) == ({"width", "height", "metadata", "cursor", "actions"}
                                  | ({"media_contract"} if mixed else set()))
    assert set(raw["history"]["actions"][0]["payload"]) == {"stroke"}
    assert not session.history.has_layer_actions
    assert session.history.layer_document is None
    recovered = AgentDrawingSession.from_dict(raw)
    assert recovered.to_dict() == raw
    assert drawing_state_hash(recovered.current_ir()) == drawing_state_hash(ir)
    before = session.to_dict()
    with pytest.raises(ValueError, match="enabled"):
        session.execute(pencil("other", "other-add"), layer_id="missing")
    assert session.to_dict() == before


@pytest.mark.parametrize("mixed", [False, True])
def test_enable_keeps_native_marks_and_imports_stable_render_order(mixed):
    session = agent(mixed)
    session.execute(pencil("upper", "g1", layer=5))
    session.execute(pencil("lower-first", "g2", layer=-2))
    session.execute(pencil("lower-second", "g3", layer=-2))
    if mixed:
        session.execute(ink("ink", "i1", layer=0))
    old = session.current_ir()
    old_actions = session.to_dict()["history"]["actions"]
    enable(session)
    now = session.current_ir()
    expected = ("lower-first", "lower-second", "ink", "upper") if mixed else (
        "lower-first", "lower-second", "upper")
    assert now.layer_document.members["base"] == expected
    assert [asdict(s) for s in now.strokes] == [asdict(s) for s in old.strokes]
    assert now.ink_elements == old.ink_elements
    assert session.to_dict()["history"]["actions"][:-1] == old_actions
    session.history.undo()
    assert session.current_ir().to_dict() == old.to_dict()
    assert not session.history.has_layer_actions
    session.history.redo()
    assert session.current_ir().layer_document.members["base"] == expected


@pytest.mark.parametrize("mixed", [False, True])
def test_routing_replacement_split_retirement_and_replay(mixed):
    session = agent(mixed)
    session.execute(pencil("g", "g-add", layer=4))
    enable(session)
    create(session, "lines")
    assign(session, ["g"], "lines")
    session.execute(pencil("second", "split-add", metadata={
        "split_fragment": "second", "geometry_edited_from": "g"}))
    assert session.history.actions[-1].payload["layer_id"] == "lines"
    session.execute(pencil("default", "default-add"))
    assert session.history.actions[-1].payload["layer_id"] == "base"
    session.execute(pencil("g-new", "g-replace", target="g", layer=4))
    assert session.history.layer_document.members["lines"] == ("g-new", "second")
    session.execute(pencil("second", "same-replace", target="second"))
    if mixed:
        session.execute(ink("ink", "ink-add"), layer_id="lines")
        assert session.history.actions[-1].payload["layer_id"] == "lines"
        session.execute(ink("ink", "ink-replace", "ink.replace"))
        session.execute(ink("ink", "ink-delete", "ink.delete"))
        assert "ink" not in session.history.layer_document.members["lines"]
    session.history.hard_delete("second", _eraser())
    assert session.history.layer_document.members["lines"] == ("g-new",)
    recovered = CanvasHistory.from_dict(session.history.to_dict())
    for cursor in range(session.history.cursor + 1):
        assert recovered.state_at(cursor).to_dict() == session.history.state_at(cursor).to_dict()


def _eraser():
    from img2drawing.core.tools import get_tool
    return get_tool("hard_eraser")


def test_layer_reordering_and_membership_do_not_change_native_seed_fields():
    session = agent(True)
    session.execute(pencil("a", "a-add", layer=8))
    session.execute(pencil("b", "b-add", layer=-4))
    enable(session)
    before = {s.stroke_id: (asdict(s), grain_seed(s), hand_seed(s)) for s in session.current_ir().strokes}
    create(session, "folder", kind="group")
    create(session, "lines", parent="folder")
    assign(session, ["a", "b"], "lines")
    assign(session, ["b"], "lines", index=0)
    session.execute(event(session, "move", {"layer_id": "folder", "parent_id": None, "index": 0}))
    document = session.history.layer_document
    assert [n.layer_id for n in document.children()] == ["folder", "base"]
    assert document.members["lines"] == ("b", "a")
    for stroke in session.current_ir().strokes:
        assert (asdict(stroke), grain_seed(stroke), hand_seed(stroke)) == before[stroke.stroke_id]


@pytest.mark.parametrize("mixed", [False, True])
def test_inherited_locks_block_content_structure_and_membership(mixed):
    session = agent(mixed)
    enable(session)
    create(session, "folder", kind="group")
    create(session, "lines", parent="folder")
    session.execute(event(session, "active", {"layer_id": "lines"}))
    session.execute(pencil("g", "g-add"))
    if mixed:
        session.execute(ink("i", "i-add"))
    update(session, "folder", locked=True)
    before = session.to_dict()
    next_id = session.history._next_id
    rejected = [
        pencil("new", "new-add"),
        pencil("g", "g-change", target="g"),
        event(session, "assign", {"element_ids": ["g"], "layer_id": "base", "index": None}),
        event(session, "move", {"layer_id": "lines", "parent_id": None, "index": 0}),
        event(session, "update", {"layer_id": "lines", "changes": {"locked": False}}),
    ]
    if mixed:
        rejected += [ink("i", "i-change", "ink.replace"), ink("i", "i-drop", "ink.delete")]
    for action in rejected:
        with pytest.raises(ValueError, match="locked"):
            session.execute(action)
        assert session.to_dict() == before
        assert session.history._next_id == next_id
    with pytest.raises(ValueError, match="locked"):
        session.history.hard_delete("g", _eraser())
    assert session.to_dict() == before
    # Deliberate display properties remain editable, including under a lock.
    update(session, "lines", name="Fine lines", visible=False, opacity=.5)
    assert not session.history.layer_document.node("lines").visible
    update(session, "folder", locked=False)
    session.execute(pencil("g", "g-change", target="g"))


@pytest.mark.parametrize("mixed", [False, True])
def test_atomic_batch_rolls_back_layers_marks_ids_and_redo_tail(mixed):
    session = agent(mixed)
    session.execute(pencil("g", "g-add"))
    enable(session)
    create(session, "lines")
    update(session, "base", locked=True)
    before = session.to_dict()
    batch = [event(session, "active", {"layer_id": "lines"}),
             pencil("new", "new-add"), pencil("g", "g-change", target="g")]
    with pytest.raises(ValueError, match="locked"):
        session.execute_many_atomic(batch)
    assert session.to_dict() == before
    session.history.undo()
    before = session.to_dict()
    with pytest.raises(ValueError, match="unknown layer"):
        create(session, "invalid", parent="unknown")
    assert session.to_dict() == before
    session.history.redo()
    assert session.history.layer_document.node("base").locked


@pytest.mark.parametrize("mixed", [False, True])
def test_redo_tail_rejects_forged_edits_under_locks(mixed):
    session = agent(mixed)
    session.execute(pencil("g", "g-add"))
    enable(session)
    session.execute(pencil("g", "g-change", target="g"))
    update(session, "base", locked=True)
    raw = session.history.to_dict()
    raw["actions"][2], raw["actions"][3] = raw["actions"][3], raw["actions"][2]
    for i, item in enumerate(raw["actions"], 1):
        item["seq"], item["logical_time"] = i, float(i - 1)
    raw["cursor"] = 2
    with pytest.raises(ValueError, match="locked"):
        CanvasHistory.from_dict(raw)


def test_empty_layers_remain_in_history_and_delete_requires_explicit_active_change():
    session = agent()
    enable(session)
    create(session, "empty")
    session.execute(event(session, "active", {"layer_id": "empty"}))
    with pytest.raises(ValueError, match="active"):
        session.execute(event(session, "delete", {"layer_id": "empty"}))
    session.execute(event(session, "active", {"layer_id": "base"}))
    before = session.current_ir().to_dict()
    session.execute(event(session, "delete", {"layer_id": "empty"}))
    assert [n.layer_id for n in session.history.layer_document.layers] == ["base"]
    session.history.undo()
    assert session.current_ir().to_dict() == before
    assert session.history.layer_document.members["empty"] == ()


@pytest.mark.parametrize("field,value", [
    ("visible", 1), ("locked", 0), ("opacity", True), ("opacity", float("nan")),
    ("opacity", float("inf")), ("opacity", 1.1), ("order", True),
    ("order", 1.0), ("order", -1), ("blend_mode", "multiply"),
])
def test_layer_node_validation_is_strict(field, value):
    with pytest.raises(ValueError):
        LayerNode("base", "Drawing", **{field: value})


def test_document_and_action_are_detached_immutable_validated_values():
    members = {"base": ["g"]}
    document = LayerDocument((LayerNode("base", "Drawing"),), members, "base")
    members["base"].append("injected")
    assert document.members["base"] == ("g",)
    with pytest.raises(TypeError):
        document.members["base"] = ()
    with pytest.raises(FrozenInstanceError):
        document.layers[0].visible = False
    raw = document.to_dict()
    assert LayerDocument.from_dict(raw) == document
    raw["members"]["base"].clear()
    assert document.members["base"] == ("g",)
    data = {"layer_id": "base", "changes": {"visible": False}}
    action = LayerAction("a", "layer.update", data, "o", "fixture", "edit")
    data["changes"]["visible"] = True
    assert action.data["changes"]["visible"] is False
    assert LayerAction.from_dict(action.to_dict()) == action
    with pytest.raises(TypeError):
        action.data["changes"]["visible"] = True
    malformed = document.to_dict()
    malformed["compositing"] = "future-compositor"
    with pytest.raises(ValueError, match="compositing"):
        LayerDocument.from_dict(malformed)
    assert document.compositing == LAYER_COMPOSITING


def test_document_rejects_cycles_membership_aliases_and_missing_live_elements():
    with pytest.raises(ValueError, match="cyclic"):
        LayerDocument((LayerNode("a", "A", "group", "b"), LayerNode("b", "B", "group", "a"),
                       LayerNode("base", "Base")), {"base": ()}, "base")
    with pytest.raises(ValueError, match="exactly one"):
        LayerDocument((LayerNode("a", "A"), LayerNode("b", "B", order=1)),
                      {"a": ("g",), "b": ("g",)}, "a")
    document = LayerDocument((LayerNode("base", "Base"),), {"base": ("g",)}, "base")
    with pytest.raises(ValueError, match="every current"):
        document.validate_elements(("g", "unassigned"))
    with pytest.raises(ValueError, match="membership"):
        StrokeIR(32, 32, layer_document=document).to_dict()


@pytest.mark.parametrize("mixed", [False, True])
def test_snapshots_and_resumed_documents_do_not_share_mutable_ownership(mixed):
    session = agent(mixed)
    enable(session)
    first = session.current_ir()
    session.execute(pencil("g", "g-add"))
    assert first.layer_document.members["base"] == ()
    state = session.current_ir().to_dict()
    restored = CanvasHistory.from_dict(deepcopy(session.history.to_dict()))
    assert restored.state_at().to_dict() == state
    returned = restored.layer_document.to_dict()
    returned["layers"][0]["locked"] = True
    assert not restored.layer_document.node("base").locked


@pytest.mark.parametrize("mixed", [False, True])
def test_layer_identity_is_reserved_after_delete_but_not_after_undone_creation(mixed):
    session = agent(mixed)
    enable(session)
    create(session, "temporary")
    session.execute(event(session, "delete", {"layer_id": "temporary"}))
    before = session.to_dict()
    with pytest.raises(ValueError, match="already used"):
        create(session, "temporary")
    assert session.to_dict() == before
    raw = session.history.to_dict()
    forged = deepcopy(raw["actions"][1])
    forged.update(seq=4, logical_time=3.)
    forged["provenance"]["action_id"] = "forged-recreation"
    raw["actions"].append(forged)
    raw["cursor"] = 1
    with pytest.raises(ValueError, match="already used"):
        CanvasHistory.from_dict(raw)
    session.history.undo(2)
    create(session, "temporary")
    assert session.history.layer_document.members["temporary"] == ()


@pytest.mark.parametrize("mixed", [False, True])
def test_split_routing_requires_current_source_and_preserves_rejected_state(mixed):
    session = agent(mixed)
    session.execute(pencil("g", "g-add"))
    enable(session)
    session.execute(pencil("replacement", "g-replace", target="g"))
    before = session.to_dict()
    for source in ("g", "unknown"):
        with pytest.raises(ValueError, match="membership"):
            session.execute(pencil("fragment", "fragment-add", metadata={
                "split_fragment": "second", "geometry_edited_from": source}))
        assert session.to_dict() == before


@pytest.mark.parametrize("mixed", [False, True])
def test_loaded_layered_additions_cannot_omit_or_forge_membership_routes(mixed):
    session = agent(mixed)
    enable(session)
    session.execute(pencil("g", "g-add"))
    raw = session.history.to_dict()
    raw["actions"][-1]["payload"].pop("layer_id")
    with pytest.raises(ValueError, match="recorded layer_id"):
        CanvasHistory.from_dict(raw)
    raw = session.history.to_dict()
    raw["actions"][-1]["payload"]["layer_id"] = "missing"
    with pytest.raises(ValueError, match="unknown layer"):
        CanvasHistory.from_dict(raw)


@pytest.mark.parametrize("mixed", [False, True])
def test_locked_descendant_blocks_group_structure_but_display_properties_are_explicit(mixed):
    session = agent(mixed)
    enable(session)
    create(session, "folder", kind="group")
    create(session, "lines", parent="folder", locked=True)
    before = session.to_dict()
    with pytest.raises(ValueError, match="locked"):
        session.execute(event(session, "move", {"layer_id": "folder", "parent_id": None, "index": 0}))
    assert session.to_dict() == before
    update(session, "lines", visible=False, opacity=.3, name="Protected lines")
    update(session, "lines", locked=False)
    update(session, "folder", locked=True)
    before = session.to_dict()
    with pytest.raises(ValueError, match="ancestor"):
        update(session, "lines", locked=True)
    assert session.to_dict() == before
    update(session, "lines", opacity=.7)


@pytest.mark.parametrize("field,value", [
    ("tool_state", {"tool": "form_pencil"}), ("role", "form"), ("part", "study"),
])
def test_raw_layer_records_reject_element_only_fields(field, value):
    session = agent(True)
    enable(session)
    raw = session.history.to_dict()
    raw["actions"][0][field] = value
    with pytest.raises(ValueError, match="typed layer"):
        CanvasHistory.from_dict(raw)


def test_layer_action_decode_rejects_unknown_fields_and_falsey_boolean_coercion():
    action = LayerAction("a", "layer.update", {"layer_id": "base", "changes": {"visible": False}},
                         "o", "fixture", "edit")
    raw = action.to_dict()
    raw["data"]["changes"]["visible"] = 0
    with pytest.raises(ValueError, match="boolean"):
        LayerAction.from_dict(raw)
    raw = action.to_dict()
    raw["extra"] = True
    with pytest.raises(ValueError, match="fields"):
        LayerAction.from_dict(raw)


def test_explicit_conversion_rejects_unrepresentable_legacy_ids_without_rewriting_them():
    session = agent()
    long_id = "g" * 129
    session.execute(pencil(long_id, "long-id-add"))
    before = session.to_dict()
    with pytest.raises(ValueError, match="element_id"):
        enable(session)
    assert session.to_dict() == before
    assert session.current_ir().strokes[0].stroke_id == long_id


@pytest.mark.parametrize("retirement", ["replace", "delete"])
def test_layered_graphite_replay_reserves_retired_element_identities(retirement):
    session = agent()
    session.execute(pencil("g", "g-add"))
    enable(session)
    if retirement == "replace":
        session.execute(pencil("g-new", "g-replace", target="g"))
    else:
        session.history.hard_delete("g", _eraser())
    raw = session.history.to_dict()
    forged = deepcopy(raw["actions"][0])
    forged.update(seq=4, logical_time=3.)
    forged["provenance"]["action_id"] = "forged-reuse"
    forged["payload"]["layer_id"] = "base"
    raw["actions"].append(forged)
    raw["cursor"] = 2
    with pytest.raises(ValueError, match="duplicate layered stroke"):
        CanvasHistory.from_dict(raw)


def test_layer_enable_rejects_earlier_identity_reuse_without_changing_unlayered_replay():
    session = agent()
    session.execute(pencil("g", "g-add"))
    session.execute(pencil("g-new", "g-replace", target="g"))
    raw = session.history.to_dict()
    reused = deepcopy(raw["actions"][0])
    reused.update(seq=3, logical_time=2.)
    reused["provenance"]["action_id"] = "historical-reuse"
    raw["actions"].append(reused)
    raw["cursor"] = 3
    history = CanvasHistory.from_dict(raw)
    # The old, unlayered replay contract remains untouched for existing files.
    assert [s.stroke_id for s in history.state_at().strokes] == ["g-new", "g"]
    before = history.to_dict()
    conversion = LayerAction("enable", "layer.enable", {"layer_id": "base", "name": "Drawing"},
                             "o1", "fixture", "enable document editing")
    with pytest.raises(ValueError, match="duplicate layered stroke"):
        history.apply_layer_action(conversion)
    assert history.to_dict() == before


def test_layered_candidate_append_cannot_create_an_unresumable_duplicate_action():
    session = agent()
    session.execute(pencil("g", "g-add"))
    enable(session)
    before = session.to_dict()
    with pytest.raises(ValueError, match="duplicate layered action"):
        session.history.add_stroke(session.current_ir().strokes[0], stroke_id="new",
                                   provenance={"action_id": "g-add"})
    assert session.to_dict() == before


@pytest.mark.parametrize("cursor", [True, -1, 99, 1.5])
def test_layered_graphite_cursor_is_not_silently_coerced_or_clamped(cursor):
    session = agent()
    enable(session)
    raw = session.history.to_dict()
    raw["cursor"] = cursor
    with pytest.raises(ValueError, match="layered history cursor"):
        CanvasHistory.from_dict(raw)
