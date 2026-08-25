# S09 closure report — modular grammar cards and A/B/C ablation

Status: `CLOSED`

S09 adds a single, schema-backed ablation harness for the three transfer conditions:

- `A_subject_contract`: subject and stage contract only
- `B_full_body_exemplar`: subject, contract, and the existing full-body exemplar
- `C_modular_cards`: subject, contract, and scoped modular grammar cards

The harness requires every trial to carry the same four structural metrics and to
be tracked through P4: region blocker count, reopen count, residual discrepancy,
and P4 structural error count. It has no prettiness or aesthetic score authority.
`C_modular_cards` is recommended only when it strictly improves every ordered
metric over both A and B; otherwise transfer remains unproven or the subject-only
contract is retained. A failed exemplar cannot be encoded as a positive card.

## Evidence

- API and invariants: `skills/img2drawing/src/img2drawing/exemplar/ablation.py`
- Schemas: `skills/img2drawing/schemas/exemplar_ablation.schema.json`,
  `skills/img2drawing/schemas/modular_grammar_card.schema.json`
- Tests: `skills/img2drawing/tests/test_exemplar_ablation.py`
- Fixture: `ablation_fixture.json`
- Generated report: `ablation_report.json`
- Comparison board: `ablation-board.svg`

The fixture records a strict structural win for C (2/1/0.20/1) over A
(4/3/0.40/3) and B (5/4/0.55/4). This is a policy fixture for the harness, not
a claim that an exemplar makes a drawing visually better in general.

## Verification

- `45 passed` in the project test suite.
- Subject-only benchmark smoke: `SUBJECT_ONLY_BENCHMARK_PASS`.
- Changed Python modules compile successfully.
- New JSON artifacts validate against their schemas.
- `git diff --check` passes.

## Reopen conditions

Reopen S09 if a future ablation allows a failed exemplar to enter a positive
card, compares unequal metric sets, omits P4 tracking, or recommends transfer on
prettiness alone.
