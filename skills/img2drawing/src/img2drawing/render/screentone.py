"""Analytic, page-anchored square-lattice dot coverage.

No stored dots, reference images, procedural geometry inference, or independent
compositor. The shared ink kernel supplies a validated clipped area mask on the
working pixel-centre grid; this module intersects it with a nested dot family.
"""
from __future__ import annotations

import math
import numpy as np

# A circle grows from its cell centre. At radius > 1/2 it reaches neighbouring
# cells; area is the disk intersected with a unit square, not pi*r*r.
_DISK_TOUCH = math.pi/4.
MIN_WORKING_PERIOD = 8.
TONE_TILE_PIXELS = 262144


def disk_cell_coverage(radius_squared):
    """Analytic unit-cell area for squared radius in [0,1/2]."""
    q=float(radius_squared)
    if not math.isfinite(q) or not 0.<=q<=.5:
        raise ValueError("dot radius squared must be in [0, 0.5]")
    if q<=.25:
        return math.pi*q
    if q==.5:
        return 1.
    return min(1.,max(0.,math.pi*q-4.*(q*math.acos(.5/math.sqrt(q))-.5*math.sqrt(q-.25))))


def radius_squared_for_coverage(coverage):
    """Deterministic inverse for a constant-coverage patch; no per-dot geometry."""
    if not math.isfinite(coverage) or not 0.<=coverage<=1.:
        raise ValueError("coverage must be in [0,1]")
    if coverage==0.:
        return 0.
    if coverage==1.:
        return .5
    if coverage<=_DISK_TOUCH:
        return coverage/math.pi
    lo,hi=.25,.5
    for _ in range(52):
        mid=(lo+hi)*.5
        if disk_cell_coverage(mid)<coverage:
            lo=mid
        else:
            hi=mid
    return (lo+hi)*.5


def constant_coverage(mark):
    if mark.gradient is None:
        return mark.coverage
    if mark.gradient.start_coverage==mark.gradient.end_coverage:
        return mark.gradient.start_coverage
    return None


def _coverage_rank(q):
    # q is the nearest-centre distance squared in a unit square. The analytic
    # area rank allows comparison against a different coverage at each sample
    # without running a scalar root solver per pixel.
    rank=np.pi*q
    high=q>.25
    if np.any(high):
        h=q[high]
        rank[high]-=4.*(h*np.arccos(.5/np.sqrt(h))-.5*np.sqrt(h-.25))
    np.clip(rank,0.,1.,out=rank)
    return rank


def intersect_dot_pattern(mask,bounds,mark,factor,*,tile_pixels=TONE_TILE_PIXELS):
    """Intersect in-place; global page coordinates make tiles/crops identical.

    A fixed logical-space lattice origin is a dot centre. Positive angles are
    clockwise on the y-down page. The gradient is sampled in page space at
    each working pixel centre, clamped at its explicit endpoints. For rapidly
    varying gradients dots can deform; exact local coverage is an ideal
    constant-field calibration, not an arbitrary-window pixel guarantee.
    """
    x0,y0,x1,y1=bounds
    if mask.shape!=(y1-y0,x1-x0):
        raise ValueError("tone mask and bounds disagree")
    if not math.isfinite(factor) or factor*mark.pitch<MIN_WORKING_PERIOD:
        raise ValueError("screentone pitch below working sample limit")
    if type(tile_pixels) is not int or not 1<=tile_pixels<=TONE_TILE_PIXELS:
        raise ValueError("invalid screentone tile budget")
    c=constant_coverage(mark)
    if c==0.:
        mask.fill(0)
        return mask
    if c==1. or not mask.size:
        return mask
    threshold=None if c is None else radius_squared_for_coverage(c)
    theta=math.radians(mark.angle_degrees)
    cos,sin=math.cos(theta),math.sin(theta)
    ox,oy=mark.phase_origin
    g=mark.gradient
    if c is None:
        gx,gy=g.end[0]-g.start[0],g.end[1]-g.start[1]
        denom=gx*gx+gy*gy
    # Bound BOTH dimensions: even an unusually wide canvas cannot turn one
    # row into an unbounded temporary. Mask storage is budgeted by ink.py.
    columns=max(1,min(x1-x0,1024,tile_pixels))
    rows=max(1,tile_pixels//columns)
    for ya in range(y0,y1,rows):
        yb=min(ya+rows,y1)
        y=(np.arange(ya,yb,dtype=np.float64)[:,None]+.5)/factor
        for xa in range(x0,x1,columns):
            xb=min(xa+columns,x1)
            dst=mask[ya-y0:yb-y0,xa-x0:xb-x0]
            if not dst.any():
                continue
            x=(np.arange(xa,xb,dtype=np.float64)[None,:]+.5)/factor
            u=(cos*(x-ox)+sin*(y-oy))/mark.pitch
            v=(-sin*(x-ox)+cos*(y-oy))/mark.pitch
            u-=np.floor(u+.5)
            v-=np.floor(v+.5)
            q=u*u+v*v
            np.minimum(q,.5,out=q)
            if threshold is not None:
                inside=q<=threshold
            else:
                t=((x-g.start[0])*gx+(y-g.start[1])*gy)/denom
                np.clip(t,0.,1.,out=t)
                coverage=g.start_coverage+(g.end_coverage-g.start_coverage)*t
                # Explicit 0/1 behaviour, including samples exactly at a dot
                # centre or cell corner. No tiny dots survive the zero endpoint.
                inside=(coverage>=1.)|((coverage>0.)&(_coverage_rank(q)<=coverage))
            dst[~inside]=0
    return mask
