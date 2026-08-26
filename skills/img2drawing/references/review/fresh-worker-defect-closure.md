# Fresh-worker E2E Defect Closure

A worker can autonomously close P1→P3, but dogfood testing exposed six practical
defects. This reference closes them without making the runtime a semantic judge.

## 1. Version authority
`SKILL.md`, the runtime package version, and worker packets must identify the current
protocol consistently. A fresh worker must never have to infer which of several past
protocol revisions is authoritative.

## 2. Runnable benchmark packaging
A benchmark request must resolve to a concrete subject/reference bundle, not a
README-only directory. Inside the packaged skill the runnable bundle is
`examples/full_body_croquis/` (subject + executable run). The subject-only P1→P5
regression fixture lives in the development repository under
`dev/benchmarks/stage_reconstruction/full_body_croquis_subject_only/` and is not shipped.

## 3. Reliable finish
`DrawingRun.finish(timelapse="auto")` persists checkpoint, final drawing, compare,
session and review manifest *before* optional timelapse work. Expensive timelapse is
skipped when estimated raster work exceeds the budget. `timelapse="full"` remains an
explicit opt-in to force the expensive export.

## 4. Checkpoint / resume
The runtime atomically checkpoints after successful stage starts, drawing mutations, prepared reviews, and submitted reviews. Resume with:

```python
run = DrawingRun.resume(output_dir)
```

The checkpoint restores drawing history, stage progress, reviews, action memory,
local reviews and reopen context. Prepared review artifacts are intentionally stale;
after new edits, prepare fresh evidence.

## 5. Local review registration evidence
Agent-selected local reviews now include:
- `subject_drawing_overlay.png`
- `subject_drawing_absdiff.png`

Registration is only the correspondence implied by the Agent's explicit crop boxes.
Runtime does not detect landmarks, optimize alignment, or score correctness.

## 6. Canvas-scale material guidance
Worker packets provide a stage-aware width multiplier and minimum visible
pressure/opacity guidance for large canvases. These are guidance only; explicit
Agent-authored stroke material is never silently rewritten.

## Fresh residual sweep
Dogfood testing also showed that a worker can clear its remembered concern list while meaningful
subject-vs-drawing mismatch remains. Therefore before `ADVANCE`, the worker must make
a fresh residual-mismatch sweep that is *not limited to carried concerns*. New defects
may keep the stage at `REVISE`.
