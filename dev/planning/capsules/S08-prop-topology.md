# Context capsule — S08 Generic Prop Topology

Status: `CLOSED`

Implementation commit: `efc487e` (`feat: add generic prop topology evidence`)

## Responsibility

Represent attached objects by topology relationships rather than rifle-specific
labels, so a plausible gross axis cannot hide wrong width transitions, terminal
masses, or body overlap.

## Public surface

- `PropTopologyObservation` stores a major axis, width-change points, terminal
  masses, body-overlap points, visible interruptions, occlusion order, and
  provenance.
- `compare_prop_topology()` returns axis/width/mass/overlap/occlusion evidence.
- `PropTopologyIntegrityError` rejects mismatched prop ids, provenance drift,
  lock mismatch, and stale drawing state.

## Invariants

- Rifle and non-rifle objects use the same fields and API.
- Width-change points are ordered and bounded to 16 entries.
- Results are `evidence_not_pass_fail`; topology evidence never auto-advances a
  stage.

## Budgets and dependencies

- Fixed-size topology comparison with no CV/network/model dependency.
- Canonical implementation is `registration/prop_topology.py` with
  `prop_topology.schema.json`.

## Evidence

- `dev/evidence/p3-fidelity/S08-prop-topology/closure_report.md`
- `dev/evidence/p3-fidelity/S08-prop-topology/prop-topology-fixtures.json`
- `dev/evidence/p3-fidelity/S08-prop-topology/prop-topology-board.svg`
- `skills/img2drawing/tests/test_prop_topology.py` (`41 passed` overall suite)

## Limitations and next integration

S08 does not alter the existing P5 process owner and does not decide whether a
prop is artistically convincing. S09 must evaluate exemplar transfer and record
whether modular cards reduce residual structural errors through P4.

## Reopen conditions

Reopen S08 if a consumer introduces rifle-only topology fields, accepts gross-axis
only evidence, bypasses provenance/staleness checks, or turns topology into an
artistic gate. Otherwise activate S09.
