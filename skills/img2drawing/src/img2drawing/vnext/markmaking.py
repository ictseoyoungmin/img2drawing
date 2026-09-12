"""Public markmaking resolution for semantic roles, material policy, and tool vocabulary.

This module is the worker-facing bridge between high-level drawing intent and the existing
``DrawingSession.draw`` surface. It deliberately does not expose renderer implementation classes.
Preset names explain intent; the fully resolved state recorded in provenance is replay evidence.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, dataclass, replace
from typing import Any, Mapping

from ..core.session import sha256_obj
from ..core.tools import ToolState, get_tool
from ..render.presets import get_pencil_preset


MARKMAKING_SCHEMA = "img2drawing.vnext.markmaking.v1"
MATERIAL_POLICY_REVISION = 1
TOOL_PRESET_REVISION = 1

MATERIAL_POLICIES = (
    "canonical-pencil",
    "manga-light",
    "dry-graphite-expressive",
)

SEMANTIC_STROKE_ROLES = (
    "construction",
    "gesture",
    "form",
    "contour",
    "accent",
    "hair",
    "hatch",
    "broad_mass",
    "environment",
)

TOOL_PRESETS = (
    "construction-light",
    "gesture-flow",
    "form-pencil",
    "contour-weighted",
    "accent-dark",
    "hair-flick",
    "broad-graphite",
    "hatch-light",
    "hatch-heavy",
    "environment-line",
)

TERMINAL_MODES = ("contact", "gentle", "flick", "residue")

_ALLOWED_MODIFIERS = {
    "width",
    "pressure",
    "opacity",
    "hardness",
    "grain",
    "taper_in",
    "taper_out",
    "jitter",
}


def _validated_modifiers(raw: Mapping[str, Any] | None) -> dict[str, float]:
    values = dict(raw or {})
    unknown = set(values).difference(_ALLOWED_MODIFIERS)
    if unknown:
        raise ValueError(f"unsupported markmaking modifiers: {sorted(unknown)}")
    out: dict[str, float] = {}
    for name, value in values.items():
        number = float(value)
        if name == "width":
            if number <= 0.0:
                raise ValueError("width modifier must be positive")
        elif not 0.0 <= number <= 1.0:
            raise ValueError(f"{name} modifier must be in [0,1]")
        out[name] = number
    return out


def _resolved_tool_state(base_tool: str, overrides: Mapping[str, float]) -> ToolState:
    tool = get_tool(base_tool)
    if overrides:
        tool = replace(tool, **dict(overrides)).validated()
    return tool


@dataclass(frozen=True)
class MaterialPolicy:
    """Stable material-policy identity used by the markmaking resolver."""

    policy_id: str
    revision: int
    value_authority: str
    core_preservation: float
    shoulder_breakup: float
    grain_exposure: float
    local_variation: float

    def __post_init__(self) -> None:
        if self.policy_id not in MATERIAL_POLICIES:
            raise ValueError(f"unknown material policy: {self.policy_id!r}")
        if int(self.revision) != self.revision or int(self.revision) < 1:
            raise ValueError("material policy revision must be a positive integer")
        if self.value_authority not in {"strict", "balanced", "relaxed"}:
            raise ValueError("value_authority must be strict, balanced, or relaxed")
        for name in (
            "core_preservation",
            "shoulder_breakup",
            "grain_exposure",
            "local_variation",
        ):
            value = float(getattr(self, name))
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be in [0,1]")
            object.__setattr__(self, name, value)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ToolPreset:
    """One semantic public tool preset resolved onto the existing runtime tool surface."""

    preset_id: str
    revision: int
    base_tool: str
    grade: str
    overrides: Mapping[str, float]
    terminal_mode: str

    def __post_init__(self) -> None:
        if self.preset_id not in TOOL_PRESETS:
            raise ValueError(f"unknown markmaking tool preset: {self.preset_id!r}")
        if int(self.revision) != self.revision or int(self.revision) < 1:
            raise ValueError("tool preset revision must be a positive integer")
        get_tool(self.base_tool)
        object.__setattr__(self, "grade", get_pencil_preset(self.grade).name)
        if self.terminal_mode not in TERMINAL_MODES:
            raise ValueError(f"unknown terminal mode: {self.terminal_mode!r}")
        object.__setattr__(self, "overrides", _validated_modifiers(self.overrides))


_MATERIAL_POLICY_REGISTRY = {
    "canonical-pencil": MaterialPolicy(
        "canonical-pencil", MATERIAL_POLICY_REVISION, "strict", 0.92, 0.28, 0.32, 0.24
    ),
    "manga-light": MaterialPolicy(
        "manga-light", MATERIAL_POLICY_REVISION, "relaxed", 0.55, 0.58, 0.48, 0.22
    ),
    "dry-graphite-expressive": MaterialPolicy(
        "dry-graphite-expressive", MATERIAL_POLICY_REVISION, "balanced", 0.72, 0.76, 0.72, 0.32
    ),
}

_TOOL_PRESET_REGISTRY = {
    "construction-light": ToolPreset(
        "construction-light",
        TOOL_PRESET_REVISION,
        "construction_pencil",
        "HB",
        {"width": 1.6, "pressure": 0.26, "opacity": 0.26, "taper_in": 0.32, "taper_out": 0.42},
        "gentle",
    ),
    "gesture-flow": ToolPreset(
        "gesture-flow",
        TOOL_PRESET_REVISION,
        "form_pencil",
        "HB",
        {"width": 2.6, "pressure": 0.52, "opacity": 0.58, "taper_in": 0.30, "taper_out": 0.48},
        "gentle",
    ),
    "form-pencil": ToolPreset(
        "form-pencil", TOOL_PRESET_REVISION, "form_pencil", "HB", {}, "gentle"
    ),
    "contour-weighted": ToolPreset(
        "contour-weighted",
        TOOL_PRESET_REVISION,
        "form_pencil",
        "2B",
        {"width": 3.6, "pressure": 0.68, "opacity": 0.78, "taper_in": 0.16, "taper_out": 0.22},
        "gentle",
    ),
    "accent-dark": ToolPreset(
        "accent-dark",
        TOOL_PRESET_REVISION,
        "accent_pencil",
        "4B",
        {"width": 4.4, "pressure": 0.86, "opacity": 0.96, "taper_in": 0.12, "taper_out": 0.18},
        "contact",
    ),
    "hair-flick": ToolPreset(
        "hair-flick",
        TOOL_PRESET_REVISION,
        "form_pencil",
        "HB",
        {"width": 2.2, "pressure": 0.56, "opacity": 0.68, "taper_in": 0.10, "taper_out": 0.92, "jitter": 0.025},
        "flick",
    ),
    "broad-graphite": ToolPreset(
        "broad-graphite",
        TOOL_PRESET_REVISION,
        "accent_pencil",
        "4B",
        {"width": 8.0, "pressure": 0.72, "opacity": 0.80, "hardness": 0.48, "grain": 0.58, "taper_in": 0.08, "taper_out": 0.18},
        "residue",
    ),
    "hatch-light": ToolPreset(
        "hatch-light",
        TOOL_PRESET_REVISION,
        "construction_pencil",
        "HB",
        {"width": 1.5, "pressure": 0.30, "opacity": 0.34, "taper_in": 0.08, "taper_out": 0.10, "jitter": 0.025},
        "gentle",
    ),
    "hatch-heavy": ToolPreset(
        "hatch-heavy",
        TOOL_PRESET_REVISION,
        "form_pencil",
        "2B",
        {"width": 2.2, "pressure": 0.58, "opacity": 0.66, "taper_in": 0.06, "taper_out": 0.08, "jitter": 0.02},
        "gentle",
    ),
    "environment-line": ToolPreset(
        "environment-line",
        TOOL_PRESET_REVISION,
        "construction_pencil",
        "HB",
        {"width": 1.8, "pressure": 0.34, "opacity": 0.42, "taper_in": 0.16, "taper_out": 0.20},
        "gentle",
    ),
}

_ROLE_DEFAULT_TOOL = {
    "construction": "construction-light",
    "gesture": "gesture-flow",
    "form": "form-pencil",
    "contour": "contour-weighted",
    "accent": "accent-dark",
    "hair": "hair-flick",
    "hatch": "hatch-light",
    "broad_mass": "broad-graphite",
    "environment": "environment-line",
}

_STYLE_MATERIAL_POLICY = {
    "pencil_loose": "canonical-pencil",
    "graphite_academic": "canonical-pencil",
    "graphite_tonal": "dry-graphite-expressive",
    # Transitional spelling until high-level intent gains a builtin manga_light profile.
    "custom:manga-light": "manga-light",
}


def material_policy_for_style(style_profile: str, *, explicit: str | None = None) -> MaterialPolicy:
    """Resolve a high-level style intent to a stable material policy.

    Unknown/custom styles conservatively use canonical material behavior unless an explicit public
    material policy is supplied. This avoids guessing a decorative renderer policy from arbitrary
    style prose.
    """

    if explicit is not None:
        key = str(explicit).strip().lower()
    else:
        style = str(style_profile).strip().lower()
        key = _STYLE_MATERIAL_POLICY.get(style, "canonical-pencil")
    try:
        return _MATERIAL_POLICY_REGISTRY[key]
    except KeyError as exc:
        raise ValueError(f"unknown material policy: {key!r}") from exc


@dataclass(frozen=True)
class ResolvedMark:
    """Portable resolved markmaking decision for one authored stroke family."""

    style_profile: str
    semantic_role: str
    material_policy: MaterialPolicy
    tool_preset_id: str
    tool_preset_revision: int
    runtime_tool: str
    grade: str
    terminal_mode: str
    tool_overrides: Mapping[str, float]
    resolved_tool_state: Mapping[str, Any]

    def __post_init__(self) -> None:
        style = str(self.style_profile).strip().lower()
        if not style:
            raise ValueError("style_profile must be non-empty")
        object.__setattr__(self, "style_profile", style)
        if self.semantic_role not in SEMANTIC_STROKE_ROLES:
            raise ValueError(f"unknown semantic stroke role: {self.semantic_role!r}")
        if self.tool_preset_id not in TOOL_PRESETS:
            raise ValueError(f"unknown markmaking tool preset: {self.tool_preset_id!r}")
        if self.terminal_mode not in TERMINAL_MODES:
            raise ValueError(f"unknown terminal mode: {self.terminal_mode!r}")
        get_tool(self.runtime_tool)
        object.__setattr__(self, "grade", get_pencil_preset(self.grade).name)
        object.__setattr__(self, "tool_overrides", _validated_modifiers(self.tool_overrides))
        object.__setattr__(self, "resolved_tool_state", deepcopy(dict(self.resolved_tool_state)))

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": MARKMAKING_SCHEMA,
            "style_profile": self.style_profile,
            "semantic_role": self.semantic_role,
            "material_policy": self.material_policy.to_dict(),
            "tool_preset_id": self.tool_preset_id,
            "tool_preset_revision": self.tool_preset_revision,
            "runtime_tool": self.runtime_tool,
            "grade": self.grade,
            "terminal_mode": self.terminal_mode,
            "tool_overrides": dict(self.tool_overrides),
            "resolved_tool_state": deepcopy(dict(self.resolved_tool_state)),
        }

    def digest(self) -> str:
        return sha256_obj(self.to_dict())

    def draw_kwargs(self, *, metadata: Mapping[str, Any] | None = None) -> dict[str, Any]:
        """Return kwargs suitable for ``DrawingSession.draw`` with mark provenance attached."""

        outer = deepcopy(dict(metadata or {}))
        outer["markmaking"] = {**self.to_dict(), "digest": self.digest()}
        return {
            "role": self.semantic_role,
            "tool": {
                "preset": self.runtime_tool,
                "grade": self.grade,
                "overrides": dict(self.tool_overrides),
            },
            "metadata": outer,
        }


def resolve_markmaking(
    style_profile: str,
    semantic_role: str,
    *,
    tool_preset: str | None = None,
    grade: str | None = None,
    modifiers: Mapping[str, Any] | None = None,
    material_policy: str | None = None,
    terminal_mode: str | None = None,
) -> ResolvedMark:
    """Resolve a semantic mark decision without exposing renderer internals."""

    role = str(semantic_role).strip().lower()
    if role not in SEMANTIC_STROKE_ROLES:
        raise ValueError(f"unknown semantic stroke role: {role!r}")
    preset_id = _ROLE_DEFAULT_TOOL[role] if tool_preset is None else str(tool_preset).strip().lower()
    try:
        preset = _TOOL_PRESET_REGISTRY[preset_id]
    except KeyError as exc:
        raise ValueError(f"unknown markmaking tool preset: {preset_id!r}") from exc

    overrides = dict(preset.overrides)
    overrides.update(_validated_modifiers(modifiers))
    resolved = _resolved_tool_state(preset.base_tool, overrides)
    selected_grade = preset.grade if grade is None else get_pencil_preset(grade).name
    selected_terminal = preset.terminal_mode if terminal_mode is None else str(terminal_mode).strip().lower()
    if selected_terminal not in TERMINAL_MODES:
        raise ValueError(f"unknown terminal mode: {selected_terminal!r}")

    return ResolvedMark(
        style_profile=str(style_profile).strip().lower(),
        semantic_role=role,
        material_policy=material_policy_for_style(style_profile, explicit=material_policy),
        tool_preset_id=preset.preset_id,
        tool_preset_revision=preset.revision,
        runtime_tool=preset.base_tool,
        grade=selected_grade,
        terminal_mode=selected_terminal,
        tool_overrides=overrides,
        resolved_tool_state={**resolved.to_dict(), "pencil_grade": selected_grade},
    )


def resolve_mark_for_intent(intent: Any, semantic_role: str, **kwargs: Any) -> ResolvedMark:
    """Resolve from any public intent-like object that exposes ``style_profile``."""

    try:
        style_profile = intent.style_profile
    except AttributeError as exc:
        raise TypeError("intent must expose style_profile") from exc
    return resolve_markmaking(str(style_profile), semantic_role, **kwargs)


__all__ = [
    "MARKMAKING_SCHEMA",
    "MATERIAL_POLICIES",
    "MATERIAL_POLICY_REVISION",
    "SEMANTIC_STROKE_ROLES",
    "TERMINAL_MODES",
    "TOOL_PRESETS",
    "TOOL_PRESET_REVISION",
    "MaterialPolicy",
    "ResolvedMark",
    "ToolPreset",
    "material_policy_for_style",
    "resolve_mark_for_intent",
    "resolve_markmaking",
]
