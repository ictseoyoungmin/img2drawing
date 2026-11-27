"""Bounded local opaque-ink patches for explicit authored geometry.

No session API or profile registration here. The future mixed compositor owns
ordering, supersample reduction, selective lifting and replay. Both path and area
kernels evaluate coverage on the same supersampled pixel-centre grid; ink is
composited once, not deposited repeatedly as graphite.
"""
from __future__ import annotations

import math

import numpy as np
from PIL import Image

from ..core.material import InkArea, InkPath

INK_KERNEL_REVISION = "opaque-swept-disks-even-odd-v1"
MAX_PATCH_PIXELS = 16 * 1024 * 1024
MAX_KERNEL_WORK = 64 * 1024 * 1024
MAX_SEGMENTS = 65536
MAX_SLAB_PIXELS = 262144
MAX_FACTOR = 16
_SEGMENT_SPAN = 64.0


def _grid(factor, hi_size):
    if (type(factor) not in (float, int) or not math.isfinite(factor)
            or not 1 <= factor <= MAX_FACTOR or int(factor) != factor):
        raise ValueError("ink factor must be a bounded positive integer")
    if (not isinstance(hi_size, (tuple, list)) or len(hi_size) != 2
            or any(type(v) is not int or not 1 <= v <= 1048576 for v in hi_size)):
        raise ValueError("invalid ink working canvas size")
    return float(factor), tuple(hi_size)


def _box(x0, y0, x1, y1, size):
    w, h = size
    return (max(0, min(w, math.floor(x0))), max(0, min(h, math.floor(y0))),
            max(0, min(w, math.ceil(x1))), max(0, min(h, math.ceil(y1))))


def _pixels(b):
    return max(0, b[2] - b[0]) * max(0, b[3] - b[1])


def _union(a, b):
    return (min(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3]))


def _empty():
    return (0, 0, 0, 0), Image.new("RGBA", (1, 1), (0, 0, 0, 0))


def _path_plan(mark, factor, size):
    points = tuple((x * factor, y * factor) for x, y in mark.points)
    radii = tuple(w * factor * 0.5 for w in mark.diameters())
    jobs = []
    bounds = None
    work = count = 0
    for a, b, r0, r1 in zip(points, points[1:], radii, radii[1:]):
        if max(r0, r1) == 0:
            continue
        # Split long segments for local work, not geometry approximation.
        # Linear radius interpolation is unchanged by this partition.
        n = max(1, math.ceil(math.dist(a, b) / max(_SEGMENT_SPAN, 2 * max(r0, r1))))
        count += n
        if count > MAX_SEGMENTS:
            raise ValueError("ink segment budget exceeded")
        dx, dy, dr = b[0] - a[0], b[1] - a[1], r1 - r0
        for i in range(n):
            t, u = i / n, (i + 1) / n
            x, y, radius = a[0] + t * dx, a[1] + t * dy, r0 + t * dr
            xx, yy, end_radius = a[0] + u * dx, a[1] + u * dy, r0 + u * dr
            bb = _box(min(x - radius, xx - end_radius), min(y - radius, yy - end_radius),
                      max(x + radius, xx + end_radius), max(y + radius, yy + end_radius), size)
            cells = _pixels(bb)
            if not cells:
                continue
            work += cells
            bounds = bb if bounds is None else _union(bounds, bb)
            if work > MAX_KERNEL_WORK or _pixels(bounds) > MAX_PATCH_PIXELS:
                raise ValueError("ink patch or work budget exceeded")
            jobs.append((bb, x, y, xx - x, yy - y, radius, end_radius - radius))
    return bounds, jobs


def _path_mask(bounds, jobs):
    x0, y0, x1, y1 = bounds
    mask = np.zeros((y1 - y0, x1 - x0), dtype=np.uint8)
    for (xa, ya, xb, yb), x, y, dx, dy, r, dr in jobs:
        # Minimum of |sample - centre(t)|^2 - radius(t)^2 on t in [0,1].
        # If the quadratic is concave, an endpoint attains its minimum
        # (including the containing-disk case). Otherwise use its stationary point.
        a = dx * dx + dy * dy - dr * dr
        xs = np.arange(xa, xb, dtype=np.float64)[None, :] + 0.5 - x
        rows = max(1, MAX_SLAB_PIXELS // (xb - xa))
        for lo in range(ya, yb, rows):
            hi = min(yb, lo + rows)
            ys = np.arange(lo, hi, dtype=np.float64)[:, None] + 0.5 - y
            b = xs * dx + ys * dy + r * dr
            c = xs * xs + ys * ys - r * r
            if a > 0.0:
                t = np.clip(b / a, 0.0, 1.0)
                f = c - 2.0 * b * t + a * t * t
            else:
                f = np.minimum(c, c - 2.0 * b + a)
            dest = mask[lo - y0:hi - y0, xa - x0:xb - x0]
            dest[f <= 0.0] = 255  # set union, never alpha accumulation
    return mask


def _area_plan(mark, factor, size):
    rings = tuple(tuple((x * factor, y * factor) for x, y in ring)
                  for ring in (mark.outer, *mark.holes))
    bounds = _box(min(x for x, _ in rings[0]), min(y for _, y in rings[0]),
                  max(x for x, _ in rings[0]), max(y for _, y in rings[0]), size)
    if _pixels(bounds) > MAX_PATCH_PIXELS:
        raise ValueError("ink patch budget exceeded")
    starts, ends = {}, {}
    work = 0
    for ring in rings:
        for p, q in zip(ring, ring[1:]):
            if p[1] == q[1]:
                continue
            a, b = (p, q) if p[1] < q[1] else (q, p)
            first = max(bounds[1], math.ceil(a[1] - 0.5))
            stop = min(bounds[3], math.ceil(b[1] - 0.5))
            if stop <= first:
                continue
            work += stop - first
            if work > MAX_KERNEL_WORK:
                raise ValueError("ink area work budget exceeded")
            edge = (a[0], a[1], (b[0] - a[0]) / (b[1] - a[1]))
            # Edge IDs avoid conflating coincident line equations.
            key = (first, stop, len(starts.get(first, ())))
            starts.setdefault(first, []).append((key, edge))
            ends.setdefault(stop, []).append(key)
    return bounds, starts, ends


def _area_mask(bounds, starts, ends):
    x0, y0, x1, y1 = bounds
    mask = np.zeros((y1 - y0, x1 - x0), dtype=np.uint8)
    active = {}
    for y in range(y0, y1):
        for key in ends.get(y, ()):
            active.pop(key)
        active.update(starts.get(y, ()))
        # Half-open crossing convention: lower Y included, upper Y excluded;
        # horizontal edges do not cross the scanline. Outer and holes share parity.
        xs = sorted(x + (y + 0.5 - edge_y) * slope for x, edge_y, slope in active.values())
        if len(xs) % 2:
            raise ValueError("invalid ink area crossing parity")
        for left, right in zip(xs[::2], xs[1::2]):
            lo = max(x0, math.ceil(left - 0.5))
            hi = min(x1, math.ceil(right - 0.5))
            if lo < hi:
                mask[y - y0, lo - x0:hi - x0] = 255
    return mask


def build_ink_patch(mark: InkPath | InkArea, *, factor, hi_size):
    """Return clipped (x0,y0,x1,y1), RGBA patch on the working-resolution grid.

    The caller owns the image and closes it. No full canvas or expanded dot
    geometry is created; unsupported work sizes fail before mask allocation.
    """
    factor, size = _grid(factor, hi_size)
    if isinstance(mark, InkPath):
        bounds, jobs = _path_plan(mark, factor, size)
        if bounds is None:
            return _empty()
        mask = _path_mask(bounds, jobs)
    elif isinstance(mark, InkArea):
        bounds, starts, ends = _area_plan(mark, factor, size)
        if not _pixels(bounds):
            return _empty()
        mask = _area_mask(bounds, starts, ends)
    else:
        raise ValueError("unsupported ink geometry")
    value = 0 if mark.paint == "black" else 255
    layer = Image.new("RGBA", (bounds[2] - bounds[0], bounds[3] - bounds[1]), (value, value, value, 0))
    with Image.fromarray(mask) as alpha:
        layer.putalpha(alpha)
    return bounds, layer
