"""Verify both persisted material contracts, not a visual quality score."""
from dataclasses import replace
from pathlib import Path
import numpy as np
import pytest
from PIL import Image
from img2drawing import DrawingSession, DrawingIntent, RenderProfile
from img2drawing.authoring import resolve_mark_for_intent
from img2drawing.render.contract import PENCIL_CONTRACT, OPACITY_NORMALIZED_CONTRACT, UnsupportedRendererError
from img2drawing.timelapse.frames import FastFrameSource, CanonicalFrameSource


def create(tmp_path, profile):
    tmp_path.mkdir(parents=True, exist_ok=True)
    reference=tmp_path/"reference.png"
    Image.new("RGB",(profile.canvas_width,profile.canvas_height),"white").save(reference)
    s=DrawingSession.create(subject=reference,output_dir=tmp_path/"run",
        intent=DrawingIntent(drawing_mode="croquis",finish_intent="subject",style_profile="graphite_academic"),
        render_profile=profile)
    oid=s.observe({"scope":"analytic explicit material fixture"})
    return s,oid,reference


def draw(s,oid,width,opacity,points,pressure):
    mark=resolve_mark_for_intent(s.intent,"value",tool_preset="broad-graphite",
                              modifiers={"width":width,"opacity":opacity,"pressure":.65})
    kwargs=mark.draw_kwargs()
    kwargs["pressure"]=pressure
    return s.draw(points,part="material_fixture",observation_id=oid,**kwargs)


def pixels(s,path):
    artifact=s.render_final(path)
    with Image.open(artifact.path) as im:
        return np.array(im.convert("RGBA"))


def test_explicit_contract_selection_and_cross_digest_rejection():
    old=RenderProfile.canonical(120,80)
    new=RenderProfile.opacity_normalized(120,80)
    assert old.renderer_version=="11" and old.renderer_contract_digest==PENCIL_CONTRACT.digest()
    assert new.renderer_version==OPACITY_NORMALIZED_CONTRACT.renderer_version
    assert new.renderer_contract_digest==OPACITY_NORMALIZED_CONTRACT.digest()
    assert new.renderer_contract_digest!=old.renderer_contract_digest
    assert new==RenderProfile.from_dict(new.to_dict())
    for profile, other in ((old,new),(new,old)):
        with pytest.raises(UnsupportedRendererError):
            RenderProfile.from_dict({**profile.to_dict(),"renderer_contract_digest":other.renderer_contract_digest})
    raw=new.to_dict();raw.pop("renderer_contract_digest")
    with pytest.raises(UnsupportedRendererError):
        RenderProfile.from_dict(raw)
    raw=old.to_dict();raw.pop("renderer_contract_digest")
    assert RenderProfile.from_dict(raw)==old


@pytest.mark.parametrize("width",[2,5,8,14,38])
def test_opacity_response_and_zero_deposit(tmp_path,width):
    p=replace(RenderProfile.opacity_normalized(160,100),supersample=2)
    s,oid,ref=create(tmp_path,p)
    blank=pixels(s,tmp_path/"blank.png")
    sid=draw(s,oid,width,.8,[(20,50),(75,50),(140,50)],[.65]*3)
    masses=[]
    prev=.8
    for i,opacity in enumerate([.8,.4,.2,.025,0]):
        if opacity!=prev:
            s.soft_lift(sid,strength=1-opacity/prev,observation_id=oid,reason="controlled attenuation")
        im=pixels(s,tmp_path/f"stroke-{i}.png")
        masses.append(float(np.maximum(blank[:,:,:3].astype(float)-im[:,:,:3],0).sum()))
        prev=opacity
    assert masses[0]>masses[1]>masses[2]>masses[3]>masses[4]==0,masses
    assert np.array_equal(blank,im)
    assert s.current_stroke(sid).points==[(20,50),(75,50),(140,50)]


@pytest.mark.parametrize("normalized",[False,True])
def test_contract_threads_through_resume_inspection_and_exact_fast_frames(tmp_path,normalized):
    factory=RenderProfile.opacity_normalized if normalized else RenderProfile.canonical
    p=replace(factory(120,100),supersample=2)
    s,oid,ref=create(tmp_path,p)
    a=draw(s,oid,22,.45,[(16,30),(40,14),(65,31),(43,55),(85,48)],[.3,.65,.8,.25,.5])
    b=draw(s,oid,7,.4,[(20,66),(80,25),(103,70)],[.3,.7,.4])
    s.soft_lift(a,strength=.6,reason="reduce mass",observation_id=oid)
    s.soft_lift_segment(b,0,1,strength=.5,feather_points=1,reason="local light",observation_id=oid)
    s.replace_segment(a,1,3,[(40,14),(65,25),(43,55)],reason="turn",observation_id=oid)
    s.delete_stroke(b,reason="retire",observation_id=oid)
    before=s.drawing_state_hash()
    final=s.render_final(tmp_path/"final.png")
    s.inspect(supersample=p.supersample)
    resume=DrawingSession.resume(s.checkpoint(),subject=ref)
    assert resume.render_profile==p and resume.drawing_state_hash()==before
    assert resume.render_final(tmp_path/"resumed.png").pixel_sha256==final.pixel_sha256
    history=resume._agent.history
    fast=FastFrameSource(history,p,persistent_cache_dir=tmp_path/"cache")
    canonical=CanonicalFrameSource(history,p)
    try:
        for cursor in range(history.cursor+1):
            fast.advance_to(cursor);canonical.advance_to(cursor)
            with fast.image() as x,canonical.image() as y:
                assert x.tobytes()==y.tobytes(),cursor
    finally:
        fast.close();canonical.close()
    assert resume.drawing_state_hash()==before


def test_cache_separates_profiles_and_same_history(tmp_path):
    p=replace(RenderProfile.canonical(120,80),supersample=2)
    s,oid,ref=create(tmp_path,p)
    draw(s,oid,30,.1,[(20,40),(100,40)],[.65,.65])
    old=s._agent.history
    new=replace(RenderProfile.opacity_normalized(120,80),supersample=2)
    a=FastFrameSource(old,p,persistent_cache_dir=tmp_path/"cache")
    b=FastFrameSource(old,new,persistent_cache_dir=tmp_path/"cache")
    try:
        a.advance_to(1);b.advance_to(1)
        with a.image() as x,b.image() as y:
            assert x.tobytes()!=y.tobytes()
        c=CanonicalFrameSource(old,new)
        try:
            c.advance_to(1)
            with b.image() as x,c.image() as y:
                assert x.tobytes()==y.tobytes()
        finally: c.close()
    finally: a.close();b.close()
