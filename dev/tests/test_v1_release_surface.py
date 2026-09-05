from __future__ import annotations

import json
from pathlib import Path

import img2drawing


ROOT = Path(__file__).resolve().parents[2]
ENTRY = ROOT / "showcase" / "entries" / "croquis-sniper-girl-astra-v1"
PUBLISH = ROOT / "dev" / "release" / "publish"


def _manifest(version: str) -> dict:
    return json.loads((PUBLISH / f"v{version}.json").read_text(encoding="utf-8"))


def test_current_v1_publish_manifest_matches_package() -> None:
    manifest = _manifest("1.0.1")
    assert manifest["tag"] == f"v{img2drawing.__version__}"
    assert manifest["notes_file"] == "docs/releases/v1.0.1.md"
    assert manifest["package_dir"] == "skills/img2drawing"
    assert manifest["assets"] == []
    assert (ROOT / manifest["notes_file"]).is_file()


def test_historical_v100_demo_manifest_and_real_assets_remain_available() -> None:
    manifest = _manifest("1.0.0")
    assert manifest["tag"] == "v1.0.0"
    assert manifest["notes_file"] == "docs/releases/v1.0.0.md"
    assert manifest["assets"] == [
        "showcase/entries/croquis-sniper-girl-astra-v1/ref-vs-drawing.jpg",
        "showcase/entries/croquis-sniper-girl-astra-v1/timelapse.gif",
    ]
    for relative in manifest["assets"]:
        path = ROOT / relative
        assert path.is_file(), relative
        # Protect against accidentally reintroducing placeholder-sized showcase binaries.
        assert path.stat().st_size > 10_000, relative


def test_v1_featured_demo_links_resolve_to_committed_artifacts() -> None:
    root_readme = (ROOT / "README.md").read_text(encoding="utf-8")
    entry_readme = (ENTRY / "README.md").read_text(encoding="utf-8")
    release_notes = (ROOT / "docs" / "releases" / "v1.0.0.md").read_text(encoding="utf-8")

    for document in (root_readme, entry_readme, release_notes):
        assert "ref-vs-drawing.png" not in document
        assert "ref-vs-drawing.jpg" in document
        assert "timelapse.gif" in document

    assert "docs/releases/v1.0.1.md" in root_readme
    assert (ROOT / "docs" / "releases" / "v1.0.1.md").is_file()


def test_release_publisher_reads_version_without_importing_runtime() -> None:
    workflow = (ROOT / ".github" / "workflows" / "publish-release.yml").read_text(encoding="utf-8")
    assert "runpy.run_path" in workflow
    assert "_version.py" in workflow
    assert "import img2drawing" not in workflow
