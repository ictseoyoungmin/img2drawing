#!/usr/bin/env python3
"""Verify the deployable img2drawing instruction graph is reachable and path-consistent."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SKILL_ROOT = ROOT / "skills" / "img2drawing"
SKILL = SKILL_ROOT / "SKILL.md"
REFERENCES = SKILL_ROOT / "references"
INDEX = REFERENCES / "INDEX.md"

GRAPH_DIRS = (
    "foundation",
    "modes",
    "observation",
    "construction",
    "description",
    "figure",
    "props",
    "environment",
    "review",
    "output",
    "api",
)
_DIRS = "|".join(re.escape(name) for name in GRAPH_DIRS)
SKILL_LEAF_PATTERN = re.compile(
    rf"`((?:references/)?(?:{_DIRS})/[^`\n]+?\.md)`"
)
INDEX_LEAF_PATTERN = re.compile(rf"`((?:{_DIRS})/[^`\n]+?\.md)`")


def _all_reference_leaves() -> set[str]:
    return {
        path.relative_to(REFERENCES).as_posix()
        for path in REFERENCES.rglob("*.md")
        if path != INDEX
    }


def verify_skill_router() -> None:
    text = SKILL.read_text(encoding="utf-8")
    assert "`references/INDEX.md`" in text, "SKILL.md must route through references/INDEX.md"

    tokens = set(SKILL_LEAF_PATTERN.findall(text))
    bare = sorted(token for token in tokens if not token.startswith("references/"))
    assert not bare, (
        "SKILL.md reference paths are skill-root relative and must start with references/:\n"
        + "\n".join(bare)
    )

    missing = sorted(
        token for token in tokens if not (SKILL_ROOT / token).is_file()
    )
    assert not missing, "SKILL.md routes to missing leaves:\n" + "\n".join(missing)

    assert "authored-element navigation" in text.lower(), (
        "SKILL.md review summary must expose authored-element navigation for discoverability"
    )


def verify_index_reachability() -> None:
    text = INDEX.read_text(encoding="utf-8")
    leaves = _all_reference_leaves()
    mentioned = set(INDEX_LEAF_PATTERN.findall(text))

    missing = sorted(leaves - mentioned)
    assert not missing, (
        "reference leaves are not reachable from references/INDEX.md:\n" + "\n".join(missing)
    )

    broken = sorted(token for token in mentioned if not (REFERENCES / token).is_file())
    assert not broken, "references/INDEX.md routes to missing leaves:\n" + "\n".join(broken)


def main() -> None:
    verify_skill_router()
    verify_index_reachability()
    print("INSTRUCTION_GRAPH_REACHABILITY_PASS")


if __name__ == "__main__":
    main()
