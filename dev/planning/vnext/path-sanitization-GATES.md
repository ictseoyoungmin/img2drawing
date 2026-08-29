# Repository Path Sanitization Gates

Scope: remove machine-local filesystem paths from repository text and preserve the
meaning of historical evidence with repository-relative or external-source IDs.

This cleanup is documentation/tooling hygiene only. It does not activate another
bottleneck or change runtime behavior.

- [x] G1 — no machine-local absolute paths remain in repository text
  - Check: `python3 dev/tools/verify_repository_paths.py`
  - Expected: `REPOSITORY_PATH_SANITIZATION_PASS`
  - Evidence: `REPOSITORY_PATH_SANITIZATION_PASS`; an additional no-ignore text-extension scan found zero machine-root, Windows-drive, or attachment-log path matches.
- [x] G2 — JSON artifacts remain parseable after path normalization
  - Check: `python3 dev/tools/verify_repository_paths.py --json`
  - Expected: `REPOSITORY_JSON_PARSE_PASS`
  - Evidence: `REPOSITORY_PATH_SANITIZATION_PASS`; `REPOSITORY_JSON_PARSE_PASS`.
- [x] G3 — Python sources remain syntactically valid
  - Check: `python3 dev/tools/verify_repository_paths.py --python`
  - Expected: `REPOSITORY_PYTHON_COMPILE_PASS`
  - Evidence: `REPOSITORY_PATH_SANITIZATION_PASS`; `REPOSITORY_PYTHON_COMPILE_PASS`.
- [x] G4 — targeted repository tests pass
  - Check: `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONPATH=skills/img2drawing/src python3 -m pytest -q dev/tests/test_public_paths.py`
  - Expected: `3 passed`
  - Evidence: `3 passed in 7.89s`.
