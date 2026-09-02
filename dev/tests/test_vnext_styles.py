from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image

from img2drawing import (
    STYLE_PROFILES,
    DrawingIntent,
    DrawingSession,
    StyleClarificationRequired,
    StyleConflictError,
    StyleGuide,
    resolve_style_guide,
)


EXPECTED_STYLES = ("pencil_loose", "graphite_academic", "graphite_tonal")


def _subject(tmp_path: Path) -> Path:
    path = tmp_path / "subject.png"
    Image.new("RGB", (64, 48), (243, 241, 237)).save(path)
    return path


def _guide_text(guide: StyleGuide) -> str:
    return " ".join(
        (
            *guide.line_behavior,
            *guide.construction_visibility,
            *guide.detail_policy,
            *guide.value_policy,
            *guide.edge_policy,
            *guide.authoring_notes,
        )
    ).lower()


def _custom(**kwargs) -> StyleGuide:
    values = {
        "style_profile": "custom:angular-quiet",
        "line_behavior": ("use angular deliberate line changes",),
        "construction_visibility": ("retain only composition-bearing axes",),
        "detail_policy": ("keep detail sparse outside the focal shape",),
        "value_policy": ("use one quiet supporting value family",),
        "edge_policy": ("reserve the sharpest edge for the focal turn",),
        "authoring_notes": ("preserve subject geometry and declared constraints",),
    }
    values.update(kwargs)
    return StyleGuide.custom(**values)


def test_preset_surface_is_small_distinct_and_portable() -> None:
    assert STYLE_PROFILES == EXPECTED_STYLES
    guides = tuple(resolve_style_guide(profile) for profile in STYLE_PROFILES)
    assert tuple(guide.style_profile for guide in guides) == EXPECTED_STYLES
    assert len({_guide_text(guide) for guide in guides}) == len(guides)
    assert all(StyleGuide.from_dict(guide.to_dict()) == guide for guide in guides)


def test_graphite_tonal_is_authored_value_policy_not_output_filter() -> None:
    text = _guide_text(resolve_style_guide("graphite_tonal"))
    assert all(term in text for term in ("large calibrated value regions", "observed lights", "hard, soft, and lost edges"))
    assert "renderprofile remains unchanged" in text
    assert "raster filter" in text and "incorrect geometry" in text


def test_one_base_overrides_are_explicit_and_reject_inheritance() -> None:
    base = resolve_style_guide("graphite_academic")
    resolved = resolve_style_guide(
        "graphite_academic",
        {"edge_policy": ("sharpen only the observed contact edge",)},
    )
    assert resolved.style_profile == base.style_profile
    assert resolved.edge_policy == ("sharpen only the observed contact edge",)
    assert resolved.value_policy == base.value_policy
    with pytest.raises(ValueError, match="unsupported fields"):
        resolve_style_guide("graphite_academic", {"base": "pencil_loose"})
    with pytest.raises(ValueError, match="base style_profile"):
        resolve_style_guide("graphite_academic", {"style_profile": "pencil_loose"})
    with pytest.raises(ValueError, match="unsupported style_profile"):
        resolve_style_guide("graphite_magic")


def test_custom_style_is_complete_structured_portable_data() -> None:
    guide = _custom()
    assert guide.style_profile == "custom:angular-quiet"
    assert StyleGuide.from_dict(guide.to_dict()) == guide
    assert resolve_style_guide(guide.style_profile, custom=guide) == guide
    assert resolve_style_guide(guide.style_profile, custom=guide.to_dict()) == guide
    with pytest.raises(ValueError, match="complete Agent-structured"):
        resolve_style_guide(guide.style_profile)
    with pytest.raises(ValueError, match="does not match"):
        resolve_style_guide("custom:other", custom=guide)
    with pytest.raises(ValueError, match="cannot combine a base override"):
        resolve_style_guide(guide.style_profile, {"edge_policy": ("soft",)}, custom=guide)
    with pytest.raises(ValueError, match="complete records"):
        guide.with_overrides({"edge_policy": ("soft",)})


def test_ambiguous_or_conflicting_style_input_fails_explicitly() -> None:
    with pytest.raises(StyleClarificationRequired, match="dry but liquid"):
        _custom(unresolved_terms=("dry but liquid line",))
    with pytest.raises(StyleClarificationRequired, match="unclear pressure"):
        resolve_style_guide("pencil_loose", unresolved_terms=("unclear pressure request",))
    with pytest.raises(StyleConflictError, match="observed shoulder width"):
        resolve_style_guide(
            "pencil_loose",
            conflicts=("stylize narrower than the observed shoulder width",),
        )
    with pytest.raises(StyleConflictError, match="preserved prop contact"):
        resolve_style_guide("graphite_academic").with_overrides(
            {"detail_policy": ("remove the prop",)},
            conflicts=("override preserved prop contact",),
        )


def test_style_change_is_intent_provenance_until_marks_are_explicitly_edited(
    tmp_path: Path,
) -> None:
    subject = _subject(tmp_path)
    session = DrawingSession.create(
        subject=subject,
        output_dir=tmp_path / "run",
        intent=DrawingIntent(style_profile="pencil_loose"),
    )
    session.draw(
        ((6, 8), (25, 20), (51, 36)),
        stroke_id="gesture-mark",
        part="gesture",
    )
    before_hash = session.drawing_state_hash()
    before_cursor = session.history_cursor
    render_profile = session.render_profile

    event = session.set_intent(
        DrawingIntent(style_profile="graphite_tonal"),
        reason="author the remaining form with grouped value",
    )
    assert event.history_cursor == before_cursor
    assert session.drawing_state_hash() == before_hash
    assert session.history_cursor == before_cursor
    assert session.render_profile == render_profile

    session.replace_stroke(
        "gesture-mark",
        ((6, 8), (29, 18), (51, 36)),
        stroke_id="gesture-mark-tonal-revision",
        part="gesture",
        reason="explicitly revise the focal turn under the selected authoring policy",
    )
    assert session.history_cursor == before_cursor + 1
    assert session.drawing_state_hash() != before_hash
    resumed = DrawingSession.resume(session.checkpoint_path, subject=subject)
    assert resumed.intent.style_profile == "graphite_tonal"
    assert resumed.intent_history == session.intent_history
    assert resumed.render_profile == render_profile
    assert resumed.drawing_state_hash() == session.drawing_state_hash()


def test_style_guide_and_render_profile_have_no_overlapping_runtime_fields(tmp_path: Path) -> None:
    session = DrawingSession.create(
        subject=_subject(tmp_path),
        output_dir=tmp_path / "run",
        intent=DrawingIntent(style_profile="graphite_tonal"),
    )
    style_keys = set(resolve_style_guide("graphite_tonal").to_dict())
    render_keys = set(session.render_profile.to_dict())
    assert not ({"renderer_id", "renderer_version", "supersample", "seed"} & style_keys)
    assert not ({"style_profile", "line_behavior", "value_policy", "edge_policy"} & render_keys)
