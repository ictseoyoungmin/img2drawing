import sys
from pathlib import Path
sys.path.insert(0,'/home/claude/work/croquis')
from helpers import S
from img2drawing import DrawingRun
run=DrawingRun.resume(Path("/home/claude/work/croquis/out"))
run.stage_start("P4_structural_connections")
def J(aid,part,pts,src,op=.62,w=2.3,pr=.54,role="connection"):
    return S(aid,"P4_structural_connections",part,pts,role=role,preset="construction_pencil",
             grade="HB",pressure=pr,width=w,opacity=op,jitter=.05,confidence=.87,source=src)
def B(aid,part,pts,src,op=.78,w=2.8,pr=.62):
    return J(aid,part,pts,src,op=op,w=w,pr=pr,role="mass")
acts=[
 J("P4C-S1","shoulder_insert_right",[[258,163],[268,168],[276,178],[280,192]],
   "Near shoulder insertion: a short curved plane from the collar over the deltoid into the sleeve, so the arm emerges from the torso."),
 J("P4C-S2","shoulder_insert_left",[[196,158],[188,163],[181,172],[176,186]],
   "Far shoulder insertion, ending where the corrected flank takes the sleeve outward."),
 J("P4C-E1","elbow_transition_right",[[284,291],[290,297],[296,297]],
   "Near elbow as a short partial plane on the outer half of the sleeve, where the direction change is actually visible."),
 J("P4C-E2","elbow_transition_right_inner",[[286,307],[292,309]],
   "Short closing plane below the near elbow on the forearm side."),
 J("P4C-E3","elbow_transition_left",[[161,268],[167,272],[173,269]],
   "Far elbow transition, minimal because sleeve and rifle occlude it; placed on the corrected flank.",op=.44,w=2.0,pr=.42),
 J("P4C-W1","wrist_right",[[280,324],[287,327],[293,323]],
   "Near wrist: a short narrowing plane where the sleeve cuff meets the hand."),
 B("P4C-W2","hand_block_right",
   [[281,329],[279,340],[280,350],[285,357],[293,359],[298,353],[300,343],[298,333]],
   "Near hand as a smooth wrist-to-palm volume with no finger detail; its lower-inner edge is left open where the pocket takes over, so it reads as occluded."),
 J("P4C-W3","hand_pocket_overlap_right",[[283,355],[291,359]],
   "Occlusion mark where the near hand enters the pocket opening."),
 B("P4C-W4","hand_block_left_occluded",[[160,336],[158,348],[163,357],[172,358]],
   "Far hand: only the partial block visible past the jacket hem and the rifle stock is stated.",op=.50,w=2.3,pr=.46),
 J("P4C-P1","hip_thigh_insert_left",[[176,390],[186,394],[196,394]],
   "Support-side pelvis-to-thigh insertion, a short plane offset from the hem rather than a second band."),
 J("P4C-P2","hip_thigh_insert_right",[[246,407],[258,411],[270,411]],
   "Braced-side insertion, lower in frame because that hip is nearer the camera."),
 J("P4C-K1","knee_plane_left",[[172,533],[180,538],[188,538]],
   "Support knee as a short partial directional plane across the front half of the leg."),
 J("P4C-K2","knee_plane_right",[[272,543],[281,548],[290,548]],
   "Braced knee plane, tilted with that leg's outward lean."),
 J("P4C-A1","ankle_bridge_left",[[171,617],[178,622],[185,622]],
   "Support ankle: a short narrowing bridge handing the leg mass to the boot."),
 B("P4C-F1","boot_block_left",
   [[166,624],[165,646],[166,666],[168,686],[172,704],[186,710],[204,709],[220,704],[223,692],[216,678],[204,666],[195,652],[192,636],[194,624]],
   "Support boot as one simple grounded block: a shaft continuing the ankle direction, a toe swinging image-right and away, and a flat sole on the ground plane."),
 J("P4C-F2","boot_sole_left",[[168,702],[186,708],[206,708],[222,701]],
   "Sole/landing line of the far boot, verified against the subject's contact height."),
 J("P4C-A2","ankle_bridge_right",[[284,639],[292,645],[299,645]],
   "Braced ankle bridge, lower and further image-right."),
 B("P4C-F3","boot_block_right",
   [[279,648],[279,672],[280,694],[282,714],[286,732],[304,740],[328,740],[350,734],[361,724],[352,710],[338,698],[322,684],[310,668],[306,652]],
   "Braced boot as the larger near block; its toe swings further image-right and its sole lands lower because it is closest to the camera."),
 J("P4C-F4","boot_sole_right",[[284,730],[306,738],[332,738],[356,729]],
   "Sole/landing line of the near boot; the two sole heights preserve the support-versus-brace reading."),
 J("P4C-R1","sling_strap_upper",[[207,148],[204,162],[201,176]],
   "Sling strap leaving the near shoulder: the attachment that makes the rifle hang from her body."),
 J("P4C-R2","sling_strap_lower",[[199,184],[196,198],[194,210]],
   "Same strap continuing to the rifle; the gap between segments is the observed buckle, stated as a break, not drawn as a part."),
 J("P4C-R3","rifle_body_overlap",[[186,220],[181,236],[178,252]],
   "Overlap mark where the rifle body passes in front of the torso; below the ownership handoff the garment is outside the prop, so this mark is now an internal boundary."),
 J("P4C-R4","rifle_stock_hip_overlap",[[192,378],[200,388],[207,400]],
   "Attachment/overlap where the skeleton buttstock crosses the image-left hip."),
 J("P4C-R5","pouch_strap_thigh",[[286,432],[296,436],[305,436]],
   "Attachment plane of the thigh pouch: the strap that fixes it to the braced leg, so the pouch hangs rather than floats."),
]
run.draw_many(acts)
run.prepare_stage_review()
print("ok")
