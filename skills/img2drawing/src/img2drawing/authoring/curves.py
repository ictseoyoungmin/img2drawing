"""Deterministic smooth-curve sampling shared by authoring helpers."""

from __future__ import annotations

from math import hypot
from typing import Sequence


def sample_catmull_rom(
    control_points: Sequence[Sequence[float]],
    *,
    spacing: float = 3.0,
    samples_per_segment: int = 24,
    closed: bool = False,
) -> list[tuple[float, float]]:
    """Sample a deterministic Catmull-Rom curve and resample it by approximate arc length.

    Use this only for a continuously smooth observed interval. Corners, cusps, tangency breaks,
    component joins, and other real topology changes should be split into separate curve/stroke
    intervals instead of being smoothed through by the sampler.
    """

    points = [(float(p[0]), float(p[1])) for p in control_points]
    if len(points) < 2:
        raise ValueError("sample_catmull_rom requires at least two control points")
    if spacing <= 0:
        raise ValueError("spacing must be positive")
    dense_n = int(samples_per_segment)
    if dense_n < 4:
        raise ValueError("samples_per_segment must be >= 4")

    if len(points) == 2:
        dense = [points[0], points[1]]
    else:
        if closed:
            padded = [points[-1], *points, points[0], points[1]]
            segment_count = len(points)
        else:
            padded = [points[0], *points, points[-1]]
            segment_count = len(points) - 1

        dense: list[tuple[float, float]] = [points[0]]
        for segment in range(segment_count):
            p0, p1, p2, p3 = padded[segment : segment + 4]
            for sample in range(1, dense_n + 1):
                t = sample / dense_n
                t2 = t * t
                t3 = t2 * t
                x = 0.5 * (
                    2.0 * p1[0]
                    + (-p0[0] + p2[0]) * t
                    + (2.0 * p0[0] - 5.0 * p1[0] + 4.0 * p2[0] - p3[0]) * t2
                    + (-p0[0] + 3.0 * p1[0] - 3.0 * p2[0] + p3[0]) * t3
                )
                y = 0.5 * (
                    2.0 * p1[1]
                    + (-p0[1] + p2[1]) * t
                    + (2.0 * p0[1] - 5.0 * p1[1] + 4.0 * p2[1] - p3[1]) * t2
                    + (-p0[1] + 3.0 * p1[1] - 3.0 * p2[1] + p3[1]) * t3
                )
                dense.append((x, y))

    if closed and dense[-1] != dense[0]:
        dense.append(dense[0])

    cumulative = [0.0]
    for a, b in zip(dense, dense[1:]):
        cumulative.append(cumulative[-1] + hypot(b[0] - a[0], b[1] - a[1]))
    total = cumulative[-1]
    if total == 0.0:
        return [dense[0], dense[-1]]

    targets: list[float] = [0.0]
    cursor = float(spacing)
    while cursor < total:
        targets.append(cursor)
        cursor += float(spacing)
    targets.append(total)

    out: list[tuple[float, float]] = []
    dense_index = 0
    for target in targets:
        while dense_index + 1 < len(cumulative) and cumulative[dense_index + 1] < target:
            dense_index += 1
        if dense_index + 1 >= len(dense):
            out.append(dense[-1])
            continue
        a = dense[dense_index]
        b = dense[dense_index + 1]
        lo = cumulative[dense_index]
        hi = cumulative[dense_index + 1]
        ratio = 0.0 if hi == lo else (target - lo) / (hi - lo)
        out.append((a[0] + (b[0] - a[0]) * ratio, a[1] + (b[1] - a[1]) * ratio))

    out[0] = dense[0]
    out[-1] = dense[-1]
    return out


__all__ = ["sample_catmull_rom"]
