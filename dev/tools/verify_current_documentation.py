#!/usr/bin/env python3
"""Verify current-facing documentation against generic release and package authority."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PLANNING = ROOT / "dev" / "planning" / "vnext"
RELEASE = ROOT / "dev" / "release" / "vnext"
PUBLISH = ROOT / "dev" / "release" / "publish"
PACKAGE = ROOT / "skills" / "img2drawing"


def _text(path: Path) -> str:
    assert path.is_file(), f"missing current-facing document: {path.relative_to(ROOT)}"
    return path.read_text(encoding="utf-8")


def _json(path: Path) -> dict:
    value = json.loads(_text(path))
    assert isinstance(value, dict), path
    return value


def _package_version() -> str:
    text = _text(PACKAGE / "src" / "img2drawing" / "_version.py")
    match = re.search(r'^__version__ = "([^"]+)"$', text, flags=re.MULTILINE)
    assert match, "current package version declaration missing"
    return match.group(1)


def _updated_date(text: str, name: str) -> str:
    match = re.search(r"^Updated: (\d{4}-\d{2}-\d{2})$", text, flags=re.MULTILINE)
    assert match, f"{name} must declare an Updated date"
    return match.group(1)


def _validate_publish_manifest(path: Path) -> dict:
    manifest = _json(path)
    version = path.stem.removeprefix("v")
    assert manifest["schema"] == "img2drawing.release.publish.v1", path
    assert manifest["tag"] == f"v{version}", path
    assert manifest["title"] == f"img2drawing v{version}", path
    assert manifest["package_dir"] == "skills/img2drawing", path
    notes = ROOT / manifest["notes_file"]
    assert notes.is_file(), notes
    assert _text(notes).startswith(f"# img2drawing v{version}\n"), notes
    for asset in manifest.get("assets", []):
        assert (ROOT / asset).is_file(), asset
    return manifest


def main() -> None:
    assert not (ROOT / "GATES.md").exists(), "retired root GATES.md reappeared"
    assert not (ROOT / "HANDOFF.md").exists(), "retired root HANDOFF.md reappeared"

    version = _package_version()
    root_readme = _text(ROOT / "README.md")
    changelog = _text(ROOT / "CHANGELOG.md")
    planning_readme = _text(PLANNING / "README.md")
    status = _text(PLANNING / "STATUS.md")
    roadmap = _text(PLANNING / "ROADMAP.md")
    contract = _text(PLANNING / "CONTRACT.md")
    attention_plan = _text(PLANNING / "INSTRUCTION_GRAPH_ATTENTION_ARCHITECTURE_PLAN.md")

    assert _updated_date(status, "STATUS.md") == _updated_date(roadmap, "ROADMAP.md")
    assert "canonical point-in-time development status" in status
    assert "canonical **point-in-time current-state authority**" in roadmap
    assert "does not create a second current-state truth" in roadmap
    assert "Status: Slice A CLOSED · Slice B CLOSED · Slice C CLOSED · Slice D CLOSED · Slice E CLOSED" in attention_plan

    current_manifest_path = PUBLISH / f"v{version}.json"
    assert current_manifest_path.is_file(), (
        f"stable package version {version} requires dev/release/publish/v{version}.json"
    )
    current_manifest = _validate_publish_manifest(current_manifest_path)

    # Every retained publish record is internally self-consistent and immutable by version.
    manifests = sorted(PUBLISH.glob("v*.json"))
    assert manifests, "no release publish manifests"
    for manifest_path in manifests:
        _validate_publish_manifest(manifest_path)

    assert f"**Current stable: v{version}**" in root_readme
    assert f"version-v{version}-" in root_readme
    assert f"## v{version} —" in changelog
    assert f"PUBLISHED STABLE:   v{version}" in status
    assert f"CURRENT SOURCE:     {version}" in status
    assert f"PACKAGE VERSION:    {version}" in status
    assert f"v{version}" in roadmap
    assert f"GitHub Release v{version}" in planning_readme
    assert f"v{version} is the latest published stable" in contract

    codex = _json(ROOT / ".codex-plugin" / "plugin.json")
    claude = _json(ROOT / ".claude-plugin" / "plugin.json")
    assert codex["version"] == version
    assert claude["version"] == version

    freeze_assets = [
        ROOT / asset
        for asset in current_manifest.get("assets", [])
        if Path(asset).name.startswith("CONTRACT_FREEZE")
    ]
    assert freeze_assets, "current stable release must attach a contract freeze"
    for freeze_path in freeze_assets:
        freeze = _json(freeze_path)
        assert freeze["package_version"] == version
        assert freeze["canonical_render_profile"]["renderer_id"] == "img2drawing-pencil"
        assert str(freeze["canonical_render_profile"]["renderer_version"]) == "11"
        assert len(freeze["renderer_authority"]["current_contract_digest"]) == 64
        runtime = freeze.get("runtime_capabilities")
        assert runtime == {
            "schema": "img2drawing.runtime.capabilities.v2",
            "authoring_operations": ["draw", "replace-stroke", "soft-lift", "delete-stroke"],
            "output_operations": ["inspect", "render", "replay", "timelapse"],
            "compatibility_alias": "supported_authoring_operations -> supported_operations",
        }

    # Historical release authority remains present and version-specific.
    for required in (
        RELEASE / "CONTRACT_FREEZE.json",
        RELEASE / "CONTRACT_FREEZE_V1_0_3.json",
        RELEASE / "CONTRACT_FREEZE_V1_1_0.json",
        PUBLISH / "v1.0.3.json",
        PUBLISH / "v1.1.0.json",
    ):
        assert required.is_file(), required

    # The accepted visual-proof limit remains explicit; maintenance must not inflate it.
    assert "S03 CAMPAIGN:      PASS / USER_ACCEPTED" in status
    assert "class runs remain NOT_RUN" in status
    assert "S03 fresh-worker visual dogfood" in roadmap
    assert "no class-level PASS claimed" in roadmap

    # Current control-plane text must not regress to superseded release sequencing.
    for marker in (
        "ACTIVE BOTTLENECK:  S07",
        "S07 mechanical release validation                       ACTIVE",
        "Current stable: v1.0.3",
        "CURRENT SOURCE:     1.0.4rc1",
        "RC CANDIDATE:       1.0.4rc1",
        "RC IN MAIN:         1.0.4rc1",
    ):
        assert marker not in status + "\n" + roadmap + "\n" + root_readme, marker

    workflow = _text(ROOT / ".github" / "workflows" / "ci.yml")
    assert "verify_package_boundary.py" in workflow
    assert "verify_vnext_b17.py" not in workflow
    assert "refs/heads/release/1.0.3-rc" not in workflow
    assert "refs/heads/release/1.0.3-stable" not in workflow

    # The release notes named by the current manifest are the human-facing release authority.
    notes = _text(ROOT / current_manifest["notes_file"])
    assert f"Release date: 2026-09-29" in notes
    assert "img2drawing-pencil / 11" in notes
    assert "renderer pixels" in notes.lower() or "pixel" in notes.lower()

    print(f"CURRENT_DOCUMENTATION_CONSISTENCY_PASS ({version})")


if __name__ == "__main__":
    main()
