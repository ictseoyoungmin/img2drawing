from __future__ import annotations

from pathlib import Path

import pytest

import img2drawing
from img2drawing._version import PUBLIC_API, RELEASE_REVISION, RELEASE_SLICE


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "skills" / "img2drawing"
CANONICAL_ROOT_EXPORTS = {
    "__version__",
    "ConstructionMark",
    "DrawingIntent",
    "DrawingSession",
    "InitialConstruct",
    "PoseObservation",
    "ReferenceAuthority",
    "ReferenceConstraint",
    "ReferenceUnavailableError",
    "RenderProfile",
    "author_initial_construct",
    "inspect_initial_construct",
    "observe_pose",
}


def test_release_candidate_version_and_root_api_are_canonical():
    assert img2drawing.__version__ == "0.6.0rc2"
    assert PUBLIC_API == "DrawingSession/0.6.0-vnext"
    assert RELEASE_REVISION == "B17"
    assert RELEASE_SLICE == "B17_package_public_api_release_candidate"
    assert set(img2drawing.__all__) == CANONICAL_ROOT_EXPORTS
    assert set(dir(img2drawing)) == CANONICAL_ROOT_EXPORTS
    assert "DrawingRun" not in img2drawing.__all__
    assert "CanvasHistory" not in img2drawing.__all__
    assert "AUTHORED_ELEMENT_SCHEMA" not in img2drawing.__all__


def test_pre_rc2_root_aliases_remain_compatible_but_not_discoverable():
    from img2drawing.core import CanvasHistory
    from img2drawing.inspection import ROI

    with pytest.warns(DeprecationWarning, match="root-compat shim"):
        assert img2drawing.CanvasHistory is CanvasHistory
    with pytest.warns(DeprecationWarning, match="root-compat shim"):
        assert img2drawing.ROI is ROI
    with pytest.warns(DeprecationWarning, match="root-compat shim"):
        assert img2drawing.VNextDrawingSession is img2drawing.DrawingSession

    assert "CanvasHistory" not in dir(img2drawing)
    assert "ROI" not in dir(img2drawing)
    assert "VNextDrawingSession" not in dir(img2drawing)


def test_manifest_selects_instruction_graph_and_excludes_control_plane_and_examples():
    manifest = (PACKAGE / "MANIFEST.in").read_text(encoding="utf-8")
    for required in (
        "LICENSE",
        "README.md",
        "SKILL.md",
        "recursive-include references *.md",
    ):
        assert required in manifest

    for forbidden in (
        "dev/",
        "dogfood",
        "NOTICE",
        "SUPPORT.md",
        "MIGRATION.md",
        "RELEASE.md",
        "FREEZE.md",
        "CONTRACT_FREEZE.json",
        "references/stages",
        "playbooks",
        "examples/",
    ):
        assert forbidden not in manifest

    assert not (PACKAGE / "examples").exists()
    for removed in (
        "NOTICE",
        "NOTICE.md",
        "SUPPORT.md",
        "MIGRATION.md",
        "RELEASE.md",
        "FREEZE.md",
        "CONTRACT_FREEZE.json",
        "playbooks",
        "references/stages",
        "references/legacy-r23.md",
        "references/intent.md",
        "references/reference-authority.md",
    ):
        assert not (PACKAGE / removed).exists()


def test_instruction_graph_contains_public_api_and_visual_leaves():
    refs = PACKAGE / "references"
    for required in (
        "foundation/line-economy.md",
        "foundation/reference-authority.md",
        "modes/croquis.md",
        "observation/visual-observation.md",
        "construction/gesture-and-masses.md",
        "description/descriptive-geometry.md",
        "figure/head-face-hair.md",
        "figure/legs-feet.md",
        "figure/clothing-folds.md",
        "props/attached-objects.md",
        "environment/ground-and-context.md",
        "review/residual-correction.md",
        "output/render-profile-and-replay.md",
        "api/public-surface.md",
    ):
        assert (refs / required).is_file(), required
