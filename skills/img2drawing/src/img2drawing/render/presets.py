from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from importlib import resources
from pathlib import Path
from typing import Mapping


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
