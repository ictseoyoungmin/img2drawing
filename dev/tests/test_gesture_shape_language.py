from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REFS = ROOT / "skills" / "img2drawing" / "references"


def _text(path: str) -> str:
    return " ".join((REFS / path).read_text(encoding="utf-8").split()).lower()


def test_gesture_final_marks_do_not_collapse_to_generic_primitives() -> None:
    mode = _text("modes/gesture-drawing.md")
    construction = _text("construction/gesture-and-masses.md")
    specificity = _text("foundation/structural-specificity.md")
    head = _text("figure/head-face-hair.md")
    completion = _text("review/completion.md")

    assert "reasoning primitive" in mode
    assert "generic circle" in mode
    assert "flat box, sharp polygon, or faceted shield" in mode
    assert "smooth bean, capsule, or egg" in mode
    assert "smooth oval, or capsule" in mode
    assert "stock rounded blobs" in mode
    assert "do not invent corners or plane breaks" in mode
    assert "temporary search primitives" in mode

    assert "construction shorthand is disposable reasoning" in construction
    assert "head search sphere must become a directional cranial volume" in construction
    assert "smooth generic bean/capsule" in construction
    assert "smooth oval or capsule" in construction
    assert "rounded` is not a sufficient quality criterion" in construction
    assert "do not invent hard corners" in construction

    assert "reasoning primitives are disposable" in specificity
    assert "orientationless circle" in specificity
    assert "stock rounded bean/capsule" in specificity
    assert "smooth oval/capsule" in specificity
    assert "rounded` is not automatically more specific" in specificity

    assert "facial features may be omitted, but head direction may not disappear" in head
    assert "cranial search sphere is temporary reasoning" in head
    assert "face cross-axis is an orientation aid, not a substitute for head volume" in head

    assert "orientationless circle-head" in completion
    assert "flat/sharply faceted ribcage" in completion
    assert "smooth generic bean/oval/capsule" in completion
    assert "rounded` alone is not a completion criterion" in completion
