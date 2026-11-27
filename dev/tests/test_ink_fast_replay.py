"""S06c exact mixed ink-only frame parity; graphite fallback stays conservative."""
from dataclasses import replace
import hashlib
import shutil

import pytest
from PIL import Image

from img2drawing import RenderProfile
from img2drawing.core.action import AgentDrawingSession
from img2drawing.core.material import InkAction,InkElement,MIXED_HISTORY_CONTRACT
from img2drawing.authoring import (solid_ink,fineliner,g_pen,ink_brush,dot_screentone,ToneGradient)
from img2drawing.render import render_image
from img2drawing.render.artifact import rgb_sha256
from img2drawing.inspection import drawing_state_hash
from img2drawing.timelapse import export_timelapse,sample_cursors
from img2drawing.timelapse.frames import (InkFrameSource,CanonicalFrameSource,
    open_frame_source,inspect_fast_path_eligibility)
from img2drawing.timelapse.patch_cache import InkPatchCache
from img2drawing.timelapse.delta_pack import iter_frames


def rect(x0,y0,x1,y1):
    return ((x0,y0),(x1,y0),(x1,y1),(x0,y1),(x0,y0))


def action(h,aid,sid,mark=None,kind="ink.add",layer=0):
    el=None if mark is None else InkElement(sid,mark,"value","swatch",layer)
    return h.apply_ink_action(InkAction(aid,kind,sid,el,"o","synthetic authored fixture","edit"))


def history():
    h=AgentDrawingSession(128,96,media_contract=MIXED_HISTORY_CONTRACT).history
    action(h,"a1","base",solid_ink(rect(-4,5,88,76),holes=(rect(10,15,25,30),)),layer=1)
    action(h,"a2","pen",g_pen(((8,12),(60,85),(125,17)),
        pressure_knots=((0,.2),(.5,.95),(1,.3)),max_width=7,min_width=.4).resolve(),layer=2)
    action(h,"a3","under",solid_ink(rect(4,4,45,80),paint="white"),layer=0)
    action(h,"a4","tone",dot_screentone(rect(46,4,132,88),pitch=6,
        gradient=ToneGradient((46,0),(125,0),.15,.95),angle_degrees=37,phase_origin=(.3,-.7)),layer=3)
    action(h,"a5","styled",fineliner(((8,88),(60,60),(125,88)),width=6,
        cap="square",join="miter").resolve(),layer=4)
    action(h,"a6","white",ink_brush(((20,34),(100,34)),pressure_knots=((0,1),(1,1)),
        max_width=8,paint="white").resolve(),layer=3)
    h.marker("metadata")
    action(h,"a7","tone",dot_screentone(rect(32,8,104,68),pitch=4,coverage=.6,
        angle_degrees=15,phase_origin=(.7,.3)),kind="ink.replace",layer=0)
    action(h,"a8","pen",fineliner(((16,10),(70,12),(120,15)),width=4).resolve(),kind="ink.replace",layer=5)
    action(h,"a9","base",kind="ink.delete")
    action(h,"a10","zero",dot_screentone(rect(2,2,16,16),coverage=0),layer=9)
    action(h,"a11","outside",solid_ink(rect(150,150,180,180)),layer=10)
    for i,sid in enumerate(("pen","under","tone","styled","white","zero","outside")):
        action(h,f"retire-{i}",sid,kind="ink.delete")
    return h


def canonical(h,p,cursor):
    return render_image(p.prepared_ir(h.state_at(cursor)),**p.renderer_kwargs())


@pytest.mark.parametrize("ss,scale,every_n,background",[
    (2,1,1,(255,255,255,255)),(4,1,1,(100,130,166,255)),
    (8,1,2,(255,255,255,255)),(2,2,4,(230,210,190,255)),
])
def test_ink_fast_matches_every_requested_cursor_and_dirty_regions(ss,scale,every_n,background):
    h=history()
    p=RenderProfile.mixed_media(128,96,supersample=ss,output_scale=scale,background_rgba=background)
    assert inspect_fast_path_eligibility(h).eligible
    # Tiny cache forces eviction and oversized-patch cleanup.
    source=InkFrameSource(h,p,cache_bytes=128)
    before=h.to_dict()
    previous=source.image()
    try:
        for cursor in sample_cursors(h.cursor,"every_n",every_n):
            info=source.advance_to(cursor)
            with source.image() as got,canonical(h,p,cursor) as want:
                assert got.tobytes()==want.tobytes(),(cursor,info)
                assert source.state_hash==drawing_state_hash(h.state_at(cursor))
                # Rebuild only advertised output rectangles: exact delta pack
                # reconstruction must not omit filter fringe or old geometry.
                for box in info["output_regions"]:
                    with got.crop(box) as crop:
                        previous.paste(crop,box[:2])
                assert previous.tobytes()==got.tobytes(),(cursor,info)
        assert source.stats["actions_applied"]==h.cursor
        assert source.renderer.stats["peak_cache_bytes"]<=128
        assert source.renderer.stats["oversize_uncached"]>0
        assert h.to_dict()==before
    finally:
        previous.close()
        source.close()
    assert source.renderer.stats["cache_bytes"]==0


def test_append_layer_reorder_delete_and_cache_reuse():
    h=history()
    p=RenderProfile.mixed_media(128,96,supersample=2)
    source=open_frame_source(h,p)
    assert isinstance(source,InkFrameSource)
    try:
        assert source.advance_to(1)["mode"]=="append"
        assert source.advance_to(2)["mode"]=="append"
        assert source.advance_to(3)["mode"]=="dirty"
        source.advance_to(6)
        assert source.advance_to(7)["mode"]=="metadata-only"
        source.advance_to(h.cursor)
        assert source.stats["dirty_advances"]>0
        assert source.renderer.stats["cache_hits"]>0
        assert source.renderer.persistent["bytes_written"]==0
        assert source.renderer.stats["peak_cache_bytes"]<=32*1024*1024
    finally:
        source.close()


@pytest.mark.parametrize("size,points", [
    ((128,192),((24,8),(40,184))),
    ((96,256),((8,100),(88,116))),
])
def test_narrow_ink_dirty_resample_matches_full_page(size,points):
    # A tall crop on a wider page, or a wide crop on a tall page, can choose
    # a different separable-filter pass order in Pillow. Geometry is synthetic.
    h=AgentDrawingSession(*size,media_contract=MIXED_HISTORY_CONTRACT).history
    action(h,"line-add","line",fineliner(points,width=1.3).resolve())
    p=RenderProfile.mixed_media(*size,supersample=2)
    src=InkFrameSource(h,p)
    previous=src.image()
    try:
        info=src.advance_to(1)
        assert info["mode"]=="append"
        assert info["output_regions"]!=[(0,0,*size)]
        with src.image() as got,canonical(h,p,1) as want:
            assert got.tobytes()==want.tobytes()
            for box in info["output_regions"]:
                with got.crop(box) as crop:
                    previous.paste(crop,box[:2])
            assert previous.tobytes()==want.tobytes()
    finally:
        previous.close()
        src.close()


def test_cache_isolation_and_eviction():
    mark=solid_ink(rect(1,1,11,11))
    p=RenderProfile.mixed_media(128,96,supersample=2)
    a=InkPatchCache(p,max_bytes=80)
    b=InkPatchCache(replace(p,background_rgba=(200,200,200,255)))
    c=InkPatchCache(p,supersample=4)
    try:
        key=a.key(mark)
        assert key!=b.key(mark) and key!=c.key(mark)
        assert key!=a.key(replace(mark,paint="white"))
        with pytest.raises(ValueError,match="another profile"):
            with b.patch(mark,key=key):
                pass
        with pytest.raises(ValueError,match="does not match mark"):
            with a.patch(replace(mark,paint="white"),key=key):
                pass
        with a.patch(mark) as (box,patch):
            raw=patch.tobytes()
        with a.patch(mark) as (_,patch):
            assert patch.tobytes()==raw
        with a.patch(replace(mark,paint="white")):
            pass
        assert a.stats["evictions"]==1
        with a.patch(mark) as (_,patch):
            assert patch.tobytes()==raw
        assert a.stats["peak_cache_bytes"]<=80
    finally:
        for cache in (a,b,c):
            cache.close()


def test_ink_source_rejects_changed_history_and_wrong_profile():
    h=history()
    p=RenderProfile.mixed_media(128,96,supersample=2)
    src=InkFrameSource(h,p)
    try:
        h.undo()
        with pytest.raises(ValueError,match="history changed"):
            src.advance_to(1)
    finally:
        src.close()
    h.redo()
    src=InkFrameSource(h,p)
    try:
        h.metadata["new-evidence"]="changed"
        with pytest.raises(ValueError,match="history changed"):
            src.advance_to(1)
    finally:
        src.close()
    h.metadata.pop("new-evidence")
    old=RenderProfile.mixed_media(128,96,supersample=2,screentones=False)
    src=InkFrameSource(h,old)
    try:
        with pytest.raises(ValueError,match="screentone requires"):
            src.advance_to(4)
        with pytest.raises(RuntimeError,match="failed"):
            src.image()
    finally:
        src.close()


def test_mixed_budget_enforced_on_cached_current_patches(monkeypatch):
    from img2drawing.render.contract import RendererContract
    h=history()
    p=RenderProfile.mixed_media(128,96,supersample=2)
    src=InkFrameSource(h,p)
    original=RendererContract.value
    def bounded(self,key):
        if key=="max_composite_work":
            return 128*96*4
        return original(self,key)
    monkeypatch.setattr(RendererContract,"value",bounded)
    try:
        with pytest.raises(ValueError,match="composite work budget"):
            src.advance_to(1)
    finally:
        src.close()


def test_transparent_and_graphite_actions_fail_closed(tmp_path):
    from img2drawing.core.ir import Stroke
    h=history()
    p=RenderProfile.mixed_media(128,96,supersample=2,background_rgba=(0,0,0,0))
    src=open_frame_source(h,p)
    assert isinstance(src,CanonicalFrameSource)
    src.close()
    with pytest.raises(ValueError,match="transparent background"):
        export_timelapse(h,p,tmp_path/"transparent",session_id="t",backend="fast")
    # Even a graphite mark retired before the final cursor is relevant to
    # earlier frames. Never classify based on the final IR alone.
    from img2drawing.core.tools import get_tool
    h.add_stroke(Stroke(points=[(2,2),(10,10)],stroke_id="g",width=2))
    h.hard_delete("g",get_tool("hard_eraser"))
    p=RenderProfile.mixed_media(128,96,supersample=2)
    assert not inspect_fast_path_eligibility(h).eligible
    with pytest.raises(ValueError,match="graphite/eraser"):
        export_timelapse(h,p,tmp_path/"graphite",session_id="g",backend="fast")
    assert isinstance(open_frame_source(h,p),CanonicalFrameSource)


@pytest.mark.skipif(shutil.which("ffmpeg") is None,reason="ffmpeg unavailable")
@pytest.mark.parametrize("every_n",[2,4])
def test_ink_fast_export_lossless_pack_and_independent_final(tmp_path,every_n):
    h=history()
    p=RenderProfile.mixed_media(128,96,supersample=2)
    # Leave a nonempty final state to exercise palette fidelity, rather than
    # verify only the blank all-retired state.
    h.undo(7)
    before=h.to_dict()
    out=tmp_path/"fast"
    result=export_timelapse(h,p,out,session_id="ink",every_n=every_n,backend="auto")
    m=result.manifest
    assert m["backend"]["selected"]=="fast"
    assert m["fast"]["engine"]=="ink-only-exact-delta-pack-v1"
    assert m["fast"]["persistent_patch_cache"]["bytes_written"]==0
    assert m["final"]["last_frame_pixel_match"] and m["gif"]["within_tolerance"]
    assert [f["cursor"] for f in m["frames"]]==sample_cursors(h.cursor,"every_n",every_n)
    assert not (out/"frames").exists()
    for rec,decoded in zip(m["frames"],iter_frames(out/"frames.idp"),strict=True):
        with decoded,canonical(h,p,rec["cursor"]) as want:
            assert rgb_sha256(decoded)==rgb_sha256(want)==rec["pixel_sha256"]
            assert rec["drawing_state_hash"]==drawing_state_hash(h.state_at(rec["cursor"]))
    assert h.to_dict()==before


@pytest.mark.parametrize("kind",["area","white","tone","zero","outside","styled","path"])
def test_compact_cache_native_roundtrip_and_bounds(kind):
    from img2drawing.render.ink import build_ink_patch
    p=RenderProfile.mixed_media(128,96,supersample=2)
    ring=rect(3.2,5.1,48.6,60.2)
    mark={
        "area":solid_ink(ring,holes=(rect(10,10,18,18),)),
        "white":solid_ink(ring,paint="white"),
        "tone":dot_screentone(ring,pitch=6,coverage=.44,angle_degrees=19),
        "zero":dot_screentone(ring,coverage=0),
        "outside":solid_ink(rect(160,160,180,180),paint="white"),
        "styled":fineliner(((4,8),(28,17),(50,7)),width=3,join="miter",cap="square").resolve(),
        "path":g_pen(((3,5),(50,30)),pressure_knots=((0,.2),(1,1)),min_width=.4,max_width=6).resolve(),
    }[kind]
    cache=InkPatchCache(p)
    try:
        bounds,native=build_ink_patch(mark,factor=2,hi_size=(256,192))
        with native:
            assert cache.bounds(mark)==bounds
            for _ in range(2):
                with cache.patch(mark) as (box,layer):
                    assert box==bounds and layer.tobytes()==native.tobytes()
            assert cache.stats["cache_misses"]==cache.stats["cache_hits"]==1
            assert cache.stats["cache_bytes"]==((native.width+7)//8)*native.height
    finally:
        cache.close()


def test_dirty_regions_borrow_each_mark_once_without_retained_pixels(monkeypatch):
    h=AgentDrawingSession(128,96,media_contract=MIXED_HISTORY_CONTRACT).history
    action(h,"a","base",solid_ink(rect(2,2,126,94)),layer=0)
    action(h,"b","left",solid_ink(rect(5,10,15,20),paint="white"),layer=1)
    action(h,"c","right",solid_ink(rect(100,70,110,80),paint="white"),layer=1)
    action(h,"d","left",kind="ink.delete")
    action(h,"e","right",kind="ink.delete")
    p=RenderProfile.mixed_media(128,96,supersample=2)
    src=InkFrameSource(h,p,cache_bytes=0)
    try:
        src.advance_to(3)
        misses=src.renderer.stats["cache_misses"]
        info=src.advance_to(5)
        assert info["regions"]==2
        assert src.renderer.stats["cache_misses"]-misses==1
        assert src.renderer.stats["cache_bytes"]==0
        with src.image() as got,canonical(h,p,5) as want:
            assert got.tobytes()==want.tobytes()
    finally:
        src.close()


def test_compact_cache_entry_limit_and_ephemeral_ownership(monkeypatch):
    p=RenderProfile.mixed_media(128,96,supersample=2)
    c=InkPatchCache(p)
    monkeypatch.setattr(c,"MAX_ENTRIES",2)
    try:
        for i in range(3):
            with c.patch(solid_ink(rect(1+i*10,1,8+i*10,8))) as (_,layer):
                assert layer.width>0
        assert len(c._entries)==2 and c.stats["evictions"]==1
        assert all(isinstance(item[3],bytes) for item in c._entries.values())
        with pytest.raises(ValueError,match="closed"):
            layer.tobytes()
    finally:
        c.close()
