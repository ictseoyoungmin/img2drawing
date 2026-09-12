from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image

from img2drawing import DrawingIntent, DrawingSession
from img2drawing.vnext import (
    MATERIAL_POLICIES,
    SEMANTIC_STROKE_ROLES,
    TOOL_PRESETS,
    material_policy_for_style,
    resolve_mark_for_intent,
    resolve_markmaking,
)


def _subject(tmp_path: Path) -> Path:
    path = tmp_path / "subject.png"
    Image.new("RGB", (96, 72), (244, 242, 238)).save(path)
    return path


def test_public_vocabularies_are_small_and_explicit() -> None:
    assert MATERIAL_POLICIES == (
        "canonical-pencil",
        "manga-light",
        "dry-graphite-expressive",
    )
    assert SEMANTIC_STROKE_ROLES == (
        "construction",
        "gesture",
        "form",
        "contour",
        "accent",
        "hair",
        "hatch",
        "broad_mass",
        "environment",
    )
    assert "hair-flick" in TOOL_PRESETS
    assert "broad-graphite" in TOOL_PRESETS


def test_existing_high_level_styles_resolve_without_second_style_axis() -> None:
    assert material_policy_for_style("pencil_loose").policy_id == "canonical-pencil"
    assert material_policy_for_style("graphite_academic").policy_id == "canonical-pencil"
    assert material_policy_for_style("graphite_tonal").policy_id == "dry-graphite-expressive"
    # Unknown/custom prose remains conservative unless material intent is explicit.
    assert material_policy_for_style("custom:angular-quiet").policy_id == "canonical-pencil"
    assert material_policy_for_style(
        "custom:angular-quiet", explicit="manga-light"
    ).policy_id == "manga-light"


def test_semantic_role_resolves_to_public_tool_without_renderer_internals() -> None:
    mark = resolve_markmaking("pencil_loose", "hair")
    assert mark.semantic_role == "hair"
    assert mark.tool_preset_id == "hair-flick"
    assert mark.terminal_mode == "flick"
    assert mark.runtime_tool == "form_pencil"
    assert mark.resolved_tool_state["width"] == pytest.approx(2.2)
    assert "renderer" not in mark.to_dict()
    assert "patch" not in str(mark.to_dict()).lower()


def test_modifiers_are_resolved_and_recordable() -> None:
    mark = resolve_markmaking(
        "graphite_academic",
        "contour",
        modifiers={"width": 4.1, "pressure": 0.74, "opacity": 0.82},
    )
    assert mark.tool_preset_id == "contour-weighted"
    assert mark.material_policy.policy_id == "canonical-pencil"
    assert mark.resolved_tool_state["width"] == pytest.approx(4.1)
    assert mark.resolved_tool_state["pressure"] == pytest.approx(0.74)
    kwargs = mark.draw_kwargs(metadata={"semantic_group": "jaw-boundary"})
    assert kwargs["role"] == "contour"
    assert kwargs["tool"]["preset"] == "form_pencil"
    assert kwargs["metadata"]["semantic_group"] == "jaw-boundary"
    assert kwargs["metadata"]["markmaking"]["digest"] == mark.digest()


def test_markmaking_resolution_survives_session_replay(tmp_path: Path) -> None:
    subject = _subject(tmp_path)
    session = DrawingSession.create(
        subject=subject,
        output_dir=tmp_path / "run",
        intent=DrawingIntent(style_profile="graphite_academic"),
    )
    mark = resolve_mark_for_intent(session.intent, "contour")
    stroke_id = session.draw(
        ((8, 12), (34, 24), (72, 50)),
        stroke_id="weighted-outline",
        part="jaw",
        **mark.draw_kwargs(),
    )
    stroke = session.current_stroke(stroke_id)
    provenance = stroke.tool_state["provenance"]
    saved = provenance["metadata"]["markmaking"]
    assert saved["digest"] == mark.digest()
    assert saved["tool_preset_id"] == "contour-weighted"
    assert saved["material_policy"]["policy_id"] == "canonical-pencil"
    assert saved["resolved_tool_state"]["width"] == pytest.approx(3.6)

    resumed = DrawingSession.resume(session.checkpoint_path, subject=subject)
    replayed = resumed.current_stroke(stroke_id)
    replayed_mark = replayed.tool_state["provenance"]["metadata"]["markmaking"]
    assert replayed_mark == saved


def test_customization_rejects_private_or_unknown_modifier_fields() -> None:
    with pytest.raises(ValueError, match="unsupported markmaking modifiers"):
        resolve_markmaking("pencil_loose", "form", modifiers={"private_renderer_knob": 1.0})
    with pytest.raises(ValueError, match="unknown semantic stroke role"):
        resolve_markmaking("pencil_loose", "magic_line")
    with pytest.raises(ValueError, match="unknown markmaking tool preset"):
        resolve_markmaking("pencil_loose", "form", tool_preset="private-brush")
