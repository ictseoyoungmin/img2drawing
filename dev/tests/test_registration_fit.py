from pathlib import Path
import pytest
from PIL import Image

from img2drawing import DrawingSession, RenderProfile
from img2drawing.authoring import InkAction, InkElement, solid_ink, apply_ink_actions
from img2drawing.inspection import Registration


@pytest.mark.parametrize("mode,scale,offset",[
    ("contain",(2.,2.),(0.,50.)),("cover",(3.,3.),(-50.,0.)),
    ("stretch",(2.,3.),(0.,0.)),
])
def test_explicit_fit_maps_image_rectangles_and_roundtrips(mode,scale,offset):
    r=Registration.fit((100,100),(200,300),mode=mode)
    assert r.scale==scale and r.offset==offset
    assert r.map_subject_to_canvas((0,0))==offset
    assert r.map_subject_to_canvas((50,50))==pytest.approx((100,150))
    assert r.map_canvas_to_subject(r.map_subject_to_canvas((24.5,62.5)))==pytest.approx((24.5,62.5))
    assert Registration.fit((100,100),(100,100),mode=mode)==Registration.identity((100,100))


@pytest.mark.parametrize("subject,canvas,mode",[
    ((0,100),(100,100),"contain"),((100,100),(100,-1),"contain"),
    ((100,100),(100,100),"automatic"),
])
def test_invalid_fit_rejected(subject,canvas,mode):
    with pytest.raises(ValueError):
        Registration.fit(subject,canvas,mode=mode)


def test_explicit_fit_unblocks_mixed_inspection_without_geometry_change(tmp_path):
    ref=tmp_path/"reference.png"
    Image.new("RGB",(80,40),"white").save(ref)
    profile=RenderProfile.mixed_media(64,48,supersample=2)
    s=DrawingSession.create(subject=ref,canvas=(64,48),output_dir=tmp_path/"session",
                            render_profile=profile)
    oid=s.observe({"fixture":"explicit whole-image mapping"})
    mark=solid_ink(((8,8),(50,8),(50,36),(8,36),(8,8)))
    apply_ink_actions(s,[InkAction("a","ink.add","mass",InkElement("mass",mark,"value"),
                                   oid,"fixture","explicit mass")])
    before=s.drawing_state_hash()
    final=s.render_final(tmp_path/"final.png")
    with pytest.raises(ValueError,match="Registration.fit"):
        s.inspect()
    r=Registration.fit((80,40),(64,48),mode="contain")
    sheet=s.inspect(registration=r,supersample=profile.supersample)
    assert sheet.drawing_state_hash==before==s.drawing_state_hash()
    assert s.render_profile==profile
    with Image.open(sheet.drawing) as a,Image.open(final.path) as b:
        assert a.convert("RGBA").tobytes()==b.convert("RGBA").tobytes()
