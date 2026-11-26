"""Versioned local pressure lift, with exact constant-lift compatibility."""
from dataclasses import replace
import numpy as np
import pytest
from PIL import Image
from img2drawing import DrawingSession, RenderProfile
from img2drawing.authoring import apply_stroke_edits, preview_stroke_edits, pressure_along_path
from img2drawing.render.contract import UnsupportedRendererError
from img2drawing.timelapse.frames import FastFrameSource, CanonicalFrameSource


def make(tmp, v2=True):
    tmp.mkdir(parents=True,exist_ok=True)
    ref=tmp/'ref.png';Image.new('RGB',(128,80),'white').save(ref)
    profile=replace(RenderProfile.opacity_normalized(128,80,pressure_lift=v2),supersample=2,background_rgba=(240,228,213,255))
    s=DrawingSession.create(subject=ref,output_dir=tmp/'run',render_profile=profile,session_id='pressure-test')
    oid=s.observe({'fixture':'analytic curved contact'})
    s.draw([(5,40),(122,40)],stroke_id='graphite',role='value',tool='continuous_pencil',grade='4B',tool_overrides={'width':33,'opacity':.88},pressure=[.8,.8],observation_id=oid)
    return s,oid,ref


def snap(s):return s.history_cursor,s.drawing_state_hash(),s.checkpoint_path.read_bytes()

def rgba(s,p):
    with Image.open(s.render_final(p).path) as im:return np.array(im.convert('RGBA'),dtype=np.int16)


def path(s,oid,pressure=None,**kw):
    return s.erase_path([(16,40),(35,37),(64,38),(92,41),(111,40)],stroke_id='lift',width=10,strength=.8,tool='soft_eraser',reason='explicit reflected curve',observation_id=oid,pressure=pressure,**kw)


def test_profile_identity_and_constant_lift_exact(tmp_path):
    a,oa,_=make(tmp_path/'a',False);b,ob,_=make(tmp_path/'b',True)
    assert a.render_profile.renderer_version=='11-opacity-normalized-v1'
    assert b.render_profile.renderer_version=='11-opacity-normalized-v2'
    assert a.render_profile.renderer_contract_digest!=b.render_profile.renderer_contract_digest
    assert a.drawing_state_hash()==b.drawing_state_hash()
    assert np.array_equal(rgba(a,tmp_path/'a0.png'),rgba(b,tmp_path/'b0.png'))
    path(a,oa);path(b,ob)
    assert a.drawing_state_hash()==b.drawing_state_hash()
    assert np.array_equal(rgba(a,tmp_path/'a1.png'),rgba(b,tmp_path/'b1.png'))
    raw=b.render_profile.to_dict();raw['renderer_contract_digest']=a.render_profile.renderer_contract_digest
    with pytest.raises(UnsupportedRendererError):RenderProfile.from_dict(raw)


def test_tapered_pressure_lift_is_local_reversible_and_resumable(tmp_path):
    s,oid,ref=make(tmp_path);before=rgba(s,tmp_path/'before.png')
    path(s,oid,[0,.32,1,.38,0]);after=rgba(s,tmp_path/'after.png')
    gain=(after[:,:,:3]-before[:,:,:3]).mean(axis=2)
    assert gain[38,64]>35
    assert gain[40,16]<5 and gain[40,111]<5
    assert np.array_equal(before[9:15,25:100],after[9:15,25:100])
    assert s.current_stroke('lift').tool_state['path_lift_contract']=='ordered-graphite-pressure-lift-v1'
    resumed=DrawingSession.resume(s.checkpoint(),subject=ref)
    assert np.array_equal(after,rgba(resumed,tmp_path/'resumed.png'))
    s.delete_stroke('lift',reason='restore original mass',observation_id=oid)
    assert np.array_equal(before,rgba(s,tmp_path/'restored.png'))


def test_fast_canonical_every_action_after_underlying_edit(tmp_path):
    s,oid,ref=make(tmp_path);path(s,oid,[0,.4,.95,.3,0]);s.soft_lift('graphite',strength=.3,reason='correct underlying tone',observation_id=oid)
    s.draw([(10,39),(115,39)],stroke_id='over',role='value',layer=1,tool_overrides={'width':3},observation_id=oid)
    s.delete_stroke('lift',reason='retire',observation_id=oid)
    a=FastFrameSource(s._agent.history,s.render_profile);b=CanonicalFrameSource(s._agent.history,s.render_profile)
    try:
        for i in range(s.history_cursor+1):
            a.advance_to(i);b.advance_to(i)
            with a.image() as x,b.image() as y: assert x.tobytes()==y.tobytes(),i
    finally:a.close();b.close()


def test_preview_binds_pressure_curve_and_retains_checkpoint(tmp_path):
    s,oid,_=make(tmp_path);before=snap(s)
    e=dict(stroke_id='lift',points=[(16,40),(64,38),(111,40)],width=10,strength=.65,pressure=[0,.9,0],tool='soft_eraser')
    kw=dict(reason='review lift profile',observation_id=oid)
    p=preview_stroke_edits(s,[],tmp_path/'preview.png',erasures=[e],**kw);assert snap(s)==before
    with pytest.raises(ValueError,match='differs from preview'):
        apply_stroke_edits(s,[],erasures=[{**e,'pressure':[0,.5,0]}],expected_action_digest=p['action_digest'],**kw)
    assert snap(s)==before
    apply_stroke_edits(s,[],erasures=[e],expected_action_digest=p['action_digest'],expected_cursor=p['base_cursor'],expected_state_hash=p['base_state_hash'],**kw)
    assert s.render_final(tmp_path/'applied.png').pixel_sha256==p['pixel_sha256']


@pytest.mark.parametrize('bad',[[0,1], [0,.4,float('nan'),.3,0], [0,.4,1.1,.3,0], [0,0,0,0,0], [0,False,1,.3,0]])
def test_invalid_pressure_rejects_before_commit(tmp_path,bad):
    s,oid,_=make(tmp_path);before=snap(s)
    with pytest.raises(ValueError):path(s,oid,bad)
    assert snap(s)==before


def test_old_profile_rejects_varying_pressure(tmp_path):
    s,oid,_=make(tmp_path,False);before=snap(s)
    with pytest.raises(ValueError,match='pressure_lift=True'):path(s,oid,[0,.4,1,.3,0])
    assert snap(s)==before
