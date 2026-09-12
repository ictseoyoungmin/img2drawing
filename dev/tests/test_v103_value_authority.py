from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image

from img2drawing.core.ir import Stroke, StrokeIR
from img2drawing.render.renderer_registry import resolve_renderer


V10 = ("pillow-pencil-contact-v10", "1")


def _core_darkness(
    tmp_path: Path,
    *,
    width: float,
    pressure: float = 1.0,
    opacity: float = 0.95,
) -> float:
    ir = StrokeIR(
        180,
        80,
        metadata={"paper": {"tooth": 0.5, "scale": 1.0, "seed": 170817}},
    )
    ir.add(
        Stroke(
            points=[(20.0, 40.0), (160.0, 40.0)],
            width=float(width),
            opacity=float(opacity),
            role="material-probe",
            part="value-authority",
            stage="compatibility-only",
            layer=0,
            stroke_id=f"probe-w{width}-p{pressure}",
            pressure=[float(pressure), float(pressure)],
            pressure_authored=True,
            tool_state={
                "hardness": 0.65,
                "grain": 0.30,
                "pressure": float(pressure),
            },
        ).cleaned()
    )
    path = tmp_path / f"w{width}-p{pressure}.png"
    resolve_renderer(*V10).render(
        ir,
        path,
        supersample=4,
        graphite=(36, 34, 32),
    )
    with Image.open(path) as image:
        luminance = np.asarray(image.convert("L"), dtype=np.float32)
    # Measure the authored core, not shoulder area. Darkness is 0 on paper and rises
    # toward black, so a broad dry shoulder may change without masking core collapse.
    center = 255.0 - luminance[40, 50:130]
    return float(np.mean(center))


def test_high_authority_core_does_not_collapse_at_broad_threshold(tmp_path: Path) -> None:
    threshold = _core_darkness(tmp_path, width=4.5)
    broad = [_core_darkness(tmp_path, width=width) for width in (6.0, 8.0, 10.0)]

    # Width may redistribute graphite into a dry shoulder, but entering the broad
    # material regime must not erase a deliberately dark authored core. The old RC
    # defect fell to roughly half the threshold darkness at 6-8 px.
    assert min(broad) >= threshold * 0.90


def test_broad_core_remains_strongly_monotone_in_authored_pressure(tmp_path: Path) -> None:
    low = _core_darkness(tmp_path, width=8.0, pressure=0.25)
    medium = _core_darkness(tmp_path, width=8.0, pressure=0.55)
    high = _core_darkness(tmp_path, width=8.0, pressure=1.0)

    assert low < medium < high
    assert high >= medium * 1.45
