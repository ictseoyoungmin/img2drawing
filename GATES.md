# Gates: img2drawing bottleneck completion

OWNS: README.md, skills/img2drawing/**, dev/tools/**, dev/tests/**, dev/schemas/**, dev/evidence/**, dev/planning/**, dev/release/**, .github/**

Scope: complete the material-derived visual-quality bottleneck slices and leave one portable, tested release candidate.

Interim R23 status: runtime/evidence truth hardening is complete for the current
canonical S10/S12 path; strict packaged fresh-worker E2E, release rebuild and
independent visual approval remain open. R23 is not final CLOSED until G5/G6 are
re-verified after those slices.

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
  EXPECT: 65 passed
  EVIDENCE: 65 passed, 5 warnings; dev/evidence/material-integration/s13_compatibility.md

- [x] G4: scripted generalization smoke fixture is portable and contains no historical authored coordinates
  CHECK: PYTHONPATH=skills/img2drawing/src python3 dev/tools/verify_bottleneck_completion.py --check s14
  EXPECT: S14_VERIFICATION_PASS (smoke only; not strict fresh-worker closure)
  EVIDENCE: dev/evidence/fresh-worker/generalization_report.json; S14_VERIFICATION_PASS

- [ ] G4b: strict packaged fresh-worker E2E and separate evaluator return are verified
  CHECK: PYTHONPATH=skills/img2drawing/src python3 dev/tools/verify_bottleneck_completion.py --check s14b --evidence-dir <returned-evidence-dir>
  EXPECT: S14B_VERIFICATION_PASS
  EVIDENCE: pending external fresh worker + independent evaluator; see dev/planning/capsules/T2-strict-fresh-worker-contract.md

- [ ] G5: rebuilt release artifacts, manifest hashes, and package-boundary validation agree with the hardened source
  CHECK: PYTHONPATH=skills/img2drawing/src python3 dev/tools/verify_bottleneck_completion.py --check s15
  EXPECT: S15_VERIFICATION_PASS
  EVIDENCE: pending T3 release rebuild; previous candidate is stale after T1 source changes

- [ ] G6: representative output and comparison board receive an independent whole-view visual inspection
  EVIDENCE: pending separate evaluator approval; T1 engineering inspection does not satisfy this gate
