from __future__ import annotations

"""S02 prototype: cache expensive per-stroke pencil-contact rasters.

This module deliberately lives under dev/benchmarks.  It does not change the
production renderer or replay contract.  The prototype reuses the exact
pillow-pencil-contact-v9 material functions, then rebuilds each requested
frame by compositing cached cropped stroke layers in authoritative layer order.

The important S02 boundary is: expensive stroke materialization happens once
per distinct stroke content/profile, while full-frame compositing/downsampling
still happens per frame.  Incremental canvas/dirty-tile reuse belongs to S04+.
"""

import dataclasses
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from PIL import Image

from img2drawing.core.ir import Stroke, StrokeIR
from img2drawing.render import pillow_eraser_material as p7
from img2drawing.render import pillow_graphite_grain as p3
from img2drawing.render import pillow_paper_interaction as p5
from img2drawing.render import pillow_pencil_contact as pc


@dataclass(frozen=True)
class CachedStrokeRaster:
    key: str
    bounds: tuple[int, int, int, int]
    mask: Image.Image
    bytes_estimate: int


class StrokeRasterCache:
    """Deterministic in-memory cache for one renderer/profile family.

    S02 intentionally rejects eraser strokes because an eraser is an ordered
    destructive operation on the accumulated graphite canvas, not an
    independently compositable source-over layer.  Delete/replace history is
    safe: deleted versions are simply absent from a requested IR and replaced
    versions produce a different content key.
    """

    def __init__(self) -> None:
        self._items: dict[str, CachedStrokeRaster] = {}
        self.hits = 0
        self.misses = 0
        self.materialize_seconds = 0.0

    @staticmethod
    def _stable_payload(
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
    ) -> dict[str, Any]:
        return {
            "renderer": pc.RENDERER_ID,
            "renderer_version": pc.RENDERER_VERSION,
            "stroke": dataclasses.asdict(stroke),
            "factor": float(factor),
            "hi_size": [int(hi_size[0]), int(hi_size[1])],
            "tooth": float(tooth),
            "paper_scale": float(paper_scale),
            "paper_seed": int(paper_seed),
            "graphite": [int(x) for x in graphite],
            "grade": None if grade is None else str(grade).upper(),
            "contact_profile": None if contact_profile is None else str(contact_profile),
        }

    def key_for(self, stroke: Stroke, **kwargs: Any) -> str:
        payload = self._stable_payload(stroke, **kwargs)
        data = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return hashlib.sha256(data).hexdigest()

    def get_or_materialize(
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
        if p7.is_eraser(stroke):
            raise ValueError("S02 StrokeRasterCache prototype does not cache eraser strokes")

        key = self.key_for(
            stroke,
            factor=factor,
            hi_size=hi_size,
            tooth=tooth,
            paper_scale=paper_scale,
            paper_seed=paper_seed,
            graphite=graphite,
            grade=grade,
            contact_profile=contact_profile,
        )
        cached = self._items.get(key)
        if cached is not None:
            self.hits += 1
            return cached

        import time
        t0 = time.perf_counter()
        prepared = pc._prepare_grade(stroke, grade)
        prepared = pc._smooth_hand_dynamics(prepared, profile)
        grain, hardness = p3._material(prepared)
        bounds = pc._contact_bounds(prepared, factor, hardness, hi_size, profile)
        mask = pc._continuous_contact_mask(prepared, factor, hardness, bounds, profile)
        continuity = pc._continuity_floor_mask(prepared, factor, hardness, bounds, profile)
        mask = pc._smooth_grain_modulate(
            mask,
            stroke=prepared,
            grain=grain,
            hardness=hardness,
            factor=factor,
            global_origin=(bounds[0], bounds[1]),
            seed=p3._stroke_seed(prepared),
            profile=profile,
        )
        mask = pc._smooth_paper_modulate(
            mask,
            stroke=prepared,
            tooth=tooth,
            paper_scale=paper_scale,
            paper_seed=paper_seed,
            factor=factor,
            global_origin=(bounds[0], bounds[1]),
            hardness=hardness,
            profile=profile,
        )
        from PIL import ImageChops
        mask = ImageChops.lighter(mask, continuity)
        # Cache the 8-bit alpha/material mask rather than a 4-channel RGBA tile.
        # Graphite RGB is constant for one render profile and is cheap to reattach on
        # composition. This keeps S02 memory roughly 4x lower without changing pixels.
        item = CachedStrokeRaster(
            key=key,
            bounds=bounds,
            mask=mask,
            bytes_estimate=int(mask.width * mask.height),
        )
        self._items[key] = item
        self.misses += 1
        self.materialize_seconds += time.perf_counter() - t0
        return item

    @property
    def entries(self) -> int:
        return len(self._items)

    @property
    def bytes_estimate(self) -> int:
        return sum(item.bytes_estimate for item in self._items.values())

    def close(self) -> None:
        for item in self._items.values():
            item.mask.close()
        self._items.clear()


def render_cached(
    ir: StrokeIR,
    path: str | Path,
    cache: StrokeRasterCache,
    background=(255, 255, 255, 255),
    *,
    scale: int = 1,
    supersample: int = pc.DEFAULT_SUPERSAMPLE,
    graphite=(36, 34, 32),
    grade: str | None = None,
    contact_profile: str | Path | None = None,
) -> None:
    """Render using the exact v9 stroke material functions plus raster reuse."""
    if int(scale) != scale or scale < 1:
        raise ValueError("scale must be a positive integer")
    if int(supersample) != supersample or supersample < 2:
        raise ValueError("supersample must be an integer >= 2")
    if grade is not None:
        pc.p6.get_grade(grade)
    profile = pc.load_pencil_contact_profile(contact_profile)
    scale = int(scale)
    supersample = int(supersample)
    factor = float(scale * supersample)
    hi_size = (int(ir.width * factor), int(ir.height * factor))
    out_size = (int(ir.width * scale), int(ir.height * scale))
    tooth, paper_scale, paper_seed = p5._paper_settings(ir)
    graphite_rgb = (int(graphite[0]), int(graphite[1]), int(graphite[2]))

    graphite_canvas = Image.new("RGBA", hi_size, (*graphite_rgb, 0))
    for stroke in sorted(ir.strokes, key=lambda z: z.layer):
        if p7.is_eraser(stroke):
            # Keep exact semantics for unsupported cases; S02 metrics separately
            # report that these are uncached destructive operations.
            p7._erase(
                graphite_canvas,
                stroke,
                factor=factor,
                hi_size=hi_size,
                tooth=tooth,
                paper_scale=paper_scale,
                paper_seed=paper_seed,
            )
            continue
        item = cache.get_or_materialize(
            stroke,
            factor=factor,
            hi_size=hi_size,
            tooth=tooth,
            paper_scale=paper_scale,
            paper_seed=paper_seed,
            graphite=graphite_rgb,
            grade=grade,
            contact_profile=contact_profile,
            profile=profile,
        )
        layer = p3._graphite_layer(item.mask.size, item.mask, graphite=graphite_rgb)
        graphite_canvas.alpha_composite(layer, dest=(item.bounds[0], item.bounds[1]))
        layer.close()

    base = Image.new("RGBA", hi_size, background)
    base = Image.alpha_composite(base, graphite_canvas)
    final = base.resize(out_size, Image.Resampling.LANCZOS)
    p = str(path)
    if p.lower().endswith((".jpg", ".jpeg")):
        final.convert("RGB").save(p, quality=95)
    else:
        final.save(p)
    final.close()
    base.close()
    graphite_canvas.close()
