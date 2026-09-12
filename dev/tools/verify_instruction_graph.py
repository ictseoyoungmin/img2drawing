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

INLINE_MD_PATH = re.compile(r"`([^`\n]+\.md)`")
MARKDOWN_MD_LINK = re.compile(r"\]\(([^)\n]+\.md)\)")


def _all_reference_leaves() -> set[str]:
    return {
        path.relative_to(REFERENCES).as_posix()
        for path in REFERENCES.rglob("*.md")
        if path != INDEX
    }


def _routing_tokens(text: str) -> set[str]:
    """Return Markdown routing targets from inline-code paths and ordinary links."""

    return set(INLINE_MD_PATH.findall(text)) | set(MARKDOWN_MD_LINK.findall(text))


def _skill_routing_paths(text: str) -> set[str]:
    return {token for token in _routing_tokens(text) if "/" in token}


def _resolve_reference_target(source: Path, token: str) -> Path | None:
    raw = token.strip()
    if not raw or raw.startswith(("http://", "https://")):
        return None
    if raw.startswith("references/"):
        candidate = SKILL_ROOT / raw
    elif "/" in raw:
        candidate = REFERENCES / raw
    else:
        candidate = source.parent / raw
    try:
        candidate = candidate.resolve()
        candidate.relative_to(REFERENCES.resolve())
    except (ValueError, OSError):
        return None
    return candidate


def _reachable_reference_leaves() -> set[str]:
    """Traverse INDEX and nested leaf links rather than requiring a flat index."""

    reachable: set[str] = set()
    pending = [INDEX]
    visited: set[Path] = set()
    while pending:
        source = pending.pop()
        source = source.resolve()
        if source in visited:
            continue
        visited.add(source)
        text = source.read_text(encoding="utf-8")
        for token in _routing_tokens(text):
            target = _resolve_reference_target(source, token)
            if target is None or target == INDEX.resolve() or not target.is_file():
                continue
            relative = target.relative_to(REFERENCES.resolve()).as_posix()
            if relative not in reachable:
                reachable.add(relative)
                pending.append(target)
    return reachable


def verify_skill_router() -> None:
    text = SKILL.read_text(encoding="utf-8")
    assert "`references/INDEX.md`" in text, "SKILL.md must route through references/INDEX.md"

    tokens = _skill_routing_paths(text)
    bare = sorted(token for token in tokens if not token.startswith("references/"))
    assert not bare, (
        "SKILL.md paths are skill-root relative; routed Markdown paths must start with references/:\n"
        + "\n".join(bare)
    )

    missing = sorted(token for token in tokens if not (SKILL_ROOT / token).is_file())
    assert not missing, "SKILL.md routes to missing Markdown files:\n" + "\n".join(missing)

    assert "navigation" in text.lower(), (
        "SKILL.md must keep authored-element navigation discoverable"
    )


def verify_index_reachability() -> None:
    """Generic invariant: every leaf in this graph is reachable from INDEX transitively."""

    leaves = _all_reference_leaves()
    reachable = _reachable_reference_leaves()
    missing = sorted(leaves - reachable)
    assert not missing, (
        "reference leaves are not reachable from references/INDEX.md or nested routes:\n"
        + "\n".join(missing)
    )


def verify_product_required_routes() -> None:
    """Current img2drawing-specific leaves that must remain reachable."""

    reachable = _reachable_reference_leaves()
    assert "review/authored-element-navigation.md" in reachable, (
        "instruction graph must route authored-element navigation"
    )
    assert "api/runtime-discovery.md" in reachable, (
        "instruction graph must route runtime discovery through the public API boundary"
    )


def main() -> None:
    verify_skill_router()
    verify_index_reachability()
    verify_product_required_routes()
    print("INSTRUCTION_GRAPH_REACHABILITY_PASS")


if __name__ == "__main__":
    main()
