# S04 — Exemplar mandatory-path cleanup closure evidence

Status: `CLOSED`

Implementation commit: `359afee` (`feat: clean exemplar mandatory review paths`)

## Verification

- `PYTHONPATH=skills/img2drawing/src python3 -m pytest -q skills/img2drawing/tests`
  → `28 passed`.
- Subject-only benchmark smoke → `SUBJECT_ONLY_BENCHMARK_PASS`.
- `py_compile` passed for reference, exemplar sync, review, and run modules.
- `git diff --check` passed.

## Historical gates and current policy

The gates below document the earlier S04 policy. The current subject-only mode
does not require a local representation comparison or any editable answer-image
tree. Runtime metadata is retained only as an internal compatibility resource;
it remains subordinate to the subject contract and cannot donate pose,
coordinates, or proportions.

- FAIL and unproven reference artifacts are warnings, not mandatory positive
  controls.
- packaged reference metadata is validated through the runtime manifest.
- subject-first review packets remain available without a reference comparison
  board.

## Evidence locations

- `skills/img2drawing/tests/test_exemplar_policy.py`
- `skills/img2drawing/tests/test_packaged_reference_policy.py`
- `skills/img2drawing/src/img2drawing/reference/loader.py`
