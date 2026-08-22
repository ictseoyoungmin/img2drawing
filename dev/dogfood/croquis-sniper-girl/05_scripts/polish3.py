import sys
from pathlib import Path
sys.path.insert(0,'/home/claude/work/croquis')
from img2drawing import DrawingRun, DrawingAction
run=DrawingRun.resume(Path('/home/claude/work/croquis/out'))
sess=run.session; ST='P6_identity_finish'
acts=[]
for i,(p,rs) in enumerate([
 ("head_cross_axis",
  "Soft lift reduces stroke opacity but not the graphite the renderer deposits from pressure, so this P2 axis still runs straight across both drawn eyes after two lifts. The P5 reference allows explicit deletion as a form of replayable retirement, and its full geometry and provenance survive in the P2 review record."),
 ("hairline_bangs_edge",
  "Same reason: the retired P3 bangs edge still cuts across the far eye. The authored bang strands now carry that boundary, so the superseded guide is explicitly deleted."),
 ("head_cross_contour_brow",
  "Same reason: the retired P3 brow cross-contour still reads as a line through both eyes."),
],1):
    acts.append({"action_id":f"PY-D{i}","kind":"delete_stroke","stage":ST,"target_stroke_id":p,
      "confidence":1.0,"tool":{"preset":"hard_eraser","grade":"HB"},
      "observation_id":f"obs-PY-D{i}",
      "source_observation":"Inspection of the finished head at four-times supersample.","reason":rs})
sess.execute_many_atomic([DrawingAction.from_dict(a) for a in acts], label="face-clear")
run.canvas.sync(sess.history)
run.canvas.render("/home/claude/work/final_croquis.png", supersample=4)
run.save_checkpoint()
print("ok")
