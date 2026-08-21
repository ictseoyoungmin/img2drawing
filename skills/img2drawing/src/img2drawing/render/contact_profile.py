from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from importlib import resources
from pathlib import Path




@dataclass(frozen=True)
class MaterialProfile:
    deposition_floor: float
    deposition_exponent: float
    width_base: float
    width_pressure_gain: float
    min_width: float
    continuity_floor_ratio: float
    continuity_min_coverage: float


@dataclass(frozen=True)
class GrainProfile:
    coarse_cell: float
    fine_cell: float
    strength: float
    thin_width_reference: float
    thin_texture_floor: float
    min_modulation: float
    max_modulation: float


@dataclass(frozen=True)
class PaperProfile:
    strength: float
    valley_band: float
    valley_depth: float
    thin_width_reference: float
    thin_texture_floor: float
    min_modulation: float
    max_modulation: float


@dataclass(frozen=True)
class HandProfile:
    pressure_cadence_strength: float
    pressure_cadence_frequency_min: float
    pressure_cadence_frequency_span: float
    tip_span: float
    taper_in_strength: float
    taper_out_strength: float


@dataclass(frozen=True)
class EdgeProfile:
    soft_halo_radius: float
    soft_halo_strength: float


@dataclass(frozen=True)
class PencilContactProfile:
    name: str
    trajectory_spacing: float
    material: MaterialProfile
    grain: GrainProfile
    paper: PaperProfile
    hand: HandProfile
    edge: EdgeProfile


def _positive(name: str, value: float) -> float:
    value = float(value)
    if value <= 0:
        raise ValueError(f"{name} must be positive")
    return value


def _unit(name: str, value: float) -> float:
    value = float(value)
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"{name} must be in [0,1]")
    return value


def _load_payload(path: str | Path | None) -> dict:
    if path is None:
        text = resources.files("img2drawing.data").joinpath("pencil_contact_profile.json").read_text(encoding="utf-8")
    else:
        text = Path(path).read_text(encoding="utf-8")
    return json.loads(text)


@lru_cache(maxsize=8)
def load_pencil_contact_profile(path: str | Path | None = None) -> PencilContactProfile:
    raw = _load_payload(path)
    m = raw["material"]; g = raw["grain"]; p = raw["paper"]; h = raw["hand"]; e = raw["edge"]
    profile = PencilContactProfile(
        name=str(raw.get("name", "pencil-contact")),
        trajectory_spacing=_positive("trajectory_spacing", raw["trajectory_spacing"]),
        material=MaterialProfile(
            deposition_floor=_unit("material.deposition_floor", m["deposition_floor"]),
            deposition_exponent=_positive("material.deposition_exponent", m["deposition_exponent"]),
            width_base=_positive("material.width_base", m["width_base"]),
            width_pressure_gain=_unit("material.width_pressure_gain", m["width_pressure_gain"]),
            min_width=_positive("material.min_width", m["min_width"]),
            continuity_floor_ratio=_unit("material.continuity_floor_ratio", m["continuity_floor_ratio"]),
            continuity_min_coverage=_unit("material.continuity_min_coverage", m["continuity_min_coverage"]),
        ),
        grain=GrainProfile(
            coarse_cell=_positive("grain.coarse_cell", g["coarse_cell"]),
            fine_cell=_positive("grain.fine_cell", g["fine_cell"]),
            strength=_unit("grain.strength", g["strength"]),
            thin_width_reference=_positive("grain.thin_width_reference", g["thin_width_reference"]),
            thin_texture_floor=_unit("grain.thin_texture_floor", g["thin_texture_floor"]),
            min_modulation=_positive("grain.min_modulation", g["min_modulation"]),
            max_modulation=_positive("grain.max_modulation", g["max_modulation"]),
        ),
        paper=PaperProfile(
            strength=_unit("paper.strength", p["strength"]),
            valley_band=_positive("paper.valley_band", p["valley_band"]),
            valley_depth=_unit("paper.valley_depth", p["valley_depth"]),
            thin_width_reference=_positive("paper.thin_width_reference", p["thin_width_reference"]),
            thin_texture_floor=_unit("paper.thin_texture_floor", p["thin_texture_floor"]),
            min_modulation=_positive("paper.min_modulation", p["min_modulation"]),
            max_modulation=_positive("paper.max_modulation", p["max_modulation"]),
        ),
        hand=HandProfile(
            pressure_cadence_strength=_unit("hand.pressure_cadence_strength", h["pressure_cadence_strength"]),
            pressure_cadence_frequency_min=_positive("hand.pressure_cadence_frequency_min", h["pressure_cadence_frequency_min"]),
            pressure_cadence_frequency_span=_positive("hand.pressure_cadence_frequency_span", h["pressure_cadence_frequency_span"]),
            tip_span=_positive("hand.tip_span", h["tip_span"]),
            taper_in_strength=_unit("hand.taper_in_strength", h["taper_in_strength"]),
            taper_out_strength=_unit("hand.taper_out_strength", h["taper_out_strength"]),
        ),
        edge=EdgeProfile(
            soft_halo_radius=_unit("edge.soft_halo_radius", e["soft_halo_radius"]),
            soft_halo_strength=_unit("edge.soft_halo_strength", e["soft_halo_strength"]),
        ),
    )
    if profile.grain.min_modulation > profile.grain.max_modulation:
        raise ValueError("grain modulation range is inverted")
    if profile.paper.min_modulation > profile.paper.max_modulation:
        raise ValueError("paper modulation range is inverted")
    return profile
