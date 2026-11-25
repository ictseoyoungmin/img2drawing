"""Agent-selected material and projected-geometry observation helpers.

No automatic detection, correspondence, hidden geometry or drawing mutation.
"""

from .palette import MaterialSample, SubjectPalette
from .landmarks import LANDMARK_SCHEMA, Landmark, LandmarkSet, compare_landmarks, compare_ratios
from .spatial import compare_axes, cross_section, compare_negative_space, occlusion_relation

__all__ = [
    "MaterialSample", "SubjectPalette", "LANDMARK_SCHEMA", "Landmark", "LandmarkSet",
    "compare_landmarks", "compare_ratios", "compare_axes", "cross_section",
    "compare_negative_space", "occlusion_relation",
]
