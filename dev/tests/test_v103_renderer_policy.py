from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageChops, ImageStat

from img2drawing import DrawingSession, RenderProfile
from img2drawing.provenance.fast_timelapse.frame_source import FastFrameSource
from img2drawing.render.renderer_registry import (
    current_renderer,
    registered_renderer_identities,
)
from img2drawing.vnext import resolve_markmaking


V9 = ("pillow-pencil-contact-v9", "1")
V10 = ("pillow-pencil-contact-v10", "1")


def _subject(tmp_path: Path, name: str = "subject.png") -> Path:
    path = tmp_path / name
    Image.new("RGB", (160, 80), (255, 255, 255)).save(path)
    return path


def _explicit_profile(identity: tuple[str, str], *, width: int = 160, height: int = 80) -> RenderProfile:
    renderer_id, renderer_version = identity
    return RenderProfile(
        profile_id=f"test-{renderer_id}-{renderer_version}",
        renderer_id=renderer_id,
        renderer_version=renderer_version,
        canvas_width=width,
        canvas_height=height,
        supersample=4,
    )


def _draw_broad(session: DrawingSession, policy: str, *, stroke_id: str = "broad") -> None:
    mark = resolve_markmaking(
        "pencil_loose",
        "broad_mass",
        material_policy=policy,
        modifiers={"width": 8.4, "pressure": 0.96, "opacity": 0.98},
    )
    session.draw(
        ((16, 40), (58, 36), (104, 43), (144, 39)),
        stroke_id=stroke_id,
        part="material-probe",
        pressure=(1.0, 1.0, 1.0, 1.0),
        **mark.draw_kwargs(),
    )


def _rgb_mean(path: Path) -> float:
    with Image.open(path) as image:
        crop = image.convert("L").crop((12, 24, 148, 56))
        return float(ImageStat.Stat(crop).mean[0])


def test_registry_keeps_v9_and_selects_v10_for_new_profiles() -> None:
    assert V9 in registered_renderer_identities()
    assert V10 in registered_renderer_identities()
    assert current_renderer().identity == V10
    profile = RenderProfile.canonical(160, 80)
    assert (profile.renderer_id, profile.renderer_version) == V10


def test_checkpoint_header_tracks_profile_and_v9_replays_after_resume(tmp_path: Path) -> None:
    subject = _subject(tmp_path)
    session = DrawingSession.create(
        subject=subject,
        output_dir=tmp_path / "v9-run",
        render_profile=_explicit_profile(V9),
    )
    session.draw(
        ((18, 42), (80, 34), (142, 42)),
        stroke_id="legacy-line",
        part="legacy",
        tool="form_pencil",
        tool_overrides={"width": 2.4, "pressure": 0.72, "opacity": 0.80},
    )
    first = session.render_final(tmp_path / "v9-first.png")

    payload = json.loads(session.checkpoint_path.read_text(encoding="utf-8"))
    assert payload["renderer"]["id"] == V9[0]
    assert str(payload["renderer"]["version"]) == V9[1]
    assert payload["render_profile"]["renderer_id"] == V9[0]

    resumed = DrawingSession.resume(session.checkpoint_path, subject=subject)
    assert (resumed.render_profile.renderer_id, resumed.render_profile.renderer_version) == V9
    second = resumed.render_final(tmp_path / "v9-resumed.png")
    assert first.pixel_sha256 == second.pixel_sha256


def test_v10_material_policies_change_actual_broad_pixels(tmp_path: Path) -> None:
    subject = _subject(tmp_path)
    paths: dict[str, Path] = {}
    means: dict[str, float] = {}
    hashes: dict[str, str] = {}

    for policy in ("canonical-pencil", "manga-light", "dry-graphite-expressive"):
        session = DrawingSession.create(
            subject=subject,
            output_dir=tmp_path / policy,
        )
        assert (session.render_profile.renderer_id, session.render_profile.renderer_version) == V10
        _draw_broad(session, policy)
        path = tmp_path / f"{policy}.png"
        artifact = session.render_final(path)
        paths[policy] = path
        hashes[policy] = artifact.pixel_sha256
        means[policy] = _rgb_mean(path)

    assert len(set(hashes.values())) == 3
    # Strict authored-value preservation should keep the broad core darker than
    # the intentionally airy manga-light interpretation.
    assert means["canonical-pencil"] < means["manga-light"]


def test_v10_fast_final_matches_canonical_and_repairs_late_lower_layer(tmp_path: Path) -> None:
    subject = _subject(tmp_path)
    session = DrawingSession.create(subject=subject, output_dir=tmp_path / "fast-run")

    high = resolve_markmaking(
        "pencil_loose",
        "contour",
        modifiers={"width": 6.2, "pressure": 0.82, "opacity": 0.90},
    )
    low = resolve_markmaking(
        "pencil_loose",
        "form",
        modifiers={"width": 7.0, "pressure": 0.68, "opacity": 0.78},
    )
    session.draw(
        ((20, 26), (80, 48), (140, 26)),
        stroke_id="high-layer",
        part="overlap",
        layer=5,
        **high.draw_kwargs(),
    )
    session.draw(
        ((20, 48), (80, 26), (140, 48)),
        stroke_id="late-low-layer",
        part="overlap",
        layer=1,
        **low.draw_kwargs(),
    )

    canonical_path = tmp_path / "canonical.png"
    session.render_final(canonical_path)

    source = FastFrameSource.from_vnext_session(session)
    try:
        first = source.advance_to(1)
        second = source.advance_to(2)
        assert first["mode"] == "append"
        assert second["mode"] == "layer-reorder-dirty"
        fast = source.image()
        try:
            with Image.open(canonical_path) as canonical:
                diff = ImageChops.difference(fast.convert("RGBA"), canonical.convert("RGBA"))
                assert diff.getbbox() is None
        finally:
            fast.close()
    finally:
        source.close()
