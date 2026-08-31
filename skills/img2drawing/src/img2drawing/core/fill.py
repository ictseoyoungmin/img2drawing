"""Region tone fill: one authored action, deterministically expanded to strokes.

A value pass is a single artistic decision ("this garment sits near value 90"),
not three hundred of them.  Authoring it as a region keeps the canonical session
one action long while the renderer still receives real, individually addressable
pencil strokes.

Hatch lines are clipped analytically against the region boundary, so a straight
line is stored as its two endpoints instead of a sampled polyline.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Iterable, Sequence

Point = tuple[float, float]


def _as_points(values: Sequence[Sequence[float]], *, field_name: str) -> tuple[Point, ...]:
    out: list[Point] = []
    for value in values:
        if len(value) != 2:
            raise ValueError(f"{field_name} requires x,y pairs")
        x, y = float(value[0]), float(value[1])
        if not (math.isfinite(x) and math.isfinite(y)):
            raise ValueError(f"{field_name} coordinates must be finite")
        out.append((x, y))
    return tuple(out)


@dataclass(frozen=True)
class ReservedLight:
    """A light the fill must leave in the paper, instead of erasing it back out.

    ``path`` is a centre line; ``width`` is the full reserved band.  ``strength``
    of 1.0 drops crossing hatch entirely, lower values thin it.
    """

    path: tuple[Point, ...]
    width: float = 12.0
    strength: float = 1.0
    note: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "path", _as_points(self.path, field_name="reserved light path"))
        if len(self.path) < 2:
            raise ValueError("reserved light path requires at least two points")
        if float(self.width) <= 0.0:
            raise ValueError("reserved light width must be positive")
        if not 0.0 <= float(self.strength) <= 1.0:
            raise ValueError("reserved light strength must be in [0,1]")
        object.__setattr__(self, "width", float(self.width))
        object.__setattr__(self, "strength", float(self.strength))
        object.__setattr__(self, "note", str(self.note or ""))

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "path": [list(p) for p in self.path],
            "width": self.width,
            "strength": self.strength,
        }
        if self.note:
            out["note"] = self.note
        return out

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "ReservedLight":
        return cls(
            path=payload.get("path", ()),
            width=float(payload.get("width", 12.0)),
            strength=float(payload.get("strength", 1.0)),
            note=str(payload.get("note", "")),
        )

    def distance_to(self, point: Point) -> float:
        return min(_point_segment_distance(point, a, b) for a, b in zip(self.path, self.path[1:]))


@dataclass(frozen=True)
class FillRegion:
    """One authored tone region: boundary, direction, density, reserved lights."""

    fill_id: str
    polygon: tuple[Point, ...]
    angle: float
    spacing: float
    part: str
    role: str = "value"
    reserved: tuple[ReservedLight, ...] = ()
    layer: int = 0
    min_length: float = 6.0

    def __post_init__(self) -> None:
        object.__setattr__(self, "fill_id", str(self.fill_id or "").strip())
        if not self.fill_id:
            raise ValueError("fill_id must be non-empty")
        object.__setattr__(self, "polygon", _as_points(self.polygon, field_name="fill polygon"))
        if len(self.polygon) < 3:
            raise ValueError("fill polygon requires at least three points")
        if float(self.spacing) <= 0.0:
            raise ValueError("fill spacing must be positive")
        object.__setattr__(self, "angle", float(self.angle))
        object.__setattr__(self, "spacing", float(self.spacing))
        object.__setattr__(self, "part", str(self.part or self.fill_id))
        object.__setattr__(self, "role", str(self.role or "value"))
        object.__setattr__(self, "reserved", tuple(self.reserved))
        object.__setattr__(self, "layer", int(self.layer))
        object.__setattr__(self, "min_length", float(self.min_length))

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "fill_id": self.fill_id,
            "polygon": [list(p) for p in self.polygon],
            "angle": self.angle,
            "spacing": self.spacing,
            "part": self.part,
            "role": self.role,
            "layer": self.layer,
            "min_length": self.min_length,
        }
        if self.reserved:
            out["reserved"] = [r.to_dict() for r in self.reserved]
        return out

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "FillRegion":
        return cls(
            fill_id=payload["fill_id"],
            polygon=payload["polygon"],
            angle=float(payload["angle"]),
            spacing=float(payload["spacing"]),
            part=str(payload.get("part") or payload["fill_id"]),
            role=str(payload.get("role", "value")),
            reserved=tuple(ReservedLight.from_dict(r) for r in payload.get("reserved", ())),
            layer=int(payload.get("layer", 0)),
            min_length=float(payload.get("min_length", 6.0)),
        )

    def area(self) -> float:
        pts = self.polygon
        total = 0.0
        for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]):
            total += x0 * y1 - x1 * y0
        return abs(total) * 0.5


def _point_segment_distance(p: Point, a: Point, b: Point) -> float:
    px, py = p
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    denom = dx * dx + dy * dy
    if denom <= 1e-12:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / denom))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def _scanline_spans(polygon: Sequence[Point], ux: float, uy: float, offset: float) -> list[tuple[float, float]]:
    """Analytic intersection of one infinite hatch line with the polygon.

    Returns inside spans as ``t`` ranges along the hatch direction, so a straight
    run is described by two numbers rather than a sampled path.
    """
    nx, ny = -uy, ux
    hits: list[float] = []
    n = len(polygon)
    for i in range(n):
        ax, ay = polygon[i]
        bx, by = polygon[(i + 1) % n]
        sa = ax * nx + ay * ny - offset
        sb = bx * nx + by * ny - offset
        if sa == sb:
            continue
        # half-open edge test keeps vertices from being counted twice
        if (sa <= 0.0 < sb) or (sb <= 0.0 < sa):
            f = sa / (sa - sb)
            hits.append((ax + f * (bx - ax)) * ux + (ay + f * (by - ay)) * uy)
    hits.sort()
    return [(hits[i], hits[i + 1]) for i in range(0, len(hits) - 1, 2)]


def _apply_reserved(
    span: tuple[float, float],
    ux: float,
    uy: float,
    nx: float,
    ny: float,
    offset: float,
    reserved: Sequence[ReservedLight],
) -> list[tuple[tuple[float, float], float]]:
    """Split one span where reserved lights cross it. Returns (span, attenuation)."""
    if not reserved:
        return [(span, 1.0)]
    start, end = span
    # Sample only to locate reserve boundaries; the emitted span stays analytic.
    step = 2.0
    n = max(2, int((end - start) / step) + 1)
    marks: list[float] = []
    for i in range(n):
        t = start + (end - start) * (i / (n - 1))
        point = (ux * t + nx * offset, uy * t + ny * offset)
        keep = 1.0
        for light in reserved:
            d = light.distance_to(point)
            if d <= light.width * 0.5:
                keep = min(keep, 1.0 - light.strength)
        marks.append(keep)
    out: list[tuple[tuple[float, float], float]] = []
    run_start = start
    run_keep = marks[0]
    for i in range(1, n):
        t = start + (end - start) * (i / (n - 1))
        if marks[i] != run_keep:
            out.append(((run_start, t), run_keep))
            run_start, run_keep = t, marks[i]
    out.append(((run_start, end), run_keep))
    return [(s, k) for s, k in out if k > 0.0 and s[1] - s[0] > 0.0]


def expand_fill(region: FillRegion) -> list[dict[str, Any]]:
    """Deterministically expand one region into hatch line descriptors.

    Each descriptor is ``{"stroke_id", "points", "attenuation"}`` with exactly two
    points per straight run - the whole reason a fill costs one action instead of
    several hundred.
    """
    ux = math.cos(math.radians(region.angle))
    uy = math.sin(math.radians(region.angle))
    nx, ny = -uy, ux
    offsets = [p[0] * nx + p[1] * ny for p in region.polygon]
    lo, hi = min(offsets), max(offsets)
    out: list[dict[str, Any]] = []
    index = 0
    steps = int(math.floor((hi - lo) / region.spacing)) + 1
    for k in range(steps):
        offset = lo + region.spacing * (k + 0.5)
        if offset > hi:
            break
        for span in _scanline_spans(region.polygon, ux, uy, offset):
            for (t0, t1), keep in _apply_reserved(span, ux, uy, nx, ny, offset, region.reserved):
                if t1 - t0 < region.min_length:
                    continue
                a = (round(ux * t0 + nx * offset, 3), round(uy * t0 + ny * offset, 3))
                b = (round(ux * t1 + nx * offset, 3), round(uy * t1 + ny * offset, 3))
                out.append({
                    "stroke_id": f"{region.fill_id}#{index:04d}",
                    "points": [list(a), list(b)],
                    "attenuation": round(keep, 4),
                })
                index += 1
    return out
