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
B and C are generic near-duplicates, with no visible C-over-B gain. Therefore
the ablation is complete as an experiment but does not close the fidelity gate.

## Evidence

- `blind_visual_report.md`
- `mechanical_ablation_report.md`
- `residual_gate.json`
- `dev/dogfood/s1s9/croquis_run/reviews/P3_primary_masses/pass_02/region_closure_manifest.json`
- `dev/dogfood/s1s9/croquis_run/reviews/P3_primary_masses/pass_02/visual_fidelity_review.json`
- `dev/evidence/p3-fidelity/S09-exemplar-ablation/ablation_report.json` (fixture only)
- `ablation_comparison.md`
- `blind_ablation_report.md`
- `real_ablation_report.json`

Mechanical smoke also passes for all three isolated runs with strict JSON audit
artifacts under each `croquis_run/mechanical_audit.json`; all three audits retain
the required `semantic_visual_audit_required=true` warning. This is why the blind
comparison, not the per-run `ADVANCE`, controls the S10 decision.

## Verification run

- `PYTHONPATH=skills/img2drawing/src python3 skills/img2drawing/tools/audit_fresh_worker.py --run-dir dev/dogfood/s1s9/croquis_run --write-json dev/dogfood/s1s9/croquis_run/mechanical_audit.json`
- strict `json.loads()` of the regenerated mechanical artifact: PASS
- `PYTHONPATH=src pytest -q` from `skills/img2drawing/`: **47 passed**
- `git diff --check`: PASS
