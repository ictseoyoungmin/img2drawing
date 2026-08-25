# S05 — Torso orientation closure evidence

Status: `CLOSED`

Implementation commit: `f2163e9` (`feat: add torso orientation evidence`)

## Verification

- `PYTHONPATH=skills/img2drawing/src python3 -m pytest -q skills/img2drawing/tests`
  → `31 passed`.
- Subject-only benchmark smoke → `SUBJECT_ONLY_BENCHMARK_PASS`.
- `py_compile` passed for orientation and public registration exports.
- `python3 -m json.tool` passed for `torso_orientation.schema.json`.
- `git diff --check` passed.

## Gates covered

- independent body-view, torso-turn, near-side, shoulder, torso bounds, and
  near/far arm exposure evidence;
- side versus back-three-quarter mismatch is surfaced even when torso width is
  unchanged;
- distinct observation/artifact provenance, shared S01 lock digest, and stale
  drawing-state rejection;
- evidence-only authority with no artistic PASS/FAIL decision;
- dogfood fixture and SVG board for the thin near-arm/depth-dominance failure;
- linear comparison budget smoke.

## Boundary

S05 records and compares evaluator-authored orientation semantics; it does not
infer pose or replace S02 contour measurements. S06 can consume this evidence
for pelvis/leg closure while keeping torso and arm contour ownership explicit.
