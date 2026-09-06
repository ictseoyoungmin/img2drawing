from __future__ import annotations

"""S03 prototype: exact low-allocation kernels for deterministic material fields.

The canonical value-noise math is unchanged. The optimization exploits the fact
that raster x/y page coordinates are separable: x terms vary only by column and
y terms only by row. The legacy kernel expands both coordinate grids eagerly;
this prototype keeps 1-D coordinate bases and relies on NumPy broadcasting for
the same 2-D hash/value-noise result.
"""

import numpy as np

from img2drawing.render import pillow_paper_interaction as p5


def value_noise_grid(
    shape: tuple[int, int],
    *,
    factor: float,
    global_origin: tuple[int, int],
    cell: float,
    seed: int,
    x_scale: float = 1.0,
    y_scale: float = 1.0,
) -> np.ndarray:
    hh, ww = int(shape[0]), int(shape[1])
    ox, oy = int(global_origin[0]), int(global_origin[1])
    cell = max(0.08, float(cell))

    xx = np.arange(ww, dtype=np.float64)
    yy = np.arange(hh, dtype=np.float64)
    lx = ((xx + float(ox)) / float(factor)) * float(x_scale)
    ly = ((yy + float(oy)) / float(factor)) * float(y_scale)
    gx = lx / cell
    gy = ly / cell

    x0 = np.floor(gx).astype(np.int64)
    y0 = np.floor(gy).astype(np.int64)
    tx = p5._smoothstep(gx - x0)[None, :]
    ty = p5._smoothstep(gy - y0)[:, None]
    x0 = x0[None, :]
    y0 = y0[:, None]

    a = p5._hash01(x0, y0, seed)
    b = p5._hash01(x0 + 1, y0, seed)
    c = p5._hash01(x0, y0 + 1, seed)
    d = p5._hash01(x0 + 1, y0 + 1, seed)
    ab = a + (b - a) * tx
    cd = c + (d - c) * tx
    return ab + (cd - ab) * ty


def paper_field_grid(
    shape: tuple[int, int],
    *,
    factor: float,
    global_origin: tuple[int, int],
    paper_scale: float,
    paper_seed: int,
) -> np.ndarray:
    s = float(paper_scale)
    coarse = value_noise_grid(
        shape, factor=factor, global_origin=global_origin,
        cell=1.85 * s, seed=paper_seed ^ 0xA24BAED4,
    )
    mid = value_noise_grid(
        shape, factor=factor, global_origin=global_origin,
        cell=0.72 * s, seed=paper_seed ^ 0x9FB21C65,
    )
    fine = value_noise_grid(
        shape, factor=factor, global_origin=global_origin,
        cell=0.29 * s, seed=paper_seed ^ 0xC13FA9A9,
    )
    fibre_y = value_noise_grid(
        shape, factor=factor, global_origin=global_origin,
        cell=0.43 * s, seed=paper_seed ^ 0x91E10DA5,
        x_scale=0.22,
    )
    fibre_x = value_noise_grid(
        shape, factor=factor, global_origin=global_origin,
        cell=0.61 * s, seed=paper_seed ^ 0xD1B54A35,
        y_scale=0.28,
    )
    field = (
        np.float32(0.33) * coarse
        + np.float32(0.34) * mid
        + np.float32(0.20) * fine
        + np.float32(0.08) * fibre_y
        + np.float32(0.05) * fibre_x
    )
    return np.clip(field, 0.0, 1.0).astype(np.float32)
