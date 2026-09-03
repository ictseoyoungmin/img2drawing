"""R23 compatibility implementation for historical structural registration checks.

Registration is not an instruction-graph lifecycle node. Current stage-free alignment and
measurement capability is owned by :mod:`img2drawing.inspection`; the subject-specific
comparison contracts exported here remain for explicit R23 compatibility until retirement.
"""

from .model import RegistrationLandmark, RegistrationConnection, RegistrationGraph
from .grid import GridSpec
from .compare import StructuralComparison, compare_registrations, RegistrationIntegrityError
from .human import make_human_pose_registration
from .envelope import (
    EnvelopeStation, RegionEnvelopeObservation, RegionEnvelopeIntegrityError,
    EnvelopeIntegrity, AxisEnvelopeEvidence, StationEnvelopeEvidence,
    RegionGeometryComparison, compare_region_envelopes,
)
from .orientation import (
    TorsoOrientationObservation, TorsoOrientationIntegrityError,
    TorsoOrientationComparison, compare_torso_orientation,
)
from .lower_body import (
    LowerBodyObservation, LowerBodyIntegrityError, LowerBodyComparison,
    compare_lower_body,
)
from .head_hair import (
    HeadHairObservation, HeadHairIntegrityError, HeadHairComparison,
    compare_head_hair,
)
from .prop_topology import (
    PropWidthChangePoint, PropTerminalMass, PropBodyOverlapPoint,
    PropTopologyObservation, PropTopologyIntegrityError,
    PropTopologyComparison, compare_prop_topology,
)
__all__=["RegistrationLandmark","RegistrationConnection","RegistrationGraph","GridSpec",
         "StructuralComparison","compare_registrations","RegistrationIntegrityError","make_human_pose_registration",
         "EnvelopeStation","RegionEnvelopeObservation","RegionEnvelopeIntegrityError",
         "EnvelopeIntegrity","AxisEnvelopeEvidence","StationEnvelopeEvidence",
         "RegionGeometryComparison","compare_region_envelopes",
         "TorsoOrientationObservation","TorsoOrientationIntegrityError",
         "TorsoOrientationComparison","compare_torso_orientation",
         "LowerBodyObservation","LowerBodyIntegrityError","LowerBodyComparison",
         "compare_lower_body",
         "HeadHairObservation","HeadHairIntegrityError","HeadHairComparison",
         "compare_head_hair",
         "PropWidthChangePoint","PropTerminalMass","PropBodyOverlapPoint",
         "PropTopologyObservation","PropTopologyIntegrityError",
         "PropTopologyComparison","compare_prop_topology"]
