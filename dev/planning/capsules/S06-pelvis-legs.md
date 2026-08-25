# Context capsule — S06 Pelvis and Legs Closure

Status: `CLOSED`

Implementation commit: `6dc7d20` (`feat: add lower body envelope evidence`)

## Responsibility

Close the lower-body chain as pelvis breadth/turn, two independent leg envelopes,
support/counterbalance, and inter-leg negative space. Prevent parallel rails from
being mistaken for a faithful lower body.

## Public surface

- `LowerBodyObservation` composes pelvis facts, `leg_A`/`leg_B`
  `RegionEnvelopeObservation` profiles, negative-space stations, and provenance.
- `compare_lower_body()` returns pelvis/leg width deltas, negative-space deltas,
  support/counterbalance and side-role mismatches, plus integrity evidence.
- `LowerBodyIntegrityError` rejects shared artifact/id, lock mismatch, and stale
  drawing state when independent comparison is required.

## Invariants

- Leg profile ids and source/artifact/lock ownership match their lower-body
  parent observation.
- Negative-space stations and leg stations are bounded and ordered.
- Results are `evidence_not_pass_fail`; parallel rails remain a discrepancy, not
  an automatic artistic score.

## Budgets and dependencies

- At most 16 stations per profile and no CV/network/model dependency.
- Canonical implementation is `registration/lower_body.py` with
  `lower_body.schema.json`.

## Evidence

- `dev/evidence/p3-fidelity/S06-lower-body/closure_report.md`
- `dev/evidence/p3-fidelity/S06-lower-body/parallel-rails-fixture.json`
- `dev/evidence/p3-fidelity/S06-lower-body/lower-body-board.svg`
- `skills/img2drawing/tests/test_lower_body.py` (`34 passed` overall suite)

## Limitations and next integration

S06 does not close head/hair or prop topology and does not perform P4 regression
itself. S07 should add head/hair primary-mass evidence while preserving the
lower-body ownership boundary.

## Reopen conditions

Reopen S06 if leg profiles can be swapped without an error, negative-space
collapse is omitted, stale evidence is accepted, or any consumer turns the
comparison into an artistic gate. Otherwise activate S07.
