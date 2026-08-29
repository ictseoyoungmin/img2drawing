import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(PROJECT_ROOT / "skills/img2drawing/src"))
from img2drawing import DrawingRun, DrawingAction
run=DrawingRun.resume(PROJECT_ROOT / "temp/dogfood/croquis-sniper-girl/run")
sess=run.session
ST='P6_identity_finish'

pol=[]
pol.append({"action_id":"PL-S1","kind":"soft_lift","stage":ST,"target_stroke_id":"head_cross_contour_brow",
  "confidence":1.0,"tool":{"preset":"soft_eraser","grade":"HB","overrides":{"erase_strength":0.85}},
  "metadata":{"strength":0.85},"observation_id":"obs-PL-S1",
  "source_observation":"Fresh look at the finished head.",
  "reason":"The P3 brow cross-contour still runs straight through both drawn eyes and reads as a scar; it is retired further now that the features carry the head's turn."})
sess.execute_many_atomic([DrawingAction.from_dict(a) for a in pol], label="brow-retire")

def W(aid,part,pts,src,op=.68,w=1.5,pr=.58,grade="2B"):
    return {"action_id":aid,"kind":"draw_stroke","stage":ST,"role":"detail","part":part,
            "points":pts,"stroke_id":part,"confidence":.88,"layer":31,
            "tool":{"preset":"construction_pencil","grade":grade,
                    "overrides":{"pressure":pr,"width":w,"opacity":op,"jitter":0.05}},
            "observation_id":"obs-"+aid,"source_observation":src}
wisp=[
 W("PL-W1","hair_wisp_l1",[[167,96],[159,104],[166,112]],"Wispy point on the image-left hair edge; the subject's bob ends in separated locks, not a smooth helmet curve."),
 W("PL-W2","hair_wisp_l2",[[167,120],[160,130],[170,132]],"Second wispy point lower on the image-left edge."),
 W("PL-W3","hair_wisp_l3",[[176,136],[170,147],[181,145]],"Third lock tip near the jaw on the image-left."),
 W("PL-W4","hair_wisp_l4",[[187,145],[183,157],[194,152]],"Lowest image-left lock tip, resting against the shoulder."),
 W("PL-W5","hair_wisp_r1",[[288,88],[296,92],[288,100]],"Wispy point on the image-right hair edge."),
 W("PL-W6","hair_wisp_r2",[[285,118],[292,127],[283,131]],"Second lock tip on the image-right."),
 W("PL-W7","hair_wisp_r3",[[279,134],[286,146],[276,146]],"Third lock tip on the image-right."),
 W("PL-W8","hair_wisp_r4",[[270,150],[276,161],[265,158]],"Lowest image-right lock tip, hanging below the jaw."),
 W("PL-W9","hair_wisp_top",[[228,40],[221,32],[230,37]],"Short flick at the crown where the parting lifts.",op=.50,w=1.2,pr=.44),
 W("PL-W10","hair_inner_strand_a",[[210,60],[206,80],[207,100]],"Inner strand group on the near side of the bob.",op=.52,w=1.3,pr=.46),
 W("PL-W11","hair_inner_strand_b",[[248,50],[254,70],[262,90]],"Inner strand group on the far side, running with the long bang.",op=.52,w=1.3,pr=.46),
]
sess.execute_many_atomic([DrawingAction.from_dict(a) for a in wisp], label="hair-wisps")
run.canvas.sync(sess.history)

ir2=sess.current_ir(); by2={s.part:s for s in ir2.strokes}
DARK={}
for p in ["nose","mouth_upper","mouth_lower","ear_outer","collar_top","shoulder_patch",
          "patch_emblem_wings_left","patch_emblem_wings_right","patch_emblem_centre",
          "sling_edge_outer","sling_edge_inner","sling_buckle_upper","sling_buckle_lower",
          "side_pouch_right","belt_lower_edge","cargo_pocket","cargo_pocket_flap","cargo_pocket_snap",
          "thigh_strap","sleeve_cuff_right","lace_line_left","lace_line_right",
          "boot_sole_band_left","boot_sole_band_right","scope_ring_front","scope_ring_rear",
          "scope_objective","scope_turret","magazine","stock_cutout_second",
          "suppressor_band_a","suppressor_band_b","hair_bang_long_right","hair_tips_left","hair_tips_right"]:
    DARK[p]=(.90,1.7,.76,"2B")
for p in ["collar_fold","belt_keeper_a","belt_keeper_b","thigh_pouch_flap","thigh_pouch_strap",
          "side_pouch_strap","jacket_hem_corner","boot_toe_cap_right","stock_tube",
          "handguard_slot_a","handguard_slot_b","handguard_slot_c","lace_loose_left","lace_loose_right",
          "hair_bang_second","hair_bang_near_eye","hair_lock_left_outer","hair_lock_right_outer",
          "hair_part_crown","hair_neck_strand","ear_inner",
          "lace_rung_l1","lace_rung_l2","lace_rung_l3","lace_rung_l4",
          "lace_rung_r1","lace_rung_r2","lace_rung_r3","lace_rung_r4",
          "sole_lug_l1","sole_lug_l2","sole_lug_l3","sole_lug_l4",
          "sole_lug_r1","sole_lug_r2","sole_lug_r3","sole_lug_r4",
          "sock_top_band_left","sock_top_band_right"]:
    DARK[p]=(.76,1.5,.64,"2B")
acts2=[]
for i,(part,(op,w,pr,gr)) in enumerate(DARK.items(),1):
    s=by2[part]
    acts2.append({"action_id":f"PL-{i:03d}","kind":"replace_stroke","stage":ST,
      "role":s.role,"part":part,"points":[list(p) for p in s.points],
      "target_stroke_id":part,"stroke_id":part,"revision_of":part,
      "confidence":.9,"layer":30,
      "tool":{"preset":"construction_pencil","grade":gr,
              "overrides":{"pressure":pr,"width":w,"opacity":op,"jitter":0.035}},
      "observation_id":f"obs-PL-{i:003d}",
      "source_observation":"Third look at the finished drawing at full render scale.",
      "reason":("Darkness in this renderer comes from pressure and pencil grade, not from stroke width. "
                "These identifying marks are re-laid with a softer grade at higher pressure and a small "
                "width, so they read clearly while staying thinner than the outer contour.")})
sess.execute_many_atomic([DrawingAction.from_dict(a) for a in acts2], label="identity-darken")
run.canvas.sync(sess.history)
run.canvas.render(PROJECT_ROOT / "temp/dogfood/croquis-sniper-girl/final_croquis.png", supersample=4)
run.save_checkpoint()
print("polish", len(wisp), len(acts2))
