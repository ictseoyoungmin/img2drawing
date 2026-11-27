"""S03 wet brush, explicit closed contours, editable solid/white ink."""
from dataclasses import replace
import json

import numpy as np
import pytest
from PIL import Image

from img2drawing import DrawingSession, RenderProfile
from img2drawing.authoring import (ink_brush, g_pen, solid_ink, sample_ink_contour,
    InkAction, InkElement, InkArea, InkPath, PenDefinition, apply_ink_actions,
    preview_ink_actions, read_pen_definition, current_ink_element,
    prepare_ink_transform, prepare_ink_group_transform, SemanticGroup,
    record_semantic_groups, inspect_semantic_groups, retire_group_guides)
from img2drawing.core.material import decode_ink_mark
from img2drawing.render.ink import build_ink_patch
from img2drawing.runtime import runtime_capabilities


def rect(x0,y0,x1,y1):
    return ((x0,y0),(x1,y0),(x1,y1),(x0,y1),(x0,y0))


def native(mark,size=(120,96),factor=4):
    bounds,patch=build_ink_patch(mark,factor=factor,hi_size=(size[0]*factor,size[1]*factor))
    out=np.zeros((size[1]*factor,size[0]*factor,4),dtype=np.uint8)
    with patch:
        x0,y0,x1,y1=bounds
        if x0<x1 and y0<y1:
            out[y0:y1,x0:x1]=np.asarray(patch)
    return out


def session(tmp,background=(255,255,255,255)):
    tmp.mkdir(parents=True,exist_ok=True)
    ref=tmp/"reference.png"
    Image.new("RGB",(120,96),"white").save(ref)
    profile=RenderProfile.mixed_media(120,96,supersample=4,background_rgba=background)
    s=DrawingSession.create(subject=ref,output_dir=tmp/"session",render_profile=profile)
    return s,s.observe({"fixture":"explicit synthetic ink swatch"}),ref


def action(oid,aid,sid,mark=None,*,kind="ink.add",layer=0,role="value"):
    element=None if mark is None else InkElement(sid,mark,role,"ink-swatch",layer)
    return InkAction(aid,kind,sid,element,oid,"explicit ink swatch","author or correct")


def pix(s,path):
    artifact=s.render_final(path)
    with Image.open(artifact.path) as im:
        return np.asarray(im.convert("RGBA")).copy()


def apply_preview(s,actions,path):
    before=s.checkpoint_path.read_bytes()
    pre=preview_ink_actions(s,actions,path)
    assert s.checkpoint_path.read_bytes()==before
    apply_ink_actions(s,actions,expected_cursor=pre["base_cursor"],
                      expected_state_hash=pre["base_state_hash"],
                      expected_profile_digest=pre["profile_digest"],
                      expected_action_digest=pre["action_digest"])
    return pre


def test_brush_wide_continuous_turn_and_overlap():
    p=ink_brush(((12,20),(90,65),(12,65),(90,20)),
                pressure_knots=((0,.65),(.5,1),(1,.65)),min_width=8,max_width=24)
    m=p.resolve()
    a=native(m)
    assert set(np.unique(a[:,:,3]))=={0,255}
    assert np.all(a[a[:,:,3]==255,:3]==0)
    assert a[42*4,51*4,3]==255
    assert a[65*4,12*4,3]==255
    assert a[3*4,3*4,3]==0
    assert PenDefinition.from_dict(p.to_dict())==p
    assert p.to_dict()["schema"]=="img2drawing.ink_brush_definition.v1"
    raw=p.to_dict()
    raw["schema"]="img2drawing.pen_definition.v1"
    with pytest.raises(ValueError,match="schema"):
        PenDefinition.from_dict(raw)


def test_brush_shaped_tip_and_geometry_not_density():
    p=ink_brush(((12,48),(108,48)),pressure_knots=((0,0),(.3,1),(.7,1),(1,0)),
                max_width=20,start_cap="point",end_cap="point")
    m=p.resolve()
    assert m.diameters()==(0.,20.,20.,0.)
    a=native(m)
    assert not a[:,0:12*4,3].any() and not a[:,108*4:,3].any()
    assert np.all(a[40*4:56*4,50*4:70*4,3]==255)
    assert np.all(a[a[:,:,3]==255,:3]==0)
    w=replace(p,paint="white").resolve()
    b=native(w)
    assert np.array_equal(a[:,:,3],b[:,:,3])
    assert np.all(b[b[:,:,3]==255,:3]==255)


def test_authored_cubic_contour_and_hole_clipping():
    # Four authored cubic segments, with repeated end vertex explicitly supplied.
    controls=((-8,48),(-8,22),(12,8),(48,8),(84,8),(106,22),(106,48),
              (106,74),(84,88),(48,88),(12,88),(-8,74),(-8,48))
    ring=sample_ink_contour(controls)
    assert ring[0]==ring[-1]==controls[0] and controls[3] in ring
    mark=solid_ink(ring,holes=(rect(28,28,62,68),))
    a=native(mark)
    assert a[48*4,0,3]==255
    assert a[48*4,45*4,3]==0
    assert a[2*4,45*4,3]==0
    assert np.all(a[a[:,:,3]==255,:3]==0)
    assert decode_ink_mark(json.loads(json.dumps(mark.to_dict())))==mark
    with pytest.raises(ValueError,match="explicitly closed"):
        sample_ink_contour(controls[:-1]+((0,48),))


@pytest.mark.parametrize("outer,holes",[
    (rect(4,4,100,80)[:-1],()),
    (((4,4),(100,80),(4,80),(100,4),(4,4)),()),
    (((4,4),(20,4),(100,4),(4,4)),()),
    (((4,4),(float("nan"),30),(20,50),(4,4)),()),
    (rect(4,4,100,80),(rect(4,12,30,40),)),
    (rect(4,4,100,80),(rect(20,20,60,60),rect(50,50,80,70))),
    (rect(4,4,100,80),(rect(20,20,60,60),rect(60,20,80,50))),
])
def test_invalid_solid_geometry_refused(outer,holes):
    with pytest.raises(ValueError):
        solid_ink(outer,holes=holes)


def test_concave_boundary_and_hole_native_coverage():
    outer=((8,8),(100,8),(100,80),(60,80),(60,35),(8,35),(8,8))
    a=native(solid_ink(outer,holes=(rect(20,15,40,28),)))
    assert a[20*4,25*4,3]==0
    assert a[55*4,30*4,3]==0
    assert a[55*4,80*4,3]==255
    assert a[20*4,55*4,3]==255


@pytest.mark.parametrize("background",[(112,139,161,255),(0,0,0,0)])
def test_white_path_and_area_are_paint_not_alpha_erase(tmp_path,background):
    s,oid,ref=session(tmp_path,background)
    # Ink area covers lower material. A white path and area sit ABOVE it.
    base=action(oid,"base","black",solid_ink(rect(12,12,102,84)),layer=0)
    white=ink_brush(((8,48),(112,48)),pressure_knots=((0,1),(1,1)),
                    min_width=12,max_width=12,paint="white").action(
                    action_id="white-path",element_id="wp",observation_id=oid,
                    source_observation="explicit white stroke",reason="paint highlight",
                    role="highlight",layer=2)
    area=action(oid,"white-area","wa",solid_ink(rect(35,23,85,72),
                holes=(rect(48,31,66,38),),paint="white"),layer=1)
    apply_ink_actions(s,[base,white,area])
    image=pix(s,tmp_path/"paint.png")
    assert tuple(image[48,8])==(255,255,255,255)  # white on bare background
    assert tuple(image[26,40])==(255,255,255,255)
    assert tuple(image[34,55])==(0,0,0,255)  # intentional hole
    assert tuple(image[18,22])==(0,0,0,255)
    assert tuple(image[4,4])==background
    revived=DrawingSession.resume(s.checkpoint(),subject=ref)
    assert np.array_equal(pix(revived,tmp_path/"revived.png"),image)
    assert read_pen_definition(revived,"wp").tool=="ink-brush"
    apply_ink_actions(revived,[action(oid,"drop-wp","wp",kind="ink.delete"),
                               action(oid,"drop-wa","wa",kind="ink.delete")])
    retired=pix(revived,tmp_path/"retired.png")
    assert tuple(retired[48,8])==background
    assert tuple(retired[26,40])==(0,0,0,255)


def test_ink_affine_group_transform_preview_resume_and_retire(tmp_path):
    s,oid,ref=session(tmp_path)
    black=solid_ink(rect(12,15,48,48),holes=(rect(20,22,28,33),))
    white=solid_ink(rect(34,20,42,35),paint="white")
    apply_ink_actions(s,[action(oid,"a","black",black),action(oid,"b","white",white,layer=1)])
    plan=record_semantic_groups(s,[SemanticGroup("ink-pair",("black","white"),guide_ids=("white",))],
                                evidence="explicit group membership")
    initial=s.render_final(tmp_path/"initial.png")
    before_group=inspect_semantic_groups(s,plan)["groups"]["ink-pair"]["signature"]
    proposal=prepare_ink_group_transform(s,plan,"ink-pair",(1,.2,0,1,12,5),
                        action_ids=("c","d"),observation_id=oid,reason="explicit shear of solid areas")
    assert s.history_cursor==2
    p=apply_preview(s,proposal["actions"],tmp_path/"preview.png")
    final=s.render_final(tmp_path/"final.png")
    assert p["pixel_sha256"]==final.pixel_sha256!=initial.pixel_sha256
    m=current_ink_element(s,"black").mark
    assert m.outer[0]==(27.,20.) and m.holes[0][0]==pytest.approx((36.4,27.))
    assert current_ink_element(s,"white").layer==1
    report=inspect_semantic_groups(s,plan)["groups"]["ink-pair"]
    assert report["signature"]!=before_group and report["review_required"]
    revived=DrawingSession.resume(s.checkpoint(),subject=ref)
    assert revived.render_final(tmp_path/"resume.png").pixel_sha256==final.pixel_sha256
    assert revived.render_at(2,tmp_path/"old.png").pixel_sha256==initial.pixel_sha256
    retire_group_guides(revived,plan,"ink-pair",["white"],reason="retire white overlay",observation_id=oid)
    with pytest.raises(ValueError,match="unknown current"):
        current_ink_element(revived,"white")
    assert current_ink_element(revived,"black").mark==m


def test_path_similarity_scales_contact_and_rejects_shear(tmp_path):
    s,oid,_=session(tmp_path)
    p=ink_brush(((10,12),(35,40)),pressure_knots=((0,.2),(1,.8)),min_width=2,max_width=12)
    a=p.action(action_id="a",element_id="brush",observation_id=oid,
               source_observation="explicit swatch",reason="author brush",role="value")
    apply_ink_actions(s,[a])
    before=s.checkpoint_path.read_bytes()
    with pytest.raises(ValueError,match="similarity"):
        prepare_ink_transform(s,["brush"],(2,0,0,1,0,0),action_ids=["b"],observation_id=oid,reason="invalid")
    assert s.checkpoint_path.read_bytes()==before
    q=prepare_ink_transform(s,["brush"],(0,-2,2,0,100,0),
                           action_ids=["b"],observation_id=oid,reason="rotate and scale")
    mark=q["actions"][0].element.mark
    old=p.resolve()
    assert mark.points[0]==(76.,20.)
    assert mark.pressure==old.pressure
    assert mark.min_width==2*old.min_width and mark.max_width==2*old.max_width
    apply_preview(s,q["actions"],tmp_path/"transform.png")
    with pytest.raises(ValueError,match="no current pen definition"):
        read_pen_definition(s,"brush")
    assert s._agent.history.actions[0].provenance["pen_definition"]==p.to_dict()


def test_atomic_invalid_batch_and_stale_transform(tmp_path,monkeypatch):
    from img2drawing.render import ink
    s,oid,_=session(tmp_path)
    a=action(oid,"a","area",solid_ink(rect(10,10,40,40)))
    apply_ink_actions(s,[a])
    q=prepare_ink_transform(s,["area"],(1,0,0,1,10,0),
                           action_ids=["b"],observation_id=oid,reason="move")
    before=s.checkpoint_path.read_bytes()
    invalid=action(oid,"c","unknown",kind="ink.delete")
    with pytest.raises(ValueError):
        apply_ink_actions(s,[q["actions"][0],invalid])
    assert s.checkpoint_path.read_bytes()==before and s.history_cursor==1
    apply_ink_actions(s,[action(oid,"d","new",solid_ink(rect(45,45,60,60)))])
    with pytest.raises(ValueError,match="stale"):
        apply_ink_actions(s,q["actions"],expected_cursor=q["base_cursor"],expected_state_hash=q["base_state_hash"])
    before=s.checkpoint_path.read_bytes()
    monkeypatch.setattr(ink,"MAX_PATCH_PIXELS",64)
    with pytest.raises(ValueError,match="budget"):
        prepare_ink_transform(s,["area"],(2,0,0,2,0,0),
                              action_ids=["e"],observation_id=oid,reason="too large")
    assert s.checkpoint_path.read_bytes()==before


def test_brush_area_white_and_interleaved_graphite_replay(tmp_path):
    s,oid,ref=session(tmp_path)
    s.draw([(5,50),(115,50)],stroke_id="under",role="form",tool="continuous_pencil",grade="4B",
           tool_overrides={"width":8,"opacity":.9,"jitter":0},pressure=[1,1],observation_id=oid)
    brush=ink_brush(((20,20),(100,20)),pressure_knots=((0,1),(1,1)),max_width=16)
    apply_ink_actions(s,[brush.action(action_id="b",element_id="brush",observation_id=oid,
                source_observation="explicit brush",reason="black stroke",role="value"),
                action(oid,"a","area",solid_ink(rect(38,30,80,72),holes=(rect(51,38,65,48),)))])
    s.draw([(5,50),(115,50)],stroke_id="over",role="form",tool="continuous_pencil",grade="4B",
           tool_overrides={"width":8,"opacity":.9,"jitter":0},pressure=[1,1],observation_id=oid)
    apply_ink_actions(s,[action(oid,"w","white",solid_ink(rect(56,43,70,58),paint="white"),layer=2)])
    before=pix(s,tmp_path/"before-lift.png")
    s.erase_path([(5,50),(115,50)],stroke_id="lift",width=18,tool="hard_eraser",strength=1,
                 pressure=[1,1],observation_id=oid,reason="lift graphite only")
    after=pix(s,tmp_path/"after-lift.png")
    assert np.array_equal(before[47:54,60:66],after[47:54,60:66])
    assert after[47:54,15:32,:3].mean()>before[47:54,15:32,:3].mean()
    assert np.all(after[18:22,30:90,:3]==0)
    final=s.render_final(tmp_path/"final.png")
    replay=s.export_timelapse(tmp_path/"replay",every_n=2,backend="canonical")
    assert [frame["cursor"] for frame in replay.manifest["frames"]]==[0,2,4,6]
    assert replay.manifest["final"]["pixel_sha256"]==final.pixel_sha256
    assert replay.manifest["final"]["last_frame_pixel_match"] and replay.manifest["gif"]["within_tolerance"]
    revived=DrawingSession.resume(s.checkpoint(),subject=ref)
    assert revived.render_final(tmp_path/"resume.png").pixel_sha256==final.pixel_sha256


def test_s03_capability_discovery():
    names=("ink_brush","solid_ink","sample_ink_contour","prepare_ink_transform",
           "prepare_ink_group_transform","current_ink_element")
    base=runtime_capabilities()
    mixed=runtime_capabilities(RenderProfile.mixed_media(120,96))
    for name in names:
        full="img2drawing.authoring."+name
        assert full not in base.authoring_helpers and full in mixed.authoring_helpers
