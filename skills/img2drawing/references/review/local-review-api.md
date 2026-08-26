# Local Review API

Local review exists to answer a **specific visual uncertainty** after the whole-view review.

The Agent chooses the region. The runtime never detects the head, pelvis, limb, joint, prop, or any other semantic region.

```python
local = run.prepare_local_review(
    label="head_face",
    intent="Check head tilt and its agreement with the subject",
    subject_box=(260, 0, 470, 225),
    drawing_box=(132, 0, 236, 116),
)
```

Pixel boxes use `(left, top, right, bottom)` with right/bottom exclusive.

## Authority
- ROI selection: Agent.
- Box coordinates: Agent.
- Runtime: bounds validation, exact crop, hashing, state binding, layout.
- CV / detector / landmark model: not used.
- Artistic interpretation: Agent.

## Separate coordinate spaces
Subject, current drawing and the optional task-stage target may have different dimensions and framing. Therefore each source receives its own explicit box.

Required:
- `subject_box`
- `drawing_box`

If the stage has a task-stage target, `task_target_box` is also required. Supplying one
when no target exists is an error.

## Generated artifacts
Each local review writes:
- exact source crops;
- `subject_vs_drawing.png`;
- optional `task_target_vs_drawing.png`;
- `local_reference_overview.png`;
- `local_review.json` with source hashes, source dimensions and exact boxes.

The pass also receives `local_reviews_manifest.json`.

## State integrity
A local review is bound to:
- stage;
- pass;
- current drawing artifact SHA-256;
- drawing-state SHA-256;
- history cursor.

Any drawing mutation makes the prepared stage review/local review stale. Re-render first; do not reuse an old crop judgement.

## Stage review linkage
Link local evidence explicitly:

```python
run.submit_stage_review(
    ...,
    local_review_ids=[local.local_review_id],
)
```

Local crops are evidence, not automatic PASS/FAIL gates.
