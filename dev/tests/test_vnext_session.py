from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest
from PIL import Image, ImageDraw

from img2drawing.inspection import Registration
from img2drawing.vnext import DrawingSession


def _subject(tmp_path: Path) -> Path:
    image = Image.new("RGB", (96, 72), (232, 231, 226))
    draw = ImageDraw.Draw(image)
    draw.ellipse((28, 8, 58, 38), fill=(80, 82, 84))
    draw.line((42, 35, 42, 62), fill=(50, 51, 53), width=3)
    path = tmp_path / "subject.png"
    image.save(path)
    return path


def _points(index: int) -> list[tuple[float, float]]:
    return [(8.0 + index * 2.0, 8.0), (18.0 + index * 2.0, 22.0), (28.0 + index * 2.0, 36.0)]


def test_vnext_import_does_not_load_legacy_stage_workflow():
    source_root = str(Path(__file__).parents[2] / "skills" / "img2drawing" / "src")
    code = """
import sys
from img2drawing.vnext import DrawingSession
assert DrawingSession.__name__ == 'DrawingSession'
assert 'img2drawing.run' not in sys.modules
assert 'img2drawing.stages' not in sys.modules
"""
    result = subprocess.run(
        [sys.executable, "-c", code],
        check=True,
        capture_output=True,
        text=True,
        env={"PYTHONPATH": source_root},
    )
    assert result.stdout == ""


def test_stage_free_session_supports_ten_strokes_edits_and_auto_checkpoint(tmp_path: Path):
    subject = _subject(tmp_path)
    output = tmp_path / "run"
    session = DrawingSession.create(subject=subject, output_dir=output, session_id="ten-strokes")

    stroke_ids = [session.draw(_points(index), part=f"part-{index}") for index in range(10)]
    assert len(session.current_ir().strokes) == 10
    assert all(stroke.stage is None for stroke in session.current_ir().strokes)
    assert session.checkpoint_path.is_file()

    replaced_id = session.replace_stroke(
        stroke_ids[0], [(8.0, 8.0), (20.0, 20.0), (32.0, 36.0)], reason="macro placement correction"
    )
    assert replaced_id != stroke_ids[0]
    session.replace_segment(
        stroke_ids[1], 0, 2, [(10.0, 8.0), (24.0, 20.0)], reason="local contour correction"
    )
    before_lift = session.current_ir().strokes[2].opacity
    lift_action_id = session.soft_lift(stroke_ids[2], strength=0.5, reason="reduce misplaced mark")
    assert lift_action_id.startswith("vnext-")
    assert session.current_ir().strokes[2].opacity < before_lift
    delete_action_id = session.delete_stroke(stroke_ids[3], reason="remove duplicate mark")
    assert delete_action_id.startswith("vnext-")
    assert len(session.current_ir().strokes) == 9

    checkpoint = json.loads(session.checkpoint_path.read_text(encoding="utf-8"))
    assert checkpoint["schema"] == "img2drawing.vnext.session.v2"
    assert checkpoint["subject"] == {
        "name": "subject.png",
        "sha256": hashlib.sha256(subject.read_bytes()).hexdigest(),
    }
    assert str(tmp_path) not in session.checkpoint_path.read_text(encoding="utf-8")
    assert all(action["stage"] == "__vnext_compat__" for action in checkpoint["history"]["actions"])
    assert checkpoint["digests"]["drawing_state_hash"] == session.drawing_state_hash()


def test_draw_many_allocates_unique_action_ids_in_one_atomic_batch(tmp_path: Path):
    session = DrawingSession.create(subject=_subject(tmp_path), output_dir=tmp_path / "run")
    assert len(session.draw_many([_points(0), _points(1), _points(2)])) == 3
    checkpoint = json.loads(session.checkpoint_path.read_text(encoding="utf-8"))
    action_ids = [action["provenance"]["action_id"] for action in checkpoint["history"]["actions"]]
    assert action_ids == ["vnext-000001", "vnext-000002", "vnext-000003"]


def test_mutation_rolls_back_when_atomic_checkpoint_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    session = DrawingSession.create(subject=_subject(tmp_path), output_dir=tmp_path / "run")
    before_hash = session.drawing_state_hash()
    before_cursor = session.history_cursor

    def fail_checkpoint(path):
        raise OSError("checkpoint storage unavailable")

    monkeypatch.setattr(session, "_write_checkpoint", fail_checkpoint)
    with pytest.raises(OSError, match="checkpoint storage unavailable"):
        session.draw([(2.0, 2.0), (10.0, 10.0)])

    assert session.history_cursor == before_cursor
    assert session.drawing_state_hash() == before_hash
    assert not session.current_ir().strokes


def test_inspect_binds_current_snapshot_and_raster_without_arbitrary_pairing(tmp_path: Path):
    subject = _subject(tmp_path)
    output = tmp_path / "run"
    session = DrawingSession.create(subject=subject, output_dir=output)
    session.draw([(12.0, 12.0), (30.0, 28.0), (50.0, 48.0)])

    sheet = session.inspect(registration=Registration.identity((96, 72)))
    manifest_path = output / "inspections" / "000001" / "inspection.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    raw = output / "inspections" / "000001" / "raw_drawing.png"
    assert sheet.drawing_state_hash == session.drawing_state_hash()
    assert manifest["drawing_state_hash"] == session.drawing_state_hash()
    assert manifest["drawing_artifact_sha256"] == hashlib.sha256(raw.read_bytes()).hexdigest()
    assert manifest["inputs"] == {"subject": "subject.png", "drawing": "raw_drawing.png"}
    assert session.inspection_history[0] == {
        "inspection_id": "000001",
        "manifest": "inspections/000001/inspection.json",
        "drawing_state_hash": sheet.drawing_state_hash,
        "drawing_artifact_sha256": sheet.drawing_artifact_sha256,
        "history_cursor": 1,
        "intent_digest": None,
        "reference_authority_digest": session.reference_authority.digest(),
    }
    with pytest.raises(TypeError):
        session.inspect(drawing=raw, drawing_state_hash="0" * 64)  # type: ignore[call-arg]


def test_repeated_inspections_are_append_only_and_keep_prior_bytes(tmp_path: Path):
    subject = _subject(tmp_path)
    output = tmp_path / "run"
    session = DrawingSession.create(subject=subject, output_dir=output)
    session.draw([(8.0, 8.0), (24.0, 24.0)])
    session.inspect()
    first_dir = output / "inspections" / "000001"
    first_bytes = {path.name: path.read_bytes() for path in first_dir.iterdir() if path.is_file()}
    first_manifest = json.loads((first_dir / "inspection.json").read_text(encoding="utf-8"))

    session.draw([(40.0, 8.0), (56.0, 24.0)])
    session.inspect()
    second_dir = output / "inspections" / "000002"
    second_manifest = json.loads((second_dir / "inspection.json").read_text(encoding="utf-8"))

    assert first_dir != second_dir
    assert {path.name: path.read_bytes() for path in first_dir.iterdir() if path.is_file()} == first_bytes
    assert first_manifest["drawing_state_hash"] == session.inspection_history[0]["drawing_state_hash"]
    assert first_manifest["drawing_artifact_sha256"] == hashlib.sha256(
        (first_dir / "raw_drawing.png").read_bytes()
    ).hexdigest()
    assert first_manifest["drawing_artifact_sha256"] == session.inspection_history[0]["drawing_artifact_sha256"]
    assert second_manifest["drawing_state_hash"] == session.inspection_history[1]["drawing_state_hash"]
    assert second_manifest["drawing_artifact_sha256"] == hashlib.sha256(
        (second_dir / "raw_drawing.png").read_bytes()
    ).hexdigest()
    assert second_manifest["drawing_artifact_sha256"] == session.inspection_history[1]["drawing_artifact_sha256"]
    assert first_manifest["drawing_state_hash"] != second_manifest["drawing_state_hash"]
    assert session.inspection_history[0]["manifest"] != session.inspection_history[1]["manifest"]


def test_subject_mutation_is_rejected_by_session_provenance(tmp_path: Path):
    subject = _subject(tmp_path)
    session = DrawingSession.create(subject=subject, output_dir=tmp_path / "run")
    subject.write_bytes(subject.read_bytes() + b"changed")
    with pytest.raises(ValueError, match="subject changed"):
        session.inspect()


def test_inspection_history_rolls_back_when_checkpoint_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    subject = _subject(tmp_path)
    session = DrawingSession.create(subject=subject, output_dir=tmp_path / "run")
    session.draw([(4.0, 4.0), (16.0, 16.0)])
    session.inspect()
    first_dir = tmp_path / "run" / "inspections" / "000001"
    first_bytes = {path.name: path.read_bytes() for path in first_dir.iterdir() if path.is_file()}
    session.draw([(24.0, 4.0), (36.0, 16.0)])

    def fail_checkpoint(path):
        raise OSError("checkpoint storage unavailable")

    monkeypatch.setattr(session, "_write_checkpoint", fail_checkpoint)
    with pytest.raises(OSError, match="checkpoint storage unavailable"):
        session.inspect()
    assert [record["inspection_id"] for record in session.inspection_history] == ["000001"]
    assert {path.name: path.read_bytes() for path in first_dir.iterdir() if path.is_file()} == first_bytes
    assert not (tmp_path / "run" / "inspections" / "000002").exists()
    assert not any(path.name.startswith(".000002.") for path in (tmp_path / "run" / "inspections").iterdir())


def test_checkpoint_resume_preserves_state_and_inspection_continuity(tmp_path: Path):
    subject = _subject(tmp_path)
    output = tmp_path / "run"
    session = DrawingSession.create(subject=subject, output_dir=output, session_id="resume-me")
    session.observe({"weight": "image-left", "uncertain": ["far elbow"]}, observation_id="obs-1")
    session.draw([(10.0, 10.0), (40.0, 32.0), (52.0, 50.0)], observation_id="obs-1")
    session.inspect(registration=Registration.identity((96, 72)))
    session.draw([(56.0, 14.0), (68.0, 30.0)])
    session.inspect(registration=Registration.identity((96, 72)))
    expected_hash = session.drawing_state_hash()
    checkpoint = session.checkpoint()

    resumed = DrawingSession.resume(checkpoint, subject=subject)
    assert resumed.session_id == "resume-me"
    assert resumed.drawing_state_hash() == expected_hash
    assert resumed.history_cursor == session.history_cursor
    assert resumed.inspection_history == session.inspection_history
    assert [record["inspection_id"] for record in resumed.inspection_history] == ["000001", "000002"]
    assert all((output / record["manifest"]).is_file() for record in resumed.inspection_history)
    resumed.draw([(60.0, 12.0), (72.0, 28.0)])
    assert resumed.history_cursor == session.history_cursor + 1
    assert json.loads(checkpoint.read_text(encoding="utf-8"))["digests"]["drawing_state_hash"] == resumed.drawing_state_hash()


def test_resume_rejects_mutated_historical_inspection_artifact(tmp_path: Path):
    subject = _subject(tmp_path)
    output = tmp_path / "run"
    session = DrawingSession.create(subject=subject, output_dir=output)
    session.draw([(10.0, 10.0), (28.0, 24.0)])
    session.inspect()
    session.draw([(40.0, 10.0), (58.0, 24.0)])
    session.inspect()
    checkpoint = session.checkpoint()
    first_manifest = output / "inspections" / "000001" / "inspection.json"
    manifest = json.loads(first_manifest.read_text(encoding="utf-8"))
    manifest["drawing_state_hash"] = "0" * 64
    first_manifest.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(ValueError, match="inspection state digest mismatch"):
        DrawingSession.resume(checkpoint, subject=subject)




def test_observation_ids_are_unique_and_must_be_known_to_draw(tmp_path: Path):
    session = DrawingSession.create(subject=_subject(tmp_path), output_dir=tmp_path / "run")
    session.observe({"flow": "left"}, observation_id="obs-1")
    with pytest.raises(ValueError, match="duplicate observation_id"):
        session.observe({"flow": "right"}, observation_id="obs-1")
    with pytest.raises(ValueError, match="unknown observation_id"):
        session.draw([(2.0, 2.0), (8.0, 8.0)], observation_id="missing")
    session.draw([(2.0, 2.0), (8.0, 8.0)])


def test_custom_checkpoint_path_records_actual_filename(tmp_path: Path):
    subject = _subject(tmp_path)
    session = DrawingSession.create(subject=subject, output_dir=tmp_path / "run")
    special = tmp_path / "special.json"
    assert session.checkpoint(special) == special
    payload = json.loads(special.read_text(encoding="utf-8"))
    assert payload["artifacts"]["checkpoint"] == "special.json"
    assert payload["artifacts"]["inspection_root"] == "run"
    session.draw([(2.0, 2.0), (8.0, 8.0)])
    assert json.loads(special.read_text(encoding="utf-8"))["artifacts"]["checkpoint"] == "special.json"
    assert DrawingSession.resume(special, subject=subject)
