from __future__ import annotations

import json
from pathlib import Path

import pytest
from PIL import Image

from img2drawing.vnext import (
    DrawingIntent,
    DrawingSession,
    IntentProvenance,
    StyleGuide,
    compatibility_intent,
    resolve_mode_guide,
    resolve_style_guide,
)


def _subject(tmp_path: Path) -> Path:
    path = tmp_path / "subject.png"
    Image.new("RGB", (48, 36), (245, 244, 240)).save(path)
    return path


def test_intent_axes_are_independent_and_portable() -> None:
    intent = DrawingIntent(
        reference_mode="imaginative",
        drawing_mode="tonal_study",
        finish_intent="expressive",
        style_profile="graphite_academic",
        provenance=IntentProvenance(source="agent", reason="alternate reading"),
    )
    restored = DrawingIntent.from_dict(intent.to_dict())
    assert restored == intent
    assert restored.digest() == intent.digest()
    assert DrawingIntent(reference_mode="hybrid").drawing_mode == "croquis"
    assert DrawingIntent(drawing_mode="free_draw").reference_mode == "observed"
    assert restored.to_dict()["provenance"]["reason"] == "alternate reading"


def test_unknown_values_and_custom_style_identifier_are_explicit() -> None:
    with pytest.raises(ValueError, match="unsupported reference_mode"):
        DrawingIntent(reference_mode="quick")
    with pytest.raises(ValueError, match="unsupported drawing_mode"):
        DrawingIntent(drawing_mode="pipeline")
    with pytest.raises(ValueError, match="unsupported finish_intent"):
        DrawingIntent(finish_intent="complete")
    with pytest.raises(ValueError, match="unsupported style_profile"):
        DrawingIntent(style_profile="graphite_magic")
    assert DrawingIntent(style_profile="custom:my_marks").style_profile == "custom:my_marks"
    with pytest.raises(ValueError, match="custom style"):
        resolve_style_guide("custom:my_marks")


def test_guides_are_data_only_and_style_overrides_one_base() -> None:
    mode = resolve_mode_guide("figure_drawing")
    style = resolve_style_guide("pencil_loose")
    assert mode.drawing_mode == "figure_drawing"
    assert "stage" not in mode.to_dict()
    assert "cursor" not in mode.to_dict()
    assert "advance" not in mode.to_dict()
    assert "verdict" not in mode.to_dict()
    assert "renderer" not in style.to_dict()
    assert "post_filter" not in style.to_dict()
    changed = style.with_overrides({"line_behavior": ["single deliberate pass"]})
    assert changed.style_profile == style.style_profile
    assert changed.line_behavior == ("single deliberate pass",)
    assert changed.value_policy == style.value_policy
    with pytest.raises(ValueError, match="lifecycle fields"):
        type(mode).from_dict({**mode.to_dict(), "cursor": 2})
    with pytest.raises(ValueError, match="unsupported fields"):
        style.with_overrides({"renderer": "pencil"})
    with pytest.raises(ValueError, match="base style_profile"):
        style.with_overrides({"style_profile": "graphite_academic"})


def test_compatibility_alias_is_an_explicit_orthogonal_lookup() -> None:
    intent = compatibility_intent("full_body_croquis")
    assert intent.reference_mode == "observed"
    assert intent.drawing_mode == "croquis"
    assert intent.provenance is not None
    assert intent.provenance.compatibility_key == "full_body_croquis"
    with pytest.raises(ValueError, match="unsupported compatibility"):
        compatibility_intent("full_body_croquis_stage")


def test_session_intent_provenance_resumes_without_geometry_rewrite(tmp_path: Path) -> None:
    subject = _subject(tmp_path)
    output = tmp_path / "run"
    initial = DrawingIntent(reference_mode="observed", drawing_mode="croquis")
    session = DrawingSession.create(subject=subject, output_dir=output, intent=initial)
    session.draw([(4, 4), (18, 16)], action_id="mark-1")
    before_hash = session.drawing_state_hash()
    before_cursor = session.history_cursor
    changed = session.set_intent(
        DrawingIntent(
            reference_mode="hybrid",
            drawing_mode="figure_drawing",
            finish_intent="subject",
            style_profile="graphite_academic",
        ),
        reason="inspection changed the emphasis",
    )
    assert changed.previous_intent_digest == initial.digest()
    assert session.drawing_state_hash() == before_hash
    assert session.history_cursor == before_cursor
    assert len(session.intent_history) == 2
    payload = json.loads(session.checkpoint_path.read_text(encoding="utf-8"))
    assert payload["intent"]["drawing_mode"] == "figure_drawing"
    assert len(payload["intent_history"]) == 2
    resumed = DrawingSession.resume(session.checkpoint_path, subject=subject)
    assert resumed.intent == session.intent
    assert resumed.intent_history == session.intent_history
    assert resumed.drawing_state_hash() == before_hash


def test_session_intent_selection_rolls_back_when_checkpoint_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    session = DrawingSession.create(subject=_subject(tmp_path), output_dir=tmp_path / "run")
    before_intent = session.intent
    before_events = session.intent_history

    def fail_checkpoint(path: Path) -> None:
        raise OSError("checkpoint storage unavailable")

    monkeypatch.setattr(session, "_write_checkpoint", fail_checkpoint)
    with pytest.raises(OSError, match="checkpoint storage unavailable"):
        session.set_intent(DrawingIntent(drawing_mode="free_draw"), reason="try alternate")
    assert session.intent == before_intent
    assert session.intent_history == before_events


def test_resume_rejects_tampered_intent_provenance(tmp_path: Path) -> None:
    subject = _subject(tmp_path)
    session = DrawingSession.create(
        subject=subject,
        output_dir=tmp_path / "run",
        intent=DrawingIntent(),
    )
    payload = json.loads(session.checkpoint_path.read_text(encoding="utf-8"))
    payload["intent_history"][0]["intent"]["drawing_mode"] = "free_draw"
    session.checkpoint_path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="intent change digest"):
        DrawingSession.resume(session.checkpoint_path, subject=subject)

    payload = json.loads(session.checkpoint_path.read_text(encoding="utf-8"))
    payload["intent_history"][0]["intent"] = DrawingIntent(drawing_mode="free_draw").to_dict()
    payload["intent_history"][0].pop("intent_digest")
    session.checkpoint_path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="intent change digest"):
        DrawingSession.resume(session.checkpoint_path, subject=subject)


def test_resume_rejects_current_intent_without_history(tmp_path: Path) -> None:
    subject = _subject(tmp_path)
    session = DrawingSession.create(
        subject=subject,
        output_dir=tmp_path / "run",
        intent=DrawingIntent(drawing_mode="free_draw"),
    )
    payload = json.loads(session.checkpoint_path.read_text(encoding="utf-8"))
    payload["intent_history"] = []
    session.checkpoint_path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="current intent requires non-empty intent history"):
        DrawingSession.resume(session.checkpoint_path, subject=subject)
