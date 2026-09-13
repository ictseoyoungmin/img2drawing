#!/usr/bin/env python3
"""Verify current-facing docs while keeping released snapshots immutable."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PLANNING = ROOT / "dev" / "planning" / "vnext"
RELEASE = ROOT / "dev" / "release" / "vnext"
PUBLISH = ROOT / "dev" / "release" / "publish"


def text(path: Path) -> str:
    assert path.is_file(), f"missing current-facing document: {path.relative_to(ROOT)}"
    return path.read_text(encoding="utf-8")


def current_identity(version_text: str) -> tuple[str, str, str]:
    def get(name: str) -> str:
        match = re.search(rf'^{name} = "([^"]+)"$', version_text, flags=re.MULTILINE)
        assert match, f"missing {name}"
        return match.group(1)
    return get("__version__"), get("RELEASE_REVISION"), get("RELEASE_SLICE")


def main() -> None:
    assert not (ROOT / "GATES.md").exists()
    assert not (ROOT / "HANDOFF.md").exists()

    root_readme = text(ROOT / "README.md")
    changelog = text(ROOT / "CHANGELOG.md")
    status = text(PLANNING / "STATUS.md")
    roadmap = text(PLANNING / "ROADMAP.md")
    contract = text(PLANNING / "CONTRACT.md")
    version_text = text(ROOT / "skills" / "img2drawing" / "src" / "img2drawing" / "_version.py")
    version, revision, release_slice = current_identity(version_text)

    assert "**Current stable: v1.0.3**" in root_readme
    assert "PUBLISHED STABLE:   v1.0.3" in status
    assert "d6151ba8dfef8dc37ef5cddd24c2c6c974d53976" in status
    assert "R23" in status and "physically retired" in status
    assert "CURRENT MAIN INVARIANTS" in contract

    stable = json.loads(text(RELEASE / "CONTRACT_FREEZE_V1_0_3.json"))
    assert stable["freeze_id"] == "v1.0.3-A14-2026-09-13"
    assert stable["package_version"] == "1.0.3"
    assert stable["public_api"] == "DrawingSession/1.0.3-vnext"
    assert stable["release_revision"] == "A14"
    assert stable["canonical_render_profile"]["renderer_id"] == "pillow-pencil-contact-v11"
    manifest = json.loads(text(PUBLISH / "v1.0.3.json"))
    assert manifest["tag"] == "v1.0.3"
    assert manifest["notes_file"] == "docs/releases/v1.0.3.md"
    assert manifest["package_dir"] == "skills/img2drawing"
    assert manifest["assets"] == []

    if version == "1.0.3":
        assert revision == "A14"
        assert release_slice == "v1.0.3_gesture_renderer_quality"
        assert "CURRENT RENDERER:   new sessions → pillow-pencil-contact-v11/1" in status
        assert "NEXT GATE:          none for v1.0.3 · release CLOSED" in status
    else:
        assert re.fullmatch(r"1\.0\.4rc\d+", version), version
        assert revision == "A15"
        assert release_slice == "v1.0.4rc1_terminal_mode_pixels"
        assert "CURRENT SOURCE:     1.0.4rc1 · DrawingSession/1.0.4-vnext · A15" in status
        assert "v1.0.3" in status and "remains latest published stable" in status
        assert "CURRENT RENDERER:   new sessions → pillow-pencil-contact-v12/1" in status
        assert "T01 TERMINAL SEMANTICS:" in status
        assert "T01" in roadmap and "terminal" in roadmap.lower()
        assert "NEXT PRODUCT BOTTLENECK" in roadmap and "T01" in roadmap
        assert "## Unreleased" in changelog
        assert "pillow-pencil-contact-v12" in changelog
        assert not (PUBLISH / "v1.0.4.json").exists()

    frozen_v102 = json.loads(text(RELEASE / "CONTRACT_FREEZE.json"))
    assert frozen_v102["freeze_id"] == "v1.0.2-A10-2026-09-09"
    assert frozen_v102["package_version"] == "1.0.2"
    assert text(RELEASE / "FREEZE.md").startswith("# v1.0.2 stable contract freeze")
    assert text(RELEASE / "RELEASE.md").startswith("# img2drawing v1.0.2 maintainer release record")
    assert "Released stable: **1.0.2**" in text(RELEASE / "SUPPORT.md")

    stale = (
        "D01 is the next authorized work",
        "Physical R23 retirement occurs only at R03",
        "NEXT ENGINEERING: fresh sealed D01 validation",
        "Known current defect:",
    )
    for document in (status, roadmap, contract):
        for marker in stale:
            assert marker not in document, marker

    print("CURRENT_DOCUMENTATION_CONSISTENCY_PASS")


if __name__ == "__main__":
    main()
