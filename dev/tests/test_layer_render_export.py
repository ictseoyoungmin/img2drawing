"""Pixel and interchange boundaries for opt-in document layers."""

from copy import deepcopy
from dataclasses import asdict, replace
import hashlib
from io import BytesIO
import json
import xml.etree.ElementTree as ET
import zipfile

import numpy as np
from PIL import Image
import pytest

from img2drawing.authoring import dot_screentone, fineliner
from img2drawing.core.history import CanvasHistory
from img2drawing.core.ir import Stroke, StrokeIR
from img2drawing.core.layers import LayerAction, LayerDocument, LayerNode
from img2drawing.core.material import InkArea, InkElement, MIXED_HISTORY_CONTRACT
from img2drawing.render import render_image
from img2drawing.render.document import (
    DOCUMENT_COMPOSITING_CONTRACT, _DocumentRenderer, document_render_mode, validate_document_work,
)
from img2drawing.render.hand import hand_seed, grain_seed
from img2drawing.render.layer_export import export_layer_pngs, export_openraster
from img2drawing.render.profile import RenderProfile
from img2drawing.timelapse.frames import (
    CanonicalFrameSource, inspect_fast_path_eligibility, open_frame_source,
)
from img2drawing.timelapse.replay import ForwardHistoryReplay


def rect(x0, y0, x1, y1):
    return ((x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0))


def _profiles():
    return [RenderProfile.canonical(48, 32),
            RenderProfile.opacity_normalized(48, 32),
            RenderProfile.opacity_normalized(48, 32, pressure_lift=True),
            RenderProfile.opacity_normalized(48, 32, contact_width=True),
            RenderProfile.mixed_media(48, 32, styled_paths=False),
            RenderProfile.mixed_media(48, 32, screentones=False),
            RenderProfile.mixed_media(48, 32)]


def _eraser(sid="erase", *, layer=3):
    return Stroke([(24, 2), (24, 30)], width=10, opacity=1, layer=layer,
                  pressure=[1, 1], stroke_id=sid, pressure_authored=True,
                  tool_state={"tool": "hard_eraser", "mode": "erase",
                              "erase_strength": 1, "hardness": 1, "grain": 0,
                              "path_lift_contract": "ordered-graphite-lift-v1"})


def _fixture_ir(profile):
    first = Stroke([(3, 12), (44, 18)], width=8, opacity=.5, layer=0, stroke_id="g1")
    second = Stroke([(3, 19), (44, 12)], width=6, opacity=.7, layer=2, stroke_id="g2")
    eraser = _eraser()
    if profile.renderer_version == "11":
        eraser.tool_state.pop("path_lift_contract")
    ir = StrokeIR(48, 32, [second, first, eraser])
    if profile.is_mixed_media:
        mark = InkArea(rect(29, 6, 37, 27))
        if profile.supports_styled_ink:
            mark = fineliner(((30, 6), (30, 25), (41, 25)), width=4,
                             cap="square", join="miter").resolve()
        if profile.supports_screentone:
            mark = dot_screentone(rect(28, 5, 43, 27), coverage=.45, pitch=4,
                                  phase_origin=(.3, .7))
        ir.media_contract = MIXED_HISTORY_CONTRACT
        ir.ink_elements = [InkElement("ink", mark, "value", "swatch", 1)]
        ir.element_order = ["g2", "ink", "g1", "erase"]
    return ir


def _ids(ir):
    return tuple(getattr(item, "element_id", getattr(item, "stroke_id", None))
                 for item in sorted(ir.ordered_elements(), key=lambda item: item.layer))


def _render(ir, profile):
    with render_image(profile.prepared_ir(ir), **profile.renderer_kwargs()) as image:
        return np.asarray(image).copy()


def test_layer_compositor_contract_is_pinned_without_changing_material_profiles():
    assert DOCUMENT_COMPOSITING_CONTRACT.digest() == "a380f54c2a086f59cd84470dc2773a3d8e0841041fac9b9e53d4a642e6939de9"
    assert "layer_document" not in RenderProfile.canonical(48, 32).to_dict()


def test_unlayered_graphite_only_mixed_ir_keeps_legacy_stroke_tie_order():
    strokes = [Stroke([(3, 8), (44, 24)], width=7, opacity=.7, stroke_id="g"), _eraser(layer=0)]
    mixed = StrokeIR(48, 32, strokes, media_contract=MIXED_HISTORY_CONTRACT,
                     element_order=["erase", "g"])
    graphite = StrokeIR(48, 32, strokes)
    profile = RenderProfile.mixed_media(48, 32, supersample=2)
    graphite_profile = replace(RenderProfile.opacity_normalized(48, 32, contact_width=True), supersample=2)
    assert np.array_equal(_render(mixed, profile), _render(graphite, graphite_profile))


@pytest.mark.parametrize("profile", _profiles(), ids=lambda p: p.renderer_version)
@pytest.mark.parametrize("background", [(237, 224, 205, 255), (49, 68, 83, 90)])
def test_neutral_conversion_is_exact_for_every_material_contract(profile, background):
    profile = replace(profile, supersample=2, background_rgba=background)
    ir = _fixture_ir(profile)
    before = _render(ir, profile)
    authored = deepcopy([asdict(stroke) for stroke in ir.strokes])
    seeds = [(hand_seed(stroke), grain_seed(stroke)) for stroke in ir.strokes]
    ir.layer_document = LayerDocument(
        (LayerNode("group", "Renamed group", kind="group", locked=True),
         LayerNode("main", "Existing drawing", parent_id="group"),
         LayerNode("empty", "Invisible empty layer", order=1, visible=False, opacity=.2)),
        {"main": _ids(ir), "empty": ()}, "main")
    assert document_render_mode(ir) == "identity_single_layer_legacy_v1"
    assert np.array_equal(_render(ir, profile), before)
    assert [asdict(stroke) for stroke in ir.strokes] == authored
    assert [(hand_seed(stroke), grain_seed(stroke)) for stroke in ir.strokes] == seeds
    assert profile.prepared_ir(ir).layer_document == ir.layer_document


def _ink_ir(nodes, members, *, paints=None, width=48, height=32):
    paints = paints or {"a": "black", "b": "black"}
    elements = [InkElement(sid, InkArea(rect(0, 0, width, height), paint=paint),
                           "value", "test", index)
                for index, (sid, paint) in enumerate(paints.items())]
    document = LayerDocument(tuple(nodes), members, next(iter(members)))
    return StrokeIR(width, height, media_contract=MIXED_HISTORY_CONTRACT,
                    ink_elements=elements, element_order=[e.element_id for e in elements],
                    layer_document=document)


def test_isolated_group_opacity_is_applied_once_after_children():
    nodes = [LayerNode("group", "Group", kind="group", opacity=.5),
             LayerNode("a", "A", parent_id="group"),
             LayerNode("b", "B", parent_id="group", order=1)]
    ir = _ink_ir(nodes, {"a": ("a",), "b": ("b",)})
    profile = RenderProfile.mixed_media(48, 32, supersample=2)
    together = _render(ir, profile)
    assert tuple(together[16, 24]) == (127, 127, 127, 255)
    separate_nodes = [replace(nodes[0], opacity=1), replace(nodes[1], opacity=.5),
                      replace(nodes[2], opacity=.5)]
    separate = replace(ir, layer_document=LayerDocument(tuple(separate_nodes),
                                                       ir.layer_document.members, "a"))
    assert tuple(_render(separate, profile)[16, 24]) == (63, 63, 63, 255)
    hidden = replace(ir, layer_document=LayerDocument(
        (replace(nodes[0], visible=False), *nodes[1:]), ir.layer_document.members, "a"))
    assert np.all(_render(hidden, profile) == 255)
    nested = replace(ir, layer_document=LayerDocument(
        (LayerNode("outer", "Outer", kind="group", opacity=.5),
         replace(nodes[0], parent_id="outer"), *nodes[1:]),
        ir.layer_document.members, "a"))
    assert tuple(_render(nested, profile)[16, 24]) == (191, 191, 191, 255)


def test_explicit_member_order_overrides_native_layers_without_mutation():
    black = InkElement("black", InkArea(rect(0, 0, 48, 32)), "value", "test", 9)
    white = InkElement("white", InkArea(rect(8, 8, 40, 24), paint="white"),
                       "value", "test", -5)
    document = LayerDocument((LayerNode("main", "Main"),),
                             {"main": ("black", "white")}, "main")
    ir = StrokeIR(48, 32, media_contract=MIXED_HISTORY_CONTRACT,
                  ink_elements=[black, white], element_order=["white", "black"],
                  layer_document=document)
    before = ir.to_dict()
    assert document_render_mode(ir) != "identity_single_layer_legacy_v1"
    profile = RenderProfile.mixed_media(48, 32, supersample=2)
    assert tuple(_render(ir, profile)[16, 24]) == (255, 255, 255, 255)
    assert ir.to_dict() == before and (black.layer, white.layer) == (9, -5)


def test_moving_graphite_layer_does_not_change_its_raw_pixels_or_seeds():
    profile = replace(RenderProfile.opacity_normalized(48, 32, contact_width=True), supersample=2)
    ir = _fixture_ir(profile)
    ir.layer_document = LayerDocument((LayerNode("first", "First"), LayerNode("other", "Other", order=1)),
                                      {"first": ("g1",), "other": ("g2", "erase")}, "first")
    before = ir.to_dict()
    prepared = profile.prepared_ir(ir)
    with _DocumentRenderer(prepared, **profile.renderer_kwargs()).raw_layer_image("first") as a:
        pixels = a.tobytes()
    nodes = tuple(replace(node, order=1 - node.order) for node in ir.layer_document.layers)
    moved = replace(ir, layer_document=LayerDocument(nodes, ir.layer_document.members, "first"))
    with _DocumentRenderer(profile.prepared_ir(moved), **profile.renderer_kwargs()).raw_layer_image("first") as b:
        assert b.tobytes() == pixels
    assert ir.to_dict() == before


def test_eraser_lifts_only_prior_graphite_in_its_own_layer_and_preserves_ink():
    first = Stroke([(4, 10), (44, 10)], width=8, opacity=.8, stroke_id="g1")
    second = Stroke([(4, 24), (44, 24)], width=8, opacity=.8, stroke_id="g2")
    ink = InkElement("ink", InkArea(rect(28, 19, 32, 29)), "value", "test", 0)
    nodes = (LayerNode("under", "Under"), LayerNode("over", "Over", order=1))
    document = LayerDocument(nodes, {"under": ("g1",), "over": ("g2", "ink")}, "over")
    before_ir = StrokeIR(48, 32, [first, second], media_contract=MIXED_HISTORY_CONTRACT,
                         ink_elements=[ink], element_order=["g1", "g2", "ink"], layer_document=document)
    after_ir = replace(before_ir, strokes=[first, second, _eraser()],
                       element_order=["g1", "g2", "ink", "erase"],
                       layer_document=LayerDocument(nodes, {"under": ("g1",),
                                                           "over": ("g2", "ink", "erase")}, "over"))
    profile = RenderProfile.mixed_media(48, 32, supersample=4)
    before, after = _render(before_ir, profile), _render(after_ir, profile)
    assert np.array_equal(before[8:12, 19:27], after[8:12, 19:27])
    assert after[24, 23, :3].mean() > before[24, 23, :3].mean() + 20
    assert tuple(after[24, 30]) == tuple(before[24, 30]) == (0, 0, 0, 255)
    early = replace(after_ir, layer_document=LayerDocument(
        nodes, {"under": ("g1",), "over": ("erase", "g2", "ink")}, "over"))
    assert np.array_equal(_render(early, profile), before)


@pytest.mark.parametrize("mixed", [False, True])
def test_document_history_uses_canonical_frames_and_forward_snapshots(mixed):
    history = CanvasHistory(48, 32, media_contract=MIXED_HISTORY_CONTRACT if mixed else None)
    history.add_stroke(Stroke([(3, 5), (40, 24)], width=5, stroke_id="g"))
    events = [("layer.enable", {"layer_id": "main", "name": "Main"}),
              ("layer.create", {"layer": LayerNode("second", "Second", order=1).to_dict()}),
              ("layer.assign", {"element_ids": ["g"], "layer_id": "second", "index": None}),
              ("layer.update", {"layer_id": "second", "changes": {"opacity": .4}})]
    for index, (kind, data) in enumerate(events):
        history.apply_layer_action(LayerAction(f"a{index}", kind, data, "o", "test observation", "test edit"))
    profile = (RenderProfile.mixed_media(48, 32, supersample=2) if mixed else
               replace(RenderProfile.canonical(48, 32), supersample=2))
    assert not inspect_fast_path_eligibility(history).eligible
    replay = ForwardHistoryReplay(history)
    source = open_frame_source(history, profile)
    assert isinstance(source, CanonicalFrameSource)
    try:
        for cursor in range(history.cursor + 1):
            snapshot = history.state_at(cursor)
            assert replay.state_at(cursor).to_dict() == snapshot.to_dict()
            source.advance_to(cursor)
            with source.image() as image:
                assert np.array_equal(np.asarray(image), _render(snapshot, profile))
    finally:
        source.close()


@pytest.mark.parametrize("mixed", [False, True])
def test_forward_replay_extended_limit_can_cross_layer_enable_in_redo_tail(mixed):
    history = CanvasHistory(48, 32, media_contract=MIXED_HISTORY_CONTRACT if mixed else None)
    history.add_stroke(Stroke([(3, 5), (40, 24)], width=5, stroke_id="g"))
    history.apply_layer_action(LayerAction("enable", "layer.enable",
        {"layer_id": "main", "name": "Main"}, "o", "test observation", "test redo"))
    history.apply_layer_action(LayerAction("fade", "layer.update",
        {"layer_id": "main", "changes": {"opacity": .4}}, "o", "test observation", "test redo"))
    history.undo(2)
    assert history.cursor == 1
    before = history.to_dict()
    replay = ForwardHistoryReplay(history)
    assert replay.state_at(1).to_dict() == history.state_at(1).to_dict()
    if not mixed:
        assert not replay._document_fallback and set(replay.state) == {"g"}
        assert inspect_fast_path_eligibility(history).eligible
    replay.limit = len(history.actions)
    for cursor in range(2, len(history.actions) + 1):
        assert replay.state_at(cursor).to_dict() == history.state_at(cursor).to_dict()
    assert history.to_dict() == before


def test_png_and_ora_preserve_structure_raw_hidden_layers_and_canonical_pixels(tmp_path):
    nodes = (LayerNode("group", "Ink & <tone>", kind="group", opacity=.5, locked=True),
             LayerNode("a", "검정", parent_id="group"),
             LayerNode("b", "Hidden white", parent_id="group", order=1, visible=False),
             LayerNode("empty", "../not-a-filename", order=1))
    ir = _ink_ir(nodes, {"a": ("a",), "b": ("b",), "empty": ()}, paints={"a": "black", "b": "white"})
    profile = RenderProfile.mixed_media(48, 32, supersample=2)
    before = ir.to_dict()
    png = export_layer_pngs(ir, profile, tmp_path / "layers")
    ora = export_openraster(ir, profile, tmp_path / "drawing.ora")
    assert png.layer_count == ora.layer_count == 3
    assert png.canonical_pixel_sha256 == ora.canonical_pixel_sha256
    assert json.loads(ora.manifest_path.read_text()) == ora.manifest
    with zipfile.ZipFile(ora.path) as archive:
        entries = archive.infolist()
        assert entries[0].filename == "mimetype" and entries[0].compress_type == zipfile.ZIP_STORED
        assert entries[0].extra == b"" and archive.read("mimetype") == b"image/openraster"
        assert {"stack.xml", "mergedimage.png", "Thumbnails/thumbnail.png", "manifest.json"} <= set(archive.namelist())
        tree = ET.fromstring(archive.read("stack.xml"))
        assert tree.attrib == {"version": "0.0.6", "w": "48", "h": "32"}
        root = tree.find("stack")
        assert root.attrib == {}
        assert [node.attrib["name"] for node in root] == ["../not-a-filename", "Ink & <tone>", "Paper"]
        group = root[1]
        assert group.attrib["isolation"] == "isolate" and group.attrib["opacity"] == "0.5"
        assert "x" not in group.attrib and "y" not in group.attrib
        assert [node.attrib["name"] for node in group] == ["Hidden white", "검정"]
        hidden = group[0]
        assert hidden.attrib["visibility"] == "hidden" and hidden.attrib["edit-locked"] == "true"
        with Image.open(BytesIO(archive.read(hidden.attrib["src"]))) as image:
            assert image.mode == "RGBA" and image.getpixel((24, 16)) == (255, 255, 255, 255)
        with Image.open(BytesIO(archive.read("mergedimage.png"))) as image:
            assert hashlib.sha256(image.tobytes()).hexdigest() == ora.canonical_pixel_sha256
            assert np.array_equal(np.asarray(image), _render(ir, profile))
        with Image.open(BytesIO(archive.read("Thumbnails/thumbnail.png"))) as image:
            assert image.size == (48, 32) and image.mode == "RGBA"
        assert json.loads(archive.read("manifest.json")) == ora.manifest
    assert ir.to_dict() == before
    original = ora.path.read_bytes()
    with pytest.raises(FileExistsError):
        export_openraster(ir, profile, ora.path)
    with pytest.raises(FileExistsError):
        export_layer_pngs(ir, profile, png.path)
    assert ora.path.read_bytes() == original


def test_reflatten_delta_exposes_noncommuting_downsampling(tmp_path):
    black = InkElement("left", InkArea(rect(0, 0, 3.25, 8)), "value", "test", 0)
    white = InkElement("right", InkArea(rect(3.25, 0, 8, 8), paint="white"), "value", "test", 1)
    document = LayerDocument((LayerNode("left", "Left"), LayerNode("right", "Right", order=1)),
                             {"left": ("left",), "right": ("right",)}, "left")
    ir = StrokeIR(8, 8, media_contract=MIXED_HISTORY_CONTRACT, ink_elements=[black, white],
                  element_order=["left", "right"], layer_document=document)
    profile = RenderProfile.mixed_media(8, 8, supersample=4)
    receipt = export_layer_pngs(ir, profile, tmp_path / "edges")
    assert not receipt.recomposition_exact and receipt.differing_pixels > 0
    assert receipt.max_channel_error > 10
    assert receipt.canonical_pixel_sha256 != receipt.recomposed_pixel_sha256
    assert "independently downsampled" in receipt.manifest["recomposition"]["fidelity_note"]


def test_document_budgets_preflight_without_allocating_and_accumulate_across_layers(monkeypatch):
    from img2drawing.render import document as compositor

    large = StrokeIR(4096, 4096, [Stroke([(0, 0), (10, 10)], stroke_id="g")],
                     layer_document=LayerDocument((LayerNode("main", "Main"),), {"main": ("g",)}, "main"))
    with pytest.raises(ValueError, match="working raster budget"):
        validate_document_work(large, RenderProfile.canonical(4096, 4096))
    nodes = (LayerNode("outer", "Outer", kind="group"),
             LayerNode("group", "Group", kind="group", parent_id="outer"),
             LayerNode("a", "A", parent_id="group"), LayerNode("b", "B", parent_id="group", order=1))
    deep = _ink_ir(nodes, {"a": ("a",), "b": ("b",)}, width=2048, height=2048)
    with pytest.raises(ValueError, match="simultaneous surface budget"):
        validate_document_work(deep, replace(RenderProfile.canonical(2048, 2048), supersample=2))
    parameters = dict(compositor.DOCUMENT_COMPOSITING_CONTRACT.parameters)
    parameters["max_composite_work"] = 4000
    monkeypatch.setattr(compositor, "DOCUMENT_COMPOSITING_CONTRACT", replace(
        compositor.DOCUMENT_COMPOSITING_CONTRACT, parameters=tuple(sorted(parameters.items()))))
    small = _ink_ir((LayerNode("a", "A"), LayerNode("b", "B", order=1)),
                    {"a": ("a",), "b": ("b",)}, width=16, height=16)
    profile = RenderProfile.mixed_media(16, 16, supersample=2)
    with pytest.raises(ValueError, match="layer document composite work"):
        _render(small, profile)


@pytest.mark.parametrize("empty_leaf", [False, True])
def test_empty_group_subtrees_need_no_working_surfaces(monkeypatch, empty_leaf):
    from img2drawing.render import document as compositor

    monkeypatch.setattr(compositor, "MAX_LIVE_SURFACE_PIXELS", 32 * 32 * 4 * 6)
    paint = LayerNode("main", "Drawing", opacity=.9)
    profile = replace(RenderProfile.canonical(32, 32), supersample=2)
    stroke = Stroke([(3, 5), (27, 24)], width=5, stroke_id="g")
    simple = StrokeIR(32, 32, [stroke], layer_document=LayerDocument(
        (paint,), {"main": ("g",)}, "main"))
    groups = tuple(LayerNode(f"group-{index}", f"Empty group {index}", kind="group",
                            parent_id=None if index == 0 else f"group-{index - 1}",
                            order=1 if index == 0 else 0)
                   for index in range(6))
    nodes, members = (paint, *groups), {"main": ("g",)}
    if empty_leaf:
        nodes = (*nodes, LayerNode("empty", "Empty paint layer", parent_id="group-5"))
        members["empty"] = ()
    deep = replace(simple, layer_document=LayerDocument(nodes, members, "main"))
    validate_document_work(deep, profile)
    assert np.array_equal(_render(deep, profile), _render(simple, profile))
