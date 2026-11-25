"""Read-only tonal evidence from canonical cursor renders and explicit live plans.

No automatic marks, raster edits, hidden inference, or artistic verdict.
"""
from __future__ import annotations

import math
from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np
from PIL import Image

PLAN_FIELDS = (
    "area_id", "part", "reference_evidence", "boundary", "direction_degrees",
    "target_density", "target_value", "pressure_range", "highlight_reserves",
)


def _plans_and_strokes(strokes):
    from ..authoring.tonal_area import TONAL_AREA_SCHEMA, TonalAreaPlan

    plans, groups = {}, {}
    for stroke in strokes:
        metadata = stroke.tool_state.get("provenance", {}).get("metadata", {})
        raw = metadata.get("tonal_area")
        if raw is None:
            continue
        if raw.get("schema") != TONAL_AREA_SCHEMA:
            raise ValueError("unsupported tonal area schema")
        plan = TonalAreaPlan(**{k: raw[k] for k in PLAN_FIELDS})
        if raw.get("digest") != plan.digest():
            raise ValueError(f"tonal plan digest mismatch: {plan.area_id}")
        previous = plans.get(plan.area_id)
        if previous is not None and previous.digest() != plan.digest():
            raise ValueError(f"conflicting live tonal plans: {plan.area_id}")
        plans[plan.area_id] = plan
        groups.setdefault(plan.area_id, []).append(stroke)
    return plans, groups


def plans_from_current_strokes(session):
    """One current IR snapshot, not repeated per-stroke history resolution."""
    return _plans_and_strokes(session.current_ir().strokes)[0]


def polygon_mask(shape, polygon, scale=1):
    """Even-odd inclusion of pixel centers; used for measurement only."""
    vertices = np.asarray(polygon, dtype=np.float64) * scale
    if (vertices.ndim != 2 or vertices.shape[1] != 2 or len(vertices) < 3
            or not np.isfinite(vertices).all()):
        raise ValueError("polygon must contain finite xy vertices")
    h, w = shape
    x0 = max(0, int(np.floor(vertices[:, 0].min())))
    x1 = min(w, int(np.ceil(vertices[:, 0].max())))
    y0 = max(0, int(np.floor(vertices[:, 1].min())))
    y1 = min(h, int(np.ceil(vertices[:, 1].max())))
    result = np.zeros(shape, dtype=bool)
    if x0 >= x1 or y0 >= y1:
        return result
    y, x = np.ogrid[y0:y1, x0:x1]
    x, y = x + .5, y + .5
    inside = np.zeros((y1-y0, x1-x0), dtype=bool)
    for a, b in zip(vertices, np.roll(vertices, -1, axis=0)):
        ax, ay = a
        bx, by = b
        if ay == by:
            continue
        inside ^= ((ay > y) != (by > y)) & (x < (bx-ax)*(y-ay)/(by-ay)+ax)
    result[y0:y1, x0:x1] = inside
    return result


def gray(path):
    """Read straight RGBA over white consistently, including transparent profiles."""
    with Image.open(path) as image:
        rgba = image.convert("RGBA")
        bg = Image.new("RGBA", rgba.size, "white")
        bg.alpha_composite(rgba)
        return np.asarray(bg.convert("L"), dtype=np.float64) / 255


def _delta_arrays(paper, before, after, scale, coverage_threshold, saturation_threshold):
    if paper.ndim != 2 or not (paper.shape == before.shape == after.shape):
        raise ValueError("paper/before/after must have the same 2D shape")
    if not all(np.isfinite(a).all() and (a >= 0).all() and (a <= 1).all()
               for a in (paper, before, after)):
        raise ValueError("luminance arrays must be finite and in [0,1]")
    if (not 0 < coverage_threshold < saturation_threshold <= 1
            or not np.isfinite(scale) or scale <= 0):
        raise ValueError("invalid measurement thresholds or scale")
    # Compute once for an entire interval, not separately for every area.
    d0, d1 = np.maximum(paper-before, 0), np.maximum(paper-after, 0)
    return d0, d1, np.maximum(d1-d0, 0), np.maximum(d0-d1, 0)


def _masks(shape, plan, scale):
    area = polygon_mask(shape, plan.boundary, scale)
    reserve = np.zeros_like(area)
    for polygon in plan.highlight_reserves:
        reserve |= polygon_mask(shape, polygon, scale)
    target, protected = area & ~reserve, reserve & area
    if not target.any():
        raise ValueError(f"no target pixels: {plan.area_id}")
    return area, reserve, target, protected


def _measure_delta(arrays, plan, *, scale, coverage_threshold, saturation_threshold):
    d0,d1,added,removed=arrays
    area,reserve,target,protected=_masks(d0.shape,plan,scale)
    def stats(d,m):
        if not m.any():
            return None
        v=d[m]
        return {"mean_darkness":float(v.mean()),
                "coverage":float((v>coverage_threshold+1e-12).mean()),
                "saturation":float((v>saturation_threshold+1e-12).mean())}
    added_mass=float(added.sum(dtype=np.float64))
    return {
        "area_id":plan.area_id, "plan_digest":plan.digest(),
        "target_pixels":int(target.sum()), "protected_pixels":int(protected.sum()),
        "reserve_outside_area_pixels":int((reserve & ~area).sum()),
        "target_before":stats(d0,target), "target_after":stats(d1,target),
        "protected_before":stats(d0,protected), "protected_after":stats(d1,protected),
        "target_added_mean":float(added[target].mean()),
        "target_removed_mean":float(removed[target].mean()),
        "outside_added_darkness_fraction":float(added[~area].sum(dtype=np.float64))/added_mass if added_mass else None,
    }


def measure_plan(paper,before,after,plan,*,scale=1,coverage_threshold=8/255,saturation_threshold=.65):
    """Paper-relative darkness; not a calibrated perceptual target score."""
    arrays=_delta_arrays(paper,before,after,scale,coverage_threshold,saturation_threshold)
    return _measure_delta(arrays,plan,scale=scale,coverage_threshold=coverage_threshold,
                          saturation_threshold=saturation_threshold)


def _inside(points, polygon):
    """Even-odd point inclusion; same convention as pixel-center masks."""
    x,y=points[:,0],points[:,1]
    inside=np.zeros(len(points),dtype=bool)
    for a,b in zip(polygon,(*polygon[1:],polygon[0])):
        ax,ay=a; bx,by=b
        if ay!=by:
            inside ^= ((ay>y)!=(by>y)) & (x<(bx-ax)*(y-ay)/(by-ay)+ax)
    return inside


def _stroke_diagnostics(strokes,plan,*,sample_spacing=2.0):
    """Approximate centerline evidence; never causal raster attribution."""
    rows=[]
    for stroke in strokes:
        p=np.asarray(stroke.points,dtype=np.float64)
        if len(p)<2:
            continue
        segments=np.diff(p,axis=0)
        lengths=np.linalg.norm(segments,axis=1)
        valid=lengths>0
        if not valid.any():
            continue
        lengths=lengths[valid]; starts=p[:-1][valid]; segments=segments[valid]
        total=float(lengths.sum())
        count=np.maximum(1,np.ceil(lengths/sample_spacing)).astype(np.int64)
        if count.sum()>100000:
            raise ValueError("tonal centerline sample budget exceeded; choose narrower scope")
        positions=[]; weights=[]
        for a,vec,L,n in zip(starts,segments,lengths,count):
            t=(np.arange(n)+.5)/n
            positions.append(a+t[:,None]*vec)
            weights.append(np.full(n,L/n))
        samples=np.concatenate(positions); weight=np.concatenate(weights)
        inside=_inside(samples,plan.boundary)
        protected=np.zeros(len(samples),dtype=bool)
        for polygon in plan.highlight_reserves:
            protected |= _inside(samples,polygon)
        protected &= inside
        angles=np.degrees(np.arctan2(segments[:,1],segments[:,0]))
        dev=np.abs((angles-plan.direction_degrees+90)%180-90)
        pressure=np.asarray(stroke.pressure if stroke.pressure is not None else [],dtype=np.float64)
        lo,hi=plan.pressure_range
        rows.append({"stroke_id":stroke.stroke_id,
                     "length":total,
                     "outside_centerline_fraction":float(weight[~inside].sum()/total),
                     "protected_centerline_fraction":float(weight[protected].sum()/total),
                     "mean_axial_direction_error_degrees":float(np.dot(dev,lengths)/total),
                     "pressure_sample_outside_declared_range":None if not len(pressure) else float(((pressure<lo)|(pressure>hi)).mean())})
    # Rank by explicit centerline exposure, not assumed contribution to pixels.
    rows.sort(key=lambda x:(-x["protected_centerline_fraction"],-x["outside_centerline_fraction"],str(x["stroke_id"])))
    return rows


def _separation(arrays,plans,pairs,scale):
    d0,d1=arrays[:2]
    output=[]
    for pair in pairs:
        a,b=pair
        if a==b or a not in plans or b not in plans:
            raise ValueError("separation requires two distinct selected live plan IDs")
        ma=_masks(d0.shape,plans[a],scale)[2]
        mb=_masks(d0.shape,plans[b],scale)[2]
        if (ma & mb).any():
            raise ValueError("separation targets overlap; select distinct regions")
        before=float(d0[ma].mean()-d0[mb].mean())
        after=float(d1[ma].mean()-d1[mb].mean())
        output.append({"areas":[a,b],"signed_mean_darkness_difference_before":before,
                       "signed_mean_darkness_difference_after":after,
                       "absolute_separation_change":abs(after)-abs(before)})
    return output


def inspect_tonal_interval(session,before_cursor,after_cursor,area_ids=None,*,
                           separation_pairs=(),coverage_threshold=8/255,saturation_threshold=.65):
    """Non-mutating diagnostic of canonical interval and current explicit plans.

    The plans/stroke IDs are from the current IR, not historical ownership.
    Pixel changes cover the entire cursor interval; only an isolated group
    interval permits interpreting outside-area changes as group leakage.
    """
    with session._lock:
        if type(before_cursor) is not int or type(after_cursor) is not int or not 0<=before_cursor<after_cursor<=session.history_cursor:
            raise ValueError("require 0 <= before < after <= current cursor")
        cursor=session.history_cursor
        state=session.drawing_state_hash()
        profile=session._require_render_profile()
        digest=profile.digest()
        plans,groups=_plans_and_strokes(session.current_ir().strokes)
        selected=list(area_ids) if area_ids is not None else sorted(plans)
        if not selected or any(k not in plans for k in selected) or len(set(selected))!=len(selected):
            raise ValueError("unique requested live tonal plans required")
        with TemporaryDirectory() as folder:
            paths=[Path(folder)/f"{n}.png" for n in (0,before_cursor,after_cursor)]
            for n,path in zip((0,before_cursor,after_cursor),paths):
                if not path.exists():
                    session.render_at(n,path)
            paper,before,after=(gray(p) for p in paths)
        arrays=_delta_arrays(paper,before,after,profile.output_scale,coverage_threshold,saturation_threshold)
        del paper,before,after
        results=[]
        for key in selected:
            r=_measure_delta(arrays,plans[key],scale=profile.output_scale,
                             coverage_threshold=coverage_threshold,saturation_threshold=saturation_threshold)
            r["current_stroke_diagnostics"]=_stroke_diagnostics(groups[key],plans[key])
            results.append(r)
        separation=_separation(arrays,{k:plans[k] for k in selected},separation_pairs,profile.output_scale)
        if session.history_cursor!=cursor or session.drawing_state_hash()!=state or session.render_profile.digest()!=digest:
            raise RuntimeError("session changed during tonal inspection")
        return {"scope":"current plans, canonical cursor interval, diagnostic only",
                "before_cursor":before_cursor,"after_cursor":after_cursor,
                "current_state_hash":state,"profile_digest":digest,
                "coverage_threshold":coverage_threshold,"saturation_threshold":saturation_threshold,
                "attribution_warning":"outside change includes all interval edits; use isolated group intervals; centerline samples are approximate, not raster contribution; plan targets are intent, not calibrated luminance",
                "centerline_sample_spacing_canvas":2.0,
                "areas":results,"separation":separation,"artistic_verdict":"NOT_EVALUATED"}


__all__=["inspect_tonal_interval"]
