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
    typical_width: float
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
            'typical_width':self.typical_width,
            'authority':self.authority,
            'rule':'Guidance only; runtime never silently rewrites Agent-authored stroke style.',
            'note':'An early stage is not a faint stage. These are floors from a completed run, not ceilings.',
        }

# Calibrated against a completed dogfood run rather than guessed. Every stage's
# strokes there sat far above the old table, which was telling workers that a
# barely-visible P1 was acceptable.
_OPACITY={'P1_gesture':0.55,'P2_primary_axes':0.60,'P3_primary_masses':0.66,'P4_structural_connections':0.58,'P5_clean_blockin':0.62}
_PRESSURE={'P1_gesture':0.45,'P2_primary_axes':0.48,'P3_primary_masses':0.54,'P4_structural_connections':0.48,'P5_clean_blockin':0.52}
_WIDTH={'P1_gesture':2.0,'P2_primary_axes':2.2,'P3_primary_masses':2.5,'P4_structural_connections':2.1,'P5_clean_blockin':2.3}

def canvas_scale_guidance(width: int, height: int, stage: str) -> CanvasScaleGuidance:
    w=max(1,int(width)); h=max(1,int(height)); sid=str(stage)
    # 720 px longest-side is the neutral authoring scale. sqrt keeps growth moderate.
    factor=max(1.0,sqrt(max(w,h)/720.0))
    return CanvasScaleGuidance(
        width=w,height=h,stage=sid,
        scale_factor=round(factor,3),
        recommended_width_multiplier=round(factor,3),
        minimum_visible_opacity=_OPACITY.get(sid,0.55),
        minimum_visible_pressure=_PRESSURE.get(sid,0.45),
        typical_width=round(_WIDTH.get(sid,2.1)*factor,2),
    )
