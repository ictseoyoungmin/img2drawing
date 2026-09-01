from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, dataclass
from typing import Any, Sequence

from .fill import FillRegion, expand_fill
from .ir import Stroke, StrokeIR
from .stroke import shaped_pressure_profile
from .tools import ToolState


def _json_native(value):
    if isinstance(value, tuple):
        return [_json_native(v) for v in value]
    if isinstance(value, list):
        return [_json_native(v) for v in value]
    if isinstance(value, dict):
        return {str(k): _json_native(v) for k, v in value.items()}
    return value


@dataclass
class CanvasAction:
    seq: int
    action: str
    stage: str
    payload: dict[str, Any]
    logical_time: float | None = None
    part: str | None = None
    role: str | None = None
    tool_state: dict[str, Any] | None = None
    provenance: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        # Backward-compatible action hashing: legacy sessions did not have provenance.
        if data.get("provenance") is None:
            data.pop("provenance", None)
        return _json_native(data)


def _persisted_stroke(stroke: Stroke) -> dict[str, Any]:
    """Serialize a stroke without the parts that are recomputed on load.

    Two things are deliberately absent. A derived pressure curve is a pure
    function of the point count and the tool taper, so persisting it stores the
    renderer's arithmetic as if it were an authored decision. And ``tool_state``
    lives once on the action record; repeating it inside the payload doubled the
    largest field in the file.
    """
    data = asdict(stroke)
    if not data.pop("pressure_authored", False):
        data["pressure"] = None
    data.pop("tool_state", None)
    return data


def _derive_pressure(tool_state: dict[str, Any] | None, n: int) -> list[float] | None:
    if not isinstance(tool_state, dict) or n <= 0:
        return None
    try:
        pressure = float(tool_state["pressure"])
        taper_in = float(tool_state.get("taper_in", 0.0))
        taper_out = float(tool_state.get("taper_out", 0.0))
    except (KeyError, TypeError, ValueError):
        return None
    return shaped_pressure_profile(
        n,
        start=max(0.05, pressure * (0.25 + 0.20 * (1.0 - taper_in))),
        peak=min(1.0, pressure * 1.18),
        end=max(0.04, pressure * (0.20 + 0.20 * (1.0 - taper_out))),
    )


def _stroke_from_dict(data: dict[str, Any], tool_state: dict[str, Any] | None = None) -> Stroke:
    d = deepcopy(data)
    d["points"] = [tuple(map(float, p)) for p in d.get("points", [])]
    if d.get("tool_state") is None and tool_state is not None:
        d["tool_state"] = deepcopy(tool_state)
    if d.get("pressure") is not None:
        # An older session, or an explicitly authored curve: keep exactly what it stored.
        d["pressure"] = [float(v) for v in d["pressure"]]
        d.setdefault("pressure_authored", True)
    else:
        d["pressure"] = _derive_pressure(d.get("tool_state"), len(d["points"]))
        d["pressure_authored"] = False
    return Stroke(**d)


def _segment_bounds(stroke: Stroke, start_index: int, end_index: int) -> tuple[int, int]:
    start = int(start_index)
    end = int(end_index)
    if start < 0 or end < 0 or start >= end or end >= len(stroke.points):
        raise ValueError(
            f"invalid stroke segment point range [{start}, {end}] for {len(stroke.points)} points"
        )
    return start, end


def _append_local_edit(stroke: Stroke, *, kind: str, action: CanvasAction) -> None:
    ts = deepcopy(stroke.tool_state) if isinstance(stroke.tool_state, dict) else {}
    edits = list(ts.get("local_edits") or [])
    record: dict[str, Any] = {
        "kind": kind,
        "seq": int(action.seq),
    }
    if action.provenance:
        record.update(deepcopy(action.provenance))
    p = action.payload
    if "start_index" in p:
        record["start_index"] = int(p["start_index"])
    if "end_index" in p:
        record["end_index"] = int(p["end_index"])
    if "strength" in p:
        record["strength"] = float(p["strength"])
    edits.append(record)
    ts["local_edits"] = edits
    stroke.tool_state = ts


def _replay_segment_replace(stroke: Stroke, action: CanvasAction) -> Stroke:
    p = action.payload
    out = deepcopy(stroke)
    start, end = _segment_bounds(out, p["start_index"], p["end_index"])
    replacement = [tuple(map(float, q)) for q in p.get("points", [])]
    if len(replacement) < 2:
        raise ValueError("segment replacement requires at least two points")
    if bool(p.get("lock_boundaries", True)):
        replacement[0] = tuple(map(float, out.points[start]))
        replacement[-1] = tuple(map(float, out.points[end]))

    original_pressure = out.pressure
    replacement_pressure = p.get("pressure")
    if original_pressure is None:
        if replacement_pressure is not None:
            raise ValueError("cannot introduce local pressure into a pressure-less stroke")
        new_pressure = None
    else:
        if len(original_pressure) != len(out.points):
            raise ValueError("stroke pressure must align with points for local segment edit")
        if replacement_pressure is None:
            p0, p1 = float(original_pressure[start]), float(original_pressure[end])
            if len(replacement) == 2:
                repl_pressure = [p0, p1]
            else:
                repl_pressure = [p0 + (p1 - p0) * (i / (len(replacement) - 1)) for i in range(len(replacement))]
        else:
            repl_pressure = [float(v) for v in replacement_pressure]
            if len(repl_pressure) != len(replacement):
                raise ValueError("segment replacement pressure count must match replacement points")
        new_pressure = list(map(float, original_pressure[:start])) + repl_pressure + list(map(float, original_pressure[end + 1 :]))

    out.points = list(map(lambda q: (float(q[0]), float(q[1])), out.points[:start])) + replacement + list(
        map(lambda q: (float(q[0]), float(q[1])), out.points[end + 1 :])
    )
    out.pressure = new_pressure
    _append_local_edit(out, kind="segment_replace", action=action)
    return out.cleaned()


def _replay_segment_soft_lift(stroke: Stroke, action: CanvasAction) -> Stroke:
    p = action.payload
    out = deepcopy(stroke)
    start, end = _segment_bounds(out, p["start_index"], p["end_index"])
    if out.pressure is None or len(out.pressure) != len(out.points):
        raise ValueError("segment soft lift requires explicit point-aligned pressure")
    strength = float(p["strength"])
    if not 0.0 <= strength <= 1.0:
        raise ValueError("erase strength must be in [0,1]")
    feather = max(0, int(p.get("feather_points", 0)))
    pressure = [float(v) for v in out.pressure]

    # Full attenuation inside the selected range; deterministic linear feather outside it.
    weights: dict[int, float] = {i: 1.0 for i in range(start, end + 1)}
    for k in range(1, feather + 1):
        weight = (feather - k + 1) / (feather + 1)
        left = start - k
        right = end + k
        if left >= 0:
            weights[left] = max(weights.get(left, 0.0), weight)
        if right < len(pressure):
            weights[right] = max(weights.get(right, 0.0), weight)
    for i, weight in weights.items():
        pressure[i] = max(0.0, min(1.0, pressure[i] * (1.0 - strength * weight)))
    out.pressure = pressure
    _append_local_edit(out, kind="segment_soft_lift", action=action)
    return out.cleaned()


def _fill_strokes(region: FillRegion, action: CanvasAction) -> list[Stroke]:
    """Expand one authored region into deterministic rendered pencil strokes."""

    base = action.tool_state or {}
    strokes: list[Stroke] = []
    for line in expand_fill(region):
        sid = line["stroke_id"]
        ts = deepcopy(base)
        attenuation = float(line["attenuation"])
        stroke = Stroke(
            points=[tuple(map(float, q)) for q in line["points"]],
            width=float(ts.get("width", 1.5)),
            opacity=float(ts.get("opacity", 1.0)) * attenuation,
            role=region.role,
            layer=region.layer,
            tool_state=ts,
            part=region.part,
            stage=action.stage,
            stroke_id=sid,
        )
        # A fill line is a tone mark, not a gesture: it carries the tool's constant
        # pressure. Deriving a taper here would spend the whole of a two-point line on
        # its own entry and exit and render far too light.
        stroke.pressure = None
        strokes.append(stroke)
    return strokes


class CanvasHistory:
    """Replayable authoritative drawing history.

    C9 adds local segment edits as first-class replay actions while preserving all legacy
    add/replace/erase semantics and action hashes for sessions that do not use C9 actions.
    """

    def __init__(self, width: int, height: int, metadata: dict | None = None):
        self.width = int(width)
        self.height = int(height)
        self.metadata = dict(metadata or {})
        self.actions: list[CanvasAction] = []
        self.cursor = 0
        self._next_id = 1

    def _append(
        self,
        action: str,
        payload: dict[str, Any],
        *,
        stage: str = "unspecified",
        part: str | None = None,
        role: str | None = None,
        tool_state: dict[str, Any] | None = None,
        provenance: dict[str, Any] | None = None,
    ) -> CanvasAction:
        if self.cursor < len(self.actions):
            self.actions = self.actions[: self.cursor]
        seq = len(self.actions) + 1
        item = CanvasAction(
            seq,
            action,
            stage,
            deepcopy(payload),
            float(seq - 1),
            part,
            role,
            deepcopy(tool_state),
            deepcopy(provenance),
        )
        self.actions.append(item)
        self.cursor = len(self.actions)
        return item

    def _current_stroke(self, stroke_id: str) -> Stroke:
        for stroke in self.state_at().strokes:
            if stroke.stroke_id == stroke_id:
                return stroke
        raise ValueError(f"missing stroke: {stroke_id}")

    def current_fill_region(self, fill_id: str) -> FillRegion:
        """Return the latest authored definition for an existing fill identity."""

        requested = str(fill_id).strip()
        if not requested:
            raise ValueError("fill_id must be non-empty")
        for item in reversed(self.actions[: self.cursor]):
            if item.action not in {"region.fill", "region.replace"}:
                continue
            raw = item.payload.get("region")
            if not isinstance(raw, dict):
                continue
            region = FillRegion.from_dict(raw)
            if region.fill_id == requested:
                return region
        raise ValueError(f"missing fill region: {requested}")

    def add_stroke(self, stroke: Stroke, *, stroke_id: str | None = None, provenance: dict[str, Any] | None = None) -> str:
        s = deepcopy(stroke).cleaned()
        sid = stroke_id or s.stroke_id or f"h{self._next_id:04d}"
        self._next_id += 1
        s.stroke_id = sid
        self._append(
            "stroke.add",
            {"stroke": _persisted_stroke(s)},
            stage=s.stage or "unspecified",
            part=s.part,
            role=s.role,
            tool_state=deepcopy(s.tool_state),
            provenance=provenance,
        )
        return sid

    def fill_region(
        self,
        region: FillRegion,
        tool_state: dict[str, Any],
        *,
        stage: str = "value_pass",
        provenance: dict[str, Any] | None = None,
    ) -> str:
        """Record one tone region. The hatch it stands for is expanded on replay."""

        try:
            self.current_fill_region(region.fill_id)
        except ValueError:
            pass
        else:
            raise ValueError(
                f"fill_id already exists: {region.fill_id}; use replace_fill_region() to revise it"
            )
        self._append(
            "region.fill",
            {"region": region.to_dict()},
            stage=stage,
            part=region.part,
            role=region.role,
            tool_state=deepcopy(tool_state),
            provenance=provenance,
        )
        return region.fill_id

    def replace_fill_region(
        self,
        fill_id: str,
        region: FillRegion,
        tool_state: dict[str, Any],
        *,
        stage: str = "value_pass",
        provenance: dict[str, Any] | None = None,
    ) -> str:
        """Append one replacement for an existing tone region, preserving fill identity."""

        current = self.current_fill_region(fill_id)
        if region.fill_id != current.fill_id:
            raise ValueError("replace_fill_region must preserve fill identity")
        self._append(
            "region.replace",
            {"fill_id": current.fill_id, "region": region.to_dict()},
            stage=stage,
            part=region.part,
            role=region.role,
            tool_state=deepcopy(tool_state),
            provenance=provenance,
        )
        return current.fill_id

    def replace_stroke(
        self,
        stroke_id: str,
        replacement: Stroke,
        *,
        new_stroke_id: str | None = None,
        provenance: dict[str, Any] | None = None,
    ) -> str:
        self._current_stroke(stroke_id)
        s = deepcopy(replacement).cleaned()
        sid = new_stroke_id or s.stroke_id or f"h{self._next_id:04d}"
        self._next_id += 1
        s.stroke_id = sid
        self._append(
            "stroke.replace",
            {"stroke_id": stroke_id, "stroke": _persisted_stroke(s)},
            stage=s.stage or "unspecified",
            part=s.part,
            role=s.role,
            tool_state=deepcopy(s.tool_state),
            provenance=provenance,
        )
        return sid

    def replace_segment(
        self,
        stroke_id: str,
        start_index: int,
        end_index: int,
        points: Sequence[tuple[float, float]],
        *,
        pressure: Sequence[float] | None = None,
        lock_boundaries: bool = True,
        stage: str | None = None,
        provenance: dict[str, Any] | None = None,
    ) -> str:
        current = self._current_stroke(stroke_id)
        start, end = _segment_bounds(current, start_index, end_index)
        replacement = [(float(x), float(y)) for x, y in points]
        if len(replacement) < 2:
            raise ValueError("segment replacement requires at least two points")
        replacement_pressure = None if pressure is None else [float(v) for v in pressure]
        if replacement_pressure is not None and len(replacement_pressure) != len(replacement):
            raise ValueError("segment replacement pressure count must match replacement points")
        if current.pressure is None and replacement_pressure is not None:
            raise ValueError("cannot introduce local pressure into a pressure-less stroke")
        payload = {
            "stroke_id": str(stroke_id),
            "start_index": start,
            "end_index": end,
            "points": replacement,
            "pressure": replacement_pressure,
            "lock_boundaries": bool(lock_boundaries),
        }
        # Apply once before recording so invalid splices fail without mutating history.
        probe = CanvasAction(0, "stroke.segment_replace", stage or current.stage or "unspecified", payload, provenance=provenance)
        _replay_segment_replace(current, probe)
        self._append(
            "stroke.segment_replace",
            payload,
            stage=stage or current.stage or "unspecified",
            part=current.part,
            role=current.role,
            tool_state=deepcopy(current.tool_state),
            provenance=provenance,
        )
        return str(stroke_id)

    def soft_lift(self, stroke_id: str, eraser: ToolState, *, strength: float | None = None,
                  stage: str = "A2_eraser_history", provenance: dict[str, Any] | None = None) -> None:
        if eraser.mode != "erase":
            raise ValueError("soft_lift requires an erase-mode tool")
        k = eraser.erase_strength if strength is None else float(strength)
        if not 0.0 <= k <= 1.0:
            raise ValueError("erase strength must be in [0,1]")
        ts = eraser.to_dict()
        self._append(
            "stroke.soft_lift",
            {"stroke_id": stroke_id, "strength": k, "tool_state": ts},
            stage=stage,
            tool_state=ts,
            provenance=provenance,
        )

    def soft_lift_segment(
        self,
        stroke_id: str,
        start_index: int,
        end_index: int,
        eraser: ToolState,
        *,
        strength: float | None = None,
        feather_points: int = 1,
        stage: str = "local_edit",
        provenance: dict[str, Any] | None = None,
    ) -> str:
        if eraser.mode != "erase":
            raise ValueError("soft_lift_segment requires an erase-mode tool")
        current = self._current_stroke(stroke_id)
        start, end = _segment_bounds(current, start_index, end_index)
        if current.pressure is None or len(current.pressure) != len(current.points):
            raise ValueError("segment soft lift requires explicit point-aligned pressure")
        k = eraser.erase_strength if strength is None else float(strength)
        if not 0.0 <= k <= 1.0:
            raise ValueError("erase strength must be in [0,1]")
        feather = int(feather_points)
        if feather < 0:
            raise ValueError("feather_points must be >= 0")
        ts = eraser.to_dict()
        payload = {
            "stroke_id": str(stroke_id),
            "start_index": start,
            "end_index": end,
            "strength": k,
            "feather_points": feather,
            "tool_state": ts,
        }
        probe = CanvasAction(0, "stroke.segment_soft_lift", stage, payload, provenance=provenance)
        _replay_segment_soft_lift(current, probe)
        self._append(
            "stroke.segment_soft_lift",
            payload,
            stage=stage,
            part=current.part,
            role=current.role,
            tool_state=ts,
            provenance=provenance,
        )
        return str(stroke_id)

    def hard_delete(self, stroke_id: str, eraser: ToolState, *, stage: str = "A2_eraser_history",
                    provenance: dict[str, Any] | None = None) -> None:
        if eraser.mode != "erase":
            raise ValueError("hard_delete requires an erase-mode tool")
        ts = eraser.to_dict()
        self._append(
            "stroke.delete",
            {"stroke_id": stroke_id, "tool_state": ts},
            stage=stage,
            tool_state=ts,
            provenance=provenance,
        )

    def marker(self, label: str, *, stage: str = "A3_replay", provenance: dict[str, Any] | None = None) -> None:
        self._append("snapshot", {"label": str(label)}, stage=stage, provenance=provenance)

    def undo(self, steps: int = 1) -> None:
        self.cursor = max(0, self.cursor - max(1, int(steps)))

    def redo(self, steps: int = 1) -> None:
        self.cursor = min(len(self.actions), self.cursor + max(1, int(steps)))

    def state_at(self, cursor: int | None = None) -> StrokeIR:
        limit = self.cursor if cursor is None else max(0, min(int(cursor), len(self.actions)))
        order: list[str] = []
        state: dict[str, Stroke] = {}
        fill_members: dict[str, set[str]] = {}
        for item in self.actions[:limit]:
            p = item.payload
            if item.action == "stroke.add":
                s = _stroke_from_dict(p["stroke"], item.tool_state)
                sid = s.stroke_id
                if sid is None:
                    raise ValueError("history stroke.add missing stroke_id")
                if sid not in state:
                    order.append(sid)
                state[sid] = s
            elif item.action == "stroke.replace":
                old_sid = p["stroke_id"]
                s = _stroke_from_dict(p["stroke"], item.tool_state)
                sid = s.stroke_id
                if sid is None:
                    raise ValueError("history stroke.replace missing replacement stroke_id")
                if old_sid in state:
                    state.pop(old_sid, None)
                if sid not in state:
                    try:
                        idx = order.index(old_sid)
                        order[idx] = sid
                    except ValueError:
                        order.append(sid)
                state[sid] = s
            elif item.action == "stroke.segment_replace":
                sid = str(p["stroke_id"])
                if sid in state:
                    state[sid] = _replay_segment_replace(state[sid], item)
            elif item.action == "stroke.soft_lift":
                sid = p["stroke_id"]
                if sid in state:
                    s = deepcopy(state[sid])
                    s.opacity = max(0.0, min(1.0, s.opacity * (1.0 - float(p["strength"]))))
                    state[sid] = s
            elif item.action == "stroke.segment_soft_lift":
                sid = str(p["stroke_id"])
                if sid in state:
                    state[sid] = _replay_segment_soft_lift(state[sid], item)
            elif item.action == "stroke.delete":
                state.pop(p["stroke_id"], None)
            elif item.action == "region.fill":
                region = FillRegion.from_dict(p["region"])
                members: set[str] = set()
                for stroke in _fill_strokes(region, item):
                    sid = str(stroke.stroke_id)
                    members.add(sid)
                    if sid not in state:
                        order.append(sid)
                    state[sid] = stroke
                fill_members[region.fill_id] = members
            elif item.action == "region.replace":
                region = FillRegion.from_dict(p["region"])
                target = str(p.get("fill_id") or region.fill_id)
                if region.fill_id != target:
                    raise ValueError("region.replace fill identity mismatch")
                previous_members = fill_members.get(target, set())
                prior_positions = [index for index, sid in enumerate(order) if sid in previous_members]
                insert_at = min(prior_positions) if prior_positions else len(order)
                for sid in previous_members:
                    state.pop(sid, None)
                if previous_members:
                    order = [sid for sid in order if sid not in previous_members]
                replacement_strokes = _fill_strokes(region, item)
                members = set()
                for offset, stroke in enumerate(replacement_strokes):
                    sid = str(stroke.stroke_id)
                    members.add(sid)
                    if sid in order:
                        order.remove(sid)
                    order.insert(min(insert_at + offset, len(order)), sid)
                    state[sid] = stroke
                fill_members[target] = members
            elif item.action == "snapshot":
                pass
            else:
                raise ValueError(f"unsupported replay action: {item.action}")
        ir = StrokeIR(self.width, self.height, metadata={**self.metadata, "history_cursor": limit})
        for sid in order:
            if sid in state:
                ir.add(deepcopy(state[sid]))
        return ir

    def to_dict(self) -> dict[str, Any]:
        return {
            "width": self.width,
            "height": self.height,
            "metadata": deepcopy(self.metadata),
            "cursor": self.cursor,
            "actions": [a.to_dict() for a in self.actions],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CanvasHistory":
        h = cls(data["width"], data["height"], data.get("metadata"))
        actions = []
        for raw in data.get("actions", []):
            payload = deepcopy(raw.get("payload", {}))
            stage = raw.get("stage") or "unspecified"
            actions.append(
                CanvasAction(
                    seq=int(raw["seq"]),
                    action=str(raw["action"]),
                    stage=stage,
                    payload=payload,
                    logical_time=float(raw.get("logical_time", int(raw["seq"]) - 1)),
                    part=raw.get("part"),
                    role=raw.get("role"),
                    tool_state=deepcopy(raw.get("tool_state")),
                    provenance=deepcopy(raw.get("provenance")),
                )
            )
        for i, a in enumerate(actions, 1):
            if a.seq != i:
                raise ValueError("action seq must be contiguous and 1-based")
        h.actions = actions
        h.cursor = max(0, min(int(data.get("cursor", len(actions))), len(actions)))
        ids = []
        for a in actions:
            if a.action in {"stroke.add", "stroke.replace"}:
                sid = a.payload.get("stroke", {}).get("stroke_id")
                if sid:
                    ids.append(sid)
        h._next_id = len(ids) + 1
        return h
