#!/usr/bin/env python3
"""Verify the selected v1.0.3 stable contract before publication."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

import img2drawing
from img2drawing._version import PUBLIC_API, RELEASE_REVISION, RELEASE_SLICE
from img2drawing.render.renderer_registry import current_renderer, registered_renderer_identities
from img2drawing.vnext import DRAWING_MODES

ROOT = Path(__file__).resolve().parents[2]
RELEASE = ROOT / "dev" / "release" / "vnext"
PUBLISH = ROOT / "dev" / "release" / "publish"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def main() -> None:
    assert img2drawing.__version__ == "1.0.3"
    assert PUBLIC_API == "DrawingSession/1.0.3-vnext"
    assert RELEASE_REVISION == "A14"
    assert RELEASE_SLICE == "v1.0.3_gesture_renderer_quality"
    assert "gesture" in DRAWING_MODES

    identities = set(registered_renderer_identities())
    for identity in (
        ("pillow-pencil-contact-v9", "1"),
        ("pillow-pencil-contact-v10", "1"),
        ("pillow-pencil-contact-v11", "1"),
    ):
        assert identity in identities
    renderer = current_renderer()
    assert renderer.identity == ("pillow-pencil-contact-v11", "1")
    assert renderer.contract_digest == "e8453d8e1cb9c73998369d10be707c010b49df1e9fb8fb9ee96f7b9b829b39fa"

    old = load(RELEASE / "CONTRACT_FREEZE.json")
    assert old["freeze_id"] == "v1.0.2-A10-2026-09-09"
    assert old["package_version"] == "1.0.2"

    stable = load(RELEASE / "CONTRACT_FREEZE_V1_0_3.json")
    assert stable["freeze_id"] == "v1.0.3-A14-2026-09-13"
    assert stable["package_version"] == "1.0.3"
    assert stable["public_api"] == PUBLIC_API
    assert stable["release_revision"] == RELEASE_REVISION
    assert stable["release_slice"] == RELEASE_SLICE
    assert stable["canonical_render_profile"]["renderer_id"] == renderer.renderer_id
    assert str(stable["canonical_render_profile"]["renderer_version"]) == renderer.renderer_version
    assert stable["renderer_authority"]["current_contract_digest"] == renderer.contract_digest
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
    assert promotion["release_slice"] == RELEASE_SLICE
    assert promotion["verified_branch"] == "release/1.0.3-stable"
    assert promotion["verified_commit"] == "0de885e6d3f2ed6ac857c46e60875cc8c5c9f727"
    assert promotion["verified_root_tree"] == "996836ef4c2188ad39e621550575e0d9780d288f"
    assert promotion["package_tree"] == "5758c5efa60d80a0d483bcb3573258e34d609055"
    assert git("show", "-s", "--format=%T", promotion["verified_commit"]) == promotion["verified_root_tree"]
    assert git("rev-parse", f"{promotion['verified_commit']}:skills/img2drawing") == promotion["package_tree"]
    assert git("rev-parse", "HEAD:skills/img2drawing") == promotion["package_tree"]

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
    assert promotion["renderer"]["contract_digest"] == renderer.contract_digest
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

    g01 = (ROOT / "dev" / "dogfood" / "g01-gesture-rc2" / "README.md").read_text(encoding="utf-8")
    g02 = (ROOT / "dev" / "dogfood" / "g02-broad-pencil-v11" / "README.md").read_text(encoding="utf-8")
    assert "PASS" in g01 and "CLOSED" in g01
    assert "PASS / CLOSED" in g02

    notes = (ROOT / "docs" / "releases" / "v1.0.3.md").read_text(encoding="utf-8")
    assert notes.startswith("# img2drawing v1.0.3")
    assert "pillow-pencil-contact-v11 / 1" in notes
    assert "CONTRACT_FREEZE_V1_0_3.json" in notes

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

    print("V1_0_3_STABLE_FREEZE_PASS")


if __name__ == "__main__":
    main()
