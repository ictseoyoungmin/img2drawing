__version__ = "0.5.2.dev23"
RELEASE_REVISION = "R23"
RELEASE_SLICE = "R23_material_integrated_visual_quality"

_BASE_VERSION = __version__.split(".dev")[0]
PUBLIC_API = f"DrawingRun/{_BASE_VERSION}-{RELEASE_REVISION.lower()}"
DEFAULT_SESSION_ID = f"img2drawing-{_BASE_VERSION.replace('.', '')}-{RELEASE_REVISION.lower()}"
