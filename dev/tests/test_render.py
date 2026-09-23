"""Behavioral properties of the pencil renderer (exact pixels are pinned by the v11 golden)."""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops

from img2drawing import DrawingSession
from img2drawing.authoring import resolve_markmaking
from img2drawing.core.ir import Stroke, StrokeIR
from img2drawing.render import render_image
from img2drawing.timelapse.frames import FastFrameSource

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "skills" / "img2drawing" / "src"
PAPER = {"paper": {"tooth": 0.46, "scale": 1.0, "seed": 170817}}


def _darkness(ir: StrokeIR) -> np.ndarray:
    return np.float32(255.0) - np.asarray(render_image(ir, supersample=4).convert("L"), dtype=np.float32)


def _line(width: float, *, stroke_id: str) -> Stroke:
    return Stroke(
        points=[(28, 45), (100, 42), (190, 48), (285, 45)],
        width=width,
        opacity=0.86,
        role="gesture",
        pressure=[0.65] * 4,
        pressure_authored=True,
        stroke_id=stroke_id,
        tool_state={"pressure": 0.65, "hardness": 0.66, "grain": 0.38, "taper_in": 0.0, "taper_out": 0.0, "jitter": 0.0},
    )


def _core_darkness(width: float, pressure: float = 1.0) -> float:
    ir = StrokeIR(180, 80, metadata={"paper": {"tooth": 0.5, "scale": 1.0, "seed": 170817}})
    ir.add(Stroke(
        points=[(20.0, 40.0), (160.0, 40.0)], width=width, opacity=0.95, role="material-probe",
        stroke_id=f"probe-w{width}-p{pressure}", pressure=[pressure, pressure], pressure_authored=True,
        tool_state={"hardness": 0.65, "grain": 0.30, "pressure": pressure},
    ).cleaned())
    # Authored core only: a broad dry shoulder may change without masking core collapse.
    return float(np.mean(_darkness(ir)[40, 50:130]))


def test_src_modules_are_named_by_role_not_renderer_generation() -> None:
    generation_tag = re.compile(r"(?:^|_)v\d+(?=_|\.py$)")
    offenders = sorted(p.relative_to(SRC).as_posix() for p in SRC.rglob("*.py") if generation_tag.search(p.name))
    assert offenders == []
    render_modules = sorted(p.stem for p in (SRC / "img2drawing" / "render").glob("*.py"))
    assert render_modules == [
        "__init__", "artifact", "contact_profile", "contract", "deposit", "eraser",
        "grades", "hand", "paper", "pencil", "profile",
    ]


def test_broad_stroke_has_a_physical_round_terminal() -> None:
    darkness = _darkness(StrokeIR(320, 90, [_line(8.0, stroke_id="w8")], PAPER))
    # The authored path begins at x=28; round contact must deposit graphite behind it
    # rather than ending the core in a square cut.
    behind_start = float(darkness[36:55, 20:29].mean())
    body = float(darkness[35:56, 80:235].mean())
    assert behind_start >= 0.25 * body


def test_broad_core_shows_page_fixed_graphite_variation() -> None:
    darkness = _darkness(StrokeIR(320, 90, [_line(14.0, stroke_id="w14")], PAPER))
    core = darkness[44:47, 80:235]
    assert float(core.std()) / float(core.mean()) > 0.12


def test_authored_core_does_not_collapse_when_contact_turns_broad() -> None:
    threshold = _core_darkness(4.5)
    assert min(_core_darkness(width) for width in (6.0, 8.0, 10.0)) >= threshold * 0.90


def test_broad_core_is_strongly_monotone_in_authored_pressure() -> None:
    low, medium, high = (_core_darkness(8.0, p) for p in (0.25, 0.55, 1.0))
    assert low < medium < high
    assert high >= medium * 1.45


def _subject(tmp_path: Path) -> Path:
    path = tmp_path / "subject.png"
    Image.new("RGB", (160, 80), (255, 255, 255)).save(path)
    return path


def test_material_policies_change_actual_broad_pixels(tmp_path: Path) -> None:
    subject = _subject(tmp_path)
    means: dict[str, float] = {}
    hashes: dict[str, str] = {}
    for policy in ("canonical-pencil", "manga-light", "dry-graphite-expressive"):
        session = DrawingSession.create(subject=subject, output_dir=tmp_path / policy)
        mark = resolve_markmaking(
            "pencil_loose", "broad_mass", material_policy=policy,
            modifiers={"width": 8.4, "pressure": 0.96, "opacity": 0.98},
        )
        session.draw(((16, 40), (58, 36), (104, 43), (144, 39)), stroke_id="broad", part="material-probe",
                     pressure=(1.0, 1.0, 1.0, 1.0), **mark.draw_kwargs())
        path = tmp_path / f"{policy}.png"
        hashes[policy] = session.render_final(path).pixel_sha256
        with Image.open(path) as image:
            means[policy] = float(np.asarray(image.convert("L").crop((12, 24, 148, 56))).mean())
    assert len(set(hashes.values())) == 3
    assert means["canonical-pencil"] < means["manga-light"]


def test_fast_final_matches_canonical_after_a_late_lower_layer(tmp_path: Path) -> None:
    session = DrawingSession.create(subject=_subject(tmp_path), output_dir=tmp_path / "fast-run")
    high = resolve_markmaking("pencil_loose", "contour", modifiers={"width": 6.2, "pressure": 0.82, "opacity": 0.90})
    low = resolve_markmaking("pencil_loose", "form", modifiers={"width": 7.0, "pressure": 0.68, "opacity": 0.78})
    session.draw(((20, 26), (80, 48), (140, 26)), stroke_id="high-layer", part="overlap", layer=5, **high.draw_kwargs())
    session.draw(((20, 48), (80, 26), (140, 48)), stroke_id="late-low-layer", part="overlap", layer=1, **low.draw_kwargs())
    canonical_path = tmp_path / "canonical.png"
    session.render_final(canonical_path)

    source = FastFrameSource(session._agent.history, session.render_profile)
    try:
        assert source.advance_to(1)["mode"] == "append"
        assert source.advance_to(2)["mode"] == "layer-reorder-dirty"
        fast = source.image()
        with Image.open(canonical_path) as canonical:
            assert ImageChops.difference(fast.convert("RGB"), canonical.convert("RGB")).getbbox() is None
        fast.close()
    finally:
        source.close()
