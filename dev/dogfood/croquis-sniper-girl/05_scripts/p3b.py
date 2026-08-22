import sys
from pathlib import Path
sys.path.insert(0,'/home/claude/work/croquis')
from helpers import S
from img2drawing import DrawingRun
run=DrawingRun.resume(Path("/home/claude/work/croquis/out"))
run.stage_start("P3_primary_masses")
def M(aid,part,pts,src,op=.78,w=2.8,pr=.62,grade="HB",role="mass"):
    return S(aid,"P3_primary_masses",part,pts,role=role,preset="construction_pencil",
             grade=grade,pressure=pr,width=w,opacity=op,jitter=.05,confidence=.88,source=src)
def C(aid,part,pts,src,op=.46,w=2.0,pr=.42):
    return M(aid,part,pts,src,op=op,w=w,pr=pr,grade="H",role="cross_contour")

acts=[
 M("P3C-H1","hair_mass_left",
   [[244,37],[224,40],[204,49],[186,62],[172,78],[164,95],[162,112],[168,129],[180,142],[194,150]],
   "Hair mass, image-left side: the bob sweeps well beyond the cranium, is widest near canvas y=100 and tucks back under the jaw."),
 M("P3C-H2","hair_mass_right",
   [[247,37],[264,40],[277,50],[285,64],[289,82],[288,101],[284,120],[278,138],[271,151],[262,159]],
   "Hair mass, image-right side: slightly narrower because the head turns that way, and it hangs lower, ending in tips below the jaw."),
 M("P3C-H3","hairline_bangs_edge",
   [[203,71],[213,82],[226,88],[241,89],[254,93],[266,101],[273,112]],
   "Boundary between hair mass and face mass: the bangs cross the forehead and drop toward the far cheek.",op=.60,w=2.3,pr=.50),
 M("P3C-H4","face_jaw_mass",
   [[207,99],[210,114],[217,127],[228,136],[240,140],[251,137],[261,127],[268,113]],
   "Face/jaw mass under the bangs, narrowing to the chin near canvas (243,140), still a plain plane with no features."),
 C("P3C-H5","head_cross_contour_brow",[[210,97],[228,100],[248,105],[266,110]],
   "Shallow brow-band cross-contour restating the head cross-axis as volume."),
 M("P3C-N1","neck_mass_left",[[222,138],[218,150],[216,160],[218,168]],
   "Short near-side neck mass bridging jaw to collar; most of the neck is occluded by hair and the raised collar."),
 M("P3C-N2","neck_mass_right",[[252,141],[252,152],[254,162],[258,169]],
   "Far side of the same neck bridge, meeting the collar mass."),
 M("P3C-T1","torso_mass_right",
   [[268,158],[277,170],[284,190],[289,212],[293,234],[296,256],[298,278],[300,300],[301,320],[302,340],[300,358],[297,372]],
   "Clothed torso mass, image-right contour from the observed jacket silhouette; widest near canvas y=340 at the near sleeve elbow."),
 M("P3C-T2","torso_mass_left",
   [[184,155],[176,172],[168,190],[160,208],[153,228],[149,248],[147,268],[147,288],[149,306],[154,324],[159,342],[162,360],[162,378],[163,396]],
   "Clothed torso mass, image-left contour, corrected on the reopened branch to the measured occupied volume: the loose jacket and the far hanging arm blouse out well past the shoulder line and reach their widest near canvas y=270-290."),
 C("P3C-T3","torso_cross_contour_chest",[[170,196],[200,206],[232,211],[260,211],[284,204]],
   "Shallow cross-contour across the upper back, dropping toward the viewer to explain the back-three-quarter turn."),
 C("P3C-T4","torso_cross_contour_waist",[[152,318],[186,330],[220,334],[252,333],[280,326]],
   "Second cross-contour at the belt band, explaining waist volume and the mild counter-twist."),
 M("P3C-T5","arm_torso_separation_right",[[272,176],[278,214],[281,252],[282,290],[280,320],[276,346]],
   "Soft separation between the near sleeve mass and the torso mass, so the sleeve reads as its own tapered volume.",op=.52,w=2.2,pr=.46),
 M("P3C-T6","arm_mass_left_inner",[[176,190],[168,232],[164,272],[164,308],[168,344]],
   "Inner boundary of the far sleeve mass, moved out with the corrected flank so the sleeve occupies the volume actually observed.",op=.46,w=2.1,pr=.42),
 M("P3C-P1","pelvis_basin_left",[[163,396],[165,410],[168,420],[172,428]],
   "Pelvis basin, image-left: the shorts mass turns under the hip and flows into the thigh root instead of closing an ellipse."),
 M("P3C-P2","pelvis_basin_right",[[299,352],[296,372],[291,390],[285,406]],
   "Pelvis basin, image-right, narrowing faster and flowing into the braced thigh root."),
 M("P3C-P3","shorts_hem_left",[[167,394],[181,398],[197,400],[212,398]],
   "Shorts hem across the support thigh, the first major internal break of the lower mass."),
 M("P3C-P4","shorts_hem_right",[[234,414],[250,418],[266,419],[281,414]],
   "Shorts hem across the braced thigh, lower in frame because that leg is nearer the camera."),
 M("P3C-L1","leg_support_outer",
   [[167,396],[165,420],[164,444],[167,462],[171,482],[170,504],[166,528],[162,552],[161,576],[164,598],[167,618],[167,634]],
   "Support-leg mass, outer contour: bare thigh, a smooth swell through the sock top, a calf peak near canvas y=482 and a slim ankle."),
 M("P3C-L2","leg_support_inner",
   [[212,398],[211,420],[210,442],[213,466],[209,492],[204,514],[198,536],[196,558],[194,580],[192,600],[191,620],[192,632]],
   "Support-leg mass, inner contour; the thigh-to-ankle taper is asymmetric, not a parallel rail."),
 M("P3C-L3","leg_brace_outer",
   [[288,416],[286,440],[285,462],[291,472],[297,484],[299,502],[301,522],[301,542],[302,562],[304,582],[304,602],[305,622],[306,642],[305,652]],
   "Braced-leg mass, outer contour: the wider, nearer leg, leaning image-right for its whole length."),
 M("P3C-L4","leg_brace_inner",
   [[235,414],[236,438],[240,462],[250,482],[257,502],[260,522],[266,542],[266,562],[268,582],[269,602],[275,622],[280,640]],
   "Braced-leg mass, inner contour; the negative space between the legs is a tall wedge, wide at the knee and closing toward the hem."),
 M("P3C-P5","thigh_holster_mass",[[286,404],[299,406],[306,416],[308,436],[307,456],[303,470],[293,472]],
   "Thigh pouch hanging on the braced leg: it owns the image-right silhouette between canvas y=405 and y=470, so it is stated as its own small mass rather than absorbed into the thigh."),
 M("P3C-R1","rifle_mass_left",
   [[113,44],[113,68],[116,86],[133,92],[134,112],[136,132],[139,152],[142,172],[146,192],[151,214],[157,238],[164,262],[172,286],[179,308],[183,330],[185,354],[187,378],[192,400],[200,422],[206,440]],
   "Rifle mass, image-left contour, corrected on the reopened branch to the measured prop edge: a fat suppressor, an abrupt step to a near-vertical tapered handguard, then a widening receiver and stock. The earlier version leaned too far right through the middle.",
   op=.66,w=2.5,pr=.54),
 M("P3C-R2","rifle_mass_right",
   [[132,44],[133,68],[136,88],[150,96],[152,126],[158,142],[180,150],[186,180],[189,206],[193,228],[198,252],[203,276],[208,300],[214,326],[221,350],[229,376],[236,400],[242,428]],
   "Rifle mass, image-right contour: it steps out at the scope near canvas y=150 and again at the skeleton stock, so the long mass is not a plain rail.",
   op=.66,w=2.5,pr=.54),
 C("P3C-R3","rifle_cross_contour_receiver",[[150,210],[166,204],[184,198]],
   "Cross-contour across the widest part of the rifle mass, tying its two contours into one integrated volume."),
 C("P3C-R4","rifle_cross_contour_stock",[[190,394],[212,388],[234,382]],
   "Second cross-contour across the buttstock mass where it overlaps the image-left hip."),
]
run.draw_many(acts)
run.prepare_stage_review()
print("ok")
