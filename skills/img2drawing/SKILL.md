---
name: img2drawing
description: Draws observed, imaginative, or hybrid subjects as inspectable hand-drawn images through one stage-free, residual-driven stroke workflow. Use for croquis, figure drawing, tonal study, free-draw, or custom style requests where explicit programmatic strokes and a replayable process matter.
---

# img2drawing

## Mission
Draw from references with explicit strokes. The worker/Agent is the semantic authority. CV/evidence tools may help the worker see, but may not decide pose, anatomy, or artistic correctness.

## Fresh-worker guarantee
A competent worker who receives only this skill, the available reference (if any), and
the requested drawing mode/style must be able to act without pass-by-pass coaching.

Observe or declare intent, draw explicit strokes, inspect the current snapshot, repair the
highest-impact residual, and repeat until the declared finish intent is materially met.
Do not stop after a routine pass to ask “continue?” or “is this okay?”. Ask only when the
source is missing/unreadable, the target is genuinely ambiguous, or requirements conflict.

## Authority model
For new work, `DrawingSession` is the only orchestration authority. `DrawingRun`,
`stages/`, stage review, and stage-oriented playbooks are legacy R23 compatibility only;
enter them through [`references/legacy-r23.md`](references/legacy-r23.md).

- `core/`: strokes, actions, history, session.
- `observation/`: agent-authored semantic observations and read-only evidence.
- `construction/`: stage-free pose, mass, balance, and joint guidance.
- `modes/`: declarative drawing goals; never lifecycle state.
- `review/`: current-state inspection and residual correction.
- `canvas/`: inspect and edit the current drawing.
- `render/`: canonical pencil-contact material.
- `provenance/`: replay and timelapse.

## Canonical drawing loop

New observed figure tasks use `img2drawing.DrawingSession` and the compact helpers
`PoseObservation`, `InitialConstruct`, `ConstructionMark`, `author_initial_construct()`,
and `inspect_initial_construct()`. Other drawing modes use the same session/history and
choose their own declarative guidance from [`references/INDEX.md`](references/INDEX.md).

For a figure, the first pass is one conceptual whole-figure hypothesis:

`read pose → line of action → head/ribcage/pelvis mass → balance/plumb → joints/limbs`

Before drawing, write a short `PoseObservation` covering support side, dominant flow,
head/ribcage/pelvis relationship, shoulder/pelvis opposition, silhouette keys, negative
spaces, ground, prop axis, occlusion, and uncertainty. Then author explicit subject-space
`ConstructionMark`s that express the observed relationships. This is drawing vocabulary,
not a runtime phase order; authored marks may be interleaved or revisited.
Use `author_initial_construct()` so the observation is recorded first and the marks are
sent through the existing atomic `draw_many()` path.

Use `inspect_initial_construct()` immediately after the first construct. It reuses the
existing `InspectionSheet` and can show the whole view, focused ROIs, contrast overlay,
`PlumbLine`, and `GroundGuide`. If the whole figure does not read as this subject's pose,
correct the construction premise before contour or detail. The worker remains free to
move backward when observation disproves a mark.

The coordinates in this example are intentionally agent-authored from the current subject;
never copy coordinates from a grammar exemplar.

```python
from img2drawing import (
    ConstructionMark, DrawingSession, InitialConstruct, PoseObservation,
    author_initial_construct, inspect_initial_construct,
)

session = DrawingSession.create(subject="subject.png", output_dir="out")

observation = PoseObservation(
    support_side="image-left with a wider counterbalance stance",
    flow="head-left → torso-right → pelvis-left reversal",
    head_ribcage_pelvis="head turns back over a three-quarter ribcage above a twisted pelvis",
    shoulder_pelvis="shoulders slope against the pelvis tilt",
    silhouette_keys=("light head mass", "long diagonal prop", "split boot stance"),
    negative_spaces=("arm-to-torso opening", "space between legs"),
    ground_relation="both feet land on the same ground plane",
    major_prop_axis="diagonal from image-left shoulder toward lower center",
    occluded_limb_evidence=("far arm continues behind the prop into the hand",),
)
construct = InitialConstruct(
    observation=observation,
    marks=(
        ConstructionMark("loa", "line_of_action", "gesture", "body_flow", ((120, 180), (126, 240), (142, 310))),
        ConstructionMark("head", "mass_blocking", "mass", "head", ((108, 110), (138, 96), (170, 118))),
        # Add ribcage/pelvis, joints/limbs, feet, and the prop axis.
    ),
)
author_initial_construct(session, construct)
inspect_initial_construct(session, construct)
```

Until the initial whole figure reads as this subject's pose, do not spend the quality
budget on metadata or detail coverage. The shared residual correction loop applies after
every mutation.

## Renderer policy

All normal drawing, review, replay, final export and timelapse paths use
`img2drawing.render.pillow_pencil_contact`. This is the sole default renderer because it
preserves pencil grade, pressure, contact, grain, paper interaction and eraser behavior.

Legacy uniform-pressure Pillow renderers are not shipped. A ballpoint request is a separate
material feature, not a reason to revive or silently emulate the removed renderer.

## Explicit stroke edits and retirement

Retirement is about the current representation, not whether an earlier line was “wrong”.
When a new axis, mass, or contour carries the information, choose whether the old cue
should remain faint or leave the visible branch.

- Use `soft_lift` (or `soft_lift_segment`) when the cue still explains weight, rhythm, or
  an occluded handoff.
- Use the public `delete_stroke` action when the complete stroke must be absent from the
  current drawing. The earlier stroke and deletion event remain in history.
- `hard_delete` is the history-layer method behind `delete_stroke`, recorded as
  `stroke.delete`; it is not a valid action kind by itself.

Do not raster-edit files or mutate history to clean the image. Supply the target stroke,
observation and reason, then render and inspect the mutated canvas afresh. Read
`references/review/stroke-retirement.md` for the API details.

## Required reading route

1. Read this file and [`references/INDEX.md`](references/INDEX.md).
2. Select the smallest relevant mode guide: croquis, figure drawing, tonal study, or
   free-draw.
3. Read `observation/visual-observation.md` for observed subjects and the relevant
   construction/figure/finish guide for the relationships present.
4. Create the first drawing through `DrawingSession`; inspect the whole result before
   adding detail, then use `review/residual-correction.md` for every repair loop.
5. Use `legacy-r23.md` only when explicitly continuing a `DrawingRun` checkpoint.

## Evidence boundary

`InspectionSheet`, registration, ROI, measurement, and renderer provenance make the
current state inspectable. They do not choose geometry, select the highest-impact issue,
or emit an artistic PASS/FAIL. The Agent compares the subject and current drawing (or
declared intent and current drawing for imaginative work), then records explicit edits.

The default sequence is whole → relation → part → relation again. Macro pose, mass,
balance, silhouette, and composition residuals outrank micro detail. A mutation makes
prior visual evidence stale; render and inspect a fresh snapshot.

## Legacy R23 continuation

Only when explicitly continuing an existing `DrawingRun` / R23 checkpoint, read
[`references/legacy-r23.md`](references/legacy-r23.md).

Do not use R23 P1–P6 lifecycle guidance for new work.
