"""Persist explicit controls as optional provenance, never as replay geometry authority."""
from __future__ import annotations

from dataclasses import dataclass
import math

from .curves import sample_catmull_rom
from .sampling import MAX_SAMPLES, pressure_along_path, sample_cubic_bezier

CURVE_SCHEMA = "img2drawing.parametric_curve.v1"
CURVE_KEY = "parametric_curve"


@dataclass(frozen=True)
class CurveDefinition:
    kind: str
    controls: tuple[tuple[float, float], ...]
    pressure_knots: tuple[tuple[float, float], ...]
    spacing: float = 3.0
    tolerance: float = .2

    def __post_init__(self):
        controls = tuple(tuple(map(float,p)) for p in self.controls)
        if (self.kind not in ("bezier","spline") or not 2 <= len(controls) <= 128
                or self.kind == "bezier" and len(controls) != 4
                or any(len(p)!=2 or not all(math.isfinite(v) for v in p) for p in controls)):
            raise ValueError("finite explicit controls; four for Bezier, 2–128 for spline")
        spacing,tolerance = float(self.spacing),float(self.tolerance)
        if not all(math.isfinite(v) and v>0 for v in (spacing,tolerance)):
            raise ValueError("positive finite curve sampling settings required")
        knots=tuple(tuple(map(float,k)) for k in self.pressure_knots)
        if (not 2<=len(knots)<=MAX_SAMPLES or any(len(k)!=2 or not all(0<=v<=1 for v in k) for k in knots)
                or knots[0][0]!=0 or knots[-1][0]!=1 or any(a[0]>=b[0] for a,b in zip(knots,knots[1:]))):
            raise ValueError("explicit pressure knots must increase from 0 to 1")
        object.__setattr__(self,"controls",controls)
        object.__setattr__(self,"pressure_knots",knots)
        object.__setattr__(self,"spacing",spacing)
        object.__setattr__(self,"tolerance",tolerance)

    def sample(self):
        if self.kind == "bezier":
            points=sample_cubic_bezier(self.controls, spacing=self.spacing, tolerance=self.tolerance)
        else:
            # Bound existing spline sampler before allocation using a conservative
            # control-polygon length upper bound for its Catmull-Rom segments.
            length=math.fsum(math.dist(a,b) for a,b in zip(self.controls,self.controls[1:]))
            if not math.isfinite(length) or 2*length/self.spacing > MAX_SAMPLES-1:
                raise ValueError("spline sample budget exceeded")
            points=sample_catmull_rom(self.controls, spacing=self.spacing)
        if not 2<=len(points)<=MAX_SAMPLES or any(a==b for a,b in zip(points,points[1:])):
            raise ValueError("curve requires bounded nondegenerate samples")
        points=tuple(points)
        return points,tuple(pressure_along_path(points,self.pressure_knots))

    def to_dict(self):
        return {"schema":CURVE_SCHEMA,"kind":self.kind,"controls":[list(p) for p in self.controls],
                "pressure_knots":[list(k) for k in self.pressure_knots],"spacing":self.spacing,"tolerance":self.tolerance}

    @classmethod
    def from_dict(cls, raw):
        if raw.get("schema")!=CURVE_SCHEMA or set(raw)!={"schema","kind","controls","pressure_knots","spacing","tolerance"}:
            raise ValueError("unsupported curve definition")
        return cls(**{k:v for k,v in raw.items() if k!="schema"})

    def draw_kwargs(self, *, metadata=None):
        points,pressure=self.sample()
        meta=dict(metadata or {})
        if CURVE_KEY in meta:
            raise ValueError("parametric curve metadata is reserved")
        meta[CURVE_KEY]=self.to_dict()
        return {"points":points,"pressure":pressure,"metadata":meta}

    def edit(self, stroke_id):
        from .stroke_edits import StrokeEdit
        points,pressure=self.sample()
        return StrokeEdit(stroke_id,points,pressure,curve_definition=self)


def read_parametric_curve(session, stroke_id):
    """Recover controls only if they still reproduce current explicit points and pressure.

    Other geometry/pressure edits can invalidate the optional definition; never regenerate
    authoritative history from an outdated recipe.
    """
    stroke=session.current_stroke(stroke_id)
    raw=((stroke.tool_state or {}).get("provenance") or {}).get("metadata") or {}
    if CURVE_KEY not in raw:
        raise ValueError("no current parametric curve definition")
    curve=CurveDefinition.from_dict(raw[CURVE_KEY])
    points,pressure=curve.sample()
    if points!=tuple(map(tuple,stroke.points)) or pressure!=tuple(stroke.pressure or ()):
        raise ValueError("parametric definition is stale after another edit")
    return curve
