"""Authoring helpers that feed ``DrawingSession`` without deciding what to draw.

- ``resolve_mark_for_intent`` / ``resolve_markmaking``: semantic mark role and preset →
  public ``DrawingSession.draw`` kwargs with recorded markmaking provenance.
- ``retune_stroke`` / ``retune_strokes``: change material while preserving authored geometry.
- ``sample_catmull_rom``: deterministic smooth sampling for an observed smooth interval.
- ``observe_pose`` / ``author_initial_construct`` / ``inspect_initial_construct``: the
  observed first-construction facade (also exported from the package root).

None of these encode subject-specific geometry; the Agent still observes and authors it.
"""

from .construction import (
    CONSTRUCTION_PHASES,
    ConstructionMark,
    InitialConstruct,
    InitialConstructResult,
    PoseObservation,
    author_initial_construct,
    inspect_initial_construct,
    observe_pose,
)
from .curves import sample_catmull_rom
from .markmaking import (
    MARKMAKING_SCHEMA,
    MATERIAL_POLICIES,
    MATERIAL_POLICY_REVISION,
    SEMANTIC_STROKE_ROLES,
    TERMINAL_MODES,
    TOOL_PRESET_REVISION,
    TOOL_PRESETS,
    MaterialPolicy,
    ResolvedMark,
    ToolPreset,
    material_policy_for_style,
    resolve_mark_for_intent,
    resolve_markmaking,
)
from .retune import retune_stroke, retune_strokes

__all__ = [
    "CONSTRUCTION_PHASES",
    "MARKMAKING_SCHEMA",
    "MATERIAL_POLICIES",
    "MATERIAL_POLICY_REVISION",
    "SEMANTIC_STROKE_ROLES",
    "TERMINAL_MODES",
    "TOOL_PRESETS",
    "TOOL_PRESET_REVISION",
    "ConstructionMark",
    "InitialConstruct",
    "InitialConstructResult",
    "MaterialPolicy",
    "PoseObservation",
    "ResolvedMark",
    "ToolPreset",
    "author_initial_construct",
    "inspect_initial_construct",
    "material_policy_for_style",
    "observe_pose",
    "resolve_mark_for_intent",
    "resolve_markmaking",
    "retune_stroke",
    "retune_strokes",
    "sample_catmull_rom",
]
