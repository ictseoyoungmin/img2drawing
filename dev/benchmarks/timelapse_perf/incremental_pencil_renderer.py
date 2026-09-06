from __future__ import annotations

"""S04 prototype: persistent add-only compositor over S02 stroke-raster cache.

This module deliberately remains under dev/benchmarks. It keeps the exact
pillow-pencil-contact-v9 material masks from S02, but unlike S02 it retains the
supersampled graphite canvas across forward replay cursors. For an add-only
history whose layer order is append-monotone, advancing from one cursor to the
next composites only newly visible strokes.

Replace/delete/eraser invalidation is intentionally out of scope here; those
belong to the next edit-invalidation slice.
"""

from dataclasses import dataclass
from pathlib import Path

from PIL import Image

from img2drawing.core.ir import StrokeIR
from img2drawing.render import pillow_eraser_material as p7
from img2drawing.render import pillow_graphite_grain as p3
from img2drawing.render import pillow_paper_interaction as p5
from img2drawing.render import pillow_pencil_contact as pc

from cached_pencil_renderer import StrokeRasterCache


@dataclass(frozen=True)
class IncrementalStats:
    advances: int
    strokes_composited: int
    snapshots: int


class IncrementalAddOnlyPencilCanvas:
    """Persistent supersampled graphite canvas for monotone add-only replay.

    Contract:
    - canonical v9 material functions are still used through StrokeRasterCache;
    - previously composited stroke identities must remain an exact prefix of
      the next requested IR after authoritative layer sorting;
    - erasers are rejected because they are destructive operations;
    - dirty output patches use the same canonical Lanczos resampling.
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
        self._stroke_ids: list[str] = []
        self._width = initial_ir.width
        self._height = initial_ir.height
        self._advances = 0
        self._strokes_composited = 0
        self._snapshots = 0
        self._dirty_hi: tuple[int, int, int, int] | None = None
        self.dirty_output_pixels = 0

    def advance_to(self, ir: StrokeIR) -> int:
        if ir.width != self._width or ir.height != self._height:
            raise ValueError("canvas dimensions changed during incremental replay")
        tooth, paper_scale, paper_seed = p5._paper_settings(ir)
        if (tooth, paper_scale, paper_seed) != (self.tooth, self.paper_scale, self.paper_seed):
            raise ValueError("paper settings changed during incremental replay")

        ordered = sorted(ir.strokes, key=lambda z: z.layer)
        if any(p7.is_eraser(stroke) for stroke in ordered):
            raise ValueError("S04 add-only prototype does not support eraser strokes")
        stroke_ids = [str(stroke.stroke_id) for stroke in ordered]
        if stroke_ids[: len(self._stroke_ids)] != self._stroke_ids:
            raise ValueError("requested IR is not an append-only extension of persistent canvas state")

        new_strokes = ordered[len(self._stroke_ids):]
        for stroke in new_strokes:
            item = self.cache.get_or_materialize(
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
            layer = p3._graphite_layer(item.mask.size, item.mask, graphite=self.graphite_rgb)
            self.graphite_canvas.alpha_composite(layer, dest=(item.bounds[0], item.bounds[1]))
            layer.close()
            self._strokes_composited += 1
            bx0, by0, bx1, by1 = item.bounds
            if self._dirty_hi is None:
                self._dirty_hi = (bx0, by0, bx1, by1)
            else:
                dx0, dy0, dx1, dy1 = self._dirty_hi
                self._dirty_hi = (min(dx0, bx0), min(dy0, by0), max(dx1, bx1), max(dy1, by1))
        self._stroke_ids = stroke_ids
        self._advances += 1
        return len(new_strokes)

    def snapshot(self, path: str | Path) -> None:
        """Canonical full-frame snapshot, retained for parity/reference timing."""
        base = Image.new("RGBA", self.hi_size, self.background)
        base.alpha_composite(self.graphite_canvas)
        final = base.resize(self.out_size, Image.Resampling.LANCZOS)
        self._save(final, path)
        final.close()
        base.close()
        self._snapshots += 1
        self._dirty_hi = None

    def snapshot_dirty(
        self,
        path: str | Path,
        *,
        influence_halo: int = 4,
        sample_halo: int = 4,
    ) -> tuple[int, int, int, int] | None:
        """Update only logical pixels influenced by newly composited high-res marks."""
        if self._dirty_hi is not None:
            import math

            hx0, hy0, hx1, hy1 = self._dirty_hi
            f = self.factor
            tx0 = max(0, int(math.floor(hx0 / f)) - influence_halo)
            ty0 = max(0, int(math.floor(hy0 / f)) - influence_halo)
            tx1 = min(self.out_size[0], int(math.ceil(hx1 / f)) + influence_halo)
            ty1 = min(self.out_size[1], int(math.ceil(hy1 / f)) + influence_halo)

            # Keep a second, logical-pixel-aligned halo around the resize box so
            # interior Lanczos samples do not observe a synthetic crop boundary.
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
            graphite_patch = self.graphite_canvas.crop(src_box)
            base = Image.new("RGBA", graphite_patch.size, self.background)
            base.alpha_composite(graphite_patch)
            outer = base.resize((ox1 - ox0, oy1 - oy0), Image.Resampling.LANCZOS)
            inner = outer.crop((tx0 - ox0, ty0 - oy0, tx1 - ox0, ty1 - oy0))
            self.output_canvas.paste(inner, (tx0, ty0))
            self.dirty_output_pixels += (tx1 - tx0) * (ty1 - ty0)
            graphite_patch.close()
            base.close()
            outer.close()
            inner.close()
            dirty = (tx0, ty0, tx1, ty1)
        else:
            dirty = None

        self._save(self.output_canvas, path)
        self._snapshots += 1
        self._dirty_hi = None
        return dirty

    @staticmethod
    def _save(image: Image.Image, path: str | Path) -> None:
        p = str(path)
        if p.lower().endswith((".jpg", ".jpeg")):
            image.convert("RGB").save(p, quality=95)
        else:
            image.save(p)

    @property
    def stats(self) -> IncrementalStats:
        return IncrementalStats(
            advances=self._advances,
            strokes_composited=self._strokes_composited,
            snapshots=self._snapshots,
        )

    @property
    def canvas_bytes_estimate(self) -> int:
        return int(self.hi_size[0] * self.hi_size[1] * 4)

    def close(self) -> None:
        self.graphite_canvas.close()
        self.output_canvas.close()
