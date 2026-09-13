#!/usr/bin/env python3
"""Verify immutable v1.0.3 stable evidence independently of mutable HEAD."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RELEASE = ROOT / "dev" / "release" / "vnext"
PUBLISH = ROOT / "dev" / "release" / "publish"

V103_TAG = "v1.0.3"
V103_RELEASE_COMMIT = "d6151ba8dfef8dc37ef5cddd24c2c6c974d53976"
V103_PACKAGE_TREE = "5758c5efa60d80a0d483bcb3573258e34d609055"
V103_RENDERER_DIGEST = "e8453d8e1cb9c73998369d10be707c010b49df1e9fb8fb9ee96f7b9b829b39fa"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def git_show(ref: str, path: str) -> str:
    return git("show", f"{ref}:{path}")


def main() -> None:
    # Historical release identity is owned by the immutable tag, not by current source.
    tag_commit = git("rev-list", "-n", "1", V103_TAG)
    assert tag_commit == V103_RELEASE_COMMIT
    assert git("rev-parse", f"{V103_TAG}:skills/img2drawing") == V103_PACKAGE_TREE

    tagged_version = git_show(V103_TAG, "skills/img2drawing/src/img2drawing/_version.py")
    assert '__version__ = "1.0.3"' in tagged_version
    assert 'RELEASE_REVISION = "A14"' in tagged_version
    assert 'RELEASE_SLICE = "v1.0.3_gesture_renderer_quality"' in tagged_version

    tagged_registry = git_show(V103_TAG, "skills/img2drawing/src/img2drawing/render/renderer_registry.py")
    assert 'pillow-pencil-contact-v11' in tagged_registry
    assert '_CURRENT_IDENTITY' in tagged_registry

    old = load(RELEASE / "CONTRACT_FREEZE.json")
    assert old["freeze_id"] == "v1.0.2-A10-2026-09-09"
    assert old["package_version"] == "1.0.2"

    stable = load(RELEASE / "CONTRACT_FREEZE_V1_0_3.json")
    assert stable["freeze_id"] == "v1.0.3-A14-2026-09-13"
    assert stable["package_version"] == "1.0.3"
    assert stable["public_api"] == "DrawingSession/1.0.3-vnext"
    assert stable["release_revision"] == "A14"
    assert stable["release_slice"] == "v1.0.3_gesture_renderer_quality"
    assert stable["canonical_render_profile"]["renderer_id"] == "pillow-pencil-contact-v11"
    assert str(stable["canonical_render_profile"]["renderer_version"]) == "1"
    assert stable["renderer_authority"]["current_contract_digest"] == V103_RENDERER_DIGEST
    assert stable["renderer_authority"]["historical_replay"] == [
        "pillow-pencil-contact-v9/1", "pillow-pencil-contact-v10/1"
    ]
    assert stable["renderer_authority"]["thin_v10_v11_exact"] is True
    assert stable["renderer_authority"]["current_fast_canonical_exact"] is True
    assert "gesture" in stable["intent_axes"]["drawing_modes"]

    promotion = load(RELEASE / "V1_0_3_STABLE_PROMOTION.json")
    assert promotion["schema"] == "img2drawing.v1_0_3_stable_promotion.v1"
    assert promotion["state"] == "STABLE_WHEEL_VERIFIED"
    assert promotion["version"] == "1.0.3"
    assert promotion["release_revision"] == "A14"
    assert promotion["release_slice"] == "v1.0.3_gesture_renderer_quality"
    assert promotion["verified_branch"] == "release/1.0.3-stable"
    assert promotion["verified_commit"] == "0de885e6d3f2ed6ac857c46e60875cc8c5c9f727"
    assert promotion["verified_root_tree"] == "996836ef4c2188ad39e621550575e0d9780d288f"
    assert promotion["package_tree"] == V103_PACKAGE_TREE
    assert git("show", "-s", "--format=%T", promotion["verified_commit"]) == promotion["verified_root_tree"]
    assert git("rev-parse", f"{promotion['verified_commit']}:skills/img2drawing") == promotion["package_tree"]
    assert git("rev-parse", f"{V103_TAG}:skills/img2drawing") == promotion["package_tree"]

    assert promotion["ci"] == {
        "workflow": "img2drawing-ci",
        "run_id": 34749311565,
        "conclusion": "success",
    }
    artifact = promotion["artifact"]
    assert artifact == {
        "artifact_id": 10315122558,
        "artifact_name": "img2drawing-1.0.3-stable-candidate-0de885e6d3f2ed6ac857c46e60875cc8c5c9f727",
        "artifact_zip_sha256": "2c7650e252b2b2f253630724bd35a30c348bd3114eebf034e45ec4f2cbdfe04a",
        "wheel_filename": "img2drawing-1.0.3-py3-none-any.whl",
        "wheel_sha256": "eaecfeb08100640211d3de73ea6dcfd1557d097c85318c814e217a3eb4265567",
        "metadata_name": "img2drawing",
        "metadata_version": "1.0.3",
    }
    assert promotion["renderer"]["contract_digest"] == V103_RENDERER_DIGEST
    assert promotion["renderer"]["thin_v10_v11_pixel_exact"] is True
    assert promotion["renderer"]["current_fast_canonical_pixel_exact"] is True
    assert promotion["renderer"]["historical_replay"] == [
        "pillow-pencil-contact-v9/1", "pillow-pencil-contact-v10/1"
    ]
    assert promotion["behavioral_gates"] == {
        "g01_gesture": "PASS_CLOSED", "g02_broad_pencil": "PASS_CLOSED"
    }
    assert promotion["publication"] == {
        "manifest_present_when_measured": False,
        "authorized_next_step": "ADD_V1_0_3_PUBLISH_MANIFEST",
    }

    # Historical dogfood and release notes are read from the release tag where possible.
    tagged_g01 = git_show(V103_TAG, "dev/dogfood/g01-gesture-rc2/README.md")
    tagged_g02 = git_show(V103_TAG, "dev/dogfood/g02-broad-pencil-v11/README.md")
    assert "PASS" in tagged_g01 and "CLOSED" in tagged_g01
    assert "PASS / CLOSED" in tagged_g02

    tagged_notes = git_show(V103_TAG, "docs/releases/v1.0.3.md")
    assert tagged_notes.startswith("# img2drawing v1.0.3")
    assert "pillow-pencil-contact-v11 / 1" in tagged_notes
    assert "CONTRACT_FREEZE_V1_0_3.json" in tagged_notes

    manifest = PUBLISH / "v1.0.3.json"
    if manifest.exists():
        payload = load(manifest)
        assert payload == {
            "schema": "img2drawing.release.publish.v1",
            "tag": "v1.0.3",
            "title": "img2drawing v1.0.3",
            "notes_file": "docs/releases/v1.0.3.md",
            "package_dir": "skills/img2drawing",
            "assets": [],
        }

    # Deliberately no HEAD package-tree equality assertion here. Post-release development is
    # expected to change current source/instructions while the tagged package remains immutable.
    print("V1_0_3_STABLE_FREEZE_PASS")


if __name__ == "__main__":
    main()
