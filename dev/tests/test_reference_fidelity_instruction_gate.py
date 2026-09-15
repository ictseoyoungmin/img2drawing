from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REFS = ROOT / "skills" / "img2drawing" / "references"


def _flat(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split()).lower()


def test_observed_reference_authority_outranks_normalization_priors() -> None:
    authority = _flat(REFS / "foundation" / "reference-authority.md")

    assert "diagnostic priors, not correction authority" in authority
    assert "particular supplied reference instance" in authority
    assert "do not silently replace it with the relation you expect" in authority
    assert "remembered canonical designs never outrank" in authority


def test_plausibility_conflict_routes_to_reobservation_not_template_repair() -> None:
    observation = _flat(REFS / "observation" / "visual-observation.md")
    hands = _flat(REFS / "figure" / "hands-and-grip.md")
    depth = _flat(REFS / "construction" / "foreshortening-and-depth.md")

    assert "plausibility conflict check" in observation
    assert "inspect more carefully" in observation
    assert "anatomy and object knowledge" in observation

    assert "preserve the visible projection before expected anatomy" in hands
    assert "do not flip handedness" in hands
    assert "silently normalizing" in hands

    assert "projection authority before plausibility repair" in depth
    assert "may not silently replace a coherent projection" in depth
    assert "do not lengthen a compressed segment" in depth


def test_supplied_identity_outranks_remembered_character_design() -> None:
    head = _flat(REFS / "figure" / "head-face-hair.md")

    assert "observed identity beats remembered identity" in head
    assert "do not redraw the supplied instance from memory" in head
    assert "does not authorize substitution" in head


def test_visual_acceptance_and_completion_block_authority_drift() -> None:
    gates = _flat(REFS / "review" / "visual-quality-gates.md")
    correction = _flat(REFS / "review" / "residual-correction.md")
    completion = _flat(REFS / "review" / "completion.md")

    assert "reference-fidelity / anti-normalization gate" in gates
    assert "authority drift" in gates
    assert "silently substitute" in gates

    assert "authority drift is an upstream residual" in correction
    assert "less faithful to the visible reference" in correction

    assert "silently normalized toward expected anatomy" in completion
    assert "reference-fidelity / anti-normalization" in completion
    assert "silently substituting another result" in completion
