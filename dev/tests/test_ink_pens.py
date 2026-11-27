"""S02 bounded authoring, exact path authority and real rendered pen swatches."""
from dataclasses import replace
import json
import math

import numpy as np
import pytest
from PIL import Image

from img2drawing import DrawingSession, RenderProfile
from img2drawing.authoring import (PenDefinition, g_pen, fineliner, read_pen_definition,
    apply_ink_actions, preview_ink_actions, InkAction, InkElement, InkPath)
from img2drawing.core.action import AgentDrawingSession
from img2drawing.core.material import MIXED_HISTORY_CONTRACT
from img2drawing.core.ir import Stroke, StrokeIR
from img2drawing.render.ink import build_ink_patch
from img2drawing.render import render_image
from img2drawing.runtime import runtime_capabilities


def _raster(mark, factor=4, size=(120,80)):
    hi=(size[0]*factor,size[1]*factor)
    bounds,patch=build_ink_patch(mark,factor=factor,hi_size=hi)
    with patch, Image.new("RGBA",hi,(255,255,255,255)) as im:
        if bounds[2]>bounds[0] and bounds[3]>bounds[1]:
            im.alpha_composite(patch,dest=bounds[:2])
        with im.resize(size,Image.Resampling.LANCZOS) as small:
            return np.array(small.convert("RGB"))


def _action(pen,oid,aid,sid,kind="ink.add"):
    return pen.action(action_id=aid,element_id=sid,observation_id=oid,
                      source_observation="explicit synthetic pen swatch",
                      reason="author or refine",role="contour",part="swatch",kind=kind)


def test_straight_constant_pen_is_two_samples_and_corner_is_preserved():
    line=fineliner(((10,20),(30000,20)),width=2)
    assert line.resolve().points==line.controls
    assert len(line.resolve().points)==2
    corner=fineliner(((10,20),(55,20),(55,65)),width=2)
    assert corner.resolve().points==corner.controls
    assert corner.resolve().diameters()==(2.,2.,2.)
    # Round corner union, no gap or double-alpha.
    im=_raster(corner.resolve())
    assert im[20,54,0]<10 and im[21,54,0]<30


def test_pressure_knots_are_inserted_at_arc_length_not_vertex_index():
    p=g_pen(((10,20),(30,20),(30,80)),pressure_knots=((0,.2),(.5,.9),(1,.3)),
            max_width=8,min_width=1,gamma=1)
    mark=p.resolve()
    assert mark.points==((10.,20.),(30.,20.),(30.,40.),(30.,80.))
    assert mark.pressure==pytest.approx((.2,.55,.9,.3))
    assert mark.diameters()==pytest.approx((2.4,4.85,7.3,3.1))


@pytest.mark.parametrize("gamma",[.25,.7,1.,1.3,2.,4.])
def test_adaptive_width_interpolation_matches_analytic_response(gamma):
    pen=g_pen(((5,30),(105,30)),pressure_knots=((0,0),(1,1)),
              max_width=16,min_width=.5,gamma=gamma,width_tolerance=.025)
    mark=pen.resolve()
    assert 2<=len(mark.points)<128
    for (a,b),(wa,wb) in zip(zip(mark.points,mark.points[1:]),zip(mark.diameters(),mark.diameters()[1:])):
        for t in np.linspace(0,1,41):
            x=a[0]+(b[0]-a[0])*t
            true=.5+15.5*((x-5)/100)**gamma
            assert abs(true-(wa+(wb-wa)*t))<=pen.width_tolerance+1e-8


def test_cubic_chain_preserves_join_and_curve_tolerance():
    controls=((8,45),(22,5),(38,5),(54,45),(70,85),(88,85),(104,45))
    p=fineliner(controls,width=3,geometry="bezier",curve_tolerance=.035)
    m=p.resolve()
    assert m.points[0]==controls[0] and m.points[-1]==controls[-1]
    assert controls[3] in m.points
    assert 10<len(m.points)<256
    # Dense mathematical reference only; no raster trace or automatic path inference.
    q=np.array(m.points); a=q[:-1]; v=q[1:]-a
    for k in (0,3):
        c=np.array(controls[k:k+4])
        for t in np.linspace(0,1,101):
            target=(1-t)**3*c[0]+3*(1-t)**2*t*c[1]+3*(1-t)*t*t*c[2]+t**3*c[3]
            u=np.clip(((target-a)*v).sum(axis=1)/(v*v).sum(axis=1),0,1)
            distance=np.linalg.norm(target-a-u[:,None]*v,axis=1).min()
            assert distance<=p.curve_tolerance+1e-8


def test_opaque_gpen_width_and_fineliner_width_across_scales():
    g=g_pen(((10,20),(110,20)),pressure_knots=((0,.2),(.25,.4),(.5,.6),(.75,.8),(1,1)),
            min_width=2,max_width=12,gamma=1)
    p=fineliner(((10,55),(110,55)),width=5)
    for factor in (2,4,8):
        im=_raster(g.resolve(),factor)
        # Integrated coverage measures AA rather than thresholding an arbitrary gray.
        coverage=(255-im[:,:,0].astype(float))/255
        cols=(35,60,85)
        widths=[coverage[:,x].sum() for x in cols]
        assert widths==sorted(widths)
        for got,want in zip(widths,(6,8,10)):
            assert abs(got-want)<.8
        assert all(im[20,x,0]==0 for x in cols)
        f=(255-_raster(p.resolve(),factor)[:,:,0].astype(float))/255
        assert np.max(np.abs(f[:,25:95].sum(axis=0)-5))<.75


def test_point_tapers_have_no_overshoot_and_round_pen_caps_extend():
    g=g_pen(((20,35),(100,35)),pressure_knots=((0,0),(.25,1),(.75,1),(1,0)),
            max_width=12,gamma=1,start_cap="point",end_cap="point")
    mark=g.resolve()
    assert mark.diameters()[0]==mark.diameters()[-1]==0.
    im=_raster(mark)
    assert im[35,:17].min()==255 and im[35,104:].min()==255
    assert im[35,60,0]==0
    round_im=_raster(fineliner(((20,35),(100,35)),width=12).resolve())
    assert round_im[35,16,0]<5 and round_im[35,103,0]<5
    with pytest.raises(ValueError,match="too steep"):
        g_pen(((20,35),(100,35)),pressure_knots=((0,0),(.01,1),(1,.5)),
              max_width=12,gamma=1,start_cap="point").resolve()


def test_self_overlap_and_reverse_geometry_constant_ink():
    a=fineliner(((15,15),(95,65),(15,65),(95,15)),width=6).resolve()
    b=fineliner(tuple(reversed(a.points)),width=6).resolve()
    assert np.array_equal(_raster(a),_raster(b))
    assert _raster(a)[40,55,0]==0


def test_same_geometry_graphite_ink_material_comparison():
    mark=fineliner(((12,40),(108,40)),width=8).resolve()
    im=_raster(mark)
    assert np.all(im[38:42,24:96]==0)
    s=Stroke(list(mark.points),width=8.,opacity=.75,role="contour",pressure=[1.,1.],
             tool_state={"tool":"continuous_pencil","mode":"draw","pencil_grade":"HB",
                         "width":8.,"opacity":.75,"pressure":1.},stroke_id="g")
    with render_image(StrokeIR(120,80,[s]),supersample=4) as graphite:
        a=np.asarray(graphite.convert("RGB"))
        assert a[38:42,24:96,0].mean()>im[38:42,24:96,0].mean()+5
    # This compares media on the same explicit centerline, not artistic quality.


@pytest.mark.parametrize("overrides",[
    {"join":"miter"},{"start_cap":"butt"},{"min_width":-1},{"gamma":float("nan")},
    {"pressure_knots":((0,.1),(.5,True),(1,.2))},
    {"pressure_knots":((0,.1),(.5,.3),(.5,.4),(1,.2))},
    {"geometry":"bezier"},{"curve_tolerance":0},
    {"start_cap":"point"},
])
def test_invalid_pen_inputs_fail_closed(overrides):
    kw=dict(controls=((5,5),(60,20)),pressure_knots=((0,.2),(1,.8)),
            max_width=5,min_width=.1)
    kw.update(overrides)
    with pytest.raises(ValueError):
        g_pen(**kw)


def test_pen_definition_roundtrip_and_rejects_stale_recipe():
    p=g_pen(((10,30),(80,30)),pressure_knots=((0,.2),(.5,.8),(1,.2)),max_width=6)
    a=_action(p,"o","a","ink")
    assert PenDefinition.from_dict(json.loads(json.dumps(p.to_dict())))==p
    assert InkAction.from_dict(a.to_dict())==a
    s=AgentDrawingSession(120,80,media_contract=MIXED_HISTORY_CONTRACT)
    stale=replace(a,pen_definition=replace(p,max_width=7))
    before=s.to_dict()
    with pytest.raises(ValueError,match="does not match"):
        s.execute(stale)
    assert s.to_dict()==before
    s.execute(a)
    saved=s.to_dict()
    saved["history"]["actions"][0]["provenance"]["pen_definition"]["max_width"]=7.
    with pytest.raises(ValueError,match="does not match"):
        AgentDrawingSession.from_dict(saved)


def test_public_pen_preview_edit_resume_and_old_cursor(tmp_path):
    ref=tmp_path/"ref.png"
    Image.new("RGB",(120,80),"white").save(ref)
    profile=RenderProfile.mixed_media(120,80,supersample=4)
    s=DrawingSession.create(subject=ref,output_dir=tmp_path/"session",render_profile=profile)
    oid=s.observe({"fixture":"explicit pen"})
    p=g_pen(((12,40),(30,10),(85,10),(108,40)),geometry="bezier",
            pressure_knots=((0,0),(.5,1),(1,0)),max_width=6,min_width=0,
            gamma=1.3,start_cap="point",end_cap="point")
    a=_action(p,oid,"a","contour")
    apply_ink_actions(s,[a])
    old=s.render_final(tmp_path/"old.png")
    assert read_pen_definition(s,"contour")==p
    edited=replace(p,controls=((12,40),(30,17),(85,17),(108,40)))
    b=_action(edited,oid,"b","contour","ink.replace")
    preview=preview_ink_actions(s,[b],tmp_path/"preview.png")
    apply_ink_actions(s,[b],expected_cursor=preview["base_cursor"],
                      expected_state_hash=preview["base_state_hash"],
                      expected_profile_digest=preview["profile_digest"],
                      expected_action_digest=preview["action_digest"])
    new=s.render_final(tmp_path/"new.png")
    assert new.pixel_sha256==preview["pixel_sha256"]
    assert new.pixel_sha256!=old.pixel_sha256
    assert read_pen_definition(s,"contour")==edited
    revived=DrawingSession.resume(s.checkpoint(),subject=ref)
    assert read_pen_definition(revived,"contour")==edited
    assert revived.render_final(tmp_path/"resume.png").pixel_sha256==new.pixel_sha256
    assert revived.render_at(1,tmp_path/"old-again.png").pixel_sha256==old.pixel_sha256
    # A raw replacement intentionally loses its old recipe instead of reusing stale controls.
    raw=InkAction("c","ink.replace","contour",InkElement("contour",
                  InkPath(((5,5),(30,30)),(1,1),2,2),"contour"),
                  oid,"explicit raw edit","replace with authored samples")
    apply_ink_actions(revived,[raw])
    with pytest.raises(ValueError,match="no current pen definition"):
        read_pen_definition(revived,"contour")


def test_pen_discovery_is_mixed_profile_scoped():
    name="img2drawing.authoring.g_pen"
    assert name not in runtime_capabilities().authoring_helpers
    assert name in runtime_capabilities(RenderProfile.mixed_media(64,48)).authoring_helpers
