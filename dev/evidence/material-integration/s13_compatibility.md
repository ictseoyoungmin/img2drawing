# S13 selective R23 compatibility

The R23 material repository was evaluated as a set of bounded features, not as
a source tree to merge. The current source integrates only:

1. non-authoritative fast preview (`PreviewArtifact` / `render_preview`),
2. assistive ROI proposals that require agent validation and an observation-lock
   digest,
3. observation-backed exclusions, and
4. `accepted_residuals` that reject material mismatches and stage-owned defects.

The subject-specific R23 workflow, alternate renderer, completion-manifest
paths, and prior PASS verdicts are not imported. `AdaptiveEvidencePolicy` and
all proposal/exclusion records round-trip through JSON and are covered by
`dev/tests/test_adaptive_evidence.py`. Preview artifacts are explicitly
ineligible for review, final, replay, or timelapse authority.

The two failures reported by the temporary R23 tree were treated as migration
signals (schema/portability mismatch), not suppressed. The current complete
suite passes with plugin autoload disabled, and malformed/stale lock and owned
residual cases are explicit negative tests.
