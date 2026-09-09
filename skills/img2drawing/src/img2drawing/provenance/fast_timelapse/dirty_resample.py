from __future__ import annotations

from PIL import Image
from .dirty_regions import merge_regions


def finalize_full(renderer, canvas: Image.Image):
    base = Image.new("RGBA", renderer.hi_size, renderer.background)
    composited = Image.alpha_composite(base, canvas)
    base.close()
    out = composited.resize(renderer.out_size, Image.Resampling.LANCZOS)
    composited.close()
    return out


def _align_down(v: int, m: int) -> int:
    return (v // m) * m


def _align_up(v: int, m: int) -> int:
    return ((v + m - 1) // m) * m


def update_output_regions(renderer, hi_canvas: Image.Image, out_canvas: Image.Image, regions,
                          influence_px: int = 12, guard_px: int = 24):
    ratio = int(round(renderer.hi_size[0] / renderer.out_size[0]))
    if ratio < 1 or abs(renderer.hi_size[0] / renderer.out_size[0] - ratio) > 1e-9 \
            or abs(renderer.hi_size[1] / renderer.out_size[1] - ratio) > 1e-9:
        raise ValueError("dirty resample requires an integer isotropic hi/out ratio")
    influence = max(influence_px, 4 * ratio)
    targets = []
    for r in regions:
        tx0 = max(0, _align_down(int(r[0]) - influence, ratio))
        ty0 = max(0, _align_down(int(r[1]) - influence, ratio))
        tx1 = min(renderer.hi_size[0], _align_up(int(r[2]) + influence, ratio))
        ty1 = min(renderer.hi_size[1], _align_up(int(r[3]) + influence, ratio))
        if tx1 > tx0 and ty1 > ty0:
            targets.append((tx0, ty0, tx1, ty1))
    targets = merge_regions(targets)
    guard = max(guard_px, 8 * ratio)
    total_out_area = 0
    for tx0, ty0, tx1, ty1 in targets:
        sx0 = max(0, _align_down(tx0 - guard, ratio))
        sy0 = max(0, _align_down(ty0 - guard, ratio))
        sx1 = min(renderer.hi_size[0], _align_up(tx1 + guard, ratio))
        sy1 = min(renderer.hi_size[1], _align_up(ty1 + guard, ratio))
        crop = hi_canvas.crop((sx0, sy0, sx1, sy1))
        base = Image.new("RGBA", crop.size, renderer.background)
        composited = Image.alpha_composite(base, crop)
        base.close(); crop.close()
        small = composited.resize(((sx1 - sx0) // ratio, (sy1 - sy0) // ratio), Image.Resampling.LANCZOS)
        composited.close()
        cx0, cy0 = (tx0 - sx0) // ratio, (ty0 - sy0) // ratio
        cx1, cy1 = (tx1 - sx0) // ratio, (ty1 - sy0) // ratio
        interior = small.crop((cx0, cy0, cx1, cy1))
        small.close()
        out_canvas.paste(interior, (tx0 // ratio, ty0 // ratio))
        total_out_area += interior.size[0] * interior.size[1]
        interior.close()
    return targets, total_out_area
