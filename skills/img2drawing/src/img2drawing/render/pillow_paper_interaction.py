from __future__ import annotations


import numpy as np
from PIL import Image

from ..core.ir import Stroke, StrokeIR
from . import pillow_graphite_grain as p3
from . import pillow_hand_dynamics as p4

RENDERER_ID = "pillow-paper-interaction-v6"
RENDERER_VERSION = "1"
DEFAULT_SUPERSAMPLE = 8
DEFAULT_PAPER_TOOTH = 0.46
DEFAULT_PAPER_SCALE = 1.0
DEFAULT_PAPER_SEED = 170817


def _clamp01(v: float) -> float:
    return max(0.0, min(1.0, float(v)))


def _paper_settings(ir: StrokeIR) -> tuple[float, float, int]:
    """Return persisted page-level paper settings.

    Paper is deliberately page state rather than stroke-local tool state.  Every stroke
    crossing the same logical coordinate must encounter the same tooth field.
    """
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


def _value_noise(x: np.ndarray, y: np.ndarray, cell: float, seed: int) -> np.ndarray:
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

    Coordinates are converted back to logical page space before sampling.  The field
    therefore belongs to the page, not to raster resolution or individual strokes.
    """
    hh, ww = int(shape[0]), int(shape[1])
    oy, ox = int(global_origin[1]), int(global_origin[0])
    yy, xx = np.indices((hh, ww), dtype=np.float64)
    lx = (xx + float(ox)) / float(factor)
    ly = (yy + float(oy)) / float(factor)

    s = float(paper_scale)
    coarse = _value_noise(lx, ly, 1.85 * s, paper_seed ^ 0xA24BAED4)
    mid = _value_noise(lx, ly, 0.72 * s, paper_seed ^ 0x9FB21C65)
    fine = _value_noise(lx, ly, 0.29 * s, paper_seed ^ 0xC13FA9A9)

    # A weak anisotropic fibre term stops the field from reading as generic isotropic
    # digital noise.  It is still deterministic and fixed in paper coordinates.
    fibre_y = _value_noise(lx * 0.22, ly, 0.43 * s, paper_seed ^ 0x91E10DA5)
    fibre_x = _value_noise(lx, ly * 0.28, 0.61 * s, paper_seed ^ 0xD1B54A35)

    field = (
        np.float32(0.33) * coarse
        + np.float32(0.34) * mid
        + np.float32(0.20) * fine
        + np.float32(0.08) * fibre_y
        + np.float32(0.05) * fibre_x
    )
    # Normalize a known theoretical-ish range into a restrained 0..1 contact relief.
    return np.clip(field, 0.0, 1.0).astype(np.float32)


def _stroke_pressure(stroke: Stroke) -> float:
    if stroke.pressure is not None and len(stroke.pressure) == len(stroke.points) and stroke.pressure:
        return _clamp01(float(np.mean(np.asarray(stroke.pressure, dtype=np.float32))))
    ts = stroke.tool_state if isinstance(stroke.tool_state, dict) else {}
    return _clamp01(ts.get("pressure", 0.55))


def _paper_modulate(
    mask: Image.Image,
    *,
    stroke: Stroke,
    tooth: float,
    paper_scale: float,
    paper_seed: int,
    factor: float,
    global_origin: tuple[int, int],
) -> Image.Image:
    """Modulate only deposited graphite with fixed page tooth.

    Background pixels are untouched.  Higher pressure fills valleys more strongly;
    harder cores retain slightly more tooth contrast.  Mean deposition over the active
    footprint is preserved so paper tooth does not silently become another opacity knob.
    """
    t = _clamp01(tooth)
    if t <= 1e-8:
        return mask

    arr = np.asarray(mask, dtype=np.float32)
    active = arr > 0.5
    if not np.any(active):
        return mask

    ts = stroke.tool_state if isinstance(stroke.tool_state, dict) else {}
    hardness = _clamp01(ts.get("hardness", p3.DEFAULT_HARDNESS))
    pressure = _stroke_pressure(stroke)

    field = paper_field(
        arr.shape,
        factor=factor,
        global_origin=global_origin,
        paper_scale=paper_scale,
        paper_seed=paper_seed,
    )
    relief = (field - np.float32(0.5)) * np.float32(2.0)

    # Low-pressure hard pencils ride the peaks most strongly; high pressure and softer
    # graphite reach into valleys, reducing but never fully eliminating paper signature.
    contact = np.float32((0.52 + 0.56 * hardness) * (1.0 - 0.56 * pressure))
    strength = np.float32(1.18 * t) * contact
    mod = np.float32(1.0) + strength * relief

    # Deep paper valleys can locally fail to take graphite at light touch.  Because this
    # uses the same fixed page field for every pass, repeated explicit strokes gradually
    # fill those valleys by normal alpha compositing rather than randomized redraw noise.
    valley_cut = np.float32(0.23 + 0.12 * t - 0.11 * pressure)
    deep_valley = field < valley_cut
    valley_factor = np.float32(0.46 + 0.34 * pressure + 0.08 * (1.0 - hardness))
    mod = np.where(deep_valley, mod * valley_factor, mod)

    mean_mod = float(np.mean(mod[active]))
    if mean_mod > 1e-6:
        mod = mod / np.float32(mean_mod)
    mod = np.clip(mod, np.float32(0.20), np.float32(1.55))

    out = np.clip(arr * mod, 0.0, 255.0).astype(np.uint8)
    return Image.fromarray(out, mode="L")


def render(
    ir: StrokeIR,
    path: str,
    background=(255, 255, 255, 255),
    *,
    scale: int = 1,
    supersample: int = DEFAULT_SUPERSAMPLE,
    graphite=(36, 34, 32),
) -> None:
    """Render P1–P4 material semantics plus P5 page-fixed paper interaction.

    P5 adds only page-level tooth during deposition. It does not shade/noise the blank
    paper raster, does not define named pencil grades (P6), and does not alter erasing
    semantics (P7).
    """
    if int(scale) != scale or scale < 1:
        raise ValueError("scale must be a positive integer")
    if int(supersample) != supersample or supersample < 2:
        raise ValueError("supersample must be an integer >= 2")
    scale = int(scale)
    supersample = int(supersample)

    tooth, paper_scale, paper_seed = _paper_settings(ir)
    if tooth <= 1e-12:
        # Exact delegation is the P5 compatibility gate.
        p4.render(ir, path, background=background, scale=scale, supersample=supersample, graphite=graphite)
        return

    # P4 derives hand motion in logical coordinates without mutating authoritative IR.
    dynamic = p4.dynamic_ir(ir)
    factor = float(scale * supersample)
    hi_size = (int(dynamic.width * factor), int(dynamic.height * factor))
    out_size = (dynamic.width * scale, dynamic.height * scale)

    base = Image.new("RGBA", hi_size, background)
    for stroke in sorted(dynamic.strokes, key=lambda z: z.layer):
        if len(stroke.points) < 2:
            continue
        grain, hardness = p3._material(stroke)
        bounds = p3._stroke_bounds(stroke, factor, hardness, hi_size)
        mask = p3._render_base_mask_local(stroke, factor, hardness, bounds)
        mask = p3._grain_modulate(
            mask,
            grain=grain,
            hardness=hardness,
            factor=factor,
            global_origin=(bounds[0], bounds[1]),
            seed=p3._stroke_seed(stroke),
        )
        mask = _paper_modulate(
            mask,
            stroke=stroke,
            tooth=tooth,
            paper_scale=paper_scale,
            paper_seed=paper_seed,
            factor=factor,
            global_origin=(bounds[0], bounds[1]),
        )
        layer = p3._graphite_layer(mask.size, mask, graphite=graphite)
        base.alpha_composite(layer, dest=(bounds[0], bounds[1]))

    final = base.resize(out_size, Image.Resampling.LANCZOS)
    p = str(path)
    if p.lower().endswith((".jpg", ".jpeg")):
        final.convert("RGB").save(p, quality=95)
    else:
        final.save(p)
