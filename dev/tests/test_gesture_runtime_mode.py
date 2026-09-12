from __future__ import annotations

from img2drawing import DrawingIntent, DrawingSession
from img2drawing.vnext import (
    DRAWING_MODES,
    ReferenceAuthority,
    resolve_mark_for_intent,
    resolve_mode_guide,
)


def test_gesture_is_a_public_drawing_intent_mode() -> None:
    assert "gesture" in DRAWING_MODES

    intent = DrawingIntent(
        reference_mode="observed",
        drawing_mode="gesture",
        finish_intent="pose",
        style_profile="pencil_loose",
    )
    assert intent.drawing_mode == "gesture"
    assert intent.to_dict()["drawing_mode"] == "gesture"

    guide = resolve_mode_guide("gesture")
    assert guide.drawing_mode == "gesture"
    joined = " ".join(
        guide.primary_observations
        + guide.recommended_grammar
        + guide.omissions
        + guide.finish_emphasis
        + guide.completion_questions
    ).lower()
    assert "head facing" in joined
    assert "rounded blobs" in joined
    assert "major limb chains" in joined
    assert "support" in joined


def test_drawing_session_checkpoint_preserves_gesture_intent(tmp_path) -> None:
    out = tmp_path / "gesture"
    intent = DrawingIntent(
        reference_mode="imaginative",
        drawing_mode="gesture",
        finish_intent="pose",
    )
    authority = ReferenceAuthority.imaginative(("gesture runtime checkpoint contract",))
    session = DrawingSession.create(
        canvas=(64, 96),
        output_dir=out,
        intent=intent,
        reference_authority=authority,
    )
    assert session.intent.drawing_mode == "gesture"

    resumed = DrawingSession.resume(session.checkpoint_path, output_dir=tmp_path / "resume")
    assert resumed.intent.drawing_mode == "gesture"
    assert resumed.intent.digest() == intent.digest()


def test_gesture_flow_semantic_preset_resolves_to_runtime_draw_kwargs(tmp_path) -> None:
    intent = DrawingIntent(
        reference_mode="imaginative",
        drawing_mode="gesture",
        finish_intent="pose",
        style_profile="pencil_loose",
    )
    authority = ReferenceAuthority.imaginative(("one rising gesture sweep",))
    session = DrawingSession.create(
        canvas=(64, 96),
        output_dir=tmp_path / "markmaking",
        intent=intent,
        reference_authority=authority,
    )

    mark = resolve_mark_for_intent(
        session.intent,
        "gesture",
        tool_preset="gesture-flow",
    )
    assert mark.tool_preset_id == "gesture-flow"
    assert mark.runtime_tool == "form_pencil"

    stroke_id = session.draw(
        ((8, 70), (26, 42), (48, 20)),
        part="dominant-action",
        **mark.draw_kwargs(),
    )
    stroke = session.current_stroke(stroke_id)
    saved = stroke.tool_state["provenance"]["metadata"]["markmaking"]
    assert saved["tool_preset_id"] == "gesture-flow"
    assert saved["runtime_tool"] == "form_pencil"
