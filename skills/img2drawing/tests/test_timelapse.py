from __future__ import annotations

from inspect import signature
from types import SimpleNamespace

from img2drawing import DrawingRun
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

