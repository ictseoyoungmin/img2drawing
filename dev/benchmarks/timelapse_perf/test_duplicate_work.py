from __future__ import annotations

import importlib.util
from pathlib import Path


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("timelapse_duplicate_work", HERE / "analyze_duplicate_work.py")
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_fixture_48_duplicate_work_contract(tmp_path: Path) -> None:
    session = MODULE.make_fixture_session(None, 4, tmp_path / "session")
    result = MODULE.summarize_duplicate_work(session, every_n=4)

    assert result["cursors"] == list(range(0, 49, 4))
    assert result["sampled_frames"] == 13
    assert result["stroke_material_passes_in_sampled_frames"] == 312
    assert result["extra_final_render_stroke_passes"] == 48
    assert result["total_stroke_material_passes"] == 360
    assert result["duplicate_stroke_material_passes"] == 312
    assert result["duplication_factor_vs_unique"] == 7.5
    assert result["actual_full_render_calls"] == 14
