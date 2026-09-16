"""Inspection-only visibility boost for agent-selected construction strokes.

The WIP guide view never mutates drawing history, stroke material, RenderProfile, or the
canonical inspection artifact. It is a derived visual aid over a *fresh* inspection's
``raw_drawing.png`` so an Agent can make provisional guides deliberately more legible while
working, then retire/soften/delete those authored marks normally before completion.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from PIL import Image, ImageDraw


WIP_GUIDE_STYLE_SCHEMA = "img2drawing.inspection.wip-guide-style.v1"
WIP_GUIDE_VIEW_SCHEMA = "img2drawing.inspection.wip-guide-view.v1"
DEFAULT_WIP_GUIDE_COLOR = (46, 122, 255)


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _rgb(value: Sequence[int]) -> tuple[int, int, int]:
    if len(value) != 3:
        raise ValueError("WIP guide color must contain exactly three RGB channels")
    channels = tuple(int(channel) for channel in value)
    if any(channel < 0 or channel > 255 for channel in channels):
        raise ValueError("WIP guide RGB channels must be in [0,255]")
    return channels


def _stroke_ids(values: Iterable[str]) -> tuple[str, ...]:
    result = tuple(str(value).strip() for value in values)
    if not result or any(not value for value in result):
        raise ValueError("WIP guide view requires at least one non-empty stroke_id")
    if len(set(result)) != len(result):
        raise ValueError("WIP guide stroke_ids must be unique")
    return result


@dataclass(frozen=True)
class WIPGuideStyle:
    """Portable display-only style for selected provisional strokes."""

    color: tuple[int, int, int] = DEFAULT_WIP_GUIDE_COLOR
    width_scale: float = 2.0
    opacity: float = 0.78

    def __post_init__(self) -> None:
        object.__setattr__(self, "color", _rgb(self.color))
        width_scale = float(self.width_scale)
        opacity = float(self.opacity)
        if not math.isfinite(width_scale) or not 1.0 <= width_scale <= 4.0:
            raise ValueError("WIP guide width_scale must be finite and in [1,4]")
        if not math.isfinite(opacity) or not 0.15 <= opacity <= 1.0:
            raise ValueError("WIP guide opacity must be finite and in [0.15,1]")
        object.__setattr__(self, "width_scale", width_scale)
        object.__setattr__(self, "opacity", opacity)

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "WIPGuideStyle":
        values = dict(payload)
        schema = values.pop("schema", WIP_GUIDE_STYLE_SCHEMA)
        if schema != WIP_GUIDE_STYLE_SCHEMA:
            raise ValueError(f"unsupported WIP guide style schema: {schema!r}")
        unknown = set(values) - {"color", "width_scale", "opacity"}
        if unknown:
            raise ValueError(f"unsupported WIP guide style fields: {sorted(unknown)}")
        return cls(
            color=tuple(values.get("color", DEFAULT_WIP_GUIDE_COLOR)),
            width_scale=float(values.get("width_scale", 2.0)),
            opacity=float(values.get("opacity", 0.78)),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": WIP_GUIDE_STYLE_SCHEMA,
            "color": list(self.color),
            "width_scale": self.width_scale,
            "opacity": self.opacity,
        }


@dataclass(frozen=True)
class WIPGuideView:
    """One derived guide-visibility artifact bound to a fresh canonical inspection."""

    path: Path
    manifest_path: Path
    inspection_id: str
    drawing_state_hash: str
    raw_drawing_sha256: str
    wip_view_sha256: str
    stroke_ids: tuple[str, ...]
    style: WIPGuideStyle

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": WIP_GUIDE_VIEW_SCHEMA,
            "inspection_id": self.inspection_id,
            "drawing_state_hash": self.drawing_state_hash,
            "raw_drawing_sha256": self.raw_drawing_sha256,
            "wip_view_sha256": self.wip_view_sha256,
            "stroke_ids": list(self.stroke_ids),
            "style": self.style.to_dict(),
            "display_only": True,
            "artifacts": {
                "view": self.path.name,
                "manifest": self.manifest_path.name,
            },
        }


def _inspection_record(session: Any, inspection_id: str | None) -> Mapping[str, Any]:
    history = tuple(session.inspection_history)
    if not history:
        raise ValueError("WIP guide view requires an existing fresh inspection")
    if inspection_id is None:
        record = history[-1]
    else:
        requested = str(inspection_id)
        matches = [item for item in history if str(item.get("inspection_id")) == requested]
        if len(matches) != 1:
            raise ValueError(f"unknown inspection_id: {requested}")
        record = matches[0]
    current_hash = str(session.drawing_state_hash())
    if str(record.get("drawing_state_hash")) != current_hash:
        raise ValueError("WIP guide view requires a fresh inspection of the current drawing")
    return record


def _confined_output(session: Any, inspection_id: str, out_dir: str | Path | None) -> Path:
    root = Path(session.output_dir).resolve()
    if out_dir is None:
        destination = root / "wip_views" / inspection_id
    else:
        requested = Path(out_dir)
        destination = requested if requested.is_absolute() else root / requested
        destination = destination.resolve()
    try:
        destination.relative_to(root)
    except ValueError as exc:
        raise ValueError("WIP guide view output must stay inside the session output directory") from exc
    return destination


def _view_key(
    inspection_id: str,
    drawing_state_hash: str,
    stroke_ids: Sequence[str],
    style: WIPGuideStyle,
) -> str:
    payload = {
        "inspection_id": inspection_id,
        "drawing_state_hash": drawing_state_hash,
        "stroke_ids": list(stroke_ids),
        "style": style.to_dict(),
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:16]


def render_wip_guides(
    session: Any,
    stroke_ids: Iterable[str],
    *,
    color: Sequence[int] = DEFAULT_WIP_GUIDE_COLOR,
    width_scale: float = 2.0,
    opacity: float = 0.78,
    inspection_id: str | None = None,
    out_dir: str | Path | None = None,
) -> WIPGuideView:
    """Render selected current strokes as a high-visibility WIP overlay.

    ``stroke_ids`` are explicit on purpose: the runtime does not infer which authored marks
    are provisional. The caller may choose any RGB color and bounded width/opacity boost.
    The canonical inspection and final drawing remain untouched.
    """

    selected_ids = _stroke_ids(stroke_ids)
    style = WIPGuideStyle(color=tuple(color), width_scale=width_scale, opacity=opacity)
    record = _inspection_record(session, inspection_id)
    inspection_id = str(record["inspection_id"])
    drawing_state_hash = str(record["drawing_state_hash"])
    root = Path(session.output_dir).resolve()
    manifest_path = (root / str(record["manifest"])).resolve()
    try:
        manifest_path.relative_to(root)
    except ValueError as exc:
        raise ValueError("inspection manifest escapes the session output directory") from exc
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    artifacts = manifest.get("artifacts") or {}
    raw_name = str(artifacts.get("raw_drawing", "")).strip()
    if not raw_name:
        raise ValueError("inspection has no canonical raw_drawing artifact")
    raw_path = (manifest_path.parent / raw_name).resolve()
    try:
        raw_path.relative_to(manifest_path.parent.resolve())
    except ValueError as exc:
        raise ValueError("inspection raw drawing escapes its immutable directory") from exc
    if not raw_path.is_file():
        raise FileNotFoundError(raw_path)
    raw_sha256 = _sha256_file(raw_path)
    expected_raw_sha256 = str(record.get("drawing_artifact_sha256") or manifest.get("drawing_artifact_sha256") or "")
    if expected_raw_sha256 and raw_sha256 != expected_raw_sha256:
        raise ValueError("inspection raw drawing no longer matches its recorded artifact digest")

    ir = session.current_ir()
    by_id = {str(stroke.stroke_id): stroke for stroke in ir.strokes if stroke.stroke_id is not None}
    missing = [stroke_id for stroke_id in selected_ids if stroke_id not in by_id]
    if missing:
        raise ValueError("WIP guide stroke_ids are not current authored strokes: " + ", ".join(missing))

    destination = _confined_output(session, inspection_id, out_dir)
    destination.mkdir(parents=True, exist_ok=True)
    view_key = _view_key(inspection_id, drawing_state_hash, selected_ids, style)
    view_path = destination / f"wip_guides-{view_key}.png"
    output_manifest = destination / f"wip_guides-{view_key}.json"

    with Image.open(raw_path) as source:
        base = source.convert("RGBA")
    if base.size != (int(ir.width), int(ir.height)):
        base.close()
        raise ValueError("inspection raw drawing size does not match current drawing canvas")
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay, "RGBA")
    alpha = int(round(style.opacity * 255.0))
    rgba = (*style.color, alpha)
    for stroke_id in selected_ids:
        stroke = by_id[stroke_id]
        points = [(float(x), float(y)) for x, y in stroke.points]
        if len(points) < 2:
            continue
        width = max(2, int(round(max(1.0, float(stroke.width)) * style.width_scale)))
        draw.line(points, fill=rgba, width=width, joint="curve")
    base.alpha_composite(overlay)
    base.convert("RGB").save(view_path)
    overlay.close()
    base.close()

    view = WIPGuideView(
        path=view_path,
        manifest_path=output_manifest,
        inspection_id=inspection_id,
        drawing_state_hash=drawing_state_hash,
        raw_drawing_sha256=raw_sha256,
        wip_view_sha256=_sha256_file(view_path),
        stroke_ids=selected_ids,
        style=style,
    )
    output_manifest.write_text(
        json.dumps(view.to_dict(), indent=2, ensure_ascii=False, sort_keys=True, allow_nan=False),
        encoding="utf-8",
    )
    return view


__all__ = [
    "DEFAULT_WIP_GUIDE_COLOR",
    "WIP_GUIDE_STYLE_SCHEMA",
    "WIP_GUIDE_VIEW_SCHEMA",
    "WIPGuideStyle",
    "WIPGuideView",
    "render_wip_guides",
]
