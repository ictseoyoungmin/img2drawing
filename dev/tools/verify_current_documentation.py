#!/usr/bin/env python3
"""Verify current-facing documentation agrees with stable + current-RC repository truth."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PLANNING = ROOT / "dev" / "planning" / "vnext"
RELEASE = ROOT / "dev" / "release" / "vnext"


def _text(path: Path) -> str:
    assert path.is_file(), f"missing current-facing document: {path.relative_to(ROOT)}"
    return path.read_text(encoding="utf-8")


def _current_package_identity(version_text: str) -> tuple[str, str]:
    version_match = re.search(r'^__version__ = "([^"]+)"$', version_text, flags=re.MULTILINE)
    revision_match = re.search(r'^RELEASE_REVISION = "([^"]+)"$', version_text, flags=re.MULTILINE)
    assert version_match, "current package version declaration missing"
    assert revision_match, "current release revision declaration missing"
    return version_match.group(1), revision_match.group(1)


def main() -> None:
    assert not (ROOT / "GATES.md").exists(), "retired root GATES.md reappeared"
    assert not (ROOT / "HANDOFF.md").exists(), "retired root HANDOFF.md reappeared"

    root_readme = _text(ROOT / "README.md")
    changelog = _text(ROOT / "CHANGELOG.md")
    version = _text(ROOT / "skills" / "img2drawing" / "src" / "img2drawing" / "_version.py")
    planning_readme = _text(PLANNING / "README.md")
    status = _text(PLANNING / "STATUS.md")
    roadmap = _text(PLANNING / "ROADMAP.md")
    contract = _text(PLANNING / "CONTRACT.md")
    validation = _text(PLANNING / "VALIDATION_RELEASE.md")

    release_readme = _text(RELEASE / "README.md")
    freeze = _text(RELEASE / "FREEZE.md")
    release_notes = _text(RELEASE / "RELEASE.md")
    support = _text(RELEASE / "SUPPORT.md")
    migration = _text(RELEASE / "MIGRATION.md")
    frozen = json.loads(_text(RELEASE / "CONTRACT_FREEZE.json"))

    # Published stable and current release-candidate truth are separate authorities. The current
    # package version is parsed rather than hard-coded so rc follow-ups do not require a stale
    # one-line verifier edit just to advance from rcN to rcN+1.
    package_version, release_revision = _current_package_identity(version)
    assert re.fullmatch(r"1\.0\.3rc\d+", package_version), package_version
    assert re.fullmatch(r"A\d+", release_revision), release_revision

    assert "**Current stable: v1.0.2**" in root_readme
    assert "unreleased post-v1.0.2 hardening" in root_readme
    assert "## Unreleased" in changelog
    assert "RELEASED STABLE:" in status and "v1.0.2" in status
    rc_marker = "RC CANDIDATE:" in status or "RC IN MAIN:" in status
    assert rc_marker and package_version in status
    if "RC IN MAIN:" in status:
        assert "MAIN INTEGRATION:" in status and "PASS" in status
        assert "MAIN CI:" in status and "PASS" in status
    assert "PUBLISH STATE:" in status and "v1.0.2 remains latest published stable" in status
    assert "R23" in status and "physically retired" in status
    assert "current unreleased main state after v1.0.2" in roadmap
    assert "G01" in roadmap and "gesture" in roadmap.lower()
    assert "CURRENT MAIN INVARIANTS" in contract
    assert "current `src` contains no installable R23 runtime/legacy namespace" in planning_readme
    assert "current validation matrix for unreleased post-v1.0.2 main" in validation

    stale_current_markers = {
        PLANNING / "README.md": (
            "D01 is the next authorized work",
            "Physical R23 retirement occurs only at R03",
        ),
        PLANNING / "STATUS.md": (
            "PACKAGE:          1.0.1",
            "STABLE BASELINE:  v1.0.1",
            "NEXT ENGINEERING: fresh sealed D01 validation",
            "R23 remains explicit compatibility only; physical retirement is still a later bounded decision",
        ),
        PLANNING / "ROADMAP.md": (
            "Phase E — fresh integrated validation — NEXT",
            "R03 physical R23 retirement",
            "stable v1.0.1 notes",
        ),
        PLANNING / "CONTRACT.md": (
            "FROZEN FOR D01–D06",
            "Physical R23 retirement occurs only at R03",
            "img2drawing.legacy.r23",
        ),
        PLANNING / "VALIDATION_RELEASE.md": (
            "Starts only after: **B18 CLOSED",
            "R03 — Physical R23 retirement",
            "The current migration implementation first resumes a `DrawingRun`",
        ),
    }
    current_text = {
        PLANNING / "README.md": planning_readme,
        PLANNING / "STATUS.md": status,
        PLANNING / "ROADMAP.md": roadmap,
        PLANNING / "CONTRACT.md": contract,
        PLANNING / "VALIDATION_RELEASE.md": validation,
    }
    for path, markers in stale_current_markers.items():
        for marker in markers:
            assert marker not in current_text[path], (
                f"stale current-state marker in {path.relative_to(ROOT)}: {marker!r}"
            )

    # Frozen release records remain v1.0.2 authority while explicitly separating later RC changes.
    assert frozen["freeze_id"] == "v1.0.2-A10-2026-09-09"
    assert frozen["package_version"] == "1.0.2"
    assert frozen["public_api"] == "DrawingSession/1.0.2-vnext"
    assert "v1.0.2 / A10" in release_readme
    assert freeze.startswith("# v1.0.2 stable contract freeze")
    assert release_notes.startswith("# img2drawing v1.0.2 maintainer release record")
    assert "Released stable: **1.0.2**" in support
    assert "Current post-v1.0.2 `main` no longer installs `img2drawing.legacy.r23`" in migration

    for name, text in {
        "FREEZE.md": freeze,
        "RELEASE.md": release_notes,
        "SUPPORT.md": support,
        "MIGRATION.md": migration,
    }.items():
        assert "v1.0.1 stable contract freeze" not in text, name
        assert "# 1.0.1 stable release notes" not in text, name
        assert "Version: **1.0.0**" not in text, name

    print("CURRENT_DOCUMENTATION_CONSISTENCY_PASS")


if __name__ == "__main__":
    main()
