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
    identities = registered_renderer_identities()
    assert ("pillow-pencil-contact-v9", "1") in identities
    assert ("pillow-pencil-contact-v10", "1") in identities
    assert ("pillow-pencil-contact-v11", "1") in identities

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
        "pillow-pencil-contact-v9/1",
        "pillow-pencil-contact-v10/1",
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
    assert promotion["verified_commit"] == "13826f4fd29ac0c021b2837b3f89bc9694e3ca75"
    assert promotion["verified_root_tree"] == "a2605f8d9e0303f8554584b6b657e5211de615dd"
    assert promotion["package_tree"] == "934930f51457c2e075eb5e8ceb8341d5cf65105c"
    assert git("rev-parse", "HEAD:skills/img2drawing") == promotion["package_tree"]
    assert promotion["ci"]["run_id"] == 34748393631
    assert promotion["ci"]["conclusion"] == "success"
    artifact = promotion["artifact"]
    assert artifact["artifact_id"] == 10314573024
    assert artifact["artifact_zip_sha256"] == "dc88d28b03253f25cc95a1d7c3838ed9e6575577d798ecbbd55375274309f6a6"
    assert artifact["wheel_filename"] == "img2drawing-1.0.3-py3-none-any.whl"
    assert artifact["wheel_sha256"] == "c1d1b2c764b57e14711cfc8a9d4198288b5832be96c7c3ec4b173b996fcfa703"
    assert artifact["metadata_name"] == "img2drawing"
    assert artifact["metadata_version"] == "1.0.3"
    assert promotion["renderer"]["contract_digest"] == renderer.contract_digest
    assert promotion["renderer"]["thin_v10_v11_pixel_exact"] is True
    assert promotion["renderer"]["current_fast_canonical_pixel_exact"] is True
    assert promotion["behavioral_gates"] == {
        "g01_gesture": "PASS_CLOSED",
        "g02_broad_pencil": "PASS_CLOSED",
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
        assert payload["tag"] == "v1.0.3"
        assert payload["notes_file"] == "docs/releases/v1.0.3.md"
        assert payload["package_dir"] == "skills/img2drawing"
        assert payload["assets"] == []

    print("V1_0_3_STABLE_FREEZE_PASS")


if __name__ == "__main__":
    main()
