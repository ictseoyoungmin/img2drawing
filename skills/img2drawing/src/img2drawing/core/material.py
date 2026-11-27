"""Strict internal authored ink geometry; no reference-image or raster-mask input.

S01 foundation only. These descriptors are not a public session API until the
versioned mixed-media history/profile route is integrated.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from collections.abc import Mapping
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .pen import PenDefinition

from .digest import sha256_obj

INK_MARK_SCHEMA = "img2drawing.ink_mark.v1"
STYLED_INK_SCHEMA = "img2drawing.styled_ink_path.v1"
SCREENTONE_SCHEMA = "img2drawing.dot_screentone.v1"
TONE_GRADIENT_SCHEMA = "img2drawing.tone_gradient.v1"
MIN_TONE_PITCH = 4.0
MAX_TONE_PITCH = 512.0
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


def _edge_candidates(first, second=None):
    """Sweep epsilon-expanded edge AABBs, then retain the existing predicate.

    For one ring skip adjacent edges (including its closing seam). For two
    rings consider only cross-ring pairs. O(n) working memory, typical
    sparse candidates; worst case remains quadratic and ring budgets remain.
    No approximation, repair, or coordinate change is performed.
    """
    def boxes(edges, group):
        for i,(a,b) in enumerate(edges):
            yield (min(a[0],b[0]),max(a[0],b[0]),
                   min(a[1],b[1]),max(a[1],b[1]),group,i,(a,b))
    n=len(first)
    ordered=list(boxes(first,0))
    if second is not None:
        ordered.extend(boxes(second,1))
    ordered.sort(key=lambda e:(e[0],e[4],e[5]))
    active=[]
    for lo,hi,ylo,yhi,g,i,edge in ordered:
        active=[entry for entry in active if entry[1]+_ORIENT_EPS>=lo]
        for _,_,other_ylo,other_yhi,other_g,j,other in active:
            if second is None:
                if abs(i-j) in (1,n-1):
                    continue
            elif g==other_g:
                continue
            if other_yhi+_ORIENT_EPS<ylo or yhi+_ORIENT_EPS<other_ylo:
                continue
            # Preserve original ring/index ordering for diagnostic identities.
            if (g,i)<(other_g,j):
                yield i,j,edge,other
            else:
                yield j,i,other,edge
        active.append((lo,hi,ylo,yhi,g,i,edge))


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
    for i,j,first,second in _edge_candidates(edges):
        if _intersects(*first,*second):
            raise ValueError(f"{name} self-intersects or touches at edges {i} and {j} (zero-based)")
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
    return any(_intersects(*first,*second)
               for _,_,first,second in _edge_candidates(tuple(zip(a,a[1:])),tuple(zip(b,b[1:]))))


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
class StyledInkPath(InkPath):
    """Explicit normal-strip stroke geometry with local joins and caps.

    A separate kind preserves the original swept-disk InkPath exactly.
    """
    start_cap: str = "round"
    end_cap: str = "round"
    join: str = "round"
    miter_limit: float = 4.

    def __post_init__(self):
        super().__post_init__()
        caps = ("round", "point", "butt", "square")
        if self.start_cap not in caps or self.end_cap not in caps:
            raise ValueError("unsupported styled ink cap")
        if self.join not in ("round", "miter", "bevel"):
            raise ValueError("unsupported styled ink join")
        object.__setattr__(self, "miter_limit", _number(self.miter_limit, "miter_limit", 1., 16.))
        widths = self.diameters()
        if not any(widths):
            raise ValueError("styled path requires nonzero authored diameter")
        for cap, width in ((self.start_cap, widths[0]), (self.end_cap, widths[-1])):
            if (cap == "point") != (width == 0.):
                raise ValueError("point caps require zero endpoint diameter; other caps require positive diameter")
        if self.points[0] == self.points[-1]:
            if widths[0] != widths[-1] or (self.start_cap,self.end_cap) != ("round","round"):
                raise ValueError("closed styled path requires matching endpoint widths and no explicit end caps")

    def to_dict(self):
        raw = super().to_dict()
        raw.update(schema=STYLED_INK_SCHEMA, kind="styled-path",
                   start_cap=self.start_cap, end_cap=self.end_cap,
                   join=self.join, miter_limit=self.miter_limit)
        return raw


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


@dataclass(frozen=True)
class ToneGradient:
    """Explicit clamped linear coverage field anchored in page coordinates."""
    start: tuple[float,float]
    end: tuple[float,float]
    start_coverage: float
    end_coverage: float

    def __post_init__(self):
        start,end=_points((self.start,self.end),"gradient axis",2,2)
        if math.dist(start,end)<1e-6:
            raise ValueError("gradient axis length must be at least 1e-6 canvas pixels")
        object.__setattr__(self,"start",start)
        object.__setattr__(self,"end",end)
        object.__setattr__(self,"start_coverage",_number(self.start_coverage,"start coverage",0.,1.))
        object.__setattr__(self,"end_coverage",_number(self.end_coverage,"end coverage",0.,1.))

    def to_dict(self):
        return {"schema":TONE_GRADIENT_SCHEMA,"start":list(self.start),"end":list(self.end),
                "start_coverage":self.start_coverage,"end_coverage":self.end_coverage}

    @classmethod
    def from_dict(cls,raw):
        fields={"schema","start","end","start_coverage","end_coverage"}
        if not isinstance(raw,Mapping) or set(raw)!=fields or raw.get("schema")!=TONE_GRADIENT_SCHEMA:
            raise ValueError("invalid tone gradient schema or fields")
        return cls(raw["start"],raw["end"],raw["start_coverage"],raw["end_coverage"])


@dataclass(frozen=True)
class Screentone(InkArea):
    """One bounded authored dot-pattern area, not a list of individual dots.

    Pitch, phase origin, angle and optional gradient are all page-space.
    Exactly one of coverage or gradient is supplied. Coverage denotes an ideal
    area fraction, not dot radius or an alpha value. Black only; the uncovered
    area and holes reveal the underlying media.
    """
    pitch: float = 6.0
    coverage: float | None = None
    angle_degrees: float = 0.0
    phase_origin: tuple[float,float] = (0.,0.)
    gradient: ToneGradient | None = None

    def __post_init__(self):
        # Validate cheap scalar fields before the pairwise ring topology checks.
        if self.paint!="black":
            raise ValueError("dot screentone is black paint only")
        if (self.coverage is None)==(self.gradient is None):
            raise ValueError("specify exactly one of coverage or gradient")
        if self.gradient is not None and not isinstance(self.gradient,ToneGradient):
            raise ValueError("gradient requires an explicit ToneGradient")
        object.__setattr__(self,"pitch",_number(self.pitch,"pitch",MIN_TONE_PITCH,MAX_TONE_PITCH))
        if self.coverage is not None:
            object.__setattr__(self,"coverage",_number(self.coverage,"coverage",0.,1.))
        angle=_number(self.angle_degrees,"angle_degrees",-360.,360.)
        object.__setattr__(self,"angle_degrees",angle%360.)
        origin=tuple(_number(v,"phase origin",-MAX_COORDINATE,MAX_COORDINATE)
                     for v in _sequence(self.phase_origin,"phase origin",2,2))
        object.__setattr__(self,"phase_origin",origin)
        super().__post_init__()

    def to_dict(self):
        raw=super().to_dict()
        raw.update(schema=SCREENTONE_SCHEMA,kind="screentone",pattern="dot",anchor="page",
                   pitch=self.pitch,coverage=self.coverage,angle_degrees=self.angle_degrees,
                   phase_origin=list(self.phase_origin),
                   gradient=None if self.gradient is None else self.gradient.to_dict())
        return raw


def decode_ink_mark(raw):
    """Strict discriminated payload. Unknown fields/revisions fail closed."""
    if not isinstance(raw, Mapping):
        raise ValueError("unsupported ink mark schema")
    if raw.get("schema") == SCREENTONE_SCHEMA:
        fields={"outer","holes","paint","pitch","coverage","angle_degrees","phase_origin","gradient"}
        if (set(raw)!=fields|{"schema","kind","pattern","anchor"}
                or raw.get("kind")!="screentone" or raw.get("pattern")!="dot" or raw.get("anchor")!="page"):
            raise ValueError("invalid screentone fields or pattern/anchor")
        data={key:raw[key] for key in fields}
        if data["gradient"] is not None:
            data["gradient"]=ToneGradient.from_dict(data["gradient"])
        return Screentone(**data)
    if raw.get("schema") == STYLED_INK_SCHEMA:
        fields = {"points", "pressure", "min_width", "max_width", "gamma", "paint",
                  "start_cap", "end_cap", "join", "miter_limit"}
        if raw.get("kind") != "styled-path" or set(raw) != fields | {"schema", "kind"}:
            raise ValueError("invalid styled ink path fields")
        return StyledInkPath(**{key: raw[key] for key in fields})
    if raw.get("schema") != INK_MARK_SCHEMA:
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


MIXED_HISTORY_CONTRACT = "img2drawing.mixed_history.v1"
INK_ELEMENT_SCHEMA = "img2drawing.ink_element.v1"
INK_ACTION_SCHEMA = "img2drawing.ink_action.v1"
INK_ACTION_KINDS = frozenset({"ink.add", "ink.replace", "ink.delete"})


def _identity_text(value, field, *, maximum=128):
    if not isinstance(value, str) or not value.strip() or len(value) > maximum or value != value.strip():
        raise ValueError(f"{field} requires a nonempty, bounded, canonical string")
    return value


@dataclass(frozen=True)
class InkElement:
    """One authored path or area; immutable geometry and stable identity."""
    element_id: str
    mark: InkPath | InkArea
    role: str
    part: str | None = None
    layer: int = 0

    def __post_init__(self):
        _identity_text(self.element_id, "element_id")
        _identity_text(self.role, "role")
        if self.part is not None:
            _identity_text(self.part, "part")
        if type(self.layer) is not int or not -(2**31) <= self.layer < 2**31:
            raise ValueError("layer must be a bounded integer")
        if not isinstance(self.mark, (InkPath, InkArea)):
            raise ValueError("element requires explicit ink geometry")

    def to_dict(self):
        return {"schema": INK_ELEMENT_SCHEMA, "element_id": self.element_id,
                "mark": self.mark.to_dict(), "role": self.role,
                "part": self.part, "layer": self.layer}

    @classmethod
    def from_dict(cls, raw):
        fields = {"schema", "element_id", "mark", "role", "part", "layer"}
        if not isinstance(raw, Mapping) or set(raw) != fields or raw["schema"] != INK_ELEMENT_SCHEMA:
            raise ValueError("unsupported ink element schema or fields")
        return cls(raw["element_id"], decode_ink_mark(raw["mark"]),
                   raw["role"], raw["part"], raw["layer"])

    def digest(self):
        return sha256_obj(self.to_dict())


@dataclass(frozen=True)
class InkAction:
    """Typed addition, same-ID replacement or retirement in CanvasHistory."""
    action_id: str
    kind: str
    element_id: str
    element: InkElement | None
    observation_id: str
    source_observation: str
    reason: str
    pen_definition: PenDefinition | None = None

    def __post_init__(self):
        _identity_text(self.action_id, "action_id")
        _identity_text(self.element_id, "element_id")
        _identity_text(self.observation_id, "observation_id")
        _identity_text(self.source_observation, "source_observation", maximum=2048)
        _identity_text(self.reason, "reason", maximum=2048)
        if not isinstance(self.kind, str) or self.kind not in INK_ACTION_KINDS:
            raise ValueError("unsupported ink action")
        if self.kind == "ink.delete":
            if self.element is not None:
                raise ValueError("ink deletion cannot include replacement geometry")
        elif not isinstance(self.element, InkElement) or self.element.element_id != self.element_id:
            raise ValueError("ink action requires an element with the same identity")
        if self.pen_definition is not None:
            from .pen import PenDefinition
            if (not isinstance(self.pen_definition,PenDefinition) or self.element is None
                    or not isinstance(self.element.mark,InkPath)):
                raise ValueError("pen definition requires an authored ink path")

    def validate_pen_definition(self):
        if self.pen_definition is not None and self.pen_definition.resolve()!=self.element.mark:
            raise ValueError("pen definition does not match resolved ink geometry")

    def provenance(self):
        result = {"action_id": self.action_id, "observation_id": self.observation_id,
                  "source_observation": self.source_observation, "reason": self.reason}
        if self.pen_definition is not None:
            result["pen_definition"] = self.pen_definition.to_dict()
        return result

    def payload(self):
        return {"element_id": self.element_id,
                "element": None if self.element is None else self.element.to_dict()}

    def to_dict(self):
        return {"schema": INK_ACTION_SCHEMA, "kind": self.kind,
                **self.payload(), **self.provenance()}

    @classmethod
    def from_dict(cls, raw):
        fields = {"schema", "kind", "element_id", "element", "action_id",
                  "observation_id", "source_observation", "reason"}
        if (not isinstance(raw, Mapping) or set(raw) not in (fields,fields|{"pen_definition"})
                or raw["schema"] != INK_ACTION_SCHEMA):
            raise ValueError("unsupported ink action schema or fields")
        recipe = None
        if "pen_definition" in raw:
            from .pen import PenDefinition
            recipe = PenDefinition.from_dict(raw["pen_definition"])
        return cls(raw["action_id"], raw["kind"], raw["element_id"],
                   None if raw["element"] is None else InkElement.from_dict(raw["element"]),
                   raw["observation_id"], raw["source_observation"], raw["reason"],recipe)
