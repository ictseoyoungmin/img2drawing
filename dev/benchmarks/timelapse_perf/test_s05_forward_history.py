from __future__ import annotations

import pytest

from img2drawing.core.history import CanvasHistory
from img2drawing.core.ir import Stroke
from img2drawing.core.tools import form_pencil, hard_eraser

from forward_history_replay import ForwardHistoryReplay


def _stroke(x: float) -> Stroke:
    return Stroke(
        points=[(x, 1.0), (x + 3.0, 4.0)],
        tool_state=form_pencil().to_dict(),
        width=form_pencil().width,
        opacity=form_pencil().opacity,
        stage="bench",
    )


def test_forward_history_matches_state_at_for_add_replace_delete_soft_lift() -> None:
    history = CanvasHistory(64, 64)
    s1 = history.add_stroke(_stroke(1.0))
    s2 = history.add_stroke(_stroke(10.0))
    history.replace_stroke(s1, _stroke(2.0))
    history.soft_lift(s2, hard_eraser(), strength=0.25)
    history.hard_delete(s2, hard_eraser())

    replay = ForwardHistoryReplay(history)
    for cursor in range(history.cursor + 1):
        replay.advance_to(cursor)
        assert replay.snapshot().to_dict() == history.state_at(cursor).to_dict()


def test_forward_history_rejects_backward_seek() -> None:
    history = CanvasHistory(64, 64)
    history.add_stroke(_stroke(1.0))
    replay = ForwardHistoryReplay(history)
    replay.advance_to(1)
    with pytest.raises(ValueError, match="cannot seek backward"):
        replay.advance_to(0)
