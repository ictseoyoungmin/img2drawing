"""Author a calibrated page-space dot pattern inside explicit closed contours."""
from __future__ import annotations
from ..core.material import Screentone, ToneGradient


def dot_screentone(outer, *, holes=(), pitch=6., coverage=None, angle_degrees=0.,
                   phase_origin=(0.,0.), gradient=None):
    """Return one editable mark; provide exactly one coverage or ToneGradient.

    All distances are logical canvas pixels. The phase origin is a dot centre
    in page coordinates. Angle is clockwise on the y-down page. Holes reveal
    underlying marks. No source images, masks, or generated dot strokes.
    """
    return Screentone(outer,holes,"black",pitch,coverage,angle_degrees,phase_origin,gradient)


__all__=["Screentone","ToneGradient","dot_screentone"]
