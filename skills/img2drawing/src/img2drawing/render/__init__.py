"""The pencil renderer. Rendering is a material concern, never semantic authority.

``render()`` turns authored stroke IR into graphite on paper. ``DrawingSession`` binds every
render to a persisted ``RenderProfile`` whose renderer identity and contract digest must match
``RENDERER_ID`` / ``RENDERER_VERSION`` / ``RENDERER_CONTRACT_DIGEST``; workers render through the
session rather than calling this module directly.
"""

from .contract import (
    PENCIL_CONTRACT,
    RENDERER_CONTRACT_DIGEST,
    RENDERER_ID,
    RENDERER_VERSION,
    UnsupportedRendererError,
    canonical_identity,
    verify_contract_digest,
)
from .grades import default_grade_name, get_pencil_preset, list_pencil_grades
from .paper import DEFAULT_PAPER_SCALE, DEFAULT_PAPER_SEED, DEFAULT_PAPER_TOOTH
from .pencil import (
    DEFAULT_SUPERSAMPLE,
    HIGH_QUALITY_SUPERSAMPLE,
    build_patch,
    is_eraser,
    load_contact_profile,
    prepare_stroke,
    render,
    render_image,
)

__all__ = [
    "DEFAULT_PAPER_SCALE",
    "DEFAULT_PAPER_SEED",
    "DEFAULT_PAPER_TOOTH",
    "DEFAULT_SUPERSAMPLE",
    "HIGH_QUALITY_SUPERSAMPLE",
    "PENCIL_CONTRACT",
    "RENDERER_CONTRACT_DIGEST",
    "RENDERER_ID",
    "RENDERER_VERSION",
    "UnsupportedRendererError",
    "build_patch",
    "canonical_identity",
    "default_grade_name",
    "get_pencil_preset",
    "is_eraser",
    "list_pencil_grades",
    "load_contact_profile",
    "prepare_stroke",
    "render",
    "render_image",
    "verify_contract_digest",
]
