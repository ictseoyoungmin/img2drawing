"""Editable, explicit pen recipes resolved to the existing opaque InkPath kernel.

No image inputs, implicit contour detection, uniform straight-line oversampling,
or replay-time resampling. Geometry and pressure decisions belong to the author.
The recipe is optional action provenance; the resolved InkPath remains pixel authority.
"""
from __future__ import annotations

from bisect import bisect_right
from collections.abc import Mapping
from dataclasses import dataclass
import math

from .material import InkPath, StyledInkPath, MAX_PATH_POINTS, MAX_WIDTH, _number, _points, _sequence, _paint

PEN_DEFINITION_SCHEMA = "img2drawing.pen_definition.v1"
STYLED_PEN_SCHEMA = "img2drawing.pen_definition.v2"
MAX_CONTROLS = 1024
MAX_PRESSURE_KNOTS = 256
MAX_RECURSION = 24
MAX_WIDTH_RECURSION = 48  # gamma<1 may need fine intervals near zero pressure


def _mid(a, b):
    return ((a[0]+b[0])*.5, (a[1]+b[1])*.5)


def _flatten_bezier(controls, tolerance):
    """Adaptive de Casteljau, retaining segment joins and original endpoints."""
    out = [controls[0]]

    def split(a, b, c, d, depth):
        chord = math.dist(a, d)
        length = math.dist(a, b) + math.dist(b, c) + math.dist(c, d)
        if chord:
            ux, uy = (d[0]-a[0])/chord, (d[1]-a[1])/chord
            deviation = max(abs(ux*(v[1]-a[1])-uy*(v[0]-a[0])) for v in (b,c))
        else:
            deviation = max(math.dist(a,v) for v in (b,c))
        if chord > 0 and length-chord <= tolerance and deviation <= tolerance:
            out.append(d)
            if len(out) > MAX_PATH_POINTS:
                raise ValueError("pen curve sample budget exceeded")
            return
        if depth >= MAX_RECURSION or length == 0:
            raise ValueError("degenerate pen curve or subdivision budget exceeded")
        ab, bc, cd = _mid(a,b), _mid(b,c), _mid(c,d)
        abc, bcd = _mid(ab,bc), _mid(bc,cd)
        center = _mid(abc,bcd)
        split(a,ab,abc,center,depth+1)
        split(center,bcd,cd,d,depth+1)

    for i in range(0,len(controls)-1,3):
        split(*controls[i:i+4],0)
    return tuple(out)


def _pressure_knots(raw):
    raw = _sequence(raw, "pressure knots", MAX_PRESSURE_KNOTS, 2)
    out = tuple(tuple(_number(v,"pressure knot",0.,1.)
                      for v in _sequence(k,"pressure knot",2,2)) for k in raw)
    if out[0][0] != 0. or out[-1][0] != 1. or any(a[0]>=b[0] for a,b in zip(out,out[1:])):
        raise ValueError("pressure knots must strictly increase from 0 to 1")
    return out


def _diameter_error(p0, p1, gamma, span):
    """Maximum chord error of span * pressure**gamma on a linear-pressure interval."""
    lo,hi = sorted((p0,p1))
    if lo == hi or gamma == 1. or not span:
        return 0.
    left,right = lo**gamma,hi**gamma
    variation = span*(right-left)
    # For nearly linear gamma, bound error without an ill-conditioned inversion.
    if abs(gamma-1.) < 1e-7:
        return min(variation,2*span*abs(gamma-1.)/(math.e*min(gamma,1.)))
    slope = (right-left)/(hi-lo)
    if slope <= 0:
        return variation
    log_p = math.log(slope/gamma)/(gamma-1.)
    if log_p >= 0:
        return variation
    p = math.exp(log_p)
    if not lo < p < hi:
        return variation
    chord = left+(right-left)*(p-lo)/(hi-lo)
    return min(variation, span*abs(p**gamma-chord))


@dataclass(frozen=True)
class PenDefinition:
    """An explicitly authored centerline, pressure knots and resolved pen settings.

    Legacy round strokes retain the swept-disk kernel. Explicit miter/bevel
    joins or butt/square caps use the separate normal-strip path geometry.
    Pointed terminals require zero endpoint width; fineliner is constant-width.
    """
    tool: str
    geometry: str
    controls: tuple[tuple[float,float],...]
    pressure_knots: tuple[tuple[float,float],...]
    min_width: float
    max_width: float
    gamma: float = 1.
    start_cap: str = "round"
    end_cap: str = "round"
    join: str = "round"
    paint: str = "black"
    curve_tolerance: float = .05
    width_tolerance: float = .05
    miter_limit: float = 4.

    def __post_init__(self):
        if self.tool not in ("g-pen","fineliner"):
            raise ValueError("unsupported pen tool")
        if self.geometry not in ("polyline","bezier"):
            raise ValueError("geometry must be polyline or cubic Bezier chain")
        if self.geometry == "polyline":
            controls = _points(self.controls,"pen controls",MAX_CONTROLS,2)
        else:
            raw = _sequence(self.controls,"Bezier controls",MAX_CONTROLS,4)
            # Repeated handles are legal: only a zero-length cubic is invalid.
            from .material import MAX_COORDINATE
            controls = tuple(tuple(_number(c,"Bezier coordinate",-MAX_COORDINATE,MAX_COORDINATE)
                                   for c in _sequence(p,"Bezier control",2,2)) for p in raw)
            if (len(controls)-1)%3 or any(len(set(controls[i:i+4]))<2 for i in range(0,len(controls)-1,3)):
                raise ValueError("Bezier chain requires 3n+1 controls and nonzero segments")
        knots = _pressure_knots(self.pressure_knots)
        low = _number(self.min_width,"min_width",0.,MAX_WIDTH)
        high = _number(self.max_width,"max_width",low,MAX_WIDTH)
        gamma = _number(self.gamma,"gamma",.25,4.)
        if not high:
            raise ValueError("max_width must be positive")
        caps = ("round","point","butt","square")
        if self.start_cap not in caps or self.end_cap not in caps or self.join not in ("round","miter","bevel"):
            raise ValueError("unsupported pen terminal or join")
        limit = _number(self.miter_limit,"miter_limit",1.,16.)
        if self.join!="miter" and limit!=4.:
            raise ValueError("non-default miter_limit requires miter join")
        object.__setattr__(self,"miter_limit",limit)
        if self.tool == "fineliner":
            if low != high or gamma != 1. or knots != ((0.,1.),(1.,1.)) or "point" in (self.start_cap,self.end_cap):
                raise ValueError("fineliner requires constant diameter, constant pressure and non-point caps")
        else:
            for cap,p in ((self.start_cap,knots[0][1]),(self.end_cap,knots[-1][1])):
                width=low+(high-low)*p**gamma
                if cap=="point" and width != 0.:
                    raise ValueError("point terminal requires zero endpoint pressure and min_width=0")
                if cap!="point" and width == 0.:
                    raise ValueError("non-point terminal requires positive endpoint diameter")
            if not low and not any(k[1]>0 for k in knots):
                raise ValueError("G-pen requires nonzero authored diameter")
        object.__setattr__(self,"controls",controls)
        object.__setattr__(self,"pressure_knots",knots)
        object.__setattr__(self,"min_width",low)
        object.__setattr__(self,"max_width",high)
        object.__setattr__(self,"gamma",gamma)
        object.__setattr__(self,"paint",_paint(self.paint))
        object.__setattr__(self,"curve_tolerance",_number(self.curve_tolerance,"curve_tolerance",.005,1.))
        object.__setattr__(self,"width_tolerance",_number(self.width_tolerance,"width_tolerance",.005,1.))

    def resolve(self):
        """Compile once into InkPath; keep original corners and all pressure knots.

        Breaks are flattened vertices and exact arc-length pressure knots.
        Only nonlinear diameter interpolation error adds samples. Thus a long
        straight constant-width line needs just two points, regardless of length.
        """
        points = self.controls if self.geometry=="polyline" else _flatten_bezier(self.controls,self.curve_tolerance)
        cumulative=[0.]
        for a,b in zip(points,points[1:]):
            cumulative.append(cumulative[-1]+math.dist(a,b))
        total=cumulative[-1]
        if not total or not math.isfinite(total):
            raise ValueError("pen path requires nonzero finite arc length")
        positions=[s/total for s in cumulative]
        if any(a>=b for a,b in zip(positions,positions[1:])):
            raise ValueError("pen path has an unresolved near-zero interval")
        knot_x=[k[0] for k in self.pressure_knots]
        knot_p=[k[1] for k in self.pressure_knots]
        pressure_at_knot=dict(self.pressure_knots)
        geometry_at_vertex=dict(zip(positions,points))
        breaks=sorted(set(positions)|set(knot_x))
        if len(breaks)>MAX_PATH_POINTS:
            raise ValueError("pen path sample budget exceeded")
        def xy(t):
            if t in geometry_at_vertex:
                return geometry_at_vertex[t]
            j=min(len(points)-2,bisect_right(positions,t)-1)
            u=(t-positions[j])/(positions[j+1]-positions[j])
            a,b=points[j],points[j+1]
            return (a[0]+(b[0]-a[0])*u,a[1]+(b[1]-a[1])*u)
        def pressure(t):
            if t in pressure_at_knot:
                return pressure_at_knot[t]
            j=min(len(knot_x)-2,bisect_right(knot_x,t)-1)
            u=(t-knot_x[j])/(knot_x[j+1]-knot_x[j])
            return min(1.,max(0.,knot_p[j]+(knot_p[j+1]-knot_p[j])*u))
        out=[points[0]]
        values=[pressure(0.)]
        def emit(a,b,p0,p1,depth):
            error=_diameter_error(p0,p1,self.gamma,self.max_width-self.min_width)
            if error>self.width_tolerance:
                m=(a+b)*.5
                if depth>=MAX_WIDTH_RECURSION or not a<m<b:
                    raise ValueError("pen width tolerance requires too many samples")
                pm=pressure(m)
                emit(a,m,p0,pm,depth+1)
                emit(m,b,pm,p1,depth+1)
                return
            q=xy(b)
            if q==out[-1]:
                raise ValueError("pen knots create an unrepresentable near-zero interval")
            out.append(q)
            values.append(p1)
            if len(out)>MAX_PATH_POINTS:
                raise ValueError("pen path sample budget exceeded")
        for a,b in zip(breaks,breaks[1:]):
            emit(a,b,pressure(a),pressure(b),0)
        if self.uses_styled_path:
            mark=StyledInkPath(tuple(out),tuple(values),self.min_width,self.max_width,
                               self.gamma,self.paint,self.start_cap,self.end_cap,
                               self.join,self.miter_limit)
        else:
            mark=InkPath(tuple(out),tuple(values),self.min_width,self.max_width,self.gamma,self.paint)
        # A zero-radius end is not a visible sharp point if the next disk
        # swallows it. Refuse too-steep local tapers rather than invent geometry.
        radii=[w*.5 for w in mark.diameters()]
        for cap,i,j,adjacent in ((self.start_cap,0,1,0),
                                 (self.end_cap,-1,-2,len(mark.points)-2)):
            if cap!="point":
                continue
            tip=mark.points[i]
            if radii[j]>=.95*math.dist(tip,mark.points[j]):
                raise ValueError("point terminal taper is too steep; extend the pressure transition")
            # A later disk or swept segment must not swallow the endpoint,
            # even when the immediately adjacent segment has a gentle taper.
            for k,(a,b,r0,r1) in enumerate(zip(mark.points,mark.points[1:],radii,radii[1:])):
                if k==adjacent or max(r0,r1)==0:
                    continue
                dx,dy=b[0]-a[0],b[1]-a[1]
                ux,uy=a[0]-tip[0],a[1]-tip[1]
                dr=r1-r0
                qa=dx*dx+dy*dy-dr*dr
                qb=2*(ux*dx+uy*dy-r0*dr)
                qc=ux*ux+uy*uy-r0*r0
                other=qa+qb+qc
                minimum=min(qc,other)
                if qa>0:
                    t=max(0.,min(1.,-qb/(2*qa)))
                    minimum=min(minimum,(qa*t+qb)*t+qc)
                if minimum<=0:
                    raise ValueError("point terminal is covered by another contact; revise the pressure transition or path")
        return mark

    @property
    def uses_styled_path(self):
        return self.join!="round" or self.start_cap in ("butt","square") or self.end_cap in ("butt","square")

    def to_dict(self):
        raw = {"schema":PEN_DEFINITION_SCHEMA,"tool":self.tool,"geometry":self.geometry,
                "controls":[list(p) for p in self.controls],
                "pressure_knots":[list(k) for k in self.pressure_knots],
                "min_width":self.min_width,"max_width":self.max_width,"gamma":self.gamma,
                "start_cap":self.start_cap,"end_cap":self.end_cap,"join":self.join,
                "paint":self.paint,"curve_tolerance":self.curve_tolerance,
                "width_tolerance":self.width_tolerance}
        if self.uses_styled_path:
            raw.update(schema=STYLED_PEN_SCHEMA,miter_limit=self.miter_limit)
        return raw

    @classmethod
    def from_dict(cls,raw):
        fields={"schema","tool","geometry","controls","pressure_knots","min_width","max_width",
                "gamma","start_cap","end_cap","join","paint","curve_tolerance","width_tolerance"}
        if not isinstance(raw,Mapping):
            raise ValueError("unsupported pen definition schema or fields")
        schema=raw.get("schema")
        if schema==STYLED_PEN_SCHEMA:
            fields=fields|{"miter_limit"}
        elif schema!=PEN_DEFINITION_SCHEMA:
            raise ValueError("unsupported pen definition schema or fields")
        if set(raw)!=fields:
            raise ValueError("unsupported pen definition schema or fields")
        result=cls(**{k:raw[k] for k in fields-{"schema"}})
        if result.uses_styled_path != (schema==STYLED_PEN_SCHEMA):
            raise ValueError("pen definition schema does not match selected geometry")
        return result

    def action(self, *, action_id, element_id, observation_id, source_observation, reason,
               role, part=None, layer=0, kind="ink.add"):
        """Create one explicit add/replace action, retaining the editable recipe."""
        from .material import InkAction, InkElement
        if kind not in ("ink.add","ink.replace"):
            raise ValueError("pen definition authors only ink.add or ink.replace")
        element=InkElement(element_id,self.resolve(),role,part,layer)
        return InkAction(action_id,kind,element_id,element,observation_id,
                         source_observation,reason,pen_definition=self)
