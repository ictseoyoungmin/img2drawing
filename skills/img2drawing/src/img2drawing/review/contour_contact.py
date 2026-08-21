from __future__ import annotations

from dataclasses import asdict, dataclass
from math import acos, degrees, hypot
from typing import Iterable

from ..core.ir import StrokeIR


@dataclass(frozen=True)
class ContourContactEvidence:
    stroke_a: str
    stroke_b: str
    min_distance_px: float
    normalized_min_distance: float
    closest_index_a: int
    closest_index_b: int
    closest_point_a: tuple[float, float]
    closest_point_b: tuple[float, float]
    tangent_angle_deg: float | None
    threshold_px: float
    near_sample_count_a: int
    near_sample_fraction_a: float

    def to_dict(self) -> dict:
        return asdict(self)


def _stroke_by_id_or_part(ir: StrokeIR, key: str):
    for stroke in ir.strokes:
        if stroke.stroke_id == key or stroke.part == key:
            return stroke
    raise ValueError(f"stroke not found: {key}")


def _tangent(points: list[tuple[float, float]], idx: int) -> tuple[float, float] | None:
    if len(points) < 2:
        return None
    if idx <= 0:
        a,b=points[0],points[1]
    elif idx >= len(points)-1:
        a,b=points[-2],points[-1]
    else:
        a,b=points[idx-1],points[idx+1]
    vx=float(b[0]-a[0]); vy=float(b[1]-a[1])
    n=hypot(vx,vy)
    if n <= 1e-12:
        return None
    return vx/n,vy/n


def _angle_deg(a,b) -> float | None:
    if a is None or b is None:
        return None
    dot=max(-1.0,min(1.0,a[0]*b[0]+a[1]*b[1]))
    angle=degrees(acos(dot))
    # Directionless contour tangents: parallel and anti-parallel mean the same visual alignment.
    return min(angle,180.0-angle)


def measure_contour_contact(
    ir: StrokeIR,
    stroke_a: str,
    stroke_b: str,
    *,
    threshold_px: float = 4.0,
) -> ContourContactEvidence:
    """Mechanical evidence for two explicitly selected contours.

    The function does not infer whether a contact is semantically right or wrong.
    An Agent selects the pair, then uses the returned distance/tangent evidence
    together with the subject image to judge silhouette ownership and overlap.
    """
    sa=_stroke_by_id_or_part(ir,stroke_a)
    sb=_stroke_by_id_or_part(ir,stroke_b)
    if not sa.points or not sb.points:
        raise ValueError("contour contact requires non-empty stroke points")

    best=(float("inf"),0,0)
    near_a=0
    threshold=float(threshold_px)
    for i,p in enumerate(sa.points):
        local=float("inf")
        for j,q in enumerate(sb.points):
            d=hypot(float(p[0]-q[0]),float(p[1]-q[1]))
            if d < local:
                local=d
            if d < best[0]:
                best=(d,i,j)
        if local <= threshold:
            near_a += 1

    d,i,j=best
    diag=max(1e-12,hypot(float(ir.width),float(ir.height)))
    ta=_tangent(list(sa.points),i)
    tb=_tangent(list(sb.points),j)
    return ContourContactEvidence(
        stroke_a=str(sa.stroke_id or sa.part or stroke_a),
        stroke_b=str(sb.stroke_id or sb.part or stroke_b),
        min_distance_px=float(d),
        normalized_min_distance=float(d/diag),
        closest_index_a=int(i),
        closest_index_b=int(j),
        closest_point_a=(float(sa.points[i][0]),float(sa.points[i][1])),
        closest_point_b=(float(sb.points[j][0]),float(sb.points[j][1])),
        tangent_angle_deg=_angle_deg(ta,tb),
        threshold_px=threshold,
        near_sample_count_a=int(near_a),
        near_sample_fraction_a=float(near_a/max(1,len(sa.points))),
    )
