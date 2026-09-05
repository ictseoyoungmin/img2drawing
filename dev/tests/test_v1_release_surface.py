from __future__ import annotations

import json
from pathlib import Path

import img2drawing


ROOT = Path(__file__).resolve().parents[2]
ENTRY = ROOT / "showcase" / "entries" / "croquis-sniper-girl-astra-v1"


def test_v1_publish_manifest_matches_package_and_assets_exist() -> None:
    manifest = json.loads((ROOT / "dev" / "release" / "publish" / "v1.0.0.json").read_text(encoding="utf-8"))
    assert manifest["tag"] == f"v{img2drawing.__version__}"
    assert manifest["notes_file"] == "docs/releases/v1.0.0.md"
    assert manifest["assets"] == [
        "showcase/entries/croquis-sniper-girl-astra-v1/ref-vs-drawing.jpg",
        "showcase/entries/croquis-sniper-girl-astra-v1/timelapse.gif",
    ]
    for relative in manifest["assets"]:
        assert (ROOT / relative).is_file(), relative


def test_v1_featured_demo_links_resolve_to_committed_artifacts() -> None:
    root_readme = (ROOT / "README.md").read_text(encoding="utf-8")
    entry_readme = (ENTRY / "README.md").read_text(encoding="utf-8")
    release_notes = (ROOT / "docs" / "releases" / "v1.0.0.md").read_text(encoding="utf-8")

    for document in (root_readme, entry_readme, release_notes):
        assert "ref-vs-drawing.png" not in document
        assert "ref-vs-drawing.jpg" in document
        assert "timelapse.gif" in document
