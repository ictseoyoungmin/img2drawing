# Context capsule — S05 Torso Orientation Closure

Status: `CLOSED`

Implementation commit: `f2163e9` (`feat: add torso orientation evidence`)

## Responsibility

Keep body view, torso turn, near-side role, and near/far arm exposure explicit so
torso width alone cannot hide a side/three-quarter interpretation error.

## Public surface

- `TorsoOrientationObservation` records independent normalized shoulder and torso
  envelope facts plus arm exposure and provenance.
- `compare_torso_orientation()` returns view/turn/near-side mismatches, shoulder
  and torso size deltas, arm exposure deltas, and integrity evidence.
- `TorsoOrientationIntegrityError` rejects same artifact/id, lock mismatch, and
  stale drawing state when independent comparison is required.

## Invariants

- Reference and drawing observations have distinct ids/artifacts and share the
  S01 frozen observation digest.
- Drawing evidence carries a state digest and cannot be compared as current
  when the supplied drawing cursor hash differs.
- A similar torso width does not erase orientation or near-arm exposure drift.
- Results are `evidence_not_pass_fail`; no artistic decision is emitted.

## Budgets and dependencies

- Comparison is constant-size linear arithmetic with no CV, network, or model
  dependency.
- Canonical implementation is `registration/orientation.py` with
  `torso_orientation.schema.json`.

## Evidence

- `dev/evidence/p3-fidelity/S05-torso-orientation/closure_report.md`
- `dev/evidence/p3-fidelity/S05-torso-orientation/near-arm-orientation-fixture.json`
- `dev/evidence/p3-fidelity/S05-torso-orientation/torso-orientation-board.svg`
- `skills/img2drawing/tests/test_orientation.py` (`31 passed` overall suite)

## Limitations and next integration

This slice does not close pelvis, legs, head, or prop topology and does not
automatically infer a view. S06 should add lower-body profiles without merging
their ownership into torso/arm evidence.

## Reopen conditions

Reopen S05 if a consumer uses torso width as a proxy for orientation, drops arm
exposure, bypasses provenance/staleness checks, or turns evidence into an
artistic gate. Otherwise activate S06.
