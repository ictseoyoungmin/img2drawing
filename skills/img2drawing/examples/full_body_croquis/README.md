# Canonical full-body construction example

This example demonstrates the stage-free `DrawingSession` route for new work. It
does not use P1–P6 progression, stage review, an answer image, a target drawing,
or a `DrawingRun` checkpoint. It reads only the bundled `subject.png`, creates an
agent-authored observation and initial construct, and records one inspection sheet.

## What it demonstrates

- Records `PoseObservation` first.
- Expresses the line of action, turned masses, balance, joint chains, feet, and
  prop relation as `ConstructionMark` values.
- Treats authored mark order as drawing vocabulary, not a runtime phase gate.
- Reuses `DrawingSession`'s atomic `draw_many()` and the existing `InspectionSheet`.
- If the initial whole figure does not read as the pose, corrects explicit strokes
  and performs a fresh inspection before adding detail.

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
