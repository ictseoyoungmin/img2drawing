"""S04 calibrated authored dot screens and page-space replay contract."""
from dataclasses import replace
import json
import math

import numpy as np
import pytest
from PIL import Image

from img2drawing import DrawingSession, RenderProfile
from img2drawing.authoring import (dot_screentone, Screentone, ToneGradient, solid_ink,
    fineliner, InkAction, InkElement, apply_ink_actions, preview_ink_actions,
    current_ink_element, prepare_ink_transform, SemanticGroup,
    record_semantic_groups, prepare_ink_group_transform)
from img2drawing.core.material import decode_ink_mark
from img2drawing.render.ink import build_ink_patch, validate_ink_work
from img2drawing.render.screentone import (disk_cell_coverage, radius_squared_for_coverage,
    intersect_dot_pattern)
from img2drawing.render.contract import MIXED_MEDIA_CONTRACT, STYLED_INK_CONTRACT, SCREENTONE_CONTRACT
from img2drawing.render import render_image
from img2drawing.timelapse.replay import ForwardHistoryReplay
from img2drawing.runtime import runtime_capabilities


def rect(x0,y0,x1,y1):
    return ((x0,y0),(x1,y0),(x1,y1),(x0,y1),(x0,y0))


def native(mark,size=(128,96),factor=4):
    box,patch=build_ink_patch(mark,factor=factor,hi_size=(size[0]*factor,size[1]*factor))
    out=np.zeros((size[1]*factor,size[0]*factor),dtype=np.uint8)
    with patch:
        if box[2]>box[0] and box[3]>box[1]:
            out[box[1]:box[3],box[0]:box[2]]=np.asarray(patch.getchannel("A"))
            assert np.all(np.asarray(patch)[...,0:3][np.asarray(patch)[...,3]==255]==0) or mark.paint=="white"
    return box,out


def action(oid,aid,sid,mark=None,*,kind="ink.add",layer=0):
    return InkAction(aid,kind,sid,None if mark is None else InkElement(sid,mark,"value","swatch",layer),
                     oid,"explicit synthetic tone study","author or correct")


def make(tmp,profile=None):
    tmp.mkdir(parents=True,exist_ok=True)
    ref=tmp/"reference.png"
    Image.new("RGB",(128,96),"white").save(ref)
    s=DrawingSession.create(subject=ref,output_dir=tmp/"session",
        render_profile=profile or RenderProfile.mixed_media(128,96,supersample=4))
    return s,s.observe({"fixture":"explicit dot screentone"}),ref


def preview_apply(s,actions,path):
    before=s.checkpoint_path.read_bytes()
    p=preview_ink_actions(s,actions,path)
    assert s.checkpoint_path.read_bytes()==before
    apply_ink_actions(s,actions,expected_cursor=p["base_cursor"],
                      expected_state_hash=p["base_state_hash"],
                      expected_profile_digest=p["profile_digest"],
                      expected_action_digest=p["action_digest"])
    return p


@pytest.mark.parametrize("c",[0.,.01,.2,.5,math.pi/4,.8,.9,.98,1.])
def test_analytic_inverse_is_area_calibrated(c):
    q=radius_squared_for_coverage(c)
    assert 0<=q<=.5
    assert disk_cell_coverage(q)==pytest.approx(c,abs=1e-12)
    if c>math.pi/4 and c<1:
        assert q>.25 and q<c  # beyond circle touching, no radius saturation


@pytest.mark.parametrize("pitch,factor,angle",[(4,2,0),(4,4,45),(6,4,23),(6,8,0),
                                             (8,2,45),(8,4,0),(10,4,23)])
def test_measured_coverage_nested_at_multiple_scales(pitch,factor,angle):
    # 48x48 logical window, fixed noninteger phase. Finite-grid calibration
    # tolerance is 4 percentage points for these specified fixtures only.
    prev=np.zeros((48*factor,48*factor),dtype=bool)
    for c in (.05,.2,.5,.78,.9,.98):
        m=dot_screentone(rect(0,0,48,48),pitch=pitch,coverage=c,
                         angle_degrees=angle,phase_origin=(.37,.61))
        _,a=native(m,(48,48),factor)
        assert set(np.unique(a))<={0,255}
        now=a==255
        assert abs(now.mean()-c)<=.04,(pitch,factor,angle,c,now.mean())
        assert np.all(~prev|now)
        prev=now


def test_zero_one_endpoints_and_concavity_holes():
    outer=((0,4),(110,4),(110,80),(72,80),(72,38),(0,38),(0,4))
    holes=(rect(18,14,38,29),)
    k=dict(holes=holes,pitch=6,angle_degrees=23,phase_origin=(.5,.5))
    b,zero=native(dot_screentone(outer,coverage=0.,**k))
    assert b==(0,0,0,0) and not zero.any()
    bounds,full=native(dot_screentone(outer,coverage=1.,**k))
    assert np.array_equal(full,native(solid_ink(outer,holes=holes))[1])
    assert bounds==(0,16,440,320)
    _,tone=native(dot_screentone(outer,coverage=.72,**k))
    assert not tone[14*4:29*4,18*4:38*4].any()
    assert not tone[40*4:78*4,8*4:68*4].any()
    assert not tone[:4*4].any()
    assert not (tone[full==0]).any()
    # Exact transparent/solid endpoints even when the dot centre equals a sample.
    _,zero=native(dot_screentone(rect(0,0,20,20),pitch=4,coverage=0,
                                 phase_origin=(.125,.125)))
    assert not zero.any()


def test_clipped_negative_bounds_and_neighbouring_regions_same_phase():
    kw=dict(pitch=7,coverage=.63,angle_degrees=37,phase_origin=(-1.2,3.4))
    whole=dot_screentone(rect(-12,-8,116,80),**kw)
    bounds,a=native(whole)
    assert bounds==(0,0,464,320)
    left=native(dot_screentone(rect(-12,-8,51,80),**kw))[1]
    right=native(dot_screentone(rect(51,-8,116,80),**kw))[1]
    assert np.array_equal(a,np.maximum(left,right))
    assert np.array_equal(a[:,20*4:42*4],
        native(dot_screentone(rect(20,-8,42,80),**kw))[1][:,20*4:42*4])


def test_tile_shapes_exact_and_gradient_monotone():
    grad=ToneGradient((24,0),(104,0),0.,1.)
    mark=dot_screentone(rect(0,0,128,96),pitch=8,angle_degrees=19,
                        phase_origin=(.37,.61),gradient=grad)
    box=(0,0,512,384)
    a=np.full((384,512),255,dtype=np.uint8)
    b=a.copy()
    intersect_dot_pattern(a,box,mark,4,tile_pixels=4096)
    intersect_dot_pattern(b,box,mark,4,tile_pixels=16384)
    assert np.array_equal(a,b)
    assert np.array_equal(a,native(mark)[1])
    assert not a[:,:24*4].any() and np.all(a[:,104*4:]==255)
    bands=[(a[:,x*4:(x+16)*4]==255).mean() for x in (24,40,56,72,88)]
    assert bands==sorted(bands)
    assert np.allclose(bands,(.1,.3,.5,.7,.9),atol=.04)
    # A constant gradient is identical to the corresponding constant screen.
    same=replace(mark,gradient=ToneGradient((0,0),(128,96),.87,.87))
    fixed=replace(mark,gradient=None,coverage=.87)
    assert np.array_equal(native(same)[1],native(fixed)[1])


@pytest.mark.parametrize("kwargs",[
    {"pitch":3.99},{"pitch":513},{"pitch":float("nan")},
    {"coverage":-1},{"coverage":1.01},{"coverage":True},{"coverage":None},
    {"angle_degrees":float("inf")},{"phase_origin":(0,float("nan"))},
    {"gradient":ToneGradient((0,0),(20,0),.1,.9)},
])
def test_invalid_tone_parameters(kwargs):
    values=dict(coverage=.3)
    values.update(kwargs)
    with pytest.raises(ValueError):
        dot_screentone(rect(0,0,40,40),**values)


def test_strict_serialization_and_geometry_rejection():
    g=ToneGradient((10,10),(80,40),.2,.95)
    m=dot_screentone(rect(2,2,100,80),holes=(rect(10,15,20,25),),
                     pitch=7.5,gradient=g,angle_degrees=-45,phase_origin=(2.5,-1.5))
    assert m.angle_degrees==315.
    raw=json.loads(json.dumps(m.to_dict()))
    assert decode_ink_mark(raw)==m
    assert decode_ink_mark(raw).digest()==m.digest()
    assert raw["pattern"]=="dot" and raw["anchor"]=="page"
    for key,val in (("raster_mask",[[1]]),("pattern","line"),("anchor","object"),("paint","white")):
        with pytest.raises(ValueError):
            decode_ink_mark({**raw,key:val})
    with pytest.raises(ValueError):
        ToneGradient((0,0),(0,0),.2,.5)
    with pytest.raises(ValueError):
        ToneGradient((0,0),(20,0),.2,1.1)
    with pytest.raises(ValueError):
        dot_screentone(rect(0,0,40,40)[:-1],coverage=.3)
    with pytest.raises(ValueError):
        dot_screentone(rect(0,0,40,40),holes=(rect(0,2,10,10),),coverage=.3)
    # Payload complexity is independent of dot count/pitch: no expanded points.
    big=dot_screentone(rect(0,0,1000,1000),pitch=4,coverage=.4)
    small=replace(big,pitch=100)
    assert len(json.dumps(big.to_dict()))-len(json.dumps(small.to_dict())) in (-2,0,2)
    assert len(big.to_dict()["outer"])==5


def test_preflight_limits_before_mask_allocation(monkeypatch):
    from img2drawing.render import ink
    m=dot_screentone(rect(0,0,80,80),pitch=4,gradient=ToneGradient((0,0),(80,0),0,1))
    def forbidden(*args,**kwargs):
        pytest.fail("mask allocated before validation")
    monkeypatch.setattr(ink,"_area_mask",forbidden)
    with pytest.raises(ValueError,match="working sample limit"):
        build_ink_patch(m,factor=1,hi_size=(128,96))
    monkeypatch.setattr(ink,"MAX_KERNEL_WORK",1000)
    with pytest.raises(ValueError,match="work budget"):
        build_ink_patch(m,factor=4,hi_size=(512,384))
    with pytest.raises(ValueError,match="work budget"):
        validate_ink_work(m,factor=4,hi_size=(512,384))


def test_profile_scope_preserves_old_contract_and_pixels(tmp_path):
    profiles=(RenderProfile.mixed_media(128,96,styled_paths=False),
              RenderProfile.mixed_media(128,96,screentones=False),
              RenderProfile.mixed_media(128,96))
    assert [p.renderer_contract_digest for p in profiles]==[
        MIXED_MEDIA_CONTRACT.digest(),STYLED_INK_CONTRACT.digest(),SCREENTONE_CONTRACT.digest()]
    assert [p.supports_styled_ink for p in profiles]==[False,True,True]
    name="img2drawing.authoring.dot_screentone"
    assert name not in runtime_capabilities().authoring_helpers
    for i,p in enumerate(profiles):
        assert RenderProfile.from_dict(p.to_dict())==p
        assert (name in runtime_capabilities(p).authoring_helpers)==(i==2)
    with pytest.raises(ValueError,match="require styled_paths"):
        RenderProfile.mixed_media(128,96,styled_paths=False,screentones=True)
    hashes=[]
    for i,p in enumerate(profiles):
        s,oid,_=make(tmp_path/str(i),p)
        apply_ink_actions(s,[action(oid,"a","solid",solid_ink(rect(10,10,80,80)))])
        hashes.append(s.render_final(tmp_path/f"old-{i}.png").pixel_sha256)
        tone=action(oid,"b","tone",dot_screentone(rect(4,4,120,90),coverage=.55))
        if i<2:
            before=s.checkpoint_path.read_bytes()
            with pytest.raises(ValueError,match="screentone requires"):
                apply_ink_actions(s,[tone])
            assert s.checkpoint_path.read_bytes()==before
        else:
            apply_ink_actions(s,[tone])
            ir=p.prepared_ir(s.current_ir())
            kw=profiles[1].renderer_kwargs()
            with pytest.raises(ValueError,match="screentone requires"):
                render_image(ir,**kw)
    assert len(set(hashes))==1


def test_pattern_edits_white_over_tone_transforms_and_replay(tmp_path):
    s,oid,ref=make(tmp_path)
    g=ToneGradient((16,0),(100,0),.2,.95)
    tone=dot_screentone(rect(8,8,88,78),holes=(rect(22,24,36,40),),
                         pitch=6,angle_degrees=23,phase_origin=(.5,1.5),gradient=g)
    apply_ink_actions(s,[action(oid,"a","tone",tone)])
    initial=s.render_final(tmp_path/"initial.png")
    original_state=s.drawing_state_hash()
    new=replace(tone,pitch=8,angle_degrees=45,phase_origin=(1.5,2.5),
                gradient=None,coverage=.85)
    edit=action(oid,"b","tone",new,kind="ink.replace")
    pre=preview_apply(s,[edit],tmp_path/"tone-edit.png")
    changed=s.render_final(tmp_path/"changed.png")
    assert changed.pixel_sha256==pre["pixel_sha256"]!=initial.pixel_sha256
    assert s.drawing_state_hash()!=original_state
    white=solid_ink(rect(42,28,62,48),paint="white")
    apply_ink_actions(s,[action(oid,"c","white",white,layer=1)])
    cover=s.render_final(tmp_path/"covered.png")
    with Image.open(cover.path) as im:
        assert im.getpixel((52,38))==(255,255,255,255)
    group=record_semantic_groups(s,[SemanticGroup("tones",("tone",))],evidence="explicit tone group")
    before=s.checkpoint_path.read_bytes()
    with pytest.raises(ValueError,match="similarity"):
        prepare_ink_group_transform(s,group,"tones",(2,0,0,1,0,0),action_ids=["d"],
                                    observation_id=oid,reason="unsupported nonuniform")
    assert s.checkpoint_path.read_bytes()==before
    q=prepare_ink_transform(s,["tone"],(1,0,0,1,24,0),action_ids=["d"],
                            observation_id=oid,reason="move contour only")
    moved=q["actions"][0].element.mark
    assert moved.phase_origin==new.phase_origin and moved.pitch==new.pitch
    assert moved.angle_degrees==new.angle_degrees and moved.coverage==new.coverage
    old_box,old_mask=native(new)
    new_box,new_mask=native(moved)
    # Compare the common interior away from holes, in global page coordinates.
    assert np.array_equal(old_mask[45*4:65*4,40*4:80*4],new_mask[45*4:65*4,40*4:80*4])
    y,x=np.where(old_mask!=new_mask)
    assert x.min()>=min(old_box[0],new_box[0]) and x.max()<max(old_box[2],new_box[2])
    assert y.min()>=min(old_box[1],new_box[1]) and y.max()<max(old_box[3],new_box[3])
    pre=preview_apply(s,q["actions"],tmp_path/"move.png")
    assert s.render_final(tmp_path/"moved.png").pixel_sha256==pre["pixel_sha256"]
    assert current_ink_element(s,"tone").mark==moved
    apply_ink_actions(s,[action(oid,"e","white",kind="ink.delete")])
    final=s.render_final(tmp_path/"revealed.png")
    assert final.pixel_sha256!=pre["pixel_sha256"]
    revived=DrawingSession.resume(s.checkpoint(),subject=ref)
    assert current_ink_element(revived,"tone").mark==moved
    assert revived.render_final(tmp_path/"resumed.png").pixel_sha256==final.pixel_sha256
    assert revived.render_at(1,tmp_path/"original.png").pixel_sha256==initial.pixel_sha256
    # Random vs forward mixed reducer and sampled canonical frame hashes.
    forward=ForwardHistoryReplay(revived._agent.history)
    for cursor in range(6):
        assert forward.state_at(cursor).to_dict()==revived._agent.history.state_at(cursor).to_dict()
    tl=revived.export_timelapse(tmp_path/"gif",every_n=2,backend="auto")
    assert [f["cursor"] for f in tl.manifest["frames"]]==[0,2,4,5]
    assert tl.manifest["final"]["pixel_sha256"]==final.pixel_sha256
    assert tl.manifest["gif"]["within_tolerance"]
    for frame in tl.manifest["frames"]:
        assert revived.render_at(frame["cursor"],tmp_path/f"check-{frame['cursor']}.png").pixel_sha256==frame["pixel_sha256"]
    with pytest.raises(ValueError,match="fast timelapse backend unavailable"):
        revived.export_timelapse(tmp_path/"fast",backend="fast")
    apply_ink_actions(revived,[action(oid,"f","tone",kind="ink.delete")])
    with Image.open(revived.render_final(tmp_path/"empty.png").path) as im:
        assert np.all(np.asarray(im)==255)


def test_gradient_transform_keeps_page_axis_and_atomic_budget_refusal(tmp_path,monkeypatch):
    from img2drawing.render import ink
    s,oid,_=make(tmp_path)
    g=ToneGradient((10,10),(90,10),.2,.8)
    m=dot_screentone(rect(8,8,65,65),gradient=g,pitch=6)
    apply_ink_actions(s,[action(oid,"a","tone",m)])
    q=prepare_ink_transform(s,["tone"],(0,-1,1,0,100,0),action_ids=["b"],
                            observation_id=oid,reason="rotate boundary")
    assert q["actions"][0].element.mark.gradient==g
    before=s.checkpoint_path.read_bytes()
    monkeypatch.setattr(ink,"MAX_KERNEL_WORK",50)
    with pytest.raises(ValueError,match="budget"):
        apply_ink_actions(s,q["actions"])
    assert s.checkpoint_path.read_bytes()==before and s.history_cursor==1
