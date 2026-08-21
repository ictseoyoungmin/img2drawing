from __future__ import annotations
from dataclasses import dataclass
from math import sqrt

@dataclass(frozen=True)
class CanvasScaleGuidance:
    width: int
    height: int
    stage: str
    scale_factor: float
    recommended_width_multiplier: float
    minimum_visible_opacity: float
    minimum_visible_pressure: float
    authority: str = 'guidance_only'

    def to_dict(self):
        return {
            'schema':'img2drawing.canvas_scale_guidance.v1',
            'canvas':[self.width,self.height],
            'stage':self.stage,
            'scale_factor':self.scale_factor,
            'recommended_width_multiplier':self.recommended_width_multiplier,
            'minimum_visible_opacity':self.minimum_visible_opacity,
            'minimum_visible_pressure':self.minimum_visible_pressure,
            'authority':self.authority,
            'rule':'Guidance only; runtime never silently rewrites Agent-authored stroke style.',
        }

_OPACITY={'P1_gesture':0.18,'P2_primary_axes':0.23,'P3_primary_masses':0.34,'P4_structural_connections':0.38,'P5_clean_blockin':0.48}
_PRESSURE={'P1_gesture':0.18,'P2_primary_axes':0.22,'P3_primary_masses':0.30,'P4_structural_connections':0.34,'P5_clean_blockin':0.42}

def canvas_scale_guidance(width: int, height: int, stage: str) -> CanvasScaleGuidance:
    w=max(1,int(width)); h=max(1,int(height)); sid=str(stage)
    # 720 px longest-side is the neutral authoring scale. sqrt keeps growth moderate.
    factor=max(1.0,sqrt(max(w,h)/720.0))
    return CanvasScaleGuidance(
        width=w,height=h,stage=sid,
        scale_factor=round(factor,3),
        recommended_width_multiplier=round(factor,3),
        minimum_visible_opacity=_OPACITY.get(sid,0.28),
        minimum_visible_pressure=_PRESSURE.get(sid,0.25),
    )
