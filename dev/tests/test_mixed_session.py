from copy import deepcopy
from dataclasses import replace
import json

import numpy as np
import pytest
from PIL import Image

from img2drawing import DrawingSession, RenderProfile
from img2drawing.authoring import (InkAction, InkElement, InkPath, InkArea,
    apply_ink_actions, preview_ink_actions, SemanticGroup, record_semantic_groups,
    inspect_semantic_groups, prepare_group_transform)
from img2drawing.core.ir import StrokeIR
from img2drawing.render import render_image
from img2drawing.render.contract import MIXED_MEDIA_CONTRACT, CONTACT_WIDTH_CONTRACT, UnsupportedRendererError
from img2drawing.runtime import runtime_capabilities


def _rect(x0, y0, x1, y1):
    return ((x0,y0),(x1,y0),(x1,y1),(x0,y1),(x0,y0))


def _make(tmp, *, mixed=True, background=(255,255,255,255)):
    tmp.mkdir(parents=True, exist_ok=True)
    ref = tmp / "ref.png"
    Image.new("RGB",(96,72),"white").save(ref)
    profile = (RenderProfile.mixed_media(96,72,supersample=2,background_rgba=background)
               if mixed else replace(RenderProfile.canonical(96,72),supersample=2))
    s = DrawingSession.create(subject=ref,output_dir=tmp/"out",render_profile=profile)
    return s, s.observe({"fixture":"explicit authored test forms"}), ref


def _action(oid, aid, sid, mark=None, *, kind="ink.add", layer=0, role="contour"):
    return InkAction(aid,kind,sid,None if mark is None else InkElement(sid,mark,role,"test",layer),
                     oid,"explicit test observation","author or correct")


def _pixels(s, path):
    with Image.open(s.render_final(path).path) as image:
        return np.asarray(image.convert("RGBA")).copy()


def test_mixed_profile_distinct_pinned_and_scoped():
    profile = RenderProfile.mixed_media(96,72,supersample=2)
    assert profile.renderer_contract_digest == MIXED_MEDIA_CONTRACT.digest()
    assert MIXED_MEDIA_CONTRACT.value("graphite_contract_digest") == CONTACT_WIDTH_CONTRACT.digest()
    assert RenderProfile.from_dict(profile.to_dict()) == profile
    assert "ink-add" in runtime_capabilities(profile).authoring_operations
    assert "ink-add" not in runtime_capabilities().authoring_operations
    bad = profile.to_dict()
    bad["renderer_contract_digest"] = CONTACT_WIDTH_CONTRACT.digest()
    with pytest.raises(UnsupportedRendererError):
        RenderProfile.from_dict(bad)
    with pytest.raises(ValueError,match="budget"):
        RenderProfile.mixed_media(4096,4096,supersample=4)


def test_ink_preview_commit_resume_and_canonical_gif(tmp_path):
    s,oid,ref = _make(tmp_path)
    s.draw([(8,20),(85,20)],stroke_id="g",observation_id=oid)
    actions = (_action(oid,"ink-1","path",InkPath(((6,8),(85,55)),(0,1),.1,5)),
               _action(oid,"ink-2","area",InkArea(_rect(15,15,65,50),(_rect(28,25,42,38),))))
    before = s.checkpoint_path.read_bytes()
    pre = preview_ink_actions(s,actions,tmp_path/"preview.png")
    assert s.checkpoint_path.read_bytes() == before
    with pytest.raises(ValueError,match="differs"):
        apply_ink_actions(s,actions,expected_action_digest="0"*64)
    assert s.checkpoint_path.read_bytes() == before
    apply_ink_actions(s,actions,expected_cursor=pre["base_cursor"],
                      expected_state_hash=pre["base_state_hash"],
                      expected_action_digest=pre["action_digest"],
                      expected_profile_digest=pre["profile_digest"])
    final = s.render_final(tmp_path/"final.png")
    assert final.pixel_sha256 == pre["pixel_sha256"]
    assert final.drawing_state_hash == pre["prospective_state_hash"]
    revived = DrawingSession.resume(s.checkpoint(),subject=ref)
    assert revived.render_final(tmp_path/"resumed.png").pixel_sha256 == final.pixel_sha256
    assert revived.current_ir().to_dict() == s.current_ir().to_dict()
    with pytest.raises(ValueError,match="fast timelapse backend unavailable"):
        s.export_timelapse(tmp_path/"fast",backend="fast")
    tl = s.export_timelapse(tmp_path/"gif",every_n=1,backend="auto")
    assert [f["cursor"] for f in tl.manifest["frames"]] == [0,1,2,3]
    assert tl.manifest["final"]["last_frame_pixel_match"]
    assert tl.manifest["final"]["pixel_sha256"] == final.pixel_sha256
    assert tl.manifest["gif"]["within_tolerance"]


def test_selective_graphite_lift_does_not_erase_ink(tmp_path):
    s,oid,_ = _make(tmp_path)
    s.draw([(5,35),(90,35)],stroke_id="g1",role="form",tool="continuous_pencil",grade="4B",
           tool_overrides={"width":12,"opacity":.95,"jitter":0},pressure=[1,1],observation_id=oid)
    apply_ink_actions(s,[_action(oid,"i1","black",InkArea(_rect(40,10,56,60)))])
    s.draw([(5,35),(90,35)],stroke_id="g2",role="form",tool="continuous_pencil",grade="4B",
           tool_overrides={"width":12,"opacity":.95,"jitter":0},pressure=[1,1],observation_id=oid)
    before = _pixels(s,tmp_path/"before.png")
    s.erase_path([(8,35),(88,35)],stroke_id="lift",width=20,tool="hard_eraser",
                 pressure=[1,1],strength=1,reason="remove graphite guide",observation_id=oid)
    after = _pixels(s,tmp_path/"after.png")
    assert np.all(after[29:41,44:52,:3] == 0)
    assert after[32:38,15:35,:3].mean() > before[32:38,15:35,:3].mean() + 10


def test_white_paint_is_not_erase_and_layer_order(tmp_path):
    s,oid,_ = _make(tmp_path,background=(110,120,130,255))
    apply_ink_actions(s,[_action(oid,"i1","white",InkArea(_rect(12,12,70,60),paint="white"),layer=5),
                         _action(oid,"i2","black",InkArea(_rect(22,22,60,50)),layer=1)])
    img = _pixels(s,tmp_path/"white.png")
    assert tuple(img[30,35,:3]) == (255,255,255)
    assert tuple(img[5,5,:3]) == (110,120,130)
    apply_ink_actions(s,[_action(oid,"i3","white",kind="ink.delete")])
    img = _pixels(s,tmp_path/"retired.png")
    assert tuple(img[30,35,:3]) == (0,0,0)
    assert tuple(img[15,15,:3]) == (110,120,130)


def test_legacy_rejects_ink_and_malformed_batch_rolls_back(tmp_path):
    s,oid,_ = _make(tmp_path/"legacy",mixed=False)
    with pytest.raises(ValueError,match="mixed_media"):
        apply_ink_actions(s,[_action(oid,"a","i",InkArea(_rect(1,1,10,10)))])
    m,o,_ = _make(tmp_path/"mixed")
    before = m.checkpoint_path.read_bytes()
    with pytest.raises(ValueError,match="duplicate"):
        apply_ink_actions(m,[_action(o,"a","i",InkArea(_rect(1,1,10,10))),
                             _action(o,"b","i",InkArea(_rect(2,2,20,20)))])
    assert m.history_cursor == 0 and m.checkpoint_path.read_bytes() == before
    with pytest.raises(ValueError,match="observation_id"):
        apply_ink_actions(m,[_action("missing","a","i",InkArea(_rect(1,1,10,10)))])


def test_mixed_group_review_signature_changes_with_ink_geometry(tmp_path):
    s,oid,_ = _make(tmp_path)
    s.draw([(3,4),(40,30)],stroke_id="g",observation_id=oid)
    apply_ink_actions(s,[_action(oid,"a","i",InkArea(_rect(4,4,30,30)))])
    group = record_semantic_groups(s,[SemanticGroup("mixed",("g","i"))],evidence="explicit group")
    a = inspect_semantic_groups(s,group)["groups"]["mixed"]
    assert set(a["current_ids"]) == {"g","i"}
    apply_ink_actions(s,[_action(oid,"b","i",InkArea(_rect(4,4,35,35)),kind="ink.replace")])
    b = inspect_semantic_groups(s,group)["groups"]["mixed"]
    assert a["signature"] != b["signature"]
    with pytest.raises(ValueError,match="mixed group transforms"):
        prepare_group_transform(s,group,"mixed",(1,0,0,1,1,1))


def test_graphite_only_mixed_profile_retains_v3_pixels(tmp_path):
    s,oid,_ = _make(tmp_path)
    s.draw([(5,8),(84,62)],stroke_id="g",observation_id=oid)
    ir = s.render_profile.prepared_ir(s.current_ir())
    old = StrokeIR(ir.width,ir.height,ir.strokes,ir.metadata)
    with render_image(ir,**s.render_profile.renderer_kwargs()) as mixed:
        kw = s.render_profile.renderer_kwargs()
        kw["renderer_version"] = CONTACT_WIDTH_CONTRACT.renderer_version
        with render_image(old,**kw) as graphite:
            assert mixed.tobytes() == graphite.tobytes()
