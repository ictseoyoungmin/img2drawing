# B07 evidence-budget dogfood

이 fixture는 B05의 동일 subject/construct에서 near-arm premise 하나를 의도적으로
나쁘게 만든 뒤 `DrawingSession`의 비용 제한 loop를 실행한다.

```bash
PYTHONPATH=skills/img2drawing/src python3 dev/dogfood/vnext-b07/run.py --output /tmp/img2drawing-b07
```

첫 번째 review는 `mode="quick"` 단일 tiled whole-view sheet이고, 두 번째 review는
quick view가 남긴 arm-to-torso 불확실성에 대한 두 개 ROI의 `focused` escalation이다.
두 sheet에서 실제로 읽은 `sheet`와 `contrast_overlay`를 telemetry에 기록하고, 이전
immutable evidence는 drawing digest가 바뀌지 않은 상태에서만 current로 취급한다.

`b07_evidence_trace.json`은 vNext의 2 review turns / 8 visual artifacts / 12 generated
artifacts / 4 image reads와 보존된 R23 `03_stage_reviews`의 5 ceremonies / 12 image
files / 60 total files를 나란히 기록한다. 수치는 비용 관찰용이며 likeness나 artistic
PASS/FAIL 점수가 아니다.
