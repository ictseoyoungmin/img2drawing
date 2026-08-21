__version__ = "0.5.2.dev22"
RELEASE_REVISION = "R22"
RELEASE_SLICE = "R22_fresh_worker_defect_closure_subject_only"

_BASE_VERSION = __version__.split(".dev")[0]
PUBLIC_API = f"DrawingRun/{_BASE_VERSION}-{RELEASE_REVISION.lower()}"
DEFAULT_SESSION_ID = f"img2drawing-{_BASE_VERSION.replace('.', '')}-{RELEASE_REVISION.lower()}"
