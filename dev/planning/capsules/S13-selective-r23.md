# S13 capsule — selective R23 integration

- Responsibility: retain only safe R23 evidence conveniences without importing
  its alternate runtime or subject-specific workflow.
- API: `AdaptiveEvidencePolicy`, `AssistiveROIProposal`, `ExcludedRegion`,
  `AcceptedResidual`, `PreviewArtifact`.
- Invariants: every proposal/exclusion binds to the frozen observation digest;
  owned or material-mismatch residuals are rejected; previews cannot be review
  authority.
- Evidence: `dev/evidence/material-integration/s13_compatibility.md` and
  `dev/tests/test_adaptive_evidence.py`.
- Limitation: proposals are assistive and never geometry truth.
- Reopen: lock mismatch, path portability regression, or any feature becoming an
  automatic art-quality gate.
