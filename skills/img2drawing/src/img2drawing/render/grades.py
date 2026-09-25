"""Named pencil grades: data-driven graphite core presets applied per stroke."""

from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import dataclass
from functools import lru_cache
from importlib import resources
from pathlib import Path
from typing import Mapping

from ..core.ir import Stroke


@dataclass(frozen=True)
class PencilPreset:
    name: str
    target_hardness: float
    target_grain: float
    graphite_release: float
    contact_spread: float


def _clamp01(v: float) -> float:
    return max(0.0, min(1.0, float(v)))


def _validate_entry(name: str, raw: dict) -> PencilPreset:
    return PencilPreset(
        name=str(name).upper(),
        target_hardness=_clamp01(raw["target_hardness"]),
        target_grain=_clamp01(raw["target_grain"]),
        graphite_release=max(0.01, float(raw["graphite_release"])),
        contact_spread=max(0.01, float(raw["contact_spread"])),
    )


@lru_cache(maxsize=8)
def load_pencil_presets(path: str | Path | None = None) -> Mapping[str, PencilPreset]:
    if path is None:
        text = resources.files("img2drawing.data").joinpath("pencil_presets.json").read_text(encoding="utf-8")
    else:
        text = Path(path).read_text(encoding="utf-8")
    payload = json.loads(text)
    grades = payload.get("grades") or {}
    out: dict[str, PencilPreset] = {}
    for name, raw in grades.items():
        preset = _validate_entry(name, raw)
        out[preset.name] = preset
    if not out:
        raise ValueError("no pencil presets loaded")
    return out


def default_grade_name(path: str | Path | None = None) -> str:
    if path is None:
        text = resources.files("img2drawing.data").joinpath("pencil_presets.json").read_text(encoding="utf-8")
    else:
        text = Path(path).read_text(encoding="utf-8")
    payload = json.loads(text)
    name = str(payload.get("default_grade", "HB")).upper()
    presets = load_pencil_presets(path)
    if name not in presets:
        raise ValueError(f"default pencil grade {name!r} is not defined in presets")
    return name


def list_pencil_grades(path: str | Path | None = None) -> tuple[str, ...]:
    return tuple(load_pencil_presets(path).keys())


def get_pencil_preset(name: str, path: str | Path | None = None) -> PencilPreset:
    key = str(name).strip().upper()
    presets = load_pencil_presets(path)
    try:
        return presets[key]
    except KeyError as exc:
        raise ValueError(f"unknown pencil grade: {name!r}; expected one of {tuple(presets)}") from exc


def selected_grade(stroke: Stroke, global_grade: str | None) -> str | None:
    """Stroke-local grade wins; otherwise an explicit render-wide grade applies."""

    ts = stroke.tool_state if isinstance(stroke.tool_state, dict) else {}
    local = ts.get("pencil_grade")
    if local is not None:
        return str(local).upper()
    return None if global_grade is None else str(global_grade).upper()


def apply_grade(stroke: Stroke, grade: str) -> Stroke:
    """Return a derived graded stroke without mutating authoritative history.

    Tool role still owns authored pressure/width/opacity/hand dynamics. Grade owns the
    graphite core response: existing role material is blended toward the named core so a
    construction line remains a construction line while reading as the chosen grade.
    """
    preset = get_pencil_preset(grade)
    out = deepcopy(stroke)
    ts = deepcopy(out.tool_state) if isinstance(out.tool_state, dict) else {}

    base_h = _clamp01(ts.get("hardness", 0.65))
    base_g = _clamp01(ts.get("grain", 0.30))
    ts["hardness"] = _clamp01(0.30 * base_h + 0.70 * preset.target_hardness)
    ts["grain"] = _clamp01(0.35 * base_g + 0.65 * preset.target_grain)
    ts["pencil_grade"] = preset.name

    # Width is physical core/paper contact spread; opacity is maximum graphite load, so
    # scaling it is graphite release at the core rather than a post-render alpha filter.
    out.width = max(0.18, float(out.width) * preset.contact_spread)
    out.opacity = _clamp01(float(out.opacity) * preset.graphite_release)
    out.tool_state = ts
    return out.cleaned()


def prepare_grade(stroke: Stroke, global_grade: str | None) -> Stroke:
    grade = selected_grade(stroke, global_grade)
    return deepcopy(stroke) if grade is None else apply_grade(stroke, grade)
