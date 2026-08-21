from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Any, Iterable

from .history import CanvasHistory
from .ir import Stroke, StrokeIR
from ..render.presets import get_pencil_preset
from .stroke import tool_stroke
from .tools import ToolState, get_tool


DRAW_KINDS = {
    "draw_stroke", "replace_stroke", "soft_lift", "delete_stroke", "marker",
    "replace_segment", "soft_lift_segment",
}
TOOL_OVERRIDE_FIELDS = {
    "width", "pressure", "opacity", "hardness", "grain", "taper_in", "taper_out", "jitter",
    "erase_strength",
}


def sha256_file(path: str | Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


@dataclass(frozen=True)
class DrawingAction:
    action_id: str
    kind: str
    stage: str
    role: str | None = None
    part: str | None = None
    points: tuple[tuple[float, float], ...] = ()
    target_stroke_id: str | None = None
    stroke_id: str | None = None
    confidence: float = 1.0
    layer: int = 0
    tool: dict[str, Any] | None = None
    pressure: tuple[float, ...] | None = None
    observation_id: str | None = None
    source_observation: str | None = None
    reason: str | None = None
    revision_of: str | None = None
    metadata: dict[str, Any] | None = None
    segment_start: int | None = None
    segment_end: int | None = None
    lock_boundaries: bool = True
    feather_points: int = 1
    strength: float | None = None

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "DrawingAction":
        kind = str(raw.get("kind", ""))
        if kind not in DRAW_KINDS:
            raise ValueError(f"unknown drawing action kind: {kind!r}")
        action_id = str(raw.get("action_id", "")).strip()
        if not action_id:
            raise ValueError("drawing action requires non-empty action_id")
        stage = str(raw.get("stage", "unspecified"))
        pts = tuple((float(p[0]), float(p[1])) for p in raw.get("points", ()))
        pressure_raw = raw.get("pressure")
        pressure = None if pressure_raw is None else tuple(float(v) for v in pressure_raw)
        confidence = float(raw.get("confidence", 1.0))
        if not 0.0 <= confidence <= 1.0:
            raise ValueError("action confidence must be in [0,1]")
        action = cls(
            action_id=action_id,
            kind=kind,
            stage=stage,
            role=raw.get("role"),
            part=raw.get("part"),
            points=pts,
            target_stroke_id=raw.get("target_stroke_id"),
            stroke_id=raw.get("stroke_id"),
            confidence=confidence,
            layer=int(raw.get("layer", 0)),
            tool=deepcopy(raw.get("tool")),
            pressure=pressure,
            observation_id=raw.get("observation_id"),
            source_observation=raw.get("source_observation"),
            reason=raw.get("reason"),
            revision_of=raw.get("revision_of"),
            metadata=deepcopy(raw.get("metadata")),
            segment_start=None if raw.get("segment_start") is None else int(raw.get("segment_start")),
            segment_end=None if raw.get("segment_end") is None else int(raw.get("segment_end")),
            lock_boundaries=bool(raw.get("lock_boundaries", True)),
            feather_points=int(raw.get("feather_points", 1)),
            strength=None if raw.get("strength") is None else float(raw.get("strength")),
        )
        action.validate()
        return action

    def validate(self) -> None:
        if self.kind in {"draw_stroke", "replace_stroke"}:
            if len(self.points) < 2:
                raise ValueError(f"{self.kind} requires at least 2 points")
            if not self.role:
                raise ValueError(f"{self.kind} requires role")
            if not isinstance(self.tool, dict):
                raise ValueError(f"{self.kind} requires explicit tool selection")
            if not str(self.tool.get("preset", "")).strip():
                raise ValueError(f"{self.kind} tool requires preset")
            if not str(self.tool.get("grade", "")).strip():
                raise ValueError(f"{self.kind} tool requires named pencil grade")
            get_pencil_preset(str(self.tool["grade"]))
            if not self.observation_id or not self.source_observation:
                raise ValueError(f"{self.kind} requires observation_id and source_observation provenance")
            if self.kind == "replace_stroke":
                if not self.target_stroke_id:
                    raise ValueError("replace_stroke requires target_stroke_id")
                if not self.reason:
                    raise ValueError("replace_stroke requires correction reason")
                if self.revision_of != self.target_stroke_id:
                    raise ValueError("replace_stroke revision_of must match target_stroke_id")
        elif self.kind == "replace_segment":
            if not self.target_stroke_id:
                raise ValueError("replace_segment requires target_stroke_id")
            if self.stroke_id is not None and self.stroke_id != self.target_stroke_id:
                raise ValueError("replace_segment preserves stroke identity; stroke_id cannot change")
            if self.role is not None or self.part is not None:
                raise ValueError("replace_segment preserves existing role/part; overrides are not allowed")
            if self.segment_start is None or self.segment_end is None:
                raise ValueError("replace_segment requires segment_start and segment_end")
            if int(self.segment_start) < 0 or int(self.segment_end) <= int(self.segment_start):
                raise ValueError("replace_segment requires a valid increasing point range")
            if len(self.points) < 2:
                raise ValueError("replace_segment requires at least 2 replacement points")
            if self.tool is not None:
                raise ValueError("replace_segment preserves the existing stroke material; tool override is not allowed")
            if not self.observation_id or not self.source_observation or not self.reason:
                raise ValueError("replace_segment requires observation and correction provenance")
            if self.revision_of != self.target_stroke_id:
                raise ValueError("replace_segment revision_of must match target_stroke_id")
        elif self.kind == "soft_lift_segment":
            if not self.target_stroke_id:
                raise ValueError("soft_lift_segment requires target_stroke_id")
            if self.points:
                raise ValueError("soft_lift_segment does not accept geometry points")
            if self.stroke_id is not None or self.role is not None or self.part is not None:
                raise ValueError("soft_lift_segment preserves stroke identity and semantics")
            if self.segment_start is None or self.segment_end is None:
                raise ValueError("soft_lift_segment requires segment_start and segment_end")
            if int(self.segment_start) < 0 or int(self.segment_end) <= int(self.segment_start):
                raise ValueError("soft_lift_segment requires a valid increasing point range")
            if not isinstance(self.tool, dict) or not str(self.tool.get("preset", "")).strip():
                raise ValueError("soft_lift_segment requires explicit eraser tool preset")
            if self.strength is not None and not 0.0 <= float(self.strength) <= 1.0:
                raise ValueError("soft_lift_segment strength must be in [0,1]")
            if int(self.feather_points) < 0:
                raise ValueError("soft_lift_segment feather_points must be >= 0")
            if not self.observation_id or not self.source_observation or not self.reason:
                raise ValueError("soft_lift_segment requires observation and correction provenance")
            if self.revision_of != self.target_stroke_id:
                raise ValueError("soft_lift_segment revision_of must match target_stroke_id")
        elif self.kind in {"soft_lift", "delete_stroke"}:
            if not self.target_stroke_id:
                raise ValueError(f"{self.kind} requires target_stroke_id")
            if not isinstance(self.tool, dict) or not str(self.tool.get("preset", "")).strip():
                raise ValueError(f"{self.kind} requires explicit eraser tool preset")
        if self.pressure is not None and len(self.pressure) != len(self.points):
            raise ValueError("explicit pressure sample count must match points")

    def provenance(self) -> dict[str, Any]:
        out = {
            "action_id": self.action_id,
            "observation_id": self.observation_id,
            "source_observation": self.source_observation,
            "reason": self.reason,
            "revision_of": self.revision_of,
        }
        if self.segment_start is not None:
            out["segment_start"] = int(self.segment_start)
        if self.segment_end is not None:
            out["segment_end"] = int(self.segment_end)
        if self.metadata:
            out["metadata"] = deepcopy(self.metadata)
        return {k: v for k, v in out.items() if v is not None}


def _resolve_tool(raw: dict[str, Any]) -> tuple[ToolState, str | None]:
    preset = str(raw["preset"])
    tool = get_tool(preset)
    overrides = raw.get("overrides") or {}
    unknown = set(overrides) - TOOL_OVERRIDE_FIELDS
    if unknown:
        raise ValueError(f"unsupported tool overrides: {sorted(unknown)}")
    if overrides:
        values = {name: float(value) for name, value in overrides.items()}
        tool = replace(tool, **values).validated()
    grade = raw.get("grade")
    if grade is not None:
        grade = get_pencil_preset(str(grade)).name
    return tool, grade


def _stroke_from_action(action: DrawingAction) -> Stroke:
    assert action.tool is not None
    tool, grade = _resolve_tool(action.tool)
    if tool.mode != "draw":
        raise ValueError(f"draw action cannot use erase-mode tool: {tool.tool}")
    stroke = tool_stroke(
        action.points,
        tool,
        pressure=None if action.pressure is None else list(action.pressure),
        role=str(action.role),
        part=action.part,
        stage=action.stage,
        layer=action.layer,
    )
    stroke.confidence = action.confidence
    stroke.stroke_id = action.stroke_id
    ts = deepcopy(stroke.tool_state) if isinstance(stroke.tool_state, dict) else {}
    ts["pencil_grade"] = grade
    ts["action_id"] = action.action_id
    ts["provenance"] = action.provenance()
    stroke.tool_state = ts
    return stroke.cleaned()


class _DrawingTransaction:
    """Atomic action-history transaction with exact rollback on failure or rejection."""

    def __init__(self, session: "AgentDrawingSession", *, label: str | None = None):
        self.session = session
        self.label = None if label is None else str(label)
        self._history_snapshot = deepcopy(session.history.to_dict())
        self._executed_snapshot = set(session.executed_action_ids)
        self._rolled_back = False
        self._committed = False

    @property
    def rolled_back(self) -> bool:
        return self._rolled_back

    @property
    def committed(self) -> bool:
        return self._committed

    def _restore(self) -> None:
        self.session.history = CanvasHistory.from_dict(deepcopy(self._history_snapshot))
        self.session.executed_action_ids = set(self._executed_snapshot)
        self._rolled_back = True
        self._committed = False

    def rollback(self) -> None:
        if self._committed:
            raise RuntimeError("cannot rollback an already committed transaction")
        if not self._rolled_back:
            self._restore()

    def commit(self) -> None:
        if self._rolled_back:
            raise RuntimeError("cannot commit a rolled-back transaction")
        self._committed = True

    def __enter__(self) -> "_DrawingTransaction":
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        # Any exception wins over an earlier explicit commit: atomicity is stronger than
        # convenience, so a failing transaction can never leave a partial accepted edit.
        if exc_type is not None:
            if not self._rolled_back:
                self._restore()
            return False
        if not self._rolled_back and not self._committed:
            self.commit()
        return False


class AgentDrawingSession:
    """Authoritative action-driven drawing session.

    This class never looks at image pixels and never derives edges, contours or hatches.
    Every mark must arrive as an explicit agent-authored DrawingAction. CanvasHistory is
    the sole drawing-state authority; presentation runtimes consume snapshots from it.
    """

    def __init__(self, width: int, height: int, *, metadata: dict[str, Any] | None = None):
        self.history = CanvasHistory(width, height, metadata={**(metadata or {}), "drawing_authority": "agent_actions"})
        self.executed_action_ids: set[str] = set()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AgentDrawingSession":
        if data.get("schema") != "img2drawing.agent_drawing_session.v1":
            raise ValueError(f"unsupported agent drawing session schema: {data.get('schema')!r}")
        history=CanvasHistory.from_dict(deepcopy(data["history"]))
        obj=cls(history.width,history.height,metadata=deepcopy(history.metadata))
        obj.history=history
        obj.executed_action_ids=set(map(str,data.get("executed_action_ids",())))
        return obj

    @property
    def width(self) -> int:
        return self.history.width

    @property
    def height(self) -> int:
        return self.history.height

    def execute(self, action: DrawingAction | dict[str, Any]) -> str | None:
        if not isinstance(action, DrawingAction):
            action = DrawingAction.from_dict(action)
        if action.action_id in self.executed_action_ids:
            raise ValueError(f"duplicate action_id: {action.action_id}")
        for x, y in action.points:
            if not (0.0 <= float(x) <= self.width - 1 and 0.0 <= float(y) <= self.height - 1):
                raise ValueError(f"drawing action point out of canvas bounds: {(x, y)}")
        result: str | None = None
        provenance = action.provenance()
        if action.kind == "draw_stroke":
            stroke = _stroke_from_action(action)
            result = self.history.add_stroke(stroke, stroke_id=action.stroke_id, provenance=provenance)
        elif action.kind == "replace_stroke":
            stroke = _stroke_from_action(action)
            result = self.history.replace_stroke(
                str(action.target_stroke_id), stroke, new_stroke_id=action.stroke_id, provenance=provenance
            )
        elif action.kind == "replace_segment":
            result = self.history.replace_segment(
                str(action.target_stroke_id), int(action.segment_start), int(action.segment_end),
                action.points, pressure=None if action.pressure is None else action.pressure,
                lock_boundaries=bool(action.lock_boundaries), stage=action.stage, provenance=provenance,
            )
        elif action.kind == "soft_lift_segment":
            assert action.tool is not None
            eraser, _ = _resolve_tool(action.tool)
            if eraser.mode != "erase":
                raise ValueError("soft_lift_segment requires erase-mode tool")
            result = self.history.soft_lift_segment(
                str(action.target_stroke_id), int(action.segment_start), int(action.segment_end), eraser,
                strength=action.strength, feather_points=int(action.feather_points),
                stage=action.stage, provenance=provenance,
            )
        elif action.kind == "soft_lift":
            assert action.tool is not None
            eraser, _ = _resolve_tool(action.tool)
            if eraser.mode != "erase":
                raise ValueError("soft_lift requires erase-mode tool")
            strength = None
            if action.metadata and "strength" in action.metadata:
                strength = float(action.metadata["strength"])
            self.history.soft_lift(str(action.target_stroke_id), eraser, strength=strength, stage=action.stage, provenance=provenance)
        elif action.kind == "delete_stroke":
            assert action.tool is not None
            eraser, _ = _resolve_tool(action.tool)
            if eraser.mode != "erase":
                raise ValueError("delete_stroke requires erase-mode tool")
            self.history.hard_delete(str(action.target_stroke_id), eraser, stage=action.stage, provenance=provenance)
        elif action.kind == "marker":
            self.history.marker(action.reason or action.action_id, stage=action.stage, provenance=provenance)
        self.executed_action_ids.add(action.action_id)
        return result

    def to_drawing_session(self, *, session_id: str = "img2drawing-run", metadata: dict[str, Any] | None = None):
        """Return the supported persisted-session bridge for replay/timelapse export."""
        from .session import DrawingSession
        return DrawingSession.from_agent_session(self, session_id=session_id, metadata=metadata)

    def transaction(self, label: str | None = None):
        return _DrawingTransaction(self, label=label)

    def execute_many(self, actions: Iterable[DrawingAction | dict[str, Any]]) -> list[str | None]:
        return [self.execute(a) for a in actions]

    def execute_many_atomic(
        self, actions: Iterable[DrawingAction | dict[str, Any]], *, label: str | None = None
    ) -> list[str | None]:
        with self.transaction(label=label):
            return self.execute_many(actions)

    def current_ir(self) -> StrokeIR:
        return self.history.state_at()

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "img2drawing.agent_drawing_session.v1",
            "history": self.history.to_dict(),
            "executed_action_ids": sorted(self.executed_action_ids),
        }


def load_drawing_plan(plan: str | Path | dict[str, Any], *, expected_width: int | None = None,
                      expected_height: int | None = None, source_path: str | Path | None = None) -> dict[str, Any]:
    if isinstance(plan, (str, Path)):
        payload = json.loads(Path(plan).read_text(encoding="utf-8"))
    else:
        payload = deepcopy(plan)
    if payload.get("schema") not in {None, "img2drawing.drawing_plan.v1"}:
        raise ValueError(f"unsupported drawing plan schema: {payload.get('schema')!r}")
    canvas = payload.get("canvas") or {}
    if expected_width is not None and int(canvas.get("width", -1)) != int(expected_width):
        raise ValueError("drawing plan width does not match source")
    if expected_height is not None and int(canvas.get("height", -1)) != int(expected_height):
        raise ValueError("drawing plan height does not match source")
    if source_path is not None:
        expected_hash = (payload.get("source") or {}).get("sha256")
        if expected_hash and str(expected_hash).lower() != sha256_file(source_path).lower():
            raise ValueError("drawing plan source sha256 does not match input")
    actions = payload.get("actions")
    if not isinstance(actions, list) or not actions:
        raise ValueError("drawing plan requires non-empty actions")
    ids: set[str] = set()
    for raw in actions:
        a = DrawingAction.from_dict(raw)
        if a.action_id in ids:
            raise ValueError(f"duplicate action_id in plan: {a.action_id}")
        ids.add(a.action_id)
    return payload


def build_agent_drawing_ir(width: int, height: int, plan: str | Path | dict[str, Any], *,
                           source_path: str | Path | None = None) -> tuple[StrokeIR, AgentDrawingSession]:
    payload = load_drawing_plan(plan, expected_width=width, expected_height=height, source_path=source_path)
    session = AgentDrawingSession(width, height, metadata={
        "mode": "pencil",
        "plan_schema": "img2drawing.drawing_plan.v1",
        "source": deepcopy(payload.get("source") or {}),
        "paper": deepcopy(payload.get("paper") or {}),
    })
    session.execute_many(payload["actions"])
    return session.current_ir(), session
