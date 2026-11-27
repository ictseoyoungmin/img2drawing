"""Reproducible public synthetic stress; never read a reference or private session.

Use the exact same plain geometry specification for both installed runtimes.
Solid/tone outlines in graphite are a workload control, not equal appearance.
"""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import platform
import resource
import sys
import time

import img2drawing
from img2drawing import DrawingSession, DrawingIntent, ReferenceAuthority, RenderProfile
from img2drawing.timelapse.delta_pack import iter_frames
from PIL import Image
import numpy as np


PROTOCOL_PATH = Path(__file__).with_name("protocol.json")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def spec(i):
    x, y = 18+(i%40)*50, 20+(i//40)*60
    j = (i*397)%1320
    if j<1160:
        return ("path", ((x,y+12),(x+8,y+2),(x+18,y+16),(x+27,y+5),(x+37,y+14)),
                (.22,.65,1.,.72,.27), 4.+(i%4)*.5)
    points=((x+1,y+2),(x+34,y+1),(x+39,y+27),(x+25,y+39),(x+3,y+31),(x+1,y+2))
    return ("area" if j<1260 else "tone",points,(.8,)*len(points),2.)


def run(mode,out,expected_version):
    protocol=json.loads(PROTOCOL_PATH.read_text())
    assert img2drawing.__version__==expected_version
    out.mkdir(parents=True,exist_ok=False)
    # Seal the exact committed fixture and thresholds before rendering.
    seal={"protocol_sha256":sha(PROTOCOL_PATH),"script_sha256":sha(Path(__file__)),
          "mode":mode,"version":img2drawing.__version__,"python":platform.python_version(),
          "numpy":np.__version__,"pillow":Image.__version__,"runtime_file":str(img2drawing.__file__)}
    (out/"seal.json").write_text(json.dumps(seal,indent=2))
    t0=time.perf_counter()
    cpu0=time.process_time()
    w,h=protocol["canvas"]
    ss=protocol["supersample"]
    n=protocol["adds"]
    assert (w,h,ss,n)==(2048,2048,2,1320)
    specs=[spec(i) for i in range(n)]
    counts=dict(Counter(z[0] for z in specs))
    assert counts=={"path":1160,"area":100,"tone":60}
    if mode=="ink":
        from img2drawing.authoring import (InkPath,InkElement,InkAction,solid_ink,
                                            dot_screentone,apply_ink_actions)
        profile=RenderProfile.mixed_media(w,h,supersample=ss)
        def mark(i):
            kind,pts,pr,width=specs[i]
            if kind=="path":
                return InkPath(pts,pr,.35,width,1.2)
            if kind=="area":
                return solid_ink(pts,paint="white" if i%13==0 else "black")
            return dot_screentone(pts,pitch=6+(i%3),coverage=.2+.1*(i%7),
                                  angle_degrees=30,phase_origin=(.3,.7))
    else:
        profile=replace(RenderProfile.opacity_normalized(w,h,contact_width=True),supersample=ss)
    s=DrawingSession.create(canvas=(w,h),output_dir=out/"session",render_profile=profile,
        intent=DrawingIntent(reference_mode="imaginative",drawing_mode="free_draw",
                             finish_intent="expressive",style_profile="custom:stress"),
        reference_authority=ReferenceAuthority.imaginative(("synthetic explicit geometry performance fixture",)))
    oid=s.observe({"fixture":"synthetic local marks; no source image or quality claim"})
    def add(i):
        sid=f"m-{i:04}"
        return InkAction(f"a-{i:04}","ink.add",sid,
            InkElement(sid,mark(i),"structure","stress"),oid,"synthetic grid geometry","add")
    def draw(i):
        _,pts,pr,width=specs[i]
        return {"points":pts,"pressure":pr,"stroke_id":f"m-{i:04}",
                "action_id":f"a-{i:04}","role":"structure","part":"stress","layer":0,
                "tool":"continuous_pencil","grade":"HB",
                "tool_overrides":{"width":width,"opacity":.8,"jitter":0},"observation_id":oid}
    for start in range(0,n,128):
        ids=range(start,min(start+128,n))
        if mode=="ink":
            apply_ink_actions(s,[add(i) for i in ids])
        else:
            s.draw_many([draw(i) for i in ids])
    paths=[i for i,z in enumerate(specs) if z[0]=="path"]
    edits,deletes=paths[::31][:32],paths[7::41][:6]
    if mode=="ink":
        actions=[]
        for j,i in enumerate(edits):
            _,pts,_,_=specs[i]
            sid=f"m-{i:04}"
            changed=replace(mark(i),points=tuple((x+1.2,y+2.4) for x,y in pts))
            actions.append(InkAction(f"e-{j:02}","ink.replace",sid,
                InkElement(sid,changed,"structure","stress"),oid,"synthetic geometry","translate"))
        for j,i in enumerate(deletes):
            actions.append(InkAction(f"d-{j:02}","ink.delete",f"m-{i:04}",None,
                                     oid,"synthetic geometry","retire"))
        apply_ink_actions(s,actions)
    else:
        for j,i in enumerate(edits):
            _,pts,pr,width=specs[i]
            sid=f"m-{i:04}"
            s.replace_stroke(sid,tuple((x+1.2,y+2.4) for x,y in pts),stroke_id=sid,
                action_id=f"e-{j:02}",role="structure",part="stress",pressure=pr,
                tool="continuous_pencil",grade="HB",tool_overrides={"width":width,"opacity":.8,"jitter":0},
                reason="synthetic translate",observation_id=oid)
        for j,i in enumerate(deletes):
            s.delete_stroke(f"m-{i:04}",action_id=f"d-{j:02}",observation_id=oid,reason="synthetic retire")
    assert s.history_cursor==protocol["actions"]
    author=time.perf_counter()-t0
    t=time.perf_counter()
    revived=DrawingSession.resume(s.checkpoint())
    resume=time.perf_counter()-t
    final=revived.render_final(out/"final.png")
    assert final.drawing_state_hash==s.drawing_state_hash()
    t=time.perf_counter()
    tl=revived.export_timelapse(out/"replay",backend="fast",every_n=protocol["every_n"],
        materialize_frames=False,max_pixel_work=protocol["max_pixel_work"],
        max_gif_bytes=protocol["max_gif_bytes"])
    elapsed=time.perf_counter()-t
    m=tl.manifest
    assert m["backend"]["selected"]=="fast"
    assert m["final"]["pixel_sha256"]==final.pixel_sha256 and m["final"]["last_frame_pixel_match"]
    assert m["gif"]["within_tolerance"]
    assert len(m["frames"])==protocol["expected_frames"]
    assert m["frames"][0]["cursor"]==0 and m["frames"][-1]["cursor"]==protocol["actions"]
    with Image.open(tl.gif_path) as im:
        assert im.n_frames==protocol["expected_frames"]
    if mode=="ink":
        assert m["fast"]["patch_cache_stats"]["peak_cache_bytes"]<=protocol["max_ink_cache_bytes"]
        assert m["fast"]["persistent_patch_cache"]["bytes_written"]==0
    # Check every stored lossless delta frame, then an independent canonical subset.
    for rec,im in zip(m["frames"],iter_frames(out/"replay/frames.idp"),strict=True):
        with im:
            assert hashlib.sha256(im.convert("RGB").tobytes()).hexdigest()==rec["pixel_sha256"]
    by={r["cursor"]:r for r in m["frames"]}
    for cursor in protocol["canonical_sample_cursors"]:
        art=revived.render_at(cursor,out/"sample.png")
        with Image.open(art.path) as im:
            assert hashlib.sha256(im.convert("RGB").tobytes()).hexdigest()==by[cursor]["pixel_sha256"]
        if by[cursor]["drawing_state_hash"] is not None:
            assert art.drawing_state_hash==by[cursor]["drawing_state_hash"]
    metrics={**seal,"counts":counts,"actions":s.history_cursor,"frames":len(m["frames"]),
        "profile_digest":profile.digest(),"drawing_state_hash":final.drawing_state_hash,
        "action_log_sha256":m["history"]["action_log_sha256"],"final_pixel_sha256":final.pixel_sha256,
        "frame_rgb_hashes":[[r["cursor"],r["pixel_sha256"]] for r in m["frames"]],
        "author_sec":author,"resume_sec":resume,"export_sec":elapsed,
        "total_sec":time.perf_counter()-t0,"parent_cpu_sec":time.process_time()-cpu0,
        "parent_peak_rss_kib":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "children_peak_rss_kib":resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
        "checkpoint_bytes":s.checkpoint().stat().st_size,"gif_bytes":m["gif"]["bytes"],
        "gif_sha256":m["gif"]["sha256"],"pack_bytes":m["fast"]["pack"]["bytes"],
        "cache":m["fast"]["patch_cache_stats"],"mechanical_gate":"PASS"}
    (out/"metrics.json").write_text(json.dumps(metrics,indent=2))
    print("MIXED_STRESS_PASS",json.dumps({k:v for k,v in metrics.items() if k!="frame_rgb_hashes"}),flush=True)


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--mode",choices=("ink","graphite"),required=True)
    p.add_argument("--out",type=Path,required=True)
    p.add_argument("--expected-version",required=True)
    args=p.parse_args()
    run(args.mode,args.out,args.expected_version)
