# Gates: img2drawing bottleneck completion

OWNS: README.md, skills/img2drawing/**, dev/tools/**, dev/tests/**, dev/schemas/**, dev/evidence/**, dev/planning/**, dev/release/**, .github/**

Scope: complete the material-derived visual-quality bottleneck slices and leave one portable, tested release candidate.

- [x] G1: semantic residual review is bound to the current subject, drawing state, and observation lock
  CHECK: PYTHONPATH=skills/img2drawing/src python3 dev/tools/verify_bottleneck_completion.py --check s10
  EXPECT: S10_VERIFICATION_PASS
  EVIDENCE: dev/evidence/material-integration/s10_residual_gate.json; S10_VERIFICATION_PASS

- [x] G2: resolved-form P4/P5 review and selective P6 contracts are executable and round-trip safe
  CHECK: PYTHONPATH=skills/img2drawing/src python3 dev/tools/verify_bottleneck_completion.py --check s11-s12
  EXPECT: S11_S12_VERIFICATION_PASS
  EVIDENCE: dev/tests/test_resolved_form.py; S11_S12_VERIFICATION_PASS

- [x] G3: selective R23 compatibility decisions pass the complete development test suite
  CHECK: PYTHONPATH=skills/img2drawing/src PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q dev/tests
  EXPECT: 60 passed
  EVIDENCE: 60 passed, 1 warning; dev/evidence/material-integration/s13_compatibility.md

- [x] G4: packaged fresh-worker evidence is portable and contains no historical authored coordinates
  CHECK: PYTHONPATH=skills/img2drawing/src python3 dev/tools/verify_bottleneck_completion.py --check s14
  EXPECT: S14_VERIFICATION_PASS
  EVIDENCE: dev/evidence/fresh-worker/generalization_report.json; S14_VERIFICATION_PASS

- [x] G5: release artifacts, manifest hashes, and package-boundary validation agree with the current source
  CHECK: PYTHONPATH=skills/img2drawing/src python3 dev/tools/verify_bottleneck_completion.py --check s15
  EXPECT: S15_VERIFICATION_PASS
  EVIDENCE: dev/release/r23/release_manifest.json; S15_VERIFICATION_PASS

- [x] G6: representative output and comparison board receive an independent whole-view visual inspection
  EVIDENCE: dev/evidence/material-integration/s10-quality-run/final/drawing.png; dev/evidence/fresh-worker/final/drawing.png; direct inspection recorded in S10/S14 reports
