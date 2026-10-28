from pathlib import Path

import pytest
from PIL import Image

from img2drawing import DrawingIntent, DrawingSession, RenderProfile
from img2drawing.authoring import reshape_stroke


def subject(tmp_path):
    path = tmp_path / "reference.png"
    Image.new("RGB", (80, 80), "white").save(path)
    return path


def test_reshape_preserves_material_and_returns_correction_action(tmp_path: Path):
    session = DrawingSession.create(subject=subject(tmp_path), output_dir=tmp_path, intent=DrawingIntent(drawing_mode="croquis"))
    oid = session.observe({"jaw": "reference tapers inward"})
    sid = session.draw([(10, 10), (40, 20), (60, 50)], role="contour", part="jaw", tool="continuous_pencil", pressure=[0.3, 0.7, 0.4], observation_id=oid)
    before = session.current_stroke(sid)
    with pytest.raises(ValueError, match="requires pressure"):
        reshape_stroke(session, sid, [(10, 10), (20, 15), (40, 25), (60, 50)], reason="narrow jaw", observation_id=oid)
    action = reshape_stroke(session, sid, [(10, 10), (35, 25), (60, 50)], reason="narrow jaw", observation_id=oid)
    after = session.current_stroke(sid)
    assert after.points != before.points
    assert (after.role, after.part, after.layer) == (before.role, before.part, before.layer)
    assert after.tool_state["tool"] == before.tool_state["tool"]
    assert after.pressure == before.pressure
    assert session.resolve_authored_element(sid).latest_action_id == action


def test_budget_failure_is_actionable_and_non_mutating(tmp_path: Path):
    session = DrawingSession.create(subject=subject(tmp_path), output_dir=tmp_path / "session")
    session.draw([(5, 5), (70, 70)])
    out = tmp_path / "replay"
    with pytest.raises(ValueError, match=r"required.*frames.*limit.*every_n"):
        session.export_timelapse(out, max_pixel_work=1)
    assert not out.exists()


def test_fast_palette_failure_retries_with_local_palettes(tmp_path: Path, monkeypatch):
    import importlib
    import shutil
    if not shutil.which("ffmpeg"):
        pytest.skip("ffmpeg unavailable")
    module = importlib.import_module("img2drawing.timelapse.export")
    original = module.encode_gif
    def damaged_gif(*args, **kwargs):
        result = original(*args, **kwargs)
        with Image.open(result["gif"]) as image:
            size = image.size
        Image.new("RGB", size, (0, 0, 0)).save(result["gif"])
        return result
    monkeypatch.setattr(module, "encode_gif", damaged_gif)
    profile = RenderProfile.from_dict({**RenderProfile.canonical(64, 64).to_dict(), "supersample": 2})
    reference = tmp_path / "reference64.png"
    Image.new("RGB", (64, 64), "white").save(reference)
    session = DrawingSession.create(subject=reference, output_dir=tmp_path / "session", render_profile=profile)
    session.draw([(8, 8), (50, 50)], tool="continuous_pencil")
    events = []
    result = session.export_timelapse(tmp_path / "replay", every_n=1, max_pixel_work=10**7, progress=events.append)
    assert [e["phase"] for e in events] == ["render", "render", "encode", "verify", "retry"]
    assert events[-1]["completed"] == events[-1]["total"] == 2
    assert result.manifest["gif"]["encoding_fallback"] == "local-frame-palettes"
    assert result.manifest["gif"]["within_tolerance"]
    assert result.manifest["final"]["last_frame_pixel_match"]


def test_reshape_action_closes_residual_with_matching_observation(tmp_path: Path):
    session = DrawingSession.create(subject=subject(tmp_path), output_dir=tmp_path / "session")
    oid = session.observe({"jaw": "too wide"})
    sid = session.draw([(10, 10), (40, 30), (70, 10)], role="contour", part="jaw", tool="continuous_pencil", observation_id=oid)
    session.inspect(supersample=2)
    before = session.inspection_history[-1]["inspection_id"]
    residual = session.record_residual(observation_id=oid, observation="jaw too wide", scope="jaw", severity="material", impact_rationale="changes the face", responsible_premise="jaw contour", responsible_stroke_ids=(sid,), planned_edit="narrow jaw", before_inspection_id=before)
    action = reshape_stroke(session, sid, [(15, 10), (40, 36), (65, 10)], reason="narrow jaw", observation_id=oid)
    session.inspect(supersample=2)
    session.resolve_residual(residual, action_ids=(action,), after_inspection_id=session.inspection_history[-1]["inspection_id"], rationale="new jaw path inspected")
    assert session.residual_history[-1].status == "resolved"
