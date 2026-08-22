import sys
from pathlib import Path
sys.path.insert(0,'/home/claude/work/croquis')
from helpers import S
from img2drawing import DrawingRun
run=DrawingRun.resume(Path("/home/claude/work/croquis/out"))
run.stage_start("P4_structural_connections")
def J(aid,part,pts,src,op=.62,w=2.3,pr=.54,grade="HB",role="connection"):
    return S(aid,"P4_structural_connections",part,pts,role=role,preset="construction_pencil",
             grade=grade,pressure=pr,width=w,opacity=op,jitter=.05,confidence=.86,source=src)
def B(aid,part,pts,src,op=.78,w=2.8,pr=.62):
    return J(aid,part,pts,src,op=op,w=w,pr=pr,role="mass")

acts=[
 # --- shoulder insertions ---------------------------------------------
 J("P4-S1","shoulder_insert_right",[[258,163],[268,168],[276,178],[280,192]],
   "Near shoulder insertion: a short curved plane running from the collar over the deltoid into the sleeve mass, so the arm emerges from the torso instead of being glued to it."),
 J("P4-S2","shoulder_insert_left",[[196,158],[188,163],[182,172],[179,186]],
   "Far shoulder insertion on the occluded side, stated only as far as the visible jacket shoulder allows."),
 # --- elbows ------------------------------------------------------------
 J("P4-E1","elbow_transition_right",[[279,290],[286,296],[293,299],[299,296]],
   "Near elbow as a short directional wedge spanning only part of the sleeve: it explains where the forearm changes direction without becoming a full-width band across the sleeve."),
 J("P4-E2","elbow_transition_right_inner",[[281,306],[288,309],[296,306]],
   "Second short plane just below the near elbow, closing the transition on the forearm side."),
 J("P4-E3","elbow_transition_left",[[165,258],[171,262],[177,259]],
   "Far elbow transition, kept minimal because the sleeve and the rifle occlude it.",op=.44,w=2.0,pr=.42),
 # --- wrists and hands --------------------------------------------------
 J("P4-W1","wrist_right",[[280,324],[287,327],[293,323]],
   "Near wrist: a short narrowing plane where the sleeve cuff meets the hand."),
 B("P4-W2","hand_block_right",[[281,330],[280,344],[284,356],[292,360],[298,352],[299,338],[295,329]],
   "Near hand as one smooth wrist-to-palm block with no finger detail; its lower edge is cut off where the hand enters the hip pocket, so it reads as occluded rather than floating."),
 J("P4-W3","hand_pocket_overlap_right",[[281,352],[290,357],[298,350]],
   "Overlap mark showing the hand entering the pocket opening rather than resting on top of it."),
 B("P4-W4","hand_block_left_occluded",[[164,334],[162,346],[166,356],[174,357]],
   "Far hand: only the partial block visible past the jacket hem and the rifle stock is stated; the rest stays occluded.",op=.50,w=2.3,pr=.46),
 # --- hip to thigh ------------------------------------------------------
 J("P4-P1","hip_thigh_insert_left",[[168,386],[178,394],[192,397],[206,394]],
   "Support-side pelvis-to-thigh insertion: a shallow plane at the thigh root explaining that the leg emerges from the basin, sitting just above the shorts hem it shares an edge with."),
 J("P4-P2","hip_thigh_insert_right",[[236,404],[250,411],[266,413],[280,408]],
   "Braced-side pelvis-to-thigh insertion, lower in frame because that hip is nearer the camera."),
 # --- knees -------------------------------------------------------------
 J("P4-K1","knee_plane_left",[[169,530],[178,536],[190,537],[197,532]],
   "Support knee as a short directional plane inside the leg mass, not a full-width tick: it states the small forward break of the weight-bearing leg."),
 J("P4-K2","knee_plane_right",[[268,540],[278,546],[291,547],[300,542]],
   "Braced knee plane, tilted with that leg's outward lean."),
 # --- ankles and boots --------------------------------------------------
 J("P4-A1","ankle_bridge_left",[[168,616],[176,621],[186,622],[193,618]],
   "Support ankle: a narrowing bridge that hands the leg mass over to the boot volume."),
 B("P4-F1","boot_block_left",
   [[166,624],[165,646],[166,666],[168,686],[172,704],[186,710],[204,709],[220,704],[223,692],[216,678],[204,666],[195,652],[192,636],[194,624]],
   "Support boot as one simple grounded block: a shaft that continues the ankle direction, a toe swinging image-right and away from the viewer, and a flat sole that sits on the ground plane."),
 J("P4-F2","boot_sole_left",[[168,702],[186,708],[206,708],[222,701]],
   "Sole/landing line of the far boot, verified against the subject's contact height."),
 J("P4-A2","ankle_bridge_right",[[281,638],[290,644],[300,645],[306,640]],
   "Braced ankle bridge, lower and further image-right, handing that leg over to the near boot."),
 B("P4-F3","boot_block_right",
   [[279,648],[279,672],[280,694],[282,714],[286,732],[304,740],[328,740],[350,734],[361,724],[352,710],[338,698],[322,684],[310,668],[306,652]],
   "Braced boot as the larger near block: same construction, but its toe swings further image-right and its sole lands lower in frame because it is closest to the camera."),
 J("P4-F4","boot_sole_right",[[284,730],[306,738],[332,738],[356,729]],
   "Sole/landing line of the near boot; the two sole heights together preserve the support-versus-brace reading."),
 # --- attached object articulation --------------------------------------
 J("P4-R1","sling_strap_upper",[[207,148],[204,162],[201,176]],
   "Sling strap leaving the near shoulder: the attachment that makes the rifle hang from her body rather than float against it."),
 J("P4-R2","sling_strap_lower",[[199,184],[196,198],[194,210]],
   "Same strap continuing to the rifle; the gap between the two segments is the hardware buckle observed on the subject, stated as a break rather than drawn as a part."),
 J("P4-R3","rifle_body_overlap",[[186,214],[178,226],[172,240]],
   "Overlap mark where the rifle body passes in front of the torso mass; the rifle owns the silhouette here and the jacket edge runs behind it."),
 J("P4-R4","rifle_stock_hip_overlap",[[196,378],[204,388],[210,400]],
   "Attachment/overlap where the skeleton buttstock crosses the image-left hip, so the stock reads as resting against the body."),
]
run.draw_many(acts)
run.prepare_stage_review()
print("ok")
