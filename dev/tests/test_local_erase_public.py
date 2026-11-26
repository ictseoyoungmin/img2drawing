import pytest
from PIL import Image
from img2drawing import DrawingSession
from img2drawing.authoring import retune_stroke, reshape_stroke


def create(tmp_path):
    ref=tmp_path/'reference.png'
    Image.new('RGB',(80,80),'white').save(ref)
    s=DrawingSession.create(subject=ref,output_dir=tmp_path/'run')
    oid=s.observe({'scope':'explicit local correction fixture'})
    sid=s.draw([(10+i*7,30) for i in range(8)],part='edge',role='contour',
               tool_overrides={'width':4,'pressure':.7,'opacity':.8},observation_id=oid)
    return s,oid,sid,ref


def test_local_lift_and_retune_preserve_edited_pressure_and_opacity(tmp_path):
    s,oid,sid,ref=create(tmp_path)
    original=s.current_stroke(sid)
    assert not original.pressure_authored
    start=s.history_cursor; state=s.drawing_state_hash()
    aid=s.soft_lift_segment(sid,2,4,strength=.75,feather_points=1,reason='local light',
                            observation_id=oid,expected_cursor=start,expected_state_hash=state)
    edited=s.current_stroke(sid)
    expected=[x*(.25 if 2<=i<=4 else .625 if i in (1,5) else 1) for i,x in enumerate(original.pressure)]
    assert list(edited.pressure)==pytest.approx(expected)
    assert edited.points==original.points and edited.opacity==original.opacity and edited.width==original.width
    assert s.resolve_authored_element(sid,element_type='stroke').latest_action_id==aid
    s.soft_lift(sid,strength=.4,reason='overall soften',observation_id=oid)
    opacity=s.current_stroke(sid).opacity
    retune_stroke(s,sid,reason='narrow edge',tool_overrides={'width':3},observation_id=oid)
    tuned=s.current_stroke(sid)
    assert tuned.opacity==opacity and tuned.width==3 and list(tuned.pressure)==pytest.approx(expected)
    reshape_stroke(s,sid,[(x,y+1) for x,y in tuned.points],reason='align edge',observation_id=oid)
    resumed=DrawingSession.resume(s.checkpoint(),subject=ref)
    assert resumed.history_cursor==5 and resumed.drawing_state_hash()==s.drawing_state_hash()
    assert list(resumed.current_stroke(sid).pressure)==pytest.approx(expected)
    assert resumed.current_stroke(sid).opacity==opacity
    retune_stroke(resumed,sid,reason='intentional opacity',tool_overrides={'opacity':.2},observation_id=oid)
    assert resumed.current_stroke(sid).opacity==pytest.approx(.2)


@pytest.mark.parametrize('kwargs', [dict(start_index=2,end_index=2),dict(start_index=-1,end_index=2),
    dict(start_index=1.5,end_index=4),dict(start_index=1,end_index=20),dict(strength=float('nan')),
    dict(strength=1.1),dict(feather_points=-1),dict(feather_points=20),dict(expected_cursor=0),
    dict(expected_state_hash='stale'),dict(observation_id='unknown'),dict(reason='')])
def test_local_lift_rejects_invalid_or_stale_without_mutation(tmp_path,kwargs):
    s,oid,sid,ref=create(tmp_path)
    cp=s.checkpoint_path.read_bytes();state=s.drawing_state_hash();cursor=s.history_cursor
    with pytest.raises(ValueError):
        s.soft_lift_segment(sid,**{**dict(start_index=2,end_index=4,strength=.5,reason='correct',observation_id=oid),**kwargs})
    assert s.checkpoint_path.read_bytes()==cp and s.history_cursor==cursor and s.drawing_state_hash()==state
