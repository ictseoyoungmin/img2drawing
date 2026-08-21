from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageChops
from .runtime import CanvasRuntime

class CanvasInspector:
    def __init__(self, runtime: CanvasRuntime):
        self.runtime=runtime
    def current(self, out: str|Path, *, supersample=3) -> Path:
        return self.runtime.render(out,supersample=supersample)
    def crop(self, source: str|Path, box, out: str|Path) -> Path:
        p=Path(out); p.parent.mkdir(parents=True,exist_ok=True)
        Image.open(source).convert("RGB").crop(tuple(map(int,box))).save(p); return p
    def difference(self, a: str|Path, b: str|Path, out: str|Path) -> Path:
        x=Image.open(a).convert("RGB"); y=Image.open(b).convert("RGB").resize(x.size,Image.Resampling.LANCZOS)
        p=Path(out); p.parent.mkdir(parents=True,exist_ok=True); ImageChops.difference(x,y).save(p); return p
