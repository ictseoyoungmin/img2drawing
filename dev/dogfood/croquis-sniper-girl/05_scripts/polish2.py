import sys
from pathlib import Path
sys.path.insert(0,'/home/claude/work/croquis')
from img2drawing import DrawingRun, DrawingAction
run=DrawingRun.resume(Path('/home/claude/work/croquis/out'))
sess=run.session; ST='P6_identity_finish'
dels=[]
for i,p in enumerate(["hair_wisp_l1","hair_wisp_l2","hair_wisp_l3","hair_wisp_l4",
                      "hair_wisp_r1","hair_wisp_r2","hair_wisp_r3","hair_wisp_r4","hair_wisp_top"],1):
    dels.append({"action_id":f"PZ-D{i}","kind":"delete_stroke","stage":ST,"target_stroke_id":p,
      "confidence":1.0,"tool":{"preset":"hard_eraser","grade":"HB"},
      "observation_id":f"obs-PZ-D{i}",
      "source_observation":"Fresh look at the finished head after the wisp pass.",
      "reason":("These wisps were drawn protruding outside the hair contour and render as a row of sawteeth "
                "around the skull, which is worse than the smooth edge they were meant to fix. They are "
                "removed and the strand character is restated inside the silhouette instead.")})
sess.execute_many_atomic([DrawingAction.from_dict(a) for a in dels], label="wisp-removal")
def W(aid,part,pts,src,op=.60,w=1.4,pr=.52,grade="2B",layer=31):
    return {"action_id":aid,"kind":"draw_stroke","stage":ST,"role":"detail","part":part,
            "points":pts,"stroke_id":part,"confidence":.88,"layer":layer,
            "tool":{"preset":"construction_pencil","grade":grade,
                    "overrides":{"pressure":pr,"width":w,"opacity":op,"jitter":0.05}},
            "observation_id":"obs-"+aid,"source_observation":src}
add=[
 W("PZ-A1","hair_lock_inner_l1",[[173,92],[170,108],[172,122],[178,134]],
   "Strand separation running just inside the image-left hair edge, so the bob reads as stacked locks rather than one smooth shell."),
 W("PZ-A2","hair_lock_inner_l2",[[183,116],[180,130],[185,144]],
   "Second inner lock on the image-left, ending in a tapered tip above the shoulder."),
 W("PZ-A3","hair_lock_inner_r1",[[281,88],[282,104],[279,120]],
   "Strand separation just inside the image-right hair edge."),
 W("PZ-A4","hair_lock_inner_r2",[[275,114],[275,130],[269,144]],
   "Second inner lock on the image-right."),
 W("PZ-A5","hair_lock_inner_r3",[[267,138],[265,150],[259,157]],
   "Lowest inner lock on the image-right, tapering into the tip that rests on the shoulder."),
 W("PZ-A6","hair_notch_left",[[167,116],[173,124]],
   "Short notch cutting inward from the image-left hair edge where two locks separate.",op=.52,w=1.3,pr=.46),
 W("PZ-A7","hair_notch_right",[[285,126],[279,136]],
   "Matching inward notch on the image-right edge.",op=.52,w=1.3,pr=.46),
]
sess.execute_many_atomic([DrawingAction.from_dict(a) for a in add], label="hair-locks")
lifts=[]
for i,(p,st,rs) in enumerate([
  ("hairline_bangs_edge",.55,"The retired P3 bangs edge still crosses the drawn eyes; the authored bang strands now carry that information."),
  ("head_cross_axis",.70,"The P2 head cross-axis remains faintly visible across the features and is retired further."),
 ],1):
    lifts.append({"action_id":f"PZ-L{i}","kind":"soft_lift","stage":ST,"target_stroke_id":p,
      "confidence":1.0,"tool":{"preset":"soft_eraser","grade":"HB","overrides":{"erase_strength":st}},
      "metadata":{"strength":st},"observation_id":f"obs-PZ-L{i}",
      "source_observation":"Fresh look at the finished head.","reason":rs})
sess.execute_many_atomic([DrawingAction.from_dict(a) for a in lifts], label="face-clarify-2")
run.canvas.sync(sess.history)
run.canvas.render("/home/claude/work/final_croquis.png", supersample=4)
run.save_checkpoint()
print("ok")
