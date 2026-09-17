from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _json(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_codex_plugin_manifest_points_at_skill_and_icon() -> None:
    manifest = _json(".codex-plugin/plugin.json")
    assert manifest["name"] == "img2drawing"
    assert manifest["version"] == "1.0.3"
    assert manifest["license"] == "Apache-2.0"
    assert manifest["skills"] == "./skills/"

    interface = manifest["interface"]
    assert interface["displayName"] == "img2drawing"
    assert interface["composerIcon"] == "./skills/img2drawing/assets/icon.svg"
    assert interface["logo"] == "./skills/img2drawing/assets/icon.svg"
    assert (ROOT / interface["logo"]).is_file()


def test_claude_plugin_and_marketplace_point_at_img2drawing_skill() -> None:
    plugin = _json(".claude-plugin/plugin.json")
    marketplace = _json(".claude-plugin/marketplace.json")

    assert plugin["name"] == "img2drawing"
    assert plugin["version"] == "1.0.3"
    assert plugin["license"] == "Apache-2.0"
    assert marketplace["name"] == "img2drawing"
    assert marketplace["plugins"] == [
        {
            "name": "img2drawing",
            "source": "./skills/",
            "description": "Observation-first drawing with explicit strokes, visual QA, correction, and replay without image generation.",
        }
    ]


def test_codex_workspace_marketplace_is_repo_local_and_available() -> None:
    marketplace = _json(".agents/plugins/marketplace.json")
    assert marketplace["name"] == "img2drawing"
    assert marketplace["interface"]["displayName"] == "img2drawing"

    [plugin] = marketplace["plugins"]
    assert plugin["name"] == "img2drawing"
    assert plugin["source"] == {"source": "local", "path": "./skills/"}
    assert plugin["policy"] == {
        "installation": "AVAILABLE",
        "authentication": "ON_INSTALL",
    }
