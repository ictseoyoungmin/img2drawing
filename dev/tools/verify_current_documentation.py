#!/usr/bin/env python3
"""Verify current-facing documentation agrees with published + candidate repository truth."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PLANNING = ROOT / "dev" / "planning" / "vnext"
RELEASE = ROOT / "dev" / "release" / "vnext"
PUBLISH = ROOT / "dev" / "release" / "publish"


def _text(path: Path) -> str:
    assert path.is_file(), f"missing current-facing document: {path.relative_to(ROOT)}"
    return path.read_text(encoding="utf-8")


def _current_package_identity(version_text: str) -> tuple[str, str]:
    version_match = re.search(r'^__version__ = "([^"]+)"$', version_text, flags=re.MULTILINE)
    revision_match = re.search(r'^RELEASE_REVISION = "([^"]+)"$', version_text, flags=re.MULTILINE)
    assert version_match, "current package version declaration missing"
    assert revision_match, "current release revision declaration missing"
    return version_match.group(1), revision_match.group(1)


def _updated_date(text: str, name: str) -> str:
    match = re.search(r"^Updated: (\d{4}-\d{2}-\d{2})$", text, flags=re.MULTILINE)
    assert match, f"{name} must declare an Updated date"
    return match.group(1)


def main() -> None:
    assert not (ROOT / "GATES.md").exists(), "retired root GATES.md reappeared"
    assert not (ROOT / "HANDOFF.md").exists(), "retired root HANDOFF.md reappeared"

    root_readme = _text(ROOT / "README.md")
    changelog = _text(ROOT / "CHANGELOG.md")
    version = _text(ROOT / "skills" / "img2drawing" / "src" / "img2drawing" / "_version.py")
    planning_readme = _text(PLANNING / "README.md")
    status = _text(PLANNING / "STATUS.md")
    roadmap = _text(PLANNING / "ROADMAP.md")
    attention_plan = _text(PLANNING / "INSTRUCTION_GRAPH_ATTENTION_ARCHITECTURE_PLAN.md")
    contract = _text(PLANNING / "CONTRACT.md")
    validation = _text(PLANNING / "VALIDATION_RELEASE.md")

    # Mutable planning documents have one current-state authority and one sequencing authority.
    assert _updated_date(status, "STATUS.md") == _updated_date(roadmap, "ROADMAP.md"), (
        "STATUS.md and ROADMAP.md must be synchronized in the same bounded authority slice"
    )
    assert "canonical point-in-time development status" in status
    assert "current mutable state: **this file, `STATUS.md`**" in status
    assert "canonical **point-in-time current-state authority**" in roadmap
    assert "does not create a second current-state truth" in roadmap
    assert "INSTRUCTION_GRAPH_ATTENTION_ARCHITECTURE_PLAN.md" in status
    assert "INSTRUCTION_GRAPH_ATTENTION_ARCHITECTURE_PLAN.md" in roadmap
    assert "Status: Slice A CLOSED · Slice B CLOSED · Slice C CLOSED · Slice D CLOSED · Slice E CLOSED" in attention_plan
    assert (
        "GRAPH CLEANUP:      Slice A CLOSED · Slice B CLOSED · Slice C CLOSED · "
        "Slice D ownership cleanup CLOSED · Slice E structural QA CLOSED"
        in status
    )
    assert "Slice A authority synchronization                         CLOSED" in roadmap
    assert "Slice B SKILL.md router reduction + direct quality gate   CLOSED" in roadmap
    assert "Slice C INDEX.md map-only reduction                       CLOSED" in roadmap
    assert "Slice D leaf ownership / runtime-boundary cleanup         CLOSED" in roadmap
    assert "Slice E attention-architecture QA + structural CI         CLOSED" in roadmap
    for slice_heading in (
        "## Slice A — authority synchronization",
        "## Slice B — make `SKILL.md` a real router",
        "## Slice C — reduce `references/INDEX.md` to a map",
        "## Slice D — canonical leaf ownership + runtime boundary cleanup",
        "## Slice E — attention-architecture QA and structural CI",
    ):
        assert slice_heading in attention_plan, slice_heading

    release_readme = _text(RELEASE / "README.md")
    freeze = _text(RELEASE / "FREEZE.md")
    release_notes = _text(RELEASE / "RELEASE.md")
    support = _text(RELEASE / "SUPPORT.md")
    migration = _text(RELEASE / "MIGRATION.md")
    frozen_v102 = json.loads(_text(RELEASE / "CONTRACT_FREEZE.json"))

    package_version, release_revision = _current_package_identity(version)
    is_rc = re.fullmatch(r"1\.0\.3rc\d+", package_version) is not None
    is_stable = package_version == "1.0.3"
    assert is_rc or is_stable, package_version
    assert re.fullmatch(r"A\d+", release_revision), release_revision

    v103_manifest = PUBLISH / "v1.0.3.json"
    v103_release_intent = v103_manifest.is_file()
    active_post_release_design = is_stable and "ACTIVE BOTTLENECK:" in status

    if is_rc:
        assert "**Current stable: v1.0.2**" in root_readme
        assert "unreleased post-v1.0.2 hardening" in root_readme
        assert "## Unreleased" in changelog
        assert ("RC CANDIDATE:" in status or "RC IN MAIN:" in status) and package_version in status
        assert "v1.0.2 remains latest published stable" in status
        assert not v103_release_intent
    else:
        assert release_revision == "A14"
        assert "## v1.0.3" in changelog
        stable_freeze = json.loads(_text(RELEASE / "CONTRACT_FREEZE_V1_0_3.json"))
        assert stable_freeze["freeze_id"] == "v1.0.3-A14-2026-09-13"
        assert stable_freeze["package_version"] == "1.0.3"
        assert stable_freeze["public_api"] == "DrawingSession/1.0.3-vnext"
        assert stable_freeze["release_revision"] == "A14"
        assert stable_freeze["canonical_render_profile"]["renderer_id"] == "pillow-pencil-contact-v11"
        assert str(stable_freeze["canonical_render_profile"]["renderer_version"]) == "1"
        assert "gesture" in stable_freeze["intent_axes"]["drawing_modes"]
        assert stable_freeze["renderer_authority"]["thin_v10_v11_exact"] is True
        assert stable_freeze["renderer_authority"]["current_fast_canonical_exact"] is True

        if v103_release_intent:
            manifest = json.loads(_text(v103_manifest))
            assert manifest["tag"] == "v1.0.3"
            assert manifest["notes_file"] == "docs/releases/v1.0.3.md"
            assert manifest["package_dir"] == "skills/img2drawing"
            assert manifest["assets"] == []
            released = "**Current stable: v1.0.3**" in root_readme
            if released:
                assert ("PUBLISHED STABLE:" in status or "RELEASED STABLE:" in status) and "v1.0.3" in status
                assert "PUBLISH STATE:      GitHub Release v1.0.3 published" in status
                if active_post_release_design:
                    assert "ACTIVE BOTTLENECK:  S03" in status
                    assert "S01 DESIGN:         CLOSED" in status
                    assert "S02 INSTRUCTIONS:   CLOSED" in status
                    assert "S03.1 RERUN:        READY / NOT_RUN" in status
                    assert "S04 CLASSIFICATION: ACTIVE / PARTIAL" in status
                    assert "CURRENT RENDERER:   pillow-pencil-contact-v11/1" in status
                    assert "RENDERER POLICY:    no additive v12" in status
                    assert "PACKAGE VERSION:    no new RC/version authorized" in status
                    assert "v1.0.3" in status and "latest published stable" in status
                    assert "S01 v11 quality-control failure taxonomy + design       CLOSED" in roadmap
                    assert "S02 instruction graph execution-gate patch              CLOSED" in roadmap
                    assert "S03 fresh-worker visual dogfood                         ACTIVE" in roadmap
                    assert "S04 classify remaining geometry vs material residuals   ACTIVE / PARTIAL" in roadmap
                    assert "No renderer v12 is authorized" in roadmap
                    assert (PLANNING / "V11_QUALITY_CONTROL_REDESIGN.md").is_file()
                    assert (PLANNING / "V11_QUALITY_CONTROL_SLICE_PLAN.md").is_file()
                    assert not (PUBLISH / "v1.0.4.json").exists()
                    assert "CURRENT SOURCE:     1.0.4rc1" not in status
                    assert "RC CANDIDATE:       1.0.4rc1" not in status
                    assert "RC IN MAIN:         1.0.4rc1" not in status
                else:
                    assert "NEXT GATE:          none for v1.0.3 · release CLOSED" in status
            else:
                assert "**Current stable: v1.0.2**" in root_readme
                assert "RELEASE INTENT:" in status and "v1.0.3" in status
                assert "GitHub Release pending" in status
        else:
            assert "**Current stable: v1.0.2**" in root_readme
            assert "STABLE CANDIDATE:" in status and "v1.0.3" in status
            assert "manifest intentionally absent" in status

    assert "R23" in status and "physically retired" in status
    roadmap_lower = roadmap.lower()
    assert "g01" in roadmap_lower and "gesture" in roadmap_lower
    assert "g02" in roadmap_lower and "broad-pencil" in roadmap_lower
    assert "CURRENT MAIN INVARIANTS" in contract
    assert "current `src` contains no installable R23 runtime/legacy namespace" in planning_readme

    if is_stable and "**Current stable: v1.0.3**" in root_readme:
        if active_post_release_design:
            assert "G05 stable freeze + wheel verification                  CLOSED" in roadmap
            assert "G06 explicit publish manifest + publish                 CLOSED" in roadmap
            assert "S01" in roadmap and "CLOSED" in roadmap
            assert "S02" in roadmap and "CLOSED" in roadmap
            assert "S03" in roadmap and "ACTIVE" in roadmap
            assert "V11_QUALITY_CONTROL_REDESIGN.md" in roadmap
            assert "V11_QUALITY_CONTROL_SLICE_PLAN.md" in roadmap
        else:
            assert "### G05 — stable freeze and wheel verification — CLOSED" in roadmap
            assert "### G06 — publish — CLOSED" in roadmap
            assert "NEXT PRODUCT BOTTLENECK" in roadmap and "UNSELECTED" in roadmap
        assert "v1.0.3 release cycle is closed" in planning_readme
        assert "The latest released stable package is **v1.0.3 / A14 / DrawingSession/1.0.3-vnext**" in contract
        assert "Known current defect:" not in contract
        assert "current validation matrix for work **after the published v1.0.3 baseline**" in validation
        assert "## V01 — Gesture mode behavior — CLOSED for v1.0.3" in validation
        assert "## V02 — Render-input parity — CLOSED for v1.0.3" in validation

    stale_current_markers = {
        PLANNING / "README.md": (
            "D01 is the next authorized work",
            "Physical R23 retirement occurs only at R03",
            "The immediate sequence is fresh-worker gesture validation",
            "release/version hardening for the post-v1.0.2 main state",
        ),
        PLANNING / "STATUS.md": (
            "PACKAGE:          1.0.1",
            "STABLE BASELINE:  v1.0.1",
            "NEXT ENGINEERING: fresh sealed D01 validation",
            "R23 remains explicit compatibility only; physical retirement is still a later bounded decision",
            "GitHub Release pending",
        ),
        PLANNING / "ROADMAP.md": (
            "Phase E — fresh integrated validation — NEXT",
            "R03 physical R23 retirement",
            "stable v1.0.1 notes",
            "G05 stable freeze + wheel verification             ACTIVE",
            "G06 explicit publish manifest + publish            NEXT",
            "currently published stable until G06",
        ),
        PLANNING / "CONTRACT.md": (
            "FROZEN FOR D01–D06",
            "Physical R23 retirement occurs only at R03",
            "img2drawing.legacy.r23",
            "Known current defect:",
            "The latest released stable package is v1.0.2",
            "still reports package version 1.0.2",
        ),
        PLANNING / "VALIDATION_RELEASE.md": (
            "Starts only after: **B18 CLOSED",
            "R03 — Physical R23 retirement",
            "The current migration implementation first resumes a `DrawingRun`",
            "current validation matrix for unreleased post-v1.0.2 main",
            "review compatibility impact of all post-v1.0.2 changes",
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

    assert frozen_v102["freeze_id"] == "v1.0.2-A10-2026-09-09"
    assert frozen_v102["package_version"] == "1.0.2"
    assert frozen_v102["public_api"] == "DrawingSession/1.0.2-vnext"
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
