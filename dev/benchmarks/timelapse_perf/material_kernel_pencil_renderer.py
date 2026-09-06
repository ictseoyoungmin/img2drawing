from __future__ import annotations

"""S03 dev prototype: exact material-field kernels over S02 raster caching."""

import time
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops

from img2drawing.render import pillow_eraser_material as p7
from img2drawing.render import pillow_graphite_grain as p3
from img2drawing.render import pillow_paper_interaction as p5
from img2drawing.render import pillow_pencil_contact as pc

from cached_pencil_renderer import CachedStrokeRaster, StrokeRasterCache
from material_field_kernel import paper_field_grid, value_noise_grid


def smooth_grain_modulate_grid(
    mask: Image.Image,
    *,
    stroke,
    grain: float,
    hardness: float,
    factor: float,
    global_origin: tuple[int, int],
    seed: int,
    profile,
) -> Image.Image:
    g = pc._clamp01(grain)
    if g <= 1e-8:
        return mask
    arr = np.asarray(mask, dtype=np.float32)
    active = arr > 0.5
    if not np.any(active):
        return mask

    gp = profile.grain
    coarse = value_noise_grid(
        arr.shape, factor=factor, global_origin=global_origin,
        cell=gp.coarse_cell, seed=seed ^ 0xA511E9B3,
    )
    fine = value_noise_grid(
        arr.shape, factor=factor, global_origin=global_origin,
        cell=gp.fine_cell, seed=seed ^ 0x63D83595,
    )
    field = np.float32(0.72) * coarse + np.float32(0.28) * fine

    width = pc._mean_contact_width(stroke, hardness, profile)
    thin_gain = pc._thin_texture_gain(width, gp.thin_width_reference, gp.thin_texture_floor)
    strength = np.float32(gp.strength * g * thin_gain)
    mod = np.float32(1.0) + strength * (field - np.float32(0.5)) * np.float32(2.0)
    mean_mod = float(np.mean(mod[active]))
    if mean_mod > 1e-6:
        mod = mod / np.float32(mean_mod)
    mod = np.clip(mod, np.float32(gp.min_modulation), np.float32(gp.max_modulation))
    out = np.clip(arr * mod, 0.0, 255.0).astype(np.uint8)
    return Image.fromarray(out, mode="L")


def smooth_paper_modulate_grid(
    mask: Image.Image,
    *,
    stroke,
    tooth: float,
    paper_scale: float,
    paper_seed: int,
    factor: float,
    global_origin: tuple[int, int],
    hardness: float,
    profile,
) -> Image.Image:
    t = pc._clamp01(tooth)
    if t <= 1e-8:
        return mask
    arr = np.asarray(mask, dtype=np.float32)
    active = arr > 0.5
    if not np.any(active):
        return mask

    pressure = p5._stroke_pressure(stroke)
    field = paper_field_grid(
        arr.shape,
        factor=factor,
        global_origin=global_origin,
        paper_scale=paper_scale,
        paper_seed=paper_seed,
    )
    pp = profile.paper
    width = pc._mean_contact_width(stroke, hardness, profile)
    thin_gain = pc._thin_texture_gain(width, pp.thin_width_reference, pp.thin_texture_floor)

    relief = (field - np.float32(0.5)) * np.float32(2.0)
    contact = np.float32((0.52 + 0.56 * hardness) * (1.0 - 0.56 * pressure))
    strength = np.float32(pp.strength * t * thin_gain) * contact
    mod = np.float32(1.0) + strength * relief
    valley_cut = float(0.23 + 0.12 * t - 0.11 * pressure)
    band = float(pp.valley_band)
    lo = valley_cut - band
    hi = valley_cut + band
    u = np.clip((field - np.float32(lo)) / np.float32(max(1e-6, hi - lo)), 0.0, 1.0)
    smooth = u * u * (np.float32(3.0) - np.float32(2.0) * u)
    valley_weight = np.float32(1.0) - smooth
    valley_depth = np.float32(pp.valley_depth * t * thin_gain * (1.0 - 0.45 * pressure))
    mod *= np.float32(1.0) - valley_weight * valley_depth

    mean_mod = float(np.mean(mod[active]))
    if mean_mod > 1e-6:
        mod = mod / np.float32(mean_mod)
    mod = np.clip(mod, np.float32(pp.min_modulation), np.float32(pp.max_modulation))
    out = np.clip(arr * mod, 0.0, 255.0).astype(np.uint8)
    return Image.fromarray(out, mode="L")


class KernelStrokeRasterCache(StrokeRasterCache):
    """S02 mask cache with exact low-allocation grain/paper field kernels."""

    def __init__(self) -> None:
        super().__init__()
        self.stage_seconds = {"grain_mod": 0.0, "paper_mod": 0.0, "other": 0.0}

    def get_or_materialize(
        self,
        stroke,
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
            raise ValueError("S03 kernel prototype does not cache eraser strokes")
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

        t_all = time.perf_counter()
        t = time.perf_counter()
        prepared = pc._prepare_grade(stroke, grade)
        prepared = pc._smooth_hand_dynamics(prepared, profile)
        grain, hardness = p3._material(prepared)
        bounds = pc._contact_bounds(prepared, factor, hardness, hi_size, profile)
        mask = pc._continuous_contact_mask(prepared, factor, hardness, bounds, profile)
        continuity = pc._continuity_floor_mask(prepared, factor, hardness, bounds, profile)
        self.stage_seconds["other"] += time.perf_counter() - t

        t = time.perf_counter()
        m2 = smooth_grain_modulate_grid(
            mask,
            stroke=prepared,
            grain=grain,
            hardness=hardness,
            factor=factor,
            global_origin=(bounds[0], bounds[1]),
            seed=p3._stroke_seed(prepared),
            profile=profile,
        )
        self.stage_seconds["grain_mod"] += time.perf_counter() - t
        if m2 is not mask:
            mask.close()
        mask = m2

        t = time.perf_counter()
        m2 = smooth_paper_modulate_grid(
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
        self.stage_seconds["paper_mod"] += time.perf_counter() - t
        if m2 is not mask:
            mask.close()
        mask = m2

        merged = ImageChops.lighter(mask, continuity)
        if merged is not mask:
            mask.close()
        continuity.close()
        mask = merged

        item = CachedStrokeRaster(
            key=key,
            bounds=bounds,
            mask=mask,
            bytes_estimate=int(mask.width * mask.height),
        )
        self._items[key] = item
        self.misses += 1
        self.materialize_seconds += time.perf_counter() - t_all
        return item
