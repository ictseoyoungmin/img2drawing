# S04 — Exemplar mandatory-path cleanup closure evidence

Status: `CLOSED`

Implementation commit: `359afee` (`feat: clean exemplar mandatory review paths`)

## Verification

- `PYTHONPATH=skills/img2drawing/src python3 -m pytest -q skills/img2drawing/tests`
  → `28 passed`.
- Subject-only benchmark smoke → `SUBJECT_ONLY_BENCHMARK_PASS`.
- `py_compile` passed for reference, exemplar sync, review, and run modules.
- `git diff --check` passed.

## Gates covered

- P1/P4/P5 FAIL exemplars omit `grammar_vs_drawing` from mandatory views and
  emit only a negative/reference warning.
- P2 PASS exemplar remains the mandatory positive control.
- P3 PASS exemplar is explicitly `unproven_until_ablation` in worker packet and
  audit artifact, so it is not silently treated as validated positive grammar.
- top-level `skills/img2drawing/exemplars/full_body_croquis/` is declared the
  authoring owner; packaged bytes are checked as a derived copy.
- packaged hash drift and missing-file drift are rejected by
  `assert_exemplar_trees_synced()`.
- FAIL exemplar paths still produce subject-first review packets without
  creating a mandatory grammar comparison board.

## Evidence locations

- `skills/img2drawing/tests/test_exemplar_policy.py`
- `skills/img2drawing/tests/test_exemplar_sync.py`
- `skills/img2drawing/exemplars/AUTHORING_OWNER.md`
- `skills/img2drawing/src/img2drawing/exemplar/sync.py`
