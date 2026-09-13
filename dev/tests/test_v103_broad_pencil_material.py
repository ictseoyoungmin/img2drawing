from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageChops

from img2drawing.core.ir import Stroke, StrokeIR
from img2drawing.render.renderer_registry import resolve_renderer


V10 = ("pillow-pencil-contact-v10", "1")
V11 = ("pillow-pencil-contact-v11", "1")
PAPER = {"paper": {"tooth": 0.46, "scale": 1.0, "seed": 170817}}


def _stroke(width: float, *, stroke_id: str) -> Stroke:
    return Stroke(
        points=[(28, 45), (100, 42), (190, 48), (285, 45)],
        width=width,
        opacity=0.86,
        role="gesture",
        pressure=[0.65, 0.65, 0.65, 0.65],
        pressure_authored=True,
        stroke_id=stroke_id,
        tool_state={
            "pressure": 0.65,
            "hardness": 0.66,
            "grain": 0.38,
            "taper_in": 0.0,
            "taper_out": 0.0,
            "jitter": 0.0,
            "provenance": {
                "metadata": {
                    "markmaking": {
                        "material_policy": {
                            "policy_id": "canonical-pencil",
                            "value_authority": "strict",
                            "core_preservation": 0.92,
                            "shoulder_breakup": 0.28,
                            "grain_exposure": 0.32,
                            "local_variation": 0.24,
                        }
                    }
                }
            },
        },
    )


def _render(tmp_path: Path, identity: tuple[str, str], width: float) -> Path:
    ir = StrokeIR(
        320,
        90,
        strokes=[_stroke(width, stroke_id=f"w-{width:g}")],
        metadata=PAPER,
    )
    path = tmp_path / f"{identity[0]}-{width:g}.png"
    resolve_renderer(*identity).render(ir, path, supersample=4)
    return path


def _darkness(path: Path) -> np.ndarray:
    with Image.open(path) as image:
        return np.float32(255.0) - np.asarray(image.convert("L"), dtype=np.float32)


def test_v11_delegates_ordinary_thin_pixels_exactly_to_v10(tmp_path: Path) -> None:
    v10 = _render(tmp_path, V10, 2.0)
    v11 = _render(tmp_path, V11, 2.0)
    with Image.open(v10) as a, Image.open(v11) as b:
        diff = ImageChops.difference(a.convert("RGB"), b.convert("RGB"))
        assert diff.getbbox() is None


def test_v11_rounds_transitional_broad_terminal_without_reauthoring_body_value(tmp_path: Path) -> None:
    v10 = _darkness(_render(tmp_path, V10, 8.0))
    v11 = _darkness(_render(tmp_path, V11, 8.0))

    # The authored path begins at x=28. A physical round contact should extend graphite
    # behind that point; v10's high-alpha continuity core ends in a visible butt/square cut.
    terminal = np.s_[36:55, 20:29]
    assert float(v11[terminal].sum()) > float(v10[terminal].sum()) * 1.5

    # Fixing the cap must not substantially darken or wash out the authored body.
    body = np.s_[35:56, 80:235]
    mean10 = float(v10[body].mean())
    mean11 = float(v11[body].mean())
    assert abs(mean11 - mean10) / max(mean10, 1.0) < 0.04


def test_v11_broad_core_exposes_more_page_fixed_graphite_variation(tmp_path: Path) -> None:
    v10 = _darkness(_render(tmp_path, V10, 14.0))
    v11 = _darkness(_render(tmp_path, V11, 14.0))

    # Center strip excludes most edge-shape variance so this measures material variation,
    # not merely a wider silhouette. v11 intentionally strengthens tooth/grain locally while
    # mean-normalizing the modulation to preserve authored value authority.
    core = np.s_[44:47, 80:235]
    std10 = float(v10[core].std())
    std11 = float(v11[core].std())
    mean10 = float(v10[core].mean())
    mean11 = float(v11[core].mean())
    assert std11 > std10 * 1.05
    assert abs(mean11 - mean10) / max(mean10, 1.0) < 0.04
