from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
VERIFIER_PATH = ROOT / "dev" / "tools" / "verify_instruction_graph.py"


def _load_verifier():
    spec = importlib.util.spec_from_file_location("verify_instruction_graph_dynamic_test", VERIFIER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _bind_fixture(module, root: Path) -> tuple[Path, Path, Path]:
    skill_root = root / "skills" / "img2drawing"
    references = skill_root / "references"
    category = references / "future-category"
    category.mkdir(parents=True)

    leaf = category / "new-leaf.md"
    leaf.write_text("# Future leaf\n", encoding="utf-8")
    index = references / "INDEX.md"
    index.write_text(
        "# Index\n\n- `future-category/new-leaf.md`\n",
        encoding="utf-8",
    )
    skill = skill_root / "SKILL.md"

    module.SKILL_ROOT = skill_root
    module.SKILL = skill
    module.REFERENCES = references
    module.INDEX = index
    return skill, index, leaf


def test_new_reference_category_bare_skill_path_is_rejected_without_allowlist(tmp_path: Path) -> None:
    module = _load_verifier()
    skill, _index, _leaf = _bind_fixture(module, tmp_path)
    skill.write_text(
        "Read `references/INDEX.md`, then `future-category/new-leaf.md`.\n"
        "Authored-element navigation remains discoverable.\n",
        encoding="utf-8",
    )

    with pytest.raises(AssertionError, match="must start with references/"):
        module.verify_skill_router()


def test_new_reference_category_is_reachable_without_verifier_changes(tmp_path: Path) -> None:
    module = _load_verifier()
    skill, _index, _leaf = _bind_fixture(module, tmp_path)
    skill.write_text(
        "Read `references/INDEX.md`, then `references/future-category/new-leaf.md`.\n"
        "Authored-element navigation remains discoverable.\n",
        encoding="utf-8",
    )

    module.verify_skill_router()
    module.verify_index_reachability()
