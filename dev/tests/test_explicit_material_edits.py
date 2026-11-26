"""Explicit material edits share the atomic geometry preview/apply contract."""
from dataclasses import replace
import math
import pytest
from PIL import Image
from img2drawing import DrawingSession, RenderProfile
from img2drawing.authoring import StrokeEdit, apply_stroke_edits, preview_stroke_edits


def make(tmp_path):
    ref=tmp_path/'ref.png'; Image.new('RGB',(64,64),'white').save(ref)
    s=DrawingSession.create(subject=ref,output_dir=tmp_path/'run',
        render_profile=replace(RenderProfile.opacity_normalized(64,64),supersample=2))
    oid=s.observe({'fixture':'explicit edits'})
    a=s.draw([(10,14),(20,14),(30,14),(40,14)],pressure=[.2,.6,.7,.3],observation_id=oid,tool_overrides={'width':8,'opacity':.7})
    b=s.draw([(10,34),(20,34),(30,34),(40,34)],pressure=[.3,.7,.6,.4],observation_id=oid,tool_overrides={'width':6,'opacity':.6})
    return s,oid,a,b,ref


def test_heterogeneous_material_preview_commit_and_resume(tmp_path):
    s,oid,a,b,ref=make(tmp_path)
    s.soft_lift_segment(a,1,2,strength=.5,feather_points=1,observation_id=oid,reason='local relief')
    s.soft_lift(b,strength=.5,observation_id=oid,reason='lighten')
    old_a=s.current_stroke(a); old_b=s.current_stroke(b)
    supplied={'width':12,'opacity':.3,'hardness':.6,'grain':.4}
    e=StrokeEdit(a,tuple(old_a.points),material_overrides=supplied)
    supplied['opacity']=.99
    assert e.material_overrides['opacity']==.3
    edits=[e,StrokeEdit(b,tuple(old_b.points),material_overrides={'width':10})]
    cp=s.checkpoint_path.read_bytes(); state=s.drawing_state_hash(); cursor=s.history_cursor
    p=preview_stroke_edits(s,edits,tmp_path/'preview.png',reason='value revision',observation_id=oid)
    assert (s.checkpoint_path.read_bytes(),s.drawing_state_hash(),s.history_cursor)==(cp,state,cursor)
    apply_stroke_edits(s,edits,reason='value revision',observation_id=oid,expected_cursor=p['base_cursor'],expected_state_hash=p['base_state_hash'])
    assert s.history_cursor==cursor+2 and s.drawing_state_hash()==p['prospective_state_hash']
    assert s.render_final(tmp_path/'committed.png').pixel_sha256==p['pixel_sha256']
    na,nb=s.current_stroke(a),s.current_stroke(b)
    assert na.points==old_a.points and na.pressure==old_a.pressure
    assert na.opacity==.3 and na.width==12 and na.tool_state['hardness']==.6 and na.tool_state['grain']==.4
    assert nb.opacity==old_b.opacity and nb.pressure==old_b.pressure and nb.width==10
    assert DrawingSession.resume(s.checkpoint(),subject=ref).drawing_state_hash()==s.drawing_state_hash()
    with pytest.raises(ValueError,match='stale'):
        apply_stroke_edits(s,edits,reason='old preview',observation_id=oid,expected_cursor=cursor)


@pytest.mark.parametrize('bad',[{'opacity':float('nan')},{'opacity':1.1},{'width':0},{'width':float('inf')},{'grain':True},{'pressure':.5},{'taper_out':.1},{'hardness':-1},['opacity',.4]])
def test_material_overrides_validate_before_mutation(bad):
    with pytest.raises(ValueError):
        StrokeEdit('x',((1,1),(2,2)),material_overrides=bad)


def test_material_batch_rollback_if_geometry_invalid(tmp_path):
    s,oid,a,b,ref=make(tmp_path)
    cp=s.checkpoint_path.read_bytes(); state=s.drawing_state_hash(); cursor=s.history_cursor
    edits=[StrokeEdit(a,tuple(s.current_stroke(a).points),material_overrides={'opacity':.2}),
           StrokeEdit(b,((1,1),(100,100)),pressure=(.4,.4),material_overrides={'opacity':.2})]
    with pytest.raises(ValueError):
        apply_stroke_edits(s,edits,reason='bad edit',observation_id=oid)
    assert (s.checkpoint_path.read_bytes(),s.drawing_state_hash(),s.history_cursor)==(cp,state,cursor)
