from __future__ import annotations

import zlib
from pathlib import Path
from typing import Iterator

from .delta_pack import FRAME_HEAD, HEADER, MAGIC, PATCH_HEAD


def iter_rgb_views(path: Path) -> Iterator[memoryview]:
    """Decode IDP1 into one persistent RGB bytearray without per-frame PIL copies."""
    with Path(path).open("rb") as f:
        magic,w,h,n,_tile=HEADER.unpack(f.read(HEADER.size))
        if magic!=MAGIC: raise ValueError("bad magic")
        stride=w*3; canvas=bytearray([255])*(w*h*3); view=memoryview(canvas)
        for _ in range(n):
            (cnt,)=FRAME_HEAD.unpack(f.read(FRAME_HEAD.size))
            for _ in range(cnt):
                x,y,pw,ph,raw_len,comp_len=PATCH_HEAD.unpack(f.read(PATCH_HEAD.size))
                raw=zlib.decompress(f.read(comp_len))
                if len(raw)!=raw_len or raw_len!=pw*ph*3: raise ValueError("corrupt patch")
                rv=memoryview(raw); row_bytes=pw*3
                for row in range(ph):
                    src0=row*row_bytes; dst0=(y+row)*stride+x*3
                    view[dst0:dst0+row_bytes]=rv[src0:src0+row_bytes]
            yield view
