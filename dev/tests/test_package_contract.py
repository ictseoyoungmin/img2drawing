from __future__ import annotations

from pathlib import Path

import pytest

import img2drawing


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


def test_version_and_root_api_are_canonical():
    assert img2drawing.__version__.startswith("1.1.0")
    assert set(img2drawing.__all__) == CANONICAL_ROOT_EXPORTS
    assert set(dir(img2drawing)) == CANONICAL_ROOT_EXPORTS
    assert "DrawingRun" not in img2drawing.__all__
    assert "CanvasHistory" not in img2drawing.__all__
    assert "AUTHORED_ELEMENT_SCHEMA" not in img2drawing.__all__


def test_retired_root_aliases_and_namespaces_do_not_resolve():
    import importlib.util

    for name in ("CanvasHistory", "ROI", "VNextDrawingSession", "Stroke", "resolve_tone", "DrawingRun"):
        with pytest.raises(AttributeError):
            getattr(img2drawing, name)
    for module in ("img2drawing.vnext", "img2drawing.provenance", "img2drawing.core.session", "img2drawing.core.fill"):
        assert importlib.util.find_spec(module) is None, module


def test_specialized_namespaces_own_their_capabilities():
    from img2drawing.authoring import resolve_mark_for_intent, retune_stroke, sample_catmull_rom
    from img2drawing.core import CanvasHistory
    from img2drawing.inspection import ROI, render_wip_guides
    from img2drawing.observation import SubjectPalette
    from img2drawing.session import FinishRecord, ResidualRecord

    assert all((resolve_mark_for_intent, retune_stroke, sample_catmull_rom, CanvasHistory, ROI,
                render_wip_guides, SubjectPalette, FinishRecord, ResidualRecord))


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
        "foundation/occlusion-inference.md",
        "modes/gesture-drawing.md",
        "modes/croquis.md",
        "observation/visual-observation.md",
        "construction/gesture-and-masses.md",
        "construction/foreshortening-and-depth.md",
        "description/descriptive-geometry.md",
        "figure/head-face-hair.md",
        "figure/hands-and-grip.md",
        "figure/legs-feet.md",
        "figure/clothing-folds.md",
        "props/attached-objects.md",
        "environment/ground-and-context.md",
        "review/residual-correction.md",
        "review/residual-routing.md",
        "output/render-profile-and-replay.md",
        "api/public-surface.md",
    ):
        assert (refs / required).is_file(), required

    skill = (PACKAGE / "SKILL.md").read_text(encoding="utf-8")
    index = (refs / "INDEX.md").read_text(encoding="utf-8")
    assert "references/INDEX.md" in skill
    assert "api/public-surface.md" in index
    assert "foundation/occlusion-inference.md" in index


def test_root_compatibility_names_stay_out_of_normal_discovery():
    for name in (
        "CanvasHistory",
        "DrawingRun",
        "FinishRecord",
        "Stroke",
        "StrokeIR",
        "SubjectPalette",
        "VNextDrawingSession",
        "replace_fill_region",
    ):
        assert name not in dir(img2drawing)
