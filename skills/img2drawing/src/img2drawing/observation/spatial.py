"""Read-only projected relationships between explicitly observed landmarks."""
from __future__ import annotations

import math
from typing import Sequence

from ..inspection import Measurement, Registration
from .landmarks import LandmarkSet, _mapped, _registered, _segment, _text


def _direction(a, b):
    dx, dy = b[0]-a[0], b[1]-a[1]
    length = math.hypot(dx, dy)
    if length == 0:
        raise ValueError("axis requires distinct positions")
    return dx/length, dy/length


def _degrees(a, b):
    dx, dy = _direction(a,b)
    return math.degrees(math.atan2(dy, dx))


def _turn(a, b, period):
    return (b-a+period/2) % period-period/2


def compare_axes(reference: LandmarkSet, drawing: LandmarkSet, *,
                 registration: Registration, axis: Sequence[str],
                 directed: bool = False) -> Measurement:
    """Signed projected tilt delta; x right, y down; no inference of 3D turn."""
    _registered(reference, drawing, registration)
    _segment(reference, axis)
    a, b = _segment(drawing, axis)
    expected = _degrees(*(_mapped(reference, n, registration) for n in axis))
    actual = _degrees(a,b)
    period = 360 if directed else 180
    return Measurement("axis_comparison", {"reference_degrees": expected % period,
                       "drawing_degrees": actual % period,
                       "signed_delta_degrees": _turn(expected, actual, period)}, "canvas",
                       {"axis": list(axis), "directed": bool(directed),
                        "registration": registration.to_dict()},
                       {"operation": "projected 2D tilt", "inference": False})


def cross_section(points: LandmarkSet, *, axis: Sequence[str],
                  edges: Sequence[str]) -> Measurement:
    """Width transverse to an explicitly observed local axis.

    The two edges must themselves be visible points. A large longitudinal
    offset signals a possibly oblique section, not a corrected contour.
    """
    a, b = _segment(points, axis)
    left, right = _segment(points, edges)
    ux, uy = _direction(a,b)
    dx, dy = right[0]-left[0], right[1]-left[1]
    return Measurement("cross_section", {"transverse_width": abs(-uy*dx+ux*dy),
                       "longitudinal_offset": ux*dx+uy*dy, "edge_distance": math.hypot(dx,dy)},
                       points.space, {"axis": list(axis), "edges": list(edges)},
                       {"operation": "visible transverse span", "inference": False})


def _cross(a,b,c):
    return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])


def _intersects(a,b,c,d):
    def on(p,q,r):
        return (min(p[0],q[0]) <= r[0] <= max(p[0],q[0]) and
                min(p[1],q[1]) <= r[1] <= max(p[1],q[1]))
    ab_c, ab_d, cd_a, cd_b = _cross(a,b,c), _cross(a,b,d), _cross(c,d,a), _cross(c,d,b)
    if ab_c == 0 and on(a,b,c) or ab_d == 0 and on(a,b,d):
        return True
    if cd_a == 0 and on(c,d,a) or cd_b == 0 and on(c,d,b):
        return True
    return ((ab_c > 0) != (ab_d > 0)) and ((cd_a > 0) != (cd_b > 0))


def _polygon(points):
    n = len(points)
    if not 3 <= n <= 128 or len(set(points)) != n:
        raise ValueError("negative space requires 3–128 distinct ordered vertices")
    for i in range(n):
        a,b = points[i],points[(i+1)%n]
        # Adjacent collinear edges may continue, but must not backtrack.
        c = points[(i+2)%n]
        if _cross(a,b,c) == 0 and (a[0]-b[0])*(c[0]-b[0])+(a[1]-b[1])*(c[1]-b[1]) > 0:
            raise ValueError("polygon boundary backtracks")
        for j in range(i+1,n):
            if j == i+1 or (i == 0 and j == n-1):
                continue
            if _intersects(a,b,points[j],points[(j+1)%n]):
                raise ValueError("polygon must be simple")
    ox,oy = points[0]
    p = [(x-ox,y-oy) for x,y in points]
    edges = list(zip(p,p[1:]+p[:1]))
    weights = [a[0]*b[1]-a[1]*b[0] for a,b in edges]
    area2 = math.fsum(weights)
    if area2 == 0:
        raise ValueError("negative space polygon has zero area")
    cx = ox+math.fsum((a[0]+b[0])*w for (a,b),w in zip(edges,weights))/(3*area2)
    cy = oy+math.fsum((a[1]+b[1])*w for (a,b),w in zip(edges,weights))/(3*area2)
    xs,ys = zip(*points)
    return {"area": abs(area2)/2, "centroid": [cx,cy],
            "bounds": [min(xs),min(ys),max(xs),max(ys)]}


def compare_negative_space(reference: LandmarkSet, drawing: LandmarkSet, *,
                           registration: Registration, boundary: Sequence[str]) -> Measurement:
    """Area, centroid, bounds and corresponding visible corner displacement.

    This is an explicit polygonal approximation, not inferred silhouette IoU.
    """
    _registered(reference, drawing, registration)
    if isinstance(boundary, str):
        raise ValueError("boundary must contain ordered landmark names")
    labels = tuple(boundary)
    expected_points = [_mapped(reference,n,registration) for n in labels]
    actual_points = [drawing.observed(n) for n in labels]
    expected, actual = _polygon(expected_points), _polygon(actual_points)
    return Measurement("negative_space_comparison", {"reference": expected, "drawing": actual,
                       "relative_area_delta": (actual["area"]-expected["area"])/expected["area"],
                       "centroid_delta": [a-b for a,b in zip(actual["centroid"],expected["centroid"])],
                       "vertex_errors": [{"name": n, "distance": math.dist(a,b)}
                                         for n,a,b in zip(labels,expected_points,actual_points)]},
                       "canvas", {"boundary": list(labels), "registration": registration.to_dict()},
                       {"operation": "explicit visible polygon approximation", "inference": False})


def occlusion_relation(points: LandmarkSet, *, foreground: str, hidden_form: str,
                       entry_segment: Sequence[str], reappearance_segment: Sequence[str] | None = None,
                       evidence: str) -> Measurement:
    """Record local visible directions on either side of a declared occluder.

    Entry runs toward disappearance; reappearance runs away from emergence.
    The hidden interval is deliberately not measured or interpolated.
    """
    foreground, hidden_form = _text(foreground,"foreground"), _text(hidden_form,"hidden_form")
    if foreground == hidden_form:
        raise ValueError("occluder and hidden form must differ")
    a,b = _segment(points, entry_segment)
    entry = _degrees(a,b)
    result = {"foreground": foreground, "hidden_form": hidden_form,
              "entry_anchor": list(b), "entry_direction_degrees": entry,
              "reappearance_anchor": None, "reappearance_direction_degrees": None,
              "visible_direction_delta_degrees": None, "hidden_geometry": "UNMEASURED"}
    if reappearance_segment is not None:
        c,d = _segment(points,reappearance_segment)
        direction = _degrees(c,d)
        result.update(reappearance_anchor=list(c), reappearance_direction_degrees=direction,
                      visible_direction_delta_degrees=_turn(entry,direction,360))
    return Measurement("occlusion_relation",result,points.space,
                       {"entry_segment": list(entry_segment), "reappearance_segment":
                        None if reappearance_segment is None else list(reappearance_segment)},
                       {"operation": "declared foreground ownership and visible directions",
                        "evidence": _text(evidence,"evidence"), "inference": False})
