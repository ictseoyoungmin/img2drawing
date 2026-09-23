from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import Iterator, Sequence

from ..core.history import (
    CanvasAction,
    CanvasHistory,
    unsupported_action_error,
    _replay_segment_replace,
    _replay_segment_soft_lift,
    _stroke_from_dict,
)
from ..core.ir import Stroke, StrokeIR


@dataclass
class ForwardReplayStats:
    actions_applied: int = 0
    snapshots_emitted: int = 0
    deep_copies_avoided: int = 0


class ForwardHistoryReplay:
    """Forward-only replay with CanvasHistory.state_at() semantics.

    Emitted snapshots borrow current immutable stroke objects. Edit actions replace
    stroke objects instead of mutating old snapshot objects.
    """

    def __init__(self, history: CanvasHistory):
        self.history = history
        self.width = history.width
        self.height = history.height
        self.metadata = dict(history.metadata)
        self.actions = history.actions
        self.limit = history.cursor
        self.cursor = 0
        self.order: list[str] = []
        self.state: dict[str, Stroke] = {}
        self.stats = ForwardReplayStats()

    def _apply(self, item: CanvasAction) -> None:
        p = item.payload
        action = item.action
        if action == "stroke.add":
            stroke = _stroke_from_dict(p["stroke"], item.tool_state)
            sid = stroke.stroke_id
            if sid is None:
                raise ValueError("history stroke.add missing stroke_id")
            if sid not in self.state:
                self.order.append(sid)
            self.state[sid] = stroke
        elif action == "stroke.replace":
            old_sid = str(p["stroke_id"])
            stroke = _stroke_from_dict(p["stroke"], item.tool_state)
            sid = stroke.stroke_id
            if sid is None:
                raise ValueError("history stroke.replace missing replacement stroke_id")
            self.state.pop(old_sid, None)
            if sid not in self.state:
                try:
                    idx = self.order.index(old_sid)
                    self.order[idx] = sid
                except ValueError:
                    self.order.append(sid)
            self.state[sid] = stroke
        elif action == "stroke.segment_replace":
            sid = str(p["stroke_id"])
            if sid in self.state:
                self.state[sid] = _replay_segment_replace(self.state[sid], item)
        elif action == "stroke.soft_lift":
            sid = str(p["stroke_id"])
            if sid in self.state:
                stroke = deepcopy(self.state[sid])
                stroke.opacity = max(0.0, min(1.0, stroke.opacity * (1.0 - float(p["strength"]))))
                self.state[sid] = stroke
        elif action == "stroke.segment_soft_lift":
            sid = str(p["stroke_id"])
            if sid in self.state:
                self.state[sid] = _replay_segment_soft_lift(self.state[sid], item)
        elif action == "stroke.delete":
            self.state.pop(str(p["stroke_id"]), None)
        elif action == "snapshot":
            pass
        else:
            raise unsupported_action_error(action)
        self.stats.actions_applied += 1

    def advance_to(self, cursor: int) -> None:
        target = max(0, min(int(cursor), self.limit))
        if target < self.cursor:
            raise ValueError("ForwardHistoryReplay cannot seek backward")
        while self.cursor < target:
            self._apply(self.actions[self.cursor])
            self.cursor += 1

    def snapshot(self) -> StrokeIR:
        ir = StrokeIR(self.width, self.height, metadata={**self.metadata, "history_cursor": self.cursor})
        if getattr(self.history, "_legacy_inline_pressure", False):
            setattr(ir, "_legacy_inline_pressure", True)
        ir.strokes = [self.state[sid] for sid in self.order if sid in self.state]
        self.stats.snapshots_emitted += 1
        self.stats.deep_copies_avoided += len(ir.strokes)
        return ir

    def state_at(self, cursor: int) -> StrokeIR:
        self.advance_to(cursor)
        return self.snapshot()

    def iter_cursors(self, cursors: Sequence[int]) -> Iterator[tuple[int, StrokeIR]]:
        for cursor in cursors:
            self.advance_to(int(cursor))
            yield self.cursor, self.snapshot()
