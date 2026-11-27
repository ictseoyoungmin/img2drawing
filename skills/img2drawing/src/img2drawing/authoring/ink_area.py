"""Explicit authored solid ink. No source masks, inference or flood filling."""
from __future__ import annotations

from ..core.material import InkArea, MAX_COORDINATE, MAX_RING_POINTS, _number, _sequence, _ring
from ..core.pen import _flatten_bezier


def sample_ink_contour(controls, *, tolerance=.05):
    """Compile an explicitly closed 3n+1 cubic Bezier chain to a simple ring.

    Controls are authored in logical canvas pixels; no implicit closure or
    auto-repair. Sampled vertices, including exact corners and closure, are
    authoritative when passed to solid_ink. Control handles are not persisted
    as a separate area recipe.
    """
    raw=_sequence(controls,"contour controls",MAX_RING_POINTS,4)
    points=tuple(tuple(_number(v,"contour coordinate",-MAX_COORDINATE,MAX_COORDINATE)
                       for v in _sequence(p,"contour control",2,2)) for p in raw)
    if (len(points)-1)%3 or points[0]!=points[-1]:
        raise ValueError("contour requires explicitly closed cubic Bezier chain (3n+1 controls)")
    if any(len(set(points[i:i+4]))<2 for i in range(0,len(points)-1,3)):
        raise ValueError("contour contains a zero-length cubic")
    tol=_number(tolerance,"contour tolerance",.005,1.)
    sampled=_flatten_bezier(points,tol,max_samples=MAX_RING_POINTS)
    return _ring(sampled,"sampled contour")


def solid_ink(outer, *, holes=(), paint="black"):
    """One editable closed contour with explicitly reserved holes.

    This is deliberate geometric authoring, not a fill of an inferred outline.
    White paint covers lower layers; a hole exposes them. The existing strict
    InkArea validator rejects open, self-intersecting or touching rings.
    """
    return InkArea(outer,holes,paint)


__all__=["sample_ink_contour","solid_ink"]
