"""Reusable authoring helpers distilled from successful explicit-stroke runs.

These helpers intentionally encode no subject-specific geometry. They reduce avoidable
mechanical friction while preserving the Agent's responsibility for observation and shape.
"""

from __future__ import annotations

from copy import deepcopy
from math import hypot
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
        pressure=(list(current.pressure) if current.pressure_authored and current.pressure is not None else None),
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


def sample_catmull_rom(
    control_points: Sequence[Sequence[float]],
    *,
    spacing: float = 3.0,
    samples_per_segment: int = 24,
    closed: bool = False,
) -> list[tuple[float, float]]:
    """Sample a deterministic Catmull-Rom curve and resample it by approximate arc length.

    Use this only for a continuously smooth observed interval. Corners, cusps, tangency breaks,
    component joins, and other real topology changes should be split into separate curve/stroke
    intervals instead of being smoothed through by the sampler.
    """

    points = [(float(p[0]), float(p[1])) for p in control_points]
    if len(points) < 2:
        raise ValueError("sample_catmull_rom requires at least two control points")
    if spacing <= 0:
        raise ValueError("spacing must be positive")
    dense_n = int(samples_per_segment)
    if dense_n < 4:
        raise ValueError("samples_per_segment must be >= 4")

    if len(points) == 2:
        dense = [points[0], points[1]]
    else:
        if closed:
            padded = [points[-1], *points, points[0], points[1]]
            segment_count = len(points)
        else:
            padded = [points[0], *points, points[-1]]
            segment_count = len(points) - 1

        dense: list[tuple[float, float]] = [points[0]]
        for segment in range(segment_count):
            p0, p1, p2, p3 = padded[segment : segment + 4]
            for sample in range(1, dense_n + 1):
                t = sample / dense_n
                t2 = t * t
                t3 = t2 * t
                x = 0.5 * (
                    2.0 * p1[0]
                    + (-p0[0] + p2[0]) * t
                    + (2.0 * p0[0] - 5.0 * p1[0] + 4.0 * p2[0] - p3[0]) * t2
                    + (-p0[0] + 3.0 * p1[0] - 3.0 * p2[0] + p3[0]) * t3
                )
                y = 0.5 * (
                    2.0 * p1[1]
                    + (-p0[1] + p2[1]) * t
                    + (2.0 * p0[1] - 5.0 * p1[1] + 4.0 * p2[1] - p3[1]) * t2
                    + (-p0[1] + 3.0 * p1[1] - 3.0 * p2[1] + p3[1]) * t3
                )
                dense.append((x, y))

    if closed and dense[-1] != dense[0]:
        dense.append(dense[0])

    cumulative = [0.0]
    for a, b in zip(dense, dense[1:]):
        cumulative.append(cumulative[-1] + hypot(b[0] - a[0], b[1] - a[1]))
    total = cumulative[-1]
    if total == 0.0:
        return [dense[0], dense[-1]]

    targets: list[float] = [0.0]
    cursor = float(spacing)
    while cursor < total:
        targets.append(cursor)
        cursor += float(spacing)
    targets.append(total)

    out: list[tuple[float, float]] = []
    dense_index = 0
    for target in targets:
        while dense_index + 1 < len(cumulative) and cumulative[dense_index + 1] < target:
            dense_index += 1
        if dense_index + 1 >= len(dense):
            out.append(dense[-1])
            continue
        a = dense[dense_index]
        b = dense[dense_index + 1]
        lo = cumulative[dense_index]
        hi = cumulative[dense_index + 1]
        ratio = 0.0 if hi == lo else (target - lo) / (hi - lo)
        out.append((a[0] + (b[0] - a[0]) * ratio, a[1] + (b[1] - a[1]) * ratio))

    out[0] = dense[0]
    out[-1] = dense[-1]
    return out
