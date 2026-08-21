"""Rendering is a material concern, never semantic authority."""
from .pillow_pencil_contact import render as render_pencil, RENDERER_ID
from .presets import get_pencil_preset, list_pencil_grades
from .scale_guidance import CanvasScaleGuidance, canvas_scale_guidance
__all__ = ["render_pencil", "RENDERER_ID", "get_pencil_preset", "list_pencil_grades", "CanvasScaleGuidance", "canvas_scale_guidance"]

from .line_weight import LineWeightProfile, profile_from_reference, calibrate_line_weight
