from copy import deepcopy
import pytest

from img2drawing.core.action import AgentDrawingSession, DrawingAction
from img2drawing.core.material import InkPath, InkArea, InkElement, InkAction, MIXED_HISTORY_CONTRACT
from img2drawing.inspection import drawing_state_hash
from img2drawing.render import render_image
from img2drawing.session.editing import authored_elements
from img2drawing.timelapse.frames import inspect_fast_path_eligibility
from img2drawing.timelapse.replay import ForwardHistoryReplay


def _session():
    return AgentDrawingSession(64, 48, media_contract=MIXED_HISTORY_CONTRACT)


def _pencil(sid, aid, *, kind="draw_stroke", target=None):
    return DrawingAction(action_id=aid, kind=kind, stage="unspecified", role="form",
                         stroke_id=sid, target_stroke_id=target,
                         points=((3, 4), (24, 20)),
                         tool={"preset": "form_pencil", "grade": "HB"},
                         observation_id="o1", source_observation="explicit test",
                         revision_of=target, reason="test correction" if target else None)


def _ink(sid, aid, kind="ink.add", *, layer=0, paint="black", area=False):
    mark = (InkArea(((4, 4), (20, 4), (20, 20), (4, 20), (4, 4)), paint=paint)
            if area else InkPath(((4, 4), (24, 20)), (0, 1), 0.2, 3, paint=paint))
    return InkAction(aid, kind, sid,
                     None if kind == "ink.delete" else InkElement(sid, mark, "contour", "test", layer),
                     "o1", "explicit test", "author or correct")


def _ids(ir):
    return [getattr(e, "stroke_id", getattr(e, "element_id", None)) for e in ir.ordered_elements()]


def test_mixed_random_and_forward_replay_roundtrip():
    s = _session()
    actions = [_pencil("g1", "a1"), _ink("i1", "a2"), _pencil("g2", "a3"),
               _ink("i2", "a4", area=True), _ink("i1", "a5", "ink.replace", paint="white"),
               _pencil("g3", "a6", kind="replace_stroke", target="g1"),
               _ink("i2", "a7", "ink.delete")]
    s.execute_many_atomic(actions)
    recovered = AgentDrawingSession.from_dict(s.to_dict())
    forward = ForwardHistoryReplay(recovered.history)
    expected = [[], ["g1"], ["g1", "i1"], ["g1", "i1", "g2"],
                ["g1", "i1", "g2", "i2"], ["g1", "i1", "g2", "i2"],
                ["g3", "i1", "g2", "i2"], ["g3", "i1", "g2"]]
    for n, ids in enumerate(expected):
        direct, other = s.history.state_at(n), forward.state_at(n)
        assert _ids(direct) == ids == _ids(other)
        assert direct.to_dict() == other.to_dict()
        assert drawing_state_hash(direct) == drawing_state_hash(other)
    assert recovered.to_dict() == s.to_dict()
    assert s.history.state_at(2).ink_elements[0].mark.paint == "black"
    assert s.current_ir().ink_elements[0].mark.paint == "white"
    records = {e.element_id: e for e in authored_elements(s.history)}
    assert records["i1"].element_type == "ink"
    assert records["i1"].revision_count == 1
    assert records["i2"].status == "deleted"
    assert records["g1"].status == "superseded"
    assert records["i1"].action_ids == ("a2", "a5")


def test_ink_and_graphite_share_one_identity_space_and_atomic_rollback():
    s = _session()
    s.execute(_ink("i1", "a1"))
    before = s.to_dict()
    with pytest.raises(ValueError, match="already exists"):
        s.execute(_pencil("i1", "a2"))
    assert s.to_dict() == before
    with pytest.raises(ValueError, match="duplicate"):
        s.execute_many_atomic([_ink("i2", "a2"), _ink("i1", "a3")])
    assert s.to_dict() == before
    with pytest.raises(ValueError, match="missing stroke"):
        s.execute(_pencil("g1", "a2", kind="replace_stroke", target="i1"))
    s.execute(_ink("i1", "a2", "ink.delete"))
    with pytest.raises(ValueError, match="duplicate"):
        s.execute(_ink("i1", "a3"))
    with pytest.raises(ValueError, match="missing or wrong-media"):
        s.execute(_ink("i1", "a3", "ink.replace"))


def test_undo_redo_and_invalid_redo_tail_fail_closed():
    s = _session()
    s.execute_many_atomic([_ink("i1", "a1"), _ink("i1", "a2", "ink.replace", paint="white")])
    s.history.undo()
    assert s.current_ir().ink_elements[0].mark.paint == "black"
    payload = s.to_dict()
    resumed = AgentDrawingSession.from_dict(payload)
    resumed.history.redo()
    assert resumed.current_ir().ink_elements[0].mark.paint == "white"
    corrupted = deepcopy(payload)
    corrupted["history"]["actions"][1]["payload"]["element"]["mark"]["paint"] = "red"
    with pytest.raises(ValueError, match="ink paint"):
        AgentDrawingSession.from_dict(corrupted)
    wrong_media = deepcopy(payload)
    wrong_media["history"].pop("media_contract")
    with pytest.raises(ValueError, match="mixed history contract"):
        AgentDrawingSession.from_dict(wrong_media)
    missing_id = deepcopy(payload)
    missing_id["executed_action_ids"].remove("a2")
    with pytest.raises(ValueError, match="unregistered"):
        AgentDrawingSession.from_dict(missing_id)


@pytest.mark.parametrize("field,value", [("role", "different"), ("tool_state", {"mode": "draw"})])
def test_ink_record_provenance_must_agree_with_geometry(field, value):
    s = _session()
    s.execute(_ink("i1", "a1"))
    payload = s.to_dict()
    payload["history"]["actions"][0][field] = value
    with pytest.raises(ValueError, match="ink"):
        AgentDrawingSession.from_dict(payload)


def test_legacy_history_and_render_reject_mixed_mark_even_when_empty():
    legacy = AgentDrawingSession(64, 48)
    before = legacy.to_dict()
    with pytest.raises(ValueError, match="explicit mixed history"):
        legacy.execute(_ink("i1", "a1"))
    assert legacy.to_dict() == before
    assert "media_contract" not in legacy.history.to_dict()
    assert "ink_elements" not in legacy.current_ir().to_dict()
    s = _session()
    assert not inspect_fast_path_eligibility(s.history).eligible
    with pytest.raises(ValueError, match="mixed-media renderer"):
        render_image(s.current_ir(), supersample=2)
    s.execute(_ink("i1", "a1"))
    with pytest.raises(ValueError, match="mixed-media renderer"):
        render_image(s.current_ir(), supersample=2)


def test_typed_action_roundtrip_and_strict_fields():
    action = _ink("i1", "a1", area=True)
    assert InkAction.from_dict(action.to_dict()) == action
    raw = action.to_dict()
    raw["raster_mask"] = [[255]]
    with pytest.raises(ValueError, match="schema or fields"):
        InkAction.from_dict(raw)
    s = _session()
    s.execute(action.to_dict())
    assert s.current_ir().ink_elements == [action.element]


def test_legacy_authored_stroke_serialization_is_unchanged():
    old = AgentDrawingSession(64, 48)
    old.execute(_pencil("g1", "a1"))
    assert set(old.history.to_dict()) == {"width", "height", "metadata", "cursor", "actions"}
    assert set(old.current_ir().to_dict()) == {"width", "height", "metadata", "strokes"}
    assert AgentDrawingSession.from_dict(old.to_dict()).to_dict() == old.to_dict()
