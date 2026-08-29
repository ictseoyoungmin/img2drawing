# S10 integration report

Status: **CLOSED** after the R23 quality run and direct whole-view inspection.

## Authority and negative controls

`subject_reference.png` is immutable geometry authority. The material-1 critic
and matte are retained only as a false-positive negative fixture; material-2's
subject-specific workflow and existing PASS verdict are not imported. The old
R22 identity run is retained as a blanket-restatement regression fixture.

## Current closure evidence

- Positive run: `s10-quality-run/quality_run_report.json`
- Final and comparison: `s10-quality-run/final/drawing.png`,
  `s10-quality-run/compare/subject_vs_final.png`
- Observation lock: `s10-quality-run/session/checkpoint.json`
- P4/P5 resolved-form manifests and independent reviews: under
  `s10-quality-run/reviews/`
- P5 construction retirement: `s10-quality-run/review_manifest.json`
- P6 calibration and bounded identity manifest: `s10-quality-run/identity/`

The evaluator inspected raw whole view, subject comparison, and face/garment/
prop relations before reading process rationale. The run keeps face opening
separate from grouped hair, introduces a small number of garment folds and
organic joint turns, and preserves rifle component topology. P4/P5 process
records and visual records share the same drawing state, artifact, cursor, and
observation-lock digest.

## What the gate does not claim

This is not an automated art-quality score and does not claim pixel likeness.
The optional P6 is bounded and cannot repair an upstream blocker. A future
reopen is required if direct inspection again finds a macro mismatch.
