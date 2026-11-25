"""Explicit local pressure correction proposals for observed tonal residuals."""
from __future__ import annotations

from dataclasses import dataclass
import math

from .stroke_edits import StrokeEdit


@dataclass(frozen=True)
class TonalPressureAdjustment:
    stroke_id: str
    start_index: int
    end_index: int
    factor: float
    feather_points: int=0

    def __post_init__(self):
        if not isinstance(self.stroke_id,str) or not self.stroke_id.strip():
            raise ValueError("current stroke ID required")
        if (type(self.start_index) is not int or type(self.end_index) is not int
                or not 0<=self.start_index<=self.end_index):
            raise ValueError("valid inclusive point range required")
        f=float(self.factor)
        if not math.isfinite(f) or not 0<=f<=1:
            raise ValueError("attenuation factor must be in [0,1]")
        object.__setattr__(self,"factor",f)
        if type(self.feather_points) is not int or self.feather_points<0:
            raise ValueError("nonnegative integer feather_points required")


def prepare_tonal_pressure_edits(session,adjustments):
    """Prepare geometry-identical StrokeEdits; no automatic area-to-stroke generation.

    Each adjustment is explicitly selected by the agent. Overlapping adjustments
    compound multiplicatively. Use the normal preview/apply API, with evidence
    and stale checks, to commit the resulting ordinary replacement actions.
    """
    changes=tuple(adjustments)
    if not changes or any(not isinstance(x,TonalPressureAdjustment) for x in changes):
        raise ValueError("nonempty TonalPressureAdjustment sequence required")
    with session._lock:
        current={s.stroke_id:s for s in session.current_ir().strokes}
        profiles={}
        for x in changes:
            if x.stroke_id not in current:
                raise ValueError("unknown current stroke")
            s=current[x.stroke_id]
            if s.pressure is None or len(s.pressure)!=len(s.points) or x.end_index>=len(s.points):
                raise ValueError("adjustment requires aligned pressure and valid point range")
            p=profiles.setdefault(x.stroke_id,list(s.pressure))
            start,end=x.start_index,x.end_index
            for i in range(start,end+1):
                p[i]*=x.factor
            for k in range(1,min(x.feather_points,len(p)-1)+1):
                weight=(x.feather_points-k+1)/(x.feather_points+1)
                factor=1-(1-x.factor)*weight
                if start-k>=0:
                    p[start-k]*=factor
                if end+k<len(p):
                    p[end+k]*=factor
        return tuple(StrokeEdit(sid,tuple(current[sid].points),tuple(p)) for sid,p in profiles.items())
