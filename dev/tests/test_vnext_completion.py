from __future__ import annotations

import json
import importlib.util
from pathlib import Path

import pytest
from PIL import Image

from img2drawing import DrawingIntent, DrawingSession, FinishRecord


ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "dev" / "fixtures" / "vnext-b10" / "run.py"


def _subject(tmp_path: Path) -> Path:
    tmp_path.mkdir(parents=True, exist_ok=True)
    path = tmp_path / "subject.png"
    Image.new("RGB", (64, 64), (242, 241, 236)).save(path)
    return path


def _ready_session(tmp_path: Path) -> tuple[DrawingSession, str]:
    session = DrawingSession.create(
        subject=_subject(tmp_path),
        output_dir=tmp_path / "run",
        intent=DrawingIntent(finish_intent="pose"),
    )
    session.draw(((8, 8), (28, 30), (40, 54)), part="whole_pose/weight_path")
    session.inspect()
    return session, session.inspection_history[-1]["inspection_id"]


def _finish(session: DrawingSession, inspection_id: str) -> FinishRecord:
    return session.finish(
        final_inspection_id=inspection_id,
        rationale="Agent finds no material pose residual in the current inspection",
        accepted_limitations=("facial features intentionally omitted for pose finish",),
        unresolved_nonmaterial_notes=("paper texture is outside this mechanical fixture",),
    )


def _load_fixture():
    spec = importlib.util.spec_from_file_location("img2drawing_vnext_b10_fixture", FIXTURE)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_finish_record_binds_current_intent_state_cursor_and_inspection(tmp_path: Path) -> None:
    session, inspection_id = _ready_session(tmp_path)
    record = _finish(session, inspection_id)

    assert record.intent_digest == session.intent.digest()
    assert record.drawing_state_hash == session.drawing_state_hash()
    assert record.history_cursor == session.history_cursor
    assert record.final_inspection_id == inspection_id
    assert session.finish_record == record
    assert session.finish_is_current
    assert session.finish_metadata == record.to_dict()

    payload = json.loads(session.checkpoint_path.read_text(encoding="utf-8"))
    assert payload["finish_record"] == record.to_dict()
    assert payload["finish_metadata"] is None
    resumed = DrawingSession.resume(session.checkpoint_path, subject=session.subject)
    assert resumed.finish_record == record
    assert resumed.finish_is_current


def test_material_mutation_preserves_record_but_makes_it_stale(tmp_path: Path) -> None:
    session, inspection_id = _ready_session(tmp_path)
    record = _finish(session, inspection_id)
    session.draw(((42, 12), (50, 28)), part="pose/correction")

    assert session.finish_record == record
    assert not session.finish_is_current
    resumed = DrawingSession.resume(session.checkpoint_path, subject=session.subject)
    assert resumed.finish_record == record
    assert not resumed.finish_is_current
    with pytest.raises(ValueError, match="stale"):
        session.finish(
            final_inspection_id=inspection_id,
            rationale="must not reuse pre-edit evidence",
        )


def test_intent_change_requires_a_new_inspection_before_refinish(tmp_path: Path) -> None:
    session, inspection_id = _ready_session(tmp_path)
    _finish(session, inspection_id)
    session.set_intent(DrawingIntent(finish_intent="subject"), reason="recognition is now material")
    assert not session.finish_is_current
    with pytest.raises(ValueError, match="predates the current intent"):
        session.finish(
            final_inspection_id=inspection_id,
            rationale="old inspection cannot support changed intent",
        )

    session.inspect()
    next_record = session.finish(
        final_inspection_id="000002",
        rationale="Agent reviewed the same drawing against the changed subject intent",
    )
    assert next_record.intent_digest == session.intent.digest()
    assert next_record.record_id == "finish-000002"
    assert session.finish_is_current


def test_finish_rejects_missing_old_or_uninspected_truth(tmp_path: Path) -> None:
    subject = _subject(tmp_path)
    no_intent = DrawingSession.create(subject=subject, output_dir=tmp_path / "no-intent")
    no_intent.inspect()
    with pytest.raises(ValueError, match="declared DrawingIntent"):
        no_intent.finish(final_inspection_id="000001", rationale="not enough provenance")

    no_inspection = DrawingSession.create(
        subject=subject,
        output_dir=tmp_path / "no-inspection",
        intent=DrawingIntent(),
    )
    with pytest.raises(ValueError, match="fresh inspection"):
        no_inspection.finish(final_inspection_id="000001", rationale="not inspected")

    session, first = _ready_session(tmp_path / "ready")
    session.inspect()
    with pytest.raises(ValueError, match="latest inspection"):
        session.finish(final_inspection_id=first, rationale="ignore newer evidence")
    with pytest.raises(TypeError, match="arbitrary finish metadata"):
        session.finish({"agent_decision": "unbound legacy claim"})


def test_open_residual_cannot_be_hidden_as_an_accepted_limitation(tmp_path: Path) -> None:
    session = DrawingSession.create(
        subject=_subject(tmp_path),
        output_dir=tmp_path / "run",
        intent=DrawingIntent(finish_intent="subject"),
    )
    observation_id = session.observe({"hand": "pocket contact unresolved"})
    stroke_id = session.draw(
        ((10, 12), (34, 38)),
        part="arm",
        observation_id=observation_id,
    )
    session.inspect()
    session.record_residual(
        observation_id=observation_id,
        observation="forearm-to-pocket contact is not resolved",
        scope="hands_and_feet/pocket_contact",
        severity="material",
        impact_rationale="subject finish depends on the visible contact",
        responsible_premise="arm termination",
        responsible_stroke_ids=(stroke_id,),
        planned_edit="redraw the visible termination at the pocket opening",
        before_inspection_id="000001",
    )
    with pytest.raises(ValueError, match="all material residuals"):
        session.finish(
            final_inspection_id="000001",
            rationale="must not certify an open material residual",
            accepted_limitations=("arm contact remains unresolved",),
        )


def test_finish_record_strictness_and_checkpoint_tampering(tmp_path: Path) -> None:
    session, inspection_id = _ready_session(tmp_path)
    record = _finish(session, inspection_id)
    with pytest.raises(ValueError, match="lifecycle/verdict fields"):
        FinishRecord.from_dict({**record.to_dict(), "verdict": "PASS"})
    with pytest.raises(ValueError, match="unsupported fields"):
        FinishRecord.from_dict({**record.to_dict(), "likeness": 0.9})

    payload = json.loads(session.checkpoint_path.read_text(encoding="utf-8"))
    payload["finish_record"]["intent_digest"] = "0" * 64
    session.checkpoint_path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="intent digest does not match"):
        DrawingSession.resume(session.checkpoint_path, subject=session.subject)


def test_resume_rejects_correlated_finish_source_tampering(tmp_path: Path) -> None:
    session, inspection_id = _ready_session(tmp_path)
    _finish(session, inspection_id)
    base = json.loads(session.checkpoint_path.read_text(encoding="utf-8"))

    tampered = json.loads(json.dumps(base))
    tampered["finish_record"]["intent_digest"] = "0" * 64
    tampered["inspection_history"][-1]["intent_digest"] = "0" * 64
    session.checkpoint_path.write_text(json.dumps(tampered), encoding="utf-8")
    with pytest.raises(ValueError, match="no prior provenance"):
        DrawingSession.resume(session.checkpoint_path, subject=session.subject)

    tampered = json.loads(json.dumps(base))
    tampered["finish_record"]["history_cursor"] = 999
    tampered["inspection_history"][-1]["history_cursor"] = 999
    session.checkpoint_path.write_text(json.dumps(tampered), encoding="utf-8")
    with pytest.raises(ValueError, match="exceeds action history"):
        DrawingSession.resume(session.checkpoint_path, subject=session.subject)

    tampered = json.loads(json.dumps(base))
    tampered["finish_record"]["final_inspection_id"] = "999999"
    session.checkpoint_path.write_text(json.dumps(tampered), encoding="utf-8")
    with pytest.raises(ValueError, match="unknown final inspection"):
        DrawingSession.resume(session.checkpoint_path, subject=session.subject)


def test_finish_rolls_back_when_checkpoint_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    session, inspection_id = _ready_session(tmp_path)

    def fail_checkpoint(path: Path) -> None:
        raise OSError("checkpoint storage unavailable")

    monkeypatch.setattr(session, "_write_checkpoint", fail_checkpoint)
    with pytest.raises(OSError, match="checkpoint storage unavailable"):
        _finish(session, inspection_id)
    assert session.finish_record is None
    assert not session.finish_is_current


def test_legacy_finish_metadata_resumes_as_noncanonical_history(tmp_path: Path) -> None:
    session = DrawingSession.create(subject=_subject(tmp_path), output_dir=tmp_path / "run")
    payload = json.loads(session.checkpoint_path.read_text(encoding="utf-8"))
    payload.pop("finish_record")
    payload["finish_metadata"] = {"agent_decision": "pre-B10 unbound metadata"}
    session.checkpoint_path.write_text(json.dumps(payload), encoding="utf-8")

    resumed = DrawingSession.resume(session.checkpoint_path, subject=session.subject)
    assert resumed.finish_record is None
    assert resumed.finish_metadata == {"agent_decision": "pre-B10 unbound metadata"}
    assert not resumed.finish_is_current


def test_deterministic_fixture_exercises_premature_and_stale_paths(tmp_path: Path) -> None:
    trace = _load_fixture().run_fixture(tmp_path / "fixture")
    assert trace["quality_claim"] == "mechanical-only"
    assert trace["first_current"]
    assert trace["stale_after_mutation"]
    assert trace["resumed_stale"]
    assert trace["second_current"]
    assert trace["stale_after_intent_change"]
    assert "fresh inspection" in trace["premature_error"]
    assert "stale" in trace["stale_inspection_error"]
    assert "predates the current intent" in trace["old_intent_error"]
