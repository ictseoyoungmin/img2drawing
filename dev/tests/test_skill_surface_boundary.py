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
        "examples",
        "pyproject.toml",
        "references",
        "src",
    }


def test_skill_examples_are_only_portable_mechanical_examples() -> None:
    assert {path.name for path in (SKILL / "examples").iterdir()} == {
        "mechanical_workflows.py",
        "observed",
        "subjectless",
    }


def test_reference_surface_has_no_legacy_stage_or_hidden_worker_tree() -> None:
    assert {path.name for path in (SKILL / "references").iterdir()} == {
        "INDEX.md",
        "construction",
        "figure",
        "finish",
        "intent.md",
        "legacy-r23.md",
        "modes",
        "observation",
        "output",
        "pencil",
        "reference-authority.md",
        "resolution",
        "review",
        "styles",
        "value",
    }
    assert {path.name for path in (SKILL / "references" / "review").iterdir()} == {
        "authored-element-navigation.md",
        "completion.md",
        "correction-loop.md",
        "residual-correction.md",
        "stroke-retirement.md",
    }


def test_skill_facing_docs_do_not_leak_internal_slice_or_release_control_plane() -> None:
    documents = [SKILL / "SKILL.md", SKILL / "README.md"]
    documents.extend((SKILL / "references").rglob("*.md"))
    documents.extend((SKILL / "examples").rglob("*.md"))

    slice_label = re.compile(r"\bB(?:0[0-9]|1[0-8])(?:-R\d+)?\b")
    forbidden_filenames = (
        "CONTRACT_FREEZE.json",
        "FREEZE.md",
        "MIGRATION.md",
        "NOTICE.md",
        "RELEASE.md",
        "SUPPORT.md",
    )

    for path in documents:
        text = path.read_text(encoding="utf-8")
        assert not slice_label.search(text), f"internal slice label leaked into {path.relative_to(ROOT)}"
        assert "`dev/" not in text, f"developer path leaked into {path.relative_to(ROOT)}"
        for name in forbidden_filenames:
            assert name not in text, f"release control-plane reference {name} leaked into {path.relative_to(ROOT)}"


def test_notice_is_not_part_of_skill_or_package_metadata() -> None:
    assert not (SKILL / "NOTICE").exists()
    assert not (SKILL / "NOTICE.md").exists()
    pyproject = (SKILL / "pyproject.toml").read_text(encoding="utf-8")
    manifest = (SKILL / "MANIFEST.in").read_text(encoding="utf-8")
    assert "NOTICE" not in pyproject
    assert "NOTICE" not in manifest
