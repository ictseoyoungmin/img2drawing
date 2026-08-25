# S10 integration report

Status: **ACTIVE / REVISE — not closed**

S10 successfully cross-checked the S01–S09 lifecycle artifacts against a fresh
independent semantic review. Mechanical digest bindings are coherent, but the
semantic gate was a false positive: P3 recorded eight closed regions while the
blind reviewer found five rendered-image blockers. The discrepancy is explained
by agent-authored geometry records and an inline evaluator, not by a stale
checkpoint.

The current result therefore proves process integrity and recovery behavior, not
professional-level subject likeness. The next production action is an evidence-
backed P1/P2/P3 reopen and a real subject A/B/C ablation. S10 must remain the one
active bottleneck slice until those conditions are executed and both mechanical
and visual artifacts can close on the same state/lock digest.

The real subject A/B/C ablation is now executed under `drawings/s10-ablation/`.
The independent image-only comparison finds A strongest but still schematic;
B and the original C are generic near-duplicates. The first comparison was
confounded by unequal identity-detail budgets (A: 82 identity-role actions;
B/C: 22 each), so it is retained as diagnosis, not a causal estimate. Bn/Cn
were then rerun with exactly 82 identity-role actions and the same requested
final-detail inventory. Their raster similarity is informative as a baseline,
but the Cn runner serialized cards only in metadata and did not bind them to
the `DrawingRun` action path; therefore the normalized image comparison cannot
estimate a modular-card effect.

The corrected C bound-v2 run proves strict runtime provenance instead: all 166
authored draw/replace actions carry a stage card, all nine worker packets carry
their current card, and checkpoint/session/review-manifest artifacts persist the
binding contract. A second card-driven C run now explicitly consumes every
stage card's `transfer_mapping` in the stroke plan. Its 166 authored point
arrays are identical to bound-v2 (geometry mutation remains forbidden), while
line-material changes produce a new final SHA
`80534c5043c3257dbd00f5183c563f545a22b1a98b280b177c40631e4c5b2788`.
This proves card consumption and a measurable raster effect, but not a
subject-fidelity gain. S10 remains `REVISE`: the next experiment must replay B
with the matched budget and run an independent blind B-versus-card-driven-C
comparison.

## Evidence

- `blind_visual_report.md`
- `mechanical_ablation_report.md`
- `residual_gate.json`
- `dev/dogfood/s1s9/croquis_run/reviews/P3_primary_masses/pass_02/region_closure_manifest.json`
- `dev/dogfood/s1s9/croquis_run/reviews/P3_primary_masses/pass_02/visual_fidelity_review.json`
- `dev/evidence/p3-fidelity/S09-exemplar-ablation/ablation_report.json` (fixture only)
- `ablation_comparison.md`
- `blind_ablation_report.md`
- `blind_normalized_ablation_report.md`
- `real_ablation_report.json`
- `drawings/s10-ablation/C_modular_grammar_cards_bound_v2/` (strict binding dogfood)
- `card_driven_stroke_plan_report.json`
- `drawings/s10-ablation/C_modular_grammar_cards_card_driven/` (card consumption dogfood)

Mechanical smoke also passes for all three isolated runs with strict JSON audit
artifacts under each `croquis_run/mechanical_audit.json`; all three audits retain
the required `semantic_visual_audit_required=true` warning. This is why the blind
comparison, not the per-run `ADVANCE`, controls the S10 decision.

## Verification run

- `PYTHONPATH=skills/img2drawing/src python3 skills/img2drawing/tools/audit_fresh_worker.py --run-dir dev/dogfood/s1s9/croquis_run --write-json dev/dogfood/s1s9/croquis_run/mechanical_audit.json`
- strict `json.loads()` of the regenerated mechanical artifact: PASS
- `PYTHONPATH=src pytest -q` from `skills/img2drawing/`: **52 passed**
- `git diff --check`: PASS
