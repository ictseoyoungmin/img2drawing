# S06 — Pelvis and legs closure evidence

Status: `CLOSED`

Implementation commit: `6dc7d20` (`feat: add lower body envelope evidence`)

## Verification

- `PYTHONPATH=skills/img2drawing/src python3 -m pytest -q skills/img2drawing/tests`
  → `34 passed`.
- Subject-only benchmark smoke → `SUBJECT_ONLY_BENCHMARK_PASS`.
- `py_compile` passed for lower-body and public registration exports.
- `python3 -m json.tool` passed for `lower_body.schema.json`.
- `git diff --check` passed.

## Gates covered

- pelvis bounds/turn, leg_A/leg_B station envelopes, side roles, support leg,
  counterbalance direction, and inter-leg negative-space stations;
- parallel-rail fixture exposing taper and negative-space collapse;
- side-role swap, distinct artifact/observation provenance, shared lock digest,
  and stale drawing-state rejection;
- evidence-only authority and bounded station comparison;
- human-readable lower-body board plus round-trip schema test.

## Boundary

S06 records lower-body geometry but does not gate P3 or infer anatomy. A future
P4 regression harness can reuse the profile to verify that taper and negative
space survive structural-connection work.
