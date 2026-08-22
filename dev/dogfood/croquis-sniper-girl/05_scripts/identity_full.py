import sys, json
from pathlib import Path
sys.path.insert(0,'/home/claude/work/croquis')
from helpers import S
from img2drawing import DrawingRun, DrawingAction
run=DrawingRun.resume(Path("/home/claude/work/croquis/out"))
sess=run.session
ST="P6_identity_finish"
def F(aid,part,pts,src,op=.70,w=1.6,pr=.55,grade="B",role="detail",layer=30):
    return S(aid,ST,part,pts,role=role,preset="construction_pencil",grade=grade,pressure=pr,
             width=w,opacity=op,jitter=.04,confidence=.88,layer=layer,source=src)
A=[]
# ============ FACE ============
A += [
 F("ID-F01","eye_right_upper_lash",[[228,101],[231,99],[235,98],[240,99],[244,101],[246,104]],
   "Near (her right) eye: the upper lash line is the heaviest mark of the face and thickens toward the outer corner, as the subject shows.",op=.90,w=2.0,pr=.70,grade="2B"),
 F("ID-F02","eye_right_lower_lid",[[231,106],[236,107],[241,106],[245,104]],
   "Lower lid of the near eye, thinner and lighter than the lash line.",op=.60,w=1.3,pr=.46),
 F("ID-F03","eye_right_iris",[[234,100],[233,103],[235,106],[239,106],[241,103],[240,100],[237,99],[234,101],[236,105],[240,104],[239,101],[236,102]],
   "Iris of the near eye: one ring re-entered a second time to build the dark value of the red iris in graphite.",op=.86,w=2.0,pr=.66,grade="4B"),
 F("ID-F04","eye_right_pupil",[[236,102],[238,104],[237,102],[238,103]],
   "Pupil core of the near eye.",op=.92,w=2.2,pr=.76,grade="6B"),
 F("ID-F05","eye_left_upper_lash",[[256,108],[260,106],[265,106],[269,108],[271,111]],
   "Far (her left) eye: the same lash construction, shorter and lower because the head turns toward it.",op=.86,w=1.9,pr=.66,grade="2B"),
 F("ID-F06","eye_left_lower_lid",[[258,113],[262,114],[266,113],[269,111]],
   "Lower lid of the far eye.",op=.58,w=1.3,pr=.46),
 F("ID-F07","eye_left_iris",[[260,108],[259,111],[261,114],[264,114],[266,111],[265,108],[262,107],[260,110],[263,113],[265,110]],
   "Iris of the far eye, compressed by the turn.",op=.84,w=1.9,pr=.64,grade="4B"),
 F("ID-F08","eye_left_pupil",[[262,110],[263,112],[262,110]],
   "Pupil core of the far eye.",op=.90,w=2.0,pr=.74,grade="6B"),
 F("ID-F09","nose",[[253,117],[255,120],[256,122],[253,123]],
   "Nose: only the small shadow plane and the underside the subject actually shows.",op=.52,w=1.3,pr=.44),
 F("ID-F10","mouth_upper",[[244,130],[247,129],[250,130],[253,130]],
   "Upper lip of the small closed mouth.",op=.70,w=1.5,pr=.54),
 F("ID-F11","mouth_lower",[[245,133],[248,133],[251,132]],
   "Lower lip, lighter than the upper line.",op=.48,w=1.2,pr=.42),
 F("ID-F13","ear_outer",[[200,93],[198,99],[199,106],[203,111],[207,112]],
   "Her right ear, visible image-left of the face because the head is turned that far.",op=.64,w=1.5,pr=.52),
 F("ID-F14","ear_inner",[[202,98],[203,104],[205,108]],
   "Inner fold of the ear.",op=.44,w=1.2,pr=.40),
]
# ============ HAIR ============
A += [
 F("ID-H01","hair_part_crown",[[240,40],[236,50],[231,62],[227,74]],
   "Crown parting of the bob, the origin the strand groups radiate from.",op=.48,w=1.3,pr=.42),
 F("ID-H02","hair_bang_long_right",[[233,45],[240,62],[249,80],[258,96],[266,110],[271,124]],
   "The long bang sweeping across the forehead and falling over the far eye: the most recognisable single strand of this bob.",op=.64,w=1.6,pr=.52),
 F("ID-H03","hair_bang_second",[[228,48],[229,66],[232,84],[236,100]],
   "Second bang group falling between the eyes.",op=.50,w=1.3,pr=.44),
 F("ID-H04","hair_bang_near_eye",[[222,52],[218,70],[216,88],[217,104],[221,118]],
   "Near-side face-framing lock running past the ear toward the jaw.",op=.54,w=1.4,pr=.46),
 F("ID-H05","hair_lock_left_outer",[[214,44],[199,60],[187,78],[180,98],[181,118],[188,136]],
   "Outer strand group on the image-left, following the widest sweep of the bob.",op=.46,w=1.3,pr=.42),
 F("ID-H06","hair_lock_right_outer",[[258,42],[272,54],[280,72],[281,92],[277,112],[271,132]],
   "Outer strand group on the image-right.",op=.46,w=1.3,pr=.42),
 F("ID-H07","hair_tips_left",[[170,128],[176,140],[184,148],[190,145],[196,152]],
   "Ragged tips where the image-left side of the bob ends just below the jaw.",op=.50,w=1.3,pr=.44),
 F("ID-H08","hair_tips_right",[[280,130],[276,142],[270,152],[264,158],[258,162]],
   "Ragged tips on the image-right, hanging slightly lower than the other side.",op=.50,w=1.3,pr=.44),
 F("ID-H09","hair_stray_top",[[236,34],[244,28],[252,32]],
   "The single stray hair above the crown the subject shows against the sky.",op=.38,w=1.1,pr=.34),
 F("ID-H10","hair_neck_strand",[[247,140],[252,152],[254,164]],
   "Short strand falling in front of the collar.",op=.42,w=1.2,pr=.38),
]
# ============ GARMENT ============
A += [
 F("ID-G01","collar_top",[[207,155],[218,148],[232,144],[246,144],[258,149],[264,157]],
   "Top edge of the raised jacket collar standing behind the neck."),
 F("ID-G02","collar_fold",[[212,167],[228,171],[244,172],[256,168]],
   "Lower fold of the collar where it meets the shoulder yoke.",op=.56,w=1.4,pr=.48),
 F("ID-G03","shoulder_patch",[[242,199],[270,196],[272,227],[258,240],[243,231],[242,199]],
   "Insignia patch on the upper back: a rounded rectangle with a pointed lower edge, the single most identifying garment feature."),
 F("ID-G04","patch_emblem_wings_left",[[246,215],[251,210],[256,214]],
   "Left wing of the winged emblem inside the patch, simplified to its shape.",op=.60,w=1.3,pr=.48),
 F("ID-G05","patch_emblem_wings_right",[[268,213],[262,209],[258,213]],
   "Right wing of the emblem.",op=.60,w=1.3,pr=.48),
 F("ID-G06","patch_emblem_centre",[[257,206],[257,216],[256,224]],
   "Central blade of the emblem.",op=.60,w=1.3,pr=.48),
 F("ID-G07","sling_edge_outer",[[205,147],[201,178],[198,207]],
   "Outer edge of the wide sling strap running from the shoulder to the rifle."),
 F("ID-G08","sling_edge_inner",[[212,148],[208,178],[205,207]],
   "Inner edge of the same strap; the pair states its real width."),
 F("ID-G09","sling_buckle_upper",[[200,163],[213,161],[214,172],[201,174],[200,163]],
   "Upper hardware buckle on the sling."),
 F("ID-G10","sling_buckle_lower",[[196,196],[208,194],[209,205],[197,207],[196,196]],
   "Lower hardware buckle on the sling."),
 F("ID-G11","side_pouch_right",[[285,234],[293,233],[294,300],[286,302],[285,234]],
   "Narrow magazine pouch hanging on her image-right side, under the arm."),
 F("ID-G12","side_pouch_strap",[[285,262],[294,261]],
   "Retaining strap across the side pouch.",op=.58,w=1.3,pr=.48),
 F("ID-G13","belt_lower_edge",[[215,319],[233,325],[250,331],[266,337],[281,343]],
   "Lower edge of the belt; with the P5 belt line it states the belt's real width."),
 F("ID-G14","belt_keeper_a",[[231,312],[232,326]],
   "Belt keeper loop.",op=.58,w=1.3,pr=.48),
 F("ID-G15","belt_keeper_b",[[263,327],[264,340]],
   "Second belt keeper loop.",op=.58,w=1.3,pr=.48),
 F("ID-G16","cargo_pocket",[[219,340],[240,344],[262,343],[263,382],[242,391],[220,388],[219,340]],
   "Cargo pocket on the back of the shorts, the other strongly identifying garment feature."),
 F("ID-G17","cargo_pocket_flap",[[219,354],[240,358],[262,356]],
   "Flap line across the cargo pocket.",op=.58,w=1.3,pr=.48),
 F("ID-G18","cargo_pocket_snap",[[228,350],[230,351]],
   "Snap stud on the pocket flap.",op=.66,w=1.6,pr=.56),
 F("ID-G19","thigh_strap",[[240,433],[258,437],[276,438],[288,436]],
   "Strap around the braced thigh that carries the drop pouch."),
 F("ID-G20","thigh_pouch_flap",[[289,419],[306,418]],
   "Flap line on the thigh pouch.",op=.58,w=1.3,pr=.48),
 F("ID-G21","thigh_pouch_strap",[[289,449],[306,448]],
   "Lower retaining strap on the thigh pouch.",op=.58,w=1.3,pr=.48),
 F("ID-G22","sleeve_cuff_right",[[277,318],[284,321],[292,320],[297,316]],
   "Cuff of the near sleeve, just above the hand."),
 F("ID-G23","jacket_fold_elbow",[[283,285],[291,290],[298,287]],
   "One major fold at the near elbow, enough to say the jacket is soft shell fabric.",op=.44,w=1.3,pr=.40),
 F("ID-G24","jacket_fold_back",[[254,248],[260,266],[262,284]],
   "One major fold down the back of the jacket.",op=.40,w=1.2,pr=.38),
 F("ID-G25","jacket_hem_corner",[[166,320],[171,330],[178,334]],
   "The pointed hem corner on the image-left of the cropped jacket.",op=.52,w=1.4,pr=.44),
 F("ID-G26","sock_top_band_left",[[169,458],[184,456],[199,455],[212,458]],
   "Ribbed band just under the top edge of the support leg's thigh-high sock.",op=.46,w=1.3,pr=.42),
 F("ID-G27","sock_top_band_right",[[247,482],[263,479],[281,478],[296,481]],
   "The same band on the braced leg's sock.",op=.46,w=1.3,pr=.42),
]
# ============ BOOTS ============
A += [
 F("ID-B01","lace_line_left",[[196,628],[201,641],[206,655],[210,668]],
   "Lacing line running up the front of the far boot."),
 F("ID-B02","lace_rung_l1",[[192,632],[201,631]],"Lace crossing on the far boot.",op=.56,w=1.3,pr=.46),
 F("ID-B03","lace_rung_l2",[[195,642],[204,641]],"Lace crossing on the far boot.",op=.56,w=1.3,pr=.46),
 F("ID-B04","lace_rung_l3",[[198,652],[207,651]],"Lace crossing on the far boot.",op=.56,w=1.3,pr=.46),
 F("ID-B05","lace_rung_l4",[[201,662],[210,661]],"Lace crossing on the far boot.",op=.56,w=1.3,pr=.46),
 F("ID-B06","lace_loose_left",[[200,634],[203,646],[201,657]],
   "Loose lace end hanging from the far boot.",op=.50,w=1.2,pr=.42),
 F("ID-B07","boot_sole_band_left",[[168,701],[186,706],[206,706],[222,699]],
   "Upper edge of the thick lug sole on the far boot."),
 F("ID-B08","sole_lug_l1",[[176,704],[176,709]],"Lug tick on the far sole.",op=.52,w=1.2,pr=.44),
 F("ID-B09","sole_lug_l2",[[188,707],[188,712]],"Lug tick on the far sole.",op=.52,w=1.2,pr=.44),
 F("ID-B10","sole_lug_l3",[[200,707],[200,712]],"Lug tick on the far sole.",op=.52,w=1.2,pr=.44),
 F("ID-B11","sole_lug_l4",[[212,704],[212,709]],"Lug tick on the far sole.",op=.52,w=1.2,pr=.44),
 F("ID-B12","lace_line_right",[[314,656],[321,672],[328,689],[335,704]],
   "Lacing line up the front of the near boot."),
 F("ID-B13","lace_rung_r1",[[309,661],[319,659]],"Lace crossing on the near boot.",op=.56,w=1.3,pr=.46),
 F("ID-B14","lace_rung_r2",[[315,674],[325,672]],"Lace crossing on the near boot.",op=.56,w=1.3,pr=.46),
 F("ID-B15","lace_rung_r3",[[321,687],[331,685]],"Lace crossing on the near boot.",op=.56,w=1.3,pr=.46),
 F("ID-B16","lace_rung_r4",[[327,699],[337,697]],"Lace crossing on the near boot.",op=.56,w=1.3,pr=.46),
 F("ID-B17","lace_loose_right",[[319,662],[324,676],[321,689]],
   "Loose lace end hanging from the near boot.",op=.50,w=1.2,pr=.42),
 F("ID-B18","boot_sole_band_right",[[285,729],[306,736],[332,736],[356,727]],
   "Upper edge of the thick lug sole on the near boot."),
 F("ID-B19","sole_lug_r1",[[296,733],[296,739]],"Lug tick on the near sole.",op=.52,w=1.2,pr=.44),
 F("ID-B20","sole_lug_r2",[[310,737],[310,743]],"Lug tick on the near sole.",op=.52,w=1.2,pr=.44),
 F("ID-B21","sole_lug_r3",[[324,737],[324,743]],"Lug tick on the near sole.",op=.52,w=1.2,pr=.44),
 F("ID-B22","sole_lug_r4",[[338,735],[338,741]],"Lug tick on the near sole.",op=.52,w=1.2,pr=.44),
 F("ID-B23","boot_toe_cap_right",[[336,706],[344,714],[350,722]],
   "Toe-cap seam on the near boot.",op=.48,w=1.3,pr=.42),
]
# ============ RIFLE ============
A += [
 F("ID-R01","suppressor_band_a",[[115,58],[131,57]],"Joint band on the suppressor.",op=.56,w=1.4,pr=.48),
 F("ID-R02","suppressor_band_b",[[115,74],[132,73]],"Second joint band on the suppressor.",op=.56,w=1.4,pr=.48),
 F("ID-R03","scope_ring_front",[[160,158],[182,155]],"Front scope mounting ring."),
 F("ID-R04","scope_ring_rear",[[161,182],[184,179]],"Rear scope mounting ring."),
 F("ID-R05","scope_objective",[[179,186],[187,185],[188,197],[180,198]],
   "Objective bell at the lower end of the scope."),
 F("ID-R06","scope_turret",[[172,203],[174,199],[179,199],[181,203],[179,207],[174,207],[172,203]],
   "Elevation turret knob on the scope, one of the rifle's most recognisable parts."),
 F("ID-R07","handguard_slot_a",[[140,161],[143,169]],"Handguard slot.",op=.48,w=1.2,pr=.42),
 F("ID-R08","handguard_slot_b",[[143,179],[146,187]],"Handguard slot.",op=.48,w=1.2,pr=.42),
 F("ID-R09","handguard_slot_c",[[146,197],[149,205]],"Handguard slot.",op=.48,w=1.2,pr=.42),
 F("ID-R10","magazine",[[160,256],[173,253],[178,277],[165,280],[160,256]],
   "Box magazine under the receiver."),
 F("ID-R11","stock_cutout_second",[[200,412],[214,408],[222,420],[208,425],[200,412]],
   "Second large cutout in the skeleton buttstock."),
 F("ID-R12","stock_tube",[[196,352],[212,347]],"Buffer tube joint on the stock.",op=.50,w=1.3,pr=.44),
]

sess.execute_many_atomic([DrawingAction.from_dict(a) for a in A], label="identity-finish")
run.canvas.sync(sess.history)
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
run.save_checkpoint()
import json
json.dump({"stage":ST,"identity_strokes":len(A),"confirmation_strokes":len(acts),"note":"Identity finishing pass drawn after the five-stage croquis closed. It deliberately exceeds the frozen P5 clean-block-in ceiling because the task requires the subject to be identifiable by face, hair and outfit."},open("/home/claude/work/croquis/out/identity_pass.json","w"),indent=2)
print("identity",len(A),"confirm",len(acts))

# ================= FINAL POLISH =================
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
run.canvas.render("/home/claude/work/final_croquis.png", supersample=4)
run.save_checkpoint()
print("polish", len(wisp), len(acts2))
