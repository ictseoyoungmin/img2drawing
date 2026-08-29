from __future__ import annotations

import pytest

from img2drawing import (
    AcceptedResidual,
    AdaptiveEvidencePolicy,
    AssistiveROIProposal,
    ExcludedRegion,
    PreviewArtifact,
)


DIGEST = "a" * 64


def test_adaptive_policy_round_trip_is_observation_bound():
    policy = AdaptiveEvidencePolicy(
        observation_lock_digest=DIGEST,
        proposals=(AssistiveROIProposal("roi-01", "face", (0.1, 0.1, 0.3, 0.3), "agent-preview", .8, DIGEST, True, "agent checked"),),
        excluded_regions=(ExcludedRegion("far-hand", "occluded by prop", ("occlusion",), DIGEST),),
        accepted_residuals=(AcceptedResidual("loose-fold", "P5_clean_blockin", "low-resolution fold", "outside requested identity scope"),),
    )
    restored = AdaptiveEvidencePolicy.from_dict(policy.to_dict())
    assert restored.digest() == policy.digest()
    assert restored.preview_only is True


def test_adaptive_policy_rejects_mismatched_lock_and_owned_residual():
    with pytest.raises(ValueError):
        AdaptiveEvidencePolicy(
            observation_lock_digest=DIGEST,
            proposals=(AssistiveROIProposal("roi-01", "face", (0.1, 0.1, 0.3, 0.3), "auto", .5, "b" * 64),),
        )
    with pytest.raises(ValueError):
        AcceptedResidual("torso", "P3_primary_masses", "wrong torso", "not allowed", stage_owned=True)


def test_preview_artifact_is_explicitly_non_authoritative(tmp_path):
    artifact = PreviewArtifact(tmp_path / "preview.png", DIGEST, "pillow-pencil-contact-v9", 1)
    data = artifact.to_dict()
    assert data["evidence_role"] == "preview_only"
    assert "not_review_final" in data["authority"]
