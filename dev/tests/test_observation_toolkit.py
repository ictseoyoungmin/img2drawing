from __future__ import annotations

import json
import math

import pytest
from PIL import Image

from img2drawing import DrawingSession
from img2drawing.inspection import Registration
from img2drawing.observation import (
    Landmark, LandmarkSet, compare_landmarks, compare_ratios, compare_axes,
    cross_section, compare_negative_space, occlusion_relation,
)
from img2drawing.runtime import runtime_capabilities


def landmarks(space, size, **values):
    return LandmarkSet(space,size,tuple(Landmark(name,p,"agent selected visible anchor")
                                       for name,p in values.items()))


def test_explicit_registration_and_normalization():
    ref = landmarks("subject",(100,100), a=(10,10), b=(50,10), c=(30,30))
    draw = landmarks("canvas",(200,200), a=(25,17), b=(105,17), c=(67,45))
    reg = Registration((100,100),(200,200),scale=(2,1.5),offset=(5,2))
    result = compare_landmarks(ref,draw,registration=reg,labels=("a","b","c"),normalizer=("a","b"))
    assert result.value["normalizer_length_canvas"] == 80
    assert result.value["landmarks"][-1]["delta"] == [2,-2]
    assert result.value["normalized_rms"] == pytest.approx(math.sqrt(8/3)/80)
    assert result.provenance["artistic_verdict"] == "NOT_EVALUATED"
    json.dumps(result.to_dict(),allow_nan=False)
    with pytest.raises(ValueError,match="sizes"):
        compare_landmarks(ref,draw,registration=Registration.identity((100,100)),
                          labels=("a",),normalizer=("a","b"))


def test_unknown_uncertain_inferred_and_duplicate_rejected():
    s = LandmarkSet("subject",(100,100),(
        Landmark("a",(0,0),"visible"),
        Landmark("b",(4,5),"hidden joint estimate","inferred"),
        Landmark("c",None,"unclear edge","uncertain")))
    assert s.to_dict()["landmarks"][2]["position"] is None
    for name in ("b","c","unknown"):
        with pytest.raises(ValueError):
            s.observed(name)
    with pytest.raises(ValueError,match="duplicate"):
        LandmarkSet("subject",(100,100),(s.landmarks[0],s.landmarks[0]))
    with pytest.raises(ValueError,match="outside"):
        landmarks("subject",(10,10),a=(11,0))
    with pytest.raises(ValueError):
        Landmark("bad",(float("nan"),0),"not finite")


def test_ratio_uses_mapped_canvas_not_raw_subject():
    ref = landmarks("subject",(100,100), a=(0,0), b=(10,0), c=(0,10))
    draw = landmarks("canvas",(200,200), a=(0,0), b=(20,0), c=(0,15))
    result = compare_ratios(ref,draw,registration=Registration((100,100),(200,200),scale=(2,1)),
                            numerator=("a","b"),denominator=("a","c"))
    assert result.value["reference"] == 2
    assert result.value["drawing"] == pytest.approx(4/3)
    assert result.value["delta"] == pytest.approx(-2/3)
    with pytest.raises(ValueError,match="denominator"):
        landmarks("subject",(100,100),a=(1,1),b=(1,1),c=(2,2)).ratio(("a","c"),("a","b"))


def test_axis_orientation_wrap_and_anisotropic_registration():
    ref = landmarks("subject",(100,100), a=(20,20), b=(30,30))
    draw = landmarks("canvas",(200,200), a=(60,30), b=(40,20))
    reg = Registration((100,100),(200,200),scale=(2,1))
    assert compare_axes(ref,draw,registration=reg,axis=("a","b")).value["signed_delta_degrees"] == pytest.approx(0)
    assert abs(compare_axes(ref,draw,registration=reg,axis=("a","b"),directed=True).value["signed_delta_degrees"]) == pytest.approx(180)


def test_cross_section_reports_oblique_offset():
    s = landmarks("subject",(100,100), a=(20,10), b=(20,40), left=(10,20), right=(40,24))
    m = cross_section(s,axis=("a","b"),edges=("left","right"))
    assert m.value["transverse_width"] == 30
    assert m.value["longitudinal_offset"] == 4
    assert m.value["edge_distance"] == pytest.approx(math.hypot(30,4))


def test_negative_space_winding_shift_and_non_simple_polygon():
    ref = landmarks("subject",(100,100), a=(10,10), b=(30,10), c=(30,30), d=(10,30))
    draw = landmarks("canvas",(200,200), a=(22,20), b=(62,20), c=(62,60), d=(22,60))
    reg = Registration((100,100),(200,200),scale=(2,2))
    for order in (("a","b","c","d"),("d","c","b","a")):
        m = compare_negative_space(ref,draw,registration=reg,boundary=order)
        assert m.value["reference"]["area"] == 1600
        assert m.value["relative_area_delta"] == 0
        assert m.value["centroid_delta"] == [2,0]
        assert [v["distance"] for v in m.value["vertex_errors"]] == [2]*4
    with pytest.raises(ValueError,match="simple"):
        compare_negative_space(ref,draw,registration=reg,boundary=("a","c","b","d"))


def test_occlusion_never_measures_hidden_interval():
    s = landmarks("subject",(100,100),a=(10,10),b=(20,10),c=(40,10),d=(40,20))
    m = occlusion_relation(s,foreground="sleeve",hidden_form="arm",
                           entry_segment=("a","b"),reappearance_segment=("c","d"),
                           evidence="visible boundaries on each side")
    assert m.value["entry_anchor"] == [20,10]
    assert m.value["reappearance_anchor"] == [40,10]
    assert m.value["visible_direction_delta_degrees"] == 90
    assert m.value["hidden_geometry"] == "UNMEASURED"
    assert occlusion_relation(s,foreground="sleeve",hidden_form="arm",
                             entry_segment=("a","b"),evidence="one visible side").value["reappearance_anchor"] is None


def test_session_inspection_accepts_measurement_and_does_not_mutate_strokes(tmp_path):
    ref = tmp_path/"reference.png"
    Image.new("RGB",(32,32),"white").save(ref)
    session = DrawingSession.create(subject=ref,output_dir=tmp_path/"run")
    session.draw([(2,2),(20,20)],part="line")
    before = (session.history_cursor,session.drawing_state_hash())
    a = landmarks("subject",(32,32),p=(2,2),q=(20,20))
    b = landmarks("canvas",(32,32),p=(2,2),q=(20,20))
    m = compare_landmarks(a,b,registration=Registration.identity((32,32)),labels=("p","q"),normalizer=("p","q"))
    session.observe(a.to_dict())
    session.inspect(measurements=(m,), supersample=2,
                    escalation_reason="check the declared visible landmark discrepancy")
    assert (session.history_cursor,session.drawing_state_hash()) == before
    assert "img2drawing.observation.compare_landmarks" in runtime_capabilities().observation_helpers
