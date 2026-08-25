# S03 — Blind visual fidelity and P3 dual-gate closure evidence

Status: `CLOSED`

Implementation commit: `26a222d` (`feat: add P3 blind fidelity dual gate`)

## Scope

S03 separates process review from subject-fidelity review. P3 now requires an
eight-region closure manifest and an independent visual review in addition to
the existing process review. The runtime remains the lifecycle owner and keeps
non-P3 progression unchanged.

## Verification

- `PYTHONPATH=skills/img2drawing/src python3 -m pytest -q skills/img2drawing/tests`
  → `22 passed`.
- Subject-only benchmark smoke → `SUBJECT_ONLY_BENCHMARK_PASS`.
- `py_compile` passed for fidelity, review, run, and public export modules.
- `python3 -m json.tool` passed for region closure, visual review, and blind
  packet schemas.
- `git diff --check` passed.

## Gates covered

- blind packet contains frozen observation, stage contract, current drawing, and
  region refs without worker rationale or exemplar verdict;
- exactly eight P3 regions require fresh subject finding, fresh drawing finding,
  independent evidence refs, and a closure decision;
- blockers, `revise`, missing/stale records, lock mismatch, and artifact drift
  fail closed before visual or P3 advance;
- `accept-with-rationale` requires uncertainty or occlusion basis;
- visual/process records bind to the same drawing state, artifact, cursor, and
  frozen observation lock digest;
- checkpoint v3 and review manifest v9 preserve visual records and blind packet;
- a non-P3 P1 advance remains available without the visual gate.

## Boundary

The visual record is an independent closure artifact, not an automated art
score. S03 does not decide whether the measured subject is aesthetically good;
it only prevents an unreviewed or stale P3 branch from advancing.
