from __future__ import annotations

"""S06 dev prototype: edit-aware dirty-region compositor.

Extends the S04 persistent supersampled canvas beyond append-only histories.
For replace/delete/soft-lift style edits, the affected high-resolution region is
rebuilt from the authoritative current active stroke set in layer order using
S02/S03 cached exact material masks, then only the influenced native-resolution
patch is Lanczos-resampled.

This remains a dev benchmark prototype and does not modify production runtime.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
import math

from PIL import Image

from img2drawing.core.ir import Stroke, StrokeIR
from img2drawing.render import pillow_eraser_material as p7
from img2drawing.render import pillow_graphite_grain as p3
from img2drawing.render import pillow_paper_interaction as p5
from img2drawing.render import pillow_pencil_contact as pc

from cached_pencil_renderer import CachedStrokeRaster, StrokeRasterCache


Box = tuple[int, int, int, int]


def _intersects(a: Box, b: Box) -> bool:
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]


def _union(a: Box, b: Box) -> Box:
    return (min(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3]))


def _touches_or_overlaps(a: Box, b: Box, *, gap: int = 0) -> bool:
    return not (
        a[2] + gap < b[0] or b[2] + gap < a[0] or
        a[3] + gap < b[1] or b[3] + gap < a[1]
    )


def merge_boxes(boxes: Iterable[Box], *, gap: int = 0) -> list[Box]:
    pending = [tuple(map(int, b)) for b in boxes if b[2] > b[0] and b[3] > b[1]]
    out: list[Box] = []
    while pending:
        current = pending.pop()
        changed = True
        while changed:
            changed = False
            rest: list[Box] = []
            for other in pending:
                if _touches_or_overlaps(current, other, gap=gap):
                    current = _union(current, other)
                    changed = True
                else:
                    rest.append(other)
            pending = rest
        out.append(current)
    return sorted(out)


@dataclass(frozen=True)
class EditAwareStats:
    advances: int
    append_strokes: int
    changed_strokes: int
    removed_strokes: int
    rebuilt_regions: int
    recomposited_strokes: int
    snapshots: int


class EditAwareIncrementalPencilCanvas:
    """Persistent exact graphite compositor supporting non-eraser history edits.

    The current implementation supports any sampled IR transition expressible as
    additions, removals, or content changes of ordinary graphite strokes. Explicit
    eraser-tool strokes remain unsupported because they are destructive ordered
    operations rather than independently compositable source-over layers.
    """

    def __init__(
        self,
        initial_ir: StrokeIR,
        cache: StrokeRasterCache,
        background=(255, 255, 255, 255),
        *,
        scale: int = 1,
        supersample: int = pc.DEFAULT_SUPERSAMPLE,
        graphite=(36, 34, 32),
        grade: str | None = None,
        contact_profile: str | Path | None = None,
    ) -> None:
        if int(scale) != scale or scale < 1:
            raise ValueError("scale must be a positive integer")
        if int(supersample) != supersample or supersample < 2:
            raise ValueError("supersample must be an integer >= 2")
        if grade is not None:
            pc.p6.get_grade(grade)
        self.profile = pc.load_pencil_contact_profile(contact_profile)
        self.scale = int(scale)
        self.supersample = int(supersample)
        self.factor = float(self.scale * self.supersample)
        self.hi_size = (int(initial_ir.width * self.factor), int(initial_ir.height * self.factor))
        self.out_size = (int(initial_ir.width * self.scale), int(initial_ir.height * self.scale))
        self.background = tuple(background)
        self.graphite_rgb = (int(graphite[0]), int(graphite[1]), int(graphite[2]))
        self.grade = grade
        self.contact_profile = contact_profile
        self.tooth, self.paper_scale, self.paper_seed = p5._paper_settings(initial_ir)
        self.cache = cache
        self.graphite_canvas = Image.new("RGBA", self.hi_size, (*self.graphite_rgb, 0))
        self.output_canvas = Image.new("RGBA", self.out_size, self.background)
        self._width = initial_ir.width
        self._height = initial_ir.height
        self._strokes: dict[str, Stroke] = {}
        self._items: dict[str, CachedStrokeRaster] = {}
        self._order: list[str] = []
        self._dirty_hi_regions: list[Box] = []
        self.dirty_output_pixels = 0
        self._advances = 0
        self._append_strokes = 0
        self._changed_strokes = 0
        self._removed_strokes = 0
        self._rebuilt_regions = 0
        self._recomposited_strokes = 0
        self._snapshots = 0

    def _materialize(self, stroke: Stroke) -> CachedStrokeRaster:
        if p7.is_eraser(stroke):
            raise ValueError("S06 edit-aware prototype does not support eraser-tool strokes")
        return self.cache.get_or_materialize(
            stroke,
            factor=self.factor,
            hi_size=self.hi_size,
            tooth=self.tooth,
            paper_scale=self.paper_scale,
            paper_seed=self.paper_seed,
            graphite=self.graphite_rgb,
            grade=self.grade,
            contact_profile=self.contact_profile,
            profile=self.profile,
        )

    def _composite_item(self, item: CachedStrokeRaster) -> None:
        layer = p3._graphite_layer(item.mask.size, item.mask, graphite=self.graphite_rgb)
        self.graphite_canvas.alpha_composite(layer, dest=(item.bounds[0], item.bounds[1]))
        layer.close()

    def _rebuild_region(self, box: Box) -> None:
        x0, y0, x1, y1 = box
        patch = Image.new("RGBA", (x1 - x0, y1 - y0), (*self.graphite_rgb, 0))
        count = 0
        for sid in self._order:
            item = self._items.get(sid)
            if item is None or not _intersects(item.bounds, box):
                continue
            ix0 = max(x0, item.bounds[0]); iy0 = max(y0, item.bounds[1])
            ix1 = min(x1, item.bounds[2]); iy1 = min(y1, item.bounds[3])
            mask_crop = item.mask.crop((ix0 - item.bounds[0], iy0 - item.bounds[1], ix1 - item.bounds[0], iy1 - item.bounds[1]))
            layer = p3._graphite_layer(mask_crop.size, mask_crop, graphite=self.graphite_rgb)
            patch.alpha_composite(layer, dest=(ix0 - x0, iy0 - y0))
            mask_crop.close(); layer.close()
            count += 1
        self.graphite_canvas.paste(patch, (x0, y0))
        patch.close()
        self._rebuilt_regions += 1
        self._recomposited_strokes += count

    @staticmethod
    def _ordered(ir: StrokeIR) -> list[Stroke]:
        return sorted(ir.strokes, key=lambda z: z.layer)

    def advance_to(self, ir: StrokeIR, *, merge_gap_hi: int = 0) -> dict:
        if ir.width != self._width or ir.height != self._height:
            raise ValueError("canvas dimensions changed during incremental replay")
        tooth, paper_scale, paper_seed = p5._paper_settings(ir)
        if (tooth, paper_scale, paper_seed) != (self.tooth, self.paper_scale, self.paper_seed):
            raise ValueError("paper settings changed during incremental replay")

        ordered = self._ordered(ir)
        if any(p7.is_eraser(s) for s in ordered):
            raise ValueError("S06 edit-aware prototype does not support eraser-tool strokes")
        new_order = [str(s.stroke_id) for s in ordered]
        if any(sid == "None" for sid in new_order):
            raise ValueError("all strokes must have stable stroke_id")
        new_strokes = {str(s.stroke_id): s for s in ordered}

        if not self._order:
            dirty: list[Box] = []
            for stroke in ordered:
                sid = str(stroke.stroke_id)
                item = self._materialize(stroke)
                self._strokes[sid] = stroke
                self._items[sid] = item
                self._order.append(sid)
                self._composite_item(item)
                dirty.append(item.bounds)
                self._append_strokes += 1
            self._dirty_hi_regions = merge_boxes(dirty, gap=merge_gap_hi)
            self._advances += 1
            return {"added": len(ordered), "changed": 0, "removed": 0, "regions": len(self._dirty_hi_regions)}

        prefix_same = new_order[:len(self._order)] == self._order and len(new_order) >= len(self._order)
        if prefix_same:
            prefix_objects_same = all(
                self._strokes[sid] is new_strokes[sid] or self._strokes[sid] == new_strokes[sid]
                for sid in self._order
            )
        else:
            prefix_objects_same = False
        if prefix_same and prefix_objects_same:
            new_tail = ordered[len(self._order):]
            dirty = []
            for stroke in new_tail:
                sid = str(stroke.stroke_id)
                item = self._materialize(stroke)
                self._strokes[sid] = stroke
                self._items[sid] = item
                self._order.append(sid)
                self._composite_item(item)
                dirty.append(item.bounds)
                self._append_strokes += 1
            self._dirty_hi_regions = merge_boxes(dirty, gap=merge_gap_hi)
            self._advances += 1
            return {"added": len(new_tail), "changed": 0, "removed": 0, "regions": len(self._dirty_hi_regions)}

        old_ids = set(self._strokes)
        new_ids = set(new_strokes)
        removed = old_ids - new_ids
        added = new_ids - old_ids
        common = old_ids & new_ids
        changed = {
            sid for sid in common
            if not (self._strokes[sid] is new_strokes[sid] or self._strokes[sid] == new_strokes[sid])
        }

        dirty: list[Box] = []
        for sid in removed | changed:
            old_item = self._items.get(sid)
            if old_item is None:
                old_item = self._materialize(self._strokes[sid])
            dirty.append(old_item.bounds)

        next_items: dict[str, CachedStrokeRaster] = {}
        for stroke in ordered:
            sid = str(stroke.stroke_id)
            if sid in added or sid in changed:
                item = self._materialize(stroke)
                next_items[sid] = item
                dirty.append(item.bounds)
            else:
                next_items[sid] = self._items[sid]

        self._strokes = new_strokes
        self._items = next_items
        self._order = new_order

        regions = merge_boxes(dirty, gap=merge_gap_hi)
        for region in regions:
            self._rebuild_region(region)
        self._dirty_hi_regions = regions
        self._changed_strokes += len(changed)
        self._removed_strokes += len(removed)
        self._append_strokes += len(added)
        self._advances += 1
        return {"added": len(added), "changed": len(changed), "removed": len(removed), "regions": len(regions)}

    def _update_output_region(self, hi_box: Box, *, influence_halo: int = 4, sample_halo: int = 4) -> Box:
        hx0, hy0, hx1, hy1 = hi_box
        f = self.factor
        tx0 = max(0, int(math.floor(hx0 / f)) - influence_halo)
        ty0 = max(0, int(math.floor(hy0 / f)) - influence_halo)
        tx1 = min(self.out_size[0], int(math.ceil(hx1 / f)) + influence_halo)
        ty1 = min(self.out_size[1], int(math.ceil(hy1 / f)) + influence_halo)
        ox0 = max(0, tx0 - sample_halo); oy0 = max(0, ty0 - sample_halo)
        ox1 = min(self.out_size[0], tx1 + sample_halo); oy1 = min(self.out_size[1], ty1 + sample_halo)
        src_box = (
            int(round(ox0 * f)), int(round(oy0 * f)),
            int(round(ox1 * f)), int(round(oy1 * f)),
        )
        graphite_patch = self.graphite_canvas.crop(src_box)
        base = Image.new("RGBA", graphite_patch.size, self.background)
        base.alpha_composite(graphite_patch)
        outer = base.resize((ox1 - ox0, oy1 - oy0), Image.Resampling.LANCZOS)
        inner = outer.crop((tx0 - ox0, ty0 - oy0, tx1 - ox0, ty1 - oy0))
        self.output_canvas.paste(inner, (tx0, ty0))
        self.dirty_output_pixels += (tx1 - tx0) * (ty1 - ty0)
        graphite_patch.close(); base.close(); outer.close(); inner.close()
        return (tx0, ty0, tx1, ty1)

    def snapshot_dirty(self, path: str | Path | None = None) -> list[Box]:
        out_boxes: list[Box] = []
        for region in self._dirty_hi_regions:
            out_boxes.append(self._update_output_region(region))
        if path is not None:
            p = str(path)
            if p.lower().endswith((".jpg", ".jpeg")):
                rgb = self.output_canvas.convert("RGB")
                rgb.save(p, quality=95)
                rgb.close()
            else:
                self.output_canvas.save(p)
        self._snapshots += 1
        self._dirty_hi_regions = []
        return out_boxes

    def snapshot_image(self) -> Image.Image:
        self.snapshot_dirty(None)
        return self.output_canvas.copy()

    @property
    def stats(self) -> EditAwareStats:
        return EditAwareStats(
            advances=self._advances,
            append_strokes=self._append_strokes,
            changed_strokes=self._changed_strokes,
            removed_strokes=self._removed_strokes,
            rebuilt_regions=self._rebuilt_regions,
            recomposited_strokes=self._recomposited_strokes,
            snapshots=self._snapshots,
        )

    @property
    def canvas_bytes_estimate(self) -> int:
        return int(self.hi_size[0] * self.hi_size[1] * 4)

    def close(self) -> None:
        self.graphite_canvas.close()
        self.output_canvas.close()
