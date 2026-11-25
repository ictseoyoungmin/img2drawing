import math
import pytest
from PIL import Image
from img2drawing import DrawingSession, ConstructionMark, DrawingIntent, ReferenceAuthority
from img2drawing.inspection import Registration
from img2drawing.authoring import projected_ellipse, ProjectedSection, projected_envelope, author_projection_guides

def test_ellipse_arc_skew_vectors_and_exact_closure():
    p=projected_ellipse((20,30),(10,0),(4,5),segments=4)
    assert p[0]==p[-1]==(30,30)
    assert p[1]==pytest.approx((24,35))
    q=projected_ellipse((20,30),(10,0),(4,5),start_degrees=90,sweep_degrees=-90,segments=3)
    assert q[0]==pytest.approx((24,35)) and q[-1]==pytest.approx((30,30))
    with pytest.raises(ValueError,match="nonparallel"):
        projected_ellipse((0,0),(1,0),(2,0))
    with pytest.raises(ValueError):
        projected_ellipse((0,0),(1,0),(0,1),segments=100000)

def test_explicit_asymmetric_sections_no_terminal_caps():
    a=ProjectedSection.from_widths((20,20),(4,0),left_width=5,right_width=8)
    b=ProjectedSection.from_widths((22,40),(2,1),left_width=3,right_width=6)
    p=projected_envelope((a,b),include_axis=True,include_sections=True)
    assert p["left"][0]==(15,20) and p["right"][0]==(28,20)
    assert p["axis"]==[(20,20),(22,40)]
    assert set(p)=={"left","right","axis","section_0","section_1"}
    with pytest.raises(ValueError):
        projected_envelope((a,ProjectedSection((22,40),b.right,b.left)))

def test_construction_uses_canonical_actions_and_retires(tmp_path):
    ref=tmp_path/"ref.png"
    Image.new("RGB",(64,64),"white").save(ref)
    s=DrawingSession.create(subject=ref,output_dir=tmp_path/"run")
    oid=s.observe({"owner":"explicit construction hypothesis"})
    guide=ConstructionMark("guide-ellipse","mass_blocking","structure","object",
                           tuple(projected_ellipse((30,30),(15,0),(0,8))))
    result=author_projection_guides(s,(guide,),observation_id=oid,
                                    registration=Registration.identity((64,64)))
    assert result.action_ids==("guide-ellipse",)
    assert s.history_cursor==1
    assert s.current_stroke("guide-ellipse").points[0]==(45,30)
    s.delete_stroke("guide-ellipse",observation_id=oid,reason="description replaces guide")
    cp=s.checkpoint()
    resumed=DrawingSession.resume(cp,subject=ref)
    assert resumed.history_cursor==2 and not resumed.current_ir().strokes
    assert resumed.drawing_state_hash()==s.drawing_state_hash()

def test_invalid_batch_fails_without_history_change(tmp_path):
    s=DrawingSession.create(canvas=(64,64),output_dir=tmp_path/"run",
        intent=DrawingIntent(reference_mode="imaginative",drawing_mode="free_draw"),
        reference_authority=ReferenceAuthority.imaginative(("test explicit guide geometry",)))
    oid=s.observe({"owner":"declared shape"})
    good=ConstructionMark("good","mass_blocking","structure","mass",((1,1),(4,4)))
    bad=ConstructionMark("bad","mass_blocking","structure","mass",((1,1),(80,80)))
    before=s.drawing_state_hash(),s.checkpoint_path.read_bytes()
    with pytest.raises(ValueError):
        author_projection_guides(s,(good,bad),observation_id=oid,
                                registration=Registration.identity((64,64)))
    assert s.history_cursor==0
    assert (s.drawing_state_hash(),s.checkpoint_path.read_bytes())==before
