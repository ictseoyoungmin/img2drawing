__version__ = "1.0.4rc1"
RELEASE_REVISION = "A15"
RELEASE_SLICE = "v1.0.4rc1_terminal_mode_pixels"

_BASE_VERSION = __version__.split("rc")[0]
PUBLIC_API = f"DrawingSession/{_BASE_VERSION}-vnext"
DEFAULT_SESSION_ID = f"img2drawing-{_BASE_VERSION.replace('.', '')}-vnext"
