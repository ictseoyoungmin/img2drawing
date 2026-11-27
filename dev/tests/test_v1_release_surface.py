from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import textwrap

import img2drawing
import pytest


ROOT = Path(__file__).resolve().parents[2]
ENTRY = ROOT / "showcase" / "entries" / "croquis-sniper-girl-astra-v1"
PUBLISH = ROOT / "dev" / "release" / "publish"


def _manifest(version: str) -> dict:
    return json.loads((PUBLISH / f"v{version}.json").read_text(encoding="utf-8"))


def _policy():
    path = ROOT / "dev/tools/verify_current_documentation.py"
    spec = importlib.util.spec_from_file_location("release_surface_policy", path)
    policy = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(policy)
    return policy


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
    context = _policy().release_context()
    assert context["package_version"] == img2drawing.__version__
    version = context["published_stable"]
    manifest = PUBLISH / f"v{version}.json"
    assert _policy().STABLE_VERSION.fullmatch(version)
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
    freeze_path = policy.release_context()["runtime_freezes"][0]
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


@pytest.fixture
def development_contract():
    policy = _policy()
    target = json.loads((policy.DEVELOPMENT / "v1.5.0.dev0.json").read_text())
    frozen = json.loads((ROOT / target["runtime_freeze"]).read_text())
    return policy, target, frozen


def test_stable_and_development_authorities_stay_separate(development_contract):
    policy, target, _ = development_contract
    stable = policy.release_context("1.4.0")
    assert stable["development"] is None
    assert stable["package_version"] == stable["published_stable"] == "1.4.0"
    assert stable["runtime_freezes"] == (ROOT / "dev/release/vnext/CONTRACT_FREEZE_V1_4_0.json",)
    current = policy.release_context("1.5.0.dev0")
    assert current["published_stable"] == "1.4.0"
    assert current["package_version"] == "1.5.0.dev0"
    assert current["runtime_freezes"] == (ROOT / target["runtime_freeze"],)
    assert current["manifest"] == stable["manifest"]
    assert current["development"]["publish"] is False
    with pytest.raises(AssertionError, match="stable package version 9.9.9"):
        policy.release_context("9.9.9")


@pytest.mark.parametrize("key,value,message", [
    ("schema", "other", "target schema"),
    ("package_version", "1.5.0.dev1", "package version mismatch"),
    ("published_stable", "1.4.0rc1", "published stable must be stable"),
    ("published_stable", "1.5.0", "must follow published stable"),
    ("publish", True, "cannot authorize publication"),
    ("publish", "false", "cannot authorize publication"),
    ("runtime_freeze", "dev/release/vnext/CONTRACT_FREEZE_V1_4_0.json", "separate from published"),
    ("runtime_freeze", "../CONTRACT_FREEZE.json", "invalid development contract path"),
    ("runtime_freeze", "/tmp/CONTRACT_FREEZE.json", "invalid development contract path"),
    ("runtime_freeze", "dev/release/development/CONTRACT_FREEZE_MISSING.json", "contract is missing"),
    ("extra", "unsupported", "target fields"),
])
def test_development_metadata_rejects_ambiguous_or_publishable_targets(
        development_contract, key, value, message):
    policy, target, _ = development_contract
    target[key] = value
    with pytest.raises(AssertionError, match=message):
        policy.validate_development_target(target, "1.5.0.dev0")


def test_nonstable_source_requires_explicit_metadata(tmp_path, monkeypatch):
    policy = _policy()
    monkeypatch.setattr(policy, "DEVELOPMENT", tmp_path)
    for version in ("1.6.0.dev0", "1.6.0rc1", "1.6.0+local"):
        with pytest.raises(AssertionError, match="requires explicit development metadata"):
            policy.release_context(version)


@pytest.mark.parametrize("key,value,message", [
    ("schema", "img2drawing.contract_freeze.v2", "development contract schema"),
    ("package_version", "1.4.0", "development contract version mismatch"),
    ("publication_status", "published", "development contract publication status mismatch"),
])
def test_development_contract_cannot_relabel_a_published_freeze(
        development_contract, tmp_path, monkeypatch, key, value, message):
    policy, target, frozen = development_contract
    monkeypatch.setattr(policy, "ROOT", tmp_path)
    monkeypatch.setattr(policy, "DEVELOPMENT", tmp_path / "dev/release/development")
    monkeypatch.setattr(policy, "PUBLISH", tmp_path / "dev/release/publish")
    policy.DEVELOPMENT.mkdir(parents=True)
    frozen[key] = value
    (tmp_path / target["runtime_freeze"]).write_text(json.dumps(frozen))
    with pytest.raises(AssertionError, match=message):
        policy.validate_development_target(target, "1.5.0.dev0")


def test_development_publish_manifest_is_rejected(development_contract, tmp_path, monkeypatch):
    policy, target, _ = development_contract
    monkeypatch.setattr(policy, "PUBLISH", tmp_path)
    manifest = tmp_path / "v1.5.0.dev0.json"
    manifest.write_text("{}")
    with pytest.raises(AssertionError, match="cannot have a publish manifest"):
        policy.validate_development_target(target, "1.5.0.dev0")
    with pytest.raises(AssertionError, match="publish manifests require a stable"):
        policy._validate_publish_manifest(manifest)


@pytest.mark.parametrize("change,message", [
    ("missing", "document layer authority missing"),
    ("extra", "document layer authority fields drift"),
    ("schema", "document layer schema drift"),
    ("action", "document layer action drift"),
    ("contract", "document compositing contract drift"),
    ("digest", "document compositing digest drift"),
    ("default_capability", "default runtime capability drift"),
    ("layered_capability", "layered runtime capability drift"),
    ("session_member", "session surface drift"),
    ("authoring_export", "authoring export drift"),
])
def test_development_contract_rejects_incomplete_layer_authority(
        development_contract, change, message):
    policy, _, frozen = development_contract
    layers = frozen["document_layers"]
    if change == "missing":
        del frozen["document_layers"]
    elif change == "extra":
        layers["unverified"] = True
    elif change == "schema":
        layers["schemas"]["layer_document"] = "img2drawing.layer_document.v0"
    elif change == "action":
        layers["action_kinds"].remove("layer.assign")
    elif change == "contract":
        layers["compositing_contract"]["renderer_id"] = "other"
    elif change == "digest":
        layers["compositing_contract_digest"] = "0" * 64
    elif change == "default_capability":
        frozen["runtime_capabilities"]["authoring_helpers"].remove("img2drawing.authoring.StrokeEdit")
    elif change == "layered_capability":
        layers["runtime_capabilities"]["authoring_helpers"].remove("img2drawing.authoring.prepare_element_transform")
    elif change == "session_member":
        frozen["drawing_session_members"].remove("enable_layers")
    else:
        frozen["authoring_exports"].remove("ElementEditProposal")
    with pytest.raises(AssertionError, match=message):
        policy.verify_runtime_freeze(frozen)


@pytest.mark.parametrize("version", ["1.5.0.dev0", "1.5.0a1", "1.5.0b1", "1.5.0rc1",
                                      "1.5.0+local", "1.5.0.post1", "01.5.0", "invalid"])
def test_publisher_executes_no_release_or_build_command_for_nonstable_versions(tmp_path, version):
    _run_publisher_fixture(tmp_path, version, stable=False)


@pytest.mark.parametrize("version", ["1.4.0", "1.5.0", "2.0.0"])
def test_publisher_stable_guard_allows_normal_manifest_detection(tmp_path, version):
    _run_publisher_fixture(tmp_path, version, stable=True)


def _run_publisher_fixture(tmp_path, version, *, stable):
    """Execute the real workflow body with local sentinels, never release tools."""
    workflow = (ROOT / ".github/workflows/publish-release.yml").read_text()
    section = workflow.split("      - name: Publish new release manifests\n", 1)[1]
    script = textwrap.dedent(section.split("        run: |\n", 1)[1])
    package = tmp_path / "skills/img2drawing/src/img2drawing"
    package.mkdir(parents=True)
    (package / "_version.py").write_text(f"__version__ = {version!r}\n")
    manifests = tmp_path / "dev/release/publish"
    manifests.mkdir(parents=True)
    if not stable:
        # A manifest is present deliberately: removing/misplacing the guard
        # would reach jq/gh instead of passing because there was no work.
        (manifests / f"v{version}.json").write_text("{}")
    binaries = tmp_path / "bin"
    binaries.mkdir()
    (binaries / "python").symlink_to(sys.executable)
    sentinel = tmp_path / "release-command-called"
    for name in ("gh", "jq"):
        tool = binaries / name
        tool.write_text('#!/bin/sh\nprintf called > "$PUBLISH_SENTINEL"\nexit 97\n')
        tool.chmod(0o755)
    env = {**os.environ, "PATH": f"{binaries}{os.pathsep}{os.environ.get('PATH', '')}",
           "PUBLISH_SENTINEL": str(sentinel)}
    result = subprocess.run(["bash", "-c", script], cwd=tmp_path, env=env,
                            text=True, capture_output=True, check=False)
    assert result.returncode == 0, result.stdout + result.stderr
    expected = "No release manifests found." if stable else "Skipping publication for non-stable package version"
    assert expected in result.stdout
    assert not sentinel.exists()
    assert not (tmp_path / "dist").exists()
