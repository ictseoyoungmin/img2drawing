"""Append-only value-region revision for the vNext drawing session.

A tone region is one authored decision.  When later inspection disproves that
decision, revise the region itself instead of stacking another fill or editing
hundreds of generated hatch strokes.
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from ..core.action import DrawingAction
from ..core.fill import FillRegion, ReservedLight
from ..render.tone_scale import resolve_tone
from .session import DrawingSession, _COMPAT_STAGE, _action_id, _tool_payload


def replace_fill_region(
    session: DrawingSession,
    fill_id: str,
    *,
    value: float,
    reason: str,
    polygon: Sequence[Sequence[float]] | None = None,
    part: str | None = None,
    angle: float | None = None,
    observation_id: str | None = None,
    source_observation: str | None = None,
    reserved: Sequence[Any] | None = None,
    spacing: float | None = None,
    role: str | None = None,
    layer: int | None = None,
    min_length: float | None = None,
    action_id: str | None = None,
    tool: str = "form_pencil",
    metadata: Mapping[str, Any] | None = None,
) -> str:
    """Replace one existing fill definition and return the correction action id.

    Omitted geometry/semantic fields are inherited from the current definition.
    The requested value is re-resolved through the calibrated tone scale, so a
    value correction is one append-only history action.  The fill identity stays
    stable while the returned action id can be passed directly to
    ``DrawingSession.record_correction``.
    """

    if not isinstance(session, DrawingSession):
        raise TypeError("session must be a vNext DrawingSession")
    target = str(fill_id).strip()
    if not target:
        raise ValueError("fill_id must be non-empty")
    normalized_reason = str(reason).strip()
    if not normalized_reason:
        raise ValueError("replace_fill_region requires a correction reason")

    current = session._agent.history.current_fill_region(target)
    recipe = resolve_tone(value)
    if reserved is None:
        lights = current.reserved
    else:
        lights = tuple(
            light if isinstance(light, ReservedLight) else ReservedLight(**dict(light))
            for light in reserved
        )
    points = current.polygon if polygon is None else tuple(
        (float(x), float(y)) for x, y in polygon
    )
    region = FillRegion(
        fill_id=target,
        polygon=points,
        angle=current.angle if angle is None else float(angle),
        spacing=float(recipe.spacing if spacing is None else spacing),
        part=current.part if part is None else str(part),
        role=current.role if role is None else str(role),
        reserved=lights,
        layer=current.layer if layer is None else int(layer),
        min_length=current.min_length if min_length is None else float(min_length),
    )
    oid, source, _ = session._provenance(
        observation_id=observation_id,
        source_observation=source_observation,
        reason=normalized_reason,
    )
    action = DrawingAction(
        action_id=_action_id(session._agent.history, action_id),
        kind="replace_fill_region",
        stage=_COMPAT_STAGE,
        role=region.role,
        part=region.part,
        layer=region.layer,
        tool=_tool_payload(tool, recipe.grade, recipe.tool_overrides()),
        observation_id=oid,
        source_observation=source,
        reason=normalized_reason,
        revision_of=target,
        region=region.to_dict(),
        metadata={**(dict(metadata) if metadata else {}), "tone": recipe.to_dict()},
    )
    session._commit(action)
    return action.action_id


__all__ = ["replace_fill_region"]
