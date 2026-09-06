from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from img2drawing.render import pillow_paper_interaction as p5
from material_field_kernel import paper_field_grid
from run_s03_material_kernel import run
from make_fixture import build_fixture
from run_baseline import make_session


def test_material_field_grid_is_exact_and_replay_pixels_match(tmp_path: Path) -> None:
    direct = p5.paper_field(
        (311, 499), factor=4.0, global_origin=(247, 319),
        paper_scale=1.0, paper_seed=170817,
    )
    optimized = paper_field_grid(
        (311, 499), factor=4.0, global_origin=(247, 319),
        paper_scale=1.0, paper_seed=170817,
    )
    assert np.array_equal(direct, optimized)

    session = make_session(build_fixture(), tmp_path / "fixture", 2)
    baseline = run(session, tmp_path / "baseline", every_n=8, kernel=False, write_gif=False)
    kernel = run(session, tmp_path / "kernel", every_n=8, kernel=True, write_gif=False)
    assert baseline["frame_hashes"] == kernel["frame_hashes"]
