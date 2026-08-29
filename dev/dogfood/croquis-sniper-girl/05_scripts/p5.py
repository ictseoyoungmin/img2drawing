import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(PROJECT_ROOT / "skills/img2drawing/src"))
from helpers import S
from img2drawing import DrawingRun
run=DrawingRun.resume(PROJECT_ROOT / "temp/dogfood/croquis-sniper-girl/run")
run.stage_start("P5_clean_blockin")

def CT(aid,part,pts,src,op=.92,w=3.2,pr=.74,grade="B",preset="form_pencil",role="contour"):
    return S(aid,"P5_clean_blockin",part,pts,role=role,preset=preset,grade=grade,
             pressure=pr,width=w,opacity=op,jitter=.045,confidence=.9,layer=20,source=src)
def BR(aid,part,pts,src,op=.68,w=2.5,pr=.58):
    return CT(aid,part,pts,src,op=op,w=w,pr=pr,grade="HB",preset="construction_pencil",role="internal_break")

acts=[
 # ---------- decisive outer contour: body ----------
 CT("P5-C1","contour_hair_right",
   [[247,37],[258,38],[269,43],[278,52],[285,64],[288,78],[289,93],[287,108],[284,122],[280,136],[273,148],[265,156],[257,161]],
   "Decisive outer contour of the hair on the image-right, stated as one hair grouping without individual strands."),
 CT("P5-C2","contour_hair_left",
   [[244,37],[231,38],[218,41],[205,48],[192,58],[181,70],[172,84],[166,98],[165,112],[169,126],[178,138],[188,146],[197,151]],
   "Decisive outer contour of the hair on the image-left, wider than the right because the head turns away from that side."),
 CT("P5-C3","contour_jacket_right",
   [[266,157],[274,166],[280,178],[285,193],[289,211],[292,229],[295,247],[297,265],[299,283],[300,301],[301,319],[302,337],[301,351],[299,363],[297,374]],
   "Decisive image-right silhouette of the jacket from the shoulder to the hem; the hair tips hand silhouette ownership to the garment here rather than riding down it."),
 CT("P5-C4","contour_jacket_left",
   [[190,152],[182,166],[174,182],[166,198],[158,214],[152,232],[148,252],[147,272],[147,290],[150,308],[155,326],[160,344],[162,360],[162,376],[163,394]],
   "Decisive image-left silhouette of the loose jacket and the far hanging arm; below the prop handoff near canvas y=205 the garment, not the rifle, owns this edge."),
 CT("P5-C5","contour_shorts_right",[[297,374],[295,386],[292,396],[288,405]],
   "Image-right shorts silhouette between the jacket hem and the thigh pouch."),
 CT("P5-C6","contour_pouch_right",
   [[288,405],[297,405],[305,413],[308,431],[308,451],[305,466],[297,472]],
   "The thigh pouch owns the image-right silhouette between canvas y=405 and y=472; its outline is stated as a major attached shape with no buckles or stitching."),
 CT("P5-C7","contour_leg_brace_outer",
   [[297,472],[299,486],[300,504],[301,524],[301,544],[302,564],[304,584],[304,604],[305,624],[306,644],[306,652]],
   "Braced-leg outer silhouette from the pouch handoff down to the boot."),
 CT("P5-C8","contour_boot_right",
   [[279,650],[279,673],[280,695],[282,715],[287,733],[305,741],[329,741],[351,735],[362,724],[352,710],[338,698],[322,684],[310,668],[306,652]],
   "Near boot silhouette: shaft, toe swinging image-right, and the sole landing that is the lowest contact point in the picture."),
 CT("P5-C9","contour_leg_support_outer",
   [[167,396],[165,420],[164,444],[167,462],[171,482],[170,504],[166,528],[162,552],[161,576],[164,598],[167,618]],
   "Support-leg outer silhouette: the slimmer, more vertical of the two legs."),
 CT("P5-C10","contour_boot_left",
   [[166,624],[165,646],[166,666],[168,686],[172,704],[186,710],[204,709],[220,704],[223,692],[216,678],[204,666],[195,652],[192,636],[194,624]],
   "Far boot silhouette, smaller in frame and landing higher than the near boot."),
 CT("P5-C11","contour_leg_support_inner",
   [[212,398],[211,420],[210,442],[213,466],[209,492],[204,514],[198,536],[196,558],[194,580],[192,600],[191,620],[192,632]],
   "Inner silhouette of the support leg, which together with its neighbour states the tall negative-space wedge between the legs."),
 CT("P5-C12","contour_leg_brace_inner",
   [[235,414],[236,438],[240,462],[250,482],[257,502],[260,522],[266,542],[266,562],[268,582],[269,602],[275,622],[280,642]],
   "Inner silhouette of the braced leg, closing the negative space against the support leg."),
 # ---------- decisive outer contour: attached object ----------
 CT("P5-C13","contour_rifle_left",
   [[113,44],[113,68],[116,86],[133,92],[134,112],[136,132],[139,152],[142,172],[146,192],[151,214],[157,238],[164,262],[172,286],[179,308],[183,330],[185,354],[187,378],[192,400],[200,422],[206,440]],
   "Rifle silhouette, image-left edge: a fat suppressor, a hard step down to a near-vertical tapered handguard, then a widening receiver and stock. The rifle owns the outer silhouette above canvas y=205 and hands it to the jacket below.",
   op=.86,w=3.0,pr=.70),
 CT("P5-C14","contour_rifle_right",
   [[132,44],[133,68],[136,88],[150,96],[152,126],[158,142],[180,150],[186,180],[189,206],[193,228],[198,252],[203,276],[208,300],[214,326],[221,350],[229,376],[236,400],[242,428]],
   "Rifle silhouette, image-right edge; it steps out at the scope and again at the skeleton stock, so the prop keeps its own contour ownership across the torso.",
   op=.86,w=3.0,pr=.70),
 CT("P5-C15","contour_rifle_butt",[[206,440],[218,438],[232,433],[242,428]],
   "Buttstock end cap, closing the prop silhouette at the image-left hip.",op=.86,w=3.0,pr=.70),
 # ---------- major internal breaks ----------
 BR("P5-B1","break_bangs_grouping",[[203,71],[213,82],[226,88],[241,89],[254,93],[266,101],[273,112]],
   "Major hair grouping: the bangs edge that separates the hair mass from the face plane."),
 BR("P5-B2","break_jaw_chin",[[209,102],[212,116],[219,128],[230,137],[240,142],[249,143],[258,138],[265,128],[271,117],[273,107]],
   "Jaw and chin break, measured at close range: the contour reaches canvas x=273 at eye level and turns at a chin near (247,143), further image-right and lower than a whole-view estimate suggested."),
 BR("P5-B3","break_collar",[[214,150],[224,158],[238,162],[252,161],[262,155]],
   "Raised jacket collar: a major garment opening, stated without seams or folds."),
 BR("P5-B4","break_jacket_hem",[[162,332],[172,339],[181,333],[196,327],[210,318],[216,310]],
   "Jacket hem: this is a cropped jacket whose body ends at the belt, with a pointed corner on the image-left, while only the sleeves continue to the hips."),
 BR("P5-B5","break_belt",[[215,309],[233,315],[250,322],[266,328],[281,334]],
   "Belt band across the waist. It runs distinctly downhill toward image-right with the hip tilt, and is visible only where the jacket hem does not cover it."),
 BR("P5-B6","break_shorts_hem_left",[[167,394],[181,398],[197,400],[212,398]],
   "Shorts hem on the support thigh."),
 BR("P5-B7","break_shorts_hem_right",[[235,414],[251,418],[267,419],[282,414]],
   "Shorts hem on the braced thigh, lower in frame."),
 BR("P5-B8","break_sock_top_left",[[168,452],[182,449],[198,448],[212,451]],
   "Top edge of the support leg's thigh-high sock: a major clothing silhouette break on bare skin."),
 BR("P5-B9","break_sock_top_right",[[246,476],[262,472],[280,471],[296,474]],
   "Top edge of the braced leg's thigh-high sock, lower because that leg is nearer the camera."),
 BR("P5-B10","break_boot_top_left",[[166,626],[178,631],[190,630],[194,624]],
   "Opening of the far boot, where the sock enters the shaft."),
 BR("P5-B11","break_boot_top_right",[[279,650],[292,655],[303,654],[306,652]],
   "Opening of the near boot."),
 BR("P5-B12","break_sleeve_right",[[272,178],[278,216],[281,254],[282,292],[279,322],[275,346]],
   "Break between the near sleeve and the torso, the one internal line needed to keep the arm readable against the jacket."),
 BR("P5-B13","break_hand_right",[[281,330],[279,341],[281,352],[287,358],[295,358],[299,350],[300,340]],
   "Simple hand silhouette taken from the verified P4 block; no fingers."),
 BR("P5-B14","break_scope",[[158,146],[181,151],[184,196],[162,199]],
   "Dominant prop subpart: the scope, the one internal break required to read the rifle's topology at this scale."),
 BR("P5-B15","break_stock_opening",[[205,392],[221,388],[231,404],[214,412]],
   "Large cutout in the skeleton buttstock, the second piece of prop topology that keeps it from reading as a solid capsule."),
 BR("P5-B16","break_sling",[[207,148],[203,164],[200,180]],
   "Sling strap where it leaves the shoulder, kept as the prop's attachment relationship."),
]
run.draw_many(acts)
run.prepare_stage_review()
print("contour drawn")
