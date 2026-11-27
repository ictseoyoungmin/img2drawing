"""Canonical, bounded mixed-media composition.

Ink patches are opaque geometry; contiguous graphite runs retain their own
alpha until all later ordered graphite lifts have been applied. Only the
local bounds of the current graphite run are allocated, never a full canvas
per stroke or per ink/graphite alternation.
"""
from __future__ import annotations

from bisect import bisect_right
import math

from PIL import Image

from ..core.ir import Stroke, StrokeIR
from ..core.material import InkElement, MIXED_HISTORY_CONTRACT, MAX_PATH_POINTS, MAX_WIDTH, StyledInkPath, Screentone
from .contract import CONTACT_WIDTH_CONTRACT, MIXED_MEDIA_CONTRACT, STYLED_INK_CONTRACT, SCREENTONE_CONTRACT, validate_mixed_raster_budget
from .eraser import erase_local, is_eraser, is_explicit_path_eraser
from .ink import build_ink_patch, validate_ink_work
from .paper import paper_settings


def _area(b):
    return max(0, b[2] - b[0]) * max(0, b[3] - b[1])


def _union(a, b):
    return (min(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3]))


class _Budget:
    def __init__(self):
        self.work = 0
        self.lifts = 0

    def reserve(self, cells):
        self.work += cells
        if self.work > MIXED_MEDIA_CONTRACT.value("max_composite_work"):
            raise ValueError("mixed-media composite work budget exceeded")

    def lift(self):
        self.lifts += 1
        if self.lifts > MIXED_MEDIA_CONTRACT.value("max_lift_pairs"):
            raise ValueError("mixed-media selective lift pair budget exceeded")


def validate_mixed_stroke(stroke):
    if (not 0 < stroke.width <= MAX_WIDTH or len(stroke.points) > MAX_PATH_POINTS
            or any(not math.isfinite(v) for p in stroke.points for v in p)
            or sum(math.dist(a, b) for a, b in zip(stroke.points, stroke.points[1:])) > 50000):
        raise ValueError("mixed-media graphite geometry budget exceeded")
    if is_eraser(stroke) and not is_explicit_path_eraser(stroke):
        raise ValueError("mixed-media accepts only explicit graphite path erasers")


class _GraphiteRun:
    def __init__(self, graphite, budget, kwargs):
        self.image = None
        self.bounds = None
        self.graphite = graphite
        self.budget = budget
        self.kwargs = kwargs

    def deposit(self, bounds, patch):
        if not _area(bounds):
            return
        if patch.size != (bounds[2] - bounds[0], bounds[3] - bounds[1]):
            raise ValueError("invalid graphite patch bounds")
        self.budget.reserve(_area(bounds))
        combined = bounds if self.bounds is None else _union(self.bounds, bounds)
        if combined != self.bounds:
            self.budget.reserve(_area(combined))
            grown = Image.new("RGBA", (combined[2] - combined[0], combined[3] - combined[1]),
                              (*self.graphite, 0))
            if self.image is not None:
                grown.paste(self.image, (self.bounds[0] - combined[0], self.bounds[1] - combined[1]))
                self.image.close()
            self.image, self.bounds = grown, combined
        self.image.alpha_composite(patch, dest=(bounds[0] - self.bounds[0], bounds[1] - self.bounds[1]))

    def lift(self, stroke):
        if self.image is not None:
            self.budget.lift()
            erase_local(self.image, stroke, origin=self.bounds[:2],
                        reserve_work=self.budget.reserve, **self.kwargs)

    def flush(self, canvas, future_lifts):
        if self.image is not None:
            for stroke in future_lifts:
                self.lift(stroke)
            self.budget.reserve(_area(self.bounds))
            canvas.alpha_composite(self.image, dest=self.bounds[:2])
            self.close()

    def close(self):
        if self.image is not None:
            self.image.close()
        self.image = self.bounds = None


def render_mixed_image(ir, *, background, scale, supersample, graphite, grade=None,
                       renderer_version=MIXED_MEDIA_CONTRACT.renderer_version):
    if getattr(ir, "layer_document", None) is not None:
        from .document import render_document_image
        return render_document_image(ir, background=background, scale=scale,
                                     supersample=supersample, graphite=graphite,
                                     grade=grade, renderer_version=renderer_version)
    with _render_mixed_working(ir, background=background, scale=scale,
                               supersample=supersample, graphite=graphite,
                               grade=grade, renderer_version=renderer_version) as canvas:
        return canvas.resize((ir.width * scale, ir.height * scale), Image.Resampling.LANCZOS)


def _render_mixed_working(ir, *, background, scale, supersample, graphite, grade=None,
                          renderer_version=MIXED_MEDIA_CONTRACT.renderer_version,
                          ordered_elements=None, budget=None):
    from .pencil import _render_working_image, load_contact_profile, prepare_stroke, build_patch
    if ir.media_contract != MIXED_HISTORY_CONTRACT:
        raise ValueError("mixed-media renderer requires an explicit mixed history")
    factor = validate_mixed_raster_budget(ir.width, ir.height, supersample, scale)
    ordered = (sorted(ir.ordered_elements(), key=lambda item: item.layer)
               if ordered_elements is None else tuple(ordered_elements))
    for item in ordered:
        if isinstance(item, Stroke):
            validate_mixed_stroke(item)
    # Preserve the exact normalized-v3 graphite-only rendering, including lifts.
    ink_elements = [item for item in ordered if isinstance(item, InkElement)]
    if not ink_elements:
        legacy_view = StrokeIR(ir.width, ir.height,
                               ir.strokes if ordered_elements is None else list(ordered), ir.metadata)
        return _render_working_image(legacy_view, background=background, scale=scale,
                                     supersample=supersample, graphite=graphite, grade=grade,
                                     renderer_version=CONTACT_WIDTH_CONTRACT.renderer_version,
                                     ordered_elements=None if ordered_elements is None else ordered,
                                     budget=budget)
    hi_size = (ir.width * factor, ir.height * factor)
    for item in ink_elements:
        if isinstance(item.mark,Screentone) and renderer_version!=SCREENTONE_CONTRACT.renderer_version:
            raise ValueError("screentone requires its explicit mixed-media renderer contract")
        if isinstance(item.mark,StyledInkPath) and renderer_version not in (
                STYLED_INK_CONTRACT.renderer_version,SCREENTONE_CONTRACT.renderer_version):
            raise ValueError("styled ink requires its explicit mixed-media renderer contract")
        validate_ink_work(item.mark, factor=factor, hi_size=hi_size)
    tooth, paper_scale, paper_seed = paper_settings(ir)
    kwargs = dict(factor=float(factor), hi_size=hi_size, tooth=tooth,
                  paper_scale=paper_scale, paper_seed=paper_seed)
    contact = load_contact_profile(CONTACT_WIDTH_CONTRACT.renderer_version)
    graphite = tuple(int(v) for v in graphite)
    budget = _Budget() if budget is None else budget
    budget.reserve(hi_size[0] * hi_size[1])
    lifts = [(i, item) for i, item in enumerate(ordered)
             if isinstance(item, Stroke) and is_eraser(item)]
    indices = [i for i, _ in lifts]
    run = _GraphiteRun(graphite, budget, kwargs)
    canvas = Image.new("RGBA", hi_size, background)
    try:
        for i, item in enumerate(ordered):
            if isinstance(item, InkElement):
                run.flush(canvas, (s for _, s in lifts[bisect_right(indices, i):]))
                bounds, patch = build_ink_patch(item.mark, factor=factor, hi_size=hi_size)
                with patch:
                    if _area(bounds):
                        budget.reserve(_area(bounds))
                        canvas.alpha_composite(patch, dest=bounds[:2])
            elif is_eraser(item):
                run.lift(item)
            else:
                bounds, patch = build_patch(prepare_stroke(item, grade, contact),
                                            graphite=graphite, profile=contact, **kwargs)
                with patch:
                    run.deposit(bounds, patch)
        run.flush(canvas, ())
        return canvas
    except BaseException:
        canvas.close()
        raise
    finally:
        run.close()
