from __future__ import annotations

import numpy as np
from PIL import Image, ImageDraw


def install_v10_value_authority_core(module) -> None:
    """Install the v10 broad authored-value core without changing historical v9.

    v10's dry radial shoulder is useful material behavior, but it must not erase an
    explicitly dark authored stroke merely because contact width enters the broad
    regime. The adapter replaces only the broad continuity floor. Thin/flick paths
    delegate byte-for-byte to the candidate module's original implementation.
    """
    if getattr(module, "_img2drawing_value_authority_v2", False):
        return

    original = module._continuity_floor_mask

    def _continuity_floor_mask(stroke, factor, hardness, bounds, profile):
        x0, y0, x1, y1 = bounds
        samples = module._pressure_samples(
            stroke, factor, hardness, profile.trajectory_spacing, profile
        )
        if len(samples) < 2:
            return Image.new("L", (x1 - x0, y1 - y0), 0)

        mean_w = float(np.mean([sample[2] for sample in samples])) / float(factor)
        broadness = module._broadness(mean_w)
        if broadness <= 1e-08:
            return original(stroke, factor, hardness, bounds, profile)

        mask = Image.new("L", (x1 - x0, y1 - y0), 0)
        draw = ImageDraw.Draw(mask)
        points = [(sample[0] - x0, sample[1] - y0) for sample in samples]
        policy = module._stroke_material_policy(stroke)
        core = module._clamp01(policy["core_preservation"])
        strictness = {
            "relaxed": 0.0,
            "balanced": 0.5,
            "strict": 1.0,
        }[policy["value_authority"]]

        # At the broad threshold this converges to the historical full-width authored
        # contact. As contact widens, only the dark core narrows; the existing radial
        # low-flow pass remains the graphite shoulder. Width therefore changes material
        # character without unexpectedly re-authoring value.
        target_width_ratio = module._clamp01(0.10 + 0.18 * core + 0.06 * strictness)
        width_ratio = 1.0 - broadness * (1.0 - target_width_ratio)
        target_alpha_retention = module._clamp01(
            0.45 + 0.45 * core + 0.08 * strictness
        )
        alpha_retention = 1.0 - broadness * (1.0 - target_alpha_retention)
        material = profile.material
        coverage_floor = int(round(material.continuity_min_coverage * 255.0))

        for index in range(len(samples) - 1):
            a = points[index]
            b = points[index + 1]
            width_src = 0.5 * (samples[index][2] + samples[index + 1][2])
            alpha_src = 0.5 * (samples[index][3] + samples[index + 1][3])
            width = max(1, int(round(width_src * width_ratio)))
            legacy_floor = max(
                coverage_floor,
                int(round(alpha_src * material.continuity_floor_ratio)),
            )
            authored_floor = int(round(alpha_src * alpha_retention))
            alpha = max(1, legacy_floor, authored_floor)
            draw.line([a, b], fill=alpha, width=width, joint="curve")

        # Preserve a graphite core rather than replacing it with a flat digital band.
        # This page-fixed modulation is intentionally subtle and cannot remove the core
        # floor; the expressive shoulder still carries the stronger dry/tooth behavior.
        arr = np.asarray(mask, dtype=np.float32)
        active = arr > 0.5
        if np.any(active):
            height, width = arr.shape
            yy, xx = np.indices((height, width), dtype=np.float64)
            lx = (xx + float(x0)) / float(factor)
            ly = (yy + float(y0)) / float(factor)
            tooth = module._pixel_hash_tooth(lx, ly, 17).astype(np.float32)
            texture_strength = np.float32(
                0.025 + 0.055 * module._clamp01(policy["grain_exposure"])
            )
            modulation = (
                np.float32(1.0)
                + texture_strength
                * (tooth - np.float32(0.5))
                * np.float32(2.0)
            )
            arr[active] *= modulation[active]
            mask = Image.fromarray(
                np.clip(arr, 0.0, 255.0).astype(np.uint8), mode="L"
            )
        return mask

    module._continuity_floor_mask = _continuity_floor_mask
    module._img2drawing_value_authority_v2 = True


__all__ = ["install_v10_value_authority_core"]
