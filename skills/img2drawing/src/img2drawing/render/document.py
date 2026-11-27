"""Opt-in document composition without changing authored material identities.

Normal paint layers and groups are isolated at working resolution. Their own
opacity scales the completed alpha once, rounded half up; the complete canvas
is then downsampled once. A neutral single content layer retains the original
renderer exactly, including mixed-media integer rounding against the paper.
"""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import replace
import math

from PIL import Image

from ..core.ir import Stroke
from ..core.layers import LAYER_COMPOSITING
from .contract import MIXED_MEDIA_CONTRACT, RendererContract, validate_mixed_raster_budget


MAX_LIVE_SURFACE_PIXELS = 96 * 1024 * 1024
DOCUMENT_COMPOSITING_CONTRACT = RendererContract(
    renderer_id="img2drawing-layer-document",
    renderer_version=LAYER_COMPOSITING,
    parameters=tuple(sorted({
        "alpha_opacity": "round-half-up-completed-node-alpha-v1",
        "blend_mode": "normal-pillow-rgba8-source-over-v1",
        "element_order": "explicit-document-member-order-material-fields-unchanged-v1",
        "eraser_scope": "earlier-graphite-in-own-paint-layer-v1",
        "group_isolation": "transparent-black-isolated-v1",
        "identity_compatibility": "identity_single_layer_legacy_v1",
        "resampling": "root-paper-then-single-lanczos-v1",
        "max_live_surface_pixels": MAX_LIVE_SURFACE_PIXELS,
        "max_working_pixels": MIXED_MEDIA_CONTRACT.value("max_working_pixels"),
        "max_factor": MIXED_MEDIA_CONTRACT.value("max_factor"),
        "max_composite_work": MIXED_MEDIA_CONTRACT.value("max_composite_work"),
        "max_lift_pairs": MIXED_MEDIA_CONTRACT.value("max_lift_pairs"),
    }.items())),
)


def _element_id(element):
    return element.stroke_id if isinstance(element, Stroke) else element.element_id


def _document_inputs(ir):
    document = getattr(ir, "layer_document", None)
    if document is None:
        raise ValueError("layer rendering/export requires an explicitly enabled layer document")
    elements = tuple(ir.ordered_elements())
    ids = tuple(_element_id(element) for element in elements)
    if any(not isinstance(sid, str) or not sid for sid in ids) or len(set(ids)) != len(ids):
        raise ValueError("layer document requires distinct current element identities")
    document.validate_elements(ids)
    return document, elements, dict(zip(ids, elements))


def _legacy_identity(document, elements):
    nonempty = [node for node in document.layers
                if node.kind == "paint" and document.members[node.layer_id]]
    if not nonempty:
        return not elements
    if len(nonempty) != 1:
        return False
    node = nonempty[0]
    expected = tuple(_element_id(item) for item in sorted(elements, key=lambda item: item.layer))
    if tuple(document.members[node.layer_id]) != expected:
        return False
    while node is not None:
        if not node.visible or node.opacity != 1.0 or node.blend_mode != "normal":
            return False
        node = None if node.parent_id is None else document.node(node.parent_id)
    return True


def document_render_mode(ir):
    """Describe the authoritative route, including the exact conversion branch."""

    document, elements, _ = _document_inputs(ir)
    return ("identity_single_layer_legacy_v1" if _legacy_identity(document, elements)
            else LAYER_COMPOSITING)


def validate_document_size(width, height, *, scale=1, supersample=4):
    """Validate the opt-in working raster without allocating or rendering it."""

    try:
        return validate_mixed_raster_budget(width, height, supersample, scale)
    except ValueError as exc:
        raise ValueError("layer document working raster budget exceeded") from exc


def _validate_work(ir, *, scale, supersample):
    document, elements, by_id = _document_inputs(ir)
    factor = validate_document_size(ir.width, ir.height, scale=scale, supersample=supersample)
    # Mixed run growth can temporarily hold canvas, old run, grown run and
    # patch. Each enclosing isolated group holds one additional full surface.
    surfaces = 4
    if not _legacy_identity(document, elements):
        for node in document.layers:
            if node.kind != "paint" or not document.members[node.layer_id]:
                continue
            ancestors = 0
            parent = node.parent_id
            while parent is not None:
                ancestors += 1
                parent = document.node(parent).parent_id
            surfaces = max(surfaces, 5 + ancestors)
    if ir.width * ir.height * factor * factor * surfaces > MAX_LIVE_SURFACE_PIXELS:
        raise ValueError("layer document simultaneous surface budget exceeded")
    return document, elements, by_id, factor


def validate_document_work(ir, profile):
    """Preflight document membership and surface dimensions without rendering."""

    profile.validate_canvas(ir.width, ir.height)
    _validate_work(ir, scale=profile.output_scale, supersample=profile.supersample)


class _DocumentBudget:
    def __init__(self):
        self.work = 0
        self.lifts = 0
        self.live_pixels = 0

    def reserve(self, pixels):
        self.work += pixels
        if self.work > DOCUMENT_COMPOSITING_CONTRACT.value("max_composite_work"):
            raise ValueError("layer document composite work budget exceeded")

    def lift(self):
        self.lifts += 1
        if self.lifts > DOCUMENT_COMPOSITING_CONTRACT.value("max_lift_pairs"):
            raise ValueError("layer document graphite lift pair budget exceeded")

    @contextmanager
    def surfaces(self, pixels):
        if self.live_pixels + pixels > MAX_LIVE_SURFACE_PIXELS:
            raise ValueError("layer document simultaneous surface budget exceeded")
        self.live_pixels += pixels
        try:
            yield
        finally:
            self.live_pixels -= pixels


def _apply_opacity(image, opacity):
    """Scale a completed node's alpha in place; leave its RGB values unchanged."""

    if opacity != 1.0:
        table = [int(math.floor(alpha * opacity + 0.5)) for alpha in range(256)]
        with image.getchannel("A") as channel:
            with channel.point(table) as attenuated:
                image.putalpha(attenuated)


class _DocumentRenderer:
    """One bounded material context shared by composition or sequential export."""

    def __init__(self, ir, *, background, scale, supersample, graphite, grade=None,
                 renderer_version):
        document, elements, by_id, factor = _validate_work(
            ir, scale=scale, supersample=supersample)
        self.ir = ir
        self.document = document
        self.elements = elements
        self.by_id = by_id
        self.background = background
        self.hi_size = (ir.width * factor, ir.height * factor)
        self.out_size = (ir.width * scale, ir.height * scale)
        self.pixels = self.hi_size[0] * self.hi_size[1]
        self.budget = _DocumentBudget()
        self.kwargs = dict(scale=scale, supersample=supersample, graphite=graphite,
                           grade=grade, renderer_version=renderer_version)
        self.legacy_ir = replace(ir, layer_document=None)
        # Empty isolated subtrees are transparent identities. Keep their nodes
        # for editing/export, but allocate no surfaces while compositing them.
        self._content_nodes = set()
        for node in document.layers:
            if node.kind == "paint" and document.members[node.layer_id]:
                self._content_nodes.add(node.layer_id)
                self._content_nodes.update(parent.layer_id
                                           for parent in document.ancestors(node.layer_id))

    def paint_nodes(self):
        """Paint nodes in bottom-to-top depth-first document order."""

        def walk(parent=None):
            for node in self.document.children(parent):
                if node.kind == "paint":
                    yield node
                else:
                    yield from walk(node.layer_id)
        return walk()

    @contextmanager
    def _paint_surface(self, node):
        from .pencil import _render_working_image

        ordered = tuple(self.by_id[sid] for sid in self.document.members[node.layer_id])
        with self.budget.surfaces(4 * self.pixels):
            with _render_working_image(
                self.legacy_ir, background=(0, 0, 0, 0), ordered_elements=ordered,
                budget=self.budget, **self.kwargs,
            ) as image:
                yield image

    @contextmanager
    def _node_surface(self, node):
        if node.kind == "paint":
            with self._paint_surface(node) as image:
                if node.opacity != 1.0:
                    self.budget.reserve(self.pixels)
                    _apply_opacity(image, node.opacity)
                yield image
            return
        with self.budget.surfaces(self.pixels):
            self.budget.reserve(self.pixels)
            with Image.new("RGBA", self.hi_size, (0, 0, 0, 0)) as image:
                self._children(image, node.layer_id)
                if node.opacity != 1.0:
                    self.budget.reserve(self.pixels)
                    _apply_opacity(image, node.opacity)
                yield image

    def _children(self, canvas, parent=None):
        for node in self.document.children(parent):
            if not node.visible or node.opacity == 0.0 or node.layer_id not in self._content_nodes:
                continue
            with self._node_surface(node) as image:
                self.budget.reserve(self.pixels)
                canvas.alpha_composite(image)

    def image(self):
        from .pencil import _render_working_image

        if _legacy_identity(self.document, self.elements):
            with self.budget.surfaces(4 * self.pixels):
                with _render_working_image(self.legacy_ir, background=self.background,
                                           budget=self.budget, **self.kwargs) as image:
                    return image.resize(self.out_size, Image.Resampling.LANCZOS)
        with self.budget.surfaces(self.pixels):
            self.budget.reserve(self.pixels)
            with Image.new("RGBA", self.hi_size, self.background) as image:
                self._children(image)
                return image.resize(self.out_size, Image.Resampling.LANCZOS)

    def raw_layer_image(self, layer_id):
        """Return raw, independently resized paint RGBA, before node properties."""

        node = self.document.node(layer_id)
        if node.kind != "paint":
            raise ValueError("transparent layer PNGs require a paint layer")
        with self._paint_surface(node) as image:
            return image.resize(self.out_size, Image.Resampling.LANCZOS)


def render_document_image(ir, *, background, scale, supersample, graphite, grade=None,
                          renderer_version):
    """Render the complete document, preserving the declared conversion boundary."""

    return _DocumentRenderer(ir, background=background, scale=scale, supersample=supersample,
                             graphite=graphite, grade=grade,
                             renderer_version=renderer_version).image()


__all__ = [
    "DOCUMENT_COMPOSITING_CONTRACT", "MAX_LIVE_SURFACE_PIXELS",
    "document_render_mode", "render_document_image", "validate_document_size",
    "validate_document_work",
]
