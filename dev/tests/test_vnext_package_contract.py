from __future__ import annotations

import importlib.util
from pathlib import Path

import img2drawing
from img2drawing._version import PUBLIC_API, RELEASE_REVISION, RELEASE_SLICE


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "skills" / "img2drawing"


def _workflows_module():
    path = PACKAGE / "examples" / "mechanical_workflows.py"
    spec = importlib.util.spec_from_file_location("b17_mechanical_workflows", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_release_candidate_version_and_root_api_are_canonical():
    assert img2drawing.__version__ == "0.6.0rc1"
    assert PUBLIC_API == "DrawingSession/0.6.0-vnext"
    assert RELEASE_REVISION == "B17"
    assert RELEASE_SLICE == "B17_package_public_api_release_candidate"
    assert "DrawingSession" in img2drawing.__all__
    assert "DrawingRun" not in img2drawing.__all__


def test_manifest_selects_current_docs_examples_and_excludes_answer_routes():
    manifest = (PACKAGE / "MANIFEST.in").read_text(encoding="utf-8")
    for required in (
        "SKILL.md", "SUPPORT.md", "MIGRATION.md", "RELEASE.md",
        "references/reference-authority.md", "examples/observed", "examples/subjectless",
    ):
        assert required in manifest
    for forbidden in ("dev/", "dogfood", "p1_target.png", "references/stages"):
        assert forbidden not in manifest
    assert not (PACKAGE / "references" / "review" / "reference-authority.md").exists()
    assert not (PACKAGE / "examples" / "full_body_croquis" / "p1_target.png").exists()


def test_selected_examples_complete_observed_and_subjectless_mechanics(tmp_path: Path):
    workflows = _workflows_module()
    observed = workflows.run_observed(tmp_path / "observed")
    subjectless = workflows.run_subjectless(tmp_path / "subjectless")
    assert observed["authority"] == "observed"
    assert subjectless["authority"] == "imaginative"
    for name, result in (("observed", observed), ("subjectless", subjectless)):
        assert result["version"] == img2drawing.__version__
        assert result["finish_current_after_resume"] is True
        assert (tmp_path / name / "canonical_final.png").is_file()
        assert (tmp_path / name / "replay" / "timelapse.gif").is_file()
