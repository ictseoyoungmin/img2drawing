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
    assert "authority rule itself is owned by `../foundation/reference-authority.md`" in observation
    assert "re-observe at useful whole/crop scales" in observation
    assert "do not turn uncertainty into a template repair" in observation

    assert "projection-fidelity reminder" in hands
    assert "../foundation/reference-authority.md" in hands
    assert "do not flip handedness" in hands
    assert "reopen observation instead of repairing from memory" in hands

    assert "projection-fidelity reminder" in depth
    assert "../foundation/reference-authority.md" in depth
    assert "do not lengthen a compressed segment" in depth
    assert "reopen observation rather than repairing from memory" in depth


def test_supplied_identity_routes_to_canonical_reference_authority() -> None:
    head = _flat(REFS / "figure" / "head-face-hair.md")

    assert "identity-fidelity reminder" in head
    assert "../foundation/reference-authority.md" in head
    assert "do not redraw a familiar or named subject from memory" in head
    assert "reopen observation rather than substituting a canonical model-sheet version" in head


def test_visual_acceptance_correction_and_completion_keep_distinct_ownership() -> None:
    gates = _flat(REFS / "review" / "visual-quality-gates.md")
    correction = _flat(REFS / "review" / "residual-correction.md")
    completion = _flat(REFS / "review" / "completion.md")

    assert "reference-fidelity / anti-normalization gate" in gates
    assert "canonical authority rule lives in `../foundation/reference-authority.md`" in gates
    assert "authority drift" in gates
    assert "reopen observation" in gates

    assert "authority drift is an upstream residual" in correction
    assert "canonical authority and anti-normalization are defined in `../foundation/reference-authority.md`" in correction
    assert "reopen the responsible observation or parent geometry" in correction

    assert "canonical anti-normalization semantics live in `../foundation/reference-authority.md`" in completion
    assert "unresolved authority drift as a blocker" in completion


def test_canonical_definition_phrases_do_not_spread_into_boundary_reminders() -> None:
    nonowners = " ".join(
        _flat(REFS / path)
        for path in (
            "observation/visual-observation.md",
            "figure/hands-and-grip.md",
            "construction/foreshortening-and-depth.md",
            "figure/head-face-hair.md",
            "review/visual-quality-gates.md",
            "review/residual-correction.md",
            "review/completion.md",
        )
    )

    assert "diagnostic priors, not correction authority" not in nonowners
    assert "particular supplied reference instance" not in nonowners
