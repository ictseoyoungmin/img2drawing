# S08 — Generic prop topology closure evidence

Status: `CLOSED`

Implementation commit: `efc487e` (`feat: add generic prop topology evidence`)

## Verification

- `PYTHONPATH=skills/img2drawing/src python3 -m pytest -q skills/img2drawing/tests`
  → `41 passed`.
- Subject-only benchmark smoke → `SUBJECT_ONLY_BENCHMARK_PASS`.
- `py_compile` passed for prop topology and public registration exports.
- `python3 -m json.tool` passed for `prop_topology.schema.json`.
- `git diff --check` passed.

## Gates covered

- generic major axis, width-change points, terminal masses, body overlap points,
  visible interruptions, and occlusion order;
- rifle and guitar fixtures using the same schema/API;
- gross axis match with width-transition and overlap drift;
- distinct provenance, shared lock digest, stale drawing rejection, round-trip
  schema validation, and evidence-only authority;
- human-readable topology board without rifle-specific ownership.

## Boundary

S08 supplies attached-object evidence but does not decide P3 closure or infer
prop semantics. It deliberately leaves artistic acceptance to the visual review
and keeps the existing P5 attached-object process owner intact.
