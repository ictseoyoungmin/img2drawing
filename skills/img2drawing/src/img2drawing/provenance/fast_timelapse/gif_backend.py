from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import time
from pathlib import Path

from .delta_pack import read_info
from .delta_stream import iter_rgb_views

ENCODER_SCHEMA="img2drawing.local.ffmpeg-rectangle-gif.v1"


def sha256_file(path:Path)->str:
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda:f.read(1<<20),b""): h.update(block)
    return h.hexdigest()


def _feed(proc,pack:Path):
    assert proc.stdin is not None
    try:
        for view in iter_rgb_views(pack): proc.stdin.write(view)
    finally:
        proc.stdin.close()
    return proc.wait()


def _palette_key(pack_hash:str)->str:
    return hashlib.sha256(f"{ENCODER_SCHEMA}|{pack_hash}|palettegen=stats_mode=diff".encode()).hexdigest()


def encode_gif(pack:Path,out_dir:Path,fps:int=12,*,palette_cache_dir:Path|None=None,rectangle:bool=True):
    pack=Path(pack); out_dir=Path(out_dir); out_dir.mkdir(parents=True,exist_ok=True)
    info=read_info(pack); w,h=info.width,info.height; palette=out_dir/"palette.png"; gif=out_dir/"timelapse.gif"
    pack_hash=sha256_file(pack); key=_palette_key(pack_hash); cache_hit=False
    cache_palette=None if palette_cache_dir is None else Path(palette_cache_dir)/f"{key}.png"
    if cache_palette is not None: cache_palette.parent.mkdir(parents=True,exist_ok=True)
    if cache_palette is not None and cache_palette.exists():
        t0=time.perf_counter(); shutil.copy2(cache_palette,palette); palette_sec=time.perf_counter()-t0; cache_hit=True
    else:
        t0=time.perf_counter()
        p=subprocess.Popen(["ffmpeg","-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{w}x{h}","-r",str(fps),"-i","-","-vf","palettegen=stats_mode=diff",str(palette)],stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        rc=_feed(p,pack); palette_sec=time.perf_counter()-t0
        if rc!=0: raise RuntimeError(f"palettegen failed {rc}")
        if cache_palette is not None:
            tmp=cache_palette.with_name(cache_palette.name+f".{os.getpid()}.tmp"); shutil.copy2(palette,tmp); os.replace(tmp,cache_palette)
    filt="[0:v][1:v]paletteuse=dither=bayer:diff_mode=rectangle" if rectangle else "[0:v][1:v]paletteuse=dither=bayer"
    t1=time.perf_counter()
    p2=subprocess.Popen(["ffmpeg","-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{w}x{h}","-r",str(fps),"-i","-","-i",str(palette),"-filter_complex",filt,"-loop","0",str(gif)],stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    rc=_feed(p2,pack); encode_sec=time.perf_counter()-t1
    if rc!=0: raise RuntimeError(f"gif encode failed {rc}")
    return {"gif":str(gif),"gif_sha256":sha256_file(gif),"palette":str(palette),"palette_cache_hit":cache_hit,
            "palette_sec":palette_sec,"gif_encode_sec":encode_sec,"total_encode_sec":palette_sec+encode_sec,
            "pack_sha256":pack_hash,"palette_key":key,"rectangle":bool(rectangle)}
