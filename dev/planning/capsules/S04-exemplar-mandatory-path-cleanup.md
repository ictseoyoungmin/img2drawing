# Context capsule — S04 Exemplar Mandatory-Path Cleanup

Status: `CLOSED`

Implementation commit: `359afee` (`feat: clean exemplar mandatory review paths`)

## Responsibility

Prevent known-bad or unproven exemplars from becoming positive grammar answers
through mandatory review artifacts. Keep subject geometry and frozen StageContract
as the authority while exposing only an explicit warning for FAIL examples.

## Public surface

- `GrammarExemplar.mandatory_path_policy` is derived as
  `negative_reference_warning_only`, `unproven_until_ablation`, or
  `mandatory_positive_reference`.
- `ReferenceReviewArtifacts` omits `grammar_vs_drawing` for FAIL exemplars and
  records the policy/warning in its serialized artifact.
- `build_worker_packet()` changes mandatory review views by policy: warning for
  FAIL/P3-unproven, grammar comparison only for positive controls.
- `compare_exemplar_trees()` and `assert_exemplar_trees_synced()` validate the
  top-level authoring owner against packaged derived bytes.

## Invariants

- FAIL exemplar is never a mandatory positive comparison.
- P2 is the only current positive control; P3 remains unproven pending ablation.
- Subject-first review packet generation remains available without a FAIL
  grammar board.
- Hash drift or missing files in either exemplar tree fail the sync assertion.

## Budgets and dependencies

- Hash comparison is linear in the fixed exemplar file set and uses no network,
  CV, or inference dependency.
- Canonical authoring owner is `skills/img2drawing/exemplars/full_body_croquis/`;
  package data is derived, not hand-edited.

## Evidence

- `dev/evidence/p3-fidelity/S04-exemplar-policy/closure_report.md`
- `skills/img2drawing/tests/test_exemplar_policy.py`
- `skills/img2drawing/tests/test_exemplar_sync.py` (`28 passed` overall suite)

## Limitations and next integration

S04 does not prove that P2 or any other exemplar transfers well to this subject;
it only makes that uncertainty explicit. S09 must run the A/B/C ablation through
P4 before changing the positive-control policy.

## Reopen conditions

Reopen S04 if a FAIL exemplar re-enters mandatory `grammar_vs_drawing`, P3 loses
its unproven label, packaged bytes drift without an error, or a consumer treats
the derived tree as authoring source. Otherwise activate S05 for torso/arm
orientation evidence.
