__version__ = "0.5.2.dev23"
RELEASE_REVISION = "R23"
RELEASE_SLICE = "R23_material_integrated_visual_quality"

_BASE_VERSION = __version__.split(".dev")[0]
PUBLIC_API = f"DrawingSession/{_BASE_VERSION}-vnext"
DEFAULT_SESSION_ID = f"img2drawing-{_BASE_VERSION.replace('.', '')}-vnext"

# R23 identifiers remain explicit historical provenance. They must not be used
# to describe the canonical package surface.
LEGACY_R23_PUBLIC_API = f"DrawingRun/{_BASE_VERSION}-{RELEASE_REVISION.lower()}"
LEGACY_R23_DEFAULT_SESSION_ID = (
    f"img2drawing-{_BASE_VERSION.replace('.', '')}-{RELEASE_REVISION.lower()}"
)
