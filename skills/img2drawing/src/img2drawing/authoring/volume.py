"""Editable projected volume hypotheses; never infer anatomy or hidden contours."""
from __future__ import annotations

from dataclasses import dataclass, replace
import math

from ..inspection import Registration
from .construction import ConstructionMark
from .projection import projected_ellipse
from .sampling import MAX_SAMPLES, pressure_along_path
from .stroke_edits import StrokeEdit


def _vector(values, n):
    q = tuple(float(v) for v in values)
    if len(q) != n or not all(math.isfinite(v) for v in q):
        raise ValueError(f"finite {n}D vector required")
    return q


def _positive(value):
    v = float(value)
    if not math.isfinite(v) or v <= 0:
        raise ValueError("positive finite parameter required")
    return v


def _turn(a, b):
    return (b - a + 180) % 360 - 180


def _rotate(v, degrees):
    a = math.radians(degrees)
    c, s = math.cos(a), math.sin(a)
    return (c*v[0]-s*v[1], s*v[0]+c*v[1])


@dataclass(frozen=True)
class ProjectionCamera:
    """Explicit camera-space projection: +z forward, +y down, no pose inference."""
    origin: tuple[float, float]
    scale: float
    perspective: bool = False
    near: float = 1e-6

    def __post_init__(self):
        object.__setattr__(self, "origin", _vector(self.origin, 2))
        object.__setattr__(self, "scale", _positive(self.scale))
        object.__setattr__(self, "near", _positive(self.near))
        if type(self.perspective) is not bool:
            raise ValueError("perspective must be boolean")

    def project(self, point):
        x, y, z = _vector(point, 3)
        if self.perspective and z <= self.near:
            raise ValueError("point at or behind near plane; explicitly clip the path")
        s = self.scale/z if self.perspective else self.scale
        return _vector((self.origin[0]+x*s, self.origin[1]+y*s), 2)

    def section_arc(self, center, u, v, *, start_degrees, sweep_degrees, segments=48):
        """Project an explicitly selected spatial ellipse arc, point by point."""
        c, u, v = (_vector(p, 3) for p in (center, u, v))
        lu, lv = math.hypot(*u), math.hypot(*v)
        if min(lu, lv) == 0:
            raise ValueError("nonzero ellipse axes required")
        a, b = tuple(x/lu for x in u), tuple(x/lv for x in v)
        cross = (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
        if math.hypot(*cross) <= 1e-10:
            raise ValueError("nonparallel ellipse axes required")
        start, sweep = float(start_degrees), float(sweep_degrees)
        if not math.isfinite(start) or not 0 < abs(sweep) <= 360 or type(segments) is not int or not 3 <= segments <= 4096:
            raise ValueError("finite arc and 3–4096 segments required")
        # Check the continuous interval, not merely sampled points, against the near plane.
        start = math.remainder(start, 360)
        lo, hi = sorted((start, start+sweep))
        phase = math.degrees(math.atan2(v[2], u[2]))+180
        extrema = [lo, hi] + [phase+360*k for k in range(-2, 3) if lo <= phase+360*k <= hi]
        if self.perspective and min(c[2]+u[2]*math.cos(math.radians(t))+v[2]*math.sin(math.radians(t)) for t in extrema) <= self.near:
            raise ValueError("arc crosses near plane; explicitly choose a visible interval")
        out = []
        for i in range(segments+1):
            t = math.radians(start+sweep*i/segments)
            out.append(self.project(tuple(x+a*math.cos(t)+b*math.sin(t) for x,a,b in zip(c,u,v))))
        if abs(sweep) == 360:
            out[-1] = out[0]
        return tuple(out)


@dataclass(frozen=True)
class VolumeStation:
    """One agent-authored section: normalized station, projected axis and half-widths."""
    t: float
    center: tuple[float, float]
    angle_degrees: float
    left_width: float
    right_width: float

    def __post_init__(self):
        t, angle = float(self.t), float(self.angle_degrees)
        if not 0 <= t <= 1 or not math.isfinite(angle):
            raise ValueError("finite station in [0,1] and angle required")
        object.__setattr__(self, "t", t)
        object.__setattr__(self, "center", _vector(self.center, 2))
        object.__setattr__(self, "angle_degrees", math.remainder(angle,360))
        for name in ("left_width", "right_width"):
            object.__setattr__(self, name, _positive(getattr(self, name)))

    @property
    def direction(self):
        return _rotate((1.,0.), self.angle_degrees)

    @property
    def edges(self):
        d = self.direction
        return _vector((self.center[i]-d[i]*self.left_width for i in range(2)),2), _vector((self.center[i]+d[i]*self.right_width for i in range(2)),2)

    def arc(self, depth_axis, *, start_degrees, sweep_degrees, segments=48):
        left, right = self.edges
        middle = tuple((a+b)/2 for a,b in zip(left,right))
        radius = tuple((b-a)/2 for a,b in zip(left,right))
        return tuple(projected_ellipse(middle, radius, depth_axis, start_degrees=start_degrees,
                                      sweep_degrees=sweep_degrees, segments=segments))

    def to_dict(self):
        return {"t":self.t,"center":list(self.center),"angle_degrees":self.angle_degrees,
                "left_width":self.left_width,"right_width":self.right_width}


def _slopes(xs, ys):
    """Shape-preserving Hermite slopes; no overshoot between explicit scalar anchors."""
    h = [b-a for a,b in zip(xs,xs[1:])]
    d = [(b-a)/step for a,b,step in zip(ys,ys[1:],h)]
    m = [d[0]]
    for i in range(1,len(ys)-1):
        p,q = d[i-1],d[i]
        if p*q <= 0:
            m.append(0.)
        else:
            a,b = 2*h[i]+h[i-1], h[i]+2*h[i-1]
            m.append((a+b)/(a/p+b/q))
    m.append(d[-1])
    return m


def _hermite(a,b,m,n,h,u):
    return (2*u**3-3*u*u+1)*a+(u**3-2*u*u+u)*h*m+(-2*u**3+3*u*u)*b+(u**3-u*u)*h*n


@dataclass(frozen=True)
class ProjectedVolume:
    stations: tuple[VolumeStation, ...]

    def __post_init__(self):
        stations = tuple(self.stations)
        if not 2 <= len(stations) <= 128 or any(not isinstance(s,VolumeStation) for s in stations):
            raise ValueError("2–128 explicit volume stations required")
        if stations[0].t != 0 or stations[-1].t != 1 or any(b.t-a.t < 1e-6 or a.center == b.center or abs(_turn(a.angle_degrees,b.angle_degrees)) >= 90 for a,b in zip(stations,stations[1:])):
            raise ValueError("stations must progress 0→1, distinct centers, no reversed adjacent section axes")
        object.__setattr__(self,"stations",stations)

    def to_dict(self):
        return {"schema":"img2drawing.projected_volume.v1","stations":[s.to_dict() for s in self.stations]}

    @classmethod
    def from_dict(cls, data):
        if data.get("schema") != "img2drawing.projected_volume.v1" or set(data) != {"schema","stations"}:
            raise ValueError("unsupported projected volume definition")
        return cls(tuple(VolumeStation(**s) for s in data["stations"]))

    def sampled_stations(self, *, samples_per_span=12):
        if type(samples_per_span) is not int or samples_per_span < 1 or (len(self.stations)-1)*samples_per_span+1 > MAX_SAMPLES:
            raise ValueError("invalid station sample budget")
        xs = [s.t for s in self.stations]
        angles = [self.stations[0].angle_degrees]
        for a,b in zip(self.stations,self.stations[1:]):
            angles.append(angles[-1]+_turn(a.angle_degrees,b.angle_degrees))
        cols = [[s.center[0] for s in self.stations], [s.center[1] for s in self.stations], angles,
                [s.left_width for s in self.stations], [s.right_width for s in self.stations]]
        slopes = [_slopes(xs,col) for col in cols]
        out = []
        for i in range(len(xs)-1):
            h = xs[i+1]-xs[i]
            out.append(self.stations[i])
            for j in range(1,samples_per_span):
                u = j/samples_per_span
                x,y,a,l,r = [_hermite(c[i],c[i+1],m[i],m[i+1],h,u) for c,m in zip(cols,slopes)]
                out.append(VolumeStation(xs[i]+u*h,(x,y),a,l,r))
        return tuple(out+[self.stations[-1]])

    def paths(self, *, samples_per_span=12, section_arcs=None):
        stations = self.sampled_stations(samples_per_span=samples_per_span)
        paths = {"axis":tuple(s.center for s in stations),"left":tuple(s.edges[0] for s in stations),"right":tuple(s.edges[1] for s in stations)}
        for i, arc in (section_arcs or {}).items():
            if type(i) is not int or not 0 <= i < len(self.stations):
                raise ValueError("section arc must name an original station")
            paths[f"section_{i}"] = self.stations[i].arc(**arc)
        return paths

    def guide_marks(self, prefix, part, *, selected, samples_per_span=12, section_arcs=None, phase="mass_blocking", layer=0):
        """Selected paths become ordinary disposable construction marks, never final contours."""
        paths = self.paths(samples_per_span=samples_per_span, section_arcs=section_arcs)
        selected = tuple(selected)
        if not selected or len(set(selected)) != len(selected) or any(k not in paths for k in selected):
            raise ValueError("choose unique explicit volume paths")
        return tuple(ConstructionMark(mark_id=f"{prefix}-{k}",phase=phase,role="construction",part=part,
                     points=paths[k],layer=layer) for k in selected)


def inspect_attachment(parent: VolumeStation, child: VolumeStation):
    """Projected anchor gaps and axis/width differences; no automatic verdict."""
    if not isinstance(parent,VolumeStation) or not isinstance(child,VolumeStation):
        raise ValueError("explicit volume stations required")
    return {"center_gap":math.dist(parent.center,child.center),
            "left_gap":math.dist(parent.edges[0],child.edges[0]),"right_gap":math.dist(parent.edges[1],child.edges[1]),
            "axis_turn_degrees":_turn(parent.angle_degrees,child.angle_degrees),
            "left_width_delta":child.left_width-parent.left_width,"right_width_delta":child.right_width-parent.right_width}


def align_attachment(parent: VolumeStation, child: ProjectedVolume, *, child_index, rotate=False, match_widths=False):
    """Explicit rigid alignment about the chosen station; optional local width match only."""
    if not isinstance(parent,VolumeStation) or not isinstance(child,ProjectedVolume):
        raise ValueError("explicit parent station and child volume required")
    if type(child_index) is not int or not 0 <= child_index < len(child.stations) or type(rotate) is not bool or type(match_widths) is not bool:
        raise ValueError("explicit child station index and boolean alignment choices required")
    anchor = child.stations[child_index]
    angle = _turn(anchor.angle_degrees,parent.angle_degrees) if rotate else 0.
    stations = []
    for i,s in enumerate(child.stations):
        offset = _rotate(tuple(a-b for a,b in zip(s.center,anchor.center)),angle)
        c = tuple(a+b for a,b in zip(parent.center,offset))
        stations.append(replace(s, center=c, angle_degrees=s.angle_degrees+angle,
                        left_width=parent.left_width if match_widths and i==child_index else s.left_width,
                        right_width=parent.right_width if match_widths and i==child_index else s.right_width))
    return ProjectedVolume(tuple(stations))


def prepare_volume_edits(session, volume, stroke_ids, *, registration, samples_per_span=12, section_arcs=None):
    """Re-sample named current guide paths, preserving pressure by normalized arc position."""
    paths = volume.paths(samples_per_span=samples_per_span, section_arcs=section_arcs)
    if not isinstance(registration,Registration) or registration.canvas_size != (session.width,session.height) or not stroke_ids or set(stroke_ids)-set(paths) or len(set(stroke_ids.values())) != len(stroke_ids):
        raise ValueError("matching registration and unique explicit guide mapping required")
    edits = []
    with session._lock:
        if session.has_reference:
            from PIL import Image
            with Image.open(session.require_reference("projected construction edit")) as image:
                if image.size != registration.subject_size:
                    raise ValueError("registration must match reference dimensions")
        elif registration.subject_size != registration.canvas_size or registration.scale != (1.,1.) or registration.offset != (0.,0.):
            raise ValueError("subjectless construction requires identity registration")
        for name,sid in stroke_ids.items():
            stroke = session.current_stroke(sid)
            if stroke.stroke_id != sid or stroke.role != "construction" or stroke.pressure is None or len(stroke.pressure)!=len(stroke.points):
                raise ValueError("only current construction guides with aligned pressure may be edited")
            lengths = [0.]
            for a,b in zip(stroke.points,stroke.points[1:]):
                lengths.append(lengths[-1]+math.dist(a,b))
            if lengths[-1] <= 0 or any(a==b for a,b in zip(lengths,lengths[1:])):
                raise ValueError("guide has degenerate path")
            knots = [(x/lengths[-1],p) for x,p in zip(lengths,stroke.pressure)]
            points = tuple(registration.map_subject_to_canvas(p) for p in paths[name])
            pressure = tuple(stroke.pressure) if points == tuple(map(tuple,stroke.points)) else tuple(pressure_along_path(points,knots))
            edits.append(StrokeEdit(sid,points,pressure))
    return tuple(edits)
