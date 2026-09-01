from __future__ import annotations

from inspect import signature
from pathlib import Path
from types import SimpleNamespace

import pytest

from img2drawing.legacy.r23 import DrawingRun
from img2drawing.core.session import DrawingSession, RENDERER_ID
from img2drawing.provenance import timelapse
from img2drawing.provenance.timelapse import select_cursors


def _session(cursor: int):
    actions = [SimpleNamespace(action="stroke.add", payload={}) for _ in range(cursor)]
    return SimpleNamespace(history=SimpleNamespace(cursor=cursor, actions=actions))


def test_every_n_sampling_keeps_first_and_final_action_cursors():
    assert select_cursors(_session(10), "every_n", every_n=4) == [0, 4, 8, 10]


def test_finish_defaults_to_dense_every_four_action_timelapse():
    params = signature(DrawingRun.finish).parameters
    assert params["timelapse_mode"].default == "every_n"
    assert params["timelapse_every_n"].default == 4


def test_timelapse_default_is_pencil_contact_renderer():
    assert timelapse.pencil_render.__module__ == "img2drawing.render.pillow_pencil_contact"


def test_new_sessions_declare_pencil_contact_renderer():
    session = DrawingSession.create("renderer-policy", 32, 32)
    assert session.to_dict()["renderer"]["id"] == RENDERER_ID
    assert RENDERER_ID == "pillow-pencil-contact-v9"


def test_production_modules_do_not_import_legacy_ballpoint_renderer():
    src = Path(__file__).resolve().parents[2] / "skills" / "img2drawing" / "src" / "img2drawing"
    offenders = []
    for path in src.rglob("*.py"):
        if path == src / "render" / "pillow.py":
            continue
        text = path.read_text(encoding="utf-8")
        if "render.pillow import" in text or "render import pillow" in text:
            offenders.append(str(path.relative_to(src)))
    assert offenders == []
    for removed in ("pillow.py", "pillow_subpixel.py", "cairo.py", "svg.py"):
        assert not (src / "render" / removed).exists()


def test_legacy_renderer_session_is_rejected():
    data = DrawingSession.create("legacy-renderer", 32, 32).to_dict()
    data["renderer"]["id"] = "pillow-pressure-v1"
    with pytest.raises(ValueError, match="renderer version mismatch"):
        DrawingSession.from_dict(data, verify=True)
