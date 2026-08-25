# Context capsule — S01 Pre-draw Observation Lock

Status: `CLOSED`

Implementation commit: `9b24ee4` (`feat: add pre-draw observation lock`)

## Responsibility

Freeze the agent-authored subject observation before drawing and make its
semantic basis authoritative across `DrawingRun` stage progression,
checkpoint/resume, and explicit correction/reopen. S01 does not measure region
silhouettes, decide visual fidelity, or alter exemplar policy.

## Public surface

- `ObservationContract` remains the semantic content owner.
- `ViewObservation` supplies typed body view, torso turn, near-side role, both-arm
  visibility/occlusion, prop overlap order, and uncertainty notes.
- `FrozenObservationRecord.create()/to_dict()/from_dict()` binds the observation
  to the subject SHA-256 and an observation digest.
- `DrawingRun.lock_observation(observation)` is required before `stage_start()`
  or drawing.
- `DrawingRun.reopen_observation(reason=..., replacement=...)` records an
  observation replacement; after drawing starts it reopens P1 and invalidates
  the downstream branch.
- `ObservationReopenRecord` stores replacement provenance and invalidated
  stages.

## Inputs and outputs

Inputs are an existing subject reference and an agent-authored
`ObservationContract` with a complete typed view. Outputs are:

- `output/observation/pre_draw_observation.json`;
- `output/observation/observation_reopens.json` when replacements occur;
- checkpoint v2 fields `observation_lock` and `observation_reopens`;
- review/session metadata carrying the same lock digest and replacement audit.

## Invariants

- A new run fails closed if P1 is started or a draw is attempted without a lock.
- The lock contains a valid subject SHA-256, schema version, observation id, and
  digest; nested input mappings are cloned and immutable after locking.
- Both `subject_left` and `subject_right` arm visibility and occlusion entries
  are required for a frozen view.
- A duplicate lock is rejected; a changed observation must use explicit reopen.
- Replacement after drawing starts must reopen P1 before a new drawing branch is
  accepted. Legacy v1 checkpoints are readable but require explicit P1 reopen and
  lock adoption before continuing.
- Checkpoint tampering or a stale digest is rejected during resume.

## Budgets and dependencies

- General full-body lock JSON is asserted to remain at or below 64 KiB.
- No network, model inference, or new CV dependency is used; this slice uses
  existing Python/Pillow runtime primitives and agent-authored facts.
- There is one canonical observation-lock implementation under
  `src/img2drawing/observation/lock.py`; no parallel `observation_v2/new/final`
  path exists.

## Evidence

- `dev/evidence/p3-fidelity/S01-observation-lock/closure_report.md`
- `skills/img2drawing/tests/test_observation_lock.py` (`11 passed`)
- subject-only benchmark smoke (`SUBJECT_ONLY_BENCHMARK_PASS`)
- observation, lock, and reopen schema validation; `py_compile`; `git diff --check`

## Limitations and next integration

S01 records view semantics but does not prove that an arm, head, torso, or prop
silhouette matches the subject. S02 must consume the lock digest and add region
envelope evidence, starting with the near-arm upper/mid/lower width profile.
S03 can then bind independent visual-fidelity review and the P3 dual gate to
this lifecycle. Do not treat a lock as a visual PASS.

## Reopen conditions

Reopen S01 if lock provenance is bypassed, checkpoint v2 cannot round-trip a
record, legacy adoption becomes implicit, or a new consumer mutates observation
content without a replacement audit. Otherwise activate S02 only after this
capsule and closure evidence have been reviewed.
