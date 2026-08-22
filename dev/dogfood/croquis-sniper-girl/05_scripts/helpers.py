from __future__ import annotations

def S(action_id, stage, part, points, *, role="construction", pressure=.20,
      width=1.2, opacity=.26, grade="2H", preset="construction_pencil",
      confidence=.86, layer=10, source="", stroke_id=None,
      taper_in=None, taper_out=None, jitter=None, hardness=None, grain=None):
    ov = {"pressure": pressure, "width": width, "opacity": opacity}
    for k, v in (("taper_in", taper_in), ("taper_out", taper_out),
                 ("jitter", jitter), ("hardness", hardness), ("grain", grain)):
        if v is not None:
            ov[k] = v
    return {
        "action_id": action_id, "kind": "draw_stroke", "stage": stage,
        "role": role, "part": part, "points": points,
        "stroke_id": stroke_id or part, "confidence": confidence, "layer": layer,
        "tool": {"preset": preset, "grade": grade, "overrides": ov},
        "observation_id": "obs-" + action_id,
        "source_observation": source or "Direct observation of the subject photograph.",
    }


def R(action_id, stage, part, points, *, reason, role="construction",
      pressure=.24, width=1.4, opacity=.32, grade="HB",
      preset="construction_pencil", confidence=.9, layer=10, source="",
      taper_in=None, taper_out=None, jitter=None):
    ov = {"pressure": pressure, "width": width, "opacity": opacity}
    for k, v in (("taper_in", taper_in), ("taper_out", taper_out), ("jitter", jitter)):
        if v is not None:
            ov[k] = v
    return {
        "action_id": action_id, "kind": "replace_stroke", "stage": stage,
        "role": role, "part": part, "points": points,
        "target_stroke_id": part, "stroke_id": part, "revision_of": part,
        "confidence": confidence, "layer": layer,
        "tool": {"preset": preset, "grade": grade, "overrides": ov},
        "observation_id": "obs-" + action_id,
        "source_observation": source or "Fresh re-observation of the subject after review.",
        "reason": reason,
    }


def LIFT(action_id, stage, part, points, *, reason, strength=.5, width=14.0,
         source=""):
    return {
        "action_id": action_id, "kind": "soft_lift", "stage": stage,
        "role": "retirement", "part": part, "points": points,
        "stroke_id": part, "confidence": .9, "layer": 10,
        "tool": {"preset": "soft_eraser", "grade": "HB",
                 "overrides": {"width": width, "erase_strength": strength}},
        "observation_id": "obs-" + action_id,
        "source_observation": source or "Construction retirement after verified contour.",
        "reason": reason,
        "strength": strength,
    }
