"""An observation-owned tonal *area plan*; never an implicit raster fill.

A plan records the observed region and intended pencil mark family. Its
per-stroke metadata follows each individually authored DrawingSession action,
so no independent history or renderer surface is introduced.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from ..core.digest import sha256_obj

TONAL_AREA_SCHEMA = "img2drawing.authoring.tonal_area.v1"


def _polygon(points: Sequence[Sequence[float]], *, label: str) -> tuple[tuple[float, float], ...]:
    try:
        out = tuple((float(p[0]), float(p[1])) for p in points)
    except (TypeError, ValueError, IndexError) as exc:
        raise ValueError(f"{label} requires finite 2D coordinates") from exc
    if len(out) < 3:
        raise ValueError(f"{label} requires at least three points")
    if not all(math.isfinite(c) for p in out for c in p):
        raise ValueError(f"{label} requires finite coordinates")
    area = sum(
        out[i][0] * out[(i + 1) % len(out)][1]
        - out[(i + 1) % len(out)][0] * out[i][1]
        for i in range(len(out))
    )
    if abs(area) <= 1e-9:
        raise ValueError(f"{label} must enclose nonzero area")
    return out


@dataclass(frozen=True)
class TonalAreaPlan:
    """Bounded semantic planning evidence, not a drawing command.

    All geometry is explicitly selected from reference observation. A
    worker still authors every stroke and validates its effect by rendering.
    `density` is an intended mark-coverage ratio, not a renderer fill factor.
    `target_value` is an intended perceptual darkness, not a pixel command.
    """

    area_id: str
    part: str
    reference_evidence: str
    boundary: tuple[tuple[float, float], ...]
    direction_degrees: float
    target_density: float
    target_value: float
    pressure_range: tuple[float, float]
    highlight_reserves: tuple[tuple[tuple[float, float], ...], ...] = ()

    def __post_init__(self) -> None:
        for key in ("area_id", "part", "reference_evidence"):
            name = str(getattr(self, key)).strip()
            if not name:
                raise ValueError(f"{key} must be non-empty")
            object.__setattr__(self, key, name)
        object.__setattr__(self, "boundary", _polygon(self.boundary, label="boundary"))
        object.__setattr__(
            self, "highlight_reserves",
            tuple(_polygon(p, label="highlight_reserve") for p in self.highlight_reserves),
        )
        direction = float(self.direction_degrees)
        if not math.isfinite(direction):
            raise ValueError("direction_degrees must be finite")
        object.__setattr__(self, "direction_degrees", direction % 180.0)
        for key in ("target_density", "target_value"):
            val = float(getattr(self, key))
            if not math.isfinite(val) or not 0.0 <= val <= 1.0:
                raise ValueError(f"{key} must be finite and in [0,1]")
            object.__setattr__(self, key, val)
        try:
            lo, hi = (float(v) for v in self.pressure_range)
        except (TypeError, ValueError) as exc:
            raise ValueError("pressure_range must contain two values") from exc
        if not (math.isfinite(lo) and math.isfinite(hi) and 0.0 <= lo <= hi <= 1.0):
            raise ValueError("pressure_range must be ordered within [0,1]")
        object.__setattr__(self, "pressure_range", (lo, hi))

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": TONAL_AREA_SCHEMA,
            "area_id": self.area_id,
            "part": self.part,
            "reference_evidence": self.reference_evidence,
            "boundary": [list(point) for point in self.boundary],
            "direction_degrees": self.direction_degrees,
            "target_density": self.target_density,
            "target_value": self.target_value,
            "pressure_range": list(self.pressure_range),
            "highlight_reserves": [
                [list(point) for point in region] for region in self.highlight_reserves
            ],
        }

    def digest(self) -> str:
        return sha256_obj(self.to_dict())

    def stroke_metadata(
        self, *, stroke_family: str, metadata: Mapping[str, Any] | None = None
    ) -> dict[str, Any]:
        """Attach a replayable plan to an individually authored pencil stroke."""
        from copy import deepcopy
        family = str(stroke_family).strip()
        if not family:
            raise ValueError("stroke_family must be non-empty")
        result = deepcopy(dict(metadata or {}))
        result["tonal_area"] = {**self.to_dict(), "digest": self.digest(), "stroke_family": family}
        return result


__all__ = ["TONAL_AREA_SCHEMA", "TonalAreaPlan"]
