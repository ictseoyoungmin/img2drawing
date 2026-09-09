from __future__ import annotations

import hashlib
import os
import struct
import time
import zlib
from pathlib import Path

from PIL import Image
from ...render.pillow_pencil_contact import _prepare_grade, _smooth_hand_dynamics
from .patch_cache import PatchCacheRenderer

MAGIC=b"IPC1"
CACHE_HEAD=struct.Struct("<4siiIIII32s")  # magic,x,y,w,h,raw_len,comp_len,raw_sha256


class PersistentPatchCacheRenderer(PatchCacheRenderer):
    """Lossless, versioned, corruption-safe cross-run extension of the local patch cache."""

    def __init__(self, *, persistent_cache_dir: Path, **kwargs):
        super().__init__(**kwargs)
        self.persistent_cache_dir=Path(persistent_cache_dir); self.persistent_cache_dir.mkdir(parents=True,exist_ok=True)
        self.persistent={"disk_hits":0,"disk_misses":0,"disk_corrupt":0,"read_sec":0.0,"write_sec":0.0,
                         "bytes_read":0,"bytes_written":0}

    def _cache_path(self,key:str)->Path:
        return self.persistent_cache_dir/key[:2]/f"{key}.pcz"

    def _read_disk_patch(self,key:str):
        path=self._cache_path(key)
        if not path.exists():
            self.persistent["disk_misses"]+=1; return None
        t0=time.perf_counter()
        try:
            data=path.read_bytes()
            if len(data)<CACHE_HEAD.size: raise ValueError("short cache")
            magic,x,y,w,h,raw_len,comp_len,digest=CACHE_HEAD.unpack_from(data,0)
            if magic!=MAGIC or w<=0 or h<=0 or raw_len!=w*h*4: raise ValueError("bad cache header")
            comp=data[CACHE_HEAD.size:CACHE_HEAD.size+comp_len]
            if len(comp)!=comp_len: raise ValueError("truncated cache")
            raw=zlib.decompress(comp)
            if len(raw)!=raw_len or hashlib.sha256(raw).digest()!=digest: raise ValueError("cache checksum mismatch")
            layer=Image.frombytes("RGBA",(w,h),raw)
            self.persistent["disk_hits"]+=1; self.persistent["bytes_read"]+=len(data)
            return ((x,y),layer,False)
        except Exception:
            self.persistent["disk_corrupt"]+=1
            return None
        finally:
            self.persistent["read_sec"]+=time.perf_counter()-t0

    def _write_disk_patch(self,key:str,patch)->None:
        (x,y),layer,_=patch; path=self._cache_path(key); path.parent.mkdir(parents=True,exist_ok=True)
        raw=layer.tobytes(); comp=zlib.compress(raw,1)
        blob=CACHE_HEAD.pack(MAGIC,int(x),int(y),layer.width,layer.height,len(raw),len(comp),hashlib.sha256(raw).digest())+comp
        tmp=path.with_name(path.name+f".{os.getpid()}.tmp")
        t0=time.perf_counter()
        try:
            tmp.write_bytes(blob); os.replace(tmp,path); self.persistent["bytes_written"]+=len(blob)
        finally:
            if tmp.exists():
                try: tmp.unlink()
                except OSError: pass
            self.persistent["write_sec"]+=time.perf_counter()-t0

    def patch_for(self,stroke):
        prepared=_smooth_hand_dynamics(_prepare_grade(stroke,self.grade),self.profile)
        key=self._fingerprint(prepared)
        hit=self.patch_cache.get(key)
        if hit is not None:
            self.stats["cache_hits"]+=1; return hit
        disk=self._read_disk_patch(key)
        if disk is not None:
            self.patch_cache[key]=disk; self.stats["cache_hits"]+=1; return disk
        t0=time.perf_counter(); patch=self._build_patch(prepared); self.stats["patch_build_wall_sec"]+=time.perf_counter()-t0
        self.patch_cache[key]=patch; self.stats["cache_misses"]+=1; self._write_disk_patch(key,patch); return patch
