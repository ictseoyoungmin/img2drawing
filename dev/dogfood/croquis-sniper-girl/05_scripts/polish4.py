import sys
from pathlib import Path
sys.path.insert(0,'/home/claude/work/croquis')
from img2drawing import DrawingRun, DrawingAction
run=DrawingRun.resume(Path('/home/claude/work/croquis/out'))
sess=run.session; ST='P6_identity_finish'
ir=sess.current_ir(); by={s.part:s for s in ir.strokes}
acts=[{"action_id":"PX-A1","kind":"draw_stroke","stage":ST,"role":"detail","part":"suppressor_muzzle_cap",
       "points":[[113,45],[118,41],[126,41],[132,45]],"stroke_id":"suppressor_muzzle_cap",
       "confidence":.9,"layer":31,
       "tool":{"preset":"construction_pencil","grade":"2B","overrides":{"pressure":.72,"width":1.8,"opacity":.86,"jitter":.035}},
       "observation_id":"obs-PX-A1",
       "source_observation":"Muzzle end cap of the suppressor: without it the fat cylinder read as an open bent bar rather than a closed tube."}]
for i,(p,op,w,pr) in enumerate([("break_scope",.88,2.0,.74),("break_stock_opening",.86,1.9,.72),
                                ("contour_rifle_butt",.90,2.6,.76),("stock_cutout_second",.86,1.8,.72)],1):
    s=by[p]
    acts.append({"action_id":f"PX-{i:02d}","kind":"replace_stroke","stage":ST,
      "role":s.role,"part":p,"points":[list(q) for q in s.points],
      "target_stroke_id":p,"stroke_id":p,"revision_of":p,"confidence":.9,"layer":30,
      "tool":{"preset":"construction_pencil","grade":"2B",
              "overrides":{"pressure":pr,"width":w,"opacity":op,"jitter":.035}},
      "observation_id":f"obs-PX-{i:02d}",
      "source_observation":"Final look at the prop against the subject.",
      "reason":"The rifle's identifying subparts were still reading as faint ticks beside a strong body contour; scope, stock cutouts and butt cap are re-laid at pressure so the prop is as recognisable as the figure."})
sess.execute_many_atomic([DrawingAction.from_dict(a) for a in acts], label="prop-confirm")
run.canvas.sync(sess.history)
run.canvas.render("/home/claude/work/final_croquis.png", supersample=4)
run.save_checkpoint()
print("ok")
