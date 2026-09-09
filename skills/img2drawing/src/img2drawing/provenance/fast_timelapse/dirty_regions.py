from __future__ import annotations

from PIL import Image


def union_box(a, b):
    if a is None:
        return b
    if b is None:
        return a
    return (min(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3]))


def clip_box(box, size):
    return (max(0, min(size[0], box[0])), max(0, min(size[1], box[1])),
            max(0, min(size[0], box[2])), max(0, min(size[1], box[3])))


def intersects(a, b):
    return not (a[2] <= b[0] or a[0] >= b[2] or a[3] <= b[1] or a[1] >= b[3])


def patch_box(renderer, stroke):
    (x, y), layer, _ = renderer.patch_for_fast(stroke)
    return (x, y, x + layer.size[0], y + layer.size[1])


def merge_regions(regions):
    regions = [r for r in regions if r is not None and r[2] > r[0] and r[3] > r[1]]
    changed = True
    while changed:
        changed = False
        out = []
        while regions:
            a = regions.pop()
            merged = False
            for i, b in enumerate(regions):
                if intersects(a, b):
                    regions[i] = union_box(a, b)
                    merged = True
                    changed = True
                    break
            if not merged:
                out.append(a)
        regions = out
    return sorted(regions)


def apply_additions(renderer, canvas: Image.Image, strokes):
    boxes = []
    for stroke in strokes:
        (x, y), layer, _ = renderer.patch_for_fast(stroke)
        canvas.alpha_composite(layer, dest=(x, y))
        boxes.append((x, y, x + layer.size[0], y + layer.size[1]))
    return merge_regions(boxes)


def rerender_full(renderer, strokes):
    canvas = Image.new("RGBA", renderer.hi_size,
                       (renderer.graphite[0], renderer.graphite[1], renderer.graphite[2], 0))
    for stroke in sorted(strokes, key=lambda z: z.layer):
        (x, y), layer, _ = renderer.patch_for_fast(stroke)
        canvas.alpha_composite(layer, dest=(x, y))
    return canvas


def recomposite_regions(renderer, canvas: Image.Image, strokes, regions):
    count = 0
    patch_meta = []
    for stroke in sorted(strokes, key=lambda z: z.layer):
        (px, py), layer, _ = renderer.patch_for_fast(stroke)
        patch_meta.append((px, py, layer, (px, py, px + layer.size[0], py + layer.size[1])))
    for dirty in regions:
        dirty = clip_box(dirty, renderer.hi_size)
        if dirty[2] <= dirty[0] or dirty[3] <= dirty[1]:
            continue
        canvas.paste((renderer.graphite[0], renderer.graphite[1], renderer.graphite[2], 0), dirty)
        for px, py, layer, pbox in patch_meta:
            if not intersects(pbox, dirty):
                continue
            ix0, iy0 = max(pbox[0], dirty[0]), max(pbox[1], dirty[1])
            ix1, iy1 = min(pbox[2], dirty[2]), min(pbox[3], dirty[3])
            crop = layer.crop((ix0 - px, iy0 - py, ix1 - px, iy1 - py))
            canvas.alpha_composite(crop, dest=(ix0, iy0))
            crop.close()
            count += 1
    return count
