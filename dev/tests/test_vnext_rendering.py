from __future__ import annotations

import json
from pathlib import Path

import pytest
from PIL import Image

from img2drawing import DrawingIntent, DrawingSession, RenderProfile
from img2drawing.render.pillow_pencil_contact import (
    RENDERER_ID as HISTORICAL_RENDERER_ID,
    RENDERER_VERSION as HISTORICAL_RENDERER_VERSION,
)
from img2drawing.render.renderer_registry import current_renderer
from img2drawing.vnext.output import export_session_timelapse


def _subject(tmp_path: Path) -> Path:
    tmp_path.mkdir(parents=True, exist_ok=True)
    path = tmp_path / "subject.png"
    Image.new("RGB", (48, 48), (244, 242, 236)).save(path)
    return path


def _session(tmp_path: Path) -> DrawingSession:
    profile = RenderProfile.from_dict(
        {**RenderProfile.canonical(48, 48).to_dict(), "supersample": 2}
    )
    session = DrawingSession.create(
        subject=_subject(tmp_path),
        output_dir=tmp_path / "run",
        intent=DrawingIntent(finish_intent="form_light"),
        render_profile=profile,
    )
    session.draw(((6, 8), (18, 22), (25, 40)), part="gesture")
    session.draw(((26, 8), (34, 20), (39, 39)), part="selected_contour")
    session.draw(
        ((12, 24), (21, 22), (30, 23), (37, 30)),
        role="value",
        part="shadow_family",
        stroke_id="fixture-shadow-stroke",
        tool="form_pencil",
        tool_overrides={"pressure": 0.48, "opacity": 0.58, "taper_in": 0.05, "taper_out": 0.05},
    )
    return session


def test_render_profile_roundtrip_and_strict_material_boundary() -> None:
    profile = RenderProfile.canonical(64, 48)
    assert RenderProfile.from_dict(profile.to_dict()) == profile
    assert profile.digest() == RenderProfile.from_dict(profile.to_dict()).digest()
    assert (profile.renderer_id, profile.renderer_version) == current_renderer().identity
    assert "style_profile" not in profile.to_dict()
    assert "line_behavior" not in profile.to_dict()
    with pytest.raises(ValueError, match="unsupported renderer"):
        RenderProfile.from_dict({**profile.to_dict(), "renderer_version": "future"})
    with pytest.raises(ValueError, match="custom file paths"):
        RenderProfile.from_dict({**profile.to_dict(), "material_profile": "/tmp/custom.json"})
    with pytest.raises(ValueError, match="unsupported fields"):
        RenderProfile.from_dict({**profile.to_dict(), "post_filter": "sketch"})
    with pytest.raises(ValueError, match="supersample"):
        RenderProfile.from_dict({**profile.to_dict(), "supersample": 2.5})


def test_session_persists_one_profile_and_rejects_header_or_canvas_drift(tmp_path: Path) -> None:
    session = _session(tmp_path)
    payload = json.loads(session.checkpoint_path.read_text(encoding="utf-8"))
    assert payload["render_profile"] == session.render_profile.to_dict()
    assert payload["renderer"] == {
        "id": session.render_profile.renderer_id,
        "version": session.render_profile.renderer_version,
        "seed_domain": session.render_profile.seed_domain,
    }
    assert DrawingSession.resume(session.checkpoint_path, subject=session.subject).render_profile == session.render_profile

    payload["renderer"]["version"] = "future"
    session.checkpoint_path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="does not match RenderProfile"):
        DrawingSession.resume(session.checkpoint_path, subject=session.subject)


def test_cursor_png_replay_gif_and_final_render_share_history_and_profile(tmp_path: Path) -> None:
    session = _session(tmp_path)
    before_hash = session.drawing_state_hash()
    before_cursor = session.history_cursor
    direct = session.render_final(tmp_path / "direct.png")
    initial = session.render_at(0, tmp_path / "initial.png")
    replay = export_session_timelapse(
        session,
        tmp_path / "replay",
        mode="action",
        max_pixel_work=10**9,
        backend="canonical",
    )

    assert session.drawing_state_hash() == before_hash
    assert session.history_cursor == before_cursor
    assert initial.cursor == 0
    assert direct.cursor == before_cursor
    assert [frame["cursor"] for frame in replay.manifest["frames"]] == [0, 1, 2, 3]
    assert [frame["action"] for frame in replay.manifest["frames"]] == [
        None,
        "stroke.add",
        "stroke.add",
        "stroke.add",
    ]
    assert replay.manifest["frames"][-1]["duration_ms"] == 900
    assert replay.manifest["sampling"]["action_zero_included"]
    assert replay.manifest["sampling"]["latest_included"]
    assert len({frame["pixel_sha256"] for frame in replay.manifest["frames"]}) > 2
    assert replay.manifest["final"]["last_frame_pixel_match"]
    assert replay.manifest["final"]["pixel_sha256"] == direct.pixel_sha256
    assert replay.manifest["gif"]["within_tolerance"]
    assert replay.manifest["budget"]["gif_bytes"] <= replay.manifest["budget"]["max_gif_bytes"]
    assert replay.manifest["render_profile_digest"] == session.render_profile.digest()

    with Image.open(replay.gif_path) as gif:
        assert gif.n_frames >= 3


def test_inspect_renders_through_the_same_persisted_profile_as_final(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import img2drawing.vnext.output as output_module
    import img2drawing.vnext.session as session_module

    custom = RenderProfile.from_dict({
        **RenderProfile.canonical(48, 48).to_dict(),
        "paper_tooth": 0.9,
        "paper_seed": 12345,
        "background_rgba": [230, 200, 180, 255],
        "graphite_rgb": [10, 10, 10],
        "output_scale": 2,
    })
    session = DrawingSession.create(
        subject=_subject(tmp_path),
        output_dir=tmp_path / "run",
        intent=DrawingIntent(finish_intent="form_light"),
        render_profile=custom,
    )
    session.draw(((6, 8), (18, 22), (25, 40)), part="gesture")

    calls: list[tuple[dict, dict]] = []

    def _spy(real_render):
        def wrapper(ir, path, *args, **kwargs):
            calls.append(({"metadata": dict(ir.metadata)}, dict(kwargs)))
            return real_render(ir, path, *args, **kwargs)

        return wrapper

    monkeypatch.setattr(session_module, "render", _spy(session_module.render))
    monkeypatch.setattr(output_module, "render", _spy(output_module.render))

    session.inspect(supersample=custom.supersample)
    session.render_final(tmp_path / "final.png")

    assert len(calls) == 2
    inspect_call, final_call = calls
    assert inspect_call[0]["metadata"]["paper"] == final_call[0]["metadata"]["paper"]
    assert tuple(inspect_call[1]["background"]) == custom.background_rgba
    assert tuple(inspect_call[1]["graphite"]) == custom.graphite_rgb
    assert tuple(final_call[1]["background"]) == custom.background_rgba
    assert tuple(final_call[1]["graphite"]) == custom.graphite_rgb
    assert inspect_call[1]["scale"] == 1
    assert final_call[1]["scale"] == custom.output_scale == 2


def test_inspect_and_final_render_are_pixel_identical(tmp_path: Path) -> None:
    """v10 seed identity must ignore the private compatibility-stage transport tag."""

    from img2drawing.provenance.timelapse import pixel_sha256

    session = DrawingSession.create(
        subject=_subject(tmp_path),
        output_dir=tmp_path / "run",
        intent=DrawingIntent(finish_intent="pose"),
    )
    session.draw(((8, 8), (30, 40), (44, 44)), part="pose/line")

    sheet = session.inspect(supersample=session.render_profile.supersample)
    final = session.render_final(tmp_path / "final.png")

    assert pixel_sha256(sheet.drawing) == final.pixel_sha256


def test_replay_is_deterministic_and_every_n_keeps_endpoints(tmp_path: Path) -> None:
    session = _session(tmp_path)
    first = export_session_timelapse(
        session, tmp_path / "first", mode="every_n", every_n=2,
        max_pixel_work=10**9, backend="canonical",
    )
    second = export_session_timelapse(
        session, tmp_path / "second", mode="every_n", every_n=2,
        max_pixel_work=10**9, backend="canonical",
    )
    assert [frame["cursor"] for frame in first.manifest["frames"]] == [0, 2, 3]
    assert [frame["pixel_sha256"] for frame in first.manifest["frames"]] == [
        frame["pixel_sha256"] for frame in second.manifest["frames"]
    ]
    assert first.manifest["final"] == second.manifest["final"]
    assert first.manifest["gif"]["sha256"] == second.manifest["gif"]["sha256"]


def test_replay_budget_and_cursor_bounds_fail_before_drift(tmp_path: Path) -> None:
    session = _session(tmp_path)
    with pytest.raises(ValueError, match="pixel-work budget"):
        session.export_timelapse(tmp_path / "too-large", max_pixel_work=1)
    assert not (tmp_path / "too-large" / "timelapse.gif").exists()
    with pytest.raises(ValueError, match="outside the authoritative history"):
        session.render_at(session.history_cursor + 1, tmp_path / "future.png")


def test_pre_b11_checkpoint_requires_explicit_profile_migration(tmp_path: Path) -> None:
    session = _session(tmp_path)
    payload = json.loads(session.checkpoint_path.read_text(encoding="utf-8"))
    payload.pop("render_profile")
    payload["renderer"] = {
        "id": HISTORICAL_RENDERER_ID,
        "version": "vnext-stage-free-1",
        "seed_domain": "vnext-stage-free",
    }
    session.checkpoint_path.write_text(json.dumps(payload), encoding="utf-8")
    resumed = DrawingSession.resume(session.checkpoint_path, subject=session.subject)
    assert resumed.render_profile is None
    with pytest.raises(ValueError, match="migrate_render_profile"):
        resumed.render_final(tmp_path / "not-yet.png")
    migrated = resumed.migrate_render_profile()
    assert migrated == RenderProfile.canonical(48, 48)
    assert resumed.render_final(tmp_path / "migrated.png").path.is_file()


def test_current_stroke_only_replay_records_parity_without_region_actions(tmp_path: Path) -> None:
    session = _session(tmp_path)
    replay = export_session_timelapse(
        session,
        tmp_path / "current-fixture",
        mode="action",
        max_pixel_work=10**9,
        backend="canonical",
    )
    assert not hasattr(session, "fill_region")
    assert replay.manifest["history"]["action_count"] == 3
    assert [frame["cursor"] for frame in replay.manifest["frames"]] == [0, 1, 2, 3]
    assert [frame["action"] for frame in replay.manifest["frames"]].count("stroke.add") == 3
    assert all(frame["action"] != "region.fill" for frame in replay.manifest["frames"])
    assert replay.manifest["final"]["last_frame_pixel_match"]
    assert replay.manifest["gif"]["within_tolerance"]
    assert replay.manifest["sampling"]["action_zero_included"]
    assert replay.manifest["sampling"]["latest_included"]
