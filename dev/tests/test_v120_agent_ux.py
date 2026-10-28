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
    assert [e["phase"] for e in events] == [
        "render", "render", "encode", "encode", "verify", "retry",
        "retry", "retry", "verify",
    ]
    assert events[-1] == {"phase": "verify", "completed": 1, "total": 1}
    assert events[-1]["completed"] == events[-1]["total"] == 2
    assert result.manifest["gif"]["encoding_fallback"] == "local-frame-palettes"
    assert result.manifest["gif"]["within_tolerance"]
    assert result.manifest["fast"]["encode"]["gif_sha256"] == result.manifest["gif"]["sha256"]
    assert result.manifest["fast"]["encode"]["strategy"] == "local-frame-palettes"
    assert "initial_attempt" in result.manifest["fast"]["encode"]
    assert result.manifest["fast"]["performance"]["encode_sec"] >= result.manifest["fast"]["encode"]["retry_encode_sec"]
    assert not (tmp_path / "replay" / "frames").exists()
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


def test_reshape_preserves_global_soft_lift(tmp_path: Path):
    session = DrawingSession.create(subject=subject(tmp_path), output_dir=tmp_path / "session")
    oid = session.observe({"jaw": "needs reshaping"})
    sid = session.draw([(10, 10), (40, 20), (70, 40)], tool="continuous_pencil", observation_id=oid)
    session.soft_lift(sid, strength=0.6, observation_id=oid, reason="reduce search-line strength")
    faded = session.current_stroke(sid)
    assert faded.opacity < faded.tool_state["opacity"]
    action = reshape_stroke(session, sid, [(10, 10), (45, 24), (70, 40)],
                            reason="fix jaw geometry", observation_id=oid)
    after = session.current_stroke(sid)
    assert after.opacity == pytest.approx(faded.opacity)
    assert after.tool_state["tool"] == "continuous_pencil"
    assert session.resolve_authored_element(sid).latest_action_id == action


def test_reshape_retains_locally_lifted_pressure(tmp_path: Path):
    from img2drawing.core.tools import soft_eraser

    session = DrawingSession.create(subject=subject(tmp_path), output_dir=tmp_path / "session")
    oid = session.observe({"contour": "partially attenuated line"})
    points = [(10, 10), (25, 12), (45, 22), (70, 40)]
    sid = session.draw(points, tool="continuous_pencil", observation_id=oid)
    # Exercise historical local-edit replay, which is not a public worker API.
    session._agent.history.soft_lift_segment(sid, 1, 2, soft_eraser(), strength=0.8)
    faded = session.current_stroke(sid)
    assert not faded.pressure_authored
    with pytest.raises(ValueError, match="requires pressure"):
        reshape_stroke(session, sid, points + [(75, 42)], reason="add detail", observation_id=oid)
    reshape_stroke(session, sid, [(11, 11), (26, 13), (46, 23), (69, 39)],
                   reason="adjust shape", observation_id=oid)
    revised = session.current_stroke(sid)
    assert revised.pressure == pytest.approx(faded.pressure)
    assert revised.pressure_authored


def test_reshape_after_segment_replace_preserves_resulting_geometry(tmp_path: Path):
    session = DrawingSession.create(subject=subject(tmp_path), output_dir=tmp_path / "session")
    oid = session.observe({"contour": "needs correction"})
    sid = session.draw([(10, 10), (25, 12), (45, 22), (70, 40)],
                       tool="continuous_pencil", observation_id=oid)
    session.replace_segment(sid, 1, 2, [(25, 12), (35, 25), (45, 22)],
                            reason="local adjustment", observation_id=oid)
    previous = session.current_stroke(sid)
    assert len(previous.points) == 5
    reshape_stroke(session, sid, [(11, 11), (25, 12), (34, 26), (45, 22), (69, 39)],
                   reason="overall adjustment", observation_id=oid)
    assert len(session.current_stroke(sid).points) == 5


def test_streaming_local_gif_closes_each_frame_before_next(tmp_path: Path):
    from img2drawing.timelapse.gif import save_gif_frames

    released = []
    def input_frames():
        previous = None
        for index in range(24):
            if previous is not None:
                assert previous.im is None, "previous frame retained in memory"
            previous = Image.new("RGBA", (96, 64), (index * 10, 24, 56, 255))
            released.append(previous)
            yield previous

    output = tmp_path / "stream.gif"
    save_gif_frames(input_frames(), [100] * 24, output)
    assert all(im.im is None for im in released)
    assert not list(tmp_path.glob(".stream.gif.*.tmp"))
    with Image.open(output) as gif:
        assert gif.n_frames == 24
        gif.seek(23)
        assert gif.convert("RGB").getpixel((0, 0)) == (230, 24, 56)
