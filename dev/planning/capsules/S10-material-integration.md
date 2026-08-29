# S10 capsule — macro semantic residual closure

- Responsibility: bind visual decisions to the original subject and prevent
  metric/matte false positives.
- Public output: `dev/evidence/material-integration/s10-quality-run/` plus
  `s10_residual_gate.json` and `s10_integration_report.md`.
- Authority: `DrawingRun`, frozen `ObservationContract`, and independent visual
  evaluator; metric and correction history are diagnostic only.
- Invariants: P4/P5 visual records share state/artifact/cursor/lock digests;
  eight macro residual regions are explicit; no checkout-specific paths are
  promoted.
- Evidence: `dev/tools/build_material_quality_run.py`,
  `dev/tools/verify_bottleneck_completion.py --check s10`.
- Limitation: visual acceptance is human/agent inspection, not a likeness score;
  later macro mismatch requires reopening the earliest responsible stage.
- Reopen: any oversized/flat/rail-like macro relation, stale digest, missing
  blind packet, or subject-reference substitution.
