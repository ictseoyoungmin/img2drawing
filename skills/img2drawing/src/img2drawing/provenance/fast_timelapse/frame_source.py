from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Iterable

from PIL import Image

from ...core.history import _stroke_from_dict
from ...render.pillow_eraser_material import is_eraser
from ...render.renderer_registry import current_renderer, resolve_renderer

from .dirty_regions import apply_additions, clip_box, merge_regions, patch_box, recomposite_regions, union_box
from .dirty_resample import finalize_full, update_output_regions
from .replay import ForwardHistoryReplay
from .patch_cache import PatchCacheRenderer

SUPPORTED_ACTIONS = {
    "stroke.add", "stroke.replace", "stroke.segment_replace", "stroke.soft_lift",
    "stroke.segment_soft_lift", "stroke.delete", "snapshot",
}
MUTATING_ACTIONS = SUPPORTED_ACTIONS - {"snapshot"}


class FastPathIneligible(RuntimeError):
    pass


@dataclass(frozen=True)
class FrameRenderConfig:
    background_rgba: tuple[int, int, int, int]
    graphite_rgb: tuple[int, int, int]
    # Keep the historical positional constructor stable: callers that pass
    # ``FrameRenderConfig(background, graphite, 1, 2)`` still mean
    # output_scale=1, supersample=2. Renderer identity is an additive optional tail.
    output_scale: int = 1
    supersample: int = 2
    paper_tooth: float = 0.46
    paper_scale: float = 1.0
    paper_seed: int = 170817
    renderer_id: str | None = None
    renderer_version: str | None = None


@dataclass(frozen=True)
class FrameSourceEligibility:
    eligible: bool
    reasons: tuple[str, ...]
    action_types: tuple[str, ...]
    raw_spatial_eraser_seen: bool


def inspect_fast_path_eligibility(history) -> FrameSourceEligibility:
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
    return FrameSourceEligibility(not reasons, tuple(reasons), tuple(action_types), raw_eraser)


class FastFrameSource:
    """Monotone exact native-RGBA frame source; independent of writer/encoder."""

    def __init__(self, history, config: FrameRenderConfig, *, renderer_cls=PatchCacheRenderer, renderer_kwargs: dict | None = None):
        self.history = history
        self.config = config
        self.eligibility = inspect_fast_path_eligibility(history)
        if not self.eligibility.eligible:
            raise FastPathIneligible("; ".join(self.eligibility.reasons))
        self.backend = (
            resolve_renderer(config.renderer_id, config.renderer_version)
            if config.renderer_id is not None and config.renderer_version is not None
            else current_renderer()
        )
        extra = dict(renderer_kwargs or {})
        extra.setdefault("renderer_backend", self.backend)
        self.renderer = renderer_cls(
            width=history.width, height=history.height, background=config.background_rgba,
            scale=config.output_scale, supersample=config.supersample, graphite=config.graphite_rgb,
            grade=None, tooth=config.paper_tooth, paper_scale=config.paper_scale, paper_seed=config.paper_seed,
            contact_profile=None, **extra,
        )
        self.replay = ForwardHistoryReplay(history)
        self.hi_canvas = Image.new("RGBA", self.renderer.hi_size,
                                   (*self.renderer.graphite, 0))
        self.out_canvas = finalize_full(self.renderer, self.hi_canvas)
        self.cursor = 0
        self.stats = {"append_advances": 0, "dirty_advances": 0, "metadata_advances": 0,
                      "dirty_regions": 0, "dirty_output_pixels": 0, "recomposited_strokes": 0}

    @classmethod
    def from_vnext_session(cls, session, *, supersample: int | None = None, renderer_cls=PatchCacheRenderer, renderer_kwargs: dict | None = None):
        profile = session.render_profile
        if profile is None:
            raise ValueError("session has no render profile")
        config = FrameRenderConfig(
            background_rgba=tuple(profile.background_rgba), graphite_rgb=tuple(profile.graphite_rgb),
            renderer_id=profile.renderer_id, renderer_version=profile.renderer_version,
            output_scale=int(profile.output_scale),
            supersample=int(profile.supersample if supersample is None else supersample),
            paper_tooth=float(profile.paper_tooth), paper_scale=float(profile.paper_scale),
            paper_seed=int(profile.paper_seed),
        )
        extra = dict(renderer_kwargs or {})
        extra.setdefault("cache_contract", {
            "profile_id": profile.profile_id,
            "renderer_id": profile.renderer_id,
            "renderer_version": profile.renderer_version,
            "material_profile": profile.material_profile,
            "seed_domain": profile.seed_domain,
            "compositing": profile.compositing,
        })
        return cls(session._agent.history, config, renderer_cls=renderer_cls, renderer_kwargs=extra)

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
    """Forward-only canonical fallback using the profile-selected renderer backend."""

    def __init__(self, history, config: FrameRenderConfig, *, reasons: tuple[str, ...] = ()):
        self.history = history
        self.config = config
        self.backend = (
            resolve_renderer(config.renderer_id, config.renderer_version)
            if config.renderer_id is not None and config.renderer_version is not None
            else current_renderer()
        )
        self.cursor = 0
        self.reasons = tuple(reasons)
        self._tmp = TemporaryDirectory(prefix="img2drawing-canonical-fallback-")
        self._path = Path(self._tmp.name) / "frame.png"
        self._image = None
        self.stats = {"canonical_renders": 0}

    @classmethod
    def from_vnext_session(cls, session, *, supersample: int | None = None, reasons: tuple[str, ...] = ()):
        profile = session.render_profile
        if profile is None:
            raise ValueError("session has no render profile")
        config = FrameRenderConfig(
            background_rgba=tuple(profile.background_rgba), graphite_rgb=tuple(profile.graphite_rgb),
            renderer_id=profile.renderer_id, renderer_version=profile.renderer_version,
            output_scale=int(profile.output_scale),
            supersample=int(profile.supersample if supersample is None else supersample),
            paper_tooth=float(profile.paper_tooth), paper_scale=float(profile.paper_scale),
            paper_seed=int(profile.paper_seed),
        )
        return cls(session._agent.history, config, reasons=reasons)

    def advance_to(self, cursor: int) -> dict:
        target = max(0, min(int(cursor), self.history.cursor))
        if target < self.cursor:
            raise ValueError("CanonicalFrameSource is forward-only")
        ir = self.history.state_at(target)
        # RenderProfile owns paper state; do not fall back to session metadata defaults.
        from copy import deepcopy
        prepared = deepcopy(ir)
        metadata = deepcopy(prepared.metadata if isinstance(prepared.metadata, dict) else {})
        metadata["paper"] = {
            "tooth": self.config.paper_tooth,
            "scale": self.config.paper_scale,
            "seed": self.config.paper_seed,
        }
        prepared.metadata = metadata
        self.backend.render(
            prepared, self._path, background=self.config.background_rgba,
            scale=self.config.output_scale, supersample=self.config.supersample,
            graphite=self.config.graphite_rgb,
        )
        if self._image is not None:
            self._image.close()
        with Image.open(self._path) as image:
            self._image = image.convert("RGBA").copy()
        self.cursor = target
        self.stats["canonical_renders"] += 1
        return {
            "cursor": target, "mode": "canonical-fallback", "regions": 1,
            "output_regions": [(0, 0, self._image.width, self._image.height)],
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
        self._tmp.cleanup()


def make_frame_source(history, config: FrameRenderConfig, *, renderer_cls=PatchCacheRenderer, renderer_kwargs: dict | None = None):
    """Return exact fast source when eligible, otherwise explicit canonical fallback."""
    eligibility = inspect_fast_path_eligibility(history)
    if eligibility.eligible:
        return FastFrameSource(history, config, renderer_cls=renderer_cls, renderer_kwargs=renderer_kwargs)
    return CanonicalFrameSource(history, config, reasons=eligibility.reasons)


def make_frame_source_from_vnext_session(session, *, supersample: int | None = None, renderer_cls=PatchCacheRenderer, renderer_kwargs: dict | None = None):
    profile = session.render_profile
    if profile is None:
        raise ValueError("session has no render profile")
    config = FrameRenderConfig(
        background_rgba=tuple(profile.background_rgba), graphite_rgb=tuple(profile.graphite_rgb),
        renderer_id=profile.renderer_id, renderer_version=profile.renderer_version,
        output_scale=int(profile.output_scale),
        supersample=int(profile.supersample if supersample is None else supersample),
        paper_tooth=float(profile.paper_tooth), paper_scale=float(profile.paper_scale),
        paper_seed=int(profile.paper_seed),
    )
    eligibility = inspect_fast_path_eligibility(session._agent.history)
    if not eligibility.eligible:
        return CanonicalFrameSource(session._agent.history, config, reasons=eligibility.reasons)
    extra = dict(renderer_kwargs or {})
    extra.setdefault("cache_contract", {
        "profile_id": profile.profile_id,
        "renderer_id": profile.renderer_id,
        "renderer_version": profile.renderer_version,
        "material_profile": profile.material_profile,
        "seed_domain": profile.seed_domain,
        "compositing": profile.compositing,
    })
    return FastFrameSource(session._agent.history, config, renderer_cls=renderer_cls, renderer_kwargs=extra)


def iter_frames(source: FastFrameSource, cursors: Iterable[int]):
    for cursor in cursors:
        info = source.advance_to(int(cursor))
        yield int(cursor), source.image(), info
