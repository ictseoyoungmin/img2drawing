from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / "skills" / "img2drawing"


def test_deployable_skill_root_is_attention_clean() -> None:
    assert {path.name for path in SKILL.iterdir()} == {
        "LICENSE",
        "MANIFEST.in",
        "README.md",
        "SKILL.md",
        "pyproject.toml",
        "references",
        "src",
    }
    assert not (SKILL / "examples").exists()


def test_reference_surface_is_the_instruction_graph() -> None:
    assert {path.name for path in (SKILL / "references").iterdir()} == {
        "INDEX.md",
        "api",
        "construction",
        "description",
        "environment",
        "figure",
        "foundation",
        "modes",
        "observation",
        "output",
        "props",
        "review",
    }
    assert {path.name for path in (SKILL / "references" / "foundation").iterdir()} == {
        "line-economy.md",
        "reference-authority.md",
        "scope-and-precedence.md",
    }
    assert {path.name for path in (SKILL / "references" / "figure").iterdir()} == {
        "clothing-folds.md",
        "head-face-hair.md",
        "legs-feet.md",
        "torso-arms-hands.md",
    }
    assert {path.name for path in (SKILL / "references" / "review").iterdir()} == {
        "authored-element-navigation.md",
        "completion.md",
        "residual-correction.md",
        "residual-routing.md",
        "stroke-retirement.md",
    }


def test_instruction_graph_hardens_geometry_preserving_line_economy() -> None:
    skill = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    croquis = (SKILL / "references" / "modes" / "croquis.md").read_text(encoding="utf-8")
    lower = (SKILL / "references" / "figure" / "legs-feet.md").read_text(encoding="utf-8")
    head = (SKILL / "references" / "figure" / "head-face-hair.md").read_text(encoding="utf-8")
    folds = (SKILL / "references" / "figure" / "clothing-folds.md").read_text(encoding="utf-8")

    assert "Croquis economizes marks, not observed geometry" in skill
    assert "Economize marks, not geometry" in croquis
    assert "uniform tube" in lower
    assert "circle" in head
    assert "zigzags" in folds


def test_instruction_graph_routes_residuals_by_cause_and_escalates_upstream() -> None:
    skill = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    index = (SKILL / "references" / "INDEX.md").read_text(encoding="utf-8")
    correction = (SKILL / "references" / "review" / "residual-correction.md").read_text(
        encoding="utf-8"
    )
    routing = (SKILL / "references" / "review" / "residual-routing.md").read_text(
        encoding="utf-8"
    )

    assert "review/residual-routing.md" in skill
    assert "route by the relationship that must change" in index.lower()
    assert "Do not route by the noun that looks wrong" in correction
    assert "Route by **cause**, not by the noun that looks wrong" in routing

    for path in (
        "construction/balance-and-limbs.md",
        "environment/ground-and-context.md",
        "figure/legs-feet.md",
        "description/contour-and-overlap.md",
        "figure/head-face-hair.md",
        "figure/torso-arms-hands.md",
        "props/attached-objects.md",
        "observation/visual-observation.md",
    ):
        assert path in routing

    assert "Escalation is not a stage reset" in routing
    assert "Do not read every branch below" in routing


def test_skill_facing_docs_do_not_leak_internal_or_release_control_plane() -> None:
    documents = [SKILL / "SKILL.md", SKILL / "README.md"]
    documents.extend((SKILL / "references").rglob("*.md"))

    slice_label = re.compile(r"\bB(?:0[0-9]|1[0-8])(?:-R\d+)?\b")
    forbidden_filenames = (
        "CONTRACT_FREEZE.json",
        "FREEZE.md",
        "MIGRATION.md",
        "NOTICE.md",
        "RELEASE.md",
        "SUPPORT.md",
    )
    forbidden_internal = ("_internal", "CanvasAction", "__vnext_compat__")

    for path in documents:
        text = path.read_text(encoding="utf-8")
        assert not slice_label.search(text), f"internal slice label leaked into {path.relative_to(ROOT)}"
        assert "`dev/" not in text, f"developer path leaked into {path.relative_to(ROOT)}"
        for name in forbidden_filenames:
            assert name not in text, f"release control-plane reference {name} leaked into {path.relative_to(ROOT)}"
        for token in forbidden_internal:
            assert token not in text, f"internal implementation token {token} leaked into {path.relative_to(ROOT)}"


def test_notice_is_not_part_of_skill_or_package_metadata() -> None:
    assert not (SKILL / "NOTICE").exists()
    assert not (SKILL / "NOTICE.md").exists()
    pyproject = (SKILL / "pyproject.toml").read_text(encoding="utf-8")
    manifest = (SKILL / "MANIFEST.in").read_text(encoding="utf-8")
    assert "NOTICE" not in pyproject
    assert "NOTICE" not in manifest
