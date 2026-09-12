__version__ = "1.0.3rc1"
RELEASE_REVISION = "A11"
RELEASE_SLICE = "v1.0.3rc1_renderer_v10_markmaking_rc"

_BASE_VERSION = __version__.split("rc")[0]
PUBLIC_API = f"DrawingSession/{_BASE_VERSION}-vnext"
DEFAULT_SESSION_ID = f"img2drawing-{_BASE_VERSION.replace('.', '')}-vnext"
