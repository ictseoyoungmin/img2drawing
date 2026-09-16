from __future__ import annotations

import json
from pathlib import Path

from PIL import Image
import pytest

from img2drawing import DrawingIntent, DrawingSession, ReferenceAuthority
from img2drawing.inspection import WIPGuideStyle, render_wip_guides
from img2drawing.runtime import runtime_capabilities


def _session(tmp_path: Path) -> DrawingSession:
    session = DrawingSession.create(
        canvas=(100, 80),
        output_dir=tmp_path,
        session_id="wip-guide-visibility",
        intent=DrawingIntent(reference_mode="imaginative", drawing_mode="free_draw"),
        reference_authority=ReferenceAuthority.imaginative(("WIP guide visibility test fixture",)),
    )
    observation_id = session.observe({"construction": "two explicit working axes"})
    session.draw(
        ((10, 20), (90, 20)),
        action_id="draw-guide",
        stroke_id="guide-line",
        role="structure",
        part="shoulder-axis",
        observation_id=observation_id,
    )
    session.draw(
        ((10, 60), (90, 60)),
        action_id="draw-control",
        stroke_id="control-line",
        role="contour",
        part="control-boundary",
        observation_id=observation_id,
    )
    return session


def _inspection_raw(session: DrawingSession) -> tuple[str, Path]:
    session.inspect(supersample=2)
    record = session.inspection_history[-1]
    manifest_path = session.output_dir / record["manifest"]
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    return str(record["inspection_id"]), manifest_path.parent / manifest["artifacts"]["raw_drawing"]


def test_wip_guide_view_boosts_only_selected_strokes_without_mutating_authoring_state(tmp_path: Path) -> None:
    session = _session(tmp_path)
    inspection_id, raw_path = _inspection_raw(session)
    before_state = session.drawing_state_hash()
    before_cursor = session.history_cursor
    before_raw = raw_path.read_bytes()

    red = render_wip_guides(
        session,
        ("guide-line",),
        color=(255, 40, 30),
        width_scale=3.0,
        opacity=1.0,
        inspection_id=inspection_id,
    )

    assert red.path.is_file()
    assert red.manifest_path.is_file()
    assert red.inspection_id == inspection_id
    assert red.stroke_ids == ("guide-line",)
    assert red.style == WIPGuideStyle(color=(255, 40, 30), width_scale=3.0, opacity=1.0)
    assert red.to_dict()["display_only"] is True
    assert session.drawing_state_hash() == before_state
    assert session.history_cursor == before_cursor
    assert raw_path.read_bytes() == before_raw

    with Image.open(raw_path) as raw_source, Image.open(red.path) as wip_source:
        raw = raw_source.convert("RGB")
        wip = wip_source.convert("RGB")
        assert raw.size == wip.size == (100, 80)
        assert wip.getpixel((50, 20))[0] > wip.getpixel((50, 20))[2]
        assert wip.getpixel((50, 20)) != raw.getpixel((50, 20))
        assert wip.getpixel((50, 60)) == raw.getpixel((50, 60))

    blue = render_wip_guides(
        session,
        ("guide-line",),
        color=(20, 120, 255),
        width_scale=2.0,
        opacity=0.75,
        inspection_id=inspection_id,
    )
    assert blue.path != red.path
    assert blue.manifest_path != red.manifest_path
    assert red.path.is_file() and blue.path.is_file()


def test_wip_guide_view_rejects_stale_inspections_and_noncurrent_stroke_ids(tmp_path: Path) -> None:
    session = _session(tmp_path)
    inspection_id, _ = _inspection_raw(session)

    with pytest.raises(ValueError, match="not current authored strokes"):
        render_wip_guides(session, ("missing-guide",), inspection_id=inspection_id)

    observation_id = session.observe({"correction": "new current mark invalidates old inspection"})
    session.draw(
        ((20, 10), (20, 70)),
        action_id="draw-later",
        stroke_id="later-line",
        role="structure",
        part="later-axis",
        observation_id=observation_id,
    )
    with pytest.raises(ValueError, match="fresh inspection"):
        render_wip_guides(session, ("guide-line",), inspection_id=inspection_id)


def test_wip_style_is_bounded_and_runtime_manifest_is_stroke_only() -> None:
    with pytest.raises(ValueError, match="width_scale"):
        WIPGuideStyle(width_scale=0.5)
    with pytest.raises(ValueError, match="opacity"):
        WIPGuideStyle(opacity=0.1)
    with pytest.raises(ValueError, match="RGB"):
        WIPGuideStyle(color=(256, 0, 0))

    operations = runtime_capabilities().supported_authoring_operations
    assert "fill" not in operations
    assert "replace-fill" not in operations
    assert {"draw", "replace-stroke", "soften-stroke", "delete-stroke"}.issubset(operations)
