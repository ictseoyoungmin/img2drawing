# S09 context capsule — exemplar ablation

## Public API

- `ModularGrammarCard`: scoped positive/negative grammar transfer with source audit status.
- `AblationTrial`: one A/B/C condition and its structural metrics.
- `ExemplarAblationReport`: validated three-condition report and policy recommendation.
- `run_exemplar_ablation(trials)`: compares A/B/C with deterministic strict-win rules.

## Conditions and metrics

`A_subject_contract`, `B_full_body_exemplar`, and `C_modular_cards` use the same
trial schema. The ordered metrics are `region_blockers`, `reopen_count`,
`residual_discrepancy`, and `p4_structural_errors`. Every trial must set
`p4_tracked=true` and include evidence references.

## Invariants

- Exactly one trial for each A/B/C condition is required.
- Modular cards are adopted only on a strict component-wise win over both other conditions.
- A failed source exemplar cannot be positive; it can remain a negative warning.
- The report authority is structural metrics, never prettiness.
- Full-body exemplar transfer remains unproven unless the ablation closes it.

## Budgets and limitations

The harness is deterministic and JSON-only; it does not perform image inference,
automatic contour extraction, or artistic scoring. P4 tracking is a required
recording invariant, not a substitute for independent visual review.

## Evidence

`dev/evidence/p3-fidelity/S09-exemplar-ablation/` contains the schemas' fixture,
generated report, board, and closure report. Tests are in
`skills/img2drawing/tests/test_exemplar_ablation.py`.

## Reopen conditions

Reopen when a trial omits P4, uses mismatched metric order, admits FAIL cards as
positive transfer, or changes the recommendation rule without a new comparative
fixture.
