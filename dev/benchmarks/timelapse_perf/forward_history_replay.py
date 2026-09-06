from __future__ import annotations

"""S05 dev prototype: forward-only authoritative history traversal.

This mirrors CanvasHistory.state_at() semantics but applies each action exactly once.
Snapshots borrow immutable stroke objects from the replay state instead of deep-copying
the whole active drawing at every sampled cursor. The cursor is monotone; backward
seek intentionally fails closed in this prototype.
"""

from copy import deepcopy
from dataclasses import dataclass
from typing import Iterable

from img2drawing.core.fill import FillRegion
from img2drawing.core.history import (
    CanvasHistory,
    _fill_strokes,
    _replay_segment_replace,
    _replay_segment_soft_lift,
    _stroke_from_dict,
)
from img2drawing.core.ir import Stroke, StrokeIR


@dataclass(frozen=True)
class ForwardReplayStats:
    actions_applied: int
    snapshots: int
    cursor: int


class ForwardHistoryReplay:
    """Forward-only replay cursor with exact CanvasHistory ordering semantics."""

    def __init__(self, history: CanvasHistory) -> None:
        self.history = history
        self.cursor = 0
        self.order: list[str] = []
        self.state: dict[str, Stroke] = {}
        self.fill_members: dict[str, set[str]] = {}
        self._snapshots = 0
        self._legacy_inline_pressure = bool(getattr(history, "_legacy_inline_pressure", False))

    def _apply(self, item) -> None:
        p = item.payload
        if item.action == "stroke.add":
            stroke = _stroke_from_dict(p["stroke"], item.tool_state)
            sid = stroke.stroke_id
            if sid is None:
                raise ValueError("history stroke.add missing stroke_id")
            if sid not in self.state:
                self.order.append(sid)
            self.state[sid] = stroke
        elif item.action == "stroke.replace":
            old_sid = p["stroke_id"]
            stroke = _stroke_from_dict(p["stroke"], item.tool_state)
            sid = stroke.stroke_id
            if sid is None:
                raise ValueError("history stroke.replace missing replacement stroke_id")
            if old_sid in self.state:
                self.state.pop(old_sid, None)
            if sid not in self.state:
                try:
                    index = self.order.index(old_sid)
                    self.order[index] = sid
                except ValueError:
                    self.order.append(sid)
            self.state[sid] = stroke
        elif item.action == "stroke.segment_replace":
            sid = str(p["stroke_id"])
            if sid in self.state:
                self.state[sid] = _replay_segment_replace(self.state[sid], item)
        elif item.action == "stroke.soft_lift":
            sid = p["stroke_id"]
            if sid in self.state:
                stroke = deepcopy(self.state[sid])
                stroke.opacity = max(0.0, min(1.0, stroke.opacity * (1.0 - float(p["strength"]))))
                self.state[sid] = stroke
        elif item.action == "stroke.segment_soft_lift":
            sid = str(p["stroke_id"])
            if sid in self.state:
                self.state[sid] = _replay_segment_soft_lift(self.state[sid], item)
        elif item.action == "stroke.delete":
            self.state.pop(p["stroke_id"], None)
        elif item.action == "region.fill":
            region = FillRegion.from_dict(p["region"])
            members: set[str] = set()
            for stroke in _fill_strokes(region, item):
                sid = str(stroke.stroke_id)
                members.add(sid)
                if sid not in self.state:
                    self.order.append(sid)
                self.state[sid] = stroke
            self.fill_members[region.fill_id] = members
        elif item.action == "region.replace":
            region = FillRegion.from_dict(p["region"])
            target = str(p.get("fill_id") or region.fill_id)
            if region.fill_id != target:
                raise ValueError("region.replace fill identity mismatch")
            previous_members = self.fill_members.get(target, set())
            prior_positions = [i for i, sid in enumerate(self.order) if sid in previous_members]
            insert_at = min(prior_positions) if prior_positions else len(self.order)
            for sid in previous_members:
                self.state.pop(sid, None)
            if previous_members:
                self.order = [sid for sid in self.order if sid not in previous_members]
            replacement_strokes = _fill_strokes(region, item)
            members: set[str] = set()
            for offset, stroke in enumerate(replacement_strokes):
                sid = str(stroke.stroke_id)
                members.add(sid)
                if sid in self.order:
                    self.order.remove(sid)
                self.order.insert(min(insert_at + offset, len(self.order)), sid)
                self.state[sid] = stroke
            self.fill_members[target] = members
        elif item.action == "snapshot":
            pass
        else:
            raise ValueError(f"unsupported replay action: {item.action}")

    def advance_to(self, cursor: int) -> int:
        target = max(0, min(int(cursor), self.history.cursor))
        if target < self.cursor:
            raise ValueError("ForwardHistoryReplay cannot seek backward")
        for item in self.history.actions[self.cursor:target]:
            self._apply(item)
        applied = target - self.cursor
        self.cursor = target
        return applied

    def snapshot(self, *, copy_strokes: bool = False) -> StrokeIR:
        strokes = [self.state[sid] for sid in self.order if sid in self.state]
        if copy_strokes:
            strokes = deepcopy(strokes)
        ir = StrokeIR(
            self.history.width,
            self.history.height,
            strokes=strokes,
            metadata={**self.history.metadata, "history_cursor": self.cursor},
        )
        if self._legacy_inline_pressure:
            setattr(ir, "_legacy_inline_pressure", True)
        self._snapshots += 1
        return ir

    def snapshots(self, cursors: Iterable[int], *, copy_strokes: bool = False):
        for cursor in cursors:
            self.advance_to(int(cursor))
            yield self.snapshot(copy_strokes=copy_strokes)

    @property
    def stats(self) -> ForwardReplayStats:
        return ForwardReplayStats(
            actions_applied=self.cursor,
            snapshots=self._snapshots,
            cursor=self.cursor,
        )
