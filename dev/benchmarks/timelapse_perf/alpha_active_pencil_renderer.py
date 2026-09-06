from __future__ import annotations

"""S07 dev prototype: exact alpha-only persistent canvas + active-only stroke material store.

This builds on S03/S05/S06 and narrows memory to what a forward timelapse actually needs:
- one 8-bit supersampled graphite-alpha canvas (RGB is fixed by the render profile),
- one exact material mask for each currently active stroke version,
- one native RGBA output canvas.

Historical replaced/deleted masks are released after their dirty region is rebuilt. The material
math and Lanczos output path remain unchanged.
"""

from dataclasses import dataclass
from pathlib import Path
import math, time

import numpy as np
from PIL import Image

from img2drawing.core.ir import Stroke, StrokeIR
from img2drawing.render import pillow_eraser_material as p7
from img2drawing.render import pillow_paper_interaction as p5
from img2drawing.render import pillow_pencil_contact as pc

from cached_pencil_renderer import CachedStrokeRaster
from material_kernel_pencil_renderer import KernelStrokeRasterCache
from edit_aware_pencil_renderer import Box, _intersects, merge_boxes


def _alpha_source_over(dst: Image.Image, src: Image.Image) -> Image.Image:
    """Exact alpha channel of Pillow source-over for same-RGB layers."""
    if dst.mode != "L" or src.mode != "L" or dst.size != src.size:
        raise ValueError("alpha_source_over expects same-size L images")
    da = np.asarray(dst, dtype=np.uint16)
    sa = np.asarray(src, dtype=np.uint16)
    out = sa + ((da * (255 - sa) + 127) // 255)
    return Image.fromarray(out.astype(np.uint8), mode="L")


@dataclass(frozen=True)
class AlphaActiveStats:
    advances: int
    append_strokes: int
    changed_strokes: int
    removed_strokes: int
    rebuilt_regions: int
    recomposited_strokes: int
    snapshots: int
    released_materials: int


class ActiveKernelMaterializer:
    """Exact S03 materializer without retaining historical versions globally."""

    def __init__(self) -> None:
        self.materialize_seconds = 0.0
        self.materializations = 0

    def materialize(
        self,
        stroke: Stroke,
        *,
        factor: float,
        hi_size: tuple[int, int],
        tooth: float,
        paper_scale: float,
        paper_seed: int,
        graphite: tuple[int, int, int],
        grade: str | None,
        contact_profile: str | Path | None,
        profile,
    ) -> CachedStrokeRaster:
        tmp = KernelStrokeRasterCache()
        t0 = time.perf_counter()
        item = tmp.get_or_materialize(
            stroke,
            factor=factor,
            hi_size=hi_size,
            tooth=tooth,
            paper_scale=paper_scale,
            paper_seed=paper_seed,
            graphite=graphite,
            grade=grade,
            contact_profile=contact_profile,
            profile=profile,
        )
        self.materialize_seconds += time.perf_counter() - t0
        self.materializations += 1
        # Transfer mask ownership to the active canvas; do not retain an historical cache entry.
        tmp._items.clear()
        return item


class AlphaActiveEditAwareCanvas:
    def __init__(
        self,
        initial_ir: StrokeIR,
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
            raise ValueError("supersample must be >= 2")
        if grade is not None:
            pc.p6.get_grade(grade)
        self.profile = pc.load_pencil_contact_profile(contact_profile)
        self.scale = int(scale)
        self.supersample = int(supersample)
        self.factor = float(self.scale * self.supersample)
        self.hi_size = (int(initial_ir.width * self.factor), int(initial_ir.height * self.factor))
        self.out_size = (int(initial_ir.width * self.scale), int(initial_ir.height * self.scale))
        self.background = tuple(background)
        self.graphite_rgb = tuple(map(int, graphite))
        self.grade = grade
        self.contact_profile = contact_profile
        self.tooth, self.paper_scale, self.paper_seed = p5._paper_settings(initial_ir)
        self.materializer = ActiveKernelMaterializer()
        self.alpha_canvas = Image.new("L", self.hi_size, 0)
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
        self._released_materials = 0
        self.peak_active_material_bytes = 0

    @staticmethod
    def _ordered(ir: StrokeIR) -> list[Stroke]:
        return sorted(ir.strokes, key=lambda z: z.layer)

    def _materialize(self, stroke: Stroke) -> CachedStrokeRaster:
        if p7.is_eraser(stroke):
            raise ValueError("S07 prototype does not support eraser-tool strokes")
        return self.materializer.materialize(
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

    def _blend_mask_at(self, mask: Image.Image, dest: tuple[int, int], target: Image.Image | None = None) -> None:
        canvas = self.alpha_canvas if target is None else target
        x, y = dest
        dst = canvas.crop((x, y, x + mask.width, y + mask.height))
        out = _alpha_source_over(dst, mask)
        canvas.paste(out, (x, y))
        dst.close()
        out.close()

    def _composite_item(self, item: CachedStrokeRaster) -> None:
        self._blend_mask_at(item.mask, (item.bounds[0], item.bounds[1]))

    def _rebuild_region(self, box: Box) -> None:
        x0, y0, x1, y1 = box
        patch = Image.new("L", (x1 - x0, y1 - y0), 0)
        count = 0
        for sid in self._order:
            item = self._items.get(sid)
            if item is None or not _intersects(item.bounds, box):
                continue
            ix0 = max(x0, item.bounds[0])
            iy0 = max(y0, item.bounds[1])
            ix1 = min(x1, item.bounds[2])
            iy1 = min(y1, item.bounds[3])
            crop = item.mask.crop(
                (ix0 - item.bounds[0], iy0 - item.bounds[1], ix1 - item.bounds[0], iy1 - item.bounds[1])
            )
            dst = patch.crop((ix0 - x0, iy0 - y0, ix1 - x0, iy1 - y0))
            out = _alpha_source_over(dst, crop)
            patch.paste(out, (ix0 - x0, iy0 - y0))
            crop.close()
            dst.close()
            out.close()
            count += 1
        self.alpha_canvas.paste(patch, (x0, y0))
        patch.close()
        self._rebuilt_regions += 1
        self._recomposited_strokes += count

    def _update_peak(self) -> None:
        value = sum(item.bytes_estimate for item in self._items.values())
        if value > self.peak_active_material_bytes:
            self.peak_active_material_bytes = value

    def advance_to(self, ir: StrokeIR, *, merge_gap_hi: int = 0) -> dict:
        if ir.width != self._width or ir.height != self._height:
            raise ValueError("canvas dimensions changed")
        if p5._paper_settings(ir) != (self.tooth, self.paper_scale, self.paper_seed):
            raise ValueError("paper settings changed")
        ordered = self._ordered(ir)
        if any(p7.is_eraser(stroke) for stroke in ordered):
            raise ValueError("eraser unsupported")
        new_order = [str(stroke.stroke_id) for stroke in ordered]
        new_strokes = {str(stroke.stroke_id): stroke for stroke in ordered}
        if any(sid == "None" for sid in new_order):
            raise ValueError("stable stroke_id required")

        prefix_same = new_order[: len(self._order)] == self._order and len(new_order) >= len(self._order)
        prefix_objects_same = prefix_same and all(
            self._strokes[sid] is new_strokes[sid] or self._strokes[sid] == new_strokes[sid]
            for sid in self._order
        )
        if prefix_same and prefix_objects_same:
            tail = ordered[len(self._order) :]
            dirty = []
            for stroke in tail:
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
            self._update_peak()
            return {"added": len(tail), "changed": 0, "removed": 0, "regions": len(self._dirty_hi_regions)}

        old_ids = set(self._strokes)
        new_ids = set(new_strokes)
        removed = old_ids - new_ids
        added = new_ids - old_ids
        common = old_ids & new_ids
        changed = {
            sid
            for sid in common
            if not (self._strokes[sid] is new_strokes[sid] or self._strokes[sid] == new_strokes[sid])
        }

        dirty = [self._items[sid].bounds for sid in removed | changed]
        next_items: dict[str, CachedStrokeRaster] = {}
        for stroke in ordered:
            sid = str(stroke.stroke_id)
            if sid in added or sid in changed:
                item = self._materialize(stroke)
                next_items[sid] = item
                dirty.append(item.bounds)
            else:
                next_items[sid] = self._items[sid]

        old_items = self._items
        self._strokes = new_strokes
        self._items = next_items
        self._order = new_order
        regions = merge_boxes(dirty, gap=merge_gap_hi)
        for region in regions:
            self._rebuild_region(region)

        for sid in removed | changed:
            old = old_items.get(sid)
            if old is not None and old is not self._items.get(sid):
                old.mask.close()
                self._released_materials += 1

        self._changed_strokes += len(changed)
        self._removed_strokes += len(removed)
        self._append_strokes += len(added)
        self._advances += 1
        self._dirty_hi_regions = regions
        self._update_peak()
        return {"added": len(added), "changed": len(changed), "removed": len(removed), "regions": len(regions)}

    def _update_output_region(self, hi_box: Box, *, influence_halo: int = 4, sample_halo: int = 4) -> Box:
        hx0, hy0, hx1, hy1 = hi_box
        f = self.factor
        tx0 = max(0, int(math.floor(hx0 / f)) - influence_halo)
        ty0 = max(0, int(math.floor(hy0 / f)) - influence_halo)
        tx1 = min(self.out_size[0], int(math.ceil(hx1 / f)) + influence_halo)
        ty1 = min(self.out_size[1], int(math.ceil(hy1 / f)) + influence_halo)
        ox0 = max(0, tx0 - sample_halo)
        oy0 = max(0, ty0 - sample_halo)
        ox1 = min(self.out_size[0], tx1 + sample_halo)
        oy1 = min(self.out_size[1], ty1 + sample_halo)
        src_box = (
            int(round(ox0 * f)),
            int(round(oy0 * f)),
            int(round(ox1 * f)),
            int(round(oy1 * f)),
        )
        alpha = self.alpha_canvas.crop(src_box)
        graphite = Image.new("RGBA", alpha.size, (*self.graphite_rgb, 0))
        graphite.putalpha(alpha)
        base = Image.new("RGBA", alpha.size, self.background)
        base.alpha_composite(graphite)
        outer = base.resize((ox1 - ox0, oy1 - oy0), Image.Resampling.LANCZOS)
        inner = outer.crop((tx0 - ox0, ty0 - oy0, tx1 - ox0, ty1 - oy0))
        self.output_canvas.paste(inner, (tx0, ty0))
        self.dirty_output_pixels += (tx1 - tx0) * (ty1 - ty0)
        alpha.close()
        graphite.close()
        base.close()
        outer.close()
        inner.close()
        return (tx0, ty0, tx1, ty1)

    def snapshot_dirty(self, path: str | Path | None = None) -> list[Box]:
        boxes = [self._update_output_region(region) for region in self._dirty_hi_regions]
        if path is not None:
            self.output_canvas.save(str(path))
        self._snapshots += 1
        self._dirty_hi_regions = []
        return boxes

    def snapshot_image(self) -> Image.Image:
        self.snapshot_dirty(None)
        return self.output_canvas.copy()

    @property
    def active_material_bytes(self) -> int:
        return sum(item.bytes_estimate for item in self._items.values())

    @property
    def canvas_bytes_estimate(self) -> int:
        return self.hi_size[0] * self.hi_size[1]

    @property
    def total_live_raster_bytes_estimate(self) -> int:
        return self.canvas_bytes_estimate + self.active_material_bytes + self.out_size[0] * self.out_size[1] * 4

    @property
    def stats(self) -> AlphaActiveStats:
        return AlphaActiveStats(
            self._advances,
            self._append_strokes,
            self._changed_strokes,
            self._removed_strokes,
            self._rebuilt_regions,
            self._recomposited_strokes,
            self._snapshots,
            self._released_materials,
        )

    def close(self) -> None:
        for item in self._items.values():
            try:
                item.mask.close()
            except Exception:
                pass
        self._items.clear()
        self.alpha_canvas.close()
        self.output_canvas.close()
