"""Regression evidence for v1.2.1 partial markmaking overrides and material provenance."""

from copy import deepcopy
from pathlib import Path

import pytest
from PIL import Image

from img2drawing import DrawingIntent, DrawingSession
from img2drawing.authoring import resolve_mark_for_intent
from img2drawing.core.digest import sha256_obj


def _session(tmp_path: Path) -> DrawingSession:
    reference = tmp_path / "reference.png"
    Image.new("RGB", (80, 80), "white").save(reference)
    return DrawingSession.create(
        subject=reference, output_dir=tmp_path / "draw",
        intent=DrawingIntent(drawing_mode="croquis"),
    )


def _assert_reconciled(stroke, *, width: float) -> None:
    actual = stroke.tool_state
    assert actual["width"] == pytest.approx(width)
    assert actual["hardness"] == pytest.approx(0.48)
    assert actual["grain"] == pytest.approx(0.58)
    assert actual["pencil_grade"] == "4B"
    recorded = actual["provenance"]["metadata"]["markmaking"]
    assert recorded["resolved_tool_state"]["width"] == pytest.approx(width)
    assert recorded["resolved_tool_state"]["hardness"] == pytest.approx(actual["hardness"])
    assert recorded["resolved_tool_state"]["grain"] == pytest.approx(actual["grain"])
    assert recorded["tool_overrides"]["width"] == pytest.approx(width)
    assert recorded["grade"] == actual["pencil_grade"]
    assert recorded["digest"] == sha256_obj({k: v for k, v in recorded.items() if k != "digest"})


def test_partial_override_preserves_broad_graphite_material_and_provenance(tmp_path: Path):
    session = _session(tmp_path)
    mark = resolve_mark_for_intent(session.intent, "value", tool_preset="broad-graphite")
    kwargs = mark.draw_kwargs()
    original = deepcopy(kwargs)
    sid = session.draw(
        [(10, 10), (20, 24), (34, 48)],
        part="hair-shadow", tool_overrides={"width": 22.0}, **kwargs,
    )
    assert kwargs == original  # never modify the caller's resolved mark
    _assert_reconciled(session.current_stroke(sid), width=22.0)
    stored = session.current_stroke(sid).tool_state["provenance"]["metadata"]["markmaking"]
    assert stored["digest"] != mark.digest()  # new effective material, new provenance

    checkpoint = session.checkpoint()
    resumed = DrawingSession.resume(checkpoint, subject=session.subject)
    _assert_reconciled(resumed.current_stroke(sid), width=22.0)
    assert resumed.drawing_state_hash() == session.drawing_state_hash()


def test_resolver_time_modifiers_produce_matching_executed_state(tmp_path: Path):
    session = _session(tmp_path)
    mark = resolve_mark_for_intent(
        session.intent, "value", tool_preset="broad-graphite",
        modifiers={"width": 6.0, "pressure": 0.40, "opacity": 0.45},
    )
    sid = session.draw([(10, 10), (30, 28), (50, 50)], part="hair-shadow", **mark.draw_kwargs())
    actual = session.current_stroke(sid).tool_state
    assert actual["width"] == pytest.approx(6.0)
    assert actual["pressure"] == pytest.approx(0.40)
    assert actual["opacity"] == pytest.approx(0.45)
    _assert_reconciled(session.current_stroke(sid), width=6.0)
    assert actual["provenance"]["metadata"]["markmaking"]["digest"] == mark.digest()


def test_draw_many_partial_override_keeps_material_and_isolation(tmp_path: Path):
    session = _session(tmp_path)
    mark = resolve_mark_for_intent(session.intent, "value", tool_preset="broad-graphite")
    kwargs = mark.draw_kwargs()
    strokes = [
        {"points": [(10, 10), (25, 25)], **kwargs, "part": "hair-left", "tool_overrides": {"width": 12.0}},
        {"points": [(50, 10), (70, 25)], **kwargs, "part": "hair-right"},
    ]
    ids = session.draw_many(strokes)
    _assert_reconciled(session.current_stroke(ids[0]), width=12.0)
    _assert_reconciled(session.current_stroke(ids[1]), width=8.0)


def test_conflicting_resolved_mark_role_is_rejected_without_mutation(tmp_path: Path):
    session = _session(tmp_path)
    mark = resolve_mark_for_intent(session.intent, "value", tool_preset="broad-graphite")
    kwargs = mark.draw_kwargs()
    before = session.history_cursor
    with pytest.raises(ValueError, match="semantic_role"):
        session.draw([(10, 10), (20, 20)], role="hair", tool=kwargs["tool"],
                     metadata=kwargs["metadata"])
    assert session.history_cursor == before



def test_tonal_area_plan_records_observed_ownership_in_stroke_history(tmp_path: Path):
    from img2drawing.authoring import TonalAreaPlan

    area = TonalAreaPlan(
        area_id="hair-left-shadow",
        part="hair",
        reference_evidence="dark underlayer around preserved highlight",
        boundary=((5, 5), (55, 5), (50, 60), (10, 55)),
        direction_degrees=190.0,
        target_density=0.48,
        target_value=0.56,
        pressure_range=(0.2, 0.6),
        highlight_reserves=(((20, 18), (28, 20), (24, 45)),),
    )
    assert area.direction_degrees == pytest.approx(10.0)
    mark_session = _session(tmp_path)
    mark = resolve_mark_for_intent(mark_session.intent, "value", tool_preset="broad-graphite")
    sid = mark_session.draw(
        [(12, 12), (27, 32), (44, 53)], part="hair",
        **mark.draw_kwargs(metadata=area.stroke_metadata(stroke_family="flow-a")),
    )
    recorded = mark_session.current_stroke(sid).tool_state["provenance"]["metadata"]
    assert recorded["tonal_area"]["area_id"] == area.area_id
    assert recorded["tonal_area"]["digest"] == area.digest()
    assert recorded["tonal_area"]["highlight_reserves"] == [[[20.0, 18.0], [28.0, 20.0], [24.0, 45.0]]]
    assert recorded["tonal_area"]["stroke_family"] == "flow-a"
    assert recorded["markmaking"]["digest"] == mark.digest()


def test_tonal_area_plan_rejects_unobserved_invalid_geometry():
    from img2drawing.authoring import TonalAreaPlan

    base = dict(
        area_id="hair-a", part="hair", reference_evidence="observed clump",
        boundary=((0, 0), (10, 0), (10, 10)),
        direction_degrees=45.0, target_density=0.4,
        target_value=0.5, pressure_range=(0.2, 0.6),
    )
    with pytest.raises(ValueError, match="boundary"):
        TonalAreaPlan(**{**base, "boundary": ((0, 0), (1, 1), (2, 2))})
    with pytest.raises(ValueError, match="target_density"):
        TonalAreaPlan(**{**base, "target_density": 1.5})
    with pytest.raises(ValueError, match="pressure_range"):
        TonalAreaPlan(**{**base, "pressure_range": (0.8, 0.3)})


def test_invalid_per_call_material_fails_before_persistence(tmp_path: Path):
    session = _session(tmp_path)
    mark = resolve_mark_for_intent(session.intent, "value", tool_preset="broad-graphite")
    before = session.history_cursor
    with pytest.raises(ValueError, match="unknown|unsupported|hardness"):
        session.draw([(10, 10), (20, 20)], tool_overrides={"not_a_field": 99}, **mark.draw_kwargs())
    assert session.history_cursor == before
