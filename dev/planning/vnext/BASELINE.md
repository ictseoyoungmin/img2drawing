# R23 legacy baseline

Status: **FROZEN / READ-ONLY**
Pinned revision: `25ec4544e86fe37fc28d64575df145a1b711d63a`
Commit: `feat: harden R23 evidence provenance`
Release line: `0.5.2.dev23 / R23_material_integrated_visual_quality`

## Pin and reproducibility

`25ec454` is the legacy/reference baseline for the vNext reset. The current
working revision is a descendant docs commit (`7789ddd`, `docs: reset img2drawing
workflow around bottleneck vNext`); that does not move or replace the baseline.

Run the read-only check from the repository root:

```bash
python3 dev/planning/vnext/verify_baseline.py
```

The check resolves the abbreviated ref to the exact full SHA, verifies the commit
subject, and verifies that the current revision descends from the pinned object.
Recorded result for this B00 closure: `BASELINE_VERIFICATION_PASS`.

The baseline is not edited, rebuilt in place, or extended as a second production
implementation. A new tag or branch is not required: the full object ID and the
read-only verifier are the pin.

## Baseline role

This baseline preserves the R23 engineering record while vNext is redesigned around
visual correction. R23 artifacts are historical, diagnostic, regression, or
provenance evidence only. They must not be silently promoted to vNext PASS evidence.

| R23 material | B00 role | vNext evidence rule |
|---|---|---|
| `dev/evidence/material-integration/s10-quality-run/` | Canonical R23 positive process/evidence fixture | R23 regression/provenance reference only; direct inspection is not a vNext pass |
| `dev/evidence/material-integration/source_audit.md` negative sources and listed fixtures | False-positive, negative, and regression controls | Preserve their classification; do not import their coordinates or verdicts |
| `dev/evidence/fresh-worker/` | Scripted packaged-worker/mechanical smoke fixture (`G4`) | Not strict fresh-worker or independent visual-approval evidence |
| `dev/p1_reference_run/`, `dev/p2_reference_run/`, `dev/p3_reference_run/` | Stage-specific legacy reference runs | Not vNext inspection or completion evidence |
| Gemini and Claude attachment logs | B00 failure evidence | Dossier inputs only; their R23 outputs are not vNext results |

The existing R23 positive/negative separation remains useful. The separation is a
classification boundary, not permission to reuse R23 images, manifests, coordinates,
or review decisions when vNext validation begins.

## R23 engineering disposition

The implementation and invariant disposition is recorded in
`failure-dossier/r23-architecture.md`. In short:

- Keep explicit strokes, history-preserving edits, pencil-contact rendering,
  checkpoint/resume, replay, timelapse, and state/hash provenance as capabilities.
- Transform stage review into lightweight inspection, stage-oriented local review
  into one unified sheet with focused crops, and stage memory into correction memory.
- Deprecate mandatory P1–P6 runtime advancement, region/resolved-form closure
  manifests, and administrative downstream invalidation from the vNext main path.

These are B00 boundary decisions, not a vNext public API freeze. B01 owns the later
contract and dependency audit.

## Explicit freeze rules

1. `25ec454` remains a read-only legacy baseline.
2. No new review schema, inspection runtime, DrawingSession, or other runtime change
   is part of B00.
3. R23 mechanical PASS, visual review, and scripted fresh-worker evidence cannot be
   auto-inherited by vNext.
4. A vNext PASS requires new evidence produced through the future vNext path and
   bound to that current state; the B00 dossiers do not claim such evidence.

## Source evidence

- Roadmap: `dev/planning/img2drawing-vnext-bottleneck-roadmap.md`, §§1–5.
- R23 assessment: external evidence ID `r23-assessment`, SHA-256
  `614645060e6718f51dae22e4ac146aa61f1a9942dda0be8eaa227b906b7ab91b`, lines 1–100.
- Baseline object: `git show 25ec454`.
- Existing fixture classification: `dev/evidence/material-integration/source_audit.md`,
  `dev/evidence/material-integration/s10_integration_report.md`, and `GATES.md`.
