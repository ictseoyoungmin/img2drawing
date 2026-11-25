"""Explicit projected construction paths; no inferred anatomy or hidden edges."""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence

from ..inspection import Registration
from .construction import ConstructionMark, InitialConstructResult


def _point(value):
    if len(value) != 2:
        raise ValueError("expected xy point/vector")
    p = tuple(float(x) for x in value)
    if not all(math.isfinite(x) for x in p):
        raise ValueError("point/vector must be finite")
    return p


def projected_ellipse(center, axis_u, axis_v, *, start_degrees=0.0,
                      sweep_degrees=360.0, segments=48):
    """Sample one explicit projected ellipse arc from two conjugate radius vectors.

    Neither a 3D orientation nor a visible interval is inferred. The caller
    chooses the vectors and angular interval. Axes need not be perpendicular.
    """
    c,u,v = map(_point,(center,axis_u,axis_v))
    lu,lv = math.hypot(*u), math.hypot(*v)
    if min(lu,lv) == 0 or abs((u[0]/lu)*(v[1]/lv)-(u[1]/lu)*(v[0]/lv)) <= 1e-10:
        raise ValueError("ellipse radius vectors must be nonzero and nonparallel")
    start,sweep = float(start_degrees),float(sweep_degrees)
    if not math.isfinite(start) or not math.isfinite(sweep) or not 0 < abs(sweep) <= 360:
        raise ValueError("ellipse requires finite start and nonzero sweep <= 360 degrees")
    if type(segments) is not int or not 2 <= segments <= 4096:
        raise ValueError("segments must be an integer in [2,4096]")
    if abs(sweep)==360 and segments<3:
        raise ValueError("full ellipse requires at least three segments")
    start=math.remainder(start,360)
    def at(angle):
        t=math.radians(angle)
        return (c[0]+u[0]*math.cos(t)+v[0]*math.sin(t),
                c[1]+u[1]*math.cos(t)+v[1]*math.sin(t))
    result=[at(start+sweep*i/segments) for i in range(segments+1)]
    if not all(math.isfinite(x) for p in result for x in p):
        raise ValueError("ellipse coordinates overflow")
    if abs(sweep)==360:
        result[-1]=result[0]
    return result


@dataclass(frozen=True)
class ProjectedSection:
    """One explicitly chosen local center and two observed/provisional edge anchors."""
    center: tuple[float,float]
    left: tuple[float,float]
    right: tuple[float,float]

    def __post_init__(self):
        for name in ("center","left","right"):
            object.__setattr__(self,name,_point(getattr(self,name)))
        if self.left == self.right:
            raise ValueError("section requires distinct edge anchors")
        a=(self.left[0]-self.center[0],self.left[1]-self.center[1])
        b=(self.right[0]-self.center[0],self.right[1]-self.center[1])
        if math.hypot(*a)==0 or math.hypot(*b)==0:
            raise ValueError("section center must differ from its edges")

    @classmethod
    def from_widths(cls, center, transverse, *, left_width, right_width):
        """Use explicit independent half-widths along an explicit projected direction."""
        c,t = _point(center),_point(transverse)
        length=math.hypot(*t)
        l,r=float(left_width),float(right_width)
        if length==0 or not all(math.isfinite(x) and x>0 for x in (l,r)):
            raise ValueError("transverse and positive finite half-widths required")
        ux,uy=t[0]/length,t[1]/length
        return cls(c,(c[0]-ux*l,c[1]-uy*l),(c[0]+ux*r,c[1]+uy*r))


def projected_envelope(sections: Sequence[ProjectedSection], *,
                       include_axis=False, include_sections=False):
    """Return independently addressable explicit side, axis, and section paths.

    Section order and edge anchors are supplied by the agent. This is a linear
    projected scaffold, not a contour detector, automatic mesh, or hidden fill.
    No implied terminal caps or smoothing are inserted.
    """
    items=tuple(sections)
    if len(items)<2 or any(not isinstance(s,ProjectedSection) for s in items):
        raise ValueError("at least two ProjectedSection values required")
    for a,b in zip(items,items[1:]):
        if a.center==b.center or a.left==b.left or a.right==b.right:
            raise ValueError("adjacent sections must have distinct centers and side anchors")
        ax,ay=a.right[0]-a.left[0],a.right[1]-a.left[1]
        bx,by=b.right[0]-b.left[0],b.right[1]-b.left[1]
        if ax*bx+ay*by<=0:
            raise ValueError("adjacent section directions reverse; split or reorder the scaffold")
    paths={"left":[s.left for s in items],"right":[s.right for s in items]}
    if include_axis:
        paths["axis"]=[s.center for s in items]
    if include_sections:
        paths.update({f"section_{i}":[s.left,s.right] for i,s in enumerate(items)})
    return paths


def author_projection_guides(session, marks: Sequence[ConstructionMark], *,
                             observation_id: str, registration: Registration,
                             source_observation: str="agent-selected projected construction"):
    """Commit explicit guide marks through the existing session batch boundary.

    A known observation and explicit registration are required. Returns the
    ordinary stroke IDs; retire individually through DrawingSession.
    """
    items=tuple(marks)
    if not items or any(not isinstance(m,ConstructionMark) for m in items):
        raise ValueError("expected nonempty ConstructionMark sequence")
    if not isinstance(registration,Registration) or registration.canvas_size!=(session.width,session.height):
        raise ValueError("registration must match session canvas")
    if len({m.mark_id for m in items})!=len(items):
        raise ValueError("duplicate construction mark id")
    if not isinstance(observation_id,str) or not observation_id.strip():
        raise ValueError("explicit observation_id required")
    if not isinstance(source_observation,str) or not source_observation.strip():
        raise ValueError("source observation required")
    # A registration maps geometric subject coordinates, while the existing
    # action layer validates the mapped drawable bounds. Do not clamp.
    if session.has_reference:
        from PIL import Image
        with Image.open(session.require_reference("projected construction")) as image:
            if image.size!=registration.subject_size:
                raise ValueError("registration must match reference dimensions")
    elif registration.subject_size!=registration.canvas_size or registration.scale!=(1.0,1.0) or registration.offset!=(0.0,0.0):
        raise ValueError("subjectless construction requires identity registration")
    specs=[m.to_draw_spec(registration) for m in items]
    return InitialConstructResult(observation_id=observation_id,
        action_ids=tuple(str(x) for x in session.draw_many(specs,
            observation_id=observation_id,source_observation=source_observation)))
