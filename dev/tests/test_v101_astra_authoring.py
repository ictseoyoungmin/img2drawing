from __future__ import annotations

from math import hypot

from PIL import Image
import pytest

import img2drawing
from img2drawing import DrawingIntent, DrawingSession
from img2drawing.core.tools import get_tool
from img2drawing.vnext import retune_stroke, retune_strokes, sample_catmull_rom


def _session(tmp_path):
    subject = tmp_path / "subject.png"
    Image.new("RGB", (96, 72), "white").save(subject)
    intent = DrawingIntent(
        reference_mode="observed",
        drawing_mode="line_study",
        finish_intent="subject",
        style_profile="pencil_loose",
    )
    return DrawingSession.create(subject=subject, output_dir=tmp_path, intent=intent)


def test_retune_preserves_geometry_semantics_and_curve_metadata(tmp_path) -> None:
    session = _session(tmp_path)
    controls = [[8.0, 20.0], [24.0, 8.0], [48.0, 18.0], [72.0, 12.0]]
    points = sample_catmull_rom(controls, spacing=2.5)
    stroke_id = session.draw(
        points,
        stroke_id="observed-curve",
        role="contour",
        part="connected-edge",
        confidence=0.83,
        layer=3,
        tool="form_pencil",
        tool_overrides={"width": 2.7},
        metadata={"control_points": controls, "interpolation": "catmull-rom"},
    )
    before = session.current_stroke(stroke_id)
    before_points = list(before.points)
    before_pressure = list(before.pressure or ())
    assert before.pressure_authored is False

    retune_stroke(
        session,
        stroke_id,
        reason="geometry is correct; endpoint taper makes a connected edge read broken",
        tool_overrides={"taper_in": 0.015, "taper_out": 0.025},
    )
    after = session.current_stroke(stroke_id)

    assert after.stroke_id == stroke_id
    assert list(after.points) == before_points
    assert after.role == before.role == "contour"
    assert after.part == before.part == "connected-edge"
    assert after.confidence == before.confidence == 0.83
    assert after.layer == before.layer == 3
    assert after.width == before.width == 2.7
    assert after.pressure_authored is False
    assert list(after.pressure or ()) != before_pressure
    assert after.tool_state["tool"] == "form_pencil"
    assert after.tool_state["taper_in"] == 0.015
    assert after.tool_state["taper_out"] == 0.025
    metadata = after.tool_state["provenance"]["metadata"]
    assert metadata["control_points"] == controls
    assert metadata["interpolation"] == "catmull-rom"
    assert metadata["geometry_preserved_from"] == stroke_id

    resumed = DrawingSession.resume(session.checkpoint_path)
    replayed = resumed.current_stroke(stroke_id)
    assert replayed.points == after.points
    assert replayed.role == after.role
    assert replayed.part == after.part
    assert replayed.tool_state["taper_in"] == 0.015


def test_retune_preserves_explicit_pressure(tmp_path) -> None:
    session = _session(tmp_path)
    pressure = [0.2, 0.5, 0.8, 0.4]
    stroke_id = session.draw(
        [(10, 50), (30, 42), (55, 46), (82, 38)],
        stroke_id="pressure-authored",
        role="form",
        part="edge",
        pressure=pressure,
        tool="form_pencil",
    )
    retune_stroke(
        session,
        stroke_id,
        reason="only opacity needs correction",
        tool_overrides={"opacity": 0.82},
    )
    revised = session.current_stroke(stroke_id)
    assert revised.pressure_authored is True
    assert revised.pressure == pressure
    assert revised.tool_state["opacity"] == 0.82


def test_batch_retune_preserves_each_geometry_and_explicit_history(tmp_path) -> None:
    session = _session(tmp_path)
    ids = [
        session.draw(
            [(10, 18), (30, 16), (50, 17)],
            stroke_id="edge-a",
            role="contour",
            part="joined-boundary",
            tool="form_pencil",
        ),
        session.draw(
            [(50, 17), (68, 20), (86, 18)],
            stroke_id="edge-b",
            role="contour",
            part="joined-boundary",
            tool="form_pencil",
        ),
    ]
    before = {stroke_id: list(session.current_stroke(stroke_id).points) for stroke_id in ids}
    cursor = session.history_cursor

    action_ids = retune_strokes(
        session,
        ids,
        reason="one connected boundary has premature endpoint taper",
        tool_overrides={"taper_in": 0.01, "taper_out": 0.02},
        metadata={"semantic_group": "joined-boundary"},
    )

    assert len(action_ids) == 2
    assert session.history_cursor == cursor + 2
    for stroke_id in ids:
        current = session.current_stroke(stroke_id)
        assert current.points == before[stroke_id]
        assert current.part == "joined-boundary"
        assert current.tool_state["taper_in"] == 0.01
        assert current.tool_state["taper_out"] == 0.02
        assert current.tool_state["provenance"]["metadata"]["semantic_group"] == "joined-boundary"

    with pytest.raises(ValueError, match="duplicate current stroke"):
        retune_strokes(
            session,
            [ids[0], ids[0]],
            reason="duplicate must not retune twice",
            tool_overrides={"opacity": 0.8},
        )


def test_continuous_pencil_changes_endpoint_behavior_without_global_form_change() -> None:
    form = get_tool("form_pencil")
    continuous = get_tool("continuous_pencil")
    assert form.taper_in == 0.24
    assert form.taper_out == 0.30
    assert continuous.width == form.width
    assert continuous.pressure == form.pressure
    assert continuous.opacity == form.opacity
    assert continuous.hardness == form.hardness
    assert continuous.grain == form.grain
    assert continuous.taper_in <= 0.03
    assert continuous.taper_out <= 0.03


def test_catmull_rom_sampling_is_deterministic_arc_length_bounded_and_specialized() -> None:
    controls = [(0, 0), (12, 18), (30, 10), (42, 24), (60, 20)]
    first = sample_catmull_rom(controls, spacing=3.0)
    second = sample_catmull_rom(controls, spacing=3.0)
    assert first == second
    assert first[0] == (0.0, 0.0)
    assert first[-1] == (60.0, 20.0)
    assert len(first) > len(controls)
    distances = [hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(first, first[1:])]
    assert max(distances[:-1]) < 3.5
    assert all(distance > 0 for distance in distances)

    straight = sample_catmull_rom([(0, 0), (10, 0)], spacing=2.0)
    assert straight[0] == (0.0, 0.0)
    assert straight[-1] == (10.0, 0.0)

    assert "retune_stroke" not in img2drawing.__all__
    assert "retune_strokes" not in img2drawing.__all__
    assert "sample_catmull_rom" not in img2drawing.__all__
