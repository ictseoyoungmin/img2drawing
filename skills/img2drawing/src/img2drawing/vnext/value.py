"""Append-only value-region revision for the vNext drawing session.

A tone region is one authored decision.  When later inspection disproves that
decision, revise the region itself instead of stacking another fill or editing
hundreds of generated hatch strokes.
"""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from .session import DrawingSession


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
    return session.replace_fill_region(
        fill_id,
        value=value,
        reason=reason,
        polygon=polygon,
        part=part,
        angle=angle,
        observation_id=observation_id,
        source_observation=source_observation,
        reserved=reserved,
        spacing=spacing,
        role=role,
        layer=layer,
        min_length=min_length,
        action_id=action_id,
        tool=tool,
        metadata=metadata,
    )


__all__ = ["replace_fill_region"]
