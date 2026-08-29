"""Pure, stage-free inspection measurements.

The functions in this module consume an explicit registration or image and
return descriptive evidence.  They do not infer correspondence, assign a
semantic judgement, or mutate a drawing object.
"""

from __future__ import annotations

from contextlib import contextmanager
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Iterator, Sequence

from PIL import Image

from .model import (
    GroundGuide,
    Grid,
    GridMeasurement,
    Measurement,
    PixelSample,
    PlumbLine,
    Point,
    PointMapping,
    Profile,
    Registration,
)


def _point(value: Sequence[float]) -> Point:
    if len(value) != 2:
        raise ValueError("point requires x,y")
    point = (float(value[0]), float(value[1]))
    if not all(math.isfinite(item) for item in point):
        raise ValueError("point coordinates must be finite")
    return point


def _jsonable(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, Path):
        return value.name
    if hasattr(value, "to_dict"):
        return _jsonable(value.to_dict())
    return value


def _strip_stage(value: Any) -> Any:
    """Remove workflow-stage labels from a drawing identity payload."""

    if isinstance(value, dict):
        return {
            key: _strip_stage(item)
            for key, item in value.items()
            if key not in {"stage", "stage_label", "workflow_stage", "history_cursor"}
        }
    if isinstance(value, list):
        return [_strip_stage(item) for item in value]
    return value


def drawing_state_payload(ir: Any) -> dict[str, Any]:
    """Return the stage-free authored drawing payload used by B02.

    This is an adapter over the existing ``StrokeIR`` representation.  The
    legacy session digest remains unchanged; B02 binds to this separate digest
    so a workflow-label edit does not create a new drawing identity.
    """

    if not hasattr(ir, "to_dict"):
        raise TypeError("drawing_state_payload expects a StrokeIR-like object")
    raw = _jsonable(ir.to_dict())
    payload = _strip_stage(raw)
    if not isinstance(payload, dict):
        raise TypeError("StrokeIR serialization must be a mapping")
    return payload


def drawing_state_hash(ir: Any) -> str:
    """Hash authored geometry/material state while ignoring workflow labels."""

    encoded = json.dumps(
        drawing_state_payload(ir),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


stage_free_drawing_state_hash = drawing_state_hash


def map_subject_to_canvas(registration: Registration, point: Sequence[float]) -> PointMapping:
    subject = _point(point)
    return PointMapping(subject=subject, canvas=registration.map_subject_to_canvas(subject))


def _points_in_space(
    points: Sequence[Sequence[float]],
    *,
    space: str,
    registration: Registration | None,
) -> tuple[Point, ...]:
    if space not in {"subject", "canvas"}:
        raise ValueError("measurement space must be subject or canvas")
    normalized = tuple(_point(point) for point in points)
    if space == "canvas" and registration is not None:
        return tuple(registration.map_subject_to_canvas(point) for point in normalized)
    return normalized


def point(point_value: Sequence[float], *, space: str = "subject") -> Measurement:
    normalized = _point(point_value)
    if space not in {"subject", "canvas"}:
        raise ValueError("point space must be subject or canvas")
    return Measurement(
        kind="point",
        value=list(normalized),
        coordinate_space=space,
        inputs={"point": list(normalized)},
        provenance={"operation": "read-only coordinate declaration"},
    )


def distance(
    start: Sequence[float],
    end: Sequence[float],
    *,
    space: str = "subject",
    registration: Registration | None = None,
) -> Measurement:
    a, b = _points_in_space((start, end), space=space, registration=registration)
    value = math.hypot(b[0] - a[0], b[1] - a[1])
    return Measurement(
        kind="distance",
        value=value,
        coordinate_space=space,
        inputs={"start": list(a), "end": list(b)},
        provenance={"operation": "read-only Euclidean distance", "registration_applied": bool(space == "canvas" and registration)},
    )


def angle(
    start: Sequence[float],
    vertex: Sequence[float],
    end: Sequence[float],
    *,
    space: str = "subject",
    registration: Registration | None = None,
) -> Measurement:
    a, b, c = _points_in_space((start, vertex, end), space=space, registration=registration)
    first = (a[0] - b[0], a[1] - b[1])
    second = (c[0] - b[0], c[1] - b[1])
    first_length = math.hypot(*first)
    second_length = math.hypot(*second)
    if first_length == 0.0 or second_length == 0.0:
        raise ValueError("angle requires distinct vertex and endpoints")
    cosine = max(-1.0, min(1.0, (first[0] * second[0] + first[1] * second[1]) / (first_length * second_length)))
    value = math.degrees(math.acos(cosine))
    return Measurement(
        kind="angle",
        value=value,
        coordinate_space=space,
        inputs={"start": list(a), "vertex": list(b), "end": list(c)},
        provenance={"operation": "read-only interior angle in degrees", "registration_applied": bool(space == "canvas" and registration)},
    )


def grid(grid_spec: Grid, size: Sequence[int]) -> GridMeasurement:
    bounds = grid_spec.resolved_bounds(size)
    left, top, right, bottom = bounds
    vertical = tuple(left + (right - left) * index / grid_spec.columns for index in range(grid_spec.columns + 1))
    horizontal = tuple(top + (bottom - top) * index / grid_spec.rows for index in range(grid_spec.rows + 1))
    return GridMeasurement(
        columns=grid_spec.columns,
        rows=grid_spec.rows,
        vertical=vertical,
        horizontal=horizontal,
        bounds=bounds,
    )


@contextmanager
def _open_image(source: str | Path | Image.Image, image_name: str | None = None) -> Iterator[tuple[Image.Image, str]]:
    if isinstance(source, Image.Image):
        yield source.convert("RGB"), image_name or "<memory>"
        return
    path = Path(source)
    with Image.open(path) as opened:
        yield opened.convert("RGB"), image_name or path.name


def _pixel_coordinate(point_value: Sequence[float], size: tuple[int, int]) -> tuple[int, int]:
    x, y = _point(point_value)
    coordinate = (int(round(x)), int(round(y)))
    if not (0 <= coordinate[0] < size[0] and 0 <= coordinate[1] < size[1]):
        raise ValueError(f"pixel point {point_value!r} lies outside image size {size}")
    return coordinate


def sample_pixel(
    source: str | Path | Image.Image,
    point_value: Sequence[float],
    *,
    image_name: str | None = None,
) -> PixelSample:
    with _open_image(source, image_name) as (image, name):
        coordinate = _pixel_coordinate(point_value, image.size)
        value = image.getpixel(coordinate)
        if not isinstance(value, tuple):
            value = (int(value),)
        return PixelSample(
            image_name=name,
            point=(float(coordinate[0]), float(coordinate[1])),
            value=tuple(int(channel) for channel in value),
        )


def horizontal_profile(
    source: str | Path | Image.Image,
    y: int,
    *,
    image_name: str | None = None,
) -> Profile:
    with _open_image(source, image_name) as (image, name):
        row = int(y)
        if row < 0 or row >= image.height:
            raise ValueError(f"horizontal profile row {y} lies outside image height {image.height}")
        gray = image.convert("L")
        values = tuple(float(gray.getpixel((x, row))) for x in range(image.width))
        return Profile("horizontal", row, values, name)


def vertical_profile(
    source: str | Path | Image.Image,
    x: int,
    *,
    image_name: str | None = None,
) -> Profile:
    with _open_image(source, image_name) as (image, name):
        column = int(x)
        if column < 0 or column >= image.width:
            raise ValueError(f"vertical profile column {x} lies outside image width {image.width}")
        gray = image.convert("L")
        values = tuple(float(gray.getpixel((column, y))) for y in range(image.height))
        return Profile("vertical", column, values, name)


def plumb_line(guide: PlumbLine, size: Sequence[int]) -> Measurement:
    width, height = int(size[0]), int(size[1])
    if width <= 0 or height <= 0:
        raise ValueError("guide image size must be positive")
    x = guide.anchor[0]
    return Measurement(
        kind="plumb_line",
        value={"x": x, "from": [x, 0.0], "to": [x, float(height)]},
        coordinate_space="subject",
        inputs={"anchor": list(guide.anchor), "size": [width, height]},
        provenance={"operation": "read-only guide declaration"},
    )


def ground_guide(guide: GroundGuide, size: Sequence[int]) -> Measurement:
    width, height = int(size[0]), int(size[1])
    if width <= 0 or height <= 0:
        raise ValueError("guide image size must be positive")
    left, right = (0.0, float(width)) if guide.x_range is None else guide.x_range
    return Measurement(
        kind="ground_guide",
        value={"y": guide.y, "from": [left, guide.y], "to": [right, guide.y]},
        coordinate_space="subject",
        inputs={"y": guide.y, "x_range": [left, right], "size": [width, height]},
        provenance={"operation": "read-only guide declaration"},
    )


__all__ = [
    "angle",
    "distance",
    "drawing_state_hash",
    "drawing_state_payload",
    "ground_guide",
    "grid",
    "horizontal_profile",
    "map_subject_to_canvas",
    "point",
    "plumb_line",
    "sample_pixel",
    "stage_free_drawing_state_hash",
    "vertical_profile",
]
