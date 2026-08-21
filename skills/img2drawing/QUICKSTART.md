# Quickstart

The default real-world path assumes **one subject image only**.

```python
from img2drawing import DrawingRun

run = DrawingRun.create("subject.png", "out")
run.stage_start("P1_gesture")
```

Reference authority in this mode is:

`subject_reference > grammar_exemplar`

The bundled stage exemplar images are **generic grammar examples**. They are not
P1/P2/P3/P4/P5 answers for the current subject and must never provide pose,
coordinates, proportions or perspective.

The worker derives each stage from:
- the subject image as geometry truth;
- the frozen StageContract for representation scope;
- the generic grammar exemplar for stroke vocabulary/detail budget;
- the verified drawing state from earlier stages.

Optional same-subject stage targets are supported only when a caller explicitly
supplies `task_stage_targets={...}`. They are not required for ordinary use.

## Autonomous loop

For every stage:

`observe subject → author explicit strokes → prepare_stage_review() → inspect whole/local evidence → revise → fresh review → advance`

After any successful drawing mutation, the runtime atomically checkpoints the run. A
successful `prepare_stage_review()` also guarantees its rendered drawing state is
resumable through:

```python
resumed = DrawingRun.resume("out")
```

Do not ask the user for routine stage-by-stage approval.

## Subject-only benchmark

```bash
python benchmarks/stage_reconstruction/full_body_croquis_subject_only/run_smoke.py
```

That benchmark directory intentionally contains no same-subject stage target drawings.
