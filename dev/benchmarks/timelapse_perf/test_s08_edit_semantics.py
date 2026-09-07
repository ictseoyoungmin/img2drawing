from __future__ import annotations

import hashlib
import sys
from copy import deepcopy
from pathlib import Path

import pytest
from PIL import Image

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO / "skills" / "img2drawing" / "src"))
sys.path.insert(0, str(HERE))

from img2drawing.core.action import AgentDrawingSession
from img2drawing.core.history import CanvasHistory
from img2drawing.core.ir import Stroke, StrokeIR
from img2drawing.core.tools import get_tool
from img2drawing.render.pillow_pencil_contact import render as render_production
from alpha_active_pencil_renderer import AlphaActiveEditAwareCanvas


def _pix(image: Image.Image) -> str:
    return hashlib.sha256(image.convert("RGBA").tobytes()).hexdigest()


def _stroke(sid: str, points, pressure, *, width=3.2, opacity=0.74, layer=0) -> Stroke:
    tool = get_tool("form_pencil").to_dict()
    return Stroke(
        points=[tuple(map(float, point)) for point in points],
        width=float(width),
        opacity=float(opacity),
        role="form",
        layer=int(layer),
        stroke_id=sid,
        pressure=[float(value) for value in pressure],
        pressure_authored=True,
        tool_state=tool,
    ).cleaned()


def _history() -> CanvasHistory:
    history = CanvasHistory(
        320,
        240,
        metadata={"paper_tooth": 0.58, "paper_scale": 1.0, "paper_seed": 77},
    )
    history.add_stroke(
        _stroke(
            "a",
            [(20, 45), (85, 55), (150, 70), (220, 80), (292, 92)],
            [0.30, 0.55, 0.82, 0.60, 0.35],
            width=3.1,
            opacity=0.72,
            layer=0,
        ),
        stroke_id="a",
    )
    history.add_stroke(
        _stroke(
            "b",
            [(35, 185), (95, 150), (160, 120), (225, 90), (285, 55)],
            [0.28, 0.52, 0.86, 0.64, 0.33],
            width=4.0,
            opacity=0.82,
            layer=1,
        ),
        stroke_id="b",
    )
    history.add_stroke(
        _stroke(
            "c",
            [(25, 118), (90, 112), (160, 116), (230, 125), (295, 132)],
            [0.35, 0.62, 0.78, 0.58, 0.31],
            width=2.4,
            opacity=0.66,
            layer=2,
        ),
        stroke_id="c",
    )
    return history


def _render_exact(ir: StrokeIR, path: Path, *, supersample: int = 2) -> str:
    render_production(ir, path, supersample=supersample)
    with Image.open(path) as image:
        return _pix(image)


def test_current_semantic_edits_remain_pixel_exact_in_incremental_replay(tmp_path):
    history = _history()
    states = [deepcopy(history.state_at())]

    history.replace_segment(
        "b",
        1,
        3,
        [(95, 150), (150, 105), (225, 90)],
        pressure=[0.52, 0.91, 0.64],
        lock_boundaries=True,
        stage="s08",
    )
    states.append(deepcopy(history.state_at()))

    history.soft_lift_segment(
        "b",
        1,
        3,
        get_tool("soft_eraser"),
        strength=0.42,
        feather_points=1,
        stage="s08",
    )
    states.append(deepcopy(history.state_at()))

    history.soft_lift("a", get_tool("soft_eraser"), strength=0.35, stage="s08")
    states.append(deepcopy(history.state_at()))

    before_retune = next(stroke for stroke in history.state_at().strokes if stroke.stroke_id == "c")
    retuned = deepcopy(before_retune)
    retuned.opacity = 0.42
    retuned.tool_state = deepcopy(retuned.tool_state)
    retuned.tool_state["grain"] = 0.24
    before_geometry = tuple(before_retune.points)
    history.replace_stroke("c", retuned, new_stroke_id="c")
    after_retune = next(stroke for stroke in history.state_at().strokes if stroke.stroke_id == "c")
    assert tuple(after_retune.points) == before_geometry
    states.append(deepcopy(history.state_at()))

    history.hard_delete("b", get_tool("hard_eraser"), stage="s08")
    states.append(deepcopy(history.state_at()))

    assert [action.action for action in history.actions[-5:]] == [
        "stroke.segment_replace",
        "stroke.segment_soft_lift",
        "stroke.soft_lift",
        "stroke.replace",
        "stroke.delete",
    ]

    canvas = AlphaActiveEditAwareCanvas(states[0], supersample=2)
    try:
        for index, ir in enumerate(states):
            canvas.advance_to(ir)
            got = canvas.snapshot_image()
            try:
                expected = _render_exact(ir, tmp_path / f"production_{index:02d}.png")
                assert _pix(got) == expected
            finally:
                got.close()
    finally:
        canvas.close()


def test_raw_spatial_eraser_is_production_compatible_but_fast_path_ineligible(tmp_path):
    draw = _stroke(
        "draw",
        [(35, 120), (100, 116), (170, 120), (235, 124), (290, 120)],
        [0.45, 0.70, 0.82, 0.68, 0.42],
        width=8.0,
        opacity=0.90,
        layer=0,
    )
    eraser_tool = get_tool("soft_eraser")
    eraser = Stroke(
        points=[(160.0, 70.0), (160.0, 170.0)],
        width=eraser_tool.width,
        opacity=eraser_tool.opacity,
        role="eraser",
        layer=1,
        stroke_id="eraser",
        pressure=[0.8, 0.8],
        pressure_authored=True,
        tool_state=eraser_tool.to_dict(),
    ).cleaned()
    metadata = {"paper_tooth": 0.58, "paper_scale": 1.0, "paper_seed": 77}
    draw_only = StrokeIR(320, 240, strokes=[draw], metadata=metadata)
    raw_eraser = StrokeIR(320, 240, strokes=[draw, eraser], metadata=metadata)

    draw_hash = _render_exact(draw_only, tmp_path / "draw_only.png")
    erased_hash = _render_exact(raw_eraser, tmp_path / "raw_eraser.png")
    assert draw_hash != erased_hash

    canvas = AlphaActiveEditAwareCanvas(draw_only, supersample=2)
    try:
        canvas.advance_to(draw_only)
        with pytest.raises(ValueError, match="eraser"):
            canvas.advance_to(raw_eraser)
    finally:
        canvas.close()

    agent = AgentDrawingSession(320, 240)
    with pytest.raises(ValueError, match="erase-mode tool"):
        agent.execute(
            {
                "action_id": "erase-as-draw",
                "kind": "draw_stroke",
                "stage": "s08",
                "role": "form",
                "points": [[50, 50], [120, 120]],
                "tool": {"preset": "soft_eraser", "grade": "2B"},
                "observation_id": "vnext-unobserved",
                "source_observation": "imaginative",
            }
        )
