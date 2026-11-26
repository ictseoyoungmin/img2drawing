"""Mixed explicit corrections use existing canonical draw/replace/delete actions."""
from dataclasses import replace
from pathlib import Path
import pytest
from PIL import Image
from img2drawing import DrawingSession, RenderProfile
from img2drawing.authoring import StrokeEdit, apply_stroke_edits, preview_stroke_edits


def make(tmp_path):
    ref=tmp_path/'ref.png'; Image.new('RGB',(64,64),'white').save(ref)
    s=DrawingSession.create(subject=ref,output_dir=tmp_path/'run',render_profile=replace(RenderProfile.opacity_normalized(64,64),supersample=2))
    oid=s.observe({'fixture':'explicit observed mark family'})
    a=s.draw([(8,14),(20,14),(40,14)],stroke_id='a',observation_id=oid)
    b=s.draw([(8,30),(20,30),(40,30)],stroke_id='b',observation_id=oid)
    return s,oid,a,b,ref


def spec(sid='new',points=((10,44),(42,44))):
    return {'stroke_id':sid,'points':points,'role':'value','part':'test','tool':'continuous_pencil','pressure':[.5,.6]}


def snapshot(s):
    return s.history_cursor,s.drawing_state_hash(),s.checkpoint_path.read_bytes()


def test_mixed_preview_apply_exact_and_resume(tmp_path):
    s,oid,a,b,ref=make(tmp_path); before=snapshot(s)
    edits=[StrokeEdit(a,tuple(s.current_stroke(a).points),material_overrides={'width':4})]
    kw=dict(reason='reviewed explicit family rewrite',observation_id=oid,retire_ids=[b],additions=[spec()])
    p=preview_stroke_edits(s,edits,tmp_path/'preview.png',**kw)
    assert snapshot(s)==before
    ids=apply_stroke_edits(s,edits,expected_cursor=p['base_cursor'],expected_state_hash=p['base_state_hash'],expected_action_digest=p['action_digest'],**kw)
    assert list(ids)==p['action_ids'] and len(ids)==3
    assert s.history_cursor==before[0]+3 and s.drawing_state_hash()==p['prospective_state_hash']
    assert s.render_final(tmp_path/'final.png').pixel_sha256==p['pixel_sha256']
    assert {st.stroke_id for st in s.current_ir().strokes}=={'a','new'}
    assert DrawingSession.resume(s.checkpoint(),subject=ref).drawing_state_hash()==s.drawing_state_hash()


def test_rejected_and_changed_proposals_never_commit(tmp_path):
    s,oid,a,b,ref=make(tmp_path); before=snapshot(s)
    kw=dict(reason='review',observation_id=oid,retire_ids=[b])
    p=preview_stroke_edits(s,[],tmp_path/'preview.png',additions=[spec()],**kw)
    assert snapshot(s)==before
    with pytest.raises(ValueError,match='differs from preview'):
        apply_stroke_edits(s,[],additions=[spec(points=((10,45),(42,45)))],expected_action_digest=p['action_digest'],**kw)
    assert snapshot(s)==before


@pytest.mark.parametrize('bad_kind',['missing','duplicate','edited_retired','reuse','duplicate_add','arbitrary_kind','no_id','out_of_bounds','retired_reuse','invalid_eraser'])
def test_bad_mixed_batch_rolls_back(tmp_path,bad_kind):
    s,oid,a,b,ref=make(tmp_path)
    if bad_kind=='retired_reuse': s.delete_stroke(a,observation_id=oid,reason='retired before proposal')
    before=snapshot(s); edits=[]; retire=[b]; additions=[spec()]
    if bad_kind=='missing': retire=['unknown']
    elif bad_kind=='duplicate': retire=[b,b]
    elif bad_kind=='edited_retired': edits=[StrokeEdit(b,tuple(s.current_stroke(b).points))]
    elif bad_kind=='reuse': additions=[spec(a)]
    elif bad_kind=='duplicate_add': additions=[spec(),spec()]
    elif bad_kind=='arbitrary_kind': additions=[{**spec(),'kind':'delete_stroke'}]
    elif bad_kind=='no_id': additions=[{k:v for k,v in spec().items() if k!='stroke_id'}]
    elif bad_kind=='out_of_bounds': additions=[spec(points=((10,44),(100,100))) ]
    elif bad_kind=='retired_reuse': additions=[spec(a)]
    elif bad_kind=='invalid_eraser': additions=[{**spec(),'tool':'hard_eraser'}]
    kw=dict(reason='invalid mixed proposal',observation_id=oid,retire_ids=retire,additions=additions)
    with pytest.raises(ValueError): preview_stroke_edits(s,edits,tmp_path/'invalid.png',**kw)
    assert snapshot(s)==before
    with pytest.raises(ValueError): apply_stroke_edits(s,edits,**kw)
    assert snapshot(s)==before


def test_retire_only_and_add_only(tmp_path):
    s,oid,a,b,ref=make(tmp_path)
    p=preview_stroke_edits(s,[],tmp_path/'retire.png',reason='retire',observation_id=oid,retire_ids=[b])
    apply_stroke_edits(s,[],reason='retire',observation_id=oid,retire_ids=[b],expected_action_digest=p['action_digest'])
    assert {x.stroke_id for x in s.current_ir().strokes}=={a}
    p=preview_stroke_edits(s,[],tmp_path/'add.png',reason='add',observation_id=oid,additions=[spec()])
    apply_stroke_edits(s,[],reason='add',observation_id=oid,additions=[spec()],expected_action_digest=p['action_digest'])
    assert {x.stroke_id for x in s.current_ir().strokes}=={a,'new'}
