"""img2drawing: an agent draws with explicit, inspectable pencil strokes.

Normal Agent/user code discovers one orchestration surface: ``DrawingSession`` plus its small
declarative inputs and the observed first-construction facade. Specialized capabilities live in
their owning namespaces:

- ``img2drawing.authoring``: markmaking resolver, retune helpers, curve sampling.
- ``img2drawing.inspection``: measurement, registration, and WIP guide views.
- ``img2drawing.observation``: subject palette sampling.
- ``img2drawing.session``: session record types and schemas (framework/debugging work).
- ``img2drawing.runtime``: source-opaque capability manifest.
"""

from ._version import __version__
from .authoring import (
    ConstructionMark,
    InitialConstruct,
    PoseObservation,
    author_initial_construct,
    inspect_initial_construct,
    observe_pose,
)
from .render.profile import RenderProfile
from .session import (
    DrawingIntent,
    DrawingSession,
    ReferenceAuthority,
    ReferenceConstraint,
    ReferenceUnavailableError,
)

__all__ = [
    "__version__",
    "DrawingSession",
    "DrawingIntent",
    "ReferenceAuthority",
    "ReferenceConstraint",
    "ReferenceUnavailableError",
    "RenderProfile",
    "PoseObservation",
    "InitialConstruct",
    "ConstructionMark",
    "author_initial_construct",
    "inspect_initial_construct",
    "observe_pose",
]
