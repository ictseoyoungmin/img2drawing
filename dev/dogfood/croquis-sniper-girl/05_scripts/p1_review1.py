import sys, json
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0,str(Path(__file__).parent))
sys.path.insert(0, str(PROJECT_ROOT / "skills/img2drawing/src"))
from img2drawing import DrawingRun
OUT=PROJECT_ROOT / "temp/dogfood/croquis-sniper-girl/run"
run=DrawingRun.resume(OUT)
run.prepare_stage_review()
h=run.prepare_local_review(label="head_face",
    intent="Check crown origin, facial-centre curvature and whether the open cranial arcs avoid a closed badge.",
    subject_box=(300,50,620,300), drawing_box=(150,25,310,150), grammar_box=(30,20,260,290))
p=run.prepare_local_review(label="pelvis_legs",
    intent="Check pelvis-to-support-leg weight transfer and support vs counterbalance differentiation.",
    subject_box=(280,700,760,1520), drawing_box=(140,350,380,760), grammar_box=(15,400,275,1080))
print(h.local_review_id, p.local_review_id)
print(h.to_dict().get('board') or h.to_dict())
