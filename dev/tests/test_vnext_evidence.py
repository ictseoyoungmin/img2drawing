from __future__ import annotations

import json
from pathlib import Path

import pytest
from PIL import Image

from img2drawing.inspection import ROI
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

    sheet = session.inspect(
        mode="deep",
        rois=rois[:2],
        measurements=({"kind": "distance"},),
        escalation_reason="the first sheet leaves the arm overlap ambiguous",
    )
    assert sheet.evidence_policy["mode"] == "deep"
    assert sheet.evidence_policy["roi_count"] == 2
    assert sheet.evidence_policy["measurement_count"] == 1


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
