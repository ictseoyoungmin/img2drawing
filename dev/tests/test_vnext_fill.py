"""Retired fill-region surface and compact canonical stroke serialization."""

import json
from pathlib import Path

import pytest

import img2drawing
from img2drawing import DrawingSession, PoseObservation, available_values, resolve_tone
from img2drawing.core import AgentDrawingSession, DrawingAction
from img2drawing.core.history import CanvasAction, CanvasHistory


def _session(tmp_path: Path, subject: Path) -> DrawingSession:
    session = DrawingSession.create(subject=subject, output_dir=Path(tmp_path) / "out")
    session.observe(
        PoseObservation(
            support_side="left",
            flow="down",
            head_ribcage_pelvis="stacked",
            shoulder_pelvis="level",
        ),
        observation_id="observation-0001",
    )
    return session


@pytest.fixture
def subject(tmp_path: Path) -> Path:
    from PIL import Image

    path = tmp_path / "subject.png"
    Image.new("RGB", (240, 240), "white").save(path)
    return path


def test_fill_region_public_surface_is_retired():
    for name in ("FillRegion", "ReservedLight", "expand_fill", "replace_fill_region"):
        assert not hasattr(img2drawing, name)
    for name in ("fill_region", "replace_fill_region", "current_fill_region"):
        assert not hasattr(DrawingSession, name)


def test_fill_action_kinds_are_rejected():
    for kind in ("fill_region", "replace_fill_region"):
        with pytest.raises(ValueError, match="unknown drawing action kind"):
            DrawingAction.from_dict({
                "action_id": "retired",
                "kind": kind,
                "stage": "retired",
            })


def test_retired_region_history_fails_closed_in_current_runtime():
    history = CanvasHistory(64, 64)
    history.actions = [
        CanvasAction(
            seq=1,
            action="region.fill",
            stage="retired",
            payload={"region": {"fill_id": "legacy-fill"}},
            logical_time=0.0,
        )
    ]
    history.cursor = 1
    with pytest.raises(ValueError, match="unsupported replay action: region.fill"):
        history.state_at()


def test_tone_scale_remains_available_without_region_authoring():
    values = available_values()
    assert list(values) == sorted(values, reverse=True)
    assert min(values) <= 40
    assert resolve_tone(120).measured == pytest.approx(120.0, abs=12)
    with pytest.raises(ValueError):
        resolve_tone(-1)


def test_derived_pressure_is_not_persisted_but_is_restored(tmp_path, subject):
    session = _session(tmp_path, subject)
    session.draw([(10, 10), (60, 60), (120, 30)], part="axis", observation_id="observation-0001")
    payload = json.loads(session.checkpoint_path.read_text())
    stored = payload["history"]["actions"][0]["payload"]["stroke"]
    assert stored["pressure"] is None
    restored = session.current_ir().strokes[0]
    assert restored.pressure is not None and len(restored.pressure) == 3


def test_authored_pressure_is_preserved_verbatim(tmp_path, subject):
    session = _session(tmp_path, subject)
    session.draw(
        [(10, 10), (60, 60), (120, 30)],
        part="axis",
        observation_id="observation-0001",
        pressure=[0.11, 0.62, 0.24],
    )
    payload = json.loads(session.checkpoint_path.read_text())
    stored = payload["history"]["actions"][0]["payload"]["stroke"]
    assert stored["pressure"] == [0.11, 0.62, 0.24]


def test_tool_state_is_stored_once_per_action(tmp_path, subject):
    session = _session(tmp_path, subject)
    session.draw([(10, 10), (60, 60)], part="axis", observation_id="observation-0001")
    action = json.loads(session.checkpoint_path.read_text())["history"]["actions"][0]
    assert action["tool_state"]
    assert action["payload"]["stroke"].get("tool_state") is None
    assert session.current_ir().strokes[0].tool_state["pencil_grade"]


def test_legacy_inline_pressure_stroke_history_still_loads(tmp_path, subject):
    from img2drawing import drawing_state_hash
    from img2drawing.core.session import sha256_obj

    session = _session(tmp_path, subject)
    session.draw([(10, 10), (60, 60), (120, 30)], part="axis", observation_id="observation-0001")
    raw = json.loads(session.checkpoint_path.read_text())
    stroke = raw["history"]["actions"][0]["payload"]["stroke"]
    stroke["pressure"] = [0.4, 0.9, 0.3]
    stroke["tool_state"] = raw["history"]["actions"][0]["tool_state"]

    agent = AgentDrawingSession.from_dict({
        "schema": "img2drawing.agent_drawing_session.v1",
        "history": raw["history"],
        "executed_action_ids": raw.get("executed_action_ids", []),
    })
    raw["digests"]["drawing_state_hash"] = drawing_state_hash(
        DrawingSession._stage_free_projection(agent.current_ir())
    )
    raw["digests"]["action_log_sha256"] = sha256_obj([a.to_dict() for a in agent.history.actions])
    path = tmp_path / "legacy-stroke.json"
    path.write_text(json.dumps(raw))

    revived = DrawingSession.resume(path, subject=subject, output_dir=tmp_path / "out2")
    assert revived.current_ir().strokes[0].pressure == [0.4, 0.9, 0.3]
