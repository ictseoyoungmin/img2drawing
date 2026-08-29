import sys, shutil, json
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0,str(Path(__file__).parent))
sys.path.insert(0, str(PROJECT_ROOT / "skills/img2drawing/src"))
from helpers import S
from img2drawing import DrawingRun

OUT=PROJECT_ROOT / "temp/dogfood/croquis-sniper-girl/run"
if OUT.exists(): shutil.rmtree(OUT)
run=DrawingRun.create(PROJECT_ROOT / "dev/dogfood/croquis-sniper-girl/01_output/subject_reference.png", OUT,
    width=512, height=768, working_supersample=3,
    session_id="sniper-girl-croquis-r1")
run.stage_start("P1_gesture")

# Dominant gesture: crown -> curved facial centre -> chin -> neck -> spine ->
# pelvis -> image-left (her left, far) SUPPORT leg -> weight landing.
dominant=[
 [245,36],[246,52],[249,68],[253,84],[257,100],[260,116],[258,128],[251,138],
 [243,148],[236,158],[234,176],[233,200],[235,228],[237,256],[239,286],[240,312],
 [238,336],[234,360],[228,382],[214,396],[200,410],[192,442],[187,486],[184,538],
 [183,578],[183,614],[186,656],[189,690],[191,706],
]

acts=[
 S("P1-A1","P1_gesture","crown_face_spine_support",dominant,role="gesture",
   pressure=.46,width=2.4,opacity=.62,grade="HB",confidence=.9,
   source=("Crown at the hair-parting apex, curved facial centre bowing toward "
           "image-right to encode the back-3/4 head turn, then chin, neck, spine "
           "down the visible back, pelvis, and transfer into the image-left "
           "(her far/left) support leg landing under the boot.")),
 # segmented OPEN cranial construction (crown arc + separate temporal->jaw arcs)
 S("P1-A2","P1_gesture","cranial_crown_arc",
   [[214,56],[224,46],[240,41],[256,44],[268,52]],
   pressure=.22,width=1.3,opacity=.30,grade="2H",
   source="Short open crown arc only; hair volume is deliberately excluded at P1."),
 S("P1-A3","P1_gesture","cranial_left_temporal_jaw",
   [[205,72],[199,86],[198,102],[204,118],[216,131],[232,139]],
   pressure=.20,width=1.25,opacity=.28,grade="2H",
   source="Open image-left temporal-to-jaw arc; narrower far-side mass because the head turns image-right."),
 S("P1-A4","P1_gesture","cranial_right_temporal_jaw",
   [[273,64],[279,80],[277,98],[269,116],[258,130]],
   pressure=.20,width=1.25,opacity=.28,grade="2H",
   source="Open image-right temporal-to-cheek-to-jaw arc; wider near-side facial mass."),
 S("P1-A5","P1_gesture","shoulder_rhythm",
   [[176,162],[199,150],[228,145],[256,150],[280,166],[292,182]],
   pressure=.19,width=1.2,opacity=.26,
   source="Broad shoulder rhythm of the back-3/4 torso; image-right (near) shoulder sits lower and further out."),
 S("P1-A6","P1_gesture","pelvis_rhythm",
   [[166,372],[192,364],[224,362],[258,368],[288,382]],
   pressure=.19,width=1.2,opacity=.26,
   source="Open pelvis rhythm; hip line tilts down toward the image-right braced leg."),
 S("P1-A7","P1_gesture","counterbalance_leg",
   [[258,400],[271,428],[276,478],[279,532],[288,584],[298,634],[310,700],[316,736]],
   pressure=.17,width=1.1,opacity=.22,
   source="Image-right (her right, near) leg braced outward as counterbalance, landing wider and lower in frame."),
 S("P1-A8","P1_gesture","rifle_major_axis",
   [[119,48],[131,86],[146,134],[161,182],[176,232],[192,282],[208,336],[222,390],[233,436]],
   pressure=.21,width=1.3,opacity=.28,
   source=("Slung sniper rifle major axis: suppressor tip upper-left to buttstock at the "
           "image-left hip; it changes the global envelope so its axis is stated at P1 but kept subordinate.")),
 S("P1-A9","P1_gesture","ground_weight_cue",
   [[168,712],[210,708],[260,722],[330,742]],
   pressure=.14,width=1.0,opacity=.18,
   source="Minimal ground cue: the near (image-right) boot lands lower in frame than the far boot."),
]
run.draw_many(acts)
art=run.prepare_stage_review()
print(json.dumps({"drawing":str(art.drawing.path),"dir":str(art.drawing.path.parent)},indent=1))
run.save_checkpoint()
