"""Reusable authoring helpers distilled from successful explicit-stroke runs.

These helpers intentionally encode no subject-specific geometry. They reduce avoidable
mechanical friction while preserving the Agent's responsibility for observation and shape.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping, Sequence


_TOOL_OVERRIDE_FIELDS = (
    "width",
    "pressure",
    "opacity",
    "hardness",
    "grain",
    "taper_in",
    "taper_out",
    "jitter",
    "erase_strength",
)


def retune_stroke(
    session: Any,
    stroke_id: str,
    *,
    reason: str,
    tool_overrides: Mapping[str, float] | None = None,
    grade: str | None = None,
    observation_id: str | None = None,
    source_observation: str | None = None,
    metadata: Mapping[str, Any] | None = None,
) -> str:
    """Change stroke material/tool parameters without re-authoring its geometry.

    The current replacement descendant is resolved first. Points, semantic part/role,
    confidence, layer, stable stroke identity, and authored pressure (when explicitly supplied)
    are inherited. Derived pressure is deliberately regenerated from the retuned tool state so
    taper/pressure changes can actually take effect.

    This helper emits the existing ``replace_stroke`` action; it does not add a persistence
    schema or a second editing path.
    """

    normalized_reason = str(reason).strip()
    if not normalized_reason:
        raise ValueError("retune_stroke requires a non-empty reason")

    current = session.current_stroke(stroke_id)
    current_id = str(current.stroke_id or stroke_id)
    tool_state = deepcopy(current.tool_state or {})
    preset = str(tool_state.get("tool", "")).strip()
    if not preset:
        raise ValueError("current stroke has no recoverable tool preset")

    inherited_overrides: dict[str, float] = {}
    for name in _TOOL_OVERRIDE_FIELDS:
        if name in tool_state:
            inherited_overrides[name] = float(tool_state[name])
    for name, value in dict(tool_overrides or {}).items():
        if name not in _TOOL_OVERRIDE_FIELDS:
            raise ValueError(f"unsupported stroke retune field: {name}")
        inherited_overrides[name] = float(value)

    selected_grade = grade
    if selected_grade is None and tool_state.get("pencil_grade") is not None:
        selected_grade = str(tool_state["pencil_grade"])

    inherited_metadata: dict[str, Any] = {}
    provenance = tool_state.get("provenance")
    if isinstance(provenance, Mapping) and isinstance(provenance.get("metadata"), Mapping):
        inherited_metadata.update(deepcopy(dict(provenance["metadata"])))
    if metadata:
        inherited_metadata.update(deepcopy(dict(metadata)))
    inherited_metadata["geometry_preserved_from"] = current_id

    action_id = session.replace_stroke(
        current_id,
        current.points,
        reason=normalized_reason,
        stroke_id=current_id,
        role=current.role,
        part=current.part,
        confidence=current.confidence,
        layer=current.layer,
        pressure=(
            list(current.pressure)
            if current.pressure_authored and current.pressure is not None
            else None
        ),
        tool=preset,
        grade=selected_grade,
        tool_overrides=inherited_overrides,
        observation_id=observation_id,
        source_observation=source_observation,
        metadata=inherited_metadata,
    )

    revised = session.current_stroke(current_id)
    if list(revised.points) != list(current.points):
        raise RuntimeError("retune_stroke changed geometry; this violates the helper contract")
    return str(action_id)


def retune_strokes(
    session: Any,
    stroke_ids: Sequence[str],
    *,
    reason: str,
    tool_overrides: Mapping[str, float] | None = None,
    grade: str | None = None,
    observation_id: str | None = None,
    source_observation: str | None = None,
    metadata: Mapping[str, Any] | None = None,
) -> tuple[str, ...]:
    """Retune one coherent stroke group while preserving explicit per-stroke history.

    All requested identifiers are resolved before the first mutation. If two supplied identifiers
    resolve to the same current replacement descendant, the call fails instead of retuning that
    stroke twice. Each successful member still records its own existing ``stroke.replace`` action,
    so replay/provenance remain explicit rather than collapsing the group into a new batch action.
    """

    requested = tuple(str(stroke_id).strip() for stroke_id in stroke_ids)
    if not requested or any(not stroke_id for stroke_id in requested):
        raise ValueError("retune_strokes requires one or more non-empty stroke ids")

    resolved: list[str] = []
    seen: set[str] = set()
    for stroke_id in requested:
        current = session.current_stroke(stroke_id)
        current_id = str(current.stroke_id or stroke_id)
        if current_id in seen:
            raise ValueError(f"duplicate current stroke in retune group: {current_id}")
        if not str((current.tool_state or {}).get("tool", "")).strip():
            raise ValueError(f"current stroke has no recoverable tool preset: {current_id}")
        seen.add(current_id)
        resolved.append(current_id)

    return tuple(
        retune_stroke(
            session,
            stroke_id,
            reason=reason,
            tool_overrides=tool_overrides,
            grade=grade,
            observation_id=observation_id,
            source_observation=source_observation,
            metadata=metadata,
        )
        for stroke_id in resolved
    )


__all__ = ["reshape_stroke", "retune_stroke", "retune_strokes"]


def reshape_stroke(
    session: Any,
    stroke_id: str,
    points: Sequence[Sequence[float]],
    *,
    reason: str,
    pressure: Sequence[float] | None = None,
    observation_id: str | None = None,
    source_observation: str | None = None,
) -> str:
    """Replace geometry while retaining the current stroke's semantic and material properties.

    Returns the *action ID* for correction provenance. An explicitly authored pressure
    profile can be reused when the point count is unchanged; otherwise a replacement
    profile is required. Derived pressure is regenerated for the new path.
    """
    if not str(reason).strip():
        raise ValueError("reshape_stroke requires a non-empty reason")
    current = session.current_stroke(stroke_id)
    current_id = str(current.stroke_id or stroke_id)
    state = deepcopy(current.tool_state or {})
    preset = str(state.get("tool", "")).strip()
    if not preset:
        raise ValueError("current stroke has no recoverable tool preset")
    new_points = list(points)
    local_lift = any(
        isinstance(edit, Mapping) and edit.get("kind") == "segment_soft_lift"
        for edit in (state.get("local_edits") or ())
    )
    # A local eraser attenuates point pressures even when the original curve
    # was derived. Carry that edited curve forward instead of regenerating it.
    if pressure is None and (current.pressure_authored or local_lift) and current.pressure is not None:
        if len(current.pressure) != len(new_points):
            raise ValueError("reshaping a stroke with edited pressure and a different point count requires pressure")
        pressure = list(current.pressure)
    overrides = {name: float(state[name]) for name in _TOOL_OVERRIDE_FIELDS if name in state}
    # Global soft_lift changes the replayed stroke opacity, not its original
    # tool_state. Preserve the visible attenuation across geometry correction.
    if current.opacity != float(state.get("opacity", current.opacity)):
        overrides["opacity"] = float(current.opacity)
    provenance = state.get("provenance")
    metadata = deepcopy(dict(provenance.get("metadata", {}))) if isinstance(provenance, Mapping) and isinstance(provenance.get("metadata"), Mapping) else {}
    metadata["geometry_reshaped_from"] = current_id
    session.replace_stroke(
        current_id, new_points, reason=str(reason).strip(), stroke_id=current_id,
        role=current.role, part=current.part, confidence=current.confidence, layer=current.layer,
        pressure=pressure, tool=preset, grade=state.get("pencil_grade"), tool_overrides=overrides,
        observation_id=observation_id, source_observation=source_observation, metadata=metadata,
    )
    element = session.resolve_authored_element(current_id, element_type="stroke")
    if element is None or not element.latest_action_id:
        raise RuntimeError("reshaped stroke has no current action")
    return str(element.latest_action_id)
