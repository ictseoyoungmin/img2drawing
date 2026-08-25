# S07 — Head and hair closure evidence

Status: `CLOSED`

Implementation commit: `c433c3a` (`feat: add head and hair envelope evidence`)

## Verification

- `PYTHONPATH=skills/img2drawing/src python3 -m pytest -q skills/img2drawing/tests`
  → `37 passed`.
- Subject-only benchmark smoke → `SUBJECT_ONLY_BENCHMARK_PASS`.
- `py_compile` passed for head/hair and public registration exports.
- `python3 -m json.tool` passed for `head_hair.schema.json`.
- `git diff --check` passed.

## Gates covered

- head top/chin, cranial and jaw contour pairs, head bounds, hair envelope,
  style, occlusion, and anatomical uncertainty;
- overlarge spherical head and helmet-like bob fixture without face features;
- independent provenance, lock binding, stale drawing rejection, round-trip
  schema validation, and evidence-only authority;
- human-readable head/hair visual board.

## Boundary

S07 closes primary head/hair mass evidence only. It does not infer or draw eyes,
nose, mouth, or later identity details; those details must follow a faithful head
mass rather than hide a primary-mass error.
