# Subject-only Stage Derivation

Most img2drawing jobs have one subject image and no same-subject intermediate drawings.
This is the default mode, not a degraded fallback.

## Core model

There is no hidden P1/P2/P3/P4/P5 answer image.

At stage `Pn`, the worker builds a **contract-constrained visual hypothesis** from:

1. the subject image — geometry truth;
2. the frozen StageContract — what may be represented now;
3. the current stage reference in `references/stages/` — how that type of stage is drawn;
4. the verified prior-stage drawing — structural continuity, never substitute geometry truth.

In shorthand:

`current_stage = observe(subject) constrained_by contract + preserve(prior_stage)`

not:

`current_stage = copy(some other drawing)`

## How each stage is derived

### P1 Gesture
Observe whole-body flow, crown/face direction, support/counterbalance and large attached
object axes directly from the subject. Do not search for a matching P1 answer image.

### P2 Primary Axes
Re-observe the subject for shoulder/pelvis/limb/object directions. Preserve the P1
gesture. P2 is a directional explanation of the same subject, not a trace of a generic
mannequin.

### P3 Primary Masses
Use visible occupied volume from the subject, including clothing-dominated volume.
Preserve P1/P2 direction. Do not infer a hidden naked-body contour merely because a
textbook figure study would show one.

### P4 Structural Connections
Explain visible chain transitions and overlap with the minimum structure required.
Occluded joints stay clothing-aware. If a joint only works by moving a P3 mass, reopen P3.

### P5 Clean Block-in
State the verified subject silhouette and major internal breaks. If clean contour must
contradict P3/P4, reopen upstream rather than beautifying the error.

## Review without a target answer

Every pass still has strong evidence:

- `subject_vs_drawing.png`
- `subject_split.png`
- registered subject/drawing overlay
- registered raw difference evidence
- generic grammar vs drawing for representation only
- Agent-selected local review crops
- prior-stage structure and pass memory

Review questions are stage-specific. For example, P2 asks whether directions agree;
P3 asks whether mass/negative space agrees; P5 asks whether silhouette ownership agrees.
The absence of a target answer does not remove the review boundary.

## Uncertainty rule

When the subject does not reveal an exact hidden structure:
- encode only what is necessary to explain the visible result;
- keep the uncertain construction simple;
- record the uncertainty in findings when it matters;
- never import coordinates or anatomy from an example image to make uncertainty disappear.

## Optional task-stage targets

If the caller explicitly provides a same-subject stage target, img2drawing switches to
`task_stage_target_augmented` mode for that stage.

This is optional additional evidence, not a requirement. Subject geometry remains the
conflict resolver even then.
