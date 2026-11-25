"""Bounded, deterministic sampling and pressure for explicit authored paths."""
from __future__ import annotations

from bisect import bisect_right
import math

MAX_SAMPLES = 16384


def _points(values, minimum=2):
    p=[]
    for v in values:
        if len(v)!=2:
            raise ValueError("points require x,y")
        q=tuple(map(float,v))
        if not all(math.isfinite(x) for x in q):
            raise ValueError("finite coordinates required")
        if not p or q!=p[-1]:
            p.append(q)
        if len(p)>MAX_SAMPLES:
            raise ValueError("sample budget exceeded")
    if len(p)<minimum:
        raise ValueError("path requires distinct consecutive points")
    return p


def _lengths(points):
    c=[0.]
    for a,b in zip(points,points[1:]):
        c.append(c[-1]+math.dist(a,b))
    if not math.isfinite(c[-1]) or c[-1]<=0:
        raise ValueError("nonzero finite path length required")
    return c


def _lerp(a,b,t):
    return tuple(x+(y-x)*t for x,y in zip(a,b))


def resample_polyline(points, *, spacing=3.0):
    """Approximate equal arc-length samples; use separate intervals at real corners."""
    p=_points(points)
    c=_lengths(p)
    step=float(spacing)
    if not math.isfinite(step) or step<=0 or c[-1]/step>MAX_SAMPLES-1:
        raise ValueError("invalid spacing or sample budget exceeded")
    n=max(1,math.ceil(c[-1]/step))
    if n+1>MAX_SAMPLES:
        raise ValueError("sample budget exceeded")
    out=[p[0]]
    for k in range(1,n):
        t=c[-1]*k/n
        j=min(len(p)-2,bisect_right(c,t)-1)
        out.append(_lerp(p[j],p[j+1],(t-c[j])/(c[j+1]-c[j])))
    return out+[p[-1]]


def sample_cubic_bezier(control_points, *, spacing=3.0, tolerance=0.2):
    """Adaptive de Casteljau subdivision then approximate arc-length sampling."""
    raw=list(control_points)
    if len(raw)!=4:
        raise ValueError("cubic Bezier requires four controls")
    p=[]
    for v in raw:
        if len(v)!=2 or not all(math.isfinite(float(x)) for x in v):
            raise ValueError("finite xy controls required")
        p.append(tuple(map(float,v)))
    tol=float(tolerance)
    if not math.isfinite(tol) or tol<=0:
        raise ValueError("positive finite tolerance required")
    dense=[p[0]]
    def subdivide(a,b,c,d,depth):
        chord=math.dist(a,d)
        length=math.dist(a,b)+math.dist(b,c)+math.dist(c,d)
        if not math.isfinite(length):
            raise ValueError("curve length overflow")
        # Control polygon excess alone is insufficient for a shallow, long arc.
        if chord>0:
            ux,uy=(d[0]-a[0])/chord,(d[1]-a[1])/chord
            deviation=max(abs(ux*(v[1]-a[1])-uy*(v[0]-a[0])) for v in (b,c))
        else:
            deviation=max(math.dist(a,v) for v in (b,c))
        if length-chord<=tol and deviation<=tol:
            dense.append(d)
            if len(dense)>MAX_SAMPLES:
                raise ValueError("curve subdivision budget exceeded")
            return
        if depth>=20:
            raise ValueError("curve tolerance requires too much subdivision")
        ab,bc,cd=_lerp(a,b,.5),_lerp(b,c,.5),_lerp(c,d,.5)
        abc,bcd=_lerp(ab,bc,.5),_lerp(bc,cd,.5)
        mid=_lerp(abc,bcd,.5)
        subdivide(a,ab,abc,mid,depth+1)
        subdivide(mid,bcd,cd,d,depth+1)
    subdivide(*p,0)
    return resample_polyline(dense,spacing=spacing)


def pressure_along_path(points, knots):
    """Interpolate explicit (normalized arc position, pressure) knots."""
    raw=list(points)
    p=_points(raw)
    if len(p)!=len(raw):
        raise ValueError("pressure requires one sample per distinct consecutive point")
    c=_lengths(p)
    k=[tuple(map(float,v)) for v in knots]
    if (len(k)<2 or any(len(v)!=2 or not all(math.isfinite(x) and 0<=x<=1 for x in v) for v in k)
            or k[0][0]!=0 or k[-1][0]!=1 or any(a[0]>=b[0] for a,b in zip(k,k[1:]))):
        raise ValueError("pressure knots must increase from 0 to 1, pressure in [0,1]")
    t=[v[0] for v in k]
    out=[]
    for value in c:
        u=value/c[-1]
        i=min(len(k)-2,bisect_right(t,u)-1)
        a,b=k[i],k[i+1]
        out.append(a[1]+(b[1]-a[1])*(u-a[0])/(b[0]-a[0]))
    out[0],out[-1]=k[0][1],k[-1][1]
    return out


def curve_join(left,right):
    """Report endpoint gap and signed tangent turn; do not smooth automatically."""
    a,b=_points(left),_points(right)
    u=math.atan2(a[-1][1]-a[-2][1],a[-1][0]-a[-2][0])
    v=math.atan2(b[1][1]-b[0][1],b[1][0]-b[0][0])
    return {"gap":math.dist(a[-1],b[0]),
            "tangent_delta_degrees":(math.degrees(v-u)+180)%360-180}


def deform_interval(points, start, end, displacement):
    """Apply a smooth, endpoint-locked displacement to an explicit point interval."""
    raw=list(points)
    p=_points(raw)
    if len(raw)!=len(p) or type(start) is not int or type(end) is not int or not 0<=start<end-1<len(p)-1:
        raise ValueError("deformation needs a valid interval with interior samples")
    dx,dy=map(float,displacement)
    if not math.isfinite(dx) or not math.isfinite(dy):
        raise ValueError("finite displacement required")
    c=_lengths(p[start:end+1])
    out=list(p)
    for j in range(start+1,end):
        weight=math.sin(math.pi*c[j-start]/c[-1])**2
        out[j]=(p[j][0]+dx*weight,p[j][1]+dy*weight)
    return out
