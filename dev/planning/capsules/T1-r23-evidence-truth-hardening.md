# T1 capsule — R23 evidence–execution truth hardening

- Responsibility: ensure lifecycle, P5 retirement, P6 budgets, calibration
  artifacts and reviewed PNG hashes describe actual runtime actions and files.
- Public API: `DrawingRun.stage_start`, `DrawingRun.identity_finish_counts`,
  `CalibrationSheet.render_artifacts`, `submit_identity_finish_manifest`.
- Authority: `DrawingRun` history/current IR and prepared review artifact; caller
  manifests are claims that must match those authorities.
- Invariants: stage operations require an explicit `started_cursor`; P6 cannot
  mutate P1–P5-owned strokes; retirement IDs exist and have actual P5 erase/lift
  actions; P6 count fields match the action slice; calibration JSON binds actual
  and 50%-scale PNG SHA-256/dimensions; P6 artifact hash matches the prepared PNG.
- Evidence: `dev/tests/test_resolved_form.py`,
  `dev/tools/build_material_quality_run.py`,
  `dev/evidence/material-integration/s10-quality-run/quality_run_report.json`,
  `dev/tools/verify_bottleneck_completion.py --check s10`.
- Verification: full development suite passes; S10, S11/S12 and scripted S14
  mechanical checks pass; canonical S10 records `P6_identity_finish` discovery
  followed by `P5_clean_blockin` reopen and fresh P5 review.
- Limitation: scripted S14 is portability smoke only; strict packaged fresh-worker
  provenance and independent whole-view visual approval remain open in T2/T3.
- Reopen: any forged/missing digest, fabricated ID/count, missing stage start,
  P6 upstream mutation, calibration artifact drift, or direct visual inspection
  finding that materially lowers the target quality.
