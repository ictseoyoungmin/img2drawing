from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageChops, ImageStat

from img2drawing import DrawingSession, RenderProfile
from img2drawing.provenance.fast_timelapse.frame_source import FastFrameSource
from img2drawing.render.renderer_registry import current_renderer, registered_renderer_identities
from img2drawing.vnext import resolve_markmaking

V11 = ("pillow-pencil-contact-v11", "1")
V12 = ("pillow-pencil-contact-v12", "1")


def _subject(tmp_path: Path) -> Path:
    path = tmp_path / "subject.png"
    Image.new("RGB", (224, 84), (255, 255, 255)).save(path)
    return path


def _profile(identity: tuple[str, str]) -> RenderProfile:
    return RenderProfile(
        profile_id=f"terminal-{identity[0]}", renderer_id=identity[0], renderer_version=identity[1],
        canvas_width=224, canvas_height=84, supersample=4,
    )


def _draw_terminal(session: DrawingSession, mode: str, *, stroke_id: str = "terminal-probe") -> None:
    mark = resolve_markmaking(
        "pencil_loose", "broad_mass", tool_preset="broad-graphite", terminal_mode=mode,
        modifiers={
            "width": 10.0, "pressure": 0.82, "opacity": 0.90, "hardness": 0.48,
            "grain": 0.58, "taper_in": 0.0, "taper_out": 0.0, "jitter": 0.0,
        },
    )
    session.draw(
        ((18, 42), (76, 39), (144, 44), (207, 41)), stroke_id=stroke_id,
        part="terminal-probe", pressure=(0.82, 0.82, 0.82, 0.82), **mark.draw_kwargs(),
    )


def _terminal_darkness(path: Path) -> float:
    with Image.open(path) as image:
        crop = image.convert("L").crop((190, 25, 224, 59))
        stat = ImageStat.Stat(crop)
        return 255.0 - float(stat.mean[0])


def test_v12_is_current_additive_backend_and_v11_remains_registered() -> None:
    identities = registered_renderer_identities()
    assert V11 in identities
    assert V12 in identities
    assert current_renderer().identity == V12
    canonical = RenderProfile.canonical(224, 84)
    assert (canonical.renderer_id, canonical.renderer_version) == V12


def test_contact_mode_is_pixel_exact_with_v11(tmp_path: Path) -> None:
    subject = _subject(tmp_path)
    paths = {}
    for identity in (V11, V12):
        session = DrawingSession.create(
            subject=subject, output_dir=tmp_path / identity[0], render_profile=_profile(identity)
        )
        _draw_terminal(session, "contact")
        paths[identity] = tmp_path / f"{identity[0]}.png"
        session.render_final(paths[identity])
    with Image.open(paths[V11]) as old, Image.open(paths[V12]) as new:
        diff = ImageChops.difference(old.convert("RGB"), new.convert("RGB"))
        assert diff.getbbox() is None


def test_public_terminal_modes_change_actual_pixels_without_geometry_changes(tmp_path: Path) -> None:
    subject = _subject(tmp_path)
    hashes: dict[str, str] = {}
    darkness: dict[str, float] = {}
    for mode in ("contact", "gentle", "flick", "residue"):
        session = DrawingSession.create(subject=subject, output_dir=tmp_path / mode)
        assert (session.render_profile.renderer_id, session.render_profile.renderer_version) == V12
        _draw_terminal(session, mode)
        stroke = session.current_stroke("terminal-probe")
        saved = stroke.tool_state["provenance"]["metadata"]["markmaking"]
        assert saved["terminal_mode"] == mode
        assert stroke.points == [(18.0, 42.0), (76.0, 39.0), (144.0, 44.0), (207.0, 41.0)]
        path = tmp_path / f"{mode}.png"
        hashes[mode] = session.render_final(path).pixel_sha256
        darkness[mode] = _terminal_darkness(path)
    assert len(set(hashes.values())) == 4
    assert darkness["contact"] > darkness["gentle"]
    assert darkness["contact"] > darkness["flick"]
    assert darkness["residue"] > 0.0


def test_noncontact_terminal_is_bounded_to_a_physical_suffix(tmp_path: Path) -> None:
    subject = _subject(tmp_path)
    contact = DrawingSession.create(subject=subject, output_dir=tmp_path / "contact")
    gentle = DrawingSession.create(subject=subject, output_dir=tmp_path / "gentle")
    _draw_terminal(contact, "contact")
    _draw_terminal(gentle, "gentle")
    p_contact = tmp_path / "contact.png"
    p_gentle = tmp_path / "gentle.png"
    contact.render_final(p_contact)
    gentle.render_final(p_gentle)
    with Image.open(p_contact) as a, Image.open(p_gentle) as b:
        diff = ImageChops.difference(a.convert("RGB"), b.convert("RGB"))
        box = diff.getbbox()
        assert box is not None
        # The semantic terminal must not re-author the long stroke body.
        assert box[0] > 150


def test_v12_terminal_semantics_are_fast_canonical_exact(tmp_path: Path) -> None:
    subject = _subject(tmp_path)
    session = DrawingSession.create(subject=subject, output_dir=tmp_path / "fast")
    _draw_terminal(session, "gentle", stroke_id="gentle")
    _draw_terminal(session, "residue", stroke_id="residue")
    canonical_path = tmp_path / "canonical.png"
    session.render_final(canonical_path)
    source = FastFrameSource.from_vnext_session(session)
    try:
        source.advance_to(1)
        source.advance_to(2)
        fast = source.image()
        try:
            with Image.open(canonical_path) as canonical:
                diff = ImageChops.difference(fast.convert("RGB"), canonical.convert("RGB"))
                assert diff.getbbox() is None
        finally:
            fast.close()
    finally:
        source.close()
