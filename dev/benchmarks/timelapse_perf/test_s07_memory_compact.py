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
from material_kernel_pencil_renderer import KernelStrokeRasterCache
from alpha_active_pencil_renderer import AlphaActiveEditAwareCanvas, _alpha_source_over


def pix(im: Image.Image) -> str:
    return hashlib.sha256(im.convert("RGBA").tobytes()).hexdigest()


def mk(strokes):
    return StrokeIR(
        320,
        240,
        strokes=strokes,
        metadata={"paper_tooth": 0.58, "paper_scale": 1.0, "paper_seed": 77},
    )


def s(sid, pts, width=3.0, opacity=0.8, layer=0):
    return Stroke(
        points=pts,
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


def test_alpha_source_over_matches_pillow_exactly():
    vals = bytes(range(256)) * 256
    src = Image.frombytes("L", (256 * 256, 1), vals)
    dst = Image.frombytes("L", (256 * 256, 1), b"".join(bytes([d]) * 256 for d in range(256)))
    graphite = Image.new("RGBA", src.size, (36, 34, 32, 0))
    graphite.putalpha(dst)
    layer = Image.new("RGBA", src.size, (36, 34, 32, 0))
    layer.putalpha(src)
    ref = Image.alpha_composite(graphite, layer).getchannel("A")
    got = _alpha_source_over(dst, src)
    assert ref.tobytes() == got.tobytes()


def test_memory_compact_replace_delete_content_change_exact(tmp_path):
    a = s("a", [(20, 30), (270, 50)], 3.0, 0.72)
    b = s("b", [(40, 180), (280, 70)], 4.0, 0.82)
    c = s("c", [(30, 110), (290, 120)], 2.2, 0.65)
    states = [
        mk([a, b, c]),
        mk([a, s("b", [(42, 178), (275, 78)], 5.2, 0.75), c]),
        mk([a, s("b", [(42, 178), (275, 78)], 5.2, 0.75)]),
        mk([s("a", [(20, 30), (270, 50)], 3.0, 0.30), s("b", [(42, 178), (275, 78)], 5.2, 0.75)]),
    ]
    canvas = AlphaActiveEditAwareCanvas(states[0], supersample=2)
    cache = KernelStrokeRasterCache()
    try:
        for index, ir in enumerate(states):
            canvas.advance_to(ir)
            got = canvas.snapshot_image()
            ref = tmp_path / f"ref_{index}.png"
            render_cached(ir, ref, cache, supersample=2)
            with Image.open(ref) as image:
                assert pix(got) == pix(image)
            got.close()
        assert canvas.canvas_bytes_estimate == 320 * 2 * 240 * 2
        assert canvas.stats.released_materials == 3
    finally:
        canvas.close()
        cache.close()
