from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REFS = ROOT / "skills" / "img2drawing" / "references"


def _text(relative: str) -> str:
    return (REFS / relative).read_text(encoding="utf-8")


def test_residual_review_owns_decision_not_runtime_tutorial() -> None:
    correction = _text("review/residual-correction.md")
    public = _text("api/public-surface.md")

    assert "## Runtime provenance boundary" in correction
    assert "../api/public-surface.md" in correction
    assert "session.record_residual(" not in correction
    assert "session.replace_stroke(" not in correction
    assert "session.resolve_residual(" not in correction

    assert "## Residual provenance" in public
    assert "session.record_residual(" in public
    assert "session.replace_stroke(" in public
    assert "session.resolve_residual(" in public
    assert "correction action observation mismatch" in public


def test_completion_owns_artistic_judgment_not_mode_or_finish_runtime_textbook() -> None:
    completion = _text("review/completion.md")
    gesture = _text("modes/gesture-drawing.md")
    public = _text("api/public-surface.md")

    assert "## Mode-specific completion ownership" in completion
    assert "../modes/gesture-drawing.md" in completion
    assert "## Runtime completion boundary" in completion
    assert "../api/public-surface.md" in completion

    assert "## Completion test" in gesture
    assert "orientationless circle" in gesture
    assert "constructive gesture" in gesture

    assert "## Evidence and completion mechanics" in public
    assert "session.record_evidence_read" in public
    assert "DrawingSession.finish()" in public
    assert "any residual record remains open" in public


def test_reference_authority_is_the_definition_owner() -> None:
    authority = _text("foundation/reference-authority.md")
    reminders = "\n".join(
        _text(path)
        for path in (
            "observation/visual-observation.md",
            "construction/foreshortening-and-depth.md",
            "figure/hands-and-grip.md",
            "figure/head-face-hair.md",
            "review/visual-quality-gates.md",
            "review/residual-correction.md",
            "review/completion.md",
        )
    )

    assert "### Visible projection outranks normalization" in authority
    assert "diagnostic priors, not correction authority" in authority
    assert "particular supplied reference instance" in authority

    assert "### Visible projection outranks normalization" not in reminders
    assert "diagnostic priors, not correction authority" not in reminders
    assert "particular supplied reference instance" not in reminders
