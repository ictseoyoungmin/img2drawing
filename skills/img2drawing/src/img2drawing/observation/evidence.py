from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageFilter, ImageOps

def grayscale(source: str | Path, out: str | Path) -> Path:
    im = ImageOps.grayscale(Image.open(source).convert("RGB"))
    p=Path(out); p.parent.mkdir(parents=True, exist_ok=True); im.save(p); return p

def edges(source: str | Path, out: str | Path) -> Path:
    # Evidence only: no pose/anatomy decision is made here.
    im = ImageOps.grayscale(Image.open(source).convert("RGB")).filter(ImageFilter.FIND_EDGES)
    p=Path(out); p.parent.mkdir(parents=True, exist_ok=True); im.save(p); return p
