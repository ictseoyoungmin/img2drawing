# S01 — Pre-draw observation lock closure evidence

Status: `CLOSED`

Implementation commit: `9b24ee4` (`feat: add pre-draw observation lock`)

## Scope

S01 binds the existing agent-authored `ObservationContract` to a typed,
immutable `ViewObservation` and a provenance-bearing `FrozenObservationRecord`.
`DrawingRun` now owns lock, checkpoint/resume, and explicit observation reopen
lifecycle. Region envelope measurement and visual-fidelity decisions remain
outside this slice.

## Verification

- `PYTHONPATH=skills/img2drawing/src python3 -m pytest -q skills/img2drawing/tests`
  → `11 passed`.
- Subject-only benchmark smoke
  (`skills/img2drawing/benchmarks/stage_reconstruction/full_body_croquis_subject_only/run_smoke.py`)
  → `SUBJECT_ONLY_BENCHMARK_PASS`.
- `py_compile` passed for the changed runtime, observation, example, and smoke
  modules.
- `python3 -m json.tool` passed for observation, lock, and reopen schemas.
- `git diff --check` passed.

## Gates covered

- typed body view, torso turn, near-side role, both-arm visibility/occlusion,
  prop overlap, and uncertainty fields;
- subject SHA-256 and observation digest binding;
- fail-closed `stage_start`/draw without a lock;
- immutable nested observation clone and checkpoint/resume round trip;
- duplicate lock, malformed view, missing arm fields, digest mismatch, and
  tampered/stale checkpoint rejection;
- pre-draw replacement audit and post-draw P1 reopen/invalidation;
- legacy v1 checkpoint read plus explicit P1 adoption path;
- lock JSON size assertion at 64 KiB and no CV/network dependency.

## Evidence locations

- `skills/img2drawing/tests/test_observation_lock.py`
- `skills/img2drawing/benchmarks/stage_reconstruction/full_body_croquis_subject_only/run_smoke.py`
- `skills/img2drawing/schemas/observation_lock.schema.json`
- `skills/img2drawing/schemas/observation_reopen.schema.json`
- `skills/img2drawing/src/img2drawing/observation/lock.py`
