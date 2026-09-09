from __future__ import annotations

import os
import struct
import zlib
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, Sequence

from PIL import Image

MAGIC = b"IDP1"
HEADER = struct.Struct("<4sIIII")  # magic,w,h,frames,tile
FRAME_HEAD = struct.Struct("<H")
PATCH_HEAD = struct.Struct("<HHHHII")  # x,y,w,h,raw_len,comp_len


@dataclass(frozen=True)
class PackInfo:
    width: int
    height: int
    frame_count: int
    tile_size: int
    patches_total: int
    raw_patch_bytes: int
    compressed_patch_bytes: int


def _normalize_rects(rects: Sequence[tuple[int,int,int,int]], width: int, height: int):
    out=[]
    for x0,y0,x1,y1 in rects:
        x0=max(0,min(width,int(x0))); y0=max(0,min(height,int(y0)))
        x1=max(0,min(width,int(x1))); y1=max(0,min(height,int(y1)))
        if x1>x0 and y1>y0:
            out.append((x0,y0,x1,y1))
    return out


class DeltaPackWriter:
    """Lossless append-only changed-rectangle frame pack used as disposable staging."""

    def __init__(self, path: Path, *, width: int, height: int, frame_count: int,
                 tile_size: int = 0, level: int = 1):
        self.path=Path(path); self.width=int(width); self.height=int(height)
        self.frame_count=int(frame_count); self.tile_size=int(tile_size); self.level=int(level)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.partial_path=self.path.with_name(self.path.name + ".partial")
        # A delta pack is disposable staging. Any stale partial from an interrupted
        # previous attempt is never trusted and is replaced from source-of-truth state.
        self.partial_path.unlink(missing_ok=True)
        self.fp=self.partial_path.open("wb")
        self.fp.write(HEADER.pack(MAGIC,self.width,self.height,self.frame_count,self.tile_size))
        self.frames_written=0; self.patches_total=0; self.raw_patch_bytes=0; self.compressed_patch_bytes=0
        self._committed=False

    def write_frame(self, canvas: Image.Image, rects: Sequence[tuple[int,int,int,int]]) -> None:
        if self.frames_written >= self.frame_count:
            raise ValueError("too many frames")
        normalized=_normalize_rects(rects,self.width,self.height)
        if len(normalized)>65535:
            raise ValueError("too many patches")
        self.fp.write(FRAME_HEAD.pack(len(normalized)))
        rgb=canvas if canvas.mode=="RGB" else canvas.convert("RGB")
        close_rgb=rgb is not canvas
        try:
            for x0,y0,x1,y1 in normalized:
                crop=rgb.crop((x0,y0,x1,y1)); raw=crop.tobytes(); crop.close()
                comp=zlib.compress(raw,self.level)
                self.fp.write(PATCH_HEAD.pack(x0,y0,x1-x0,y1-y0,len(raw),len(comp)))
                self.fp.write(comp)
                self.patches_total+=1; self.raw_patch_bytes+=len(raw); self.compressed_patch_bytes+=len(comp)
        finally:
            if close_rgb: rgb.close()
        self.frames_written+=1

    def close(self) -> PackInfo:
        if self._committed:
            return PackInfo(self.width,self.height,self.frame_count,self.tile_size,self.patches_total,
                            self.raw_patch_bytes,self.compressed_patch_bytes)
        if self.frames_written != self.frame_count:
            if not self.fp.closed:
                self.fp.close()
            self.partial_path.unlink(missing_ok=True)
            raise ValueError(f"frame count mismatch: wrote {self.frames_written}, expected {self.frame_count}")
        if not self.fp.closed:
            self.fp.flush(); os.fsync(self.fp.fileno()); self.fp.close()
        os.replace(self.partial_path, self.path)
        self._committed=True
        return PackInfo(self.width,self.height,self.frame_count,self.tile_size,self.patches_total,
                        self.raw_patch_bytes,self.compressed_patch_bytes)

    def abort(self) -> None:
        if not self.fp.closed:
            self.fp.close()
        self.partial_path.unlink(missing_ok=True)

    def __enter__(self): return self
    def __exit__(self, exc_type, exc, tb):
        if exc_type is None: self.close()
        else: self.abort()


def read_info(path: Path) -> PackInfo:
    with Path(path).open("rb") as f:
        raw=f.read(HEADER.size)
        if len(raw)!=HEADER.size: raise ValueError("truncated header")
        magic,w,h,n,tile=HEADER.unpack(raw)
        if magic!=MAGIC: raise ValueError("bad magic")
        patches=raw_total=comp_total=0
        for _ in range(n):
            head=f.read(FRAME_HEAD.size)
            if len(head)!=FRAME_HEAD.size: raise ValueError("truncated frame header")
            (cnt,)=FRAME_HEAD.unpack(head)
            for _ in range(cnt):
                ph=f.read(PATCH_HEAD.size)
                if len(ph)!=PATCH_HEAD.size: raise ValueError("truncated patch header")
                x,y,pw,phh,raw_len,comp_len=PATCH_HEAD.unpack(ph)
                if x+pw>w or y+phh>h: raise ValueError("patch outside canvas")
                data=f.read(comp_len)
                if len(data)!=comp_len: raise ValueError("truncated patch payload")
                patches+=1; raw_total+=raw_len; comp_total+=comp_len
        if f.read(1): raise ValueError("unexpected trailing bytes")
    return PackInfo(w,h,n,tile,patches,raw_total,comp_total)


def iter_frames(path: Path) -> Iterator[Image.Image]:
    with Path(path).open("rb") as f:
        magic,w,h,n,tile=HEADER.unpack(f.read(HEADER.size))
        if magic!=MAGIC: raise ValueError("bad magic")
        canvas=Image.new("RGB",(w,h),(255,255,255))
        try:
            for _ in range(n):
                (cnt,)=FRAME_HEAD.unpack(f.read(FRAME_HEAD.size))
                for _ in range(cnt):
                    x,y,pw,ph,raw_len,comp_len=PATCH_HEAD.unpack(f.read(PATCH_HEAD.size))
                    raw=zlib.decompress(f.read(comp_len))
                    if len(raw)!=raw_len or raw_len!=pw*ph*3: raise ValueError("corrupt patch")
                    patch=Image.frombytes("RGB",(pw,ph),raw); canvas.paste(patch,(x,y)); patch.close()
                yield canvas.copy()
        finally:
            canvas.close()
