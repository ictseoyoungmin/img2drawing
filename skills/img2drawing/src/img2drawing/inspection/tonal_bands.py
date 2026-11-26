"""Explicit strip probes for repeated tonal bands on a selected visible plane."""
from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from .model import Box, _box
from .tonal_patches import TonalPatch, inspect_tonal_patches, compare_tonal_patches


@dataclass(frozen=True)
class TonalBandProbe:
    """Matched rectangular regions divided across an explicitly chosen direction.

    Average along each strip to reduce grain, then compare the cross-strip
    relationships. The caller chooses one plane and the direction; neither
    the form nor a causal stroke is inferred.
    """
    label: str
    subject_box: Box
    canvas_box: Box
    axis: str
    bins: int = 16

    def __post_init__(self):
        if not isinstance(self.label,str) or not self.label.strip():
            raise ValueError("band probe requires a nonempty label")
        if self.axis not in ("x","y") or type(self.bins) is not int or not 4<=self.bins<=64:
            raise ValueError("band probe requires x/y axis and 4–64 strips")
        object.__setattr__(self,"subject_box",_box(self.subject_box))
        object.__setattr__(self,"canvas_box",_box(self.canvas_box))
        for box in (self.subject_box,self.canvas_box):
            i=0 if self.axis=="x" else 1
            if box[i+2]-box[i]<self.bins:
                raise ValueError("band strips require at least one native pixel each")

    def patches(self):
        i=0 if self.axis=="x" else 1
        def interval(box,j):
            b=list(box); span=box[i+2]-box[i]
            b[i]=box[i]+span*j/self.bins
            b[i+2]=box[i]+span*(j+1)/self.bins
            return tuple(b)
        return tuple(TonalPatch(f"{self.label}:{j+1:02d}",interval(self.subject_box,j),interval(self.canvas_box,j))
                     for j in range(self.bins))

    def summarize(self, chain):
        """Summarize an existing canonical or prospective matched-chain result."""
        expected=self.patches(); rows=chain["patches"]
        if len(rows)!=len(expected) or any(
            r["label"]!=p.label or tuple(r["subject_box"])!=p.subject_box or tuple(r["canvas_box"])!=p.canvas_box
            for r,p in zip(rows,expected)):
            raise ValueError("tonal chain does not match this strip probe")
        deadband=float(chain["deadband"])
        if not np.isfinite(deadband) or not 0<=deadband<1:
            raise ValueError("invalid chain deadband")
        def stats(which):
            v=np.array([r[which]["mean_darkness"] for r in rows],dtype=float)
            if not np.all(np.isfinite(v)) or np.any(v<0) or np.any(v>1):
                raise ValueError("invalid strip darkness values")
            d=np.diff(v)
            turns={i+1:("peak" if a>0 else "trough") for i,(a,b) in enumerate(zip(d,d[1:]))
                   if abs(a)>deadband and abs(b)>deadband and a*b<0}
            return v,d,turns,{"mean_darkness":float(v.mean()),"total_adjacent_variation":float(np.abs(d).sum()),
                    "mean_absolute_second_difference":float(np.mean(np.abs(np.diff(d)))),
                    "prominent_turns":len(turns),"turns":[{"strip":i+1,"kind":k} for i,k in turns.items()]}
        r,rd,rt,rs=stats("reference"); d,dd,dt,ds=stats("drawing")
        # A missing same-kind reference extremum at the identical strip is a
        # discrepancy candidate, not proof of an invented band. Misregistration,
        # real folds and highlight position shifts can produce this result.
        unmatched=[{"strip":i+1,"kind":kind} for i,kind in dt.items() if rt.get(i)!=kind]
        return {"label":self.label,"axis":self.axis,"bins":self.bins,"deadband":deadband,
                "reference":rs,"drawing":ds,"unmatched_drawing_turns":unmatched,
                "mean_absolute_delta_difference":float(np.mean(np.abs(dd-rd))),
                "interpretation":"Explicit corresponding strips; local turn positions are registration-sensitive. Compare with the image and actual form; no inferred cause, ranking or artistic pass.",
                "artistic_verdict":"NOT_EVALUATED"}


def inspect_tonal_bands(session, probe: TonalBandProbe, **kwargs):
    """Canonical, cache-verified, read-only strip inspection at chosen cursors."""
    if not isinstance(probe,TonalBandProbe):
        raise TypeError("TonalBandProbe required")
    result=inspect_tonal_patches(session,probe.patches(),**kwargs)
    for item in result["results"]:
        item["band_metrics"]=probe.summarize(item)
    return result


def compare_tonal_bands(subject,drawing,paper,probe:TonalBandProbe,**kwargs):
    """Read saved images; preserve their explicitly unverified provenance."""
    if not isinstance(probe,TonalBandProbe):
        raise TypeError("TonalBandProbe required")
    result=compare_tonal_patches(subject,drawing,paper,probe.patches(),**kwargs)
    result["band_metrics"]=probe.summarize(result)
    return result


__all__=["TonalBandProbe","inspect_tonal_bands","compare_tonal_bands"]
