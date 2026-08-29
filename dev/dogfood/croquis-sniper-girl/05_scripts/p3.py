import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(PROJECT_ROOT / "skills/img2drawing/src"))
from helpers import S
from img2drawing import DrawingRun
run=DrawingRun.resume(PROJECT_ROOT / "temp/dogfood/croquis-sniper-girl/run")
if run.current_stage!="P3_primary_masses":
    raise SystemExit("wrong stage "+str(run.current_stage))
run.stage_start("P3_primary_masses")

def M(aid,part,pts,src,op=.78,w=2.8,pr=.62,grade="HB",role="mass"):
    return S(aid,"P3_primary_masses",part,pts,role=role,preset="construction_pencil",
             grade=grade,pressure=pr,width=w,opacity=op,jitter=.05,confidence=.87,source=src)
def C(aid,part,pts,src,op=.46,w=2.0,pr=.42):
    return M(aid,part,pts,src,op=op,w=w,pr=pr,grade="H",role="cross_contour")

acts=[
 # --- head / hair mass -------------------------------------------------
 M("P3-H1","hair_mass_left",
   [[244,37],[224,40],[204,49],[186,62],[172,78],[164,95],[162,112],[168,129],[180,142],[194,150]],
   "Hair mass, image-left side: the bob sweeps out well beyond the cranium, reaches its widest near canvas y=100 and tucks back under the jaw line."),
 M("P3-H2","hair_mass_right",
   [[247,37],[264,40],[277,50],[285,64],[289,82],[288,101],[284,120],[278,138],[271,151],[262,159]],
   "Hair mass, image-right side: slightly narrower than the left because the head turns that way, and it hangs lower, ending in tips below the jaw."),
 M("P3-H3","hairline_bangs_edge",
   [[203,71],[213,82],[226,88],[241,89],[254,93],[266,101],[273,112]],
   "Boundary between the hair mass and the face mass: the bangs run across the forehead and drop toward the far cheek, leaving the face plane open.",
   op=.60,w=2.3,pr=.50),
 M("P3-H4","face_jaw_mass",
   [[207,99],[210,114],[217,127],[228,136],[240,140],[251,137],[261,127],[268,113]],
   "Face/jaw mass under the bangs: it narrows to the chin near canvas (243,140) and stays a plain plane with no features at this stage."),
 C("P3-H5","head_cross_contour_brow",
   [[210,97],[228,100],[248,105],[266,110]],
   "Shallow cross-contour on the brow band, restating the head cross-axis as volume rather than as a line."),
 # --- neck bridge ------------------------------------------------------
 M("P3-N1","neck_mass_left",[[222,138],[218,150],[216,160],[218,168]],
   "Short neck mass on the near side, bridging jaw to collar; most of the neck is occluded by hair and the raised collar."),
 M("P3-N2","neck_mass_right",[[252,141],[252,152],[254,162],[258,169]],
   "Far side of the same neck bridge, meeting the collar mass."),
 # --- torso / clothed jacket mass -------------------------------------
 M("P3-T1","torso_mass_right",
   [[268,158],[277,170],[284,190],[289,212],[293,234],[296,256],[298,278],[300,300],[301,320],[302,340],[300,358],[297,372]],
   "Clothed torso mass, image-right contour, taken from the observed jacket silhouette rather than from a fitted body: it widens steadily to its broadest near canvas y=340 where the sleeve elbow sits."),
 M("P3-T2","torso_mass_left",
   [[186,155],[178,172],[172,192],[168,214],[165,238],[163,262],[162,286],[161,308],[161,330],[162,352],[164,370]],
   "Clothed torso mass, image-left contour. The far arm hangs against this side, so the jacket and the arm share one occupied edge; the rifle mass overlays it without replacing it."),
 C("P3-T3","torso_cross_contour_chest",
   [[178,196],[204,206],[232,211],[260,211],[284,204]],
   "Shallow cross-contour across the upper back, dropping toward the viewer to explain the back-three-quarter turn of the torso volume."),
 C("P3-T4","torso_cross_contour_waist",
   [[164,320],[192,330],[222,334],[252,333],[280,326]],
   "Second cross-contour at the belt band, explaining the waist volume and the mild counter-twist without drawing the belt itself."),
 M("P3-T5","arm_torso_separation_right",
   [[272,176],[278,214],[281,252],[282,290],[280,320],[276,346]],
   "Soft separation between the near sleeve mass and the torso mass; the sleeve reads as its own tapered volume emerging from the shoulder.",
   op=.52,w=2.2,pr=.46),
 M("P3-T6","arm_mass_left_inner",
   [[181,180],[176,220],[173,262],[172,300],[172,336]],
   "Inner boundary of the far sleeve mass; it is largely occluded by the rifle but its width still occupies the image-left flank.",
   op=.46,w=2.1,pr=.42),
 # --- pelvis basin -----------------------------------------------------
 M("P3-P1","pelvis_basin_left",[[162,352],[163,372],[166,388],[171,398]],
   "Pelvis basin, image-left: the shorts mass turns under the hip and flows straight into the thigh root instead of closing an ellipse."),
 M("P3-P2","pelvis_basin_right",[[299,352],[296,372],[291,390],[285,406]],
   "Pelvis basin, image-right: it narrows faster on this side and flows into the braced thigh root."),
 M("P3-P3","shorts_hem_left",[[167,394],[181,398],[197,400],[212,398]],
   "Shorts hem across the support thigh, the first major internal break of the lower mass."),
 M("P3-P4","shorts_hem_right",[[234,414],[250,418],[266,419],[281,414]],
   "Shorts hem across the braced thigh; it sits lower in frame because that leg is nearer the camera."),
 # --- legs -------------------------------------------------------------
 M("P3-L1","leg_support_outer",
   [[167,396],[165,420],[164,444],[168,466],[172,490],[170,512],[166,534],[162,556],[161,578],[164,600],[168,620],[167,632]],
   "Support-leg mass, outer image-left contour: the bare thigh, the sock top step near canvas y=470, then a calf that swells and tapers into a slim ankle."),
 M("P3-L2","leg_support_inner",
   [[212,398],[211,420],[210,442],[213,466],[209,492],[204,514],[198,536],[196,558],[194,580],[192,600],[191,620],[192,632]],
   "Support-leg mass, inner contour; the taper from thigh to ankle is asymmetric, not a parallel rail."),
 M("P3-L3","leg_brace_outer",
   [[288,416],[286,440],[285,462],[298,482],[299,502],[301,522],[301,542],[302,562],[304,582],[304,602],[305,622],[306,640]],
   "Braced-leg mass, outer image-right contour: it is the wider and nearer of the two legs and leans image-right all the way down."),
 M("P3-L4","leg_brace_inner",
   [[235,414],[236,438],[240,462],[250,482],[257,502],[260,522],[266,542],[266,562],[268,582],[269,602],[275,622],[280,640]],
   "Braced-leg mass, inner contour; the negative space between the two legs is a tall wedge that is wide at the knee and closes toward the hem."),
 M("P3-B1","boot_mass_left",
   [[167,630],[169,652],[170,672],[168,692],[172,710],[196,713],[218,708],[222,690],[218,672],[200,650],[188,634]],
   "Far boot mass: a single blocky volume with the toe swinging image-right and away, sitting on its own thick sole."),
 M("P3-B2","boot_mass_right",
   [[281,644],[283,668],[284,690],[282,710],[281,730],[300,737],[330,736],[358,732],[371,724],[362,706],[340,692],[320,672],[308,652]],
   "Near boot mass: larger in frame, its toe swings further image-right and its sole lands lower because it is closest to the camera."),
 # --- attached object mass --------------------------------------------
 M("P3-R1","rifle_mass_left",
   [[113,44],[113,66],[116,84],[132,92],[137,120],[141,146],[147,172],[152,200],[160,232],[168,262],[176,292],[184,322],[191,352],[197,382],[203,412],[208,436]],
   "Rifle mass, image-left contour: a fat suppressor at the top, an abrupt step down to a thin barrel, then a steady widening through receiver and stock.",
   op=.66,w=2.5,pr=.54),
 M("P3-R2","rifle_mass_right",
   [[132,44],[133,68],[136,86],[150,96],[153,124],[157,148],[180,152],[184,180],[189,208],[196,240],[204,272],[212,304],[220,336],[228,368],[236,398],[242,428]],
   "Rifle mass, image-right contour: it steps out at the scope near canvas y=150 and again at the skeleton stock, so the long mass is not a plain rail.",
   op=.66,w=2.5,pr=.54),
 C("P3-R3","rifle_cross_contour_receiver",[[151,205],[168,201],[184,196]],
   "Cross-contour across the widest part of the rifle mass, tying the two contours into one integrated volume rather than two floating lines."),
 C("P3-R4","rifle_cross_contour_stock",[[196,392],[214,386],[232,380]],
   "Second cross-contour across the buttstock mass where it overlaps the image-left hip."),
]
run.draw_many(acts)
run.prepare_stage_review()
print("ok")
