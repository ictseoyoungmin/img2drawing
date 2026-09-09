__version__ = "1.0.2"
RELEASE_REVISION = "A10"
RELEASE_SLICE = "v1.0.2_local_first_exact_timelapse"

_BASE_VERSION = __version__.split("rc")[0]
PUBLIC_API = f"DrawingSession/{_BASE_VERSION}-vnext"
DEFAULT_SESSION_ID = f"img2drawing-{_BASE_VERSION.replace('.', '')}-vnext"
