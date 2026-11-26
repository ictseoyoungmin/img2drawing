"""Bounded, explicitly corresponding value patches; never author marks or judge likeness."""
from __future__ import annotations

from dataclasses import dataclass
import math
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Sequence

import numpy as np

from ..core.digest import sha256_file
from .model import Box, _box
from .tonal import gray, _verified_cached_renders


@dataclass(frozen=True)
class TonalPatch:
    """One agent-selected visible value region in each native coordinate space.

    Boxes are independent because the drawing's proportions may differ. Their
    correspondence is an observation, not an automatically solved registration.
    """
    label: str
    subject_box: Box
    canvas_box: Box

    def __post_init__(self):
        if not isinstance(self.label, str) or not self.label.strip():
            raise ValueError("patch label must be non-empty")
        object.__setattr__(self, "label", self.label.strip())
        object.__setattr__(self, "subject_box", _box(self.subject_box))
        object.__setattr__(self, "canvas_box", _box(self.canvas_box))


def _inputs(patches, deadband, output_scale):
    patches = tuple(patches)
    if not 2 <= len(patches) <= 64 or any(not isinstance(p, TonalPatch) for p in patches):
        raise ValueError("choose an ordered chain of 2–64 TonalPatch objects")
    if len({p.label for p in patches}) != len(patches):
        raise ValueError("patch labels must be unique")
    if type(output_scale) is not int or output_scale < 1:
        raise ValueError("output_scale must be a positive integer")
    if isinstance(deadband, bool) or not math.isfinite(float(deadband)) or not 0 <= float(deadband) < 1:
        raise ValueError("deadband must be finite and in [0,1)")
    return patches, float(deadband)


def _slices(box, shape, scale=1):
    h, w = shape
    x0, y0, x1, y1 = (v * scale for v in box)
    if x0 < 0 or y0 < 0 or x1 > w or y1 > h:
        raise ValueError("patch box outside its image")
    # Include pixel centers in [left,right) × [top,bottom); never silently clip.
    x0, y0, x1, y1 = (math.ceil(v - .5) for v in (x0, y0, x1, y1))
    if x0 >= x1 or y0 >= y1:
        raise ValueError("patch contains no pixel centers")
    return np.s_[y0:y1, x0:x1]


def _stats(values):
    q = np.quantile(values, [.1, .5, .9])
    return {"pixels": int(values.size), "mean_darkness": float(values.mean()),
            "p10": float(q[0]), "p50": float(q[1]), "p90": float(q[2])}


def _chain(values, deadband):
    differences = np.diff(values)
    signs = [1 if d > deadband else -1 if d < -deadband else 0 for d in differences]
    nonflat = [s for s in signs if s]
    return signs, {"mean_darkness": float(np.mean(values)),
                   "span": float(np.ptp(values)),
                   "total_adjacent_variation": float(np.abs(differences).sum()),
                   "direction_reversals": sum(a != b for a, b in zip(nonflat, nonflat[1:]))}


def _measure(subject, drawing, paper, patches, deadband, output_scale):
    if drawing.shape != paper.shape:
        raise ValueError("drawing and blank paper dimensions differ")
    rows = []
    for p in patches:
        rs = _slices(p.subject_box, subject.shape)
        ds = _slices(p.canvas_box, drawing.shape, output_scale)
        rows.append({"label": p.label, "subject_box": list(p.subject_box),
                     "canvas_box": list(p.canvas_box),
                     "reference": _stats(1 - subject[rs]),
                     "drawing": _stats(np.maximum(paper[ds] - drawing[ds], 0))})
    ref = np.array([p["reference"]["mean_darkness"] for p in rows])
    draw = np.array([p["drawing"]["mean_darkness"] for p in rows])
    ref_signs, ref_stats = _chain(ref, deadband)
    draw_signs, draw_stats = _chain(draw, deadband)
    relations = []
    names = {-1: "lighter", 0: "similar", 1: "darker"}
    for i, (r, d) in enumerate(zip(ref_signs, draw_signs)):
        relations.append({"from": rows[i]["label"], "to": rows[i+1]["label"],
                          "reference_delta": float(ref[i+1] - ref[i]),
                          "drawing_delta": float(draw[i+1] - draw[i]),
                          "reference_relation": names[r], "drawing_relation": names[d],
                          "opposite_order": r * d == -1})
    return {"scope": "agent-selected tonal chain, diagnostic only",
            "deadband": deadband, "output_scale": output_scale, "patches": rows,
            "reference_chain": ref_stats, "drawing_chain": draw_stats,
            "adjacent_relations": relations,
            "interpretation": "Reference darkness is 1 minus grayscale luminance; drawing darkness is relative to blank paper. Compare relations, not absolute photographic values. Reversals omit deadband-flat steps; all results depend on selected patches and order.",
            "artistic_verdict": "NOT_EVALUATED"}


def compare_tonal_patches(subject, drawing, paper, patches: Sequence[TonalPatch], *,
                          output_scale=1, deadband=8/255):
    """Measure saved images without claiming that their provenance is canonical.

    subject_box is in original reference pixels; canvas_box is in
    unscaled drawing canvas coordinates. Use the matching blank paper and
    output scale. No pixels are copied into the drawing and no target is inferred.
    """
    patches, deadband = _inputs(patches, deadband, output_scale)
    result = _measure(gray(subject), gray(drawing), gray(paper), patches, deadband, output_scale)
    result["evidence_binding"] = "external_images_unverified"
    result["image_sha256"] = {k: sha256_file(Path(p)) for k, p in
                               (("subject", subject), ("drawing", drawing), ("paper", paper))}
    return result


def inspect_tonal_patches(session, patches: Sequence[TonalPatch], *, cursors=None,
                          deadband=8/255, cached_renders=None):
    """Read one or more canonical cursor renders using the same explicit patch chain.

    Trusted supplied cache entries undergo the same history/profile/pixel
    validation as inspect_tonal_interval. Missing entries render normally.
    No observation or history mutation is performed. The caller decides how
    to route the measured discrepancy.
    """
    with session._lock:
        if session.subject is None:
            raise ValueError("tonal patch comparison requires a reference image")
        session._assert_subject_current()
        cursor = session.history_cursor
        state = session.drawing_state_hash()
        profile = session._require_render_profile()
        patches, deadband = _inputs(patches, deadband, profile.output_scale)
        selected = (cursor,) if cursors is None else tuple(cursors)
        if (not 1 <= len(selected) <= 8 or any(type(n) is not int or not 0 <= n <= cursor for n in selected)
                or len(set(selected)) != len(selected)):
            raise ValueError("choose 1–8 unique valid integer cursors")
        subject = gray(session.subject)
        canvas_shape = (profile.canvas_height * profile.output_scale,
                        profile.canvas_width * profile.output_scale)
        for p in patches:
            _slices(p.subject_box, subject.shape)
            _slices(p.canvas_box, canvas_shape, profile.output_scale)
        requested = tuple(dict.fromkeys((0, *selected)))
        cached = _verified_cached_renders(session, profile, cached_renders, set(requested))
        with TemporaryDirectory() as folder:
            def load(n):
                path = cached.get(n, Path(folder) / f"{n}.png")
                if n not in cached and not path.exists():
                    session.render_at(n, path)
                return gray(path)
            paper = load(0)
            results = [{"cursor": n, **_measure(subject, load(n), paper, patches,
                                                deadband, profile.output_scale)} for n in selected]
        session._assert_subject_current()
        if session.history_cursor != cursor or session.drawing_state_hash() != state or session.render_profile.digest() != profile.digest():
            raise RuntimeError("session changed during tonal patch inspection")
        return {"scope": "explicit corresponding patches across canonical cursor renders",
                "evidence_binding": "canonical_session", "current_state_hash": state,
                "profile_digest": profile.digest(), "subject_sha256": sha256_file(session.subject),
                "render_inputs": [{"cursor": n, "source": "verified_cached_artifact" if n in cached else "rendered"} for n in requested],
                "results": results, "artistic_verdict": "NOT_EVALUATED"}


__all__ = ["TonalPatch", "compare_tonal_patches", "inspect_tonal_patches"]
