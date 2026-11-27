from copy import deepcopy
import json
from pathlib import Path
import shutil
import zipfile

import pytest
from PIL import Image

from img2drawing import DrawingIntent, DrawingSession, RenderProfile
from img2drawing.authoring import (
    InkAction, InkArea, InkElement, LayerAction, SemanticGroup,
    apply_ink_actions, preview_ink_actions, record_semantic_groups, inspect_semantic_groups,
)
from img2drawing.core.digest import sha256_file
from img2drawing.runtime import runtime_capabilities


def make(tmp_path):
    ref = tmp_path / "reference.png"
    Image.new("RGB", (64, 48), "white").save(ref)
    session = DrawingSession.create(subject=ref, output_dir=tmp_path / "session",
        render_profile=RenderProfile.mixed_media(64, 48, supersample=2))
    oid = session.observe({"test": "explicit editable shapes"})
    session.draw([(5, 12), (55, 32)], stroke_id="g", observation_id=oid)
    return session, oid, ref


def ink(oid, aid="ink", eid="i"):
    mark = InkArea(((10, 10), (38, 10), (38, 30), (10, 30), (10, 10)))
    return InkAction(aid, "ink.add", eid, InkElement(eid, mark, "form", "shape", 7),
                     oid, "explicit test form", "add an editable ink area")


def test_optional_layer_facade_roundtrip_and_routing(tmp_path):
    session, oid, ref = make(tmp_path)
    assert session.layer_document is None
    assert "layer_document" not in session.current_ir().to_dict()
    before = session.render_final(tmp_path / "before.png")
    original = session.current_ir().strokes[0]
    session.enable_layers(name="Pencil", observation_id=oid)
    assert session.render_final(tmp_path / "converted.png").pixel_sha256 == before.pixel_sha256
    session.create_layer("group", "Character", kind="group")
    session.create_layer("ink", "Ink & <tone>", parent_id="group")
    session.set_active_layer("ink")
    session.draw_many([
        {"points": [(3, 40), (40, 40)], "stroke_id": "in-active"},
        {"points": [(3, 42), (40, 42)], "stroke_id": "in-pencil", "layer_id": "drawing"},
    ], observation_id=oid)
    apply_ink_actions(session, [ink(oid)], layer_id="drawing")
    assert session.layer_document.members == {
        "drawing": ("g", "in-pencil", "i"), "ink": ("in-active",),
    }
    session.assign_elements(["g", "i"], "ink", index=0)
    assert session.layer_document.members["ink"] == ("g", "i", "in-active")
    assert session.current_ir().strokes[0] == original
    session.move_layer("ink", index=0)
    session.delete_layer("group")
    session.update_layer("ink", name="Editable result", opacity=.7, visible=False)
    revived = DrawingSession.resume(session.checkpoint(), subject=ref)
    assert revived.current_ir().to_dict() == session.current_ir().to_dict()
    assert revived.layer_document.node("ink").name == "Editable result"
    assert revived.render_final(tmp_path / "resume.png").pixel_sha256 == session.render_final(
        tmp_path / "current.png").pixel_sha256


def test_typed_layer_batch_rolls_back_checkpoint_and_redo_on_failure(tmp_path, monkeypatch):
    session, oid, _ = make(tmp_path)
    session.enable_layers()
    session.create_layer("other", "Other")
    session.undo()
    before, checkpoint = deepcopy(session._agent.to_dict()), session.checkpoint_path.read_bytes()
    actions = (
        LayerAction("rename", "layer.update", {"layer_id": "drawing", "changes": {"name": "Changed"}},
                    oid, "test", "rename"),
        LayerAction("bad", "layer.assign", {"layer_id": "drawing", "element_ids": ["absent"], "index": None},
                    oid, "test", "invalid last member"),
    )
    with pytest.raises(ValueError):
        session.apply_layer_actions(actions)
    assert session._agent.to_dict() == before
    assert session.checkpoint_path.read_bytes() == checkpoint
    with pytest.raises(ValueError, match="stale"):
        session.apply_layer_actions(actions[:1], expected_cursor=0)
    def fail(*args):
        raise OSError("checkpoint write failed")
    monkeypatch.setattr(session, "_write_checkpoint", fail)
    with pytest.raises(OSError, match="checkpoint"):
        session.apply_layer_actions(actions[:1])
    assert session._agent.to_dict() == before
    assert session.checkpoint_path.read_bytes() == checkpoint


def test_ink_routing_is_preview_bound_and_inherited_lock_blocks_add(tmp_path):
    session, oid, _ = make(tmp_path)
    session.enable_layers()
    session.create_layer("group", "Locked parent", kind="group")
    session.create_layer("ink", "Ink", parent_id="group")
    action = ink(oid)
    receipt = preview_ink_actions(session, [action], tmp_path / "preview.png", layer_id="ink")
    with pytest.raises(ValueError, match="differs"):
        apply_ink_actions(session, [action], layer_id="drawing", expected_action_digest=receipt["action_digest"])
    apply_ink_actions(session, [action], layer_id="ink", expected_action_digest=receipt["action_digest"])
    assert session.render_final(tmp_path / "applied.png").pixel_sha256 == receipt["pixel_sha256"]
    session.update_layer("group", locked=True)
    before = session.checkpoint_path.read_bytes()
    with pytest.raises(ValueError, match="locked"):
        session.draw_many([
            {"points": [(2, 2), (10, 10)], "stroke_id": "first", "layer_id": "drawing"},
            {"points": [(4, 2), (14, 10)], "stroke_id": "last", "layer_id": "ink"},
        ], observation_id=oid)
    assert session.checkpoint_path.read_bytes() == before
    assert "first" not in {s.stroke_id for s in session.current_ir().strokes}


def test_semantic_signature_tracks_visual_layer_context(tmp_path):
    session, oid, _ = make(tmp_path)
    plan = record_semantic_groups(session, [SemanticGroup("shape", ("g",))], evidence="shape is selected")
    def signature():
        return inspect_semantic_groups(session, plan)["groups"]["shape"]["signature"]
    legacy = signature()
    session.enable_layers()
    layered = signature()
    assert layered != legacy
    session.update_layer("drawing", name="New display name", locked=True)
    assert signature() == layered
    session.update_layer("drawing", opacity=.5)
    assert signature() != layered


@pytest.mark.parametrize("format", ["png", "ora"])
def test_session_export_keeps_native_checkpoint_and_canonical_merge(tmp_path, format):
    session, oid, ref = make(tmp_path)
    session.enable_layers()
    session.create_layer("ink", "Ink")
    apply_ink_actions(session, [ink(oid)], layer_id="ink")
    session.update_layer("ink", opacity=.65)
    session.inspect()
    session.record_evidence_read(session.inspection_history[-1]["inspection_id"], artifact="raw_drawing")
    before = session.checkpoint_path.read_bytes()
    final = session.render_final(tmp_path / "final.png")
    target = tmp_path / ("delivery" if format == "png" else "delivery.ora")
    export = session.export_layer_pngs if format == "png" else session.export_openraster
    receipt = export(target)
    assert receipt.path == target and receipt.canonical_pixel_sha256 == final.pixel_sha256
    manifest = json.loads(receipt.manifest_path.read_text())
    native = receipt.manifest_path.parent / manifest["native_checkpoint"]["file"]
    assert sha256_file(native) == manifest["native_checkpoint"]["sha256"]
    assert manifest["native_checkpoint"]["drawing_state_hash"] == session.drawing_state_hash()
    assert session.checkpoint_path.read_bytes() == before
    # The exchange checkpoint must not depend on the old session's evidence tree.
    shutil.rmtree(session.output_dir)
    revived = DrawingSession.resume(native, subject=ref)
    assert revived.current_ir().to_dict() == session.current_ir().to_dict()
    assert revived.inspection_history == session.inspection_history
    assert revived.evidence_telemetry == session.evidence_telemetry
    assert revived.render_final(tmp_path / "revived.png").pixel_sha256 == final.pixel_sha256
    if format == "ora":
        with zipfile.ZipFile(target) as archive:
            assert archive.namelist()[0] == "mimetype"
            assert archive.read("mimetype") == b"image/openraster"
            assert archive.getinfo("mimetype").compress_type == zipfile.ZIP_STORED
            assert json.loads(archive.read("manifest.json"))["canonical"]["pixel_sha256"] == final.pixel_sha256
    preserved = receipt.manifest_path.read_bytes()
    with pytest.raises(FileExistsError):
        export(target)
    assert receipt.manifest_path.read_bytes() == preserved


@pytest.mark.parametrize("format", ["png", "ora"])
def test_native_checkpoint_failure_publishes_no_partial_exchange(tmp_path, monkeypatch, format):
    session, oid, _ = make(tmp_path)
    session.enable_layers()
    target = tmp_path / ("delivery" if format == "png" else "delivery.ora")
    before = session.checkpoint_path.read_bytes()
    def fail(*args):
        raise OSError("native checkpoint failure")
    monkeypatch.setattr(session, "_write_checkpoint", fail)
    export = session.export_layer_pngs if format == "png" else session.export_openraster
    with pytest.raises(OSError, match="native checkpoint"):
        export(target)
    assert not target.exists()
    assert not target.with_suffix(".layers.json").exists()
    assert not target.with_suffix(".checkpoint.json").exists()
    assert session.checkpoint_path.read_bytes() == before


def test_layered_discovery_is_explicit_and_source_opaque():
    ordinary = runtime_capabilities()
    assert "layer-create" not in ordinary.authoring_operations
    layered = runtime_capabilities(RenderProfile.mixed_media(64, 48), layered=True)
    assert {"ink-add", "layer-create", "element-transform"} <= set(layered.authoring_operations)
    assert "openraster-export" in layered.output_operations
    assert layered.supported_operations == layered.authoring_operations + layered.output_operations
    assert all("._" not in name for name in layered.authoring_entrypoints + layered.authoring_helpers)
    assert "DrawingSession.export_openraster" in layered.output_entrypoints


def test_public_undo_redo_retains_layers_and_checkpoint_on_write_failure(tmp_path, monkeypatch):
    session, oid, ref = make(tmp_path)
    original = session.current_ir().to_dict()
    session.enable_layers()
    session.create_layer("ink", "Ink")
    layered = session.current_ir().to_dict()
    session.undo(2)
    assert session.current_ir().to_dict() == original
    restored = DrawingSession.resume(session.checkpoint(), subject=ref)
    restored.redo(2)
    assert restored.current_ir().to_dict() == layered
    before = restored.checkpoint_path.read_bytes()
    def fail(*args):
        raise OSError("history checkpoint failure")
    monkeypatch.setattr(restored, "_write_checkpoint", fail)
    with pytest.raises(OSError, match="history checkpoint"):
        restored.undo()
    assert restored.current_ir().to_dict() == layered
    assert restored.checkpoint_path.read_bytes() == before


def test_branching_does_not_orphan_inspection_evidence(tmp_path):
    session, oid, ref = make(tmp_path)
    session.enable_layers()
    session.create_layer("ink", "Ink")
    session.inspect()
    session.undo()
    before = session.checkpoint_path.read_bytes()
    with pytest.raises(ValueError, match="retained audit evidence"):
        session.update_layer("drawing", name="Branch would discard inspected state")
    assert session.checkpoint_path.read_bytes() == before
    restored = DrawingSession.resume(session.checkpoint(), subject=ref)
    restored.redo()
    restored.update_layer("drawing", name="Safe correction after inspected state")
    DrawingSession.resume(restored.checkpoint(), subject=ref)


def test_mark_only_branch_keeps_action_identity_reservations(tmp_path):
    from img2drawing.authoring import StrokeEdit, apply_stroke_edits
    session, oid, ref = make(tmp_path)
    session.enable_layers()
    session.create_layer("discarded", "Discarded future")
    session.update_layer("drawing", opacity=.5)
    reserved = set(session._agent.executed_action_ids)
    session.undo(2)
    session.update_layer("drawing", name="A new branch")
    session.draw_many([
        {"points": [(2, 2), (20, 2)], "stroke_id": "new-a"},
        {"points": [(2, 4), (20, 4)], "stroke_id": "new-b"},
    ], observation_id=oid)
    apply_stroke_edits(session, [StrokeEdit("g", points=((6, 13), (56, 33)))],
                       observation_id=oid, reason="branch correction")
    ids = [(a.provenance or {})["action_id"] for a in session._agent.history.actions]
    assert len(ids) == len(set(ids))
    assert reserved <= session._agent.executed_action_ids
    assert "discarded" not in {n.layer_id for n in session.layer_document.layers}
    assert DrawingSession.resume(session.checkpoint(), subject=ref).current_ir().to_dict() == session.current_ir().to_dict()


def test_branching_preserves_observation_cursor_provenance(tmp_path):
    session, oid, ref = make(tmp_path)
    session.draw([(2, 2), (20, 2)], stroke_id="later", observation_id=oid)
    plan = record_semantic_groups(session, [SemanticGroup("later-shape", ("later",))],
                                  evidence="retain this observed group definition")
    session.undo()
    before = session.checkpoint_path.read_bytes()
    with pytest.raises(ValueError, match="retained audit evidence"):
        session.draw([(2, 4), (20, 4)], stroke_id="would-orphan", observation_id=oid)
    assert session.checkpoint_path.read_bytes() == before
    revived = DrawingSession.resume(session.checkpoint(), subject=ref)
    revived.redo()
    assert inspect_semantic_groups(revived, plan)["groups"]["later-shape"]["current_ids"] == ["later"]


def test_rewound_inspection_requires_current_intent_provenance(tmp_path):
    session, oid, ref = make(tmp_path)
    session.set_intent(DrawingIntent(drawing_mode="croquis"))
    session.draw([(2, 2), (20, 2)], stroke_id="later", observation_id=oid)
    intent = DrawingIntent(drawing_mode="line_study")
    session.set_intent(intent)
    session.undo()
    before = session.checkpoint_path.read_bytes()
    with pytest.raises(ValueError, match="intent was selected later"):
        session.inspect()
    assert session.checkpoint_path.read_bytes() == before
    session.set_intent(intent, reason="explicitly inspect this earlier state under the new intent")
    session.inspect()
    revived = DrawingSession.resume(session.checkpoint(), subject=ref)
    assert revived.intent == intent
