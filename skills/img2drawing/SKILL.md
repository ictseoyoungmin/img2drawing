---
name: img2drawing
description: Creates inspectable hand-drawn images through one stage-free, residual-driven stroke workflow using observed, imaginative, or hybrid reference authority. Supports subject-backed and subjectless sessions without fabricating reference evidence.
---

# img2drawing

## Mission
Draw from references with explicit strokes. The worker/Agent is the semantic authority. CV/evidence tools may help the worker see, but may not decide pose, anatomy, or artistic correctness.

## Fresh-worker guarantee
A competent worker who receives this skill, an available reference for observed work,
and the requested drawing mode/style must be able to act without pass-by-pass coaching.

Observed work supplies a readable subject. Imaginative work supplies an explicit canvas,
an imaginative `DrawingIntent`, and `ReferenceAuthority.imaginative()` with concrete
composition/shape goals. Hybrid work supplies a subject plus distinct preserved and
transformed `ReferenceConstraint` records. Never create a blank placeholder subject or
claim overlay/registration evidence when no reference exists. Read
[`references/reference-authority.md`](references/reference-authority.md).

Observe or declare intent, draw explicit strokes, inspect the current snapshot, repair the
highest-impact residual, and repeat until the declared finish intent is materially met.
Do not stop after a routine pass to ask “continue?” or “is this okay?”. Ask only when the
source is missing/unreadable, the target is genuinely ambiguous, or requirements conflict.

## Authority model
For new work, `DrawingSession` is the only orchestration authority. `DrawingRun`,
`stages/`, stage review, and stage-oriented playbooks are legacy R23 compatibility only.
Enter them explicitly through `img2drawing.legacy.r23` and read
[`references/legacy-r23.md`](references/legacy-r23.md). Root legacy attributes are
deprecated, non-advertised compatibility shims—not a normal import route.

- `core/`: strokes, actions, history, session.
- `observation/`: agent-authored semantic observations, material palette, read-only evidence.
- `construction/`: stage-free pose, mass, balance, and joint guidance.
- `modes/`: declarative drawing goals; never lifecycle state.
- `review/`: current-state inspection and residual correction.
- `canvas/`: inspect and edit the current drawing.
- `render/`: canonical pencil-contact material and the cached tone scale.
- `provenance/`: replay and timelapse.

## Plain-data drawing intent

Use `DrawingIntent` when the request names a reference relationship, drawing mode,
finish emphasis, or style profile. Its four fields are orthogonal data selections:
`reference_mode` (`observed`, `imaginative`, `hybrid`), `drawing_mode` (`croquis`,
`figure_drawing`, `tonal_study`, `free_draw`), `finish_intent` (`pose`, `subject`,
`form_light`, `expressive`), and `style_profile` (the built-ins `pencil_loose`,
`graphite_academic`, or an explicit `custom:<identifier>`). No field is a stage, cursor,
pipeline, or completion gate. `DrawingSession.create(intent=...)` records the initial
selection; `session.set_intent(..., reason=...)` records a later selection as provenance
without changing geometry or forking the action history. A session's reference authority
mode is immutable: an intent change may adjust drawing/finish/style axes but cannot
silently redefine what counts as comparison truth.

Resolve the matching `ModeGuide` for observations and construction vocabulary,
`FinishGuide` for the relationships and omissions required by the stopping target, and
`StyleGuide` for the material behavior of the selected marks. Reference/geometry truth
outranks finish advice, which outranks a conflicting style preference. These guides are
immutable plain data: they do not advance, close, judge, select a renderer, or apply a
raster post-filter. Read [`references/finish/identity-and-value.md`](references/finish/identity-and-value.md)
before subject, form-light, or expressive refinement. A guide may be read again when an
inspection changes the Agent's hypothesis. The explicit compatibility lookup
`full_body_croquis` returns an ordinary `observed`/`croquis` intent and is not a lifecycle
state. See [`references/intent.md`](references/intent.md).

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

For each repair, anchor the Agent's selected mismatch with `DrawingSession.record_residual()`
against the latest inspection and observation. Choose `scope="global"` when a premise or
mass must be reconstructed, or `scope="local"` for a bounded contour/segment concern.
Apply an explicit `replace_stroke`, `replace_segment`, `soft_lift`, `delete_stroke`, or
`draw` action, inspect the new snapshot, and bind the action plus fresh inspection with
`resolve_residual()` (or `record_correction(decision="revise")` when the attempt is not
accepted). A mutation makes prior evidence stale; the Agent chooses priority and keeps
or revises the residual. Read [`review/residual-correction.md`](references/review/residual-correction.md)
for the compact record fields and provenance contract.

### Evidence budget

`DrawingSession.inspect()` defaults to one tiled whole-view sheet (`mode="quick"`).
Quick accepts no ROI, guide, grid, or measurement extras. The Agent may choose
`mode="focused"` with one to three prioritized ROIs (and no guides, grid, or
measurements), or opt into `mode="deep"` with up to three ROIs and guides/grid/measurements
when uncertainty warrants it. Deep escalation must include a short human-readable
`escalation_reason`;
these are inspection presentation/read budgets, not lifecycle stages or acceptance
gates. Observable reads can be recorded with
`session.record_evidence_read(inspection_id, artifact="sheet")`. Telemetry counts
artifacts, reads, review turns, and elapsed work only; it never selects a residual,
changes geometry, or emits an artistic PASS/FAIL. Earlier immutable sheets remain
available and are marked stale when their drawing-state digest no longer matches.

## Three questions before a mark, and again before a correction

These are cheap to ask and they are where completed drawings actually go wrong. A
correction is a new premise and inherits none of them, so ask them again on every repair.

1. **What does this line separate?** Name both sides. Same name on both sides means the
   stroke duplicates an existing contour instead of articulating anything; an inner limb
   edge that separates sleeve from sleeve is in the wrong place. Put the relation in
   `part`.
2. **Could my measurement see this boundary?** A luminance profile answers only a
   luminance question. On a subject in dark clothing, bare skin and a mid-grey background
   sit together far from the garment, so a darkness scan reports skin as absent body and
   cuts a false notch where a hand emerges. Build a `SubjectPalette`, read
   `ambiguous_pairs()`, and ask `boundary_kind()` before trusting an edge.
3. **Did I observe this ending, or assume it?** Hands, feet, features and hair tips are
   where invention is cheapest. Two arms do not imply two visible hands; a gloved hand in
   a pocket has no visible knuckles; a jaw does not continue under hair. Occluded means
   draw no ending - the limb's contour runs into whatever hides it.

Establish a chain before refining what it ends in: shoulder to elbow to wrist, then the
hand. A third correction in a row to one terminal means its parent limb was never drawn.

Read [`references/observation/measuring-boundaries.md`](references/observation/measuring-boundaries.md)
before the first measurement of a new subject.

## Value and tone

A value region is one authored decision. Use `DrawingSession.fill_region()` with
the mean `value` you read off the subject (0 black - 255 paper); the material
that reaches it comes from a cached deposition calibration. Lights inside a
dark mass are `reserved` by the fill, not erased back out afterwards.

Do not manually generate individual value strokes, sample straight lines into
polylines, or probe renderer opacity/pressure inside a drawing session - those
are renderer capabilities, regenerated by
`dev/calibration/calibrate_tone_scale.py`.
Read [`references/value/tone-and-fill.md`](references/value/tone-and-fill.md)
before any value work.

## Renderer policy

All normal drawing, review, replay, final export and timelapse paths use
`img2drawing.render.pillow_pencil_contact`. This is the sole default renderer because it
preserves pencil grade, pressure, contact, grain, paper interaction and eraser behavior.

Final PNG, cursor replay, and GIF export use the session's immutable `RenderProfile`.
Call `session.render_final()`, `session.render_at()`, and `session.export_timelapse()`;
do not call a different renderer or change supersampling/material kwargs per output.
Replay always includes cursor 0 and latest. A value region is one authored replay action,
not one frame per generated contact. Read
[`references/output/render-profile-and-replay.md`](references/output/render-profile-and-replay.md)
before exporting. A pre-B11 checkpoint must call `migrate_render_profile()` explicitly
before canonical output.

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
   free-draw; select a style guide only when the request calls for one.
3. Read `references/reference-authority.md`, then
   `references/observation/visual-observation.md` for observed
   subjects, and
   `references/observation/measuring-boundaries.md` before profiling anything, then the relevant
   construction/figure/finish guide for the relationships present.
4. Create the first drawing through `DrawingSession`; inspect the whole result before
   adding detail, then use `references/review/residual-correction.md` for every repair loop.
5. Read `references/review/completion.md` and bind the Agent's decision to the latest current
   inspection; continue the same correction loop if that record becomes stale.
6. Use `references/output/render-profile-and-replay.md` for final PNG or process export.
7. Use `references/legacy-r23.md` and `img2drawing.legacy.r23` only when explicitly continuing or
   migrating a `DrawingRun` checkpoint.

## Evidence boundary

`InspectionSheet`, registration, ROI, measurement, and renderer provenance make the
current state inspectable. They do not choose geometry, select the highest-impact issue,
or emit an artistic PASS/FAIL. Subjectless sessions produce an honest drawing-only sheet;
subject overlay, registration, subject-space ROI, and subject measurements fail explicitly.
The Agent compares the subject or declared authority with the current drawing, then
records explicit edits.

The default sequence is whole → relation → part → relation again. Macro pose, mass,
balance, silhouette, and composition residuals outrank micro detail. A mutation makes
prior visual evidence stale; render and inspect a fresh snapshot.

## Completion provenance

Finish only after a fresh inspection under the current `DrawingIntent` and after every
recorded material residual is resolved. Call `session.finish(final_inspection_id=...,
rationale=..., accepted_limitations=..., unresolved_nonmaterial_notes=...)`; do not write
arbitrary finish metadata. `FinishRecord` binds the Agent decision to the exact intent
digest, drawing-state hash, history cursor, and inspection. It is not an artistic PASS or
a lock. A later mark, intent change, or newly recorded material residual makes
`session.finish_is_current` false, after which the ordinary correction loop continues.
Read [`references/review/completion.md`](references/review/completion.md) before recording
completion.

## Legacy R23 continuation

Only when explicitly continuing an existing `DrawingRun` / R23 checkpoint, read
[`references/legacy-r23.md`](references/legacy-r23.md).

Import compatibility operations from `img2drawing.legacy.r23`; do not use deprecated
root shims in new code. Do not use R23 P1–P6 lifecycle guidance for new work.
