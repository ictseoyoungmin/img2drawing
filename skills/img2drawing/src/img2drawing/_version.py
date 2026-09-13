__version__ = "1.0.3rc3"
RELEASE_REVISION = "A13"
RELEASE_SLICE = "v1.0.3rc3_broad_pencil_material"

_BASE_VERSION = __version__.split("rc")[0]
PUBLIC_API = f"DrawingSession/{_BASE_VERSION}-vnext"
DEFAULT_SESSION_ID = f"img2drawing-{_BASE_VERSION.replace('.', '')}-vnext"
