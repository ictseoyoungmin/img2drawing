#!/usr/bin/env python3
"""Verify immutable v1.0.3 stable evidence after mutable main advances."""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

from img2drawing.render.renderer_registry import registered_renderer_identities, resolve_renderer

ROOT = Path(__file__).resolve().parents[2]
RELEASE = ROOT / "dev" / "release" / "vnext"
PUBLISH = ROOT / "dev" / "release" / "publish"
V103_RELEASE_COMMIT = "d6151ba8dfef8dc37ef5cddd24c2c6c974d53976"
V103_RENDERER = ("pillow-pencil-contact-v11", "1")
V103_RENDERER_DIGEST = "e8453d8e1cb9c73998369d10be707c010b49df1e9fb8fb9ee96f7b9b829b39fa"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def main() -> None:
    identities = set(registered_renderer_identities())
    for identity in (
        ("pillow-pencil-contact-v9", "1"),
        ("pillow-pencil-contact-v10", "1"),
        V103_RENDERER,
    ):
        assert identity in identities
    v11 = resolve_renderer(*V103_RENDERER)
    assert v11.contract_digest == V103_RENDERER_DIGEST

    old = load(RELEASE / "CONTRACT_FREEZE.json")
    assert old["freeze_id"] == "v1.0.2-A10-2026-09-09"
    assert old["package_version"] == "1.0.2"

    stable = load(RELEASE / "CONTRACT_FREEZE_V1_0_3.json")
    assert stable["freeze_id"] == "v1.0.3-A14-2026-09-13"
    assert stable["package_version"] == "1.0.3"
    assert stable["public_api"] == "DrawingSession/1.0.3-vnext"
    assert stable["release_revision"] == "A14"
    assert stable["release_slice"] == "v1.0.3_gesture_renderer_quality"
    assert stable["canonical_render_profile"]["renderer_id"] == V103_RENDERER[0]
    assert str(stable["canonical_render_profile"]["renderer_version"]) == V103_RENDERER[1]
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
    assert promotion["package_tree"] == "5758c5efa60d80a0d483bcb3573258e34d609055"
    assert promotion["renderer"]["contract_digest"] == V103_RENDERER_DIGEST
    assert promotion["renderer"]["thin_v10_v11_pixel_exact"] is True
    assert promotion["renderer"]["current_fast_canonical_pixel_exact"] is True
    assert promotion["behavioral_gates"] == {
        "g01_gesture": "PASS_CLOSED", "g02_broad_pencil": "PASS_CLOSED"
    }

    # Stable evidence is anchored to the immutable tag/candidate trees, never mutable HEAD.
    assert git("rev-parse", "v1.0.3^{commit}") == V103_RELEASE_COMMIT
    assert git("rev-parse", "v1.0.3:skills/img2drawing") == promotion["package_tree"]
    assert git("rev-parse", f"{promotion['verified_commit']}:skills/img2drawing") == promotion["package_tree"]

    manifest = load(PUBLISH / "v1.0.3.json")
    assert manifest == {
        "schema": "img2drawing.release.publish.v1",
        "tag": "v1.0.3",
        "title": "img2drawing v1.0.3",
        "notes_file": "docs/releases/v1.0.3.md",
        "package_dir": "skills/img2drawing",
        "assets": [],
    }
    notes = (ROOT / manifest["notes_file"]).read_text(encoding="utf-8")
    assert notes.startswith("# img2drawing v1.0.3")
    assert "pillow-pencil-contact-v11 / 1" in notes
    assert "CONTRACT_FREEZE_V1_0_3.json" in notes

    print("V1_0_3_STABLE_FREEZE_PASS")


if __name__ == "__main__":
    main()
