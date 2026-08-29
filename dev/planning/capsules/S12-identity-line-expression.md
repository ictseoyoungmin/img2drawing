# S12 capsule — optional P6 identity and line expression

- Responsibility: optional bounded identity finish after P1–P5 closure: face
  relations, grouped hair, sparse garment marks, and selective accents.
- API: `full_body_croquis_with_p6`, `IdentityFinishProfile`,
  `CalibrationSheet`, `IdentityPreflightResult`, `IdentityFinishManifest`.
- Budgets: 48 identity strokes, 12 confirmations, 8 folds, and 25% maximum
  accent fraction by default; calibration uses rendered actual-size and 50% PNG
  samples from the real output canvas.
- Invariants: preflight fails closed on upstream blockers; per-point pressure and
  taper stay in action/history; P6 cannot mutate P1–P5-owned strokes; manifest
  counts and artifact digests match runtime observations.
- Evidence: `identity/calibration_sheet.json`, `identity/calibration_sheet.png`,
  `identity/calibration_sheet_50pct.png`, identity manifest and
  `dev/tests/test_resolved_form.py`.
- Limitation: P6 does not guarantee pixel-level likeness and remains optional.
- Reopen: upstream visual blocker, blanket confirmation, broad value band, or
  face/hair relation that collapses into one envelope.
