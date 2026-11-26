"""Read-only diagnostics of explicitly selected graphite contacts before ordered lifts."""
from __future__ import annotations

from itertools import combinations
import math

import numpy as np

from .model import _box
from .tonal_patches import _slices


def inspect_contact_overlap(session, stroke_ids, canvas_box, *, axis="x", bins=16,
                            threshold=8/255, max_pixel_work=100_000_000):
    """Measure isolated *actual* renderer patch alphas inside a selected canvas ROI.

    The caller declares the group and cross-strip direction. Each patch is built
    using the bound profile, grade, hand dynamics, pressure, width and page seed.
    Overlap counts ignore all other marks and subsequent spatial erasure, and
    describe supersampled deposition, not the downsampled final drawing or a
    causal attribution of a visible tonal band. Never mutate or recommend marks.
    """
    if isinstance(stroke_ids, str):
        raise ValueError("choose 2–12 distinct current graphite stroke IDs")
    ids = tuple(stroke_ids)
    if (not 2 <= len(ids) <= 12 or any(not isinstance(s, str) or not s.strip() for s in ids)
            or len(set(ids)) != len(ids)):
        raise ValueError("choose 2–12 distinct current graphite stroke IDs")
    box = _box(canvas_box)
    if axis not in ("x", "y") or type(bins) is not int or not 4 <= bins <= 64:
        raise ValueError("choose x/y and 4–64 strips")
    if isinstance(threshold, bool) or not math.isfinite(float(threshold)) or not 0 < float(threshold) < 1:
        raise ValueError("threshold must be finite and in (0,1)")
    threshold = float(threshold)
    if type(max_pixel_work) is not int or max_pixel_work <= 0:
        raise ValueError("positive integer pixel-work budget required")
    # Import here: render.artifact imports inspection during package initialization.
    from ..render.pencil import build_patch, is_eraser, load_contact_profile, prepare_stroke

    with session._lock:
        cursor, state = session.history_cursor, session.drawing_state_hash()
        profile = session.render_profile
        factor = profile.output_scale * profile.supersample
        w, h = profile.canvas_width * factor, profile.canvas_height * factor
        ys, xs = _slices(box, (h, w), factor)
        x0, x1, y0, y1 = xs.start, xs.stop, ys.start, ys.stop
        if box[2 if axis == "x" else 3] - box[0 if axis == "x" else 1] < bins:
            raise ValueError("each strip requires at least one native canvas pixel")
        size = (y1-y0, x1-x0)
        roi_pixels = size[0]*size[1]
        # Conservative raster-area budget, not an upper bound on stroke-kernel CPU time.
        work = len(ids)*w*h + (len(ids)+len(ids)*(len(ids)-1)//2+3)*roi_pixels
        if work > max_pixel_work:
            raise ValueError(f"contact overlap pixel-work budget exceeded: {work}")
        ir = session.current_ir()
        strokes = {s.stroke_id:s for s in ir.strokes}
        if any(i not in strokes or is_eraser(strokes[i]) for i in ids):
            raise ValueError("contact overlap requires current graphite stroke IDs, not erasers")
        contact = load_contact_profile(profile.renderer_version)
        masks = []
        for sid in ids:
            s = prepare_stroke(strokes[sid], None, contact)
            bounds, patch = build_patch(s, factor=float(factor), hi_size=(w,h),
                tooth=profile.paper_tooth, paper_scale=profile.paper_scale, paper_seed=profile.paper_seed,
                graphite=profile.graphite_rgb, profile=contact)
            mask = np.zeros(size, dtype=np.uint8)
            try:
                bx, by, ex, ey = bounds
                a,b,c,d = max(x0,bx), max(y0,by), min(x1,ex), min(y1,ey)
                if a<c and b<d:
                    with patch.getchannel("A") as alpha:
                        with alpha.crop((a-bx,b-by,c-bx,d-by)) as crop:
                            mask[b-y0:d-y0,a-x0:c-x0] = np.asarray(crop)
            finally:
                patch.close()
            masks.append(mask)
        count = np.zeros(size, dtype=np.uint8)
        remaining = np.ones(size, dtype=np.float32)
        cutoff = threshold*255
        rows = []
        for sid,mask in zip(ids,masks):
            support = mask>cutoff
            count += support
            remaining *= 1-mask.astype(np.float32)/255
            rows.append({"stroke_id":sid,"covered_fraction":float(support.mean()),
                         "mean_isolated_alpha":float(mask.mean()/255)})
        def stats(c,r):
            return {"uncovered_fraction":float((c==0).mean()),
                    "single_fraction":float((c==1).mean()),
                    "multiple_fraction":float((c>=2).mean()),
                    "mean_contact_count":float(c.mean()),
                    "mean_selected_alpha_union":float(1-r.mean(dtype=np.float64))}
        pairs=[]
        for i,j in combinations(range(len(ids)),2):
            a,b=masks[i],masks[j]
            common=(a>cutoff)&(b>cutoff)
            either=(a>cutoff)|(b>cutoff)
            pairs.append({"stroke_ids":[ids[i],ids[j]],"overlap_fraction":float(common.mean()),
                          "support_iou":float(common.sum()/either.sum()) if either.any() else None,
                          "mean_min_alpha":float(np.minimum(a,b).mean()/255)})
        # Same physical boxes as matched band probes; partition by pixel centers,
        # rather than splitting an already-rounded ROI into unequal coordinates.
        dim=0 if axis=="x" else 1
        start,end=box[dim],box[dim+2]
        strips=[]
        for j in range(bins):
            bounds=list(box)
            bounds[dim]=start+(end-start)*j/bins
            bounds[dim+2]=start+(end-start)*(j+1)/bins
            sy,sx=_slices(bounds,(h,w),factor)
            sel=np.s_[sy.start-y0:sy.stop-y0,sx.start-x0:sx.stop-x0]
            strips.append({"strip":j+1,"canvas_box":bounds,**stats(count[sel],remaining[sel])})
        if session.history_cursor!=cursor or session.drawing_state_hash()!=state or session.render_profile.digest()!=profile.digest():
            raise RuntimeError("session changed during contact overlap inspection")
        return {"cursor":cursor,"current_state_hash":state,"profile_digest":profile.digest(),
                "canvas_box":list(box),"axis":axis,"bins":bins,"threshold":threshold,
                "supersample_factor":factor,"roi_pixels":roi_pixels,"raster_work_estimate":work,
                "stroke_ids":list(ids),"strokes":rows,"pairs":pairs,"strips":strips,
                "summary":stats(count,remaining),"evidence_binding":"isolated canonical graphite patches",
                "interpretation":"Selected supersampled deposit alpha before ordered erasure, without unselected marks; alpha union is analytical, not final RGBA. Compare matched tonal bands and observed form. No inferred cause or artistic verdict.",
                "artistic_verdict":"NOT_EVALUATED"}


__all__=["inspect_contact_overlap"]
