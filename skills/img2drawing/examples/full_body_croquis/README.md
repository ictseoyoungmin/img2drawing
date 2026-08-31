# Canonical full-body construction example

이 예제는 새 작업의 stage-free `DrawingSession` 경로를 보여준다. P1–P6 진행,
stage review, answer image, target drawing, 또는 `DrawingRun` checkpoint를 사용하지
않는다. bundled `subject.png`만 읽어 agent-authored observation과 initial construct를
만들고, 하나의 inspection sheet를 기록한다.

## What it demonstrates

- `PoseObservation`을 먼저 기록한다.
- line of action, turned masses, balance, joint chains, feet, and prop relation을
  `ConstructionMark`로 명시한다.
- authored mark order는 drawing vocabulary이며 runtime phase gate가 아니다.
- `DrawingSession`의 atomic `draw_many()`와 기존 `InspectionSheet`를 재사용한다.
- initial whole figure가 pose로 읽히지 않으면 detail을 추가하지 않고 explicit stroke를
  수정한 뒤 fresh inspection을 수행한다.

The coordinates in `run.py` belong only to the bundled subject. They are not a general
landmark table or a target to copy for another subject.

## Run

From the repository root:

```bash
PYTHONPATH=skills/img2drawing/src python skills/img2drawing/examples/full_body_croquis/run.py \
  --output ./tmp/full_body_croquis_example
```

The output contains the portable checkpoint, raw drawing, inspection sheet, and
stage-free trace. The example does not claim a finished illustration; it is a minimal
construction-and-inspection fixture for the canonical route.

## Legacy continuation

Existing R23 stage runs are documented separately in
[`../../references/legacy-r23.md`](../../references/legacy-r23.md). Do not use that route
for new work or for tonal/free-draw requests.
