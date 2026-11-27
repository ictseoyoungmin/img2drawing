"""Authoring helpers that feed ``DrawingSession`` without deciding what to draw.

- ``resolve_mark_for_intent`` / ``resolve_markmaking``: semantic mark role and preset →
  public ``DrawingSession.draw`` kwargs with recorded markmaking provenance.
- ``retune_stroke`` / ``retune_strokes``: change material while preserving authored geometry.
- ``sample_catmull_rom``: deterministic smooth sampling for an observed smooth interval.
- ``observe_pose`` / ``author_initial_construct`` / ``inspect_initial_construct``: the
  observed first-construction facade (also exported from the package root).

None of these encode subject-specific geometry; the Agent still observes and authors it.
"""

from ..core.contact_width import ContactWidthProfile, read_contact_width_profile
from ..core.material import InkAction, InkElement, InkPath, InkArea, StyledInkPath
from .ink_edits import apply_ink_actions, preview_ink_actions
from .ink_pen import PenDefinition, g_pen, fineliner, read_pen_definition
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
from .volume import ProjectionCamera, VolumeStation, ProjectedVolume, inspect_attachment, align_attachment, prepare_volume_edits
from .parametric_curve import CurveDefinition, read_parametric_curve
from .projection import ProjectedSection, projected_ellipse, projected_envelope, author_projection_guides
from .sampling import resample_polyline, sample_cubic_bezier, pressure_along_path, curve_join, deform_interval
from .stroke_edits import StrokeEdit, transform_strokes, apply_stroke_edits, preview_stroke_edits
from .semantic_groups import SemanticGroup, record_semantic_groups, inspect_semantic_groups, review_semantic_group, prepare_group_transform, retire_group_guides
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
from .retune import reshape_stroke, retune_stroke, retune_strokes
from .tonal_area import TONAL_AREA_SCHEMA, TonalAreaPlan
from .tonal_preview import inspect_tonal_proposals
from .tonal_correction import TonalPressureAdjustment, prepare_tonal_pressure_edits

__all__ = [
    "InkAction", "InkElement", "InkPath", "InkArea", "StyledInkPath", "apply_ink_actions", "preview_ink_actions",
    "PenDefinition", "g_pen", "fineliner", "read_pen_definition",
    "ContactWidthProfile",
    "read_contact_width_profile",
    "ProjectionCamera", "VolumeStation", "ProjectedVolume", "inspect_attachment", "align_attachment",
    "prepare_volume_edits", "CurveDefinition", "read_parametric_curve",
    "SemanticGroup",
    "record_semantic_groups",
    "inspect_semantic_groups",
    "review_semantic_group",
    "prepare_group_transform",
    "retire_group_guides",
    "inspect_tonal_proposals",
    "TonalPressureAdjustment",
    "prepare_tonal_pressure_edits",
    "resample_polyline",
    "sample_cubic_bezier",
    "pressure_along_path",
    "curve_join",
    "deform_interval",
    "StrokeEdit",
    "transform_strokes",
    "apply_stroke_edits",
    "preview_stroke_edits",
    "ProjectedSection",
    "projected_ellipse",
    "projected_envelope",
    "author_projection_guides",
    "CONSTRUCTION_PHASES",
    "MARKMAKING_SCHEMA",
    "MATERIAL_POLICIES",
    "MATERIAL_POLICY_REVISION",
    "SEMANTIC_STROKE_ROLES",
    "TERMINAL_MODES",
    "TOOL_PRESETS",
    "TOOL_PRESET_REVISION",
    "TONAL_AREA_SCHEMA",
    "TonalAreaPlan",
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
    "reshape_stroke",
    "retune_stroke",
    "retune_strokes",
    "sample_catmull_rom",
]
