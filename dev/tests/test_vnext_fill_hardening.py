"""Post-B07-R1 hardening: visual identity and append-only value correction."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image

from img2drawing import DrawingSession, PoseObservation, drawing_state_hash, replace_fill_region
from img2drawing.core import AgentDrawingSession
from img2drawing.core.ir import Stroke, StrokeIR
from img2drawing.core.session import sha256_obj


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


def test_pressure_authored_flag_is_not_visual_drawing_identity():
    first = StrokeIR(100, 100)
    second = StrokeIR(100, 100)
    a = Stroke(points=[(10, 10), (50, 50), (90, 20)], pressure=[0.2, 0.8, 0.3])
    b = Stroke(points=[(10, 10), (50, 50), (90, 20)], pressure=[0.2, 0.8, 0.3])
    a.pressure_authored = False
    b.pressure_authored = True
    first.add(a)
    second.add(b)
    assert drawing_state_hash(first) == drawing_state_hash(second)


def test_pre_compaction_inline_pressure_checkpoint_resumes_without_digest_rewrite(tmp_path):
    """Emulate a real pre-compaction file while preserving its old visual digest."""

    session, oid = _session(tmp_path)
    session.draw([(10, 10), (60, 60), (120, 30)], part="axis", observation_id=oid)
    raw = json.loads(session.checkpoint_path.read_text())
    untouched_visual_digest = raw["digests"]["drawing_state_hash"]

    # Old vNext persisted both the derived pressure and tool_state inline on the stroke.
    derived = session.current_ir().strokes[0].pressure
    action = raw["history"]["actions"][0]
    action["payload"]["stroke"]["pressure"] = list(derived)
    action["payload"]["stroke"]["tool_state"] = action["tool_state"]

    # The action log genuinely changed representation, so update only that digest.  A
    # compatibility test must NOT rewrite the saved visual drawing digest with new code.
    agent = AgentDrawingSession.from_dict({
        "schema": "img2drawing.agent_drawing_session.v1",
        "history": raw["history"],
        "executed_action_ids": raw.get("executed_action_ids", []),
    })
    raw["digests"]["action_log_sha256"] = sha256_obj(
        [item.to_dict() for item in agent.history.actions]
    )
    assert raw["digests"]["drawing_state_hash"] == untouched_visual_digest

    legacy = tmp_path / "pre_compaction.checkpoint.json"
    legacy.write_text(json.dumps(raw), encoding="utf-8")
    revived = DrawingSession.resume(
        legacy,
        subject=session.subject,
        output_dir=tmp_path / "revived",
    )
    assert revived.drawing_state_hash() == untouched_visual_digest
    assert revived.current_ir().strokes[0].pressure == list(derived)


def test_value_region_revision_is_one_append_only_action_and_resume_safe(tmp_path):
    session, oid = _session(tmp_path)
    fid = session.fill_region(
        [(20, 20), (220, 20), (220, 220), (20, 220)],
        value=170,
        part="coat",
        angle=74,
        observation_id=oid,
        reason="initial observed coat value",
    )
    before_hash = session.drawing_state_hash()
    before_actions = len(session._agent.history.actions)

    action_id = replace_fill_region(
        session,
        fid,
        value=70,
        reason="inspection shows the coat is materially darker",
        observation_id=oid,
    )

    assert len(session._agent.history.actions) == before_actions + 1
    assert session._agent.history.actions[-1].action == "region.replace"
    assert session._agent.history.actions[-1].payload["region"]["fill_id"] == fid
    assert session.drawing_state_hash() != before_hash
    assert action_id == session._agent.history.actions[-1].provenance["action_id"]

    revived = DrawingSession.resume(
        session.checkpoint_path,
        subject=session.subject,
        output_dir=session.output_dir,
    )
    assert revived.drawing_state_hash() == session.drawing_state_hash()
    assert revived._agent.history.current_fill_region(fid).fill_id == fid


def test_value_region_revision_action_binds_directly_to_residual_correction(tmp_path):
    session, oid = _session(tmp_path)
    fid = session.fill_region(
        [(20, 20), (220, 20), (220, 220), (20, 220)],
        value=170,
        part="coat",
        angle=74,
        observation_id=oid,
        reason="initial observed coat value",
    )
    before = session.inspect(mode="quick")
    rid = session.record_residual(
        observation_id=oid,
        observation="coat value reads too light",
        scope="coat",
        severity="high",
        impact_rationale="large value family changes the figure read",
        responsible_premise="initial coat value estimate",
        responsible_stroke_ids=(),
        planned_edit="revise the authored coat value region",
        before_inspection_id=session.inspection_history[-1]["inspection_id"],
    )

    replacement_action_id = replace_fill_region(
        session,
        fid,
        value=70,
        reason="correct the coat value from the fresh inspection",
        observation_id=oid,
    )
    session.inspect(mode="quick")
    correction = session.record_correction(
        rid,
        action_ids=[replacement_action_id],
        after_inspection_id=session.inspection_history[-1]["inspection_id"],
        rationale="darker region now matches the observed value family",
    )

    assert correction.action_ids == (replacement_action_id,)
    assert correction.before_drawing_state_hash == before.drawing_state_hash
    assert session.residual_history[-1].status == "resolved"


def test_duplicate_fill_identity_requires_revision_path(tmp_path):
    session, oid = _session(tmp_path)
    fid = session.fill_region(
        [(20, 20), (220, 20), (220, 220), (20, 220)],
        value=170,
        part="coat",
        fill_id="coat-value",
        observation_id=oid,
        reason="initial value",
    )
    assert fid == "coat-value"
    try:
        session.fill_region(
            [(20, 20), (220, 20), (220, 220), (20, 220)],
            value=70,
            part="coat",
            fill_id="coat-value",
            observation_id=oid,
            reason="do not stack another copy",
        )
    except ValueError as exc:
        assert "replace_fill_region" in str(exc)
    else:
        raise AssertionError("duplicate fill_id should require the append-only revision path")
