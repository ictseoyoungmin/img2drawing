from __future__ import annotations

from img2drawing import DrawingIntent, DrawingSession
from img2drawing.vnext import DRAWING_MODES, resolve_mode_guide


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
    intent = DrawingIntent(drawing_mode="gesture", finish_intent="pose")
    session = DrawingSession.create(canvas=(64, 96), output_dir=out, intent=intent)
    assert session.intent.drawing_mode == "gesture"

    resumed = DrawingSession.resume(session.checkpoint_path, output_dir=tmp_path / "resume")
    assert resumed.intent.drawing_mode == "gesture"
    assert resumed.intent.digest() == intent.digest()
