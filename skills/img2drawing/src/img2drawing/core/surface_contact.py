"""Explicit side-of-pencil contact, not a region fill or inferred material."""
from dataclasses import dataclass
from collections.abc import Mapping
import math

SURFACE_KEY = "img2drawing_surface_contact"
SURFACE_SCHEMA = "img2drawing.surface_contact.v1"


@dataclass(frozen=True)
class SurfaceContactProfile:
    """Fraction of transverse radius allocated to a smooth graphite shoulder.

    The remaining central interval has constant optical depth on a straight pass.
    Width and pressure still come from the ordinary authored stroke.
    """
    shoulder: float = .65

    def __post_init__(self):
        if (type(self.shoulder) not in (int, float) or not math.isfinite(self.shoulder)
                or not .35 <= self.shoulder <= .85):
            raise ValueError("surface contact shoulder must lie in [.35,.85]")
        object.__setattr__(self, "shoulder", float(self.shoulder))

    def to_dict(self):
        return {"schema": SURFACE_SCHEMA, "shoulder": self.shoulder}

    @classmethod
    def from_dict(cls, raw):
        if not isinstance(raw, Mapping) or set(raw) != {"schema", "shoulder"} or raw["schema"] != SURFACE_SCHEMA:
            raise ValueError("unsupported surface contact profile")
        return cls(raw["shoulder"])

    def metadata(self, existing=None):
        result = dict(existing or {})
        if SURFACE_KEY in result:
            raise ValueError("surface contact metadata already present")
        result[SURFACE_KEY] = self.to_dict()
        return result


def surface_from_metadata(metadata):
    if isinstance(metadata, Mapping) and SURFACE_KEY in metadata:
        return SurfaceContactProfile.from_dict(metadata[SURFACE_KEY])
    return None


def surface_from_stroke(stroke):
    return surface_from_metadata(((stroke.tool_state or {}).get("provenance") or {}).get("metadata"))


def read_surface_contact_profile(session, stroke_id):
    return surface_from_stroke(session.current_stroke(stroke_id))
