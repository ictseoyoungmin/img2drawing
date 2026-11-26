"""Explicit projected hypotheses and prospective tonal decisions over ordinary history."""
from dataclasses import replace
import math

import pytest
from PIL import Image
from img2drawing import DrawingSession, RenderProfile
from img2drawing.authoring import (
    VolumeStation, ProjectedVolume, ProjectionCamera, inspect_attachment, align_attachment,
    author_projection_guides, prepare_volume_edits, CurveDefinition, read_parametric_curve,
    StrokeEdit, preview_stroke_edits, apply_stroke_edits, inspect_tonal_proposals, TonalAreaPlan,
)
from img2drawing.inspection import Registration, TonalPatch


def form():
    return ProjectedVolume((VolumeStation(0,(48,14),-10,16,20),
                            VolumeStation(.4,(50,40),5,22,24),
                            VolumeStation(1,(58,79),24,9,13)))


def make(tmp_path):
    ref=tmp_path/'ref.png';Image.new('RGB',(96,96),(150,150,150)).save(ref)
    s=DrawingSession.create(subject=ref,output_dir=tmp_path/'run',
        render_profile=replace(RenderProfile.opacity_normalized(96,96),supersample=2))
    return s,s.observe({'fixture':'explicit projected and value relationship'}),ref


def snapshot(s):
    return s.history_cursor,s.drawing_state_hash(),s.checkpoint_path.read_bytes()


def commit(s, edits, tmp_path, oid, name='candidate'):
    before=snapshot(s)
    report=preview_stroke_edits(s,edits,tmp_path/f'{name}.png',reason='review explicit edit',observation_id=oid)
    assert snapshot(s)==before
    apply_stroke_edits(s,edits,reason='review explicit edit',observation_id=oid,
        expected_cursor=report['base_cursor'],expected_state_hash=report['base_state_hash'],
        expected_action_digest=report['action_digest'])
    assert s.drawing_state_hash()==report['prospective_state_hash']
    assert s.render_final(tmp_path/f'{name}-final.png').pixel_sha256==report['pixel_sha256']


def test_volume_anchors_widths_smoothness_and_serialization():
    v=form();sampled=v.sampled_stations(samples_per_span=1000)
    assert (sampled[0],sampled[1000],sampled[-1])==v.stations
    for s in sampled:
        assert 9<=s.left_width<=22 and 13<=s.right_width<=24
    # Derivative on both sides of the explicitly nonuniform middle station.
    a,b,c=sampled[999:1002]
    for attr in ('left_width','right_width','angle_degrees'):
        d0=(getattr(b,attr)-getattr(a,attr))/(b.t-a.t)
        d1=(getattr(c,attr)-getattr(b,attr))/(c.t-b.t)
        assert d0==pytest.approx(d1,abs=.8)
    assert ProjectedVolume.from_dict(v.to_dict())==v
    paths=v.paths(section_arcs={1:dict(depth_axis=(0,4),start_degrees=0,sweep_degrees=180)})
    assert paths['section_1'][0]==pytest.approx(v.stations[1].edges[1])
    assert paths['section_1'][-1]==pytest.approx(v.stations[1].edges[0])
    assert set(v.paths())=={'axis','left','right'}


def test_angle_wrap_and_reversed_station_guard():
    a=VolumeStation(0,(20,10),179,5,7);b=VolumeStation(1,(20,30),-179,8,10)
    v=ProjectedVolume((a,b));assert abs(v.sampled_stations(samples_per_span=2)[1].angle_degrees)==pytest.approx(180)
    with pytest.raises(ValueError):ProjectedVolume((a,replace(b,angle_degrees=0)))
    with pytest.raises(ValueError):v.sampled_stations(samples_per_span=20_000)


def test_projection_uses_explicit_depth_and_rejects_continuous_near_plane_crossing():
    p=ProjectionCamera((48,48),100,perspective=True,near=.1)
    assert p.project((1,0,2))==(98,48)
    assert p.project((1,0,4))==(73,48)
    assert ProjectionCamera((48,48),10).project((1,0,-4))==(58,48)
    arc=p.section_arc((0,0,5),(1,0,0),(0,1,1),start_degrees=0,sweep_degrees=180,segments=4)
    assert arc[0]==pytest.approx((68,48));assert arc[2]==pytest.approx((48,48+100/6))
    with pytest.raises(ValueError):p.section_arc((0,0,.6),(1,0,0),(0,1,1),start_degrees=210,sweep_degrees=120,segments=3)


def test_attachment_is_explicit_and_local_width_match():
    v=form();anchor=VolumeStation(1,(42,12),-30,12,13)
    before=inspect_attachment(anchor,v.stations[0]);assert before['center_gap']>0
    translated=align_attachment(anchor,v,child_index=0)
    assert translated.stations[0].center==anchor.center
    assert translated.stations[0].angle_degrees==v.stations[0].angle_degrees
    assert translated.stations[0].left_width==v.stations[0].left_width
    aligned=align_attachment(anchor,v,child_index=0,rotate=True,match_widths=True)
    assert all(x==pytest.approx(0,abs=1e-9) for x in inspect_attachment(anchor,aligned.stations[0]).values())
    assert aligned.stations[-1].left_width==v.stations[-1].left_width
    assert math.dist(*[s.center for s in aligned.stations[:2]])==pytest.approx(math.dist(*[s.center for s in v.stations[:2]]))
    assert v==form()


def test_guides_roundtrip_edit_retire_and_replay(tmp_path):
    s,oid,ref=make(tmp_path);v=form();reg=Registration.identity((96,96))
    s.draw([(9,9),(12,14)],stroke_id='unrelated',role='form',observation_id=oid)
    initial=s.render_final(tmp_path/'initial.png').pixel_sha256
    arcs={1:dict(depth_axis=(0,4),start_degrees=0,sweep_degrees=180)}
    marks=v.guide_marks('mass','test',selected=('left','right','axis','section_1'),section_arcs=arcs)
    result=author_projection_guides(s,marks,observation_id=oid,registration=reg)
    assert len(result.action_ids)==4
    v2=ProjectedVolume((v.stations[0],replace(v.stations[1],center=(51,42),right_width=19),v.stations[2]))
    edits=prepare_volume_edits(s,v2,{'left':'mass-left','right':'mass-right','axis':'mass-axis','section_1':'mass-section_1'},registration=reg,samples_per_span=8,section_arcs=arcs)
    commit(s,edits,tmp_path,oid)
    resumed=DrawingSession.resume(s.checkpoint(),subject=ref)
    assert resumed.drawing_state_hash()==s.drawing_state_hash()
    for mark in marks:resumed.delete_stroke(mark.mark_id,reason='retire provisional guide',observation_id=oid)
    assert resumed.render_final(tmp_path/'retired.png').pixel_sha256==initial


@pytest.mark.parametrize('kind,controls',[('bezier',((10,30),(20,17),(35,47),(70,30))),('spline',((10,30),(30,17),(48,45),(70,30)))])
def test_curve_controls_persist_edit_preview_and_stale_detection(tmp_path,kind,controls):
    s,oid,ref=make(tmp_path)
    c=CurveDefinition(kind,controls,((0,.2),(.55,.85),(1,.1)))
    s.draw(stroke_id='curve',role='form',tool='continuous_pencil',observation_id=oid,**c.draw_kwargs())
    assert read_parametric_curve(s,'curve')==c
    resumed=DrawingSession.resume(s.checkpoint(),subject=ref)
    assert read_parametric_curve(resumed,'curve')==c
    revised=replace(c,controls=(controls[0],(22,22),*controls[2:]),spacing=2.5)
    commit(resumed,[revised.edit('curve')],tmp_path,oid)
    assert read_parametric_curve(resumed,'curve')==revised
    resumed.soft_lift_segment('curve',1,3,strength=.5,reason='explicit pressure correction',observation_id=oid)
    with pytest.raises(ValueError,match='stale|no current'):read_parametric_curve(resumed,'curve')


def test_curve_invalid_recipe_and_sample_budget():
    c=CurveDefinition('bezier',((1,1),(2,4),(3,3),(5,5)),((0,.2),(1,.7)))
    p,q=c.sample()
    with pytest.raises(ValueError):StrokeEdit('c',p,tuple(0 for _ in q),curve_definition=c)
    with pytest.raises(ValueError):CurveDefinition('spline',((0,0),(20,20)),((0,.2),(1,.7)),spacing=1e-12).sample()


def test_tonal_alternatives_share_baseline_and_exact_commit(tmp_path):
    s,oid,_=make(tmp_path)
    s.draw([(15,45),(48,45),(80,45)],stroke_id='shade',role='value',tool='continuous_pencil',grade='4B',
           tool_overrides={'width':18,'opacity':.8},pressure=[.7,.7,.7],observation_id=oid)
    stroke=s.current_stroke('shade');points=tuple(stroke.points)
    proposals={'light':{'edits':(StrokeEdit('shade',points,material_overrides={'opacity':.15}),)},
               'moderate':{'edits':(StrokeEdit('shade',points,material_overrides={'opacity':.45}),)}}
    chains={'across':[TonalPatch('a',(20,35,30,42),(20,35,30,42)),TonalPatch('b',(20,43,30,50),(20,43,30,50))]}
    plan=TonalAreaPlan('plane','test','observed broad plane',((10,32),(85,32),(85,58),(10,58)),0,.5,.5,(.1,.8))
    before=snapshot(s)
    with pytest.raises(ValueError,match='budget'):inspect_tonal_proposals(s,proposals,chains,tmp_path/'no',reason='test',observation_id=oid,max_pixel_work=1)
    assert not (tmp_path/'no').exists()
    report=inspect_tonal_proposals(s,proposals,chains,tmp_path/'previews',reason='test',observation_id=oid,plans=(plan,))
    assert snapshot(s)==before
    a,b=[report['proposals'][k] for k in proposals]
    assert a['areas'][0]['target_after']['mean_darkness']<b['areas'][0]['target_after']['mean_darkness']
    selected=b['preview']
    apply_stroke_edits(s,proposals['moderate']['edits'],reason='test',observation_id=oid,expected_cursor=selected['base_cursor'],expected_state_hash=selected['base_state_hash'],expected_action_digest=selected['action_digest'])
    assert s.render_final(tmp_path/'accepted.png').pixel_sha256==selected['pixel_sha256']
