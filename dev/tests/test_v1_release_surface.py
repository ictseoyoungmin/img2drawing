from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import img2drawing
import pytest


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
    assert (ROOT / "docs" / "releases" / "v1.1.0.md").is_file()
    assert (ROOT / "docs" / "releases" / "v1.1.1.md").is_file()


def test_release_publisher_reads_version_without_importing_runtime() -> None:
    workflow = (ROOT / ".github" / "workflows" / "publish-release.yml").read_text(encoding="utf-8")
    assert "runpy.run_path" in workflow
    assert "_version.py" in workflow
    assert "import img2drawing" not in workflow


def test_current_stable_version_has_matching_publish_manifest() -> None:
    version = img2drawing.__version__
    manifest = PUBLISH / f"v{version}.json"
    assert ".dev" not in version
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    assert payload["tag"] == f"v{version}"
    assert payload["title"] == f"img2drawing v{version}"
    assert (ROOT / payload["notes_file"]).is_file()
    for asset in payload["assets"]:
        assert (ROOT / asset).is_file()


def test_v110_manifest_remains_immutable_historical_authority() -> None:
    assert _manifest("1.1.0") == {
        "schema": "img2drawing.release.publish.v1",
        "tag": "v1.1.0",
        "title": "img2drawing v1.1.0",
        "notes_file": "docs/releases/v1.1.0.md",
        "package_dir": "skills/img2drawing",
        "assets": ["dev/release/vnext/CONTRACT_FREEZE_V1_1_0.json"],
    }


def test_retired_s09_streaming_test_is_not_active_ci_surface() -> None:
    assert not (ROOT / "dev" / "tests" / "test_streaming_timelapse_resume.py").exists()
    assert not (ROOT / "skills" / "img2drawing" / "src" / "img2drawing" / "provenance" / "streaming.py").exists()
    legacy = ROOT / "dev" / "legacy" / "post_1_0_1" / "s09_streaming"
    assert (legacy / "streaming.py").is_file()
    assert (legacy / "test_streaming_timelapse_resume.py").is_file()


def test_readme_does_not_reaccumulate_release_history() -> None:
    path = ROOT / "dev/tools/verify_current_documentation.py"
    spec = importlib.util.spec_from_file_location("readme_policy", path)
    policy = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(policy)
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    policy.verify_readme_scope(readme)
    with pytest.raises(AssertionError, match="version-specific"):
        policy.verify_readme_scope(readme + "\n## v1.0.0 — Old release\n")
    with pytest.raises(AssertionError, match="budget"):
        policy.verify_readme_scope(readme + "x" * 6501)


def test_release_publisher_builds_separate_skill_zip() -> None:
    workflow = (ROOT / ".github/workflows/publish-release.yml").read_text(encoding="utf-8")
    assert 'python dev/tools/build_skill_zip.py --package-dir "$package_dir"' in workflow
    assert 'img2drawing-skill-$version.zip' in workflow
    assert workflow.index('python dev/tools/build_skill_zip.py') < workflow.index('assets=(dist/*)')


def test_current_runtime_freeze_matches_live_authority_and_rejects_drift():
    path = ROOT / "dev/tools/verify_current_documentation.py"
    spec = importlib.util.spec_from_file_location("current_release_policy", path)
    policy = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(policy)
    manifest = _manifest(img2drawing.__version__)
    freeze_path = next(ROOT / asset for asset in manifest["assets"] if Path(asset).name.startswith("CONTRACT_FREEZE"))
    frozen = json.loads(freeze_path.read_text(encoding="utf-8"))
    policy.verify_runtime_freeze(frozen)
    for key, value, match in (
        ("gif_disposal", 2 if frozen["canonical_render_profile"]["gif_disposal"] == 1 else 1, "profile drift"),
        ("renderer_contract_digest", "0" * 64, "profile drift"),
    ):
        modified = json.loads(json.dumps(frozen))
        modified["canonical_render_profile"][key] = value
        with pytest.raises(AssertionError, match=match):
            policy.verify_runtime_freeze(modified)
    modified = json.loads(json.dumps(frozen))
    modified["renderer_authority"]["current_contract_digest"] = "0" * 64
    with pytest.raises(AssertionError, match="digest drift"):
        policy.verify_runtime_freeze(modified)
    modified = json.loads(json.dumps(frozen))
    modified["root_exports"].append("nonexistent_export")
    with pytest.raises(AssertionError, match="export drift"):
        policy.verify_runtime_freeze(modified)


@pytest.fixture
def mixed_runtime_freeze():
    from img2drawing import DrawingSession, RenderProfile, authoring
    from img2drawing.render.artifact import RENDER_ARTIFACT_SCHEMA

    path = ROOT / "dev/tools/verify_current_documentation.py"
    spec = importlib.util.spec_from_file_location("mixed_release_policy", path)
    policy = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(policy)
    historical = json.loads((ROOT / "dev/release/vnext/CONTRACT_FREEZE_V1_3_1.json").read_text())
    # The old published freeze stays valid without new mixed fields or exports.
    policy.verify_runtime_freeze(historical)
    frozen = json.loads(json.dumps(historical))
    frozen["package_version"] = "1.4.0"
    frozen["persisted_schemas"]["render_artifact"] = RENDER_ARTIFACT_SCHEMA
    canvas = frozen["canonical_render_profile"]
    width, height = canvas["canvas_width"], canvas["canvas_height"]
    frozen["mixed_media"] = {
        "default_profile": "mixed-media-v3",
        "profiles": {
            "mixed-media-v1": RenderProfile.mixed_media(width, height, styled_paths=False).to_dict(),
            "mixed-media-v2": RenderProfile.mixed_media(width, height, screentones=False).to_dict(),
            "mixed-media-v3": RenderProfile.mixed_media(width, height).to_dict(),
        },
    }
    frozen["authoring_exports"] = sorted(authoring.__all__)
    frozen["drawing_session_members"] = sorted(name for name in dir(DrawingSession) if not name.startswith("_"))
    return policy, frozen


def test_mixed_freeze_matches_all_live_profile_selections(mixed_runtime_freeze):
    policy, frozen = mixed_runtime_freeze
    policy.verify_runtime_freeze(frozen)


@pytest.mark.parametrize("schema", [None, "img2drawing.vnext.render_artifact.v1"])
def test_mixed_freeze_rejects_missing_or_stale_render_artifact_schema(mixed_runtime_freeze, schema):
    policy, frozen = mixed_runtime_freeze
    if schema is None:
        del frozen["persisted_schemas"]["render_artifact"]
    else:
        frozen["persisted_schemas"]["render_artifact"] = schema
    with pytest.raises(AssertionError, match="render artifact schema drift"):
        policy.verify_runtime_freeze(frozen)


@pytest.mark.parametrize("version", ["1.4.0", "1.5.0", "2.0.0"])
def test_mixed_freeze_authority_cannot_be_omitted(mixed_runtime_freeze, version):
    policy, frozen = mixed_runtime_freeze
    frozen["package_version"] = version
    del frozen["mixed_media"]
    with pytest.raises(AssertionError, match="mixed-media authority missing"):
        policy.verify_runtime_freeze(frozen)


@pytest.mark.parametrize("version,key,value", [
    ("mixed-media-v1", "renderer_contract_digest", "0" * 64),
    ("mixed-media-v2", "renderer_id", "img2drawing-other"),
    ("mixed-media-v3", "gif_disposal", 2),
])
def test_mixed_freeze_rejects_profile_drift(mixed_runtime_freeze, version, key, value):
    policy, frozen = mixed_runtime_freeze
    frozen["mixed_media"]["profiles"][version][key] = value
    with pytest.raises(AssertionError, match="mixed render profile drift"):
        policy.verify_runtime_freeze(frozen)


@pytest.mark.parametrize("change", ["missing", "extra", "default"])
def test_mixed_freeze_requires_complete_profile_set_and_default(mixed_runtime_freeze, change):
    policy, frozen = mixed_runtime_freeze
    if change == "missing":
        del frozen["mixed_media"]["profiles"]["mixed-media-v2"]
    elif change == "extra":
        frozen["mixed_media"]["profiles"]["mixed-media-v4"] = {}
    else:
        frozen["mixed_media"]["default_profile"] = "mixed-media-v2"
    with pytest.raises(AssertionError, match="mixed render profile drift"):
        policy.verify_runtime_freeze(frozen)


@pytest.mark.parametrize("surface,member,match", [
    ("authoring_exports", "g_pen", "authoring export drift"),
    ("drawing_session_members", "finish", "session surface drift"),
])
def test_mixed_freeze_rejects_stale_public_surface(mixed_runtime_freeze, surface, member, match):
    policy, frozen = mixed_runtime_freeze
    frozen[surface].remove(member)
    with pytest.raises(AssertionError, match=match):
        policy.verify_runtime_freeze(frozen)
