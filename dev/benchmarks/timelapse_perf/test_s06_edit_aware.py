from __future__ import annotations

import hashlib
import sys
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(HERE))

from img2drawing.core.ir import Stroke, StrokeIR
from cached_pencil_renderer import render_cached
from edit_aware_pencil_renderer import EditAwareIncrementalPencilCanvas
from material_kernel_pencil_renderer import KernelStrokeRasterCache


def pix(image: Image.Image) -> str:
    rgba = image.convert("RGBA")
    try:
        return hashlib.sha256(rgba.tobytes()).hexdigest()
    finally:
        rgba.close()


def make_ir(strokes):
    return StrokeIR(
        320,
        240,
        strokes=strokes,
        metadata={"paper_tooth": 0.58, "paper_scale": 1.0, "paper_seed": 77},
    )


def stroke(sid, points, width=3.0, opacity=0.8, layer=0):
    return Stroke(
        points=points,
        width=width,
        opacity=opacity,
        role="form",
        layer=layer,
        stroke_id=sid,
        pressure=[0.4, 0.8],
        pressure_authored=True,
        tool_state={
            "tool": "pencil_form",
            "grain": 0.38,
            "hardness": 0.48,
            "flow": 0.84,
            "stabilization": 0.18,
        },
    )


def test_replace_delete_soft_lift_like_content_change_exact(tmp_path):
    a = stroke("a", [(20, 30), (270, 50)], 3.0, 0.72)
    b = stroke("b", [(40, 180), (280, 70)], 4.0, 0.82)
    c = stroke("c", [(30, 110), (290, 120)], 2.2, 0.65)
    states = [
        make_ir([a, b, c]),
        make_ir([a, stroke("b", [(42, 178), (275, 78)], 5.2, 0.75), c]),
        make_ir([a, stroke("b", [(42, 178), (275, 78)], 5.2, 0.75)]),
        make_ir([
            stroke("a", [(20, 30), (270, 50)], 3.0, 0.30),
            stroke("b", [(42, 178), (275, 78)], 5.2, 0.75),
        ]),
    ]
    cache = KernelStrokeRasterCache()
    canvas = EditAwareIncrementalPencilCanvas(states[0], cache, supersample=2)
    try:
        for index, ir in enumerate(states):
            canvas.advance_to(ir)
            got = canvas.snapshot_image()
            ref = tmp_path / f"ref_{index}.png"
            render_cached(ir, ref, cache, supersample=2)
            with Image.open(ref) as reference:
                assert pix(got) == pix(reference)
            got.close()
    finally:
        canvas.close()
        cache.close()
