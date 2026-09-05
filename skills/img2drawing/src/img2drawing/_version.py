__version__ = "1.0.0"
RELEASE_REVISION = "A8"
RELEASE_SLICE = "v1.0.0_stable_demo_baseline"

_BASE_VERSION = __version__.split("rc")[0]
PUBLIC_API = f"DrawingSession/{_BASE_VERSION}-vnext"
DEFAULT_SESSION_ID = f"img2drawing-{_BASE_VERSION.replace('.', '')}-vnext"

# R23 identifiers remain explicit historical provenance. They must not be used
# to describe the canonical package surface.
LEGACY_R23_PUBLIC_API = "DrawingRun/0.5.2-r23"
LEGACY_R23_DEFAULT_SESSION_ID = (
    "img2drawing-052-r23"
)
