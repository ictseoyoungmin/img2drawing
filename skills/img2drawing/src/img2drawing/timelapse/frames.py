"""Forward-only frame sources for timelapse export.

``FastFrameSource`` advances through history incrementally: appended strokes composite their
cached patches, edits recomposite only the dirty rectangles, and only changed output regions
are resampled. It is pixel-exact with a full canonical render at every cursor.
``CanonicalFrameSource`` re-renders the whole drawing per frame and is used when a history
contains semantics the incremental path does not support (ordered spatial erasers).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from PIL import Image

from ..core.history import _stroke_from_dict
from ..render import is_eraser, render_image
from ..render.profile import RenderProfile
from .dirty import apply_additions, clip_box, finalize_full, merge_regions, patch_box, recomposite_regions, union_box, update_output_regions
from .patch_cache import PatchCache
from .replay import ForwardHistoryReplay

SUPPORTED_ACTIONS = {
    "stroke.add", "stroke.replace", "stroke.segment_replace", "stroke.soft_lift",
    "stroke.segment_soft_lift", "stroke.delete", "snapshot",
}
MUTATING_ACTIONS = SUPPORTED_ACTIONS - {"snapshot"}


@dataclass(frozen=True)
class FastPathEligibility:
    eligible: bool
    reasons: tuple[str, ...]
    action_types: tuple[str, ...]
    raw_spatial_eraser_seen: bool


def inspect_fast_path_eligibility(history) -> FastPathEligibility:
    reasons: list[str] = []
    action_types = sorted({item.action for item in history.actions[:history.cursor]})
    unsupported = sorted(set(action_types) - SUPPORTED_ACTIONS)
    if unsupported:
        reasons.append("unsupported actions: " + ", ".join(unsupported))
    raw_eraser = False
    for item in history.actions[:history.cursor]:
        if item.action not in {"stroke.add", "stroke.replace"}:
            continue
        payload = item.payload.get("stroke")
        if not payload:
            continue
        try:
            stroke = _stroke_from_dict(payload, item.tool_state)
        except Exception as exc:
            reasons.append(f"cannot decode stroke action seq={item.seq}: {exc}")
            continue
        if is_eraser(stroke):
            raw_eraser = True
            reasons.append(f"raw spatial eraser stroke at seq={item.seq}")
            break
    return FastPathEligibility(not reasons, tuple(reasons), tuple(action_types), raw_eraser)


def _cache_contract(profile: RenderProfile) -> dict[str, str]:
    return {
        "profile_id": profile.profile_id,
        "renderer_id": profile.renderer_id,
        "renderer_version": profile.renderer_version,
        "material_profile": profile.material_profile,
        "seed_domain": profile.seed_domain,
        "compositing": profile.compositing,
    }


class FastFrameSource:
    """Monotone exact native-RGBA frame source; independent of writer/encoder."""

    def __init__(self, history, profile: RenderProfile, *, supersample: int | None = None,
                 persistent_cache_dir: str | Path | None = None):
        self.history = history
        self.eligibility = inspect_fast_path_eligibility(history)
        if not self.eligibility.eligible:
            raise ValueError("fast frame source is ineligible: " + "; ".join(self.eligibility.reasons))
        self.renderer = PatchCache(
            width=history.width, height=history.height, background=profile.background_rgba,
            scale=profile.output_scale,
            supersample=int(profile.supersample if supersample is None else supersample),
            graphite=profile.graphite_rgb, tooth=profile.paper_tooth,
            paper_scale=profile.paper_scale, paper_seed=profile.paper_seed,
            cache_contract=_cache_contract(profile), persistent_cache_dir=persistent_cache_dir,
        )
        self.replay = ForwardHistoryReplay(history)
        self.hi_canvas = Image.new("RGBA", self.renderer.hi_size, (*self.renderer.graphite, 0))
        self.out_canvas = finalize_full(self.renderer, self.hi_canvas)
        self.cursor = 0
        self.stats = {"append_advances": 0, "dirty_advances": 0, "metadata_advances": 0,
                      "dirty_regions": 0, "dirty_output_pixels": 0, "recomposited_strokes": 0}

    @staticmethod
    def _append_order_safe(prev_state: dict, strokes) -> bool:
        """Return True only when direct append preserves canonical stable layer order.

        Canonical rendering is stable-sorted by ``stroke.layer``. Directly alpha-
        compositing new strokes on top is exact only when all new layers come after
        every existing layer and the new batch itself is non-decreasing. Otherwise
        the affected region must be recomposited in canonical layer order.
        """
        if not strokes:
            return True
        new_layers = [stroke.layer for stroke in strokes]
        if any(b < a for a, b in zip(new_layers, new_layers[1:])):
            return False
        if prev_state:
            max_existing = max(stroke.layer for stroke in prev_state.values())
            if new_layers[0] < max_existing:
                return False
        return True

    def _changed_ids(self, delta) -> set[str]:
        changed: set[str] = set()
        for item in delta:
            if item.action == "stroke.add":
                new_id = (item.payload.get("stroke") or {}).get("stroke_id")
                if new_id:
                    changed.add(str(new_id))
            elif item.action == "stroke.replace":
                changed.add(str(item.payload["stroke_id"]))
                new_id = (item.payload.get("stroke") or {}).get("stroke_id")
                if new_id:
                    changed.add(str(new_id))
            elif item.action in MUTATING_ACTIONS:
                sid = item.payload.get("stroke_id")
                if sid:
                    changed.add(str(sid))
        return changed

    def _semantic_dirty_regions(self, delta, prev_state: dict):
        regions = []
        for sid in sorted(self._changed_ids(delta)):
            old = prev_state.get(sid)
            new = self.replay.state.get(sid)
            box = None
            if old is not None:
                box = union_box(box, patch_box(self.renderer, old))
            if new is not None:
                box = union_box(box, patch_box(self.renderer, new))
            if box is not None:
                regions.append(clip_box(box, self.renderer.hi_size))
        return merge_regions(regions)

    def advance_to(self, cursor: int) -> dict:
        target = max(0, min(int(cursor), self.history.cursor))
        if target < self.cursor:
            raise ValueError("FastFrameSource is forward-only")
        if target == self.cursor:
            return {"cursor": target, "mode": "noop", "regions": 0, "output_regions": []}
        prev_state = dict(self.replay.state)
        delta = self.history.actions[self.cursor:target]
        self.replay.advance_to(target)
        snapshot = self.replay.snapshot()
        non_snapshot = [item for item in delta if item.action != "snapshot"]
        if non_snapshot and all(item.action == "stroke.add" for item in non_snapshot):
            strokes = [self.replay.state[str(item.payload["stroke"]["stroke_id"])] for item in non_snapshot]
            if self._append_order_safe(prev_state, strokes):
                changed_regions = apply_additions(self.renderer, self.hi_canvas, strokes)
                mode = "append"
                self.stats["append_advances"] += 1
            else:
                changed_regions = merge_regions([
                    clip_box(patch_box(self.renderer, stroke), self.renderer.hi_size)
                    for stroke in strokes
                ])
                recomposited = recomposite_regions(self.renderer, self.hi_canvas, snapshot.strokes, changed_regions)
                self.stats["recomposited_strokes"] += recomposited
                self.stats["dirty_advances"] += 1
                mode = "layer-reorder-dirty"
        elif not non_snapshot:
            changed_regions = []
            mode = "metadata-only"
            self.stats["metadata_advances"] += 1
        else:
            changed_regions = self._semantic_dirty_regions(non_snapshot, prev_state)
            recomposited = recomposite_regions(self.renderer, self.hi_canvas, snapshot.strokes, changed_regions)
            self.stats["recomposited_strokes"] += recomposited
            self.stats["dirty_advances"] += 1
            mode = "dirty"
        output_regions = []
        if changed_regions:
            targets, output_area = update_output_regions(self.renderer, self.hi_canvas, self.out_canvas, changed_regions)
            ratio = int(round(self.renderer.hi_size[0] / self.renderer.out_size[0]))
            output_regions = [(x0 // ratio, y0 // ratio, x1 // ratio, y1 // ratio) for x0, y0, x1, y1 in targets]
            self.stats["dirty_output_pixels"] += int(output_area)
        self.cursor = target
        self.stats["dirty_regions"] += len(changed_regions)
        return {"cursor": target, "mode": mode, "regions": len(changed_regions), "output_regions": output_regions}

    def image(self) -> Image.Image:
        return self.out_canvas.copy()

    def close(self) -> None:
        self.hi_canvas.close()
        self.out_canvas.close()
        self.renderer.close()


class CanonicalFrameSource:
    """Forward-only full re-render of every requested cursor."""

    def __init__(self, history, profile: RenderProfile, *, supersample: int | None = None,
                 reasons: tuple[str, ...] = ()):
        self.history = history
        self.profile = profile
        self.supersample = int(profile.supersample if supersample is None else supersample)
        self.cursor = 0
        self.reasons = tuple(reasons)
        self._image: Image.Image | None = None
        self.stats = {"canonical_renders": 0}

    def advance_to(self, cursor: int) -> dict:
        target = max(0, min(int(cursor), self.history.cursor))
        if target < self.cursor:
            raise ValueError("CanonicalFrameSource is forward-only")
        kwargs = self.profile.renderer_kwargs()
        kwargs["supersample"] = self.supersample
        image = render_image(self.profile.prepared_ir(self.history.state_at(target)), **kwargs)
        if self._image is not None:
            self._image.close()
        self._image = image
        self.cursor = target
        self.stats["canonical_renders"] += 1
        return {
            "cursor": target, "mode": "canonical-fallback", "regions": 1,
            "output_regions": [(0, 0, image.width, image.height)],
            "fallback_reasons": list(self.reasons),
        }

    def image(self) -> Image.Image:
        if self._image is None:
            self.advance_to(self.cursor)
        return self._image.copy()

    def close(self) -> None:
        if self._image is not None:
            self._image.close()
            self._image = None


def open_frame_source(history, profile: RenderProfile, *, supersample: int | None = None,
                      persistent_cache_dir: str | Path | None = None):
    """Return the exact fast source when eligible, otherwise the canonical source."""

    eligibility = inspect_fast_path_eligibility(history)
    if eligibility.eligible:
        return FastFrameSource(history, profile, supersample=supersample, persistent_cache_dir=persistent_cache_dir)
    return CanonicalFrameSource(history, profile, supersample=supersample, reasons=eligibility.reasons)


def iter_frames(source, cursors: Iterable[int]):
    for cursor in cursors:
        info = source.advance_to(int(cursor))
        yield int(cursor), source.image(), info


__all__ = [
    "CanonicalFrameSource",
    "FastFrameSource",
    "FastPathEligibility",
    "inspect_fast_path_eligibility",
    "iter_frames",
    "open_frame_source",
]
