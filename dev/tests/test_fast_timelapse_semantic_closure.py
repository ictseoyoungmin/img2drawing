from __future__ import annotations

import hashlib
from copy import deepcopy
from pathlib import Path

from PIL import Image

from img2drawing.core.history import CanvasHistory
from img2drawing.core.ir import Stroke
from img2drawing.core.tools import get_tool
from img2drawing.render.pillow_pencil_contact import render as canonical_render

from img2drawing.provenance.fast_timelapse.frame_source import FastFrameSource, FastPathIneligible, FrameRenderConfig, inspect_fast_path_eligibility


def _hash_image(image: Image.Image) -> str:
    return hashlib.sha256(image.convert("RGBA").tobytes()).hexdigest()


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


def _history_and_cursors():
    h = CanvasHistory(320, 240, metadata={"paper_tooth": 0.58, "paper_scale": 1.0, "paper_seed": 77})
    h.add_stroke(_stroke("a", [(20,45),(85,55),(150,70),(220,80),(292,92)], [0.3,0.55,0.82,0.6,0.35], layer=0), stroke_id="a")
    h.add_stroke(_stroke("b", [(35,185),(95,150),(160,120),(225,90),(285,55)], [0.28,0.52,0.86,0.64,0.33], layer=1, width=4.0, opacity=0.82), stroke_id="b")
    h.add_stroke(_stroke("c", [(25,118),(90,112),(160,116),(230,125),(295,132)], [0.35,0.62,0.78,0.58,0.31], layer=2, width=2.4, opacity=0.66), stroke_id="c")
    states = [("initial_adds", h.cursor)]

    h.replace_segment("b", 1, 3, [(95,150),(150,105),(225,90)], pressure=[0.52,0.91,0.64], lock_boundaries=True, stage="local-integration")
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


def test_semantic_edits_are_pixel_exact(tmp_path: Path):
    history, states = _history_and_cursors()
    config = FrameRenderConfig((255,255,255,255), (36,34,32), 1, 2)
    source = FastFrameSource(history, config)
    try:
        for label, cursor in states:
            info = source.advance_to(cursor)
            got = source.image()
            expected_path = tmp_path / f"canonical_{cursor:03d}_{label}.png"
            canonical_render(history.state_at(cursor), expected_path, supersample=2)
            with Image.open(expected_path) as expected:
                assert _hash_image(got) == _hash_image(expected), (label, cursor, info)
            got.close()
    finally:
        source.close()


def test_raw_spatial_eraser_fails_closed():
    h = CanvasHistory(128, 96, metadata={"paper_tooth":0.5, "paper_scale":1.0, "paper_seed":12})
    h.add_stroke(_stroke("a", [(10,20),(90,60)], [0.4,0.7], layer=0), stroke_id="a")
    eraser_tool = get_tool("soft_eraser")
    raw = Stroke(
        points=[(30.0, 10.0), (50.0, 80.0)], width=8.0, opacity=1.0,
        role="correction", stage="legacy-raw-eraser", layer=1, stroke_id="e",
        pressure=[0.8,0.8], pressure_authored=True, tool_state=eraser_tool.to_dict(),
    ).cleaned()
    h.add_stroke(raw, stroke_id="e")
    eligibility = inspect_fast_path_eligibility(h)
    assert eligibility.eligible is False
    assert eligibility.raw_spatial_eraser_seen is True
    try:
        FastFrameSource(h, FrameRenderConfig((255,255,255,255),(36,34,32),1,2))
    except FastPathIneligible:
        pass
    else:
        raise AssertionError("raw spatial eraser must fail closed")
