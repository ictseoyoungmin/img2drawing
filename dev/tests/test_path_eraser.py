"""Ordered path lifts reuse the canonical graphite composite and history."""
from dataclasses import replace
import numpy as np
import pytest
from PIL import Image
from img2drawing import DrawingSession, RenderProfile
from img2drawing.authoring import apply_stroke_edits, preview_stroke_edits
from img2drawing.core.history import CanvasHistory
from img2drawing.core.stroke import tool_stroke
from img2drawing.core.tools import hard_eraser
from img2drawing.timelapse.frames import FastFrameSource, CanonicalFrameSource, inspect_fast_path_eligibility


def make(tmp, normalized=True):
    tmp.mkdir(parents=True, exist_ok=True)
    ref=tmp/'ref.png'; Image.new('RGB',(80,64),'white').save(ref)
    factory=RenderProfile.opacity_normalized if normalized else RenderProfile.canonical
    s=DrawingSession.create(subject=ref,output_dir=tmp/'run',render_profile=replace(factory(80,64),supersample=2,background_rgba=(232,218,199,255)))
    oid=s.observe({'fixture':'explicit visible graphite lift'})
    return s,oid,ref


def snapshot(s):
    return s.history_cursor,s.drawing_state_hash(),s.checkpoint_path.read_bytes()


def draw(s,oid,sid,y,layer=0):
    return s.draw([(8,y),(40,y),(72,y)],stroke_id=sid,role='value',part='plane',tool='continuous_pencil',grade='4B',tool_overrides={'width':13,'opacity':.75},pressure=[.8]*3,observation_id=oid,layer=layer)


def erase(s,oid,sid='lift',**kwargs):
    return s.erase_path([(40,8),(40,54)],stroke_id=sid,width=3.0,reason='lift a visible narrow reflection',observation_id=oid,**kwargs)


def rgb(path):
    with Image.open(path) as im:return np.array(im.convert('RGB'),dtype=np.int16)


def test_lift_crosses_multiple_graphite_marks_and_does_not_paint_paper(tmp_path):
    s,oid,ref=make(tmp_path)
    blank=rgb(s.render_final(tmp_path/'paper.png').path)
    draw(s,oid,'a',23); draw(s,oid,'b',39)
    before=rgb(s.render_final(tmp_path/'before.png').path)
    assert erase(s,oid)=='lift'
    lifted=rgb(s.render_final(tmp_path/'lifted.png').path)
    for y in (23,39):
        assert lifted[y,40].mean() > before[y,40].mean()+15
        assert np.array_equal(lifted[y,20],before[y,20])
    assert np.array_equal(lifted[12,40],blank[12,40])
    assert s.current_stroke('lift').role=='highlight_lift'
    assert s.resolve_authored_element('lift',element_type='stroke').status=='current'
    s.delete_stroke('lift',reason='retire the lift',observation_id=oid)
    assert np.array_equal(rgb(s.render_final(tmp_path/'restored.png').path),before)


def test_exact_fast_replay_layer_order_edit_and_retirement(tmp_path):
    s,oid,ref=make(tmp_path)
    draw(s,oid,'a',23); draw(s,oid,'b',39,layer=1)
    erase(s,oid,layer=1)
    draw(s,oid,'c',23,layer=1) # after lift on same layer
    draw(s,oid,'d',39,layer=-1) # added later but rendered below lift
    s.soft_lift('a',strength=.3,reason='revise underlying graphite',observation_id=oid)
    s.replace_segment('b',0,1,[(8,39),(23,37),(40,39)],reason='revise prior path',observation_id=oid)
    s.delete_stroke('lift',reason='retire',observation_id=oid)
    erase(s,oid,'lift-2',layer=1,tool='soft_eraser',strength=.5)
    assert inspect_fast_path_eligibility(s._agent.history).eligible
    resumed=DrawingSession.resume(s.checkpoint(),subject=ref)
    assert resumed.drawing_state_hash()==s.drawing_state_hash()
    fast=FastFrameSource(resumed._agent.history,resumed.render_profile)
    canonical=CanonicalFrameSource(resumed._agent.history,resumed.render_profile)
    try:
        for cursor in range(resumed.history_cursor+1):
            fast.advance_to(cursor);canonical.advance_to(cursor)
            with fast.image() as a,canonical.image() as b:assert a.tobytes()==b.tobytes(),cursor
    finally: fast.close();canonical.close()


def test_mixed_preview_apply_and_digest_guard(tmp_path):
    s,oid,ref=make(tmp_path); draw(s,oid,'a',23)
    before=snapshot(s)
    adds=[dict(stroke_id='new',points=[(8,39),(72,39)],role='value',tool='continuous_pencil',tool_overrides={'width':9})]
    erasures=[dict(stroke_id='lift',points=[(40,8),(40,54)],width=3,strength=.7)]
    kw=dict(reason='review value and light',observation_id=oid,retire_ids=['a'],additions=adds,erasures=erasures)
    p=preview_stroke_edits(s,[],tmp_path/'preview.png',**kw)
    assert snapshot(s)==before
    with pytest.raises(ValueError,match='differs from preview'):
        apply_stroke_edits(s,[],**{**kw,'erasures':[{**erasures[0],'strength':.8}]},expected_action_digest=p['action_digest'])
    assert snapshot(s)==before
    apply_stroke_edits(s,[],**kw,expected_cursor=p['base_cursor'],expected_state_hash=p['base_state_hash'],expected_action_digest=p['action_digest'])
    assert s.history_cursor==before[0]+3
    assert s.drawing_state_hash()==p['prospective_state_hash']
    assert s.render_final(tmp_path/'final.png').pixel_sha256==p['pixel_sha256']


def test_legacy_raw_eraser_still_uses_existing_fallback():
    h=CanvasHistory(32,32)
    h.add_stroke(tool_stroke([(5,5),(10,10)],hard_eraser()),stroke_id='raw')
    result=inspect_fast_path_eligibility(h)
    assert not result.eligible and result.raw_spatial_eraser_seen


def test_legacy_profile_refuses_new_path_eraser(tmp_path):
    s,oid,ref=make(tmp_path,False); before=snapshot(s)
    with pytest.raises(ValueError,match='opacity-normalized'):erase(s,oid)
    assert snapshot(s)==before


@pytest.mark.parametrize('bad',[{'width':0},{'width':float('nan')},{'width':10000},{'strength':0},{'strength':1.2},{'tool':'form_pencil'},{'layer':1.5},{'points':[(1,1),(1,1)]},{'points':[(5,5),(90,10)]},{'observation_id':'unknown'},{'reason':''},{'stroke_id':'a'}])
def test_invalid_mixed_path_lift_is_atomic(tmp_path,bad):
    s,oid,ref=make(tmp_path);draw(s,oid,'a',23);before=snapshot(s)
    base=dict(stroke_id='lift',points=[(40,8),(40,54)],width=3,strength=.7)
    # Batch-level observation/reason cannot be overridden by a path record.
    proposal=dict(reason='explicit correction',observation_id=oid,additions=[dict(stroke_id='b',points=[(8,39),(72,39)],role='value',tool='continuous_pencil')],erasures=[{**base,**bad}])
    with pytest.raises(ValueError):apply_stroke_edits(s,[],**proposal)
    assert snapshot(s)==before


def test_path_eraser_cannot_be_retuned_as_graphite(tmp_path):
    s,oid,ref=make(tmp_path);draw(s,oid,'a',23);erase(s,oid);before=snapshot(s)
    with pytest.raises(ValueError,match='re-author'):
        s.soft_lift('lift',strength=.5,reason='invalid material edit',observation_id=oid)
    with pytest.raises(ValueError,match='re-author'):
        s.soft_lift_segment('lift',0,1,strength=.5,reason='invalid material edit',observation_id=oid)
    assert snapshot(s)==before
