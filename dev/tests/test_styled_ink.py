"""Native geometry probes and lifecycle for S02's explicit join/cap extension."""
from dataclasses import replace
import json

import numpy as np
import pytest
from PIL import Image

from img2drawing import DrawingSession, RenderProfile
from img2drawing.authoring import (g_pen, fineliner, StyledInkPath, InkPath,
    InkAction, PenDefinition, apply_ink_actions, preview_ink_actions, read_pen_definition)
from img2drawing.core.material import decode_ink_mark
from img2drawing.render.ink import build_ink_patch
from img2drawing.render.contract import MIXED_MEDIA_CONTRACT, STYLED_INK_CONTRACT
from img2drawing.runtime import runtime_capabilities


def raster(mark, size=(128,96), factor=4):
    box,patch=build_ink_patch(mark,factor=factor,hi_size=(size[0]*factor,size[1]*factor))
    a=np.zeros((size[1]*factor,size[0]*factor),dtype=np.uint8)
    with patch:
        if box[2]>box[0] and box[3]>box[1]:
            a[box[1]:box[3],box[0]:box[2]]=np.asarray(patch.getchannel("A"))
    return a


def sample(a,x,y,factor=4):
    return a[int(y*factor),int(x*factor)]


@pytest.mark.parametrize("cap",["butt","square","round"])
def test_cap_extent_and_exact_native_width(cap):
    # Explicit styled mode using a bevel join, also for a straight round-cap line.
    mark=fineliner(((20,40),(100,40)),width=12,cap=cap,join="bevel").resolve()
    a=raster(mark)
    y,x=np.where(a==255)
    extend=0 if cap=="butt" else 6
    assert (x.min(),x.max()+1)==((20-extend)*4,(100+extend)*4)
    assert (y.min(),y.max()+1)==(34*4,46*4)
    assert np.all(a[34*4:46*4,30*4:90*4]==255)
    assert set(np.unique(a))=={0,255}
    if cap=="round":
        assert sample(a,15,35)==0
    elif cap=="square":
        assert sample(a,15,35)==255


def test_round_bevel_miter_have_distinct_corner_shapes():
    pts=((20,60),(60,60),(60,20))
    a={join:raster(fineliner(pts,width=20,cap="butt",join=join).resolve())
       for join in ("round","bevel","miter")}
    assert sample(a["miter"],68,68)==255
    assert sample(a["round"],68,68)==0
    assert sample(a["round"],66,66)==255
    assert sample(a["bevel"],66,66)==0
    assert all(sample(v,59,59)==255 for v in a.values())
    assert np.count_nonzero(a["bevel"])<np.count_nonzero(a["round"])<np.count_nonzero(a["miter"])


def test_acute_miter_limit_falls_back_exactly_to_bevel():
    pts=((12,82),(60,12),(67,82))
    loose=fineliner(pts,width=10,cap="butt",join="miter",miter_limit=8)
    strict=replace(loose,miter_limit=1.2)
    bevel=replace(loose,join="bevel",miter_limit=4.)
    assert np.array_equal(raster(strict.resolve()),raster(bevel.resolve()))
    assert np.count_nonzero(raster(loose.resolve()))>np.count_nonzero(raster(bevel.resolve()))


@pytest.mark.parametrize("join",["round","bevel","miter"])
def test_reversal_and_self_overlap_are_unions(join):
    pts=((20,20),(100,70),(20,70),(100,20),(20,70))
    p=fineliner(pts,width=8,cap="square",join=join)
    a,b=raster(p.resolve()),raster(replace(p,controls=tuple(reversed(pts))).resolve())
    # Geometrically identical direction reversal; subpixel boundary tie
    # convention is fixed and no alpha stacking occurs.
    assert np.array_equal(a,b)
    assert set(np.unique(a))=={0,255}
    assert sample(a,60,45)==255


def test_variable_width_strips_preserve_cross_sections_and_linear_resampling():
    p=g_pen(((10,40),(110,40)),pressure_knots=((0,.2),(1,1)),
            max_width=12,min_width=2,gamma=1,join="miter",start_cap="butt",end_cap="square")
    a=raster(p.resolve(),factor=8)
    for x in (35,60,85):
        expected=2+10*(.2+.8*((x-10)/100))
        got=(a[:,x*8]==255).sum()/8
        assert abs(got-expected)<=.25
    q=replace(p,controls=((10,40),(35,40),(60,40),(85,40),(110,40)))
    assert np.array_equal(a,raster(q.resolve(),factor=8))


def test_closed_miter_seam_and_versioned_serialization():
    p=fineliner(((25,25),(85,25),(85,70),(25,70),(25,25)),width=10,join="miter")
    m=p.resolve()
    assert isinstance(m,StyledInkPath)
    assert sample(raster(m),21,21)==255
    assert decode_ink_mark(json.loads(json.dumps(m.to_dict())))==m
    assert PenDefinition.from_dict(p.to_dict())==p
    assert p.to_dict()["schema"].endswith(".v2")
    old=fineliner(((25,25),(85,25)),width=10)
    assert type(old.resolve()) is InkPath
    assert old.to_dict()["schema"].endswith(".v1")
    assert "miter_limit" not in old.to_dict()
    with pytest.raises(ValueError,match="closed styled"):
        replace(p,start_cap="butt").resolve()


def test_profile_boundary_resume_preview_and_legacy_pixel_parity(tmp_path):
    ref=tmp_path/"ref.png"
    Image.new("RGB",(128,96),"white").save(ref)
    a=RenderProfile.mixed_media(128,96,styled_paths=False)
    b=RenderProfile.mixed_media(128,96,screentones=False)
    assert a.renderer_contract_digest==MIXED_MEDIA_CONTRACT.digest()
    assert b.renderer_contract_digest==STYLED_INK_CONTRACT.digest()
    assert RenderProfile.from_dict(a.to_dict())==a
    assert RenderProfile.from_dict(b.to_dict())==b
    assert "img2drawing.authoring.StyledInkPath" not in runtime_capabilities(a).authoring_helpers
    assert "img2drawing.authoring.StyledInkPath" in runtime_capabilities(b).authoring_helpers
    def make(profile,name):
        s=DrawingSession.create(subject=ref,output_dir=tmp_path/name,render_profile=profile)
        oid=s.observe({"fixture":"authored line geometry"})
        return s,oid
    old,oi=make(a,"old")
    new,ni=make(b,"new")
    plain=fineliner(((12,20),(60,70),(110,20)),width=6)
    def act(p,oid,aid,kind="ink.add"):
        return p.action(action_id=aid,element_id="pen",observation_id=oid,
                        source_observation="explicit swatch",reason="author or correct",
                        role="contour",kind=kind)
    apply_ink_actions(old,[act(plain,oi,"a")])
    apply_ink_actions(new,[act(plain,ni,"a")])
    x=old.render_final(tmp_path/"v1.png")
    y=new.render_final(tmp_path/"v2.png")
    assert x.pixel_sha256==y.pixel_sha256
    styled=replace(plain,join="miter",start_cap="square",end_cap="butt")
    before=old.checkpoint_path.read_bytes()
    with pytest.raises(ValueError,match="styled ink requires"):
        apply_ink_actions(old,[act(styled,oi,"b","ink.replace")])
    assert old.checkpoint_path.read_bytes()==before
    edit=act(styled,ni,"b","ink.replace")
    preview=preview_ink_actions(new,[edit],tmp_path/"preview.png")
    apply_ink_actions(new,[edit],expected_cursor=preview["base_cursor"],
                      expected_state_hash=preview["base_state_hash"],
                      expected_profile_digest=preview["profile_digest"],
                      expected_action_digest=preview["action_digest"])
    final=new.render_final(tmp_path/"final.png")
    assert final.pixel_sha256==preview["pixel_sha256"]!=y.pixel_sha256
    revived=DrawingSession.resume(new.checkpoint(),subject=ref)
    assert read_pen_definition(revived,"pen")==styled
    assert revived.render_final(tmp_path/"resumed.png").pixel_sha256==final.pixel_sha256
    assert revived.render_at(1,tmp_path/"original.png").pixel_sha256==y.pixel_sha256


def test_styled_work_budget_preflight_and_clipped_geometry(monkeypatch):
    from img2drawing.render import ink
    p=fineliner(((-20,20),(80,20),(120,60)),width=8,join="miter",cap="square")
    a=raster(p.resolve())
    assert sample(a,0,20)==255
    monkeypatch.setattr(ink,"MAX_KERNEL_WORK",32)
    def forbidden(*args,**kw):
        pytest.fail("mask allocated before styled geometry work validation")
    monkeypatch.setattr(ink,"_styled_mask",forbidden)
    with pytest.raises(ValueError,match="budget"):
        build_ink_patch(p.resolve(),factor=4,hi_size=(512,384))
