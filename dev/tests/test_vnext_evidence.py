from __future__ import annotations

import json
from pathlib import Path

import pytest
from PIL import Image

from img2drawing.inspection import Grid, ROI
from img2drawing.vnext import DrawingSession


def _subject(tmp_path: Path) -> Path:
    path = tmp_path / "subject.png"
    Image.new("RGB", (96, 72), (232, 231, 226)).save(path)
    return path


def _roi(label: str, left: float) -> ROI:
    return ROI(label, (left, 8.0, left + 20.0, 32.0))


def test_default_quick_sheet_records_policy_and_telemetry(tmp_path: Path):
    session = DrawingSession.create(subject=_subject(tmp_path), output_dir=tmp_path / "run")
    session.draw([(12.0, 10.0), (44.0, 48.0)])

    sheet = session.inspect()
    manifest = json.loads((tmp_path / "run" / "inspections" / "000001" / "inspection.json").read_text())

    assert sheet.evidence_policy["mode"] == "quick"
    assert manifest["evidence_policy"] == sheet.evidence_policy
    assert session.evidence_telemetry.inspection_calls == 1
    assert session.evidence_telemetry.review_turns == 1
    assert session.evidence_telemetry.generated_artifacts == 6
    assert session.evidence_telemetry.visual_artifacts == 4


def test_roi_cap_and_deep_escalation(tmp_path: Path):
    session = DrawingSession.create(subject=_subject(tmp_path), output_dir=tmp_path / "run")
    rois = tuple(_roi(f"roi-{index}", 4.0 + index * 22.0) for index in range(4))
    with pytest.raises(ValueError, match="at most 3"):
        session.inspect(rois=rois)

    with pytest.raises(ValueError, match="escalation_reason"):
        session.inspect(mode="deep", measurements=( {"kind": "distance"}, ))

    with pytest.raises(ValueError, match="quick evidence budget"):
        session.inspect(mode="quick", rois=rois[:1])
    with pytest.raises(ValueError, match="focused evidence budget"):
        session.inspect(mode="focused", rois=rois[:1], measurements=({"kind": "distance"},))
    with pytest.raises(ValueError, match="focused evidence budget"):
        session.inspect(mode="focused")
    with pytest.raises(ValueError, match="deep evidence escalation"):
        session.inspect(mode="deep")
    with pytest.raises(ValueError, match="quick evidence budget"):
        session.inspect(mode="quick", grid=Grid(columns=4, rows=4))

    sheet = session.inspect(
        mode="deep",
        rois=rois[:2],
        measurements=({"kind": "distance"},),
        escalation_reason="the first sheet leaves the arm overlap ambiguous",
    )
    assert sheet.evidence_policy["mode"] == "deep"
    assert sheet.evidence_policy["roi_count"] == 2
    assert sheet.evidence_policy["measurement_count"] == 1

    deep_with_grid = session.inspect(
        mode="deep",
        grid=Grid(columns=4, rows=4),
        escalation_reason="the relation needs a coarse balance grid",
    )
    assert deep_with_grid.evidence_policy["grid_count"] == 1


def test_reads_are_counted_and_stale_reads_marked(tmp_path: Path):
    session = DrawingSession.create(subject=_subject(tmp_path), output_dir=tmp_path / "run")
    stroke_id = session.draw([(12.0, 10.0), (44.0, 48.0)])
    session.inspect()

    current = session.record_evidence_read("000001", artifact="sheet")
    assert current.artifact == "sheet"
    assert current.stale is False
    session.replace_stroke(stroke_id, [(12.0, 10.0), (52.0, 42.0)], reason="change silhouette")
    stale = session.record_evidence_read("000001", artifact="contrast_overlay.png")
    assert stale.stale is True
    assert session.evidence_telemetry.image_reads == 2
    assert [event.event_id for event in session.evidence_telemetry.read_events] == [
        "evidence-read-000001",
        "evidence-read-000002",
    ]
    (tmp_path / "run" / "inspections" / "000001" / "registered_drawing.png").write_bytes(b"not-an-image")
    with pytest.raises(ValueError, match="evidence unreadable"):
        session.record_evidence_read("000001", artifact="registered_drawing")
    with pytest.raises(ValueError, match="evidence unreadable"):
        session.record_evidence_read("000001", artifact="does-not-exist.png")


def test_evidence_telemetry_survives_resume(tmp_path: Path):
    subject = _subject(tmp_path)
    session = DrawingSession.create(subject=subject, output_dir=tmp_path / "run")
    session.inspect()
    session.record_evidence_read("000001")

    resumed = DrawingSession.resume(session.checkpoint_path, subject=subject)
    assert resumed.evidence_telemetry.to_dict() == session.evidence_telemetry.to_dict()
    assert resumed.record_evidence_read("000001").event_id == "evidence-read-000002"


def test_resume_rejects_orphan_or_cross_bound_evidence_read(tmp_path: Path):
    subject = _subject(tmp_path)
    session = DrawingSession.create(subject=subject, output_dir=tmp_path / "run")
    session.inspect()
    session.record_evidence_read("000001", artifact="sheet")
    checkpoint = json.loads(session.checkpoint_path.read_text())

    checkpoint["evidence_telemetry"]["read_events"][0]["inspection_id"] = "999999"
    with pytest.raises(ValueError, match="unknown inspection_id"):
        session.checkpoint_path.write_text(json.dumps(checkpoint), encoding="utf-8")
        DrawingSession.resume(session.checkpoint_path, subject=subject)

    session = DrawingSession.create(subject=subject, output_dir=tmp_path / "second-run")
    session.inspect()
    session.record_evidence_read("000001", artifact="sheet")
    checkpoint = json.loads(session.checkpoint_path.read_text())
    checkpoint["evidence_telemetry"]["read_events"][0]["artifact"] = "invented-artifact"
    with pytest.raises(ValueError, match="unknown artifact"):
        session.checkpoint_path.write_text(json.dumps(checkpoint), encoding="utf-8")
        DrawingSession.resume(session.checkpoint_path, subject=subject)

    session = DrawingSession.create(subject=subject, output_dir=tmp_path / "third-run")
    session.inspect()
    session.record_evidence_read("000001", artifact="sheet")
    checkpoint = json.loads(session.checkpoint_path.read_text())
    checkpoint["evidence_telemetry"]["read_events"][0]["inspection_drawing_state_hash"] = "0" * 64
    with pytest.raises(ValueError, match="inspection digest mismatch"):
        session.checkpoint_path.write_text(json.dumps(checkpoint), encoding="utf-8")
        DrawingSession.resume(session.checkpoint_path, subject=subject)
