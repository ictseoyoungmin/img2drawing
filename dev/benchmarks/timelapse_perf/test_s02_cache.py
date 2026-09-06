from __future__ import annotations

import hashlib
from pathlib import Path

from PIL import Image

from cached_pencil_renderer import StrokeRasterCache, render_cached
from make_fixture import build_fixture
from run_baseline import make_session
from img2drawing.render.pillow_pencil_contact import render as canonical_render


def _pixel_hash(path: Path) -> str:
    with Image.open(path) as im:
        return hashlib.sha256(im.convert("RGBA").tobytes()).hexdigest()


def test_s02_cache_reuses_identical_strokes_and_preserves_pixels(tmp_path: Path) -> None:
    # Keep CI quick: only first four strokes and ss2, but compare exact canonical pixels.
    fixture = build_fixture()
    fixture["strokes"] = fixture["strokes"][:4]
    session = make_session(fixture, tmp_path / "session", supersample=2)
    profile = session.render_profile
    assert profile is not None
    cache = StrokeRasterCache()
    try:
        for cursor in (2, 4):
            ir = session._agent.history.state_at(cursor)
            prepared = profile.prepared_ir(ir)
            expected = tmp_path / f"expected_{cursor}.png"
            actual = tmp_path / f"actual_{cursor}.png"
            canonical_render(prepared, expected, **profile.renderer_kwargs())
            render_cached(prepared, actual, cache, **profile.renderer_kwargs())
            assert _pixel_hash(actual) == _pixel_hash(expected)
        assert cache.misses == 4
        # first two strokes hit again in cursor 4, while strokes 3-4 are new misses
        assert cache.hits == 2
        assert cache.entries == 4
    finally:
        cache.close()
