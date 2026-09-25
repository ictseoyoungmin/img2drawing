"""Fill-region retirement hardening and stroke-history continuity."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image

import img2drawing
from img2drawing import DrawingSession, PoseObservation
from img2drawing.core import AgentDrawingSession
from img2drawing.core.digest import sha256_obj
from img2drawing.session import ELEMENT_TYPES


def _subject(tmp_path: Path) -> Path:
    path = tmp_path / "subject.png"
    Image.new("RGB", (240, 240), "white").save(path)
    return path


def _session(tmp_path: Path) -> tuple[DrawingSession, str]:
    subject = _subject(tmp_path)
    session = DrawingSession.create(subject=subject, output_dir=tmp_path / "out")
    oid = session.observe(
        PoseObservation(
            support_side="left",
            flow="down",
            head_ribcage_pelvis="stacked",
            shoulder_pelvis="level",
        ),
        observation_id="observation-0001",
    )
    return session, oid


def test_authoring_element_model_is_stroke_only():
    assert ELEMENT_TYPES == ("stroke",)


def test_removed_fill_names_are_not_lazy_compatibility_shims():
    for name in ("FillRegion", "ReservedLight", "expand_fill", "replace_fill_region"):
        assert name not in dir(img2drawing)
        try:
            getattr(img2drawing, name)
        except AttributeError:
            pass
        else:
            raise AssertionError(f"retired fill surface leaked through root compatibility: {name}")


def test_post_compaction_checkpoint_keeps_its_existing_visual_digest(tmp_path):
    session, oid = _session(tmp_path)
    session.draw([(10, 10), (60, 60), (120, 30)], part="axis", observation_id=oid)
    saved = json.loads(session.checkpoint_path.read_text())["digests"]["drawing_state_hash"]
    revived = DrawingSession.resume(
        session.checkpoint_path,
        subject=session.subject,
        output_dir=session.output_dir,
    )
    assert revived.drawing_state_hash() == saved


def test_pre_compaction_inline_pressure_checkpoint_resumes_without_digest_rewrite(tmp_path):
    session, oid = _session(tmp_path)
    session.draw([(10, 10), (60, 60), (120, 30)], part="axis", observation_id=oid)
    raw = json.loads(session.checkpoint_path.read_text())

    current = session.current_ir().to_dict()
    current["metadata"].pop("history_cursor", None)
    for stroke in current["strokes"]:
        stroke.pop("stage", None)
        stroke.pop("pressure_authored", None)
    pre_compaction_visual_digest = sha256_obj(current)

    derived = session.current_ir().strokes[0].pressure
    action = raw["history"]["actions"][0]
    action["payload"]["stroke"]["pressure"] = list(derived)
    action["payload"]["stroke"]["tool_state"] = action["tool_state"]
    raw["digests"]["drawing_state_hash"] = pre_compaction_visual_digest

    agent = AgentDrawingSession.from_dict({
        "schema": "img2drawing.agent_drawing_session.v1",
        "history": raw["history"],
        "executed_action_ids": raw.get("executed_action_ids", []),
    })
    raw["digests"]["action_log_sha256"] = sha256_obj(
        [item.to_dict() for item in agent.history.actions]
    )

    legacy = tmp_path / "pre_compaction.checkpoint.json"
    legacy.write_text(json.dumps(raw), encoding="utf-8")
    revived = DrawingSession.resume(
        legacy,
        subject=session.subject,
        output_dir=tmp_path / "revived",
    )
    assert revived.drawing_state_hash() == pre_compaction_visual_digest
    assert revived.current_ir().strokes[0].pressure == list(derived)


def test_value_is_authored_as_explicit_strokes_not_region_expansion(tmp_path):
    session, oid = _session(tmp_path)
    before = session.history_cursor
    ids = session.draw_many(
        [
            {
                "points": [(30, 80), (210, 80)],
                "role": "value",
                "part": "coat-shadow",
                "observation_id": oid,
                "source_observation": "observed shadow family",
            },
            {
                "points": [(30, 92), (210, 92)],
                "role": "value",
                "part": "coat-shadow",
                "observation_id": oid,
                "source_observation": "observed shadow family",
            },
        ]
    )
    assert session.history_cursor == before + 2
    assert len(ids) == 2
    assert len(session.current_ir().strokes) == 2
    assert all(action.action == "stroke.add" for action in session._agent.history.actions[-2:])
