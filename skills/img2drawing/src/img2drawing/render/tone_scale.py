"""Cached deposition calibration for value work.

The pencil-contact renderer does not deposit graphite in proportion to the numbers
an agent would guess. Authoring a garment at ``opacity=0.24`` looks reasonable and
renders as blank paper, which is how a dogfood session ended up laying 372 strokes
to move a value by one level.

That is a property of the renderer, not of any drawing, so it is measured once by
``dev/calibration/calibrate_tone_scale.py`` and cached here. Ask for the value you
observed in the subject; the table supplies the material that reaches it.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from importlib import resources
from typing import Any


@dataclass(frozen=True)
class ToneRecipe:
    """Material that renders to a known mean value on this canvas."""

    value: int
    measured: float
    grade: str
    opacity: float
    pressure: float
    width: float
    spacing: float

    def tool_overrides(self) -> dict[str, float]:
        return {"opacity": self.opacity, "pressure": self.pressure, "width": self.width}

    def to_dict(self) -> dict[str, Any]:
        return {
            "value": self.value, "measured": self.measured, "grade": self.grade,
            "opacity": self.opacity, "pressure": self.pressure,
            "width": self.width, "spacing": self.spacing,
        }


@lru_cache(maxsize=1)
def load_tone_scale() -> tuple[ToneRecipe, ...]:
    text = resources.files("img2drawing.data").joinpath("tone_scale.json").read_text(encoding="utf-8")
    payload = json.loads(text)
    if payload.get("schema") != "img2drawing.tone_scale/v1":
        raise ValueError(f"unsupported tone scale schema: {payload.get('schema')!r}")
    steps = tuple(
        ToneRecipe(
            value=int(s["value"]), measured=float(s["measured"]), grade=str(s["grade"]),
            opacity=float(s["opacity"]), pressure=float(s["pressure"]),
            width=float(s["width"]), spacing=float(s["spacing"]),
        )
        for s in payload.get("steps", ())
    )
    if not steps:
        raise ValueError("tone scale contains no steps")
    return steps


def available_values() -> tuple[int, ...]:
    return tuple(r.value for r in load_tone_scale())


def resolve_tone(value: float) -> ToneRecipe:
    """Nearest calibrated recipe for a target mean value (0 black - 255 paper)."""
    v = float(value)
    if not 0.0 <= v <= 255.0:
        raise ValueError("tone value must be in [0,255]")
    return min(load_tone_scale(), key=lambda r: abs(r.measured - v))
