#!/usr/bin/env python3
"""Verify the deployable img2drawing instruction graph is reachable and attention-bounded."""

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
CONTROL_PLANE_PATH = re.compile(r"(?:^|[\s`(])(?:\.\./)*dev/|(?:^|[\s`(])(?:\.\./)*\.github/", re.MULTILINE)

# Slice E budgets are deliberately above the cleaned Slice D baseline while low enough to
# prevent the router/map from silently regrowing into textbooks.
MAX_SKILL_BYTES = 12_000
MAX_INDEX_BYTES = 10_000
MAX_ROOT_DIRECT_LEAF_ROUTES = 16

CANONICAL_OWNER_LEAVES = {
    "foundation/reference-authority.md",
    "foundation/line-economy.md",
    "foundation/structural-specificity.md",
    "foundation/occlusion-inference.md",
    "observation/visual-observation.md",
    "modes/gesture-drawing.md",
    "review/visual-quality-gates.md",
    "review/residual-correction.md",
    "review/residual-routing.md",
    "review/stroke-retirement.md",
    "review/completion.md",
    "output/render-profile-and-replay.md",
    "api/public-surface.md",
}

FORBIDDEN_RELEASE_CONTROL_FILENAMES = {
    "CONTRACT_FREEZE.json",
    "FREEZE.md",
    "MIGRATION.md",
    "NOTICE.md",
    "RELEASE.md",
    "SUPPORT.md",
}


def _all_reference_leaves() -> set[str]:
    return {
        path.relative_to(REFERENCES).as_posix()
        for path in REFERENCES.rglob("*.md")
        if path != INDEX
    }


def _deployable_markdown() -> list[Path]:
    return [SKILL, *sorted(REFERENCES.rglob("*.md"))]


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


def verify_single_skill_entrypoint() -> None:
    """The deployable skill root has one Agent-facing Markdown entrypoint: SKILL.md."""

    assert SKILL.is_file(), "skills/img2drawing/SKILL.md must exist"
    assert not (SKILL_ROOT / "README.md").exists(), (
        "skills/img2drawing/README.md creates a second skill-root entrypoint; "
        "keep Agent routing authority in SKILL.md"
    )


def verify_skill_router() -> None:
    """Generic router/path invariant; keep product-specific routes out of this layer."""

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


def verify_index_map_surface() -> None:
    """INDEX is a direct low-attention map: one routing row per deployable leaf."""

    text = INDEX.read_text(encoding="utf-8")
    assert "This file is a **map**" in text
    assert "## Runtime-awareness invariant" not in text

    lines = text.splitlines()
    for leaf in sorted(_all_reference_leaves()):
        marker = f"`{leaf}`"
        matches = [line for line in lines if marker in line]
        assert len(matches) == 1, (
            f"INDEX.md must contain exactly one direct map row for {leaf}; found {len(matches)}"
        )
        row = matches[0]
        assert "open when:" in row, f"INDEX.md map row missing open-when metadata: {leaf}"
        assert "owns:" in row, f"INDEX.md map row missing ownership metadata: {leaf}"


def verify_product_required_routes() -> None:
    """Current img2drawing-specific routes layered on top of generic graph reachability."""

    reachable = _reachable_reference_leaves()
    assert "review/authored-element-navigation.md" in reachable, (
        "instruction graph must route authored-element navigation"
    )
    assert "review/visual-quality-gates.md" in reachable, (
        "instruction graph must keep the central visual-quality gate reachable"
    )
    assert "api/runtime-discovery.md" in reachable, (
        "instruction graph must route runtime discovery through the public API boundary"
    )

    skill_text = SKILL.read_text(encoding="utf-8")
    skill_tokens = _skill_routing_paths(skill_text)
    quality_gate = "references/review/visual-quality-gates.md"
    assert quality_gate in skill_tokens, (
        "SKILL.md must directly route observed finished/substantially-resolved work "
        "to the central visual-quality gate"
    )
    assert "before accepting the first descriptive semantic group" in skill_text, (
        "the direct visual-quality route must state its acceptance boundary"
    )


def verify_internal_route_integrity() -> None:
    """Slash-qualified deployable Markdown routes must remain inside the graph and resolve."""

    failures: list[str] = []
    for source in _deployable_markdown():
        text = source.read_text(encoding="utf-8")
        for token in sorted(_routing_tokens(text)):
            raw = token.strip()
            if raw.startswith(("http://", "https://")) or "/" not in raw:
                continue
            target = _resolve_reference_target(source, raw)
            if target is None or not target.is_file():
                failures.append(f"{source.relative_to(ROOT)} -> {raw}")
    assert not failures, "deployable Markdown contains broken/out-of-graph routes:\n" + "\n".join(failures)


def verify_attention_budgets() -> None:
    """Keep the root router and INDEX map beneath explicit Slice E attention ceilings."""

    skill_bytes = len(SKILL.read_bytes())
    index_bytes = len(INDEX.read_bytes())
    assert skill_bytes <= MAX_SKILL_BYTES, (
        f"SKILL.md exceeds attention budget: {skill_bytes} > {MAX_SKILL_BYTES} bytes"
    )
    assert index_bytes <= MAX_INDEX_BYTES, (
        f"references/INDEX.md exceeds attention budget: {index_bytes} > {MAX_INDEX_BYTES} bytes"
    )

    direct_leaf_routes = {
        token
        for token in _skill_routing_paths(SKILL.read_text(encoding="utf-8"))
        if token != "references/INDEX.md"
    }
    assert len(direct_leaf_routes) <= MAX_ROOT_DIRECT_LEAF_ROUTES, (
        "SKILL.md direct leaf fan-out exceeds attention budget: "
        f"{len(direct_leaf_routes)} > {MAX_ROOT_DIRECT_LEAF_ROUTES}\n"
        + "\n".join(sorted(direct_leaf_routes))
    )


def verify_deployable_control_plane_boundary() -> None:
    """Deployable worker guidance must not depend on development/release control-plane docs."""

    failures: list[str] = []
    for source in _deployable_markdown():
        text = source.read_text(encoding="utf-8")
        if CONTROL_PLANE_PATH.search(text):
            failures.append(f"development path leaked into {source.relative_to(ROOT)}")
        for filename in sorted(FORBIDDEN_RELEASE_CONTROL_FILENAMES):
            if filename in text:
                failures.append(
                    f"release control-plane reference {filename} leaked into {source.relative_to(ROOT)}"
                )
    assert not failures, "deployable/control-plane boundary violations:\n" + "\n".join(failures)


def verify_canonical_owner_routes() -> None:
    """Canonical policy owners must remain deployable and reachable after future graph edits."""

    leaves = _all_reference_leaves()
    reachable = _reachable_reference_leaves()
    missing = sorted(CANONICAL_OWNER_LEAVES - leaves)
    unrouted = sorted(CANONICAL_OWNER_LEAVES - reachable)
    assert not missing, "canonical instruction owners are missing:\n" + "\n".join(missing)
    assert not unrouted, "canonical instruction owners are not reachable:\n" + "\n".join(unrouted)


def main() -> None:
    verify_single_skill_entrypoint()
    verify_skill_router()
    verify_index_reachability()
    verify_index_map_surface()
    verify_product_required_routes()
    verify_internal_route_integrity()
    verify_attention_budgets()
    verify_deployable_control_plane_boundary()
    verify_canonical_owner_routes()
    print("INSTRUCTION_GRAPH_ATTENTION_ARCHITECTURE_PASS")


if __name__ == "__main__":
    main()
