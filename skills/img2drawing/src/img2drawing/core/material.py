"""Strict internal authored ink geometry; no reference-image or raster-mask input.

S01 foundation only. These descriptors are not a public session API until the
versioned mixed-media history/profile route is integrated.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from collections.abc import Mapping

from .digest import sha256_obj

INK_MARK_SCHEMA = "img2drawing.ink_mark.v1"
MAX_PATH_POINTS = 16384
MAX_RING_POINTS = 1024  # total including the explicitly repeated closing vertices
MAX_COORDINATE = 32768.0
MAX_WIDTH = 1024.0
_ORIENT_EPS = 1e-9


def _number(value, name, low, high):
    if type(value) not in (int, float) or not low <= value <= high or not math.isfinite(value):
        raise ValueError(f"{name} must be a finite number in [{low}, {high}]")
    return float(value)


def _sequence(value, name, maximum, minimum=0):
    if not isinstance(value, (tuple, list)) or not minimum <= len(value) <= maximum:
        raise ValueError(f"{name} requires {minimum}–{maximum} entries")
    return value


def _points(value, name, maximum, minimum):
    raw = _sequence(value, name, maximum, minimum)
    out = tuple(tuple(_number(c, name, -MAX_COORDINATE, MAX_COORDINATE)
                      for c in _sequence(p, name, 2, 2)) for p in raw)
    if any(a == b for a, b in zip(out, out[1:])):
        raise ValueError(f"{name} contains repeated consecutive points")
    return out


def _paint(value):
    if type(value) is not str or value not in ("black", "white"):
        raise ValueError("ink paint must be black or white")
    return value


def _orientation(a, b, c):
    cross = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
    return 1 if cross > _ORIENT_EPS else -1 if cross < -_ORIENT_EPS else 0


def _on_segment(a, b, c):
    return (min(a[0], b[0]) - _ORIENT_EPS <= c[0] <= max(a[0], b[0]) + _ORIENT_EPS
            and min(a[1], b[1]) - _ORIENT_EPS <= c[1] <= max(a[1], b[1]) + _ORIENT_EPS)


def _intersects(a, b, c, d):
    p, q = _orientation(a, b, c), _orientation(a, b, d)
    u, v = _orientation(c, d, a), _orientation(c, d, b)
    return ((p * q < 0 and u * v < 0)
            or (p == 0 and _on_segment(a, b, c))
            or (q == 0 and _on_segment(a, b, d))
            or (u == 0 and _on_segment(c, d, a))
            or (v == 0 and _on_segment(c, d, b)))


def _ring(raw, name):
    pts = _points(raw, name, MAX_RING_POINTS, 4)
    if pts[0] != pts[-1]:
        raise ValueError(f"{name} must be explicitly closed")
    vertices = pts[:-1]
    if len(set(vertices)) != len(vertices):
        raise ValueError(f"{name} repeats a non-closing vertex")
    n = len(vertices)
    # Adjacent reversals overlap even though adjacent edges share an endpoint.
    for i, b in enumerate(vertices):
        a, c = vertices[i - 1], vertices[(i + 1) % n]
        if (_orientation(a, b, c) == 0
                and (a[0] - b[0]) * (c[0] - b[0]) + (a[1] - b[1]) * (c[1] - b[1]) > 0):
            raise ValueError(f"{name} has a reversing edge")
    edges = tuple(zip(pts, pts[1:]))
    for i, (a, b) in enumerate(edges):
        for j in range(i + 2, n):
            if i == 0 and j == n - 1:
                continue
            if _intersects(a, b, *edges[j]):
                raise ValueError(f"{name} self-intersects or touches")
    area2 = math.fsum(a[0] * b[1] - b[0] * a[1] for a, b in edges)
    if abs(area2) <= _ORIENT_EPS:
        raise ValueError(f"{name} encloses no area")
    return pts


def _inside(point, ring):
    x, y = point
    inside = False
    for a, b in zip(ring, ring[1:]):
        if _orientation(a, b, point) == 0 and _on_segment(a, b, point):
            return False
        if (a[1] > y) != (b[1] > y):
            cross_x = a[0] + (y - a[1]) * (b[0] - a[0]) / (b[1] - a[1])
            if x < cross_x:
                inside = not inside
    return inside


def _rings_touch(a, b):
    return any(_intersects(p, q, u, v)
               for p, q in zip(a, a[1:]) for u, v in zip(b, b[1:]))


@dataclass(frozen=True)
class InkPath:
    """Opaque ink, with pressure mapped to diameter at authored path knots.

    Diameter varies linearly between knots; a constant diameter is the same
    model with equal min/max widths. No graphite grade, grain, jitter or alpha
    accumulation. Round swept-disk geometry is the initial kernel.
    """

    points: tuple[tuple[float, float], ...]
    pressure: tuple[float, ...]
    min_width: float
    max_width: float
    gamma: float = 1.0
    paint: str = "black"

    def __post_init__(self):
        points = _points(self.points, "ink path", MAX_PATH_POINTS, 2)
        pressure = tuple(_number(p, "pressure", 0.0, 1.0)
                         for p in _sequence(self.pressure, "pressure", len(points), len(points)))
        low = _number(self.min_width, "min_width", 0.0, MAX_WIDTH)
        high = _number(self.max_width, "max_width", low, MAX_WIDTH)
        if high == 0:
            raise ValueError("max_width must be positive")
        object.__setattr__(self, "points", points)
        object.__setattr__(self, "pressure", pressure)
        object.__setattr__(self, "min_width", low)
        object.__setattr__(self, "max_width", high)
        object.__setattr__(self, "gamma", _number(self.gamma, "gamma", 0.25, 4.0))
        object.__setattr__(self, "paint", _paint(self.paint))

    def diameters(self):
        return tuple(self.min_width + (self.max_width - self.min_width) * p ** self.gamma
                     for p in self.pressure)

    def to_dict(self):
        return {"schema": INK_MARK_SCHEMA, "kind": "path", "paint": self.paint,
                "points": [list(p) for p in self.points], "pressure": list(self.pressure),
                "min_width": self.min_width, "max_width": self.max_width, "gamma": self.gamma}

    def digest(self):
        return sha256_obj(self.to_dict())


@dataclass(frozen=True)
class InkArea:
    """Explicit authored closed boundary plus optional disjoint interior holes."""

    outer: tuple[tuple[float, float], ...]
    holes: tuple[tuple[tuple[float, float], ...], ...] = ()
    paint: str = "black"

    def __post_init__(self):
        raw_holes = _sequence(self.holes, "holes", MAX_RING_POINTS // 4)
        rings = [self.outer, *raw_holes]
        # Reject excessive complexity before pairwise geometry validation.
        counts = [len(_sequence(r, "ring", MAX_RING_POINTS, 4)) for r in rings]
        if sum(counts) > MAX_RING_POINTS:
            raise ValueError("total ring point budget exceeded")
        outer = _ring(self.outer, "outer")
        holes = tuple(_ring(h, "hole") for h in raw_holes)
        for i, h in enumerate(holes):
            if not _inside(h[0], outer) or _rings_touch(h, outer):
                raise ValueError("hole must be strictly inside outer boundary")
            for other in holes[:i]:
                if (_rings_touch(h, other) or _inside(h[0], other) or _inside(other[0], h)):
                    raise ValueError("holes must be disjoint and non-nested")
        object.__setattr__(self, "outer", outer)
        object.__setattr__(self, "holes", holes)
        object.__setattr__(self, "paint", _paint(self.paint))

    def to_dict(self):
        return {"schema": INK_MARK_SCHEMA, "kind": "area", "paint": self.paint,
                "outer": [list(p) for p in self.outer],
                "holes": [[list(p) for p in ring] for ring in self.holes]}

    def digest(self):
        return sha256_obj(self.to_dict())


def decode_ink_mark(raw):
    """Strict discriminated payload. Unknown fields/revisions fail closed."""
    if not isinstance(raw, Mapping) or raw.get("schema") != INK_MARK_SCHEMA:
        raise ValueError("unsupported ink mark schema")
    kind = raw.get("kind")
    if kind == "path":
        fields = {"points", "pressure", "min_width", "max_width", "gamma", "paint"}
        cls = InkPath
    elif kind == "area":
        fields = {"outer", "holes", "paint"}
        cls = InkArea
    else:
        raise ValueError("unsupported ink mark kind")
    if set(raw) != fields | {"schema", "kind"}:
        raise ValueError("invalid ink mark fields")
    return cls(**{key: raw[key] for key in fields})
