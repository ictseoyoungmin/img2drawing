from __future__ import annotations

import json
from pathlib import Path

import img2drawing


ROOT = Path(__file__).resolve().parents[2]
ENTRY = ROOT / "showcase" / "entries" / "croquis-sniper-girl-astra-v1"
PUBLISH = ROOT / "dev" / "release" / "publish"


def _manifest(version: str) -> dict:
    return json.loads((PUBLISH / f"v{version}.json").read_text(encoding="utf-8"))


def test_v102_manifest_remains_historical_authority_as_v103_publish_intent_opens() -> None:
    v102 = _manifest("1.0.2")
    assert v102["tag"] == "v1.0.2"
    assert v102["notes_file"] == "docs/releases/v1.0.2.md"
    assert v102["package_dir"] == "skills/img2drawing"
    assert v102["assets"] == []
    assert (ROOT / v102["notes_file"]).is_file()

    v103 = _manifest("1.0.3")
    assert v103 == {
        "schema": "img2drawing.release.publish.v1",
        "tag": "v1.0.3",
        "title": "img2drawing v1.0.3",
        "notes_file": "docs/releases/v1.0.3.md",
        "package_dir": "skills/img2drawing",
        "assets": [],
    }
    assert (ROOT / v103["notes_file"]).is_file()


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
        assert path.stat().st_size > 10_000, relative


def test_v1_featured_demo_links_and_release_notes_resolve() -> None:
    root_readme = (ROOT / "README.md").read_text(encoding="utf-8")
    entry_readme = (ENTRY / "README.md").read_text(encoding="utf-8")
    release_notes = (ROOT / "docs" / "releases" / "v1.0.0.md").read_text(encoding="utf-8")
    for document in (root_readme, entry_readme, release_notes):
        assert "ref-vs-drawing.png" not in document
        assert "ref-vs-drawing.jpg" in document
        assert "timelapse.gif" in document
    assert (ROOT / "docs" / "releases" / "v1.0.1.md").is_file()
    assert (ROOT / "docs" / "releases" / "v1.0.2.md").is_file()
    assert (ROOT / "docs" / "releases" / "v1.0.3rc1.md").is_file()
    assert (ROOT / "docs" / "releases" / "v1.0.3rc2.md").is_file()
    assert (ROOT / "docs" / "releases" / "v1.0.3rc3.md").is_file()
    assert (ROOT / "docs" / "releases" / "v1.0.3.md").is_file()


def test_release_publisher_reads_version_without_importing_runtime() -> None:
    workflow = (ROOT / ".github" / "workflows" / "publish-release.yml").read_text(encoding="utf-8")
    assert "runpy.run_path" in workflow
    assert "_version.py" in workflow
    assert "import img2drawing" not in workflow


def test_unreleased_development_version_has_no_publish_manifest() -> None:
    version = img2drawing.__version__
    manifest = PUBLISH / f"v{version}.json"
    if ".dev" in version:
        # A development version must never trigger the publish workflow.
        assert not manifest.exists()
        assert sorted(p.stem for p in PUBLISH.glob("v*.json"))[-1] == "v1.0.3"
    else:
        assert json.loads(manifest.read_text(encoding="utf-8"))["tag"] == f"v{version}"


def test_retired_s09_streaming_test_is_not_active_ci_surface() -> None:
    assert not (ROOT / "dev" / "tests" / "test_streaming_timelapse_resume.py").exists()
    assert not (ROOT / "skills" / "img2drawing" / "src" / "img2drawing" / "provenance" / "streaming.py").exists()
    legacy = ROOT / "dev" / "legacy" / "post_1_0_1" / "s09_streaming"
    assert (legacy / "streaming.py").is_file()
    assert (legacy / "test_streaming_timelapse_resume.py").is_file()
