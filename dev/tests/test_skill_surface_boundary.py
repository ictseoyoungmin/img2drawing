from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / "skills" / "img2drawing"


def _text(relative: str) -> str:
    return (SKILL / relative).read_text(encoding="utf-8")


def test_deployable_skill_root_is_attention_clean() -> None:
    assert {path.name for path in SKILL.iterdir()} == {
        "LICENSE",
        "MANIFEST.in",
        "SKILL.md",
        "pyproject.toml",
        "references",
        "src",
    }
    assert not (SKILL / "examples").exists()


def test_reference_surface_is_the_instruction_graph() -> None:
    assert {path.name for path in (SKILL / "references").iterdir()} == {
        "INDEX.md",
        "api",
        "construction",
        "description",
        "environment",
        "figure",
        "foundation",
        "markmaking",
        "modes",
        "observation",
        "output",
        "props",
        "review",
    }
    assert {path.name for path in (SKILL / "references" / "foundation").iterdir()} == {
        "line-economy.md",
        "occlusion-inference.md",
        "reference-authority.md",
        "scope-and-precedence.md",
        "structural-specificity.md",
    }
    assert {path.name for path in (SKILL / "references" / "construction").iterdir()} == {
        "balance-and-limbs.md",
        "foreshortening-and-depth.md",
        "gesture-and-masses.md",
        "orientation-and-twist.md",
    }
    assert {path.name for path in (SKILL / "references" / "figure").iterdir()} == {
        "clothing-folds.md",
        "hands-and-grip.md",
        "head-face-hair.md",
        "legs-feet.md",
        "torso-arms-hands.md",
    }
    assert {path.name for path in (SKILL / "references" / "review").iterdir()} == {
        "authored-element-navigation.md",
        "completion.md",
        "markmaking-residuals.md",
        "residual-correction.md",
        "residual-routing.md",
        "stroke-retirement.md",
        "visual-quality-gates.md",
    }


def test_skill_root_is_router_not_specialist_textbook() -> None:
    skill = _text("SKILL.md")

    assert "`SKILL.md` is the router" in skill
    assert "references/INDEX.md" in skill
    assert "## Conditional start route" in skill
    assert "## Canonical drawing loop" in skill
    assert "## Completion and output routing" in skill

    for specialist_heading in (
        "## Whole-subject structural hypothesis",
        "## Structural read before description",
        "## Revalidate before inheriting construction",
        "## Occlusion inference boundary",
        "## Head and face policy",
        "## Hands and grip policy",
        "## Foreshortening and depth policy",
        "## Legs and feet policy",
        "## Clothing-fold policy",
        "## Croquis value boundary",
        "## Stroke retirement",
    ):
        assert specialist_heading not in skill


def test_instruction_graph_hardens_geometry_preserving_line_economy() -> None:
    skill = _text("SKILL.md")
    croquis = _text("references/modes/croquis.md")
    lower = _text("references/figure/legs-feet.md")
    head = _text("references/figure/head-face-hair.md")
    folds = _text("references/figure/clothing-folds.md")

    assert "Croquis economizes marks, not observed geometry" in skill
    assert "Economize marks, not geometry" in croquis
    assert "uniform tube" in lower
    assert "circle" in head
    assert "zigzags" in folds


def test_visual_quality_gate_is_a_direct_conditional_root_route() -> None:
    skill = _text("SKILL.md")
    index = _text("references/INDEX.md")
    gates = _text("references/review/visual-quality-gates.md")
    head = _text("references/figure/head-face-hair.md")
    completion = _text("references/review/completion.md")

    assert "references/review/visual-quality-gates.md" in skill
    assert "before accepting the first descriptive semantic group" in skill
    assert "Do not rely on transitive discovery" in skill
    assert "review/visual-quality-gates.md" in index
    assert "Visible authority" in gates
    assert "Line ownership gate" in gates
    assert "Anti-symbol gate" in gates
    assert "Perspective-propagation gate" in gates
    assert "KEEP" in gates and "SOFTEN" in gates and "RETIRE" in gates
    assert "head + hair outer mass" in head
    assert "selected strand accents" in head
    assert "three largest remaining visible mismatches" in completion


def test_instruction_graph_routes_residuals_by_cause_and_escalates_upstream() -> None:
    skill = _text("SKILL.md")
    index = _text("references/INDEX.md")
    correction = _text("references/review/residual-correction.md")
    routing = _text("references/review/residual-routing.md")

    assert "references/review/residual-routing.md" in skill
    assert "references/review/residual-correction.md" in skill
    assert "Route residuals by cause, not by noun" in skill
    assert "route by the relationship that must change" in index.lower()
    assert "Do not route by the noun that looks wrong" in correction
    assert "Route by **cause**, not by the noun that looks wrong" in routing

    for path in (
        "construction/balance-and-limbs.md",
        "construction/orientation-and-twist.md",
        "environment/ground-and-context.md",
        "figure/legs-feet.md",
        "description/contour-and-overlap.md",
        "figure/head-face-hair.md",
        "figure/hands-and-grip.md",
        "props/attached-objects.md",
        "observation/visual-observation.md",
    ):
        assert path in routing

    assert "Escalation is not a stage reset" in routing
    assert "Do not read every branch below" in routing


def test_high_value_hand_and_foreshortening_leaves_remain_routable() -> None:
    index = _text("references/INDEX.md")
    hands = _text("references/figure/hands-and-grip.md")
    depth = _text("references/construction/foreshortening-and-depth.md")
    routing = _text("references/review/residual-routing.md")

    for path in ("figure/hands-and-grip.md", "construction/foreshortening-and-depth.md"):
        assert path in index
        assert path in routing

    assert "A hand is not a mitten" in hands
    assert "Do not begin by counting fingers" in hands
    assert "Do not invent knuckles, fingertips, or hidden digits" in hands
    assert "projected spacing" in depth
    assert "near and far anchors" in depth
    assert "unfold a foreshortened limb" in depth
    assert "Foreshortening or depth compression looks wrong" in routing


def test_structural_orientation_hardening_is_owned_by_leaves_not_root_textbook() -> None:
    skill = _text("SKILL.md")
    index = _text("references/INDEX.md")
    observation = _text("references/observation/visual-observation.md")
    orientation = _text("references/construction/orientation-and-twist.md")
    croquis = _text("references/modes/croquis.md")
    routing = _text("references/review/residual-routing.md")

    for document in (index, routing):
        assert "construction/orientation-and-twist.md" in document

    assert "Macro pose, mass, orientation" in skill
    assert "tilt" in observation
    assert "turn" in observation
    assert "near/far" in observation
    assert "projected centerline" in observation
    assert "head / ribcage / pelvis orientation" in orientation
    assert "shoulder / pelvis counter-relation" in orientation
    assert "local contours look clean while the whole pose has lost" in orientation
    assert "not a runtime stage" in orientation.lower()
    assert "Broad value regions and dense regular hatch fields are **off by default**" in croquis
    assert "pose must remain readable" in croquis
    assert "Whole pose feels flatter, more frontal, or more symmetric" in routing
    assert "local parts become cleaner while the whole pose becomes more frontal" in routing


def test_structural_specificity_is_cross_subject_and_revalidates_inheritance() -> None:
    skill = _text("SKILL.md")
    index = _text("references/INDEX.md")
    specificity = _text("references/foundation/structural-specificity.md")
    economy = _text("references/foundation/line-economy.md")
    correction = _text("references/review/residual-correction.md")
    descriptive = _text("references/description/descriptive-geometry.md")

    assert "references/foundation/structural-specificity.md" in skill
    assert "foundation/structural-specificity.md" in index
    assert "For any observed subject" in index
    assert "Defer secondary detail, not structural specificity" in specificity
    assert "A small feature is not automatically secondary" in specificity
    assert "merely because it was drawn earlier" in specificity
    assert "parent structure still credible?" in specificity
    assert "Construction is provisional" in skill
    assert "Revalidate parent structure against current evidence" in skill
    assert "Detail is not classified by size" in economy
    assert "Earlier construction is provisional" in correction
    assert "must not promote a provisional construction primitive" in descriptive


def test_occlusion_inference_separates_hidden_structure_from_visible_appearance() -> None:
    skill = _text("SKILL.md")
    index = _text("references/INDEX.md")
    occlusion = _text("references/foundation/occlusion-inference.md")
    observation = _text("references/observation/visual-observation.md")
    measuring = _text("references/observation/measuring-boundaries.md")
    contour = _text("references/description/contour-and-overlap.md")
    routing = _text("references/review/residual-routing.md")

    assert "references/foundation/occlusion-inference.md" in skill
    assert "foundation/occlusion-inference.md" in index
    assert "Infer hidden structure only when continuity requires it" in skill
    assert "do not fabricate hidden appearance" in skill
    assert "Keep three layers separate" in occlusion
    assert "Visible evidence" in occlusion
    assert "Provisional hidden structure" in occlusion
    assert "Rendered visible description" in occlusion
    assert "When hidden inference is required" in occlusion
    assert "How to infer without overclaiming" in occlusion
    assert "Partial and one-sided occlusion" in occlusion
    assert "Measurement tools stop at occlusion" in occlusion
    assert "entry direction before an occluder" in observation
    assert "first visible reappearance" in observation
    assert "hard boundary for **measurement**, not for all structural reasoning" in measuring
    assert "hidden-continuity hypothesis" in measuring
    assert "Occlusion is not structural termination" in contour
    assert "provisional hidden continuation" in contour
    assert "Occluded relation looks disconnected or ends at the occluder" in routing
    assert "do not infer anything" in routing


def test_skill_facing_docs_do_not_leak_internal_or_release_control_plane() -> None:
    documents = [SKILL / "SKILL.md"]
    documents.extend((SKILL / "references").rglob("*.md"))

    slice_label = re.compile(r"\bB(?:0[0-9]|1[0-8])(?:-R\d+)?\b")
    forbidden_filenames = (
        "CONTRACT_FREEZE.json",
        "FREEZE.md",
        "MIGRATION.md",
        "NOTICE.md",
        "RELEASE.md",
        "SUPPORT.md",
    )
    forbidden_internal = ("_internal", "CanvasAction", "__vnext_compat__")

    for path in documents:
        text = path.read_text(encoding="utf-8")
        assert not slice_label.search(text), f"internal slice label leaked into {path.relative_to(ROOT)}"
        assert "`dev/" not in text, f"developer path leaked into {path.relative_to(ROOT)}"
        for name in forbidden_filenames:
            assert name not in text, f"release control-plane reference {name} leaked into {path.relative_to(ROOT)}"
        for token in forbidden_internal:
            assert token not in text, f"internal implementation token {token} leaked into {path.relative_to(ROOT)}"


def test_notice_is_not_part_of_skill_or_package_metadata() -> None:
    assert not (SKILL / "NOTICE").exists()
    assert not (SKILL / "NOTICE.md").exists()
    pyproject = (SKILL / "pyproject.toml").read_text(encoding="utf-8")
    manifest = (SKILL / "MANIFEST.in").read_text(encoding="utf-8")
    assert "NOTICE" not in pyproject
    assert "NOTICE" not in manifest
