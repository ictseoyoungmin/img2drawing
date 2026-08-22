import sys
from pathlib import Path
sys.path.insert(0,'/home/claude/work/croquis')
from img2drawing import DrawingRun, DrawingAction
run=DrawingRun.resume(Path("/home/claude/work/croquis/out"))
sess=run.session
ST="P6_identity_finish"
ir=sess.current_ir()
by={s.part:s for s in ir.strokes}

# 1) segment-lift the construction that still crosses the face
seg=[]
def SL(aid,target,a,b,reason):
    return {"action_id":aid,"kind":"soft_lift_segment","stage":ST,"target_stroke_id":target,
            "revision_of":target,"segment_start":a,"segment_end":b,"feather_points":1,
            "tool":{"preset":"soft_eraser","grade":"HB","overrides":{"erase_strength":0.85}},
            "strength":0.85,"observation_id":"obs-"+aid,
            "source_observation":"Fresh inspection of the finished head at four-times supersample.",
            "reason":reason}
seg.append(SL("CF-S1","head_cross_axis",0,5,
  "The retired P2 head cross-axis still runs straight across both eyes and competes with the lash lines; its face-crossing segment is lifted further."))
seg.append(SL("CF-S2","crown_face_spine_support",0,10,
  "The surviving P1 gesture is kept for the weight path, but its craniofacial segment now cuts through the drawn features, so only that segment is lifted."))
sess.execute_many_atomic([DrawingAction.from_dict(a) for a in seg], label="face-clarify")

# 2) confirmation pass: go over the identity marks a second time, as with a real pencil
BOOST={
 "hair_bang_long_right":(.80,2.0,.66),"hair_bang_second":(.66,1.7,.56),
 "hair_bang_near_eye":(.70,1.8,.58),"hair_lock_left_outer":(.62,1.7,.54),
 "hair_lock_right_outer":(.62,1.7,.54),"hair_tips_left":(.72,1.8,.60),
 "hair_tips_right":(.72,1.8,.60),"hair_part_crown":(.60,1.6,.50),
 "hair_neck_strand":(.56,1.5,.48),"hair_stray_top":(.48,1.3,.40),
 "nose":(.72,1.6,.58),"mouth_upper":(.84,1.8,.66),"mouth_lower":(.64,1.5,.52),
 "ear_outer":(.78,1.8,.62),"ear_inner":(.58,1.4,.48),
 "collar_top":(.82,2.0,.66),"collar_fold":(.68,1.7,.56),
 "shoulder_patch":(.82,1.9,.66),"patch_emblem_wings_left":(.72,1.5,.56),
 "patch_emblem_wings_right":(.72,1.5,.56),"patch_emblem_centre":(.72,1.5,.56),
 "sling_edge_outer":(.80,1.9,.64),"sling_edge_inner":(.80,1.9,.64),
 "sling_buckle_upper":(.82,1.9,.66),"sling_buckle_lower":(.82,1.9,.66),
 "side_pouch_right":(.76,1.8,.62),"side_pouch_strap":(.68,1.5,.56),
 "belt_lower_edge":(.82,2.0,.66),"belt_keeper_a":(.70,1.6,.56),"belt_keeper_b":(.70,1.6,.56),
 "cargo_pocket":(.82,1.9,.66),"cargo_pocket_flap":(.70,1.6,.56),"cargo_pocket_snap":(.80,1.8,.64),
 "thigh_strap":(.82,2.0,.66),"thigh_pouch_flap":(.70,1.6,.56),"thigh_pouch_strap":(.70,1.6,.56),
 "sleeve_cuff_right":(.76,1.8,.62),"jacket_hem_corner":(.68,1.7,.56),
 "sock_top_band_left":(.60,1.5,.50),"sock_top_band_right":(.60,1.5,.50),
 "lace_line_left":(.80,1.8,.64),"lace_line_right":(.80,1.8,.64),
 "lace_loose_left":(.68,1.5,.56),"lace_loose_right":(.68,1.5,.56),
 "boot_sole_band_left":(.86,2.2,.70),"boot_sole_band_right":(.86,2.2,.70),
 "boot_toe_cap_right":(.66,1.5,.54),
 "suppressor_band_a":(.74,1.7,.60),"suppressor_band_b":(.74,1.7,.60),
 "scope_ring_front":(.84,2.0,.68),"scope_ring_rear":(.84,2.0,.68),
 "scope_objective":(.84,2.0,.68),"scope_turret":(.84,2.0,.68),
 "handguard_slot_a":(.64,1.5,.52),"handguard_slot_b":(.64,1.5,.52),"handguard_slot_c":(.64,1.5,.52),
 "magazine":(.82,1.9,.66),"stock_cutout_second":(.82,1.9,.66),"stock_tube":(.68,1.6,.56),
}
for k in ["lace_rung_l1","lace_rung_l2","lace_rung_l3","lace_rung_l4",
          "lace_rung_r1","lace_rung_r2","lace_rung_r3","lace_rung_r4"]:
    BOOST[k]=(.72,1.6,.58)
for k in ["sole_lug_l1","sole_lug_l2","sole_lug_l3","sole_lug_l4",
          "sole_lug_r1","sole_lug_r2","sole_lug_r3","sole_lug_r4"]:
    BOOST[k]=(.68,1.5,.56)

acts=[]
for i,(part,(op,w,pr)) in enumerate(BOOST.items(),1):
    s=by[part]
    acts.append({
      "action_id":f"CF-{i:03d}","kind":"replace_stroke","stage":ST,
      "role":s.role,"part":part,"points":[list(p) for p in s.points],
      "target_stroke_id":part,"stroke_id":part,"revision_of":part,
      "confidence":.9,"layer":30,
      "tool":{"preset":"construction_pencil","grade":s.tool_state.get("grade","B") if isinstance(s.tool_state,dict) else "B",
              "overrides":{"pressure":pr,"width":w,"opacity":op,"jitter":0.035}},
      "observation_id":f"obs-CF-{i:03d}",
      "source_observation":"Second look at the finished drawing at full render scale.",
      "reason":("Confirmation pass: this identifying mark was authored too lightly to survive against the "
                "decisive contour, so it is gone over a second time, the way a pencil drawing is confirmed "
                "once the structure is trusted."),
    })
sess.execute_many_atomic([DrawingAction.from_dict(a) for a in acts], label="identity-confirm")
run.canvas.sync(sess.history)
run.canvas.render("/home/claude/work/final_croquis.png", supersample=4)
print("confirmed",len(acts))
