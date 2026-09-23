"""Pixel golden for the current v11 pencil renderer and its session output paths.

The expected hashes were recorded from the v1.0.3 source before the v1.1 structural
refactor. Any change to these digests is a pixel change and must be an intentional,
versioned renderer decision rather than a side effect of moving code.

Regenerate only when a renderer change is deliberate:

    IMG2DRAWING_REGEN_GOLDEN=1 python -m pytest dev/tests/test_v11_render_golden.py
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
from pathlib import Path

import pytest
from PIL import Image

from img2drawing import DrawingSession, RenderProfile
from img2drawing.core.ir import Stroke, StrokeIR

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = ROOT / "dev" / "fixtures" / "v11-golden"
GOLDEN_PATH = FIXTURES / "golden.json"
REGEN = os.environ.get("IMG2DRAWING_REGEN_GOLDEN") == "1"


def _current_render():
    from img2drawing.render.renderer_registry import current_renderer

    return current_renderer().render


def _pixel_sha(path: Path) -> str:
    with Image.open(path) as image:
        rgba = image.convert("RGBA")
        return hashlib.sha256(f"{rgba.size}".encode() + rgba.tobytes()).hexdigest()


def _load_golden() -> dict[str, str]:
    if GOLDEN_PATH.exists():
        return json.loads(GOLDEN_PATH.read_text(encoding="utf-8"))
    return {}


_RECORDED: dict[str, str] = {}


def _check(key: str, digest: str) -> None:
    if REGEN:
        _RECORDED[key] = digest
        merged = {**_load_golden(), **_RECORDED}
        GOLDEN_PATH.write_text(json.dumps(merged, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return
    golden = _load_golden()
    assert key in golden, f"missing golden digest for {key}; regenerate deliberately"
    assert digest == golden[key], f"v11 pixel drift for {key}"


def _ir_from_fixture(name: str) -> StrokeIR:
    data = json.loads((FIXTURES / f"{name}.ir.json").read_text(encoding="utf-8"))
    strokes = []
    for raw in data["strokes"]:
        raw = dict(raw)
        raw["points"] = [tuple(point) for point in raw["points"]]
        strokes.append(Stroke(**raw))
    return StrokeIR(data["width"], data["height"], strokes, {})


def _tool(**values) -> dict:
    base = {
        "tool": "form_pencil",
        "width": 3.2,
        "pressure": 0.58,
        "opacity": 0.70,
        "hardness": 0.66,
        "grain": 0.36,
        "taper_in": 0.24,
        "taper_out": 0.30,
        "jitter": 0.045,
        "mode": "draw",
        "erase_strength": 0.0,
    }
    base.update(values)
    return base


def _policy(policy_id: str, authority: str, core: float, breakup: float, grain: float, variation: float) -> dict:
    return {
        "markmaking": {
            "material_policy": {
                "policy_id": policy_id,
                "value_authority": authority,
                "core_preservation": core,
                "shoulder_breakup": breakup,
                "grain_exposure": grain,
                "local_variation": variation,
            }
        }
    }


def _wave(x0: float, y: float, length: float, n: int, amp: float) -> list[tuple[float, float]]:
    return [
        (x0 + length * i / (n - 1), y + amp * ((i % 5) - 2) * 0.4 + amp * (i / (n - 1)) ** 2)
        for i in range(n)
    ]


def _synthetic_ir(*, paper: dict | None = None) -> StrokeIR:
    strokes: list[Stroke] = []
    y = 14.0
    widths = (0.8, 1.5, 2.4, 3.2, 4.6, 5.8, 7.0, 8.4, 10.5, 14.0, 20.0)
    for index, width in enumerate(widths):
        n = 6 + index * 3
        pts = _wave(12.0, y, 220.0, n, 1.5 + 0.3 * index)
        pressure = [0.2 + 0.75 * abs(((i / (n - 1)) * 2.0) - 1.0) for i in range(n)] if index % 2 else None
        taper = (0.0, 0.0) if index % 3 == 0 else (0.35, 0.9) if index % 3 == 1 else (0.1, 0.25)
        strokes.append(
            Stroke(
                pts,
                width=width,
                opacity=0.35 + 0.06 * index,
                layer=index % 3,
                pressure=pressure,
                tool_state=_tool(
                    width=width,
                    taper_in=taper[0],
                    taper_out=taper[1],
                    jitter=(0.0, 0.03, 0.08)[index % 3],
                    hardness=(0.2, 0.66, 0.95)[index % 3],
                    grain=(0.1, 0.36, 0.6)[index % 3],
                    pencil_grade=(None, "4H", "HB", "6B")[index % 4],
                ),
                stage=("A1_tool_proof", None, "vnext")[index % 3],
                stroke_id=f"w{index:02d}",
            )
        )
        y += 22.0
    policies = (
        ("canonical-pencil", "strict", 0.92, 0.28, 0.32, 0.24),
        ("manga-light", "balanced", 0.7, 0.4, 0.2, 0.1),
        ("dry-graphite-expressive", "relaxed", 0.55, 0.6, 0.8, 0.45),
    )
    for p_index, policy in enumerate(policies):
        for w_index, width in enumerate((3.0, 6.0, 9.5, 16.0)):
            pts = _wave(250.0, 16.0 + 30.0 * (p_index * 4 + w_index), 180.0, 14, 2.0)
            tool_state = _tool(width=width, taper_in=0.2, taper_out=0.85 if w_index == 1 else 0.3)
            tool_state.update(_policy(*policy))
            strokes.append(
                Stroke(
                    pts,
                    width=width,
                    opacity=0.9,
                    pressure=[0.95] * 14 if w_index % 2 else None,
                    tool_state=tool_state,
                    stroke_id=f"p{p_index}{w_index}",
                )
            )
    # Provenance-nested policy location.
    nested = _tool(width=11.0)
    nested["provenance"] = {"metadata": _policy(*policies[2])}
    strokes.append(Stroke(_wave(20.0, 270.0, 200.0, 9, 4.0), width=11.0, opacity=0.8, tool_state=nested, stroke_id="nested"))
    # Erasers over earlier marks at different strengths / pressures.
    for e_index, (strength, pressure) in enumerate(((0.3, 0.45), (0.8, 0.9), (1.0, 0.2))):
        strokes.append(
            Stroke(
                [(30.0 + 70.0 * e_index, 20.0), (60.0 + 70.0 * e_index, 200.0)],
                width=18.0,
                opacity=1.0,
                layer=5,
                tool_state=_tool(
                    tool="soft_eraser", width=18.0, pressure=pressure, hardness=0.18,
                    grain=0.08, mode="erase", erase_strength=strength,
                ),
                stroke_id=f"e{e_index}",
            )
        )
    # Degenerate strokes: single point and duplicated points.
    strokes.append(Stroke([(300.0, 300.0)], width=4.0, tool_state=_tool(), stroke_id="single"))
    strokes.append(Stroke([(310.0, 300.0), (310.0, 300.0), (340.0, 305.0)], width=4.0, tool_state=_tool(), stroke_id="dup"))
    # Tool-state pressure fallback (no tool_state dict).
    strokes.append(Stroke(_wave(20.0, 296.0, 150.0, 8, 1.0), width=2.0, tool_state=None, stroke_id="bare"))
    metadata = {} if paper is None else {"paper": paper}
    return StrokeIR(460, 380, strokes, metadata)


RENDER_CASES = {
    "synthetic-default-ss4": (lambda: _synthetic_ir(), {"supersample": 4}),
    "synthetic-ss2": (lambda: _synthetic_ir(), {"supersample": 2}),
    "synthetic-ss8": (lambda: _synthetic_ir(), {"supersample": 8}),
    "synthetic-scale2": (lambda: _synthetic_ir(), {"supersample": 4, "scale": 2}),
    "synthetic-paper": (
        lambda: _synthetic_ir(paper={"tooth": 0.8, "scale": 2.2, "seed": 99}),
        {"supersample": 4},
    ),
    "synthetic-no-tooth": (lambda: _synthetic_ir(paper={"tooth": 0.0}), {"supersample": 4}),
    "synthetic-colors-grade": (
        lambda: _synthetic_ir(),
        {"supersample": 4, "graphite": (60, 40, 30), "background": (240, 236, 228, 255), "grade": "2B"},
    ),
    "fixture-s10-quality-run": (lambda: _ir_from_fixture("s10-quality-run"), {"supersample": 4}),
    "fixture-croquis-sniper-girl": (lambda: _ir_from_fixture("croquis-sniper-girl"), {"supersample": 4}),
}


@pytest.mark.parametrize("case", sorted(RENDER_CASES))
def test_v11_backend_render_is_pixel_stable(tmp_path: Path, case: str) -> None:
    build, kwargs = RENDER_CASES[case]
    out = tmp_path / f"{case}.png"
    _current_render()(build(), out, **kwargs)
    _check(f"render/{case}", _pixel_sha(out))


def _session_subject(tmp_path: Path) -> Path:
    path = tmp_path / "subject.png"
    Image.new("RGB", (240, 180), (255, 255, 255)).save(path)
    return path


def _build_session(tmp_path: Path) -> DrawingSession:
    from img2drawing.vnext import resolve_markmaking

    session = DrawingSession.create(
        subject=_session_subject(tmp_path),
        output_dir=tmp_path / "run",
        render_profile=RenderProfile.canonical(240, 180),
    )
    ids = []
    for index, (role, preset, policy) in enumerate(
        (
            ("construction", "construction-light", "canonical-pencil"),
            ("gesture", "gesture-flow", "manga-light"),
            ("contour", "contour-weighted", "canonical-pencil"),
            ("accent", "accent-dark", "dry-graphite-expressive"),
            ("hair", "hair-flick", "manga-light"),
            ("broad_mass", "broad-graphite", "dry-graphite-expressive"),
            ("hatch", "hatch-heavy", "canonical-pencil"),
            ("form", "form-pencil", "canonical-pencil"),
        )
    ):
        mark = resolve_markmaking("pencil_loose", role, tool_preset=preset, material_policy=policy)
        y = 16 + 20 * index
        ids.append(
            session.draw(
                ((14, y), (70, y - 6 + index), (140, y + 4), (220, y - 2)),
                stroke_id=f"m{index}",
                part="golden",
                layer=index % 2,
                **mark.draw_kwargs(),
            )
        )
    session.draw(((20, 170), (120, 150), (220, 172)), stroke_id="plain", tool="continuous_pencil", grade="2B")
    session.replace_stroke("m2", ((14, 58), (80, 50), (150, 62), (222, 54)), reason="golden replace", tool="form_pencil")
    session.replace_segment("m7", 1, 2, ((75, 150), (138, 162)), reason="golden segment")
    session.soft_lift("m3", strength=0.6, reason="golden lift")
    session.delete_stroke("m4", reason="golden delete")
    session.draw(((30, 30), (200, 150)), stroke_id="late", layer=0, tool="accent_pencil")
    return session


def test_v11_session_outputs_are_pixel_stable(tmp_path: Path) -> None:
    session = _build_session(tmp_path)
    cursor = session.history_cursor

    final = session.render_final(tmp_path / "final.png")
    _check("session/final", _pixel_sha(final.path))
    mid = session.render_at(cursor // 2, tmp_path / "mid.png")
    _check("session/mid", _pixel_sha(mid.path))

    sheet = session.inspect()
    _check("session/inspect-raw", _pixel_sha(Path(sheet.drawing)))

    if shutil.which("ffmpeg") is None:
        pytest.skip("ffmpeg unavailable; fast timelapse golden requires it")
    fast = session.export_timelapse(tmp_path / "tl-fast", every_n=2)
    _check("session/timelapse-final", _pixel_sha(fast.final_path))
    with Image.open(fast.gif_path) as gif:
        frames = []
        for index in range(gif.n_frames):
            gif.seek(index)
            frames.append(hashlib.sha256(gif.convert("RGB").tobytes()).hexdigest())
    _check("session/timelapse-gif-frames", hashlib.sha256("".join(frames).encode()).hexdigest())

    from img2drawing.vnext.output import export_session_timelapse

    canonical = export_session_timelapse(session, tmp_path / "tl-canonical", every_n=2, backend="canonical")
    _check("session/timelapse-canonical-final", _pixel_sha(canonical.final_path))
    frame_hashes = [
        _pixel_sha(path) for path in sorted(Path(canonical.frame_dir).glob("*.png"))
    ]
    _check("session/timelapse-canonical-frames", hashlib.sha256("".join(frame_hashes).encode()).hexdigest())
