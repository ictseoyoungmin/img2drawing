"""Developer-only tonal QA for real DrawingSession histories.

This is a measurement tool, not a raster authoring backend or artistic judge.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np
from PIL import Image

from img2drawing import DrawingSession
from img2drawing.authoring import TONAL_AREA_SCHEMA, TonalAreaPlan

PLAN_FIELDS = (
    "area_id", "part", "reference_evidence", "boundary", "direction_degrees",
    "target_density", "target_value", "pressure_range", "highlight_reserves",
)


def plans_from_current_strokes(session):
    """Inspect a single current IR snapshot, rather than resolving each stroke."""
    plans = {}
    for stroke in session.current_ir().strokes:
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
    return plans


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


def measure_plan(paper, before, after, plan, *, scale=1,
                 coverage_threshold=8/255, saturation_threshold=.65):
    """Measure paper-relative darkness, not a calibrated perceptual target score."""
    if paper.ndim != 2 or not (paper.shape == before.shape == after.shape):
        raise ValueError("paper/before/after must have the same 2D shape")
    if not all(np.isfinite(a).all() and (a >= 0).all() and (a <= 1).all()
               for a in (paper, before, after)):
        raise ValueError("luminance arrays must be finite and in [0,1]")
    if (not 0 < coverage_threshold < saturation_threshold <= 1
            or not np.isfinite(scale) or scale <= 0):
        raise ValueError("invalid measurement thresholds or scale")
    area = polygon_mask(paper.shape, plan.boundary, scale)
    reserve = np.zeros_like(area)
    for polygon in plan.highlight_reserves:
        reserve |= polygon_mask(paper.shape, polygon, scale)
    target, protected = area & ~reserve, reserve & area
    if not target.any():
        raise ValueError(f"no target pixels: {plan.area_id}")
    d0, d1 = np.maximum(paper-before, 0), np.maximum(paper-after, 0)
    added, removed = np.maximum(d1-d0, 0), np.maximum(d0-d1, 0)

    def stats(d, m):
        if not m.any():
            return None
        v = d[m]
        return {
            "mean_darkness": float(v.mean()),
            # Suppress floating roundoff at the exact strict threshold.
            "coverage": float((v > coverage_threshold + 1e-12).mean()),
            "saturation": float((v > saturation_threshold + 1e-12).mean()),
        }

    added_mass = float(added.sum(dtype=np.float64))
    return {
        "area_id": plan.area_id, "plan_digest": plan.digest(),
        "target_pixels": int(target.sum()), "protected_pixels": int(protected.sum()),
        "reserve_outside_area_pixels": int((reserve & ~area).sum()),
        "target_before": stats(d0, target), "target_after": stats(d1, target),
        "protected_before": stats(d0, protected), "protected_after": stats(d1, protected),
        "target_added_mean": float(added[target].mean()),
        "target_removed_mean": float(removed[target].mean()),
        "outside_added_darkness_fraction": (
            float(added[~area].sum(dtype=np.float64))/added_mass if added_mass else None
        ),
    }


def audit(session, before_cursor, after_cursor, area_ids=None):
    """Measure an authoritative cursor interval against live authored plans.

    Plans are current, not historical snapshots. Outside-area changes are not
    per-stroke attribution; only an isolated group interval supports leakage review.
    """
    if not 0 <= before_cursor < after_cursor <= session.history_cursor:
        raise ValueError("require 0 <= before < after <= current cursor")
    cursor = session.history_cursor
    state = session.drawing_state_hash()
    profile = session.render_profile
    digest = profile.digest()
    plans = plans_from_current_strokes(session)
    selected = list(area_ids) if area_ids is not None else sorted(plans)
    if not selected or any(k not in plans for k in selected):
        raise ValueError("no requested live tonal plans found")
    if len(set(selected)) != len(selected):
        raise ValueError("duplicate area selection")
    with TemporaryDirectory() as folder:
        paths = [Path(folder)/f"{n}.png" for n in (0, before_cursor, after_cursor)]
        for n, path in zip((0, before_cursor, after_cursor), paths):
            if not path.exists():
                session.render_at(n, path)
        paper, before, after = (gray(p) for p in paths)
    if (session.history_cursor != cursor or session.drawing_state_hash() != state
            or session.render_profile.digest() != digest):
        raise RuntimeError("session changed during tonal inspection")
    return {
        "scope": "current plans, canonical cursor interval, diagnostic only",
        "before_cursor": before_cursor, "after_cursor": after_cursor,
        "current_state_hash": state, "profile_digest": digest,
        "coverage_threshold": 8/255, "saturation_threshold": .65,
        "attribution_warning": (
            "outside change includes all interval edits; use isolated group intervals; "
            "plan targets are authored intent, not measured luminance targets"
        ),
        "areas": [
            measure_plan(paper, before, after, plans[k], scale=profile.output_scale)
            for k in selected
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--session", type=Path, required=True)
    parser.add_argument("--subject", type=Path, required=True)
    parser.add_argument("--before", type=int, required=True)
    parser.add_argument("--after", type=int, required=True)
    parser.add_argument("--area", action="append")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    session = DrawingSession.resume(args.session, subject=args.subject)
    report = audit(session, args.before, args.after, args.area)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False)+"\n",
                        encoding="utf-8")
    print(f'measured {len(report["areas"])} explicitly planned tonal areas; no artistic verdict')


if __name__ == "__main__":
    main()
