"""Timelapse export: one entrypoint, exact incremental frames, explicit canonical fallback."""

from __future__ import annotations

import hashlib
import shutil
from copy import deepcopy
from pathlib import Path

import pytest
from PIL import Image

from img2drawing import DrawingIntent, DrawingSession, RenderProfile
from img2drawing.core.history import CanvasHistory
from img2drawing.core.ir import Stroke
from img2drawing.core.tools import get_tool
from img2drawing.render import render
from img2drawing.timelapse import export_timelapse, sample_cursors
from img2drawing.timelapse.delta_pack import DeltaPackWriter, iter_frames, read_info
from img2drawing.timelapse.frames import (
    CanonicalFrameSource,
    FastFrameSource,
    inspect_fast_path_eligibility,
    open_frame_source,
)
from img2drawing.timelapse.patch_cache import CACHE_SCHEMA, PatchCache

needs_ffmpeg = pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="ffmpeg unavailable")


def _rgba_hash(image: Image.Image) -> str:
    return hashlib.sha256(image.convert("RGBA").tobytes()).hexdigest()


def _profile(width: int, height: int, **overrides) -> RenderProfile:
    return RenderProfile.from_dict({**RenderProfile.canonical(width, height).to_dict(), "supersample": 2, **overrides})


def _canonical(history, cursor: int, profile: RenderProfile, path: Path) -> str:
    render(profile.prepared_ir(history.state_at(cursor)), path, **profile.renderer_kwargs())
    with Image.open(path) as image:
        return _rgba_hash(image)


def _stroke(sid: str, points, pressure, *, layer: int, width: float = 3.0, opacity: float = 0.75) -> Stroke:
    return Stroke(
        points=[tuple(map(float, p)) for p in points],
        width=float(width),
        opacity=float(opacity),
        role="form",
        stage="local-integration",
        layer=int(layer),
        stroke_id=sid,
        pressure=[float(v) for v in pressure],
        pressure_authored=True,
        tool_state=get_tool("form_pencil").to_dict(),
    ).cleaned()


def _edited_history():
    h = CanvasHistory(320, 240)
    h.add_stroke(_stroke("a", [(20, 45), (85, 55), (150, 70), (220, 80), (292, 92)], [0.3, 0.55, 0.82, 0.6, 0.35], layer=0), stroke_id="a")
    h.add_stroke(_stroke("b", [(35, 185), (95, 150), (160, 120), (225, 90), (285, 55)], [0.28, 0.52, 0.86, 0.64, 0.33], layer=1, width=4.0, opacity=0.82), stroke_id="b")
    h.add_stroke(_stroke("c", [(25, 118), (90, 112), (160, 116), (230, 125), (295, 132)], [0.35, 0.62, 0.78, 0.58, 0.31], layer=2, width=2.4, opacity=0.66), stroke_id="c")
    states = [("initial_adds", h.cursor)]

    h.replace_segment("b", 1, 3, [(95, 150), (150, 105), (225, 90)], pressure=[0.52, 0.91, 0.64], lock_boundaries=True, stage="local-integration")
    states.append(("segment_replace", h.cursor))
    h.soft_lift_segment("b", 1, 3, get_tool("soft_eraser"), strength=0.42, feather_points=1, stage="local-integration")
    states.append(("segment_soft_lift", h.cursor))
    h.soft_lift("a", get_tool("soft_eraser"), strength=0.35, stage="local-integration")
    states.append(("soft_lift", h.cursor))

    current_c = next(s for s in h.state_at().strokes if s.stroke_id == "c")
    retuned = deepcopy(current_c)
    retuned.opacity = 0.42
    retuned.tool_state = deepcopy(retuned.tool_state)
    retuned.tool_state["grain"] = 0.24
    h.replace_stroke("c", retuned, new_stroke_id="c")
    states.append(("retune_same_id", h.cursor))

    current_a = next(s for s in h.state_at().strokes if s.stroke_id == "a")
    replacement_a = deepcopy(current_a)
    replacement_a.opacity = 0.51
    h.replace_stroke("a", replacement_a, new_stroke_id="a2")
    states.append(("replace_new_id", h.cursor))

    h.hard_delete("b", get_tool("hard_eraser"), stage="local-integration")
    states.append(("delete", h.cursor))
    h.marker("semantic-closure", stage="local-integration")
    states.append(("snapshot", h.cursor))
    return h, states


def _raw_eraser_history() -> CanvasHistory:
    h = CanvasHistory(128, 96)
    h.add_stroke(_stroke("a", [(10, 20), (90, 60)], [0.4, 0.7], layer=0), stroke_id="a")
    raw = Stroke(
        points=[(30.0, 10.0), (50.0, 80.0)], width=8.0, opacity=1.0,
        role="correction", stage="legacy-raw-eraser", layer=1, stroke_id="e",
        pressure=[0.8, 0.8], pressure_authored=True, tool_state=get_tool("soft_eraser").to_dict(),
    ).cleaned()
    h.add_stroke(raw, stroke_id="e")
    return h


# -- sampling ---------------------------------------------------------------

def test_sample_cursors_keep_both_endpoints() -> None:
    assert sample_cursors(10, "every_n", 4) == [0, 4, 8, 10]
    assert sample_cursors(8, "every_n", 4) == [0, 4, 8]
    assert sample_cursors(3, "action") == [0, 1, 2, 3]
    assert sample_cursors(0, "every_n", 4) == [0]
    with pytest.raises(ValueError):
        sample_cursors(5, "stage")
    with pytest.raises(ValueError):
        sample_cursors(5, "every_n", 0)


# -- incremental frame source ------------------------------------------------

@pytest.mark.parametrize("every_n", [1, 4, 8])
def test_fast_frames_match_canonical_render_at_every_sampled_cursor(tmp_path: Path, every_n: int) -> None:
    history, _ = _edited_history()
    profile = _profile(320, 240, paper_tooth=0.58, paper_seed=77)
    source = FastFrameSource(history, profile)
    try:
        for cursor in sample_cursors(history.cursor, "every_n", every_n):
            source.advance_to(cursor)
            got = source.image()
            assert _rgba_hash(got) == _canonical(history, cursor, profile, tmp_path / f"{every_n}_{cursor}.png"), cursor
            got.close()
    finally:
        source.close()


def test_every_edit_kind_is_pixel_exact(tmp_path: Path) -> None:
    history, states = _edited_history()
    profile = _profile(320, 240)
    source = FastFrameSource(history, profile)
    try:
        for label, cursor in states:
            info = source.advance_to(cursor)
            got = source.image()
            assert _rgba_hash(got) == _canonical(history, cursor, profile, tmp_path / f"{label}.png"), (label, info)
            got.close()
    finally:
        source.close()


def test_raw_spatial_eraser_is_ineligible_and_falls_back_to_canonical_frames(tmp_path: Path) -> None:
    history = _raw_eraser_history()
    profile = _profile(128, 96)
    eligibility = inspect_fast_path_eligibility(history)
    assert not eligibility.eligible and eligibility.raw_spatial_eraser_seen
    with pytest.raises(ValueError, match="ineligible"):
        FastFrameSource(history, profile)

    source = open_frame_source(history, profile)
    assert isinstance(source, CanonicalFrameSource)
    try:
        info = source.advance_to(history.cursor)
        assert info["mode"] == "canonical-fallback"
        assert any("raw spatial eraser" in reason for reason in info["fallback_reasons"])
        got = source.image()
        assert _rgba_hash(got) == _canonical(history, history.cursor, profile, tmp_path / "canonical.png")
        got.close()
    finally:
        source.close()


def _cache(**overrides) -> PatchCache:
    args = dict(
        width=320, height=240, background=(255, 255, 255, 255), scale=1, supersample=2,
        graphite=(36, 34, 32), tooth=0.58, paper_scale=1.0, paper_seed=77,
        cache_contract={"profile_id": "test-profile", "seed_domain": "seed-v1"},
    )
    args.update(overrides)
    return PatchCache(**args)


def test_patch_cache_key_covers_every_pixel_affecting_input() -> None:
    stroke = _stroke("k", [(20, 40), (120, 90), (240, 130)], [0.3, 0.8, 0.4], layer=0)
    base, same = _cache(), _cache()
    variants = [
        _cache(supersample=3),
        _cache(graphite=(35, 34, 32)),
        _cache(tooth=0.61),
        _cache(paper_scale=1.25),
        _cache(paper_seed=78),
        _cache(cache_contract={"profile_id": "other-profile", "seed_domain": "seed-v1"}),
    ]
    try:
        assert CACHE_SCHEMA.endswith(".v3")
        assert base._fingerprint(stroke) == same._fingerprint(stroke)
        assert all(variant._fingerprint(stroke) != base._fingerprint(stroke) for variant in variants)
    finally:
        for cache in (base, same, *variants):
            cache.close()


def test_persistent_patch_cache_is_disposable_and_rebuilds_corrupt_entries(tmp_path: Path) -> None:
    stroke = _stroke("k", [(20, 40), (120, 90), (240, 130)], [0.3, 0.8, 0.4], layer=0)
    cold = _cache(persistent_cache_dir=tmp_path / "patches")
    (x, y), layer = cold.patch_for(stroke)
    expected = _rgba_hash(layer)
    cold.close()
    assert cold.persistent["bytes_written"] > 0

    warm = _cache(persistent_cache_dir=tmp_path / "patches")
    _, warm_layer = warm.patch_for(stroke)
    assert warm.persistent["disk_hits"] == 1 and _rgba_hash(warm_layer) == expected
    warm.close()

    for entry in (tmp_path / "patches").rglob("*.pcz"):
        entry.write_bytes(entry.read_bytes()[:40])
    rebuilt = _cache(persistent_cache_dir=tmp_path / "patches")
    _, rebuilt_layer = rebuilt.patch_for(stroke)
    assert rebuilt.persistent["disk_corrupt"] == 1 and _rgba_hash(rebuilt_layer) == expected
    rebuilt.close()


def test_delta_pack_is_atomic_and_recovers_from_partial_or_corrupt_staging(tmp_path: Path) -> None:
    target = tmp_path / "frames.idp"
    red = Image.new("RGB", (16, 12), (255, 0, 0))
    blue = Image.new("RGB", (16, 12), (0, 0, 255))
    try:
        with pytest.raises(RuntimeError, match="interrupt"):
            with DeltaPackWriter(target, width=16, height=12, frame_count=2) as writer:
                writer.write_frame(red, [(0, 0, 16, 12)])
                raise RuntimeError("interrupt")
        assert not target.exists()
        assert not target.with_name(target.name + ".partial").exists()

        partial = target.with_name(target.name + ".partial")
        partial.write_bytes(b"stale-partial")
        with DeltaPackWriter(target, width=16, height=12, frame_count=2) as writer:
            writer.write_frame(red, [(0, 0, 16, 12)])
            writer.write_frame(blue, [(0, 0, 16, 12)])
        assert target.exists() and not partial.exists()
        assert read_info(target).frame_count == 2
        frames = list(iter_frames(target))
        try:
            assert frames[0].getpixel((0, 0)) == (255, 0, 0)
            assert frames[1].getpixel((0, 0)) == (0, 0, 255)
        finally:
            for frame in frames:
                frame.close()

        target.write_bytes(target.read_bytes()[:25])
        with pytest.raises(ValueError):
            read_info(target)
        with DeltaPackWriter(target, width=16, height=12, frame_count=1) as writer:
            writer.write_frame(red, [(0, 0, 16, 12)])
        assert read_info(target).frame_count == 1
    finally:
        red.close()
        blue.close()


# -- session export ---------------------------------------------------------

def _session(tmp_path: Path, *, paper_tooth: float = 0.5) -> DrawingSession:
    subject = tmp_path / "subject.png"
    Image.new("RGB", (64, 48), (244, 242, 236)).save(subject)
    session = DrawingSession.create(
        subject=subject,
        output_dir=tmp_path / "session",
        intent=DrawingIntent(finish_intent="form_light"),
        render_profile=_profile(64, 48, paper_tooth=paper_tooth),
    )
    session.draw(((6, 8), (18, 22), (25, 40)), part="gesture")
    session.draw(((26, 8), (34, 20), (39, 39)), part="contour")
    return session


@needs_ffmpeg
def test_default_backend_is_fast_and_does_not_spool_png_frames(tmp_path: Path) -> None:
    result = _session(tmp_path).export_timelapse(tmp_path / "replay", every_n=1, max_pixel_work=10**9)
    assert result.manifest["backend"] == {"requested": "auto", "selected": "fast", "fallback_reason": None}
    assert result.manifest["final"]["last_frame_pixel_match"] is True
    assert result.manifest["fast"]["pack"]["file"] == "frames.idp"
    assert not list(result.frame_dir.glob("*.png"))
    assert result.gif_path.is_file() and result.final_path.is_file()


def test_canonical_backend_writes_every_frame_png(tmp_path: Path) -> None:
    result = _session(tmp_path).export_timelapse(tmp_path / "canonical", mode="action", backend="canonical", max_pixel_work=10**9)
    assert result.manifest["backend"]["selected"] == "canonical"
    assert len(list(result.frame_dir.glob("*.png"))) == len(result.manifest["frames"])
    assert result.manifest["final"]["last_frame_pixel_match"] is True


@needs_ffmpeg
def test_fast_and_canonical_backends_agree_on_every_frame(tmp_path: Path) -> None:
    session = _session(tmp_path)
    fast = session.export_timelapse(tmp_path / "fast", mode="action", max_pixel_work=10**9)
    canonical = session.export_timelapse(tmp_path / "canonical", mode="action", backend="canonical", max_pixel_work=10**9)
    rgb = []
    for frame in canonical.manifest["frames"]:
        with Image.open(tmp_path / "canonical" / frame["file"]) as image:
            rgb.append(hashlib.sha256(image.convert("RGB").tobytes()).hexdigest())
    assert [frame["pixel_sha256"] for frame in fast.manifest["frames"]] == rgb


def test_ineligible_history_falls_back_to_canonical_for_the_whole_export(tmp_path: Path) -> None:
    history = _raw_eraser_history()
    result = export_timelapse(history, _profile(128, 96), tmp_path / "out", session_id="t", every_n=1, max_pixel_work=10**9)
    assert result.manifest["backend"]["selected"] == "canonical"
    assert "raw spatial eraser" in result.manifest["backend"]["fallback_reason"]
    with pytest.raises(ValueError, match="fast timelapse backend unavailable"):
        export_timelapse(history, _profile(128, 96), tmp_path / "strict", session_id="t", backend="fast", max_pixel_work=10**9)


def test_current_stroke_only_session_is_fast_path_eligible(tmp_path: Path) -> None:
    eligibility = inspect_fast_path_eligibility(_session(tmp_path)._agent.history)
    assert eligibility.eligible and eligibility.reasons == ()
    assert set(eligibility.action_types) == {"stroke.add"}


@needs_ffmpeg
def test_render_profile_paper_state_is_authority_for_fast_final(tmp_path: Path) -> None:
    result = _session(tmp_path, paper_tooth=0.63).export_timelapse(tmp_path / "paper", mode="action", max_pixel_work=10**9)
    assert result.manifest["backend"]["selected"] == "fast"
    assert result.manifest["render_profile"]["paper_tooth"] == 0.63
    assert result.manifest["final"]["last_frame_pixel_match"] is True


@needs_ffmpeg
def test_materialize_frames_is_explicit_opt_in(tmp_path: Path) -> None:
    result = _session(tmp_path).export_timelapse(tmp_path / "frames", mode="action", materialize_frames=True, max_pixel_work=10**9)
    assert len(list(result.frame_dir.glob("*.png"))) == len(result.manifest["frames"])
    assert all(frame["file"] is not None for frame in result.manifest["frames"])


def test_pixel_work_gate_applies_before_any_output(tmp_path: Path) -> None:
    out = tmp_path / "too-large"
    with pytest.raises(ValueError, match="pixel-work budget"):
        _session(tmp_path).export_timelapse(out, mode="action", max_pixel_work=1)
    assert not (out / "timelapse.gif").exists()


def test_legacy_timelapse_paths_are_gone() -> None:
    import importlib.util

    for name in ("img2drawing.provenance", "img2drawing.vnext"):
        assert importlib.util.find_spec(name) is None, name
