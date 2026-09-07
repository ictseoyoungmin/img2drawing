from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import pytest
from PIL import Image, ImageDraw

from img2drawing.core.ir import Stroke
from img2drawing.core.session import DrawingSession
from img2drawing.core.tools import ToolState
from img2drawing.provenance.streaming import (
    ResumeMismatchError,
    SimulatedInterruption,
    export_timelapse_streaming,
)


def _session(path: Path) -> DrawingSession:
    session = DrawingSession.create("s09-streaming-resume", 64, 48)
    for index in range(6):
        session.history.add_stroke(
            Stroke(
                points=[(4 + index * 5, 5), (10 + index * 5, 40)],
                width=2.0,
                opacity=0.8,
                role="form",
                stage="vnext",
                stroke_id=f"s{index}",
                tool_state={"pressure": 0.6, "width": 2.0, "opacity": 0.8, "mode": "draw"},
            )
        )
    session.history.marker("stage_end:test")
    eraser = ToolState(
        tool="eraser",
        mode="erase",
        pressure=0.5,
        width=4.0,
        opacity=1.0,
        hardness=0.2,
        grain=0.1,
        taper_in=0.1,
        taper_out=0.1,
        jitter=0.0,
        erase_strength=0.5,
    )
    session.history.hard_delete("s1", eraser, stage="vnext")
    session.save(path)
    return session


def _renderer(ir, path, **_kwargs) -> None:
    image = Image.new("RGBA", (64, 48), (255, 255, 255, 255))
    draw = ImageDraw.Draw(image)
    for index, stroke in enumerate(sorted(ir.strokes, key=lambda item: item.layer)):
        draw.line(
            [(int(x), int(y)) for x, y in stroke.points],
            fill=(30 + index * 5, 30 + index * 5, 30 + index * 5, 255),
            width=max(1, int(stroke.width)),
        )
    image.save(path)
    image.close()


def _decoded_hashes(path: Path) -> list[str]:
    image = Image.open(path)
    hashes = []
    try:
        for index in range(image.n_frames):
            image.seek(index)
            hashes.append(hashlib.sha256(image.convert("RGB").tobytes()).hexdigest())
    finally:
        image.close()
    return hashes


def test_streaming_resume_truncates_partial_tail_and_matches_uninterrupted(tmp_path: Path):
    session_path = tmp_path / "session.json"
    _session(session_path)
    uninterrupted = export_timelapse_streaming(
        session_path,
        tmp_path / "uninterrupted",
        every_n=2,
        renderer=_renderer,
        renderer_id="s09-test-renderer",
        colors=32,
        delta_bbox=True,
    )

    resume_dir = tmp_path / "resumed"
    with pytest.raises(SimulatedInterruption):
        export_timelapse_streaming(
            session_path,
            resume_dir,
            every_n=2,
            renderer=_renderer,
            renderer_id="s09-test-renderer",
            colors=32,
            delta_bbox=True,
            _stop_after_frames=3,
        )

    checkpoint = json.loads((resume_dir / "checkpoint.json").read_text(encoding="utf-8"))
    committed_offset = checkpoint["gif_byte_offset"]
    with open(resume_dir / "timelapse.tmp.gif", "ab") as handle:
        handle.write(b"CORRUPT-PARTIAL-FRAME-TAIL")
    assert (resume_dir / "timelapse.tmp.gif").stat().st_size > committed_offset

    resumed = export_timelapse_streaming(
        session_path,
        resume_dir,
        every_n=2,
        resume=True,
        renderer=_renderer,
        renderer_id="s09-test-renderer",
        colors=32,
        delta_bbox=True,
    )
    assert resumed.resumed is True
    assert resumed.manifest["export"]["final_frame_matches_session_state"] is True
    assert resumed.manifest["export"]["frame_spool_used"] is False
    assert _decoded_hashes(resumed.gif_path) == _decoded_hashes(uninterrupted.gif_path)
    assert resumed.gif_path.read_bytes() == uninterrupted.gif_path.read_bytes()


def test_resume_contract_rejects_changed_sampling_and_recovers_final_rename(tmp_path: Path):
    session_path = tmp_path / "session.json"
    _session(session_path)
    out = tmp_path / "export"
    result = export_timelapse_streaming(
        session_path,
        out,
        every_n=2,
        renderer=_renderer,
        renderer_id="s09-test-renderer",
        colors=32,
    )
    final_bytes = result.gif_path.read_bytes()

    # Simulate a process/host failure after completed checkpoint + manifest fsync but before
    # the final atomic rename becomes durable/observable.
    os.replace(result.gif_path, out / "timelapse.tmp.gif")
    recovered = export_timelapse_streaming(
        session_path,
        out,
        every_n=2,
        resume=True,
        renderer=_renderer,
        renderer_id="s09-test-renderer",
        colors=32,
    )
    assert recovered.resumed is True
    assert recovered.gif_path.read_bytes() == final_bytes

    with pytest.raises(ResumeMismatchError, match="does not match"):
        export_timelapse_streaming(
            session_path,
            out,
            every_n=3,
            resume=True,
            renderer=_renderer,
            renderer_id="s09-test-renderer",
            colors=32,
        )
