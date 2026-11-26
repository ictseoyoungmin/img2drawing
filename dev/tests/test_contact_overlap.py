from dataclasses import replace
import numpy as np
import pytest
from PIL import Image
from img2drawing import DrawingSession, RenderProfile
from img2drawing.authoring import ContactWidthProfile, StrokeEdit, apply_stroke_edits
from img2drawing.inspection import inspect_contact_overlap


def make(tmp_path):
    ref=tmp_path/'ref.png';Image.new('RGB',(96,96),'white').save(ref)
    s=DrawingSession.create(subject=ref,output_dir=tmp_path/'run',render_profile=replace(RenderProfile.opacity_normalized(96,96,contact_width=True),supersample=2))
    oid=s.observe({'fixture':'explicit contact pair'})
    return s,oid


def draw(s,oid,sid,x):
    return s.draw([(x,12),(x,84)],stroke_id=sid,role='value',tool='continuous_pencil',grade='4B',tool_overrides={'width':26,'opacity':.8},pressure=[.8,.8],observation_id=oid)


def snap(s):return s.history_cursor,s.drawing_state_hash(),s.checkpoint_path.read_bytes()


def test_overlap_gap_and_read_only(tmp_path):
    s,oid=make(tmp_path);draw(s,oid,'a',32);draw(s,oid,'b',39);draw(s,oid,'c',82)
    state=snap(s)
    a=inspect_contact_overlap(s,['a','b'],(5,20,90,75),bins=8)
    b=inspect_contact_overlap(s,['a','c'],(5,20,90,75),bins=8)
    assert snap(s)==state
    assert a['pairs'][0]['overlap_fraction']>0
    assert b['pairs'][0]['overlap_fraction']==0
    assert a['summary']['multiple_fraction']>b['summary']['multiple_fraction']
    assert a['artistic_verdict']=='NOT_EVALUATED'
    assert abs(sum(a['summary'][k] for k in ['uncovered_fraction','single_fraction','multiple_fraction'])-1)<1e-8


def test_width_and_eraser_exclusion(tmp_path):
    s,oid=make(tmp_path);draw(s,oid,'a',32);draw(s,oid,'b',39)
    old=inspect_contact_overlap(s,['a','b'],(10,25,72,70),bins=6)
    st=s.current_stroke('b');apply_stroke_edits(s,[StrokeEdit('b',tuple(st.points),contact_width_profile=ContactWidthProfile(((0,.2),(1,.2))))],reason='explicit narrow contact',observation_id=oid)
    new=inspect_contact_overlap(s,['a','b'],(10,25,72,70),bins=6)
    assert new['strokes'][1]['covered_fraction']<old['strokes'][1]['covered_fraction']
    s.erase_path([(20,40),(55,40)],stroke_id='lift',width=8,strength=.7,pressure=[0.5,1],reason='test ordered lift',observation_id=oid)
    after=inspect_contact_overlap(s,['a','b'],(10,25,72,70),bins=6)
    assert after['summary']==new['summary']
    with pytest.raises(ValueError,match='not erasers'):inspect_contact_overlap(s,['a','lift'],(10,25,72,70))


@pytest.mark.parametrize('ids,box,kwargs', [(['a','a'],(0,0,96,96),{}),(['a','missing'],(0,0,96,96),{}),(['a','b'],(-1,0,96,96),{}),(['a','b'],(0,0,96,96),{'max_pixel_work':1}),(['a','b'],(0,0,96,96),{'bins':65}),(['a','b'],(0,0,96,96),{'threshold':float('nan')})])
def test_invalid_requests_fail_closed(tmp_path,ids,box,kwargs):
    s,oid=make(tmp_path);draw(s,oid,'a',32);draw(s,oid,'b',39);before=snap(s)
    with pytest.raises(ValueError):inspect_contact_overlap(s,ids,box,**kwargs)
    assert snap(s)==before
