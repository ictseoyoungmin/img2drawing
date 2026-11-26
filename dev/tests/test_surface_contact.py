"""Explicit side-contact scope, exact compatibility, and overlap behavior."""
from dataclasses import replace
import numpy as np
import pytest
from PIL import Image
from img2drawing import DrawingSession, RenderProfile
from img2drawing.authoring import (SurfaceContactProfile, read_surface_contact_profile,
    ContactWidthProfile, StrokeEdit, preview_stroke_edits, apply_stroke_edits, retune_stroke)
from img2drawing.render.contract import UnsupportedRendererError
from img2drawing.timelapse.frames import FastFrameSource, CanonicalFrameSource


def make(tmp, *, v4=True, w=192, h=112):
    tmp.mkdir(parents=True,exist_ok=True)
    ref=tmp/'ref.png';Image.new('RGB',(w,h),(180,180,180)).save(ref)
    p=replace(RenderProfile.opacity_normalized(w,h,contact_width=True,surface_contact=v4),supersample=2)
    s=DrawingSession.create(subject=ref,output_dir=tmp/'run',render_profile=p,session_id='surface-contact-test')
    return s,s.observe({'fixture':'explicit graphite contact on observed plane'}),ref


def draw(s,oid,sid='mass',points=((18,50),(174,50)),surface=None,width=None,opacity=.35):
    meta={} if width is None else width.metadata()
    if surface is not None:meta=surface.metadata(meta)
    return s.draw(points,stroke_id=sid,role='value',part='plane',tool='continuous_pencil',grade='2B',
                  tool_overrides={'width':40,'opacity':opacity,'jitter':0.,'taper_in':0.,'taper_out':0.},
                  pressure=[.65]*len(points),observation_id=oid,metadata=meta or None)


def pixels(s,p):
    with Image.open(s.render_final(p).path) as im:return np.asarray(im.convert('RGBA'),dtype=np.int16)


def snapshot(s):return s.history_cursor,s.drawing_state_hash(),s.checkpoint_path.read_bytes()


def test_v4_unmarked_v3_exact_and_distinct_digest(tmp_path):
    a,oa,_=make(tmp_path/'a',v4=False);b,ob,_=make(tmp_path/'b')
    w=ContactWidthProfile(((0,.35),(.3,1),(1,.4)))
    for s,o in [(a,oa),(b,ob)]:
        draw(s,o,width=w)
        s.erase_path([(65,50),(85,50),(105,50)],stroke_id='lift',width=8,pressure=[0,1,0],
                     tool='soft_eraser',strength=.8,reason='local reflection',observation_id=o)
    assert a.drawing_state_hash()==b.drawing_state_hash()
    assert np.array_equal(pixels(a,tmp_path/'a.png'),pixels(b,tmp_path/'b.png'))
    assert b.render_profile.renderer_version=='11-opacity-normalized-v4'
    raw=b.render_profile.to_dict();raw['renderer_contract_digest']=a.render_profile.renderer_contract_digest
    with pytest.raises(UnsupportedRendererError):RenderProfile.from_dict(raw)


@pytest.mark.parametrize('bad',[True,.34,.86,float('nan'),float('inf'),'0.65'])
def test_invalid_shoulder(bad):
    with pytest.raises(ValueError):SurfaceContactProfile(bad)


def test_v3_rejects_before_mutation(tmp_path):
    s,o,_=make(tmp_path,v4=False);before=snapshot(s)
    with pytest.raises(ValueError,match='surface_contact=True'):draw(s,o,surface=SurfaceContactProfile())
    assert snapshot(s)==before


def test_overlap_is_not_always_better(tmp_path):
    values={}
    for shape in ('radial','side'):
        for spacing in (18,24):
            s,o,_=make(tmp_path/f'{shape}{spacing}')
            for j in range(4):
                y=24+j*spacing
                draw(s,o,f's{j}',((18,y),(174,y)),surface=SurfaceContactProfile() if shape=='side' else None)
            a=pixels(s,tmp_path/f'{shape}{spacing}.png')
            profile=1-a[24:24+3*spacing,45:147,:3].mean(axis=(1,2))/255
            values[shape,spacing]=(float(profile.std()),float(profile.mean()))
    # The side-contact shoulders are complementary only for an appropriate spacing.
    # At 24px, reduce strip variation relative to mean, not merely overall darkness.
    assert values['side',24][0]/values['side',24][1] < .45*values['radial',24][0]/values['radial',24][1]
    assert values['side',18][0]/values['side',18][1] > values['radial',18][0]/values['radial',18][1]


def test_preview_set_clear_split_retune_resume_replay(tmp_path):
    s,o,ref=make(tmp_path);w=ContactWidthProfile(((0,.25),(.35,.9),(1,.5)))
    draw(s,o,points=((8,10),(38,28),(92,45),(55,78),(55,36),(55,78),(176,110)),width=w)
    original=pixels(s,tmp_path/'original.png');st=s.current_stroke('mass')
    edit=StrokeEdit('mass',tuple(st.points),surface_contact_profile=SurfaceContactProfile(.8))
    before=snapshot(s);args={'reason':'reassess graphite shoulder','observation_id':o}
    pre=preview_stroke_edits(s,[edit],tmp_path/'preview.png',**args);assert snapshot(s)==before
    with pytest.raises(ValueError,match='differs from preview'):
        apply_stroke_edits(s,[replace(edit,surface_contact_profile=SurfaceContactProfile(.5))],expected_action_digest=pre['action_digest'],**args)
    apply_stroke_edits(s,[edit],expected_cursor=pre['base_cursor'],expected_state_hash=pre['base_state_hash'],expected_action_digest=pre['action_digest'],**args)
    assert s.render_final(tmp_path/'applied.png').pixel_sha256==pre['pixel_sha256']
    assert s.current_stroke('mass').pressure==st.pressure
    assert read_surface_contact_profile(s,'mass')==SurfaceContactProfile(.8)
    assert read_surface_contact_profile(DrawingSession.resume(s.checkpoint(),subject=ref),'mass')==SurfaceContactProfile(.8)
    apply_stroke_edits(s,[StrokeEdit('mass',tuple(st.points),clear_surface_contact=True)],**args)
    assert read_surface_contact_profile(s,'mass') is None
    assert np.array_equal(original,pixels(s,tmp_path/'cleared.png'))
    apply_stroke_edits(s,[edit],**args)
    retune_stroke(s,'mass',reason='adjust existing graphite',tool_overrides={'opacity':.5},observation_id=o)
    assert read_surface_contact_profile(s,'mass')==SurfaceContactProfile(.8)
    cur=s.current_stroke('mass')
    apply_stroke_edits(s,[StrokeEdit('mass',tuple(cur.points),split_at=2,new_stroke_id='tail')],**args)
    assert read_surface_contact_profile(s,'tail')==SurfaceContactProfile(.8)
    s.erase_path([(50,38),(55,50),(60,62)],stroke_id='lift',width=9,pressure=[0,1,0],
                 tool='soft_eraser',reason='local reflected light',observation_id=o)
    s.delete_stroke('lift',reason='retire lift',observation_id=o)
    a=FastFrameSource(s._agent.history,s.render_profile);b=CanonicalFrameSource(s._agent.history,s.render_profile)
    try:
        for cursor in range(s.history_cursor+1):
            a.advance_to(cursor);b.advance_to(cursor)
            with a.image() as x,b.image() as y:assert x.tobytes()==y.tobytes(),cursor
    finally:a.close();b.close()


def test_zero_and_eraser_boundary(tmp_path):
    s,o,_=make(tmp_path);blank=pixels(s,tmp_path/'blank.png');p=SurfaceContactProfile()
    draw(s,o,surface=p,opacity=0)
    assert np.array_equal(blank,pixels(s,tmp_path/'zero.png'))
    before=snapshot(s)
    with pytest.raises(ValueError,match='graphite drawing only'):
        s.draw([(10,20),(20,20)],tool='soft_eraser',metadata=p.metadata(),observation_id=o)
    assert snapshot(s)==before
