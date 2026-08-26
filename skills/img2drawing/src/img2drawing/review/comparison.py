from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageDraw, ImageChops, ImageOps

def _fit(im: Image.Image, box: tuple[int,int]) -> Image.Image:
    out=im.copy(); out.thumbnail(box, Image.Resampling.LANCZOS); return out

def side_by_side(left: str | Path, right: str | Path, out: str | Path, *, left_label="REFERENCE", right_label="DRAWING") -> Path:
    a=Image.open(left).convert("RGB"); b=Image.open(right).convert("RGB")
    target_h=max(a.height,b.height)
    def resize_h(im):
        s=target_h/im.height
        return im.resize((max(1,round(im.width*s)),target_h),Image.Resampling.LANCZOS)
    a,b=resize_h(a),resize_h(b)
    pad=24; title=44
    canvas=Image.new("RGB",(a.width+b.width+pad*3,target_h+title+pad),(246,245,242))
    canvas.paste(a,(pad,title)); canvas.paste(b,(a.width+pad*2,title))
    d=ImageDraw.Draw(canvas)
    d.text((pad,14),left_label,fill=(30,30,30))
    d.text((a.width+pad*2,14),right_label,fill=(30,30,30))
    p=Path(out); p.parent.mkdir(parents=True,exist_ok=True); canvas.save(p); return p

def split_compare(reference: str | Path, drawing: str | Path, out: str | Path) -> Path:
    a=Image.open(reference).convert("RGB"); b=Image.open(drawing).convert("RGB").resize(a.size,Image.Resampling.LANCZOS)
    cut=a.width//2
    canvas=b.copy(); canvas.paste(a.crop((0,0,cut,a.height)),(0,0))
    ImageDraw.Draw(canvas).line((cut,0,cut,a.height),fill=(100,100,100),width=2)
    p=Path(out); p.parent.mkdir(parents=True,exist_ok=True); canvas.save(p); return p

def labeled_multi_way(items, out: str | Path, *, tile_w=430, tile_h=650) -> Path:
    """Render 2-4 labeled images without assigning semantic authority.

    Authority lives in ReferenceBundle; this function is visual layout only.
    """
    normalized=[(str(label), Path(path)) for label,path in items]
    if not 2 <= len(normalized) <= 4:
        raise ValueError("labeled_multi_way expects 2-4 items")
    ims=[Image.open(path).convert("RGB") for _,path in normalized]
    pad=18; header=62
    canvas=Image.new(
        "RGB",
        (tile_w*len(ims)+pad*(len(ims)+1), tile_h+header+pad),
        (246,245,242),
    )
    d=ImageDraw.Draw(canvas)
    for i,((label,_),im) in enumerate(zip(normalized,ims)):
        fitted=_fit(im,(tile_w-24,tile_h-24))
        x=pad+i*(tile_w+pad)
        y=header
        canvas.paste(
            fitted,
            (x+(tile_w-fitted.width)//2, y+(tile_h-fitted.height)//2),
        )
        d.text((x+8,18),label,fill=(28,28,28))
    p=Path(out); p.parent.mkdir(parents=True,exist_ok=True); canvas.save(p); return p


def crop_registered_overlay(subject_crop: str | Path, drawing_crop: str | Path, out: str | Path, *, drawing_alpha: float = 0.80) -> Path:
    """Overlay the Agent-selected drawing crop on the subject crop.

    Registration is ONLY the explicit crop correspondence supplied by the Agent.
    Runtime resizes the drawing crop to the subject crop; it does not detect
    landmarks, infer anatomy, optimize alignment, or score similarity.
    """
    subject=Image.open(subject_crop).convert('RGB')
    drawing=Image.open(drawing_crop).convert('L').resize(subject.size,Image.Resampling.LANCZOS)
    inv=ImageChops.invert(drawing)
    # White drawing background becomes transparent; dark strokes become red overlay.
    alpha=inv.point(lambda v:max(0,min(255,int(v*float(drawing_alpha)))))
    ink=Image.new('RGBA',subject.size,(220,35,35,0)); ink.putalpha(alpha)
    canvas=subject.convert('RGBA')
    canvas.alpha_composite(ink)
    p=Path(out); p.parent.mkdir(parents=True,exist_ok=True); canvas.convert('RGB').save(p); return p

def crop_registered_absdiff(subject_crop: str | Path, drawing_crop: str | Path, out: str | Path) -> Path:
    """Write an unscored pixel-difference view for explicit crop correspondence.

    This is evidence only. Photo-vs-drawing difference is not a correctness score.
    """
    subject=Image.open(subject_crop).convert('L')
    drawing=Image.open(drawing_crop).convert('L').resize(subject.size,Image.Resampling.LANCZOS)
    diff=ImageChops.difference(subject,drawing)
    canvas=ImageOps.autocontrast(diff).convert('RGB')
    p=Path(out); p.parent.mkdir(parents=True,exist_ok=True); canvas.save(p); return p
