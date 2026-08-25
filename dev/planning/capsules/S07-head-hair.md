# Context capsule — S07 Head and Hair Closure

Status: `CLOSED`

Implementation commit: `c433c3a` (`feat: add head and hair envelope evidence`)

## Responsibility

Close head and hair primary-mass fidelity before feature detail, exposing an
overlarge spherical head or helmet-like bob envelope independently of eyes,
nose, or mouth.

## Public surface

- `HeadHairObservation` records head top/chin, cranial/jaw contours, head/hair
  bounds, hair style/occlusion, uncertainty, and provenance.
- `compare_head_hair()` returns head/hair size deltas, contour asymmetry, style
  and occlusion changes, and integrity evidence.
- `HeadHairIntegrityError` rejects shared artifacts/ids, lock mismatch, and
  stale drawing state.

## Invariants

- Feature detail is not required for primary head/hair evidence.
- Results are `evidence_not_pass_fail`; no artistic score is emitted.
- Drawing evidence is state-bound and independent from subject evidence.

## Budgets and dependencies

- Fixed-size point/bounds comparison with no CV/network/model dependency.
- Canonical implementation is `registration/head_hair.py` with
  `head_hair.schema.json`.

## Evidence

- `dev/evidence/p3-fidelity/S07-head-hair/closure_report.md`
- `dev/evidence/p3-fidelity/S07-head-hair/bob-head-fixture.json`
- `dev/evidence/p3-fidelity/S07-head-hair/head-hair-board.svg`
- `skills/img2drawing/tests/test_head_hair.py` (`37 passed` overall suite)

## Limitations and next integration

S07 does not close attached-object topology or produce identity feature strokes.
S08 should generalize prop topology across rifle and non-rifle objects without
creating a second owner for attached-object closure.

## Reopen conditions

Reopen S07 if a consumer hides head/hair mass drift behind face detail, drops hair
occlusion/uncertainty, accepts stale evidence, or turns the comparison into an
artistic gate. Otherwise activate S08.
