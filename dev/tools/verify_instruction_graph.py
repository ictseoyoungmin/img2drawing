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

# Inline routing paths are written as code spans. Keep this syntax-based rather than
# category-based so a newly added references/<category>/ leaf is covered automatically.
INLINE_MD_PATH = re.compile(r"`([^`\n]+\.md)`")


def _all_reference_leaves() -> set[str]:
    return {
        path.relative_to(REFERENCES).as_posix()
        for path in REFERENCES.rglob("*.md")
        if path != INDEX
    }


def _inline_routing_paths(text: str) -> set[str]:
    """Return inline-code Markdown paths that include a directory component."""

    return {token for token in INLINE_MD_PATH.findall(text) if "/" in token}


def verify_skill_router() -> None:
    text = SKILL.read_text(encoding="utf-8")
    assert "`references/INDEX.md`" in text, "SKILL.md must route through references/INDEX.md"

    tokens = _inline_routing_paths(text)
    bare = sorted(token for token in tokens if not token.startswith("references/"))
    assert not bare, (
        "SKILL.md paths are skill-root relative; routed Markdown paths must start with references/:\n"
        + "\n".join(bare)
    )

    missing = sorted(token for token in tokens if not (SKILL_ROOT / token).is_file())
    assert not missing, "SKILL.md routes to missing Markdown files:\n" + "\n".join(missing)

    assert "authored-element navigation" in text.lower(), (
        "SKILL.md review summary must expose authored-element navigation for discoverability"
    )


def verify_index_reachability() -> None:
    text = INDEX.read_text(encoding="utf-8")
    leaves = _all_reference_leaves()
    mentioned = _inline_routing_paths(text)

    missing = sorted(leaves - mentioned)
    assert not missing, (
        "reference leaves are not reachable from references/INDEX.md:\n" + "\n".join(missing)
    )

    broken = sorted(token for token in mentioned if not (REFERENCES / token).is_file())
    assert not broken, "references/INDEX.md routes to missing Markdown files:\n" + "\n".join(broken)


def main() -> None:
    verify_skill_router()
    verify_index_reachability()
    print("INSTRUCTION_GRAPH_REACHABILITY_PASS")


if __name__ == "__main__":
    main()
