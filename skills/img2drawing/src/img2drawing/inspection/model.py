"""Stage-free value objects for agent-selected inspection evidence.

These objects describe coordinate correspondence and measurements.  They do not
judge anatomy, likeness, alignment quality, or completion.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import math
from typing import Any, Mapping, Sequence


Point = tuple[float, float]
Size = tuple[int, int]
Box = tuple[float, float, float, float]


def _point(value: Sequence[float]) -> Point:
    if len(value) != 2:
        raise ValueError("point requires x,y")
    x, y = float(value[0]), float(value[1])
    if not all(math.isfinite(item) for item in (x, y)):
        raise ValueError("point coordinates must be finite")
    return x, y


def _box(value: Sequence[float]) -> Box:
    if len(value) != 4:
        raise ValueError("box requires left,top,right,bottom")
    left, top, right, bottom = map(float, value)
    if not all(math.isfinite(item) for item in (left, top, right, bottom)):
        raise ValueError("box coordinates must be finite")
    if not (left < right and top < bottom):
        raise ValueError("box must have positive area")
    return left, top, right, bottom


def _size(value: Sequence[int]) -> Size:
    if len(value) != 2:
        raise ValueError("size requires width,height")
    width, height = map(int, value)
    if width <= 0 or height <= 0:
        raise ValueError("size must be positive")
    return width, height


@dataclass(frozen=True)
class Registration:
    """Explicit axis-aligned subject-to-canvas coordinate mapping.

    Subject points are mapped as ``canvas = offset + subject * scale``.  This is
    deliberately smaller than a registration solver: the Agent supplies the
    correspondence and the runtime only applies it.
    """

    subject_size: Size
    canvas_size: Size
    scale: Point = (1.0, 1.0)
    offset: Point = (0.0, 0.0)

    def __post_init__(self) -> None:
        object.__setattr__(self, "subject_size", _size(self.subject_size))
        object.__setattr__(self, "canvas_size", _size(self.canvas_size))
        scale = _point(self.scale)
        offset = _point(self.offset)
        if scale[0] <= 0.0 or scale[1] <= 0.0:
            raise ValueError("registration scale must be positive")
        object.__setattr__(self, "scale", scale)
        object.__setattr__(self, "offset", offset)

    @classmethod
    def identity(cls, size: Sequence[int]) -> "Registration":
        size = _size(size)
        return cls(subject_size=size, canvas_size=size)

    def map_subject_to_canvas(self, point: Sequence[float]) -> Point:
        x, y = _point(point)
        return self.offset[0] + x * self.scale[0], self.offset[1] + y * self.scale[1]

    def map_canvas_to_subject(self, point: Sequence[float]) -> Point:
        x, y = _point(point)
        return (x - self.offset[0]) / self.scale[0], (y - self.offset[1]) / self.scale[1]

    def to_dict(self) -> dict[str, Any]:
        return {
            "subject_size": list(self.subject_size),
            "canvas_size": list(self.canvas_size),
            "scale": list(self.scale),
            "offset": list(self.offset),
            "mapping": "canvas = offset + subject * scale",
        }


@dataclass(frozen=True)
class ROI:
    """Agent-selected subject-space region of interest."""

    label: str
    box: Box
    scale: float = 2.5

    def __post_init__(self) -> None:
        label = str(self.label).strip()
        if not label:
            raise ValueError("ROI label must be non-empty")
        box = _box(self.box)
        scale = float(self.scale)
        if not 1.0 <= scale <= 12.0:
            raise ValueError("ROI scale must be in [1,12]")
        object.__setattr__(self, "label", label)
        object.__setattr__(self, "box", box)
        object.__setattr__(self, "scale", scale)

    def validate_for_size(self, size: Size) -> None:
        width, height = _size(size)
        left, top, right, bottom = self.box
        if left < 0 or top < 0 or right > width or bottom > height:
            raise ValueError(f"ROI {self.label!r} lies outside subject size {size}: {self.box}")

    def to_dict(self) -> dict[str, Any]:
        return {"label": self.label, "box": list(self.box), "scale": self.scale, "space": "subject"}


@dataclass(frozen=True)
class Grid:
    columns: int = 10
    rows: int = 10
    bounds: Box | None = None

    def __post_init__(self) -> None:
        columns, rows = int(self.columns), int(self.rows)
        if not 1 <= columns <= 64 or not 1 <= rows <= 64:
            raise ValueError("grid rows and columns must be in [1,64]")
        object.__setattr__(self, "columns", columns)
        object.__setattr__(self, "rows", rows)
        object.__setattr__(self, "bounds", None if self.bounds is None else _box(self.bounds))

    def resolved_bounds(self, size: Size) -> Box:
        width, height = _size(size)
        if self.bounds is None:
            return 0.0, 0.0, float(width), float(height)
        left, top, right, bottom = self.bounds
        if left < 0 or top < 0 or right > width or bottom > height:
            raise ValueError(f"grid bounds lie outside image size {size}: {self.bounds}")
        return self.bounds

    def to_dict(self, size: Size | None = None) -> dict[str, Any]:
        bounds = None if size is None else self.resolved_bounds(size)
        if bounds is None and self.bounds is not None:
            bounds = self.bounds
        return {
            "columns": self.columns,
            "rows": self.rows,
            "bounds": None if bounds is None else list(bounds),
            "space": "subject",
        }


@dataclass(frozen=True)
class PlumbLine:
    anchor: Point
    color: tuple[int, int, int] = (0, 190, 220)
    width: int = 3

    def __post_init__(self) -> None:
        object.__setattr__(self, "anchor", _point(self.anchor))
        object.__setattr__(self, "color", tuple(map(int, self.color)))
        if len(self.color) != 3 or any(not 0 <= value <= 255 for value in self.color):
            raise ValueError("guide color must be an RGB triple")
        object.__setattr__(self, "width", max(1, int(self.width)))

    def to_dict(self) -> dict[str, Any]:
        return {"kind": "plumb_line", "anchor": list(self.anchor), "space": "subject", "color": list(self.color)}


@dataclass(frozen=True)
class GroundGuide:
    y: float
    x_range: tuple[float, float] | None = None
    color: tuple[int, int, int] = (30, 130, 220)
    width: int = 3

    def __post_init__(self) -> None:
        y = float(self.y)
        if not math.isfinite(y):
            raise ValueError("ground guide y must be finite")
        object.__setattr__(self, "y", y)
        if self.x_range is not None:
            x_range = _point(self.x_range)
            if x_range[0] >= x_range[1]:
                raise ValueError("ground guide x_range must be increasing")
            object.__setattr__(self, "x_range", x_range)
        object.__setattr__(self, "color", tuple(map(int, self.color)))
        if len(self.color) != 3 or any(not 0 <= value <= 255 for value in self.color):
            raise ValueError("guide color must be an RGB triple")
        object.__setattr__(self, "width", max(1, int(self.width)))

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": "ground_guide",
            "y": self.y,
            "x_range": None if self.x_range is None else list(self.x_range),
            "space": "subject",
            "color": list(self.color),
        }


@dataclass(frozen=True)
class Measurement:
    kind: str
    value: Any
    coordinate_space: str | None = None
    inputs: Mapping[str, Any] = field(default_factory=dict)
    provenance: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not str(self.kind).strip():
            raise ValueError("measurement kind must be non-empty")
        if self.coordinate_space is not None and self.coordinate_space not in {"subject", "canvas", "image"}:
            raise ValueError("unsupported measurement coordinate space")
        object.__setattr__(self, "kind", str(self.kind))
        object.__setattr__(self, "inputs", dict(self.inputs))
        object.__setattr__(self, "provenance", dict(self.provenance))

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "value": self.value,
            "coordinate_space": self.coordinate_space,
            "inputs": dict(self.inputs),
            "provenance": dict(self.provenance),
        }


@dataclass(frozen=True)
class PixelSample:
    image_name: str
    point: Point
    value: tuple[int, ...]
    coordinate_space: str = "image"

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": "pixel_sample",
            "image": self.image_name,
            "point": list(self.point),
            "value": list(self.value),
            "coordinate_space": self.coordinate_space,
        }


@dataclass(frozen=True)
class Profile:
    orientation: str
    index: int
    values: tuple[float, ...]
    image_name: str

    def __post_init__(self) -> None:
        if self.orientation not in {"horizontal", "vertical"}:
            raise ValueError("profile orientation must be horizontal or vertical")
        object.__setattr__(self, "values", tuple(float(value) for value in self.values))

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": f"{self.orientation}_profile",
            "orientation": self.orientation,
            "index": int(self.index),
            "values": list(self.values),
            "image": self.image_name,
            "coordinate_space": "image",
        }


@dataclass(frozen=True)
class GridMeasurement:
    columns: int
    rows: int
    vertical: tuple[float, ...]
    horizontal: tuple[float, ...]
    bounds: Box

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": "grid",
            "columns": self.columns,
            "rows": self.rows,
            "vertical": list(self.vertical),
            "horizontal": list(self.horizontal),
            "bounds": list(self.bounds),
            "coordinate_space": "subject",
        }


@dataclass(frozen=True)
class PointMapping:
    subject: Point
    canvas: Point

    def to_dict(self) -> dict[str, Any]:
        return {"kind": "point_mapping", "subject": list(self.subject), "canvas": list(self.canvas)}
