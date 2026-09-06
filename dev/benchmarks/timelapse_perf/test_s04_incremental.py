from __future__ import annotations

from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from img2drawing.provenance.timelapse import select_cursors
from make_fixture import build_fixture
from run_baseline import make_session
from cached_pencil_renderer import StrokeRasterCache, render_cached
from incremental_pencil_renderer import IncrementalAddOnlyPencilCanvas


def test_incremental_add_only_matches_s02_cached_pixels(tmp_path: Path) -> None:
    session = make_session(build_fixture(), tmp_path / "work", 2)
    profile = session.render_profile
    assert profile is not None
    cursors = select_cursors(session._agent, "every_n", every_n=4)
    cache = StrokeRasterCache()
    initial = profile.prepared_ir(session._agent.history.state_at(0))
    canvas = IncrementalAddOnlyPencilCanvas(initial, cache, **profile.renderer_kwargs())
    try:
        for i, cursor in enumerate(cursors):
            ir = profile.prepared_ir(session._agent.history.state_at(cursor))
            canvas.advance_to(ir)
            inc = tmp_path / f"inc_{i}.png"
            ref = tmp_path / f"ref_{i}.png"
            canvas.snapshot_dirty(inc)
            render_cached(ir, ref, cache, **profile.renderer_kwargs())
            assert inc.read_bytes() == ref.read_bytes()
        assert canvas.stats.strokes_composited == 48
        assert cache.entries == 48
    finally:
        canvas.close()
        cache.close()
