"""Explicit normalized arc-length contact diameter controls (opt-in renderer)."""
from __future__ import annotations

from bisect import bisect_right
from collections.abc import Mapping
from dataclasses import dataclass
import math

WIDTH_KEY = "img2drawing_contact_width"
WIDTH_SCHEMA = "img2drawing.contact_width.v1"


@dataclass(frozen=True)
class ContactWidthProfile:
    """Multipliers of the resolved diameter, independent of authored pressure.

    Knots span the full normalized path. A factor of one preserves the
    ordinary maximum contact; smaller values narrow it. No extrapolation.
    """
    knots: tuple[tuple[float, float], ...]

    def __post_init__(self):
        raw = tuple(tuple(pair) for pair in self.knots)
        if not 2 <= len(raw) <= 64 or any(len(k)!=2 or any(type(v) not in (int,float) for v in k) for k in raw):
            raise ValueError("contact width requires 2–64 numeric knot pairs")
        k = tuple(tuple(map(float, p)) for p in raw)
        if (any(not math.isfinite(t) or not math.isfinite(w) or not 0<=t<=1 or not .15<=w<=1 for t,w in k)
                or k[0][0]!=0 or k[-1][0]!=1 or any(a[0]>=b[0] for a,b in zip(k,k[1:]))):
            raise ValueError("contact width knots must increase from 0 to 1 with factors in [.15,1]")
        object.__setattr__(self, "knots", k)

    def to_dict(self):
        return {"schema": WIDTH_SCHEMA, "knots": [list(p) for p in self.knots]}

    @classmethod
    def from_dict(cls, raw):
        if not isinstance(raw, Mapping) or set(raw)!={"schema","knots"} or raw["schema"]!=WIDTH_SCHEMA:
            raise ValueError("unsupported contact width profile")
        try:
            return cls(raw["knots"])
        except TypeError as exc:
            raise ValueError("invalid contact width knots") from exc

    def metadata(self, existing=None):
        result = dict(existing or {})
        if WIDTH_KEY in result:
            raise ValueError("contact width metadata already present")
        result[WIDTH_KEY] = self.to_dict()
        return result

    def at(self, t):
        t=float(t)
        if not math.isfinite(t) or not 0<=t<=1:
            raise ValueError("normalized path position must lie in [0,1]")
        i = min(len(self.knots)-2, bisect_right([p[0] for p in self.knots],t)-1)
        (a,u),(b,v)=self.knots[i:i+2]
        return min(1.,max(.15,u+(v-u)*(t-a)/(b-a)))

    def interval(self, start, end):
        """Restrict and renormalize a chosen interval for a stroke split."""
        if not 0<=start<end<=1:
            raise ValueError("contact width interval must be nonempty inside [0,1]")
        return ContactWidthProfile(((0.,self.at(start)),
            *(( (t-start)/(end-start), w) for t,w in self.knots if start<t<end),
            (1.,self.at(end))))


def profile_from_metadata(metadata):
    if isinstance(metadata, Mapping) and WIDTH_KEY in metadata:
        return ContactWidthProfile.from_dict(metadata[WIDTH_KEY])
    return None


def profile_from_stroke(stroke):
    state = stroke.tool_state or {}
    return profile_from_metadata((state.get("provenance") or {}).get("metadata"))


def read_contact_width_profile(session, stroke_id):
    """Read the current width recipe; absent metadata means ordinary contact."""
    return profile_from_stroke(session.current_stroke(stroke_id))
