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

## 3. Grammar exemplar — representation only
Grammar exemplars teach:
- stage abstraction vocabulary;
- line hierarchy;
- stroke economy;
- detail budget;
- construction conventions.

Never copy from a grammar exemplar:
- pose;
- coordinates;
- subject proportions;
- subject perspective.

## Authority order

With a task stage target:
`task_stage_target > subject_reference > grammar_exemplar`

Without one:
`subject_reference > grammar_exemplar`

This is not a numerical scoring order. It determines which reference answers which question.

## Review artifacts
`prepare_stage_review()` now creates:
- subject ↔ drawing;
- subject split;
- grammar ↔ drawing;
- optional task-target ↔ drawing;
- optional task-target split;
- a 3-way or 4-way `reference_authority_overview.png`.

The worker packet records the exact authority order for the current stage.
