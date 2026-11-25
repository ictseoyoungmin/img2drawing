import math
import pytest
from PIL import Image
from img2drawing import DrawingSession
from img2drawing.authoring import (
    resample_polyline, sample_cubic_bezier, pressure_along_path, curve_join,
    deform_interval, StrokeEdit, transform_strokes, apply_stroke_edits, preview_stroke_edits,
)

def make(tmp):
    ref=tmp/"ref.png"
    Image.new("RGB",(80,80),"white").save(ref)
    s=DrawingSession.create(subject=ref,output_dir=tmp/"run")
    oid=s.observe({"test":"explicit geometry"})
    return s,oid,ref

def test_sampling_and_pressure_arc_length():
    p=resample_polyline([(0,0),(10,0)],spacing=3)
    assert p==[(0,0),(2.5,0),(5,0),(7.5,0),(10,0)]
    q=sample_cubic_bezier([(0,0),(0,10),(10,10),(10,0)],spacing=1)
    assert q[0]==(0,0) and q[-1]==(10,0)
    assert max(y for x,y in q)>7
    assert pressure_along_path([(0,0),(1,0),(4,0)],[(0,0),(1,1)])==[0,.25,1]
    with pytest.raises(ValueError):
        resample_polyline([(0,0),(100,0)],spacing=1e-12)
    with pytest.raises(ValueError):
        pressure_along_path([(0,0),(1,0)],[(0,0),(.5,1)])

def test_join_and_deform_preserve_endpoint():
    assert curve_join([(0,0),(2,0)],[(2,0),(2,3)])=={"gap":0,"tangent_delta_degrees":90}
    p=[(0,0),(1,0),(2,0),(3,0),(4,0)]
    q=deform_interval(p,1,3,(0,5))
    assert q==[(0,0),(1,0),(2,5),(3,0),(4,0)]
    assert p[2]==(2,0)

def test_preview_matches_commit_and_preserves_attenuation(tmp_path):
    s,oid,ref=make(tmp_path)
    a=s.draw([(10,10),(20,10),(30,10)],pressure=[.3,.7,.4],tool="continuous_pencil",observation_id=oid)
    b=s.draw([(10,20),(20,20)],observation_id=oid)
    s.soft_lift(a,strength=.5,reason="lighten",observation_id=oid)
    old=s.current_stroke(a)
    edits=transform_strokes(s,[a,b],(1,0,0,1,4,3))
    cp=s.checkpoint_path.read_bytes()
    report=preview_stroke_edits(s,edits,tmp_path/"preview.png",reason="shift",observation_id=oid)
    assert s.checkpoint_path.read_bytes()==cp and s.history_cursor==3
    ids=apply_stroke_edits(s,edits,reason="shift",observation_id=oid,
        expected_cursor=report["base_cursor"],expected_state_hash=report["base_state_hash"])
    assert len(ids)==2 and s.drawing_state_hash()==report["prospective_state_hash"]
    artifact=s.render_final(tmp_path/"final.png")
    assert artifact.pixel_sha256==report["pixel_sha256"]
    after=s.current_stroke(a)
    assert after.opacity==old.opacity and after.pressure==old.pressure and after.width==old.width
    resumed=DrawingSession.resume(s.checkpoint(),subject=ref)
    assert resumed.drawing_state_hash()==s.drawing_state_hash()
    with pytest.raises(ValueError,match="stale"):
        apply_stroke_edits(s,edits,reason="stale",observation_id=oid,expected_cursor=3)

def test_split_records_two_addressable_fragments(tmp_path):
    s,oid,ref=make(tmp_path)
    sid=s.draw([(10,10),(20,10),(30,20),(40,20)],pressure=[.2,.4,.6,.8],observation_id=oid)
    old=s.current_stroke(sid)
    e=StrokeEdit(sid,tuple(old.points),split_at=2,new_stroke_id="tail")
    preview=preview_stroke_edits(s,[e],tmp_path/"split.png",reason="split ownership",observation_id=oid)
    actions=apply_stroke_edits(s,[e],reason="split ownership",observation_id=oid)
    assert len(actions)==2 and s.history_cursor==3
    assert s.current_stroke(sid).pressure==[.2,.4,.6]
    assert s.current_stroke("tail").pressure==[.6,.8]
    assert s.drawing_state_hash()==preview["prospective_state_hash"]

def test_batch_failure_rolls_back_and_pressure_alignment(tmp_path):
    s,oid,ref=make(tmp_path)
    a=s.draw([(10,10),(20,20)],observation_id=oid)
    b=s.draw([(10,20),(20,30)],observation_id=oid)
    old=(s.history_cursor,s.drawing_state_hash(),s.checkpoint_path.read_bytes())
    with pytest.raises(ValueError):
        apply_stroke_edits(s,[StrokeEdit(a,((11,10),(20,20))),StrokeEdit(b,((10,20),(90,30)))],
                          reason="invalid",observation_id=oid)
    assert (s.history_cursor,s.drawing_state_hash(),s.checkpoint_path.read_bytes())==old
    with pytest.raises(ValueError,match="point count"):
        apply_stroke_edits(s,[StrokeEdit(a,((10,10),(15,15),(20,20)))],
                          reason="insert",observation_id=oid)
    assert (s.history_cursor,s.drawing_state_hash(),s.checkpoint_path.read_bytes())==old
