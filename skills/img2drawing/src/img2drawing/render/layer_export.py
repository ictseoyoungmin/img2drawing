"""Editable layer PNG/OpenRaster exports with an exact canonical merged image.

Layer PNGs are resized separately and retain raw opacity and hidden content.
Their recomposition is measured against the canonical composite-then-resize
image; the two operations are not generally pixel-equivalent.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory
import xml.etree.ElementTree as ET
import zipfile

import numpy as np
from PIL import Image

from ..core.digest import sha256_file
from ..inspection import drawing_state_hash
from .document import (
    DOCUMENT_COMPOSITING_CONTRACT, _DocumentRenderer, _apply_opacity,
    document_render_mode, validate_document_work,
)
from .pencil import render_image


LAYER_EXPORT_SCHEMA = "img2drawing.layer_export.v1"
_RESAMPLING_NOTE = (
    "The merged image is the exact canonical render. Paint-layer PNGs are "
    "independently downsampled, so recompositing them can differ from compositing "
    "at working resolution and then downsampling. Neutral legacy conversion "
    "also preserves the original renderer's paper-compositing rounding. The "
    "reported delta uses this package's RGBA8 normal compositor; external "
    "editors may use different rounding or color management."
)


@dataclass
class LayerExport:
    path: Path
    manifest_path: Path
    manifest: dict

    @property
    def canonical_pixel_sha256(self):
        return self.manifest["canonical"]["pixel_sha256"]

    @property
    def recomposed_pixel_sha256(self):
        return self.manifest["recomposition"]["pixel_sha256"]

    @property
    def recomposition_exact(self):
        return self.manifest["recomposition"]["exact"]

    @property
    def differing_pixels(self):
        return self.manifest["recomposition"]["differing_pixels"]

    @property
    def max_channel_error(self):
        return self.manifest["recomposition"]["max_channel_error"]

    @property
    def layer_count(self):
        return len(self.manifest["layers"])

    def to_dict(self):
        return {"path": str(self.path), "manifest_path": str(self.manifest_path),
                "canonical_pixel_sha256": self.canonical_pixel_sha256,
                "recomposed_pixel_sha256": self.recomposed_pixel_sha256,
                "recomposition_exact": self.recomposition_exact,
                "differing_pixels": self.differing_pixels,
                "max_channel_error": self.max_channel_error,
                "layer_count": self.layer_count}


def _pixel_digest(image):
    return hashlib.sha256(image.tobytes()).hexdigest()


def _save_png(image, root, name):
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, format="PNG", interlace=0)
    return {"file": name, "png_sha256": sha256_file(path),
            "pixel_sha256": _pixel_digest(image), "mode": image.mode,
            "width": image.width, "height": image.height}


def _recompose(document, root, sources, size, background):
    """Composite actual exported PNG bytes with their saved node properties."""

    def node_image(node):
        if node.kind == "paint":
            with Image.open(root / sources[node.layer_id]) as source:
                image = source.convert("RGBA")
        else:
            image = Image.new("RGBA", size, (0, 0, 0, 0))
            try:
                children(image, node.layer_id)
            except BaseException:
                image.close()
                raise
        _apply_opacity(image, node.opacity)
        return image

    def children(canvas, parent=None):
        for node in document.children(parent):
            if not node.visible or node.opacity == 0.0:
                continue
            with node_image(node) as layer:
                canvas.alpha_composite(layer)

    image = Image.new("RGBA", size, (0, 0, 0, 0))
    try:
        if background is not None:
            with Image.open(root / background["file"]) as paper:
                image.alpha_composite(paper)
        children(image)
        return image
    except BaseException:
        image.close()
        raise


def _difference(canonical, recomposed):
    count = maximum = total = 0
    for top in range(0, canonical.height, 128):
        box = (0, top, canonical.width, min(canonical.height, top + 128))
        with canonical.crop(box) as a, recomposed.crop(box) as b:
            delta = np.abs(np.asarray(a, dtype=np.int16) - np.asarray(b, dtype=np.int16))
            count += int(np.any(delta != 0, axis=2).sum())
            maximum = max(maximum, int(delta.max()))
            total += int(delta.sum())
    return {"exact": count == 0, "differing_pixels": count,
            "max_channel_error": maximum,
            "mean_absolute_channel_error": total / (canonical.width * canonical.height * 4),
            "pixel_sha256": _pixel_digest(recomposed), "comparison": "RGBA8",
            "fidelity_note": _RESAMPLING_NOTE}


def _stack_xml(document, sources, size, background):
    """OpenRaster 0.0.6: first child is uppermost; only non-root stacks have properties."""

    image = ET.Element("image", version="0.0.6", w=str(size[0]), h=str(size[1]))
    root = ET.SubElement(image, "stack")

    def children(xml_parent, parent=None):
        for node in reversed(document.children(parent)):
            attrs = {"name": node.name, "opacity": str(node.opacity),
                     "visibility": "visible" if node.visible else "hidden",
                     "composite-op": "svg:src-over"}
            if node.kind == "group":
                attrs["isolation"] = "isolate"
                children(ET.SubElement(xml_parent, "stack", attrs), node.layer_id)
            else:
                attrs.update(src=sources[node.layer_id], x="0", y="0")
                # Standard edit-locking extension applies to layers. Inherited
                # group locks are carried to leaves; the native tree stays in JSON.
                if document.effective_locked(node.layer_id):
                    attrs["edit-locked"] = "true"
                if node.layer_id == document.active_layer_id:
                    attrs["selected"] = "true"
                ET.SubElement(xml_parent, "layer", attrs)

    children(root)
    if background is not None:
        ET.SubElement(root, "layer", name="Paper", src=background["file"],
                      x="0", y="0", opacity="1.0", visibility="visible",
                      **{"composite-op": "svg:src-over", "edit-locked": "true"})
    return ET.tostring(image, encoding="utf-8", xml_declaration=True)


def _write_bundle(ir, profile, root, *, export_format):
    validate_document_work(ir, profile)
    prepared = profile.prepared_ir(ir)
    kwargs = profile.renderer_kwargs()
    renderer = _DocumentRenderer(prepared, **kwargs)
    document = renderer.document
    sources, layers = {}, []
    for index, node in enumerate(renderer.paint_nodes(), 1):
        name = f"data/layer-{index:04d}.png"
        with renderer.raw_layer_image(node.layer_id) as image:
            record = _save_png(image, root, name)
        sources[node.layer_id] = name
        layers.append({"layer_id": node.layer_id, "name": node.name,
                       "node_opacity_baked": False, "visibility_baked": False,
                       "element_ids": list(document.members[node.layer_id]), **record})
    background = None
    if profile.background_rgba[3] != 0:
        with Image.new("RGBA", renderer.out_size, profile.background_rgba) as paper:
            background = _save_png(paper, root, "data/background.png")
    with render_image(prepared, **kwargs) as canonical:
        canonical_record = _save_png(canonical, root, "mergedimage.png")
        canonical_record["render_mode"] = document_render_mode(ir)
        with _recompose(document, root, sources, renderer.out_size, background) as recomposed:
            recomposition = _difference(canonical, recomposed)
        with canonical.copy() as thumbnail:
            thumbnail.thumbnail((256, 256), Image.Resampling.LANCZOS)
            _save_png(thumbnail, root, "Thumbnails/thumbnail.png")
    (root / "stack.xml").write_bytes(_stack_xml(document, sources, renderer.out_size, background))
    manifest = {
        "schema": LAYER_EXPORT_SCHEMA, "format": export_format,
        "drawing_state_hash": drawing_state_hash(ir),
        "render_profile": profile.to_dict(), "render_profile_digest": profile.digest(),
        "document": document.to_dict(),
        "compositing_contract": DOCUMENT_COMPOSITING_CONTRACT.to_dict(),
        "compositing_contract_digest": DOCUMENT_COMPOSITING_CONTRACT.digest(),
        "canonical": canonical_record, "layers": layers, "background": background,
        "recomposition": recomposition,
        "native_editability": "Raster layers are editable; authored geometry and replay require the native checkpoint.",
    }
    (root / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    return manifest


def _require_new(path):
    if path.exists() or path.is_symlink():
        raise FileExistsError(f"layer export destination already exists: {path}")


def export_layer_pngs(ir, profile, out_dir):
    """Write a new PNG bundle directory; do not mutate or overwrite authored work."""

    target = Path(out_dir)
    _require_new(target)
    validate_document_work(ir, profile)
    target.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix=".img2drawing-layers-", dir=target.parent) as temporary:
        staged = Path(temporary) / "bundle"
        staged.mkdir()
        manifest = _write_bundle(ir, profile, staged, export_format="png_layers")
        # Reserve the requested directory exclusively, then move only our files.
        target.mkdir()
        try:
            for path in staged.iterdir():
                path.rename(target / path.name)
        except BaseException:
            shutil.rmtree(target)
            raise
    return LayerExport(target, target / "manifest.json", manifest)


def _zip_file(archive, source, name, *, stored=False):
    info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_STORED if stored else zipfile.ZIP_DEFLATED
    info.create_system = 3
    info.external_attr = 0o100644 << 16
    with archive.open(info, "w") as destination:
        with source.open("rb") as stream:
            shutil.copyfileobj(stream, destination)


def export_openraster(ir, profile, path):
    """Write a new standards-shaped ORA plus a readable external fidelity manifest."""

    target = Path(path)
    if target.suffix.lower() != ".ora":
        raise ValueError("OpenRaster output must use .ora")
    manifest_path = target.with_suffix(".layers.json")
    _require_new(target)
    _require_new(manifest_path)
    validate_document_work(ir, profile)
    target.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix=".img2drawing-ora-", dir=target.parent) as temporary:
        root = Path(temporary) / "bundle"
        root.mkdir()
        manifest = _write_bundle(ir, profile, root, export_format="openraster")
        (root / "mimetype").write_bytes(b"image/openraster")
        staged = Path(temporary) / "drawing.ora"
        with zipfile.ZipFile(staged, "w", allowZip64=True) as archive:
            _zip_file(archive, root / "mimetype", "mimetype", stored=True)
            for member in sorted(root.rglob("*")):
                if member.is_file() and member.name != "mimetype":
                    _zip_file(archive, member, member.relative_to(root).as_posix())
        # Hard links publish completed files without overwriting a raced target.
        os.link(staged, target)
        try:
            os.link(root / "manifest.json", manifest_path)
        except BaseException:
            target.unlink()
            raise
    return LayerExport(target, manifest_path, manifest)


__all__ = ["LAYER_EXPORT_SCHEMA", "LayerExport", "export_layer_pngs", "export_openraster"]
