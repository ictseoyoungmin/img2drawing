#!/usr/bin/env python3
"""Verify the 1.0.3 markmaking instruction graph and runtime-awareness boundary."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / "skills" / "img2drawing"
REFS = SKILL / "references"

REQUIRED = {
    "markmaking/style-policy.md",
    "markmaking/stroke-role-vocabulary.md",
    "markmaking/tool-preset-selection.md",
    "markmaking/stroke-dynamics.md",
    "markmaking/pressure-and-terminals.md",
    "markmaking/broad-graphite.md",
    "markmaking/custom-tools.md",
    "review/markmaking-residuals.md",
    "api/public-surface.md",
    "INDEX.md",
}


def require(text: str, *needles: str) -> None:
    for needle in needles:
        assert needle in text, f"missing instruction-graph contract phrase: {needle!r}"


def main() -> None:
    missing = sorted(path for path in REQUIRED if not (REFS / path).is_file())
    assert not missing, f"missing 1.0.3 instruction leaves: {missing}"

    index = (REFS / "INDEX.md").read_text(encoding="utf-8")
    public = (REFS / "api" / "public-surface.md").read_text(encoding="utf-8")
    custom = (REFS / "markmaking" / "custom-tools.md").read_text(encoding="utf-8")
    residual = (REFS / "review" / "markmaking-residuals.md").read_text(encoding="utf-8")

    require(
        index,
        "runtime-aware and implementation-blind",
        "DrawingSession",
        "markmaking/style-policy.md",
        "markmaking/stroke-role-vocabulary.md",
        "review/markmaking-residuals.md",
        "api/public-surface.md",
    )
    require(
        public,
        "runtime-aware and implementation-blind",
        "Do **not** replace the runtime with a hand-written Pillow/ImageDraw script",
        "does **not** need to inspect the full `src/` tree",
        "runtime capability gap",
    )
    require(
        custom,
        "session-local custom tool",
        "resolved tool state",
        "Pillow",
    )
    require(
        residual,
        "Is the visible path / overlap / contact itself wrong?",
        "Is the semantic role wrong?",
        "Is the active style policy producing the wrong material interpretation?",
        "runtime capability gap",
    )

    # Shipped canonical guidance remains English-only.
    for relative in REQUIRED:
        text = (REFS / relative).read_text(encoding="utf-8")
        assert not any("\uac00" <= ch <= "\ud7a3" for ch in text), relative

    print("1.0.3 markmaking/runtime-awareness graph: PASS")


if __name__ == "__main__":
    main()
