# S15 capsule — release and CI closure

- Responsibility: publish one R23 identity containing current source, schemas,
  evidence contracts and packaged smoke checks.
- Outputs: `dev/release/r23/` manifest, ZIP/tree artifacts, checksums, report and
  validator; CI runs tests, schema and portability checks.
- Invariants: version/revision/README/changelog/manifest agree; no stale
  checkout paths; image quality is never reduced to one numeric gate.
- Evidence: `dev/release/validate_r23_release.py` and CI workflow.
- Limitation: package smoke does not replace direct visual inspection.
- Reopen: artifact hash drift, stale release identity, failed clean import, or
  canonical distributable retaining superseded R21/R22 references.
