"""Page-fixed paper relief and deterministic noise fields.

Paper is page state rather than stroke-local tool state: every stroke crossing the same
logical coordinate encounters the same tooth field, independent of raster resolution.
"""

from __future__ import annotations

import numpy as np

from ..core.ir import Stroke, StrokeIR

DEFAULT_PAPER_TOOTH = 0.46
DEFAULT_PAPER_SCALE = 1.0
DEFAULT_PAPER_SEED = 170817


def _clamp01(v: float) -> float:
    return max(0.0, min(1.0, float(v)))


def paper_settings(ir: StrokeIR) -> tuple[float, float, int]:
    """Return the page-level ``(tooth, scale, seed)`` stamped into render IR metadata."""

    meta = ir.metadata if isinstance(ir.metadata, dict) else {}
    paper = meta.get("paper", {}) if isinstance(meta.get("paper", {}), dict) else {}
    tooth = _clamp01(paper.get("tooth", DEFAULT_PAPER_TOOTH))
    scale = max(0.35, min(4.0, float(paper.get("scale", DEFAULT_PAPER_SCALE))))
    seed = int(paper.get("seed", DEFAULT_PAPER_SEED)) & 0xFFFFFFFF
    return tooth, scale, seed


def _hash01(x: np.ndarray, y: np.ndarray, seed: int) -> np.ndarray:
    xx = np.asarray(x, dtype=np.int64).astype(np.uint64)
    yy = np.asarray(y, dtype=np.int64).astype(np.uint64)
    n = (xx * np.uint64(0x9E3779B1) + yy * np.uint64(0x85EBCA77) + np.uint64(seed)) & np.uint64(0xFFFFFFFF)
    n ^= n >> np.uint64(16)
    n = (n * np.uint64(0x7FEB352D)) & np.uint64(0xFFFFFFFF)
    n ^= n >> np.uint64(15)
    n = (n * np.uint64(0x846CA68B)) & np.uint64(0xFFFFFFFF)
    n ^= n >> np.uint64(16)
    return (n & np.uint64(0x00FFFFFF)).astype(np.float32) / np.float32(0x00FFFFFF)


def _smoothstep(x: np.ndarray) -> np.ndarray:
    x = np.clip(x, 0.0, 1.0)
    return x * x * (3.0 - 2.0 * x)


def value_noise(x: np.ndarray, y: np.ndarray, cell: float, seed: int) -> np.ndarray:
    """Deterministic bilinear value noise in logical paper coordinates."""
    cell = max(0.08, float(cell))
    gx = x / cell
    gy = y / cell
    x0 = np.floor(gx).astype(np.int64)
    y0 = np.floor(gy).astype(np.int64)
    tx = _smoothstep(gx - x0)
    ty = _smoothstep(gy - y0)

    a = _hash01(x0, y0, seed)
    b = _hash01(x0 + 1, y0, seed)
    c = _hash01(x0, y0 + 1, seed)
    d = _hash01(x0 + 1, y0 + 1, seed)
    ab = a + (b - a) * tx
    cd = c + (d - c) * tx
    return ab + (cd - ab) * ty


def paper_field(
    shape: tuple[int, int],
    *,
    factor: float,
    global_origin: tuple[int, int],
    paper_scale: float,
    paper_seed: int,
) -> np.ndarray:
    """Sample a fixed multiscale page relief field in [0,1].

    Coordinates are converted back to logical page space before sampling, so the field
    belongs to the page, not to raster resolution or individual strokes.
    """
    hh, ww = int(shape[0]), int(shape[1])
    oy, ox = int(global_origin[1]), int(global_origin[0])
    yy, xx = np.indices((hh, ww), dtype=np.float64)
    lx = (xx + float(ox)) / float(factor)
    ly = (yy + float(oy)) / float(factor)

    s = float(paper_scale)
    coarse = value_noise(lx, ly, 1.85 * s, paper_seed ^ 0xA24BAED4)
    mid = value_noise(lx, ly, 0.72 * s, paper_seed ^ 0x9FB21C65)
    fine = value_noise(lx, ly, 0.29 * s, paper_seed ^ 0xC13FA9A9)

    # A weak anisotropic fibre term stops the field from reading as generic isotropic
    # digital noise. It is still deterministic and fixed in paper coordinates.
    fibre_y = value_noise(lx * 0.22, ly, 0.43 * s, paper_seed ^ 0x91E10DA5)
    fibre_x = value_noise(lx, ly * 0.28, 0.61 * s, paper_seed ^ 0xD1B54A35)

    field = (
        np.float32(0.33) * coarse
        + np.float32(0.34) * mid
        + np.float32(0.20) * fine
        + np.float32(0.08) * fibre_y
        + np.float32(0.05) * fibre_x
    )
    return np.clip(field, 0.0, 1.0).astype(np.float32)


def pixel_hash_tooth(lx: np.ndarray, ly: np.ndarray, seed: int = 7) -> np.ndarray:
    """Per-logical-pixel graphite tooth: a fine hash blended with a 3x3-cell coarse hash."""

    x = np.floor(lx).astype(np.uint32)
    y = np.floor(ly).astype(np.uint32)

    def h2(xx, yy, s):
        with np.errstate(over="ignore"):
            n = xx * np.uint32(374761393) + yy * np.uint32(668265263) + np.uint32(s & 4294967295) * np.uint32(1274126177)
            n = (n ^ n >> np.uint32(13)) * np.uint32(1274126177)
            n = n ^ n >> np.uint32(16)
        return n.astype(np.float32) / np.float32(4294967295.0)

    fine = h2(x, y, seed)
    coarse = h2(x // np.uint32(3), y // np.uint32(3), seed + 991)
    return np.clip(np.float32(0.45) * fine + np.float32(0.55) * coarse, 0.0, 1.0)


def mean_stroke_pressure(stroke: Stroke) -> float:
    if stroke.pressure is not None and len(stroke.pressure) == len(stroke.points) and stroke.pressure:
        return _clamp01(float(np.mean(np.asarray(stroke.pressure, dtype=np.float32))))
    ts = stroke.tool_state if isinstance(stroke.tool_state, dict) else {}
    return _clamp01(ts.get("pressure", 0.55))


__all__ = [
    "DEFAULT_PAPER_SCALE",
    "DEFAULT_PAPER_SEED",
    "DEFAULT_PAPER_TOOTH",
    "mean_stroke_pressure",
    "paper_field",
    "paper_settings",
    "pixel_hash_tooth",
    "value_noise",
]
