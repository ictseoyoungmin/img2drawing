# Visual observation

Read whole → region → part → relation. Evidence maps and measurements help the worker
see; they never decide pose, anatomy, likeness, or artistic correctness.

## Before the first stroke

For a new vNext session, write a short agent-authored `PoseObservation` covering support
side, dominant flow, head/ribcage/pelvis relationship, shoulder/pelvis opposition,
silhouette keys, negative spaces, ground, prop axis, occlusion and uncertainty. Record it
with `DrawingSession.observe()` or `observe_pose()` before the initial construct.

This is a semantic snapshot, not automatic pose inference and not a lifecycle lock. If a
later view disproves it, update the observation through an explicit session action and
reinspect the affected drawing state.

## Whole-view questions

- What is the body view and torso turn?
- Which foot supports weight and where does the counterbalance land?
- How do head, ribcage and pelvis rotate relative to one another?
- Which silhouette breaks, negative spaces, or prop/body contacts identify this subject?
- Which arm, hand, leg, or foot is occluded, and what evidence locates its endpoint?

Do not replace these questions with a copied landmark table or ideal stroke image.

## Relationship evidence

When whole-view review leaves a concrete uncertainty, choose a focused ROI explicitly and
use the existing read-only inspection helpers. Grid, plumb, relative distance, angle,
negative-space width, profiles, pixel samples, and contour/envelope comparisons describe
relationships and provenance only. They do not emit an artistic verdict or rewrite
geometry.

For an axis that looks plausible while a part is too thin, record an occupied envelope
separately from the centre axis. For torso orientation, lower body, head/hair, and
attached objects, preserve view label, near/far exposure, bounds, overlap order, and
uncertainty rather than guessing a generic primitive.

## Registration and evidence

`InspectionSheet` accepts an explicit subject-to-canvas registration:

```text
canvas = offset + subject * scale
```

Registered images are presentation evidence; they never alter authored stroke
coordinates. Bind inspection artifacts to the exact subject bytes, raw drawing artifact,
and stage-free drawing state digest. After any mutation, render and inspect a fresh
snapshot; do not reuse stale crops or verdicts.
