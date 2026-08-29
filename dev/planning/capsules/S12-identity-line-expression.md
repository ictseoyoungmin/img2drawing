# S12 capsule — optional P6 identity and line expression

- Responsibility: optional bounded identity finish after P1–P5 closure: face
  relations, grouped hair, sparse garment marks, and selective accents.
- API: `full_body_croquis_with_p6`, `IdentityFinishProfile`,
  `CalibrationSheet`, `IdentityPreflightResult`, `IdentityFinishManifest`.
- Budgets: 48 identity strokes, 12 confirmations, 8 folds, and 25% maximum
  accent fraction by default; calibration uses real output canvas pressure samples.
- Invariants: preflight fails closed on upstream blockers; per-point pressure and
  taper stay in action/history; P6 cannot substitute for P1–P5 correction.
- Evidence: `identity/calibration_sheet.json`, identity manifest and
  `dev/tests/test_resolved_form.py`.
- Limitation: P6 does not guarantee pixel-level likeness and remains optional.
- Reopen: upstream visual blocker, blanket confirmation, broad value band, or
  face/hair relation that collapses into one envelope.
