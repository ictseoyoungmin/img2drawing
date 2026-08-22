import sys, json
from pathlib import Path
sys.path.insert(0,'/home/claude/work/croquis')
from helpers import S
from img2drawing import DrawingRun
run=DrawingRun.resume(Path("/home/claude/work/croquis/out"))
ed=run.canvas_editor if hasattr(run,'canvas_editor') else None
sess=run.session
ST="P6_identity_finish"
def F(aid,part,pts,src,op=.72,w=1.7,pr=.56,grade="B",preset="construction_pencil",role="detail",layer=30):
    return S(aid,ST,part,pts,role=role,preset=preset,grade=grade,pressure=pr,width=w,
             opacity=op,jitter=.04,confidence=.88,layer=layer,source=src)
acts=[
 # ---------------- FACE ----------------
 F("ID-F01","eye_right_upper_lash",[[228,101],[231,99],[235,98],[240,99],[244,101],[246,104]],
   "Near (her right) eye: the upper lash line is the heaviest mark of the face, thickening toward the outer corner exactly as the subject shows.",
   op=.90,w=2.0,pr=.70,grade="2B"),
 F("ID-F02","eye_right_lower_lid",[[231,106],[236,107],[241,106],[245,104]],
   "Lower lid of the near eye, thinner and lighter than the lash line.",op=.62,w=1.4,pr=.48),
 F("ID-F03","eye_right_iris",
   [[234,100],[233,103],[235,106],[239,106],[241,103],[240,100],[237,99],[234,101],[236,105],[240,104],[239,101],[236,102]],
   "Iris of the near eye, drawn as one closed ring re-entered a second time to build the dark red value the subject shows.",
   op=.86,w=2.0,pr=.66,grade="4B"),
 F("ID-F04","eye_right_pupil",[[236,102],[238,104],[237,102],[238,103]],
   "Pupil core: a small dense accent inside the iris.",op=.92,w=2.2,pr=.76,grade="6B"),
 F("ID-F05","eye_left_upper_lash",[[256,108],[260,106],[265,106],[269,108],[271,111]],
   "Far (her left) eye: the same lash construction, shorter and lower because the head is turned toward it.",
   op=.86,w=1.9,pr=.66,grade="2B"),
 F("ID-F06","eye_left_lower_lid",[[258,113],[262,114],[266,113],[269,111]],
   "Lower lid of the far eye.",op=.60,w=1.4,pr=.48),
 F("ID-F07","eye_left_iris",[[260,108],[259,111],[261,114],[264,114],[266,111],[265,108],[262,107],[260,110],[263,113],[265,110]],
   "Iris of the far eye, slightly compressed by the turn.",op=.84,w=1.9,pr=.64,grade="4B"),
 F("ID-F08","eye_left_pupil",[[262,110],[263,112],[262,110]],
   "Pupil core of the far eye.",op=.90,w=2.0,pr=.74,grade="6B"),
 F("ID-F09","nose",[[253,117],[255,120],[256,122],[253,123]],
   "Nose: only the small shadow plane and the underside the subject actually shows, no nostrils or bridge line.",
   op=.55,w=1.3,pr=.46),
 F("ID-F10","mouth_upper",[[244,130],[247,129],[250,130],[253,130]],
   "Upper lip line of the small closed mouth.",op=.70,w=1.5,pr=.54),
 F("ID-F11","mouth_lower",[[245,133],[248,133],[251,132]],
   "Lower lip, lighter than the upper line.",op=.50,w=1.3,pr=.44),
 F("ID-F12","jaw_chin_refined",[[261,113],[262,120],[262,127],[259,134],[254,139],[248,142],[242,142]],
   "Refined jaw and chin taken from the close observation: the chin sits slightly further image-right and lower than the block-in estimate.",
   op=.72,w=1.8,pr=.58),
 F("ID-F13","ear_outer",[[200,93],[198,99],[199,106],[203,111],[207,112]],
   "Her right ear, visible on the image-left of the face because the head is turned that far.",op=.66,w=1.5,pr=.52),
 F("ID-F14","ear_inner",[[202,98],[203,104],[205,108]],
   "Inner fold of the ear.",op=.46,w=1.2,pr=.40),
 # ---------------- HAIR ----------------
 F("ID-H01","hair_part_crown",[[240,40],[236,50],[231,62],[227,74]],
   "Crown parting of the bob, the origin every strand group radiates from.",op=.50,w=1.4,pr=.44),
 F("ID-H02","hair_bang_long_right",[[233,45],[240,62],[249,80],[258,96],[266,110],[271,124]],
   "The long bang that sweeps across the forehead and falls over the far eye, the most recognisable single strand of this bob.",
   op=.66,w=1.7,pr=.54),
 F("ID-H03","hair_bang_second",[[228,48],[229,66],[232,84],[236,100]],
   "Second bang group falling between the eyes.",op=.52,w=1.4,pr=.46),
 F("ID-H04","hair_bang_near_eye",[[222,52],[218,70],[216,88],[217,104],[221,118]],
   "Near-side face-framing lock that runs down past the ear to the jaw.",op=.56,w=1.5,pr=.48),
 F("ID-H05","hair_lock_left_outer",[[214,44],[199,60],[187,78],[180,98],[181,118],[188,136]],
   "Outer strand group on the image-left, following the widest sweep of the bob.",op=.48,w=1.4,pr=.44),
 F("ID-H06","hair_lock_right_outer",[[258,42],[272,54],[280,72],[281,92],[277,112],[271,132]],
   "Outer strand group on the image-right.",op=.48,w=1.4,pr=.44),
 F("ID-H07","hair_tips_left",[[170,128],[176,140],[184,148],[190,145],[196,152]],
   "Ragged tips where the image-left side of the bob ends just below the jaw.",op=.52,w=1.4,pr=.46),
 F("ID-H08","hair_tips_right",[[280,130],[276,142],[270,152],[264,158],[258,162]],
   "Ragged tips on the image-right, hanging slightly lower than the other side.",op=.52,w=1.4,pr=.46),
 F("ID-H09","hair_stray_top",[[236,34],[244,28],[252,32]],
   "The single stray hair above the crown that the subject shows against the sky.",op=.40,w=1.2,pr=.36),
 F("ID-H10","hair_neck_strand",[[247,140],[252,152],[254,164]],
   "Short strand falling in front of the collar.",op=.44,w=1.3,pr=.40),
]
sess.execute_many_atomic([__import__('img2drawing').DrawingAction.from_dict(a) for a in acts], label="identity-face-hair")
run.canvas.sync(sess.history)
run.canvas.render("/home/claude/work/id_face.png", supersample=4)
print("ok")
