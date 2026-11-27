"""Unified authored transforms preserve policies and commit all media atomically."""
from dataclasses import FrozenInstanceError, asdict, replace

import numpy as np
import pytest
from PIL import Image

from img2drawing import DrawingSession, RenderProfile
from img2drawing.authoring import (
    ContactWidthProfile, SemanticGroup, StrokeEdit, apply_ink_actions,
    apply_stroke_edits, inspect_semantic_groups, record_semantic_groups,
)
from img2drawing.authoring.element_edits import (
    ElementEditProposal, apply_element_edits, prepare_element_edits,
    prepare_element_group_transform, prepare_element_transform,
    preview_element_edits,
)
from img2drawing.core.contact_width import profile_from_stroke
from img2drawing.core.material import (
    InkAction, InkArea, InkElement, Screentone, StyledInkPath, ToneGradient,
)
from img2drawing.render.ink import build_ink_patch


def rect(x0, y0, x1, y1):
    return ((x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0))


def make(tmp_path):
    ref = tmp_path / "reference.png"
    Image.new("RGB", (128, 96), "white").save(ref)
    session = DrawingSession.create(subject=ref, output_dir=tmp_path / "session",
        render_profile=RenderProfile.mixed_media(128, 96, supersample=4))
    oid = session.observe({"fixture": "explicit mixed transform swatch"})
    width = ContactWidthProfile(((0., .4), (.5, 1.), (1., .5)))
    session.draw(((10, 10), (20, 16), (30, 12)), stroke_id="g", action_id="add-g",
                 pressure=(.2, .7, .4), tool_overrides={"width": 3., "opacity": .6},
                 metadata=width.metadata(), layer=-1, observation_id=oid)
    marks = [
        ("path", StyledInkPath(((12, 23), (25, 26), (38, 21)), (.2, .8, .5),
                              1., 5., start_cap="butt", end_cap="square", join="bevel")),
        ("area", InkArea(rect(45, 8, 65, 25), (rect(50, 12, 55, 18),), paint="white")),
        ("tone", Screentone(rect(10, 36, 42, 62), holes=(rect(20, 43, 26, 49),),
                            pitch=8., angle_degrees=19.,
                            phase_origin=(.37, .61),
                            gradient=ToneGradient((0, 36), (62, 62), .2, .8))),
    ]
    apply_ink_actions(session, [
        InkAction("add-" + sid, "ink.add", sid, InkElement(sid, mark, "value", "swatch", i),
                  oid, "explicit swatch", "author mixed study")
        for i, (sid, mark) in enumerate(marks)
    ])
    session.draw(((70, 72), (86, 82)), stroke_id="unrelated", action_id="add-unrelated",
                 layer=3, observation_id=oid)
    return session, oid, ref


def proposal(session, oid, ids=("g", "path", "area", "tone"),
             matrix=(1., 0., 0., 1., 3., 2.), **kwargs):
    return prepare_element_transform(session, ids, matrix,
        action_ids=tuple("move-" + sid for sid in ids), observation_id=oid,
        reason="correct explicit group geometry", **kwargs)


def elements(session):
    snapshot = session.current_ir()
    return {**{s.stroke_id: s for s in snapshot.strokes},
            **{e.element_id: e for e in snapshot.ink_elements}}


def unchanged(session, before, checkpoint):
    assert session._agent.to_dict() == before
    assert session.checkpoint_path.read_bytes() == checkpoint


def native_tone(mark):
    bounds, patch = build_ink_patch(mark, factor=4, hi_size=(512, 384))
    result = np.zeros((384, 512), dtype=np.uint8)
    with patch:
        x0, y0, x1, y1 = bounds
        if x1 > x0 and y1 > y0:
            result[y0:y1, x0:x1] = np.asarray(patch)[:, :, 3]
    return result


def test_mixed_group_preview_commit_resume_and_history(tmp_path, monkeypatch):
    session, oid, ref = make(tmp_path)
    plan = record_semantic_groups(session,
        [SemanticGroup("study", ("tone", "g", "area", "path"))],
        evidence="explicit mixed group membership")
    original = session.current_ir().to_dict()
    unrelated = asdict(elements(session)["unrelated"])
    signature = inspect_semantic_groups(session, plan)["groups"]["study"]["signature"]
    before, checkpoint = session._agent.to_dict(), session.checkpoint_path.read_bytes()
    edit = prepare_element_group_transform(session, plan, "study", (1, 0, 0, 1, 3, 2),
        action_ids=("move-tone", "move-g", "move-area", "move-path"),
        observation_id=oid, reason="move the exact mixed membership")
    assert isinstance(edit, ElementEditProposal)
    preview = preview_element_edits(session, edit, tmp_path / "preview.png")
    unchanged(session, before, checkpoint)
    calls = []
    commit = session._commit

    def counted(actions):
        calls.append(tuple(a.action_id for a in actions))
        return commit(actions)

    monkeypatch.setattr(session, "_commit", counted)
    ids = apply_element_edits(session, edit)
    assert calls == [ids] == [("move-tone", "move-g", "move-area", "move-path")]
    current = session.current_ir().to_dict()
    assert current["element_order"] == original["element_order"]
    assert asdict(elements(session)["unrelated"]) == unrelated
    assert all(elements(session)[sid].layer == layer
               for sid, layer in (("g", -1), ("path", 0), ("area", 1), ("tone", 2)))
    rendered = session.render_final(tmp_path / "committed.png")
    assert preview["pixel_sha256"] == rendered.pixel_sha256
    assert preview["prospective_state_hash"] == session.drawing_state_hash()
    report = inspect_semantic_groups(session, plan)["groups"]["study"]
    assert report["signature"] != signature and report["review_required"]
    resumed = DrawingSession.resume(session.checkpoint(), subject=ref)
    assert resumed.current_ir().to_dict() == current
    assert resumed.render_final(tmp_path / "resumed.png").pixel_sha256 == rendered.pixel_sha256
    resumed._agent.history.undo(len(ids))
    assert resumed.current_ir().to_dict() == original
    resumed._agent.history.redo(len(ids))
    assert resumed.current_ir().to_dict() == current


@pytest.mark.parametrize("width_policy, factor", [("preserve", 1.), ("scale", 1.25)])
def test_width_policy_matches_graphite_and_styled_ink(tmp_path, width_policy, factor):
    session, oid, _ = make(tmp_path)
    session.soft_lift("g", strength=.3, observation_id=oid, reason="preserve lifted material")
    old = elements(session)
    edit = proposal(session, oid, matrix=(1.25, 0, 0, 1.25, 2, 3), width_policy=width_policy)
    apply_element_edits(session, edit)
    new = elements(session)
    assert new["g"].width == pytest.approx(old["g"].width * factor)
    assert new["g"].opacity == old["g"].opacity
    assert new["g"].pressure == old["g"].pressure
    assert profile_from_stroke(new["g"]) == profile_from_stroke(old["g"])
    path, original = new["path"].mark, old["path"].mark
    assert isinstance(path, StyledInkPath)
    assert (path.start_cap, path.end_cap, path.join) == ("butt", "square", "bevel")
    assert path.min_width == pytest.approx(original.min_width * factor)
    assert path.max_width == pytest.approx(original.max_width * factor)
    assert path.pressure == original.pressure
    assert new["g"].points[0] == (14.5, 15.5)
    tone, original_tone = new["tone"].mark, old["tone"].mark
    assert tone.pitch == original_tone.pitch
    assert tone.phase_origin == original_tone.phase_origin
    assert tone.gradient == original_tone.gradient


def test_object_following_tone_scales_phase_angle_gradient_and_holes(tmp_path):
    session, oid, _ = make(tmp_path)
    old = elements(session)["tone"].mark
    # Clockwise 90 degrees and scale two, with explicit page translation.
    edit = proposal(session, oid, ids=("tone",), matrix=(0, -2, 2, 0, 130, 5),
                    tone_policy="object")
    tone = edit.actions[0].element.mark
    assert tone.pitch == 2 * old.pitch
    assert tone.angle_degrees == pytest.approx(109.)
    assert tone.phase_origin == pytest.approx((128.78, 5.74))
    assert tone.outer[0] == (58., 25.)
    assert tone.holes[0][0] == (44., 45.)
    assert tone.gradient.start == (58., 5.)
    assert tone.gradient.end == (6., 129.)
    assert tone.gradient.start_coverage == old.gradient.start_coverage
    assert tone.gradient.end_coverage == old.gradient.end_coverage


@pytest.mark.parametrize("constant", [False, True])
def test_object_tone_reflection_and_translation_match_native_pixels(tmp_path, constant):
    session, oid, _ = make(tmp_path)
    old = elements(session)["tone"].mark
    if constant:
        old = replace(old, gradient=None, coverage=.57)
        apply_ink_actions(session, [InkAction("constant-tone", "ink.replace", "tone",
            replace(elements(session)["tone"], mark=old), oid, "explicit screen", "constant patch")])
    baseline = native_tone(old)
    reflected = proposal(session, oid, ids=("tone",), matrix=(-1, 0, 0, 1, 128, 0),
                         tone_policy="object").actions[0].element.mark
    assert np.array_equal(native_tone(reflected), baseline[:, ::-1])
    translated = proposal(session, oid, ids=("tone",), matrix=(1, 0, 0, 1, 7, 5),
                          tone_policy="object").actions[0].element.mark
    assert np.array_equal(native_tone(translated)[20:, 28:], baseline[:-20, :-28])
    fixed = proposal(session, oid, ids=("tone",), matrix=(1, 0, 0, 1, 7, 5),
                     tone_policy="page").actions[0].element.mark
    assert not np.array_equal(native_tone(fixed), native_tone(translated))
    assert fixed.phase_origin == old.phase_origin and fixed.gradient == old.gradient


def test_area_and_page_tone_accept_affine_but_paths_and_object_tone_refuse(tmp_path):
    session, oid, _ = make(tmp_path)
    shear = (1, .3, 0, 1.2, 2, 1)
    before, checkpoint = session._agent.to_dict(), session.checkpoint_path.read_bytes()
    edit = proposal(session, oid, ids=("area", "tone"), matrix=shear)
    area, tone = (a.element.mark for a in edit.actions)
    assert area.outer[0] == pytest.approx((49.4, 10.6))
    assert area.holes[0][0] == pytest.approx((55.6, 15.4))
    assert tone.phase_origin == elements(session)["tone"].mark.phase_origin
    for ids, policy in ((("g",), "page"), (("path",), "page"),
                        (("tone",), "object"), (("area", "g"), "page")):
        with pytest.raises(ValueError, match="similarity"):
            proposal(session, oid, ids=ids, matrix=shear, tone_policy=policy)
        unchanged(session, before, checkpoint)


@pytest.mark.parametrize("change, message", [
    ("cursor", "cursor"), ("state", "state"), ("profile", "profile"),
    ("action", "prepared actions"),
])
def test_preview_and_apply_reject_every_stale_receipt(tmp_path, change, message):
    session, oid, _ = make(tmp_path)
    edit = proposal(session, oid)
    if change == "cursor":
        session.draw(((80, 5), (90, 9)), stroke_id="extra", observation_id=oid)
    elif change == "state":
        # A branch can reach the same cursor with different drawing truth.
        session._agent.history.undo()
        session.draw(((80, 5), (90, 9)), stroke_id="branch", observation_id=oid)
        assert session.history_cursor == edit.base_cursor
    elif change == "profile":
        session._render_profile = replace(session.render_profile, background_rgba=(240, 240, 240, 255))
    else:
        edit.actions[0].metadata["unexpected_edit"] = True
    before, checkpoint = session._agent.to_dict(), session.checkpoint_path.read_bytes()
    for apply in (lambda: preview_element_edits(session, edit, tmp_path / "stale.png"),
                  lambda: apply_element_edits(session, edit)):
        with pytest.raises(ValueError, match=message):
            apply()
        unchanged(session, before, checkpoint)
    assert not (tmp_path / "stale.png").exists()


def test_proposal_detaches_input_and_rejects_field_assignment(tmp_path):
    session, oid, _ = make(tmp_path)
    action = proposal(session, oid, ids=("g",)).actions[0]
    edit = prepare_element_edits(session, [action])
    action.metadata["caller_mutation"] = "does not touch receipt"
    assert "caller_mutation" not in edit.actions[0].metadata
    with pytest.raises(FrozenInstanceError):
        edit.base_cursor = 0
    apply_element_edits(session, edit)


def test_invalid_final_action_and_failed_checkpoint_preserve_redo_tail(tmp_path, monkeypatch):
    session, oid, _ = make(tmp_path)
    session._agent.history.undo()
    session.checkpoint()
    before, checkpoint = session._agent.to_dict(), session.checkpoint_path.read_bytes()
    records = tuple(session._agent.history.actions)
    edit = proposal(session, oid, ids=("g", "path"))
    invalid = replace(edit.actions[1], element_id="missing",
                      element=replace(edit.actions[1].element, element_id="missing"))
    with pytest.raises(ValueError, match="missing or wrong-media"):
        prepare_element_edits(session, (edit.actions[0], invalid))
    unchanged(session, before, checkpoint)

    def failed_write(*args, **kwargs):
        raise OSError("injected checkpoint failure after all edits")

    with monkeypatch.context() as patch:
        patch.setattr(session, "_write_checkpoint", failed_write)
        with pytest.raises(OSError, match="checkpoint failure"):
            apply_element_edits(session, edit)
    unchanged(session, before, checkpoint)
    assert all(a is b for a, b in zip(records, session._agent.history.actions))
    session._agent.history.redo()
    assert "unrelated" in elements(session)


@pytest.mark.parametrize("ids, matrix, options, message", [
    (("g", "missing"), (1, 0, 0, 1, 0, 0), {}, "current element"),
    (("g", "g"), (1, 0, 0, 1, 0, 0), {}, "unique identities"),
    (("g",), (1, 0, 0, 0, 0, 0), {}, "nonsingular"),
    (("g",), (True, 0, 0, 1, 0, 0), {}, "finite number"),
    (("g",), (1, 0, 0, 1, 200, 0), {}, "out of canvas"),
    (("tone",), (.1, 0, 0, .1, 0, 0), {"tone_policy": "object"}, "pitch"),
    (("g",), (1, 0, 0, 1, 0, 0), {"width_policy": "auto"}, "width_policy"),
    (("tone",), (1, 0, 0, 1, 0, 0), {"tone_policy": "auto"}, "tone_policy"),
])
def test_invalid_transform_has_no_partial_state(tmp_path, ids, matrix, options, message):
    session, oid, _ = make(tmp_path)
    before, checkpoint = session._agent.to_dict(), session.checkpoint_path.read_bytes()
    with pytest.raises(ValueError, match=message):
        proposal(session, oid, ids=ids, matrix=matrix, **options)
    unchanged(session, before, checkpoint)


def test_invalid_provenance_action_identity_and_work_budget(tmp_path, monkeypatch):
    session, oid, _ = make(tmp_path)
    before, checkpoint = session._agent.to_dict(), session.checkpoint_path.read_bytes()
    for aids, observation, message in ((["add-g"], oid, "duplicate action_id"),
                                       (["new"], "unknown", "observation_id"),
                                       (["new", "other"], oid, "one explicit action")):
        with pytest.raises(ValueError, match=message):
            prepare_element_transform(session, ["g"], (1, 0, 0, 1, 1, 1),
                action_ids=aids, observation_id=observation, reason="test invalid receipt")
        unchanged(session, before, checkpoint)
    from img2drawing.render import ink
    monkeypatch.setattr(ink, "MAX_KERNEL_WORK", 1)
    with pytest.raises(ValueError, match="work budget"):
        proposal(session, oid, ids=("g", "path"))
    unchanged(session, before, checkpoint)


def test_path_eraser_requires_explicit_reauthoring(tmp_path):
    session, oid, _ = make(tmp_path)
    session.erase_path(((5, 5), (15, 12)), stroke_id="eraser", width=4.,
                       observation_id=oid, reason="explicit graphite lift")
    before, checkpoint = session._agent.to_dict(), session.checkpoint_path.read_bytes()
    with pytest.raises(ValueError, match="path eraser"):
        proposal(session, oid, ids=("g", "eraser"))
    unchanged(session, before, checkpoint)


def test_semantic_group_missing_and_unassigned_split_block_transform(tmp_path):
    session, oid, _ = make(tmp_path)
    plan = record_semantic_groups(session, [SemanticGroup("mixed", ("g", "tone"))],
                                  evidence="explicit mixed membership")
    apply_stroke_edits(session, [StrokeEdit("g", tuple(elements(session)["g"].points),
                                           split_at=1, new_stroke_id="tail")],
                       reason="split needs new membership", observation_id=oid)
    before, checkpoint = session._agent.to_dict(), session.checkpoint_path.read_bytes()
    with pytest.raises(ValueError, match="redeclare"):
        prepare_element_group_transform(session, plan, "mixed", (1, 0, 0, 1, 1, 0),
            action_ids=("a", "b"), observation_id=oid, reason="blocked group")
    unchanged(session, before, checkpoint)
    fresh = record_semantic_groups(session, [SemanticGroup("mixed", ("g", "tail", "tone"))],
                                   evidence="explicit split membership")
    session.delete_stroke("g", observation_id=oid, reason="reopen shape")
    before, checkpoint = session._agent.to_dict(), session.checkpoint_path.read_bytes()
    with pytest.raises(ValueError, match="redeclare"):
        prepare_element_group_transform(session, fresh, "mixed", (1, 0, 0, 1, 1, 0),
            action_ids=("a", "b"), observation_id=oid, reason="blocked missing member")
    unchanged(session, before, checkpoint)


def test_layer_actions_are_rejected_by_element_only_proposals(tmp_path):
    from img2drawing.core.layers import LayerAction
    session, oid, _ = make(tmp_path)
    action = LayerAction("enable", "layer.enable", {"layer_id": "drawing", "name": "Drawing"},
                         oid, "explicit layer action", "enable document layers")
    before, checkpoint = session._agent.to_dict(), session.checkpoint_path.read_bytes()
    with pytest.raises(ValueError, match="typed DrawingAction or InkAction"):
        prepare_element_edits(session, [action])
    unchanged(session, before, checkpoint)


@pytest.mark.parametrize("lock_id", ["leaf", "group"])
def test_layer_and_inherited_locks_block_entire_mixed_selection(tmp_path, lock_id):
    session, oid, _ = make(tmp_path)
    session.enable_layers(observation_id=oid)
    session.create_layer("group", "Protected", kind="group", observation_id=oid)
    session.create_layer("leaf", "Ink and tone", parent_id="group", observation_id=oid)
    session.assign_elements(("path", "tone"), "leaf", observation_id=oid)
    edit = proposal(session, oid, ids=("g", "path", "tone"))
    membership = session.layer_document.members
    session.update_layer(lock_id, locked=True, observation_id=oid)
    before, checkpoint = session._agent.to_dict(), session.checkpoint_path.read_bytes()
    with pytest.raises(ValueError, match="stale element edit cursor"):
        apply_element_edits(session, edit)
    with pytest.raises(ValueError, match="locked"):
        proposal(session, oid, ids=("g", "path", "tone"))
    unchanged(session, before, checkpoint)
    # Caller-supplied guards cannot bypass authoritative lock enforcement.
    # The first graphite replacement is editable; the later ink edit must
    # roll it back even if the caller deliberately rebinds an old receipt.
    rebound = replace(edit, base_cursor=session.history_cursor,
                      base_state_hash=session.drawing_state_hash())
    with pytest.raises(ValueError, match="locked"):
        apply_element_edits(session, rebound)
    unchanged(session, before, checkpoint)
    session.update_layer(lock_id, locked=False, observation_id=oid)
    apply_element_edits(session, proposal(session, oid, ids=("g", "path", "tone")))
    assert session.layer_document.members == membership
