from __future__ import annotations
from copy import deepcopy
from math import pi
from pathlib import Path
import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter
from ..core.ir import Stroke, StrokeIR
from .contact_profile import PencilContactProfile, load_pencil_contact_profile
from . import pillow_graphite_grain as p3
from . import pillow_hand_dynamics as p4
from . import pillow_paper_interaction as p5
from . import pillow_pencil_grades as p6
from . import pillow_eraser_material as p7
from .renderer_contracts import V10_CONTRACT
RENDERER_ID = 'pillow-pencil-contact-v10'
RENDERER_VERSION = '1'
DEFAULT_SUPERSAMPLE = 4
HIGH_QUALITY_SUPERSAMPLE = 8

def _clamp01(v: float) -> float:
    return max(0.0, min(1.0, float(v)))

def _pixel_hash_tooth(lx: np.ndarray, ly: np.ndarray, seed: int=7) -> np.ndarray:
    x = np.floor(lx).astype(np.uint32)
    y = np.floor(ly).astype(np.uint32)

    def h2(xx, yy, s):
        with np.errstate(over='ignore'):
            n = xx * np.uint32(374761393) + yy * np.uint32(668265263) + np.uint32(s & 4294967295) * np.uint32(1274126177)
            n = (n ^ n >> np.uint32(13)) * np.uint32(1274126177)
            n = n ^ n >> np.uint32(16)
        return n.astype(np.float32) / np.float32(4294967295.0)
    fine = h2(x, y, seed)
    coarse = h2(x // np.uint32(3), y // np.uint32(3), seed + 991)
    return np.clip(np.float32(0.45) * fine + np.float32(0.55) * coarse, 0.0, 1.0)
RENDERER_CONTRACT = V10_CONTRACT
_BROAD_START = float(RENDERER_CONTRACT.value('broad_start'))
_BROAD_FULL = float(RENDERER_CONTRACT.value('broad_full'))
_DEPOSITION_VARIABILITY_AMP = float(RENDERER_CONTRACT.value('deposition_variability_amp'))
_DEPOSITION_VARIABILITY_COARSE = float(RENDERER_CONTRACT.value('deposition_variability_coarse'))
_DEPOSITION_VARIABILITY_FINE = float(RENDERER_CONTRACT.value('deposition_variability_fine'))
_DEPOSITION_VARIABILITY_FINE_MIX = float(RENDERER_CONTRACT.value('deposition_variability_fine_mix'))
_AUTHORED_CONTRAST_GAMMA = float(RENDERER_CONTRACT.value('authored_contrast_gamma'))
_BROAD_DIAMETER_SCALE = float(RENDERER_CONTRACT.value('broad_diameter_scale'))
_BROAD_FLOW_GAIN = float(RENDERER_CONTRACT.value('broad_flow_gain'))
_BROAD_PIGMENT_DARKEN = float(RENDERER_CONTRACT.value('broad_pigment_darken'))
_DEFAULT_MATERIAL_POLICY = {'policy_id': 'canonical-pencil', 'value_authority': 'strict', 'core_preservation': 0.92, 'shoulder_breakup': 0.28, 'grain_exposure': 0.32, 'local_variation': 0.24}

def _stroke_material_policy(stroke: Stroke) -> dict:
    """Resolve persisted markmaking material policy without importing vNext.

    The renderer intentionally consumes only the already-resolved provenance payload.
    This keeps the render layer independent from agent instruction code and makes replay
    source-opaque: historical strokes carry the policy values needed to reproduce pixels.
    """
    ts = stroke.tool_state if isinstance(stroke.tool_state, dict) else {}
    policy = None
    provenance = ts.get('provenance')
    if isinstance(provenance, dict):
        metadata = provenance.get('metadata')
        if isinstance(metadata, dict):
            markmaking = metadata.get('markmaking')
            if isinstance(markmaking, dict):
                candidate = markmaking.get('material_policy')
                if isinstance(candidate, dict):
                    policy = candidate
    if policy is None:
        markmaking = ts.get('markmaking')
        if isinstance(markmaking, dict):
            candidate = markmaking.get('material_policy')
            if isinstance(candidate, dict):
                policy = candidate
    raw = dict(_DEFAULT_MATERIAL_POLICY)
    if policy is not None:
        for key in raw:
            if key in policy:
                raw[key] = policy[key]
    raw['policy_id'] = str(raw['policy_id']).strip().lower() or 'canonical-pencil'
    authority = str(raw['value_authority']).strip().lower()
    raw['value_authority'] = authority if authority in {'strict', 'balanced', 'relaxed'} else 'strict'
    for key in ('core_preservation', 'shoulder_breakup', 'grain_exposure', 'local_variation'):
        raw[key] = _clamp01(raw[key])
    return raw

def _policy_broad_grain(policy: dict, broadness: float) -> float:
    exposure = _clamp01(policy['grain_exposure'])
    return _clamp01((0.34 + 0.46 * exposure) * (0.88 + 0.12 * broadness))

def _policy_flow_multiplier(policy: dict, broadness: float) -> float:
    core = _clamp01(policy['core_preservation'])
    strictness = {'relaxed': 0.0, 'balanced': 0.5, 'strict': 1.0}[policy['value_authority']]
    normalized = _clamp01((core - 0.55) / 0.37)
    gain = 0.9 + 0.36 * normalized + 0.16 * strictness
    return 1.0 + (gain - 1.0) * broadness

def _policy_variation_scale(policy: dict) -> float:
    return max(0.0, min(1.8, float(policy['local_variation']) / 0.24))

def _policy_continuity_floor(policy: dict, broadness: float) -> tuple[float, float]:
    core = _clamp01(policy['core_preservation'])
    normalized = _clamp01((core - 0.55) / 0.37)
    strictness = {'relaxed': 0.0, 'balanced': 0.5, 'strict': 1.0}[policy['value_authority']]
    width_extra = broadness * (0.22 * normalized + 0.08 * strictness)
    alpha_extra = broadness * (0.34 * normalized + 0.12 * strictness)
    return (width_extra, alpha_extra)

def _policy_pigment_darken(policy: dict, broadness: float) -> float:
    authority = policy['value_authority']
    base = {'relaxed': float(_BROAD_PIGMENT_DARKEN) * 0.45, 'balanced': float(_BROAD_PIGMENT_DARKEN), 'strict': float(_BROAD_PIGMENT_DARKEN) * 0.82}[authority]
    return max(0.0, min(0.65, base * broadness))

def _smoothstep01(x: float) -> float:
    x = _clamp01(x)
    return x * x * (3.0 - 2.0 * x)

def _broadness(width_logical: float) -> float:
    if _BROAD_FULL <= _BROAD_START:
        return 1.0
    return _smoothstep01((float(width_logical) - _BROAD_START) / (_BROAD_FULL - _BROAD_START))

def _broad_edge_radius(width_logical: float, hardness: float) -> float:
    b = _broadness(width_logical)
    if b <= 1e-08:
        return 0.0
    softness = (1.0 - _clamp01(hardness)) ** 1.25
    return b * max(0.15, min(1.6, float(width_logical) * (0.02 + 0.05 * softness)))

def _physical_terminal_span(width_logical: float, *, incoming: bool) -> float:
    if incoming:
        return max(6.0, min(24.0, 3.0 + 0.95 * float(width_logical)))
    return max(7.0, min(28.0, 4.0 + 1.2 * float(width_logical)))

def _pressure_variability(samples: np.ndarray) -> float:
    if len(samples) <= 1:
        return 0.0
    return float(min(1.0, max(0.0, np.std(samples) / 0.22)))

def _wrapped_angle_delta(a: np.ndarray) -> np.ndarray:
    d = np.diff(a)
    return (d + np.pi) % (2.0 * np.pi) - np.pi

def _thin_flick_gate(width_logical: float, taper_out: float) -> float:
    thin_zone = _smoothstep01((float(width_logical) - 2.1) / 1.9) * (1.0 - _smoothstep01((float(width_logical) - 6.4) / 2.0))
    flick_zone = _smoothstep01((float(taper_out) - 0.72) / 0.2)
    return thin_zone * flick_zone

def _hash1_scalar(i: int, seed: int) -> float:
    n = int(i) * 374761393 + int(seed) * 668265263 & 4294967295
    n = (n ^ n >> 13) * 1274126177 & 4294967295
    n = (n ^ n >> 16) & 4294967295
    return float(n) / 4294967295.0

def _value_noise_1d(s: np.ndarray, cell: float, seed: int) -> np.ndarray:
    cell = max(0.25, float(cell))
    u = np.asarray(s, dtype=np.float64) / cell
    i0 = np.floor(u).astype(np.int64)
    f = u - i0
    f = f * f * (3.0 - 2.0 * f)
    a = np.array([_hash1_scalar(int(i), seed) for i in i0], dtype=np.float64)
    b = np.array([_hash1_scalar(int(i) + 1, seed) for i in i0], dtype=np.float64)
    return a * (1.0 - f) + b * f

def _authored_contrast_field(chosen: list, broadness: float) -> np.ndarray:
    n = len(chosen)
    gamma = max(0.0, float(_AUTHORED_CONTRAST_GAMMA)) * float(broadness)
    if n <= 1 or gamma <= 1e-08:
        return np.ones(n, dtype=np.float32)
    a = np.asarray([max(0.015, float(q[3]) / 255.0) for q in chosen], dtype=np.float64)
    mean_a = max(1e-06, float(np.mean(a)))
    field = np.power(a / mean_a, gamma)
    field = np.clip(field, 0.45, 1.7)
    mean = float(np.mean(field))
    if mean > 1e-09:
        field = field / mean
    return field.astype(np.float32)

def _local_deposition_field(chosen: list, seed: int, broadness: float, *, variation_scale: float=1.0) -> np.ndarray:
    n = len(chosen)
    if n <= 1 or broadness <= 1e-08 or _DEPOSITION_VARIABILITY_AMP <= 1e-08:
        return np.ones(n, dtype=np.float32)
    xy = np.asarray([[float(q[0]), float(q[1])] for q in chosen], dtype=np.float64)
    seg = np.linalg.norm(np.diff(xy, axis=0), axis=1)
    s = np.concatenate([[0.0], np.cumsum(seg)])
    coarse = _value_noise_1d(s, _DEPOSITION_VARIABILITY_COARSE, seed ^ 1939981753)
    fine = _value_noise_1d(s, _DEPOSITION_VARIABILITY_FINE, seed ^ 2654435769)
    mix = float(np.clip(_DEPOSITION_VARIABILITY_FINE_MIX, 0.0, 1.0))
    v = (1.0 - mix) * coarse + mix * fine
    v = v - float(np.mean(v))
    authored = np.asarray([float(q[3]) / 255.0 for q in chosen], dtype=np.float64)
    a0 = authored - float(np.mean(authored))
    denom = float(np.dot(a0, a0))
    if denom > 1e-09:
        v = v - a0 * (float(np.dot(v, a0)) / denom)
    v = v - float(np.mean(v))
    std = float(np.std(v))
    if std > 1e-08:
        v = v / std
    v = np.clip(v, -2.0, 2.0)
    amp = float(_DEPOSITION_VARIABILITY_AMP) * float(broadness) * max(0.0, float(variation_scale))
    field = np.clip(1.0 + amp * v, 0.58, 1.42)
    mean = float(np.mean(field))
    if mean > 1e-09:
        field = field / mean
    return field.astype(np.float32)

def _selected_grade(stroke: Stroke, global_grade: str | None) -> str | None:
    ts = stroke.tool_state if isinstance(stroke.tool_state, dict) else {}
    local = ts.get('pencil_grade')
    if local is not None:
        return str(local).upper()
    return None if global_grade is None else str(global_grade).upper()

def _prepare_grade(stroke: Stroke, global_grade: str | None) -> Stroke:
    grade = _selected_grade(stroke, global_grade)
    return deepcopy(stroke) if grade is None else p6.apply_grade(stroke, grade)

def _smooth_hand_dynamics(stroke: Stroke, profile: PencilContactProfile) -> Stroke:
    """P4-compatible path wobble with continuous pressure variation, not micro-breaks."""
    jitter, taper_in, taper_out = p4._dynamics(stroke)
    if jitter <= 1e-12 and taper_in <= 1e-12 and (taper_out <= 1e-12):
        return deepcopy(stroke)
    pts, pressure, t = p4._resample(stroke, spacing=profile.trajectory_spacing)
    if len(pts) < 2:
        return deepcopy(stroke)
    tangent = np.empty_like(pts)
    tangent[0] = pts[1] - pts[0]
    tangent[-1] = pts[-1] - pts[-2]
    if len(pts) > 2:
        tangent[1:-1] = pts[2:] - pts[:-2]
    norm = np.linalg.norm(tangent, axis=1)
    norm[norm < 1e-09] = 1.0
    tangent /= norm[:, None]
    normal = np.column_stack([-tangent[:, 1], tangent[:, 0]])
    seed = p4._stable_seed(stroke)
    wave = p4._hand_wave(t, seed)
    end_anchor = np.sin(pi * t) ** 0.78
    amp = min(1.35, (0.42 + 0.14 * min(float(stroke.width), 5.0)) * np.sqrt(jitter))
    moved = pts + normal * (amp * end_anchor * wave)[:, None]
    moved[0] = pts[0]
    moved[-1] = pts[-1]
    hp = profile.hand
    entry = p4._smoothstep(t / hp.tip_span)
    release = p4._smoothstep((1.0 - t) / hp.tip_span)
    tip_factor = (1.0 - hp.taper_in_strength * taper_in * (1.0 - entry)) * (1.0 - hp.taper_out_strength * taper_out * (1.0 - release))
    phase = 2.0 * pi * p4._seed_unit(seed ^ 3039394381, 12)
    freq = hp.pressure_cadence_frequency_min + hp.pressure_cadence_frequency_span * p4._seed_unit(seed, 28)
    cadence = 1.0 + hp.pressure_cadence_strength * np.sqrt(jitter) * np.sin(2.0 * pi * freq * t + phase)
    dyn_pressure = np.clip(pressure * tip_factor * cadence, 0.025, 1.0)
    out = deepcopy(stroke)
    out.points = [(float(x), float(y)) for x, y in moved]
    out.pressure = [float(v) for v in dyn_pressure]
    return out.cleaned()

def _contact_width(base_width: float, pressure: float, hardness: float, profile: PencilContactProfile) -> float:
    m = profile.material
    p = _clamp01(pressure)
    h = _clamp01(hardness)
    pressure_width = float(base_width) * (m.width_base + m.width_pressure_gain * p)
    return max(m.min_width, pressure_width * (1.08 - 0.16 * h))

def _contact_deposition(base_opacity: float, pressure: float, hardness: float, profile: PencilContactProfile) -> float:
    m = profile.material
    p = _clamp01(pressure)
    h = _clamp01(hardness)
    load = m.deposition_floor + (1.0 - m.deposition_floor) * p ** m.deposition_exponent
    hardness_release = 1.1 - 0.18 * h
    return _clamp01(float(base_opacity) * load * hardness_release)

def _contact_bounds(stroke: Stroke, factor: float, hardness: float, hi_size: tuple[int, int], profile: PencilContactProfile) -> tuple[int, int, int, int]:
    pts = [(float(x) * factor, float(y) * factor) for x, y in stroke.points]
    if not pts:
        return (0, 0, 1, 1)
    max_contact_logical = _contact_width(stroke.width, 1.0, hardness, profile)
    max_contact = max_contact_logical * factor
    softness = (1.0 - hardness) ** 1.35
    halo = softness * profile.edge.soft_halo_radius * factor
    broad_shoulder = _broad_edge_radius(max_contact_logical, hardness) * factor
    margin = max(3.0, max_contact * 0.7 + halo * 2.0 + broad_shoulder * 2.5 + 3.0)
    xs = [q[0] for q in pts]
    ys = [q[1] for q in pts]
    x0 = max(0, int(np.floor(min(xs) - margin)))
    y0 = max(0, int(np.floor(min(ys) - margin)))
    x1 = min(int(hi_size[0]), int(np.ceil(max(xs) + margin)) + 1)
    y1 = min(int(hi_size[1]), int(np.ceil(max(ys) + margin)) + 1)
    return (x0, y0, max(x0 + 1, x1), max(y0 + 1, y1))

def _pressure_samples(stroke: Stroke, factor: float, hardness: float, spacing: float, profile: PencilContactProfile):
    pts = np.asarray(stroke.points, dtype=np.float64)
    if len(pts) < 2:
        return []
    seg = np.linalg.norm(np.diff(pts, axis=0), axis=1)
    cumulative = np.concatenate([[0.0], np.cumsum(seg)])
    total = float(cumulative[-1])
    if total <= 1e-09:
        return []
    count = max(2, int(np.ceil(total / max(0.18, float(spacing)))) + 1)
    sdist = np.linspace(0.0, total, count)
    x = np.interp(sdist, cumulative, pts[:, 0])
    y = np.interp(sdist, cumulative, pts[:, 1])
    if stroke.pressure is not None and len(stroke.pressure) == len(stroke.points):
        src_p = np.asarray(stroke.pressure, dtype=np.float64)
    else:
        ts = stroke.tool_state if isinstance(stroke.tool_state, dict) else {}
        src_p = np.full(len(stroke.points), _clamp01(ts.get('pressure', 0.55)), dtype=np.float64)
    p = np.interp(sdist, cumulative, src_p)
    mean_p = float(np.mean(p)) if len(p) else 0.55
    nominal_width = _contact_width(stroke.width, mean_p, hardness, profile)
    b = _broadness(nominal_width)
    ts = stroke.tool_state if isinstance(stroke.tool_state, dict) else {}
    taper_in = _clamp01(ts.get('taper_in', 0.0))
    taper_out = _clamp01(ts.get('taper_out', 0.0))
    broad_gate = _smoothstep01((nominal_width - 5.2) / 3.8)
    thin_flick = _thin_flick_gate(nominal_width, taper_out)
    if broad_gate <= 1e-08 and thin_flick <= 1e-08:
        out = []
        for xx, yy, pp in zip(x, y, p):
            pp = _clamp01(pp)
            out.append((float(xx) * factor, float(yy) * factor, _contact_width(stroke.width, pp, hardness, profile) * factor, int(round(_contact_deposition(stroke.opacity, pp, hardness, profile) * 255.0)), pp))
        return out
    dynamic_gate = max(broad_gate, 0.75 * thin_flick)
    pvar = _pressure_variability(p)
    dx = np.gradient(x)
    dy = np.gradient(y)
    ddx = np.gradient(dx)
    ddy = np.gradient(dy)
    curv = np.abs(dx * ddy - dy * ddx) / np.power(dx * dx + dy * dy + 1e-06, 1.5)
    curv = np.nan_to_num(curv, nan=0.0, posinf=0.0, neginf=0.0)
    c95 = float(np.percentile(curv, 95)) if len(curv) else 0.0
    if c95 > 1e-08:
        curv_n = np.clip(curv / c95, 0.0, 1.0)
    else:
        curv_n = np.zeros_like(curv)
    if len(p) > 1:
        dp = np.gradient(p, sdist)
        d95 = float(np.percentile(np.abs(dp), 95))
        if d95 > 1e-08:
            dp_n = np.clip(dp / d95, -1.0, 1.0)
        else:
            dp_n = np.zeros_like(dp)
    else:
        dp_n = np.zeros_like(p)
    pos_dp = np.clip(dp_n, 0.0, 1.0)
    neg_dp = np.clip(-dp_n, 0.0, 1.0)
    expn = 1.0 + 0.8 * b
    taper_in_eff = 1.0 - (1.0 - taper_in) ** expn
    taper_out_eff = 1.0 - (1.0 - taper_out) ** expn
    flick = _smoothstep01((taper_out_eff - 0.78) / 0.18) * max(_smoothstep01((nominal_width - 3.2) / 6.0), thin_flick)
    span_in = _physical_terminal_span(nominal_width, incoming=True) * (1.0 - 0.1 * flick)
    span_out = _physical_terminal_span(nominal_width, incoming=False) * (1.0 - 0.42 * flick - 0.26 * thin_flick)
    angles = np.arctan2(dy, dx)
    dtheta = np.concatenate([[0.0], _wrapped_angle_delta(angles)]) if len(angles) > 1 else np.zeros_like(angles)
    turn_n = np.clip(np.abs(dtheta) / 0.26, 0.0, 1.0)
    out = []
    for i, (ss, xx, yy, pp) in enumerate(zip(sdist, x, y, p)):
        pp = _clamp01(pp)
        base_w = _contact_width(stroke.width, pp, hardness, profile)
        base_a = _contact_deposition(stroke.opacity, pp, hardness, profile)
        local_pressure = 2.0 * (pp - mean_p)
        express = dynamic_gate * (0.5 + 0.5 * pvar)
        width_lift = 1.0 + express * (0.17 * local_pressure + 0.11 * pos_dp[i] - 0.06 * neg_dp[i] + 0.09 * curv_n[i])
        thin_bonus = thin_flick * (0.05 * pos_dp[i] + 0.05 * curv_n[i])
        alpha_lift = 1.0 + express * (0.08 * local_pressure + 0.17 * pos_dp[i] - 0.03 * neg_dp[i] + 0.16 * curv_n[i] + 0.09 * turn_n[i]) + thin_flick * (0.07 * pos_dp[i] + 0.05 * turn_n[i])
        width = base_w * max(0.52, width_lift + thin_bonus)
        alpha_base = _clamp01(base_a * max(0.42, alpha_lift))
        entry = _smoothstep01(ss / span_in) if taper_in_eff > 1e-08 else 1.0
        release = _smoothstep01((total - ss) / span_out) if taper_out_eff > 1e-08 else 1.0
        if b > 1e-08 or flick > 1e-08 or thin_flick > 1e-08:
            terminal_shape = (1.0 - taper_in_eff * (1.0 - entry)) * (1.0 - taper_out_eff * (1.0 - release))
            width_pow = 1.35 + 0.55 * b + 0.85 * flick + 1.3 * thin_flick
            alpha_pow = 1.9 + 0.8 * b + 1.2 * flick + 1.65 * thin_flick
            width_mul = terminal_shape ** width_pow
            alpha_mul = terminal_shape ** alpha_pow
            floor = profile.material.min_width * (0.35 - 0.23 * flick - 0.22 * thin_flick)
            floor = max(profile.material.min_width * 0.04, floor)
            tip_window = 1.0 - min(1.0, max(0.0, (total - ss) / max(1e-06, span_out)))
            tip_shape = _smoothstep01(tip_window)
            if thin_flick > 1e-08:
                width_mul *= 1.0 - 0.18 * thin_flick * tip_shape
                alpha_mul *= 1.0 - 0.1 * thin_flick * tip_shape
            width = max(floor, width * width_mul)
            alpha = int(round(_clamp01(alpha_base * alpha_mul) * 255.0))
        else:
            alpha = int(round(_clamp01(alpha_base) * 255.0))
        out.append((float(xx) * factor, float(yy) * factor, width * factor, alpha, pp))
    return out

def _continuous_contact_mask(stroke: Stroke, factor: float, hardness: float, bounds: tuple[int, int, int, int], profile: PencilContactProfile) -> Image.Image:
    """Thin: exact RC1 line mask. Broad: radial max-contact envelope."""
    x0, y0, x1, y1 = bounds
    samples = _pressure_samples(stroke, factor, hardness, profile.trajectory_spacing, profile)
    mask = Image.new('L', (x1 - x0, y1 - y0), 0)
    if len(samples) < 2:
        return mask
    mean_w_logical = float(np.mean([q[2] for q in samples])) / float(factor)
    b = _broadness(mean_w_logical)
    if b <= 1e-08:
        segments = []
        for prev, cur in zip(samples, samples[1:]):
            width = max(1, int(round((prev[2] + cur[2]) * 0.5)))
            alpha = int(round((prev[3] + cur[3]) * 0.5))
            segments.append((alpha, width, (prev[0] - x0, prev[1] - y0), (cur[0] - x0, cur[1] - y0)))
        d = ImageDraw.Draw(mask)
        for alpha, width, a, bb in sorted(segments, key=lambda row: row[0]):
            d.line([a, bb], fill=alpha, width=width)
        softness = (1.0 - hardness) ** 1.35
        radius = softness * profile.edge.soft_halo_radius * factor
        if radius > 0.05 and profile.edge.soft_halo_strength > 1e-06:
            halo = mask.filter(ImageFilter.GaussianBlur(radius=radius))
            halo = halo.point([int(round(i * profile.edge.soft_halo_strength * softness)) for i in range(256)])
            mask = ImageChops.lighter(mask, halo)
        return mask
    hh, ww = (y1 - y0, x1 - x0)
    trans = np.ones((hh, ww), dtype=np.float32)
    target_spacing = 0.78
    step = max(1, int(round(target_spacing / max(profile.trajectory_spacing, 1e-06))))
    chosen = samples[::step]
    if chosen[-1] is not samples[-1]:
        chosen = chosen + [samples[-1]]
    radial_exp = 0.4 + 0.5 * _clamp01(hardness)
    yy, xx = np.indices((hh, ww), dtype=np.float64)
    lx = (xx + float(x0)) / float(factor)
    ly = (yy + float(y0)) / float(factor)
    tooth = _pixel_hash_tooth(lx, ly, 7).astype(np.float32)
    policy = _stroke_material_policy(stroke)
    broad_grain = np.float32(_policy_broad_grain(policy, b))
    flow_base = np.float32(0.041 + 0.05 * b)
    flow_policy = np.float32(_policy_flow_multiplier(policy, b))
    seed = p4._stable_seed(stroke)
    local_variability = _local_deposition_field(chosen, seed, b, variation_scale=_policy_variation_scale(policy))
    authored_contrast = _authored_contrast_field(chosen, b)
    for idx, (cx, cy, diameter, alpha, pressure) in enumerate(chosen):
        if alpha <= 1:
            continue
        r = max(0.5, float(diameter) * 0.5 * float(_BROAD_DIAMETER_SCALE))
        lx0 = float(cx) - x0
        ly0 = float(cy) - y0
        xa = max(0, int(np.floor(lx0 - r)) - 1)
        xb = min(ww, int(np.ceil(lx0 + r)) + 2)
        ya = max(0, int(np.floor(ly0 - r)) - 1)
        yb = min(hh, int(np.ceil(ly0 + r)) + 2)
        if xa >= xb or ya >= yb:
            continue
        ys = np.arange(ya, yb, dtype=np.float32)[:, None]
        xs = np.arange(xa, xb, dtype=np.float32)[None, :]
        dist = np.sqrt((xs - lx0) ** 2 + (ys - ly0) ** 2) / np.float32(r)
        contact = np.clip(1.0 - dist * dist, 0.0, 1.0) ** np.float32(radial_exp)
        authored = np.float32(alpha / 255.0)
        p = np.float32(_clamp01(pressure))
        local_flow = flow_base * np.float32(_BROAD_FLOW_GAIN) * flow_policy * (np.float32(0.62) + np.float32(0.48) * authored) * (np.float32(0.86) + np.float32(0.24) * p) * local_variability[idx] * authored_contrast[idx]
        t = tooth[ya:yb, xa:xb]
        dry = np.float32(1.0) - broad_grain + broad_grain * t
        dab = np.clip(contact * local_flow * dry, 0.0, 0.15)
        trans[ya:yb, xa:xb] *= np.float32(1.0) - dab
    ink = np.clip(np.float32(1.0) - trans, 0.0, 1.0)
    ink = np.minimum(ink, np.float32(0.92))
    return Image.fromarray(np.clip(ink * 255.0, 0, 255).astype(np.uint8), mode='L')

def _continuity_floor_mask(stroke: Stroke, factor: float, hardness: float, bounds: tuple[int, int, int, int], profile: PencilContactProfile) -> Image.Image:
    x0, y0, x1, y1 = bounds
    mask = Image.new('L', (x1 - x0, y1 - y0), 0)
    samples = _pressure_samples(stroke, factor, hardness, profile.trajectory_spacing, profile)
    if len(samples) < 2:
        return mask
    pts = [(s[0] - x0, s[1] - y0) for s in samples]
    mean_w = float(np.mean([s[2] for s in samples])) / float(factor)
    b = _broadness(mean_w)
    ts = stroke.tool_state if isinstance(stroke.tool_state, dict) else {}
    thin_flick = _thin_flick_gate(mean_w, _clamp01(ts.get('taper_out', 0.0)))
    min_width = max(1, int(round(min((s[2] for s in samples)))))
    min_alpha = min((s[3] for s in samples))
    max_alpha = max((s[3] for s in samples)) if samples else 0
    m = profile.material
    d = ImageDraw.Draw(mask)
    if b > 1e-08:
        policy = _stroke_material_policy(stroke)
        width_extra, alpha_extra = _policy_continuity_floor(policy, b)
        width_ratio = min(1.0, 1.0 - 0.92 * b + width_extra)
        alpha_ratio = min(1.0, 1.0 - 0.94 * b + alpha_extra)
        min_width = max(1, int(round(min_width * width_ratio)))
        base_alpha = max(int(round(m.continuity_min_coverage * 255.0)), int(round(min_alpha * m.continuity_floor_ratio)))
        alpha = max(1, int(round(base_alpha * alpha_ratio)))
        if alpha > 1 or b < 0.75:
            d.line(pts, fill=alpha, width=min_width, joint='curve')
        return mask
    if thin_flick <= 1e-06:
        alpha = max(int(round(m.continuity_min_coverage * 255.0)), int(round(min_alpha * m.continuity_floor_ratio)))
        d.line(pts, fill=alpha, width=min_width, joint='curve')
        return mask
    base_alpha = max(1, int(round(max(int(round(m.continuity_min_coverage * 255.0 * 0.45)), min_alpha * (0.34 + 0.2 * (1.0 - thin_flick))))))
    floor_w = max(1, int(round(min_width * (0.8 - 0.25 * thin_flick))))
    segs = []
    n = len(samples)
    for i in range(n - 1):
        a = pts[i]
        bpt = pts[i + 1]
        t = i / max(1, n - 2)
        tail = _smoothstep01(1.0 - t)
        body = 1.0 - 0.32 * thin_flick + 0.1 * tail
        tip = 1.0 - _smoothstep01((t - 0.76) / 0.24) if t > 0.76 else 1.0
        seg_alpha_src = 0.5 * (samples[i][3] + samples[i + 1][3])
        alpha_norm = seg_alpha_src / max(1.0, float(max_alpha))
        seg_alpha = int(round(base_alpha * body * tip * (0.8 + 0.35 * alpha_norm)))
        if seg_alpha < 1:
            continue
        seg_width_src = 0.5 * (samples[i][2] + samples[i + 1][2])
        seg_width = max(1, int(round(min(floor_w, max(1.0, seg_width_src * (0.16 + 0.1 * alpha_norm))))))
        segs.append((seg_alpha, seg_width, a, bpt))
    for alpha, width, a, bpt in sorted(segs, key=lambda row: row[0]):
        d.line([a, bpt], fill=alpha, width=width, joint='curve')
    return mask

def _thin_texture_gain(width_logical: float, reference: float, floor: float) -> float:
    if reference <= 1e-09:
        return 1.0
    u = np.clip(float(width_logical) / float(reference), 0.0, 1.0)
    s = float(u * u * (3.0 - 2.0 * u))
    return float(floor + (1.0 - floor) * s)

def _mean_contact_width(stroke: Stroke, hardness: float, profile: PencilContactProfile) -> float:
    if stroke.pressure is not None and len(stroke.pressure) == len(stroke.points) and stroke.pressure:
        pressure = float(np.mean(np.asarray(stroke.pressure, dtype=np.float32)))
    else:
        ts = stroke.tool_state if isinstance(stroke.tool_state, dict) else {}
        pressure = _clamp01(ts.get('pressure', 0.55))
    return _contact_width(stroke.width, pressure, hardness, profile)

def _smooth_grain_modulate(mask: Image.Image, *, stroke: Stroke, grain: float, hardness: float, factor: float, global_origin: tuple[int, int], seed: int, profile: PencilContactProfile) -> Image.Image:
    """Continuous correlated grain modulation; never removes isolated pixels."""
    g = _clamp01(grain)
    if g <= 1e-08:
        return mask
    arr = np.asarray(mask, dtype=np.float32)
    active = arr > 0.5
    if not np.any(active):
        return mask
    hh, ww = arr.shape
    oy, ox = (int(global_origin[1]), int(global_origin[0]))
    yy, xx = np.indices((hh, ww), dtype=np.float64)
    lx = (xx + float(ox)) / float(factor)
    ly = (yy + float(oy)) / float(factor)
    gp = profile.grain
    coarse = p5._value_noise(lx, ly, gp.coarse_cell, seed ^ 2769414579)
    fine = p5._value_noise(lx, ly, gp.fine_cell, seed ^ 1675113877)
    width = _mean_contact_width(stroke, hardness, profile)
    b = _broadness(width)
    ts = stroke.tool_state if isinstance(stroke.tool_state, dict) else {}
    thin_flick = _thin_flick_gate(width, _clamp01(ts.get('taper_out', 0.0)))
    activity = max(b, thin_flick)
    variability = 0.0
    if activity > 1e-08 and stroke.pressure is not None and (len(stroke.pressure) == len(stroke.points)) and (len(stroke.pressure) > 1):
        variability = _pressure_variability(np.asarray(stroke.pressure, dtype=np.float32))
    if b > 1e-08:
        micro = p5._value_noise(lx, ly, 0.22, seed ^ 3535225863)
        sparkle = p5._value_noise(lx, ly, 0.11, seed ^ 2465573313)
        field = np.float32(0.42) * coarse + np.float32(0.18) * fine + np.float32(0.25) * micro + np.float32(0.15) * sparkle
    else:
        field = np.float32(0.72) * coarse + np.float32(0.28) * fine
    thin_gain = _thin_texture_gain(width, gp.thin_width_reference, gp.thin_texture_floor)
    strength = np.float32(gp.strength * g * thin_gain * (1.0 + 0.38 * b) * (1.0 + 0.22 * variability))
    mod = np.float32(1.0) + strength * (field - np.float32(0.5)) * np.float32(2.0)
    mean_mod = float(np.mean(mod[active]))
    if mean_mod > 1e-06:
        mod = mod / np.float32(mean_mod)
    mod = np.clip(mod, np.float32(gp.min_modulation), np.float32(gp.max_modulation))
    out = np.clip(arr * mod, 0.0, 255.0).astype(np.uint8)
    return Image.fromarray(out, mode='L')

def _smooth_paper_modulate(mask: Image.Image, *, stroke: Stroke, tooth: float, paper_scale: float, paper_seed: int, factor: float, global_origin: tuple[int, int], hardness: float, profile: PencilContactProfile) -> Image.Image:
    """Page-fixed tooth with smooth valley attenuation and thin-line protection."""
    t = _clamp01(tooth)
    if t <= 1e-08:
        return mask
    arr = np.asarray(mask, dtype=np.float32)
    active = arr > 0.5
    if not np.any(active):
        return mask
    pressure = p5._stroke_pressure(stroke)
    field = p5.paper_field(arr.shape, factor=factor, global_origin=global_origin, paper_scale=paper_scale, paper_seed=paper_seed)
    pp = profile.paper
    width = _mean_contact_width(stroke, hardness, profile)
    thin_gain = _thin_texture_gain(width, pp.thin_width_reference, pp.thin_texture_floor)
    relief = (field - np.float32(0.5)) * np.float32(2.0)
    contact = np.float32((0.52 + 0.56 * hardness) * (1.0 - 0.56 * pressure))
    strength = np.float32(pp.strength * t * thin_gain * (1.0 + 0.28 * _broadness(width))) * contact
    mod = np.float32(1.0) + strength * relief
    valley_cut = float(0.23 + 0.12 * t - 0.11 * pressure)
    band = float(pp.valley_band)
    lo = valley_cut - band
    hi = valley_cut + band
    u = np.clip((field - np.float32(lo)) / np.float32(max(1e-06, hi - lo)), 0.0, 1.0)
    smooth = u * u * (np.float32(3.0) - np.float32(2.0) * u)
    valley_weight = np.float32(1.0) - smooth
    valley_depth = np.float32(pp.valley_depth * t * thin_gain * (1.0 - 0.45 * pressure))
    mod *= np.float32(1.0) - valley_weight * valley_depth
    mean_mod = float(np.mean(mod[active]))
    if mean_mod > 1e-06:
        mod = mod / np.float32(mean_mod)
    mod = np.clip(mod, np.float32(pp.min_modulation), np.float32(pp.max_modulation))
    out = np.clip(arr * mod, 0.0, 255.0).astype(np.uint8)
    return Image.fromarray(out, mode='L')

def _build_contact_patch(stroke: Stroke, *, factor: float, hi_size: tuple[int, int], tooth: float, paper_scale: float, paper_seed: int, graphite: tuple[int, int, int], profile: PencilContactProfile):
    """Return the exact canonical contact patch used by both full and fast renderers."""
    if len(stroke.points) < 2:
        return ((0, 0, 0, 0), Image.new('RGBA', (1, 1), (0, 0, 0, 0)))
    grain, hardness = p3._material(stroke)
    bounds = _contact_bounds(stroke, factor, hardness, hi_size, profile)
    mask = _continuous_contact_mask(stroke, factor, hardness, bounds, profile)
    continuity = _continuity_floor_mask(stroke, factor, hardness, bounds, profile)
    mean_width = _mean_contact_width(stroke, hardness, profile)
    broad_material = _broadness(mean_width)
    if broad_material < 0.35:
        mask = _smooth_grain_modulate(mask, stroke=stroke, grain=grain, hardness=hardness, factor=factor, global_origin=(bounds[0], bounds[1]), seed=p3._stroke_seed(stroke), profile=profile)
        mask = _smooth_paper_modulate(mask, stroke=stroke, tooth=tooth, paper_scale=paper_scale, paper_seed=paper_seed, factor=factor, global_origin=(bounds[0], bounds[1]), hardness=hardness, profile=profile)
    elif broad_material < 0.7:
        soft_grain = max(0.0, float(grain) * (0.7 - broad_material) / 0.35)
        if soft_grain > 1e-06:
            mask = _smooth_grain_modulate(mask, stroke=stroke, grain=soft_grain, hardness=hardness, factor=factor, global_origin=(bounds[0], bounds[1]), seed=p3._stroke_seed(stroke), profile=profile)
    mask = ImageChops.lighter(mask, continuity)
    pigment_b = _broadness(mean_width)
    policy = _stroke_material_policy(stroke)
    darken = _policy_pigment_darken(policy, pigment_b)
    local_graphite = tuple((max(0, min(255, int(round(float(c) * (1.0 - darken))))) for c in graphite))
    layer = p3._graphite_layer(mask.size, mask, graphite=local_graphite)
    mask.close()
    continuity.close()
    return (bounds, layer)

def _deposit(graphite_canvas: Image.Image, stroke: Stroke, *, factor: float, hi_size: tuple[int, int], tooth: float, paper_scale: float, paper_seed: int, graphite: tuple[int, int, int], profile: PencilContactProfile) -> None:
    bounds, layer = _build_contact_patch(stroke, factor=factor, hi_size=hi_size, tooth=tooth, paper_scale=paper_scale, paper_seed=paper_seed, graphite=graphite, profile=profile)
    graphite_canvas.alpha_composite(layer, dest=(bounds[0], bounds[1]))
    layer.close()

def render(ir: StrokeIR, path: str | Path, background=(255, 255, 255, 255), *, scale: int=1, supersample: int=DEFAULT_SUPERSAMPLE, graphite=(36, 34, 32), grade: str | None=None, contact_profile: str | Path | None=None) -> None:
    """Candidate Contact Patch v10 renderer.

    Ordinary thin strokes preserve the historical v9 material path while broad graphite,
    authored pressure dynamics, physical-pixel terminal spans, and thin flicks use the v10
    material model. Resolved markmaking material policy is read from stroke provenance rather
    than from private agent/runtime implementation state.
    """
    if int(scale) != scale or scale < 1:
        raise ValueError('scale must be a positive integer')
    if int(supersample) != supersample or supersample < 2:
        raise ValueError('supersample must be an integer >= 2')
    if grade is not None:
        p6.get_grade(grade)
    profile = load_pencil_contact_profile(contact_profile)
    scale = int(scale)
    supersample = int(supersample)
    factor = float(scale * supersample)
    hi_size = (int(ir.width * factor), int(ir.height * factor))
    out_size = (int(ir.width * scale), int(ir.height * scale))
    tooth, paper_scale, paper_seed = p5._paper_settings(ir)
    graphite_canvas = Image.new('RGBA', hi_size, (int(graphite[0]), int(graphite[1]), int(graphite[2]), 0))
    for stroke in sorted(ir.strokes, key=lambda z: z.layer):
        if p7.is_eraser(stroke):
            p7._erase(graphite_canvas, stroke, factor=factor, hi_size=hi_size, tooth=tooth, paper_scale=paper_scale, paper_seed=paper_seed)
            continue
        prepared = _prepare_grade(stroke, grade)
        prepared = _smooth_hand_dynamics(prepared, profile)
        _deposit(graphite_canvas, prepared, factor=factor, hi_size=hi_size, tooth=tooth, paper_scale=paper_scale, paper_seed=paper_seed, graphite=(int(graphite[0]), int(graphite[1]), int(graphite[2])), profile=profile)
    base = Image.new('RGBA', hi_size, background)
    base = Image.alpha_composite(base, graphite_canvas)
    final = base.resize(out_size, Image.Resampling.LANCZOS)
    p = str(path)
    if p.lower().endswith(('.jpg', '.jpeg')):
        final.convert('RGB').save(p, quality=95)
    else:
        final.save(p)
