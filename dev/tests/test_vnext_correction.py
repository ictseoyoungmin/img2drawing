from __future__ import annotations

import json
from pathlib import Path

import pytest
from PIL import Image

from img2drawing.vnext import DrawingSession


def _subject(tmp_path: Path) -> Path:
    path = tmp_path / "subject.png"
    Image.new("RGB", (96, 72), (232, 231, 226)).save(path)
    return path


def _session(tmp_path: Path) -> tuple[DrawingSession, str, str, dict]:
    session = DrawingSession.create(subject=_subject(tmp_path), output_dir=tmp_path / "run")
    observation_id = session.observe(
        {"subject": "B05 figure", "mismatch": "near arm angle"}, observation_id="obs-arm"
    )
    stroke_id = session.draw(
        [(18.0, 10.0), (28.0, 30.0), (38.0, 54.0)],
        stroke_id="near-arm",
        part="near_arm",
        observation_id=observation_id,
    )
    session.inspect()
    return session, observation_id, stroke_id, session.inspection_history[-1]


def test_global_and_local_corrections_preserve_history_and_resume(tmp_path: Path):
    session, observation_id, stroke_id, before = _session(tmp_path)
    residual_id = session.record_residual(
        observation_id=observation_id,
        observation="near arm exits too vertically and weakens the torso overlap",
        scope="global",
        severity="high",
        impact_rationale="the dominant silhouette and depth read disagree",
        responsible_premise="near-arm depth path",
        responsible_stroke_ids=(stroke_id,),
        planned_edit="replace the arm premise with a bent foreground path",
        before_inspection_id=before["inspection_id"],
    )
    replaced = session.replace_stroke(
        stroke_id,
        [(18.0, 10.0), (39.0, 25.0), (56.0, 44.0), (44.0, 58.0)],
        reason="restore the bent near-arm overlap",
        observation_id=observation_id,
    )
    session.inspect()
    after = session.inspection_history[-1]
    correction = session.resolve_residual(
        residual_id,
        action_ids=(replaced,),
        after_inspection_id=after["inspection_id"],
        rationale="the arm now turns through the foreground torso overlap",
    )
    assert correction.action_ids == ("vnext-000002",)
    assert session.residual_history[0].status == "resolved"

    # A later local segment edit remains part of the same authoritative history.
    local_stroke = session.draw(
        [(12.0, 62.0), (25.0, 60.0), (38.0, 61.0), (52.0, 58.0), (68.0, 60.0)],
        stroke_id="ground-contour",
        part="ground",
        observation_id=observation_id,
    )
    session.inspect()
    local_before = session.inspection_history[-1]
    local_residual = session.record_residual(
        observation_id=observation_id,
        observation="ground contour kinks under the support foot",
        scope="local",
        severity="medium",
        impact_rationale="a small contour kink distracts from the weight line",
        responsible_premise=None,
        responsible_stroke_ids=(local_stroke,),
        planned_edit="replace only the middle contour segment",
        before_inspection_id=local_before["inspection_id"],
    )
    local_action = session.replace_segment(
        local_stroke,
        1,
        3,
        [(25.0, 60.0), (38.0, 59.0), (52.0, 59.0)],
        reason="smooth the support contour locally",
        observation_id=observation_id,
    )
    session.inspect()
    local_after = session.inspection_history[-1]
    local_correction = session.resolve_residual(
        local_residual,
        action_ids=(local_action,),
        after_inspection_id=local_after["inspection_id"],
        rationale="the support contour is quieter while its endpoints remain anchored",
    )
    assert local_correction.action_ids == ("vnext-000004",)
    assert len(session.current_ir().strokes) == 2
    assert session.history_cursor == 4

    checkpoint = json.loads(session.checkpoint_path.read_text(encoding="utf-8"))
    assert checkpoint["residuals"][0]["after_inspection_id"] == after["inspection_id"]
    assert checkpoint["corrections"][1]["observation_id"] == observation_id
    resumed = DrawingSession.resume(session.checkpoint_path, subject=_subject(tmp_path))
    assert [record.status for record in resumed.residual_history] == ["resolved", "resolved"]
    assert [record.action_ids for record in resumed.correction_history] == [
        ("vnext-000002",),
        ("vnext-000004",),
    ]
    assert resumed.drawing_state_hash() == session.drawing_state_hash()


def test_revise_keeps_residual_open_without_becoming_a_stage_gate(tmp_path: Path):
    session, observation_id, stroke_id, before = _session(tmp_path)
    residual_id = session.record_residual(
        observation_id=observation_id,
        observation="near arm may still be too narrow",
        scope="local",
        severity="low",
        impact_rationale="the concern is visible but not yet dominant",
        responsible_premise=None,
        responsible_stroke_ids=(stroke_id,),
        planned_edit="try a lighter local segment edit",
        before_inspection_id=before["inspection_id"],
    )
    attempt = session.replace_segment(
        stroke_id,
        0,
        2,
        [(18.0, 10.0), (31.0, 30.0), (42.0, 52.0)],
        reason="test a tentative local correction",
        observation_id=observation_id,
    )
    session.inspect()
    correction = session.record_correction(
        residual_id,
        action_ids=(attempt,),
        after_inspection_id=session.inspection_history[-1]["inspection_id"],
        decision="revise",
        rationale="the tentative edit is not accepted yet; inspect again after another premise change",
    )
    assert correction.decision == "revise"
    assert session.residual_history[0].status == "open"
    assert not hasattr(session, "current_stage")
    assert not hasattr(session, "advance")


def test_stale_residual_and_after_evidence_are_rejected(tmp_path: Path):
    session, observation_id, stroke_id, before = _session(tmp_path)
    session.draw([(55.0, 10.0), (65.0, 30.0)], observation_id=observation_id)
    with pytest.raises(ValueError, match="stale"):
        session.record_residual(
            observation_id=observation_id,
            observation="old snapshot concern",
            scope="global",
            severity="high",
            impact_rationale="old evidence must not be reused",
            responsible_premise="old premise",
            responsible_stroke_ids=(stroke_id,),
            planned_edit="inspect current state first",
            before_inspection_id=before["inspection_id"],
        )

    session.inspect()
    current = session.inspection_history[-1]
    residual_id = session.record_residual(
        observation_id=observation_id,
        observation="current concern",
        scope="global",
        severity="medium",
        impact_rationale="current evidence is required",
        responsible_premise="current premise",
        responsible_stroke_ids=(stroke_id,),
        planned_edit="replace the current premise",
        before_inspection_id=current["inspection_id"],
    )
    action = session.replace_stroke(
        stroke_id,
        [(18.0, 10.0), (35.0, 30.0), (54.0, 54.0)],
        reason="current correction",
        observation_id=observation_id,
    )
    with pytest.raises(ValueError, match="after inspection is stale"):
        session.resolve_residual(
            residual_id,
            action_ids=(action,),
            after_inspection_id=current["inspection_id"],
            rationale="must inspect after the edit",
        )


def test_resume_rejects_orphan_correction_action(tmp_path: Path):
    session, observation_id, stroke_id, before = _session(tmp_path)
    residual_id = session.record_residual(
        observation_id=observation_id,
        observation="arm premise is too narrow",
        scope="global",
        severity="high",
        impact_rationale="the overlap loses its foreground read",
        responsible_premise="near arm",
        responsible_stroke_ids=(stroke_id,),
        planned_edit="replace near arm",
        before_inspection_id=before["inspection_id"],
    )
    action = session.replace_stroke(
        stroke_id,
        [(18.0, 10.0), (42.0, 28.0), (58.0, 50.0)],
        reason="restore overlap",
        observation_id=observation_id,
    )
    session.inspect()
    session.resolve_residual(
        residual_id,
        action_ids=(action,),
        after_inspection_id=session.inspection_history[-1]["inspection_id"],
        rationale="fresh inspection accepts the overlap",
    )
    payload = json.loads(session.checkpoint_path.read_text(encoding="utf-8"))
    payload["corrections"][0]["action_ids"] = ["orphan-action"]
    session.checkpoint_path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="unknown action_id"):
        DrawingSession.resume(session.checkpoint_path, subject=_subject(tmp_path))
