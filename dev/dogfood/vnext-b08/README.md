# B08 intent scaffolding dogfood

이 fixture는 B05와 같은 subject/construction을 한 `DrawingSession`에 author한 뒤,
`observed/croquis/pose/pencil_loose`에서 `hybrid/figure_drawing/subject/graphite_academic`
으로 intent를 바꾼다. 두 선택은 서로 독립적인 plain data이고, 변경은 기존 action
cursor에서 provenance event로만 기록된다. stroke geometry와 history cursor는 전후에
같다. 두 mode guide와 두 style guide는 같은 core를 위한 관찰/authoring guidance이며,
새 pipeline, renderer, stage, raster filter를 만들지 않는다.

```bash
PYTHONPATH=skills/img2drawing/src python3 dev/dogfood/vnext-b08/run.py \
  --output /tmp/img2drawing-b08
```

`b08_intent_trace.json`에는 initial/changed intent, full provenance event, 두 mode와
두 style fixture, immutable inspection digest, geometry invariant, checkpoint resume
결과가 남는다. `custom:<identifier>`는 intent 데이터로 보존되지만 자동 prose
구조화하지 않는다.
