"""Width control is explicit material data, and strip diagnostics never author marks."""
from dataclasses import replace
import numpy as np
import pytest
from PIL import Image
from img2drawing import DrawingSession, RenderProfile
from img2drawing.authoring import (ContactWidthProfile, read_contact_width_profile,
    StrokeEdit, preview_stroke_edits, apply_stroke_edits, retune_stroke, inspect_tonal_proposals)
from img2drawing.inspection import TonalBandProbe, inspect_tonal_bands, compare_tonal_bands
from img2drawing.render.contract import UnsupportedRendererError
from img2drawing.timelapse.frames import FastFrameSource, CanonicalFrameSource


def make(tmp_path,version=3):
    tmp_path.mkdir(parents=True,exist_ok=True)
    ref=tmp_path/'ref.png'; Image.new('RGB',(160,100),(170,170,170)).save(ref)
    profile=RenderProfile.canonical(160,100) if version==0 else RenderProfile.opacity_normalized(160,100,pressure_lift=version>=2,contact_width=version==3)
    s=DrawingSession.create(subject=ref,output_dir=tmp_path/'run',render_profile=replace(profile,supersample=2),session_id='contact-width-test')
    return s,s.observe({'fixture':'explicit curve width and band observation'}),ref


def draw(s,oid,profile=None,opacity=.72):
    return s.draw([(20,50),(60,50),(100,50),(140,50)],stroke_id='mass',role='value',tool='continuous_pencil',grade='4B',
                  tool_overrides={'width':36,'opacity':opacity,'jitter':0.,'taper_in':0.,'taper_out':0.},
                  pressure=[.8]*4,observation_id=oid,metadata=None if profile is None else profile.metadata())


def rgb(s,p):
    with Image.open(s.render_final(p).path) as im:return np.asarray(im.convert('RGB'),dtype=np.int16)


def snap(s):return s.history_cursor,s.drawing_state_hash(),s.checkpoint_path.read_bytes()


def test_default_and_all_one_are_exact(tmp_path):
    a,oa,_=make(tmp_path/'a',2);b,ob,_=make(tmp_path/'b',3);c,oc,_=make(tmp_path/'c',3)
    draw(a,oa);draw(b,ob);draw(c,oc,ContactWidthProfile(((0,1),(.33,1),(1,1))))
    assert a.render_profile.renderer_version=='11-opacity-normalized-v2'
    assert b.render_profile.renderer_version=='11-opacity-normalized-v3'
    assert a.render_profile.renderer_contract_digest!=b.render_profile.renderer_contract_digest
    first=rgb(a,tmp_path/'a.png')
    assert np.array_equal(first,rgb(b,tmp_path/'b.png'))
    assert np.array_equal(first,rgb(c,tmp_path/'c.png'))
    invalid=b.render_profile.to_dict();invalid['renderer_contract_digest']=a.render_profile.renderer_contract_digest
    with pytest.raises(UnsupportedRendererError):RenderProfile.from_dict(invalid)


@pytest.mark.parametrize('version',[0,1,2])
def test_older_contract_rejects_before_mutation(tmp_path,version):
    s,oid,_=make(tmp_path,version);before=snap(s)
    with pytest.raises(ValueError,match='contact_width=True'):
        draw(s,oid,ContactWidthProfile(((0,.4),(1,1))))
    assert snap(s)==before


def test_width_changes_support_not_authored_pressure_and_preview_binds(tmp_path):
    s,oid,ref=make(tmp_path);draw(s,oid)
    before=rgb(s,tmp_path/'before.png');old=s.current_stroke('mass')
    p=ContactWidthProfile(((0,.2),(.35,.2),(.65,1),(1,1)))
    edit=StrokeEdit('mass',tuple(old.points),contact_width_profile=p)
    state=snap(s);args={'reason':'vary contact only','observation_id':oid}
    preview=preview_stroke_edits(s,[edit],tmp_path/'preview.png',**args);assert snap(s)==state
    alternate=replace(edit,contact_width_profile=ContactWidthProfile(((0,.4),(1,1))))
    with pytest.raises(ValueError,match='differs from preview'):
        apply_stroke_edits(s,[alternate],expected_action_digest=preview['action_digest'],**args)
    assert snap(s)==state
    apply_stroke_edits(s,[edit],expected_cursor=preview['base_cursor'],expected_state_hash=preview['base_state_hash'],expected_action_digest=preview['action_digest'],**args)
    assert s.drawing_state_hash()==preview['prospective_state_hash']
    assert s.render_final(tmp_path/'applied.png').pixel_sha256==preview['pixel_sha256']
    after=rgb(s,tmp_path/'final.png');now=s.current_stroke('mass')
    assert (now.points,now.pressure,now.width,now.opacity)==(old.points,old.pressure,old.width,old.opacity)
    assert read_contact_width_profile(s,'mass')==p
    assert np.array_equal(before[:10],after[:10])
    # Width shrinks only where requested; tests measure actual rendered support.
    def span(im,x):return np.count_nonzero(im[:,x,:].mean(axis=1)<242)
    assert span(after,40)<.55*span(before,40)
    assert abs(span(after,120)-span(before,120))<=4
    assert np.array_equal(after,rgb(DrawingSession.resume(s.checkpoint(),subject=ref),tmp_path/'resume.png'))
    retune_stroke(s,'mass',reason='change opacity only',tool_overrides={'opacity':.5},observation_id=oid)
    assert read_contact_width_profile(s,'mass')==p


def test_split_restricts_recipe_and_fast_canonical_all_cursors(tmp_path):
    s,oid,ref=make(tmp_path);p=ContactWidthProfile(((0,.2),(.4,.9),(1,.35)));draw(s,oid,p)
    st=s.current_stroke('mass');e=StrokeEdit('mass',tuple(st.points),split_at=1,new_stroke_id='tail')
    apply_stroke_edits(s,[e],reason='split observed form',observation_id=oid)
    a,b=read_contact_width_profile(s,'mass'),read_contact_width_profile(s,'tail')
    assert a.at(1)==pytest.approx(p.at(1/3))==pytest.approx(b.at(0))
    assert b.at(1)==pytest.approx(p.at(1))
    s.erase_path([(70,50),(90,50),(110,50)],stroke_id='lift',width=5,strength=.65,pressure=[0,1,0],tool='soft_eraser',reason='visible light',observation_id=oid)
    s.soft_lift('mass',strength=.3,reason='retune beneath lift',observation_id=oid)
    s.delete_stroke('lift',reason='retire lift',observation_id=oid)
    resumed=DrawingSession.resume(s.checkpoint(),subject=ref)
    fast=FastFrameSource(resumed._agent.history,resumed.render_profile);can=CanonicalFrameSource(resumed._agent.history,resumed.render_profile)
    try:
        for n in range(resumed.history_cursor+1):
            fast.advance_to(n);can.advance_to(n)
            with fast.image() as a,can.image() as b:assert a.tobytes()==b.tobytes(),n
    finally:fast.close();can.close()


@pytest.mark.parametrize('knots',[((0,.1),(1,1)),((0,1),(.5,.8),(.5,.4),(1,1)),((.1,1),(1,1)),((0,True),(1,1)),((0,float('nan')),(1,1)),((0,.4),(1,1.01))])
def test_invalid_width_knots(knots):
    with pytest.raises(ValueError):ContactWidthProfile(knots)


def test_zero_opacity_and_eraser_rejection(tmp_path):
    s,oid,_=make(tmp_path);p=ContactWidthProfile(((0,.2),(1,1)))
    blank=rgb(s,tmp_path/'blank.png');draw(s,oid,p,opacity=0)
    assert np.array_equal(blank,rgb(s,tmp_path/'zero.png'))
    before=snap(s)
    with pytest.raises(ValueError,match='graphite drawing only'):
        s.draw([(20,20),(40,40)],role='value',tool='soft_eraser',metadata=p.metadata(),observation_id=oid)
    assert snap(s)==before


def test_band_probe_detects_local_reversals_and_keeps_real_ones(tmp_path):
    shape=(48,64);paper=np.full(shape,255,dtype=np.uint8)
    smooth=np.tile(np.repeat(np.arange(8)*8+160,8),(48,1)).astype(np.uint8)
    stripes=np.tile(np.repeat([190,120,190,120,190,120,190,120],8),(48,1)).astype(np.uint8)
    for name,image in [('smooth',smooth),('striped',stripes),('paper',paper)]:Image.fromarray(image).save(tmp_path/f'{name}.png')
    p=TonalBandProbe('plane',(0,0,64,48),(0,0,64,48),'x',8)
    s=compare_tonal_bands(tmp_path/'smooth.png',tmp_path/'striped.png',tmp_path/'paper.png',p)
    assert s['evidence_binding']=='external_images_unverified'
    b=s['band_metrics'];assert b['reference']['prominent_turns']==0;assert b['drawing']['prominent_turns']==6;assert len(b['unmatched_drawing_turns'])==6
    real=compare_tonal_bands(tmp_path/'striped.png',tmp_path/'striped.png',tmp_path/'paper.png',p)
    assert not real['band_metrics']['unmatched_drawing_turns']
    assert p.summarize(s)==b
    with pytest.raises(ValueError):replace(p,axis='y').summarize(s)
    with pytest.raises(ValueError):TonalBandProbe('bad',(0,0,3,20),(0,0,3,20),'x',8)


def test_canonical_and_prospective_band_inspection(tmp_path):
    s,oid,_=make(tmp_path);draw(s,oid)
    p=TonalBandProbe('plane',(15,28,145,72),(15,28,145,72),'x',13)
    s.render_at(0,tmp_path/'paper.png');s.render_final(tmp_path/'base.png');before=snap(s)
    cache={0:tmp_path/'paper.png',s.history_cursor:tmp_path/'base.png'}
    base=inspect_tonal_bands(s,p,cached_renders=cache)
    assert base['evidence_binding']=='canonical_session';assert all(x['source']=='verified_cached_artifact' for x in base['render_inputs'])
    e=StrokeEdit('mass',tuple(s.current_stroke('mass').points),contact_width_profile=ContactWidthProfile(((0,.5),(.5,1),(1,.4))))
    v=inspect_tonal_proposals(s,{'taper':{'edits':[e]}},{'plane':p.patches()},tmp_path/'proposals',reason='compare explicit width',observation_id=oid,cached_renders=cache)
    assert snap(s)==before
    b=p.summarize(v['proposals']['taper']['chains']['plane']);assert b['bins']==13
