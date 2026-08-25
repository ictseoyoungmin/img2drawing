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
- The default subject-only workflow has no editable authoring owner. Runtime
  reference metadata is validated through its manifest and remains subordinate
  to subject geometry.

## Invariants

- FAIL exemplar is never a mandatory positive comparison.
- The former P2/P3 positive-control labels are historical; subject-only mode
  does not require a local reference comparison.
- Subject-first review packet generation remains available without a FAIL
  grammar board.
- Missing or malformed runtime reference metadata fails reference-bundle
  construction; it never becomes pose or coordinate authority.

## Budgets and dependencies

- Hash comparison is linear in the fixed exemplar file set and uses no network,
  CV, or inference dependency.
- No local answer-image tree is part of the worker input. Package data is an
  internal compatibility resource, not a source for subject geometry.

## Evidence

- `dev/evidence/p3-fidelity/S04-exemplar-policy/closure_report.md`
- `skills/img2drawing/tests/test_exemplar_policy.py`
- `skills/img2drawing/tests/test_packaged_reference_policy.py`

## Limitations and next integration

S04 does not prove that P2 or any other exemplar transfers well to this subject;
it only makes that uncertainty explicit. S09 must run the A/B/C ablation through
P4 before changing the positive-control policy.

## Reopen conditions

Reopen S04 if a FAIL exemplar re-enters mandatory `grammar_vs_drawing`, P3 loses
its unproven label, packaged bytes drift without an error, or a consumer treats
the derived tree as authoring source. Otherwise activate S05 for torso/arm
orientation evidence.
