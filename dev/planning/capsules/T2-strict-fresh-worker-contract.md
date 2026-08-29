# T2 strict packaged fresh-worker contract capsule

Status: `ACTIVE — contract and verifier ready; external execution pending`

## Closed in this slice

- `prepare_strict_fresh_worker_input.py` creates a non-overwriting input envelope
  containing only a candidate skill ZIP, the supplied subject, and a user goal.
- The candidate ZIP excludes `examples/`, `build/`, `dist/`, caches and egg-info so
  packaged dogfood subjects, targets, coordinates and generated artifacts cannot
  silently become fresh-worker inputs.
- Envelope, returned report and independent visual-review schemas are versioned under
  `dev/schemas/strict_fresh_worker_*.schema.json`.
- `verify_strict_fresh_worker.py` validates hashes, allowlist/forbidden context,
  worker/evaluator session separation, returned paths, schema records, mechanical
  audit parity and non-portable provenance tokens. It deliberately does not create
  a run or grant artistic approval.
- `audit_fresh_worker.py` accepts the current P1→P5/P6 registry and reports
  `semantic_visual_audit_required: true`; the existing scripted fixture is therefore
  mechanical smoke only.
- Contract tests cover schema validity, input preparation, package exclusion and
  fail-closed refusal to promote the scripted fixture.

## Required returned evidence to close T2

An external fresh worker must run the prepared package in a new worker session using
the envelope's package, subject and goal only. A separate evaluator session must then
inspect the returned whole-view/comparison/calibration artifacts without worker
rationale and write an `advance` visual review. The evidence directory must contain:

```text
input_envelope.json
strict_fresh_worker_report.json
mechanical_audit.json
<returned run directory>/session/checkpoint.json
<returned run directory>/session/session.json
<returned run directory>/final/drawing.png
<returned run directory>/compare/subject_vs_final.png
<independent visual review JSON>
```

`verify_strict_fresh_worker.py --evidence-dir <dir>` is the only closure command. No
report boolean, scripted coordinate fixture or same-session visual note substitutes for
the fresh worker and independent evaluator records.

## Current limitation

The repository contains no genuine external worker/evaluator return for this slice.
The prepared `/tmp` candidate is a delivery artifact for that run, not canonical
evidence and not a T2 closure claim. T3 release rebuild remains queued behind this
gate.
