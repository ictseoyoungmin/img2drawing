"""One-call, stage-free inspection sheet generation."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
import shutil
from typing import Any, Mapping, Sequence

from PIL import Image, ImageChops, ImageDraw

from .measure import drawing_state_hash
from .model import GroundGuide, Grid, PlumbLine, ROI, Registration


_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_BACKGROUND = (247, 246, 242)
_TEXT = (35, 35, 35)


def _portable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _portable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_portable(item) for item in value]
    if isinstance(value, Path):
        return value.name
    if hasattr(value, "to_dict"):
        return _portable(value.to_dict())
    return value


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _fit(image: Image.Image, box: tuple[int, int]) -> Image.Image:
    fitted = image.copy()
    fitted.thumbnail(box, Image.Resampling.LANCZOS)
    return fitted


def _tile(image: Image.Image, label: str, size: tuple[int, int]) -> Image.Image:
    width, height = size
    tile = Image.new("RGB", size, _BACKGROUND)
    fitted = _fit(image.convert("RGB"), (width - 24, height - 58))
    tile.paste(fitted, ((width - fitted.width) // 2, 46 + (height - 46 - fitted.height) // 2))
    ImageDraw.Draw(tile).text((12, 14), label, fill=_TEXT)
    return tile


def _registered_drawing(drawing: Image.Image, registration: Registration) -> Image.Image:
    scale_x, scale_y = registration.scale
    offset_x, offset_y = registration.offset
    # PIL's affine transform maps each output subject pixel back to the input
    # canvas pixel.  This is a display mapping only; no drawing geometry moves.
    data = (
        scale_x,
        0.0,
        offset_x,
        0.0,
        scale_y,
        offset_y,
    )
    return drawing.transform(
        registration.subject_size,
        Image.Transform.AFFINE,
        data,
        resample=Image.Resampling.BICUBIC,
        fillcolor=(255, 255, 255),
    )


def _contrast_overlay(
    subject: Image.Image,
    registered: Image.Image,
    *,
    subject_dim: float,
) -> Image.Image:
    white = Image.new("RGB", subject.size, (255, 255, 255))
    faded_subject = Image.blend(subject, white, 1.0 - subject_dim)
    drawing_gray = registered.convert("L")
    ink_alpha = ImageChops.invert(drawing_gray).point(lambda value: min(245, int(value * 0.92)))

    # Cyan is reserved for ink over dark subject pixels; red is used elsewhere.
    # The two-channel treatment keeps a dark photographic region from hiding a
    # drawing stroke without pretending that either colour is a score.
    dark_subject = subject.convert("L").point(lambda value: 255 if value < 112 else 0)
    red = Image.new("RGB", subject.size, (224, 38, 52))
    cyan = Image.new("RGB", subject.size, (0, 188, 210))
    ink_color = Image.composite(cyan, red, dark_subject).convert("RGBA")
    ink_color.putalpha(ink_alpha)
    result = faded_subject.convert("RGBA")
    result.alpha_composite(ink_color)
    return result.convert("RGB")


def _draw_overlay_annotations(
    image: Image.Image,
    *,
    grid: Grid | None,
    guides: Sequence[PlumbLine | GroundGuide],
    subject_size: tuple[int, int],
) -> Image.Image:
    result = image.copy().convert("RGB")
    draw = ImageDraw.Draw(result)
    width, height = subject_size
    if grid is not None:
        left, top, right, bottom = grid.resolved_bounds(subject_size)
        for index in range(grid.columns + 1):
            x = left + (right - left) * index / grid.columns
            draw.line((x, top, x, bottom), fill=(255, 203, 0), width=2)
        for index in range(grid.rows + 1):
            y = top + (bottom - top) * index / grid.rows
            draw.line((left, y, right, y), fill=(255, 203, 0), width=2)
    for guide in guides:
        if isinstance(guide, PlumbLine):
            x = guide.anchor[0]
            draw.line((x, 0, x, height), fill=guide.color, width=guide.width)
        else:
            left, right = (0.0, float(width)) if guide.x_range is None else guide.x_range
            draw.line((left, guide.y, right, guide.y), fill=guide.color, width=guide.width)
    return result


def _draw_roi_boxes(image: Image.Image, rois: Sequence[ROI]) -> Image.Image:
    result = image.copy().convert("RGB")
    draw = ImageDraw.Draw(result)
    for index, roi in enumerate(rois, start=1):
        draw.rectangle(roi.box, outline=(255, 238, 0), width=3)
        left, top, _, _ = roi.box
        draw.text((left + 4, top + 4), f"{index}: {roi.label}", fill=(255, 238, 0))
    return result


@dataclass(frozen=True)
class InspectionSheet:
    """A portable inspection product bound to one authored drawing digest."""

    subject: Path
    drawing: Path
    subject_sha256: str
    drawing_artifact_sha256: str
    drawing_state_hash: str
    registration: Registration
    rois: tuple[ROI, ...] = ()
    overlay: str = "contrast"
    subject_dim: float = 0.35
    grid: Grid | None = None
    guides: tuple[PlumbLine | GroundGuide, ...] = ()
    measurements: tuple[Any, ...] = ()
    evidence_policy: Mapping[str, Any] | None = None

    @classmethod
    def create(
        cls,
        *,
        subject: str | Path,
        drawing: str | Path,
        drawing_state_hash: str | None = None,
        drawing_ir: Any | None = None,
        registration: Registration,
        rois: Sequence[ROI] = (),
        overlay: str = "contrast",
        subject_dim: float = 0.35,
        grid: Grid | bool | None = None,
        guides: Sequence[PlumbLine | GroundGuide] = (),
        measurements: Sequence[Any] = (),
        evidence_policy: Mapping[str, Any] | None = None,
        out_dir: str | Path | None = None,
    ) -> "InspectionSheet":
        subject_path = Path(subject)
        drawing_path = Path(drawing)
        if not subject_path.is_file():
            raise FileNotFoundError(subject_path)
        if not drawing_path.is_file():
            raise FileNotFoundError(drawing_path)
        if overlay != "contrast":
            raise ValueError("the B02 overlay mode is 'contrast'")
        subject_dim = float(subject_dim)
        if not 0.0 < subject_dim <= 1.0:
            raise ValueError("subject_dim must be in (0,1]")

        with Image.open(subject_path) as subject_image, Image.open(drawing_path) as drawing_image:
            subject_size = subject_image.size
            drawing_size = drawing_image.size
        if subject_size != registration.subject_size:
            raise ValueError(
                f"subject image size {subject_size} does not match registration {registration.subject_size}"
            )
        if drawing_size != registration.canvas_size:
            raise ValueError(
                f"drawing image size {drawing_size} does not match registration {registration.canvas_size}"
            )
        grid_spec = None if grid is False else grid
        if grid_spec is not None and not isinstance(grid_spec, Grid):
            raise TypeError("grid must be a Grid, False, or None")
        for roi in rois:
            roi.validate_for_size(subject_size)
        if grid_spec is not None:
            grid_spec.resolved_bounds(subject_size)
        for guide in guides:
            if isinstance(guide, PlumbLine) and not 0.0 <= guide.anchor[0] <= subject_size[0]:
                raise ValueError("plumb line anchor must lie within subject width")
            if isinstance(guide, GroundGuide) and not 0.0 <= guide.y <= subject_size[1]:
                raise ValueError("ground guide y must lie within subject height")
            if isinstance(guide, GroundGuide) and guide.x_range is not None:
                if guide.x_range[0] < 0.0 or guide.x_range[1] > subject_size[0]:
                    raise ValueError("ground guide x_range must lie within subject width")

        if drawing_ir is not None:
            computed_hash = drawing_state_hash_from_ir(drawing_ir)
            if drawing_state_hash is not None and drawing_state_hash != computed_hash:
                raise ValueError("drawing_state_hash does not match drawing_ir")
            drawing_state_hash = computed_hash
        if drawing_state_hash is None:
            raise ValueError("drawing_state_hash or drawing_ir is required")
        if not _SHA256.fullmatch(str(drawing_state_hash)):
            raise ValueError("drawing_state_hash must be a lowercase SHA-256 digest")
        subject_sha256 = _sha256_file(subject_path)
        drawing_artifact_sha256 = _sha256_file(drawing_path)

        sheet = cls(
            subject=subject_path,
            drawing=drawing_path,
            subject_sha256=subject_sha256,
            drawing_artifact_sha256=drawing_artifact_sha256,
            drawing_state_hash=str(drawing_state_hash),
            registration=registration,
            rois=tuple(rois),
            overlay=overlay,
            subject_dim=subject_dim,
            grid=grid_spec,
            guides=tuple(guides),
            measurements=tuple(measurements),
            evidence_policy=None if evidence_policy is None else _portable(dict(evidence_policy)),
        )
        if out_dir is not None:
            sheet.write(out_dir)
        return sheet

    def to_dict(self) -> dict[str, Any]:
        payload = {
            "format": "inspection-sheet/v1",
            "inputs": {"subject": self.subject.name, "drawing": self.drawing.name},
            "subject_sha256": self.subject_sha256,
            "drawing_artifact_sha256": self.drawing_artifact_sha256,
            "drawing_state_hash": self.drawing_state_hash,
            "registration": self.registration.to_dict(),
            "rois": [roi.to_dict() for roi in self.rois],
            "overlay": self.overlay,
            "subject_dim": self.subject_dim,
            "grid": None if self.grid is None else self.grid.to_dict(self.registration.subject_size),
            "guides": [guide.to_dict() for guide in self.guides],
            "measurements": [_portable(item) for item in self.measurements],
            "evidence_only": True,
        }
        if self.evidence_policy is not None:
            payload["evidence_policy"] = _portable(self.evidence_policy)
        return payload

    def write(self, out_dir: str | Path) -> dict[str, Path]:
        output = Path(out_dir)
        output.mkdir(parents=True, exist_ok=True)
        if _sha256_file(self.subject) != self.subject_sha256:
            raise ValueError("subject changed after sheet creation")
        if _sha256_file(self.drawing) != self.drawing_artifact_sha256:
            raise ValueError("drawing artifact changed after sheet creation")
        raw_path = output / "raw_drawing.png"
        if self.drawing.resolve() != raw_path.resolve():
            shutil.copyfile(self.drawing, raw_path)

        with Image.open(self.subject) as subject_source, Image.open(self.drawing) as drawing_source:
            subject = subject_source.convert("RGB")
            drawing = drawing_source.convert("RGB")
        if subject.size != self.registration.subject_size or drawing.size != self.registration.canvas_size:
            raise ValueError("source image dimensions changed after sheet creation")

        registered = _registered_drawing(drawing, self.registration)
        contrast = _contrast_overlay(subject, registered, subject_dim=self.subject_dim)
        contrast = _draw_overlay_annotations(
            contrast,
            grid=self.grid,
            guides=self.guides,
            subject_size=self.registration.subject_size,
        )
        registered_path = output / "registered_drawing.png"
        contrast_path = output / "contrast_overlay.png"
        registered.save(registered_path)
        contrast.save(contrast_path)

        tile_width, tile_height = 360, 330
        top_tiles = [
            _tile(subject, "SUBJECT", (tile_width, tile_height)),
            _tile(drawing, "DRAWING RAW", (tile_width, tile_height)),
            _tile(_draw_roi_boxes(contrast, self.rois), "CONTRAST OVERLAY", (tile_width, tile_height)),
        ]
        columns = max(1, min(2, len(self.rois)))
        margin = 18
        top_width = len(top_tiles) * tile_width + (len(top_tiles) + 1) * margin
        roi_rows = (len(self.rois) + columns - 1) // columns
        total_width = max(top_width, columns * tile_width + (columns + 1) * margin)
        total_height = margin + tile_height + margin
        if roi_rows:
            total_height += roi_rows * tile_height + (roi_rows + 1) * margin
        sheet = Image.new("RGB", (total_width, total_height), _BACKGROUND)
        for index, tile in enumerate(top_tiles):
            sheet.paste(tile, (margin + index * (tile_width + margin), margin))
        for index, roi in enumerate(self.rois):
            left, top, right, bottom = map(int, map(round, roi.box))
            crop = contrast.crop((left, top, right, bottom))
            enlarged = crop.resize(
                (max(1, round(crop.width * roi.scale)), max(1, round(crop.height * roi.scale))),
                Image.Resampling.NEAREST,
            )
            label = f"ROI {roi.label}  box=({left},{top},{right},{bottom})  scale={roi.scale:g}x"
            tile = _tile(enlarged, label, (tile_width, tile_height))
            row, column = divmod(index, columns)
            x = margin + column * (tile_width + margin)
            y = margin + tile_height + 2 * margin + row * (tile_height + margin)
            sheet.paste(tile, (x, y))
        sheet_path = output / "inspection_sheet.png"
        sheet.save(sheet_path)

        measurement_payload = {
            "format": "inspection-measurements/v1",
            "subject_sha256": self.subject_sha256,
            "drawing_artifact_sha256": self.drawing_artifact_sha256,
            "drawing_state_hash": self.drawing_state_hash,
            "measurements": [_portable(item) for item in self.measurements],
        }
        measurements_path = output / "measurements.json"
        measurements_path.write_text(
            json.dumps(measurement_payload, indent=2, ensure_ascii=False, sort_keys=True, allow_nan=False),
            encoding="utf-8",
        )
        artifacts = {
            "sheet": "inspection_sheet.png",
            "raw_drawing": "raw_drawing.png",
            "registered_drawing": "registered_drawing.png",
            "contrast_overlay": "contrast_overlay.png",
            "manifest": "inspection.json",
            "measurements": "measurements.json",
        }
        manifest = {**self.to_dict(), "artifacts": artifacts}
        manifest_path = output / "inspection.json"
        manifest_path.write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True, allow_nan=False),
            encoding="utf-8",
        )
        return {
            "sheet": sheet_path,
            "raw_drawing": raw_path,
            "registered_drawing": registered_path,
            "contrast_overlay": contrast_path,
            "manifest": manifest_path,
            "measurements": measurements_path,
        }


def drawing_state_hash_from_ir(ir: Any) -> str:
    """Named adapter used by ``InspectionSheet.create`` for readability."""

    return drawing_state_hash(ir)


__all__ = ["InspectionSheet"]
