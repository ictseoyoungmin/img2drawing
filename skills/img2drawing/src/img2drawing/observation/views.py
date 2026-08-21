from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageOps

def crop_view(source: str | Path, box: tuple[int,int,int,int], out: str | Path) -> Path:
    im = Image.open(source).convert("RGB")
    p = Path(out); p.parent.mkdir(parents=True, exist_ok=True)
    im.crop(tuple(map(int, box))).save(p)
    return p

def mirror_view(source: str | Path, out: str | Path) -> Path:
    im = Image.open(source).convert("RGB")
    p = Path(out); p.parent.mkdir(parents=True, exist_ok=True)
    ImageOps.mirror(im).save(p)
    return p

def thumbnail_view(source: str | Path, out: str | Path, max_size=(512,512)) -> Path:
    im = Image.open(source).convert("RGB")
    im.thumbnail(tuple(map(int, max_size)), Image.Resampling.LANCZOS)
    p = Path(out); p.parent.mkdir(parents=True, exist_ok=True)
    im.save(p); return p
