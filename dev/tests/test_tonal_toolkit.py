import pytest
import numpy as np
from PIL import Image
from img2drawing import DrawingIntent, DrawingSession, RenderProfile
from img2drawing.authoring import (
    TonalAreaPlan, resolve_mark_for_intent, TonalPressureAdjustment,
    prepare_tonal_pressure_edits, apply_stroke_edits, preview_stroke_edits,
)
from img2drawing.inspection import inspect_tonal_interval
from img2drawing.inspection.tonal import measure_plan


def make(tmp):
    ref=tmp/"ref.png"
    Image.new("RGB",(64,64),"white").save(ref)
    s=DrawingSession.create(subject=ref,output_dir=tmp/"run",
        intent=DrawingIntent(drawing_mode="croquis"),
        render_profile=RenderProfile.from_dict({**RenderProfile.canonical(64,64).to_dict(),"supersample":2}))
    oid=s.observe({"test":"explicit tonal plans"})
    return s,oid,ref

def plan(name="a",left=8,right=40,reserve=True):
    return TonalAreaPlan(area_id=name,part="swatch",reference_evidence="analytic fixture",
        boundary=((left,8),(right,8),(right,56),(left,56)),direction_degrees=90,
        target_density=.5,target_value=.6,pressure_range=(.3,.8),
        highlight_reserves=(((left+2,26),(right-2,26),(right-2,36),(left+2,36)),) if reserve else ())

def add(s,oid,p,points,pressure):
    mark=resolve_mark_for_intent(s.intent,"value",tool_preset="broad-graphite",
                               modifiers={"width":5,"opacity":.7})
    return s.draw(points,pressure=pressure,part="swatch",observation_id=oid,
        **mark.draw_kwargs(metadata=p.stroke_metadata(stroke_family="vertical")))

def test_explicit_pressure_proposal_preview_and_real_inspection(tmp_path):
    s,oid,ref=make(tmp_path)
    p=plan()
    sid=add(s,oid,p,[(20,10),(20,24),(20,30),(20,38),(20,54)],[.8,.8,.8,.8,.8])
    before=s.checkpoint_path.read_bytes()
    initial=inspect_tonal_interval(s,0,1)
    row=initial["areas"][0]
    assert row["protected_after"]["coverage"]>0
    geom=row["current_stroke_diagnostics"][0]
    assert geom["stroke_id"]==sid
    assert geom["mean_axial_direction_error_degrees"]==pytest.approx(0)
    assert geom["protected_centerline_fraction"]>0
    assert initial["artistic_verdict"]=="NOT_EVALUATED"
    assert s.checkpoint_path.read_bytes()==before
    edits=prepare_tonal_pressure_edits(s,[TonalPressureAdjustment(sid,1,3,.0,1)])
    assert s.checkpoint_path.read_bytes()==before
    preview=preview_stroke_edits(s,edits,tmp_path/"preview.png",reason="reduce protected light marks",observation_id=oid)
    apply_stroke_edits(s,edits,reason="reduce protected light marks",observation_id=oid,
        expected_cursor=preview["base_cursor"],expected_state_hash=preview["base_state_hash"])
    assert s.drawing_state_hash()==preview["prospective_state_hash"]
    result=inspect_tonal_interval(s,1,2)["areas"][0]
    assert result["protected_after"]["mean_darkness"]<result["protected_before"]["mean_darkness"]
    assert result["target_removed_mean"]>0
    assert s.current_stroke(sid).points==[(20,10),(20,24),(20,30),(20,38),(20,54)]

def test_separation_and_outside_diagnostic(tmp_path):
    s,oid,_=make(tmp_path)
    a,b=plan("a",2,28,False),plan("b",36,60,False)
    add(s,oid,a,[(10,10),(10,40)],[.7,.7])
    add(s,oid,b,[(32,10),(32,40)],[.9,.9])
    m=inspect_tonal_interval(s,0,2,separation_pairs=[("a","b")])
    assert len(m["separation"])==1
    row=next(x for x in m["areas"] if x["area_id"]=="b")
    assert row["current_stroke_diagnostics"][0]["outside_centerline_fraction"]==pytest.approx(1)
    assert row["current_stroke_diagnostics"][0]["pressure_sample_outside_declared_range"]==1
    with pytest.raises(ValueError):
        inspect_tonal_interval(s,0,2,separation_pairs=[("a","a")])

def test_pressure_proposal_rejects_invalid_or_unknown(tmp_path):
    s,oid,_=make(tmp_path)
    sid=add(s,oid,plan(),[(10,10),(10,30)],[.6,.6])
    before=s.drawing_state_hash()
    with pytest.raises(ValueError):
        prepare_tonal_pressure_edits(s,[TonalPressureAdjustment(sid,0,2,.4)])
    assert s.drawing_state_hash()==before

def test_measurement_does_not_reuse_target_density_as_luminance():
    paper=np.ones((64,64)); after=paper.copy(); after[8:56,8:40]=.2
    m=measure_plan(paper,paper,after,plan())
    assert m["target_after"]["mean_darkness"]==pytest.approx(.8)
    assert m["protected_after"]["coverage"]==1


def test_verified_cached_renders_reuse_history_prefix_and_reject_tampering(tmp_path):
    s,oid,ref=make(tmp_path)
    blank=s.render_at(0,tmp_path/"blank.png")
    add(s,oid,plan(),[(10,10),(10,40)],[.7,.7])
    first=s.render_final(tmp_path/"first.png")
    add(s,oid,plan(),[(16,10),(16,40)],[.7,.7])
    last=s.render_final(tmp_path/"last.png")
    expected=inspect_tonal_interval(s,1,2)
    actual=inspect_tonal_interval(s,1,2,cached_renders={0:blank.path,1:first.path,2:last.path})
    assert expected["areas"]==actual["areas"]
    assert [v["source"] for v in actual["render_inputs"]]==["verified_cached_artifact"]*3
    with pytest.raises(ValueError,match="invalid cached canonical render"):
        inspect_tonal_interval(s,1,2,cached_renders={1:last.path})
    with Image.open(first.path) as img:
        corrupted=img.copy()
    corrupted.putpixel((0,0),(0,0,0,255))
    corrupted.save(first.path)
    with pytest.raises(ValueError,match="invalid cached canonical render"):
        inspect_tonal_interval(s,1,2,cached_renders={1:first.path})
