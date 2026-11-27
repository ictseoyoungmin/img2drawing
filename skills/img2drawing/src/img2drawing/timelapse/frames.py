"""Forward-only frame sources for timelapse export.

``FastFrameSource`` advances through history incrementally: appended strokes composite their
cached patches, edits recomposite only the dirty rectangles, and only changed output regions
are resampled. It is pixel-exact with a full canonical render at every cursor.
``CanonicalFrameSource`` re-renders the whole drawing per frame and is used when a history
contains unsupported semantics. Explicit path lifts use the same eraser in both sources.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from PIL import Image

from ..core.history import _stroke_from_dict, _MixedCanvasAction
from ..core.material import INK_ACTION_KINDS, MIXED_HISTORY_CONTRACT
from ..inspection import drawing_state_hash
from ..render.contract import MIXED_MEDIA_CONTRACT
from ..render import is_eraser, render_image
from ..render.eraser import is_explicit_path_eraser
from ..render.profile import RenderProfile
from .dirty import apply_additions, clip_box, finalize_full, intersects, merge_regions, patch_box, recomposite_regions, union_box, update_output_regions
from .patch_cache import PatchCache, InkPatchCache
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
    if history.media_contract is not None:
        if history.media_contract!=MIXED_HISTORY_CONTRACT:
            reasons.append("unknown mixed history contract")
        if set(action_types)-INK_ACTION_KINDS-{"snapshot"}:
            reasons.append("mixed graphite/eraser history requires canonical replay")
        if not set(action_types)&INK_ACTION_KINDS:
            reasons.append("mixed history has no ink actions")
        if not all(type(item) is _MixedCanvasAction for item in history.actions[:history.cursor]):
            reasons.append("unsealed mixed history requires canonical replay")
        return FastPathEligibility(not reasons,tuple(reasons),tuple(action_types),False)
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
        if is_eraser(stroke) and not is_explicit_path_eraser(stroke):
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
        profile.validate_history(history)
        if profile.is_mixed_media:
            raise ValueError("use InkFrameSource or open_frame_source for mixed histories")
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
            renderer_version=profile.renderer_version, renderer_contract_digest=profile.renderer_contract_digest,
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
        ordered_lift = any(is_eraser(s) for s in snapshot.strokes) or any(is_eraser(s) for s in prev_state.values())
        if non_snapshot and all(item.action == "stroke.add" for item in non_snapshot):
            strokes = [self.replay.state[str(item.payload["stroke"]["stroke_id"])] for item in non_snapshot]
            if self._append_order_safe(prev_state, strokes):
                changed_regions = apply_additions(self.renderer, self.hi_canvas, strokes)
                mode = "append"
                self.stats["append_advances"] += 1
            else:
                changed_regions = [(0, 0, *self.renderer.hi_size)] if ordered_lift else merge_regions([
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
            changed_regions = [(0, 0, *self.renderer.hi_size)] if ordered_lift else self._semantic_dirty_regions(non_snapshot, prev_state)
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


@dataclass(frozen=True)
class _InkFrameEntry:
    element: object
    key: tuple
    bounds: tuple[int,int,int,int]


def _box_area(box):
    return max(0,box[2]-box[0])*max(0,box[3]-box[1])


def _bounded_regions(boxes):
    boxes=[b for b in boxes if _box_area(b)]
    # Bound quadratic rectangle merging and delta pack patch count. A larger
    # enclosing rectangle is conservative, never a smaller affected region.
    if len(boxes)>128:
        return [(min(b[0] for b in boxes),min(b[1] for b in boxes),
                 max(b[2] for b in boxes),max(b[3] for b in boxes))]
    return merge_regions(boxes)


class InkFrameSource:
    """Exact incremental opaque-paper ink-only frames.

    Same native ink kernel and stable layer ordering as canonical mixed
    composition. Old/new patch bounds select dirty regions; replacement or
    deletion reconstructs those regions from all intersecting current marks.
    Graphite/eraser histories and transparent RGB staging are out of scope.
    """
    def __init__(self,history,profile:RenderProfile,*,supersample=None,
                 cache_bytes=InkPatchCache.DEFAULT_MAX_BYTES):
        profile.validate_history(history)
        eligible=inspect_fast_path_eligibility(history)
        if not profile.is_mixed_media or not eligible.eligible:
            raise ValueError("ink fast frame source is ineligible: "+"; ".join(eligible.reasons))
        if profile.background_rgba[3]!=255:
            raise ValueError("ink fast frame source requires opaque background")
        self.history=history
        self.profile=profile
        self.renderer=InkPatchCache(profile,supersample=supersample,max_bytes=cache_bytes)
        self.replay=ForwardHistoryReplay(history)
        self._records=tuple(history.actions[:history.cursor])
        self._entries={}
        self.cursor=0
        self._failed=False
        self._closed=False
        self.hi_canvas=Image.new("RGBA",self.renderer.hi_size,profile.background_rgba)
        self.out_canvas=self.hi_canvas.resize(self.renderer.out_size,Image.Resampling.LANCZOS)
        self.state_hash=drawing_state_hash(self.replay.snapshot())
        self.stats={"append_advances":0,"dirty_advances":0,"metadata_advances":0,
                    "dirty_regions":0,"dirty_output_pixels":0,"recomposited_marks":0,
                    "actions_applied":0}

    def _check_history(self):
        if (self.history.cursor!=len(self._records) or
                any(a is not b for a,b in zip(self._records,self.history.actions)) or
                len(self.history.actions)<len(self._records)):
            raise ValueError("history changed during ink fast replay; open a new frame source")

    def _apply_entry(self,entry,dirty=None):
        if not _box_area(entry.bounds):
            return
        with self.renderer.patch(entry.element.mark,key=entry.key) as (box,patch):
            if box!=entry.bounds:
                raise RuntimeError("ink patch bounds changed within a fixed profile")
            if dirty is None:
                self.hi_canvas.alpha_composite(patch,dest=box[:2])
            else:
                x0,y0=max(box[0],dirty[0]),max(box[1],dirty[1])
                x1,y1=min(box[2],dirty[2]),min(box[3],dirty[3])
                with patch.crop((x0-box[0],y0-box[1],x1-box[0],y1-box[1])) as crop:
                    self.hi_canvas.alpha_composite(crop,dest=(x0,y0))

    def advance_to(self,cursor:int)->dict:
        if self._failed or self._closed:
            raise RuntimeError("ink frame source is closed or failed; open a new source")
        self._check_history()
        target=max(0,min(int(cursor),len(self._records)))
        if target<self.cursor:
            raise ValueError("InkFrameSource is forward-only")
        if target==self.cursor:
            return {"cursor":target,"mode":"noop","regions":0,"output_regions":[]}
        try:
            return self._advance(target)
        except Exception:
            # A failed frame never becomes reusable partially composed state.
            self._failed=True
            raise

    def _advance(self,target):
        previous=self._entries
        delta=[item for item in self._records[self.cursor:target] if item.action!="snapshot"]
        self.replay.advance_to(target)
        ir=self.replay.snapshot()
        if ir.strokes:
            raise ValueError("graphite reached ink-only frame source")
        entries={}
        for e in ir.ink_elements:
            old=previous.get(e.element_id)
            if old is not None and (old.element.mark is e.mark or old.element.mark==e.mark):
                entries[e.element_id]=_InkFrameEntry(e,old.key,old.bounds)
                continue
            key=self.renderer.key(e.mark)
            with self.renderer.patch(e.mark,key=key) as (bounds,_):
                entries[e.element_id]=_InkFrameEntry(e,key,bounds)
        # Canonical ink-only composite work is the page plus all current patch
        # bounds. Preserve the same gate even when incremental work is small.
        work=self.renderer.hi_size[0]*self.renderer.hi_size[1]+sum(
            _box_area(entry.bounds) for entry in entries.values())
        if work>MIXED_MEDIA_CONTRACT.value("max_composite_work"):
            raise ValueError("mixed-media composite work budget exceeded")
        ordered=sorted(entries.values(),key=lambda entry:entry.element.layer)
        changed={item.payload["element_id"] for item in delta}
        boxes=[mapping[sid].bounds for sid in changed for mapping in (previous,entries)
               if sid in mapping]
        regions=_bounded_regions(boxes)
        if not delta:
            mode="metadata-only"
            self.stats["metadata_advances"]+=1
        else:
            append=all(item.action=="ink.add" for item in delta)
            additions=[entries[item.payload["element_id"]] for item in delta] if append else []
            layers=[entry.element.layer for entry in additions]
            append=append and all(a<=b for a,b in zip(layers,layers[1:])) and (
                not previous or layers[0]>=max(entry.element.layer for entry in previous.values()))
            if append:
                for entry in additions:
                    self._apply_entry(entry)
                mode="append"
                self.stats["append_advances"]+=1
            else:
                for region in regions:
                    self.hi_canvas.paste(self.profile.background_rgba,region)
                    for entry in ordered:
                        if _box_area(entry.bounds) and intersects(entry.bounds,region):
                            self._apply_entry(entry,region)
                            self.stats["recomposited_marks"]+=1
                mode="dirty"
                self.stats["dirty_advances"]+=1
        output_regions=[]
        if regions:
            targets,area=update_output_regions(self.renderer,self.hi_canvas,self.out_canvas,
                                               regions,precomposited=True)
            ratio=self.renderer.supersample
            output_regions=[tuple(v//ratio for v in box) for box in targets]
            self.stats["dirty_output_pixels"]+=area
        self._entries=entries
        self.cursor=target
        self.state_hash=drawing_state_hash(ir)
        self.stats["dirty_regions"]+=len(regions)
        self.stats["actions_applied"]=self.replay.stats.actions_applied
        return {"cursor":target,"mode":mode,"regions":len(regions),"output_regions":output_regions}

    def image(self):
        if self._failed or self._closed:
            raise RuntimeError("ink frame source is closed or failed")
        return self.out_canvas.copy()

    def close(self):
        if not self._closed:
            self.hi_canvas.close()
            self.out_canvas.close()
            self.renderer.close()
            self._entries.clear()
            self._closed=True


class CanonicalFrameSource:
    """Forward-only full re-render of every requested cursor."""

    def __init__(self, history, profile: RenderProfile, *, supersample: int | None = None,
                 reasons: tuple[str, ...] = ()):
        profile.validate_history(history)
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
    reasons=eligibility.reasons
    if eligibility.eligible:
        if profile.is_mixed_media:
            if profile.background_rgba[3]==255:
                return InkFrameSource(history,profile,supersample=supersample)
            reasons=("transparent background requires canonical RGBA frame staging",)
        else:
            return FastFrameSource(history, profile, supersample=supersample, persistent_cache_dir=persistent_cache_dir)
    return CanonicalFrameSource(history, profile, supersample=supersample, reasons=reasons)


def iter_frames(source, cursors: Iterable[int]):
    for cursor in cursors:
        info = source.advance_to(int(cursor))
        yield int(cursor), source.image(), info


__all__ = [
    "CanonicalFrameSource",
    "FastFrameSource",
    "InkFrameSource",
    "FastPathEligibility",
    "inspect_fast_path_eligibility",
    "iter_frames",
    "open_frame_source",
]
