from __future__ import annotations

import hashlib
import json
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any

from PIL import Image, ImageChops

from ...render.pillow_graphite_grain import _graphite_layer, _material, _stroke_seed
from ...render.pillow_eraser_material import is_eraser
from ...render.pillow_pencil_contact import (
    _contact_bounds,
    _continuous_contact_mask,
    _continuity_floor_mask,
    _prepare_grade,
    _smooth_grain_modulate,
    _smooth_hand_dynamics,
    _smooth_paper_modulate,
    load_pencil_contact_profile,
)

CACHE_SCHEMA = "img2drawing.local.patch-cache.v2"


class PatchCacheRenderer:
    """Exact in-memory content-addressed P9 stroke-patch cache."""

    def __init__(self, *, width: int, height: int, background, scale: int, supersample: int,
                 graphite, grade: str | None, tooth: float, paper_scale: float,
                 paper_seed: int, contact_profile: str | Path | None = None,
                 cache_contract: dict[str, Any] | None = None):
        self.width = int(width)
        self.height = int(height)
        self.background = tuple(int(x) for x in background)
        self.scale = int(scale)
        self.supersample = int(supersample)
        self.factor = float(self.scale * self.supersample)
        self.hi_size = (int(self.width * self.factor), int(self.height * self.factor))
        self.out_size = (int(self.width * self.scale), int(self.height * self.scale))
        self.graphite = tuple(int(x) for x in graphite)
        self.grade = grade
        self.tooth = float(tooth)
        self.paper_scale = float(paper_scale)
        self.paper_seed = int(paper_seed)
        self.profile = load_pencil_contact_profile(contact_profile)
        self.cache_contract = dict(cache_contract or {})
        self.profile_contract = asdict(self.profile)
        self.patch_cache: dict[str, tuple[tuple[int, int], Image.Image, bool]] = {}
        self.object_cache: dict[int, tuple[object, tuple[tuple[int, int], Image.Image, bool]]] = {}
        self.stats = {"cache_hits": 0, "cache_misses": 0, "patch_build_wall_sec": 0.0,
                      "object_cache_hits": 0, "object_cache_misses": 0}

    def _fingerprint(self, stroke) -> str:
        payload: dict[str, Any] = asdict(stroke)
        meta = {
            "schema": CACHE_SCHEMA,
            "scale": self.scale,
            "supersample": self.supersample,
            "graphite": self.graphite,
            "grade": self.grade,
            "tooth": self.tooth,
            "paper_scale": self.paper_scale,
            "paper_seed": self.paper_seed,
            "contact_profile": self.profile_contract,
            "renderer_contract": self.cache_contract,
        }
        blob = json.dumps({"stroke": payload, "meta": meta}, ensure_ascii=False,
                          sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(blob.encode("utf-8")).hexdigest()

    def _build_patch(self, stroke):
        if is_eraser(stroke):
            raise RuntimeError("ordered spatial eraser reached the fast patch cache after eligibility gating")
        grain, hardness = _material(stroke)
        bounds = _contact_bounds(stroke, self.factor, hardness, self.hi_size, self.profile)
        mask = _continuous_contact_mask(stroke, self.factor, hardness, bounds, self.profile)
        continuity = _continuity_floor_mask(stroke, self.factor, hardness, bounds, self.profile)
        mask = _smooth_grain_modulate(
            mask, stroke=stroke, grain=grain, hardness=hardness, factor=self.factor,
            global_origin=(bounds[0], bounds[1]), seed=_stroke_seed(stroke), profile=self.profile,
        )
        mask = _smooth_paper_modulate(
            mask, stroke=stroke, tooth=self.tooth, paper_scale=self.paper_scale,
            paper_seed=self.paper_seed, factor=self.factor, global_origin=(bounds[0], bounds[1]),
            hardness=hardness, profile=self.profile,
        )
        mask = ImageChops.lighter(mask, continuity)
        layer = _graphite_layer(mask.size, mask, graphite=self.graphite)
        mask.close()
        continuity.close()
        return (bounds[0], bounds[1]), layer, False

    def patch_for(self, stroke):
        prepared = _smooth_hand_dynamics(_prepare_grade(stroke, self.grade), self.profile)
        key = self._fingerprint(prepared)
        hit = self.patch_cache.get(key)
        if hit is not None:
            self.stats["cache_hits"] += 1
            return hit
        t0 = time.perf_counter()
        patch = self._build_patch(prepared)
        self.stats["patch_build_wall_sec"] += time.perf_counter() - t0
        self.patch_cache[key] = patch
        self.stats["cache_misses"] += 1
        return patch

    def patch_for_fast(self, stroke):
        oid = id(stroke)
        hit = self.object_cache.get(oid)
        if hit is not None and hit[0] is stroke:
            self.stats["object_cache_hits"] += 1
            return hit[1]
        self.stats["object_cache_misses"] += 1
        patch = self.patch_for(stroke)
        self.object_cache[oid] = (stroke, patch)
        return patch

    def close(self) -> None:
        seen: set[int] = set()
        for _, layer, _ in self.patch_cache.values():
            if id(layer) in seen:
                continue
            seen.add(id(layer))
            layer.close()
        self.patch_cache.clear()
        self.object_cache.clear()
