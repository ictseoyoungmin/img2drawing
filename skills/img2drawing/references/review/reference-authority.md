# Reference authority

img2drawing distinguishes three reference roles before any stage review.

## 1. Subject reference — geometry truth
The subject decides:
- pose;
- subject-specific proportions;
- perspective;
- overlap;
- weight distribution;
- subject-specific silhouette.

The subject does **not** decide which construction vocabulary belongs to P1/P2/P3/etc.

## 2. Task stage target — optional same-task stage truth
A task stage target is a drawing of the **same task/subject at the same stage**.

When present it is the strongest stage-specific comparison because it can express both:
- where the current subject should be represented;
- how far the current stage should have progressed.

It still may not override contradictory subject geometry.

Example:
```python
run = DrawingRun.create(
    "subject.png",
    "out",
    task_stage_targets={
        "P1_gesture": "same_subject_p1.png",
        "P2_primary_axes": "same_subject_p2.png",
    },
)
```

`stage_targets=` is a compatibility alias for `task_stage_targets=`.

## Authority order

With a task stage target:
`task_stage_target > subject_reference`

Without one the subject reference is the only geometry authority.

This is not a numerical scoring order. It determines which reference answers which question.
Stage grammar is not in this order at all: it comes from the frozen contract and the stage
reference, which never decide pose.

## Review artifacts
`prepare_stage_review()` now creates:
- subject ↔ drawing;
- subject split;
- optional task-target ↔ drawing;
- optional task-target split;
- a 2-way or 3-way `reference_authority_overview.png`.

The worker packet records the exact authority order for the current stage.
