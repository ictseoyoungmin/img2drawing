from __future__ import annotations

import hashlib
from pathlib import Path

import pytest
from PIL import Image

from img2drawing.core.history import CanvasHistory
from img2drawing.core.ir import Stroke
from img2drawing.core.tools import get_tool
from img2drawing.render.pillow_pencil_contact import render as canonical_render

from img2drawing.provenance.fast_timelapse.delta_pack import DeltaPackWriter, iter_frames, read_info
from img2drawing.provenance.fast_timelapse.frame_source import (
    CanonicalFrameSource,
    FastFrameSource,
    FrameRenderConfig,
    make_frame_source,
)
from img2drawing.provenance.fast_timelapse.patch_cache import CACHE_SCHEMA, PatchCacheRenderer
from test_fast_timelapse_semantic_closure import _history_and_cursors, _stroke


def _rgba_hash(image: Image.Image) -> str:
    return hashlib.sha256(image.convert("RGBA").tobytes()).hexdigest()


def _sampled(limit: int, n: int) -> list[int]:
    out = list(range(0, limit + 1, n))
    if out[-1] != limit:
        out.append(limit)
    return out


def test_sampling_matrix_every_1_4_8_is_exact(tmp_path: Path):
    history, _ = _history_and_cursors()
    config = FrameRenderConfig((255, 255, 255, 255), (36, 34, 32), 1, 2)
    for every_n in (1, 4, 8):
        source = FastFrameSource(history, config)
        try:
            for cursor in _sampled(history.cursor, every_n):
                source.advance_to(cursor)
                got = source.image()
                ref = tmp_path / f"n{every_n}_c{cursor}.png"
                canonical_render(history.state_at(cursor), ref, supersample=2)
                with Image.open(ref) as expected:
                    assert _rgba_hash(got) == _rgba_hash(expected), (every_n, cursor)
                got.close()
        finally:
            source.close()


def test_ineligible_history_uses_explicit_canonical_fallback(tmp_path: Path):
    history = CanvasHistory(128, 96, metadata={"paper_tooth": 0.5, "paper_scale": 1.0, "paper_seed": 12})
    history.add_stroke(_stroke("a", [(10, 20), (90, 60)], [0.4, 0.7], layer=0), stroke_id="a")
    eraser_tool = get_tool("soft_eraser")
    raw = Stroke(
        points=[(30.0, 10.0), (50.0, 80.0)], width=8.0, opacity=1.0,
        role="correction", stage="legacy-raw-eraser", layer=1, stroke_id="e",
        pressure=[0.8, 0.8], pressure_authored=True, tool_state=eraser_tool.to_dict(),
    ).cleaned()
    history.add_stroke(raw, stroke_id="e")
    config = FrameRenderConfig((255, 255, 255, 255), (36, 34, 32), 1, 2)
    source = make_frame_source(history, config)
    assert isinstance(source, CanonicalFrameSource)
    try:
        info = source.advance_to(history.cursor)
        assert info["mode"] == "canonical-fallback"
        assert any("raw spatial eraser" in reason for reason in info["fallback_reasons"])
        got = source.image()
        ref = tmp_path / "canonical.png"
        canonical_render(history.state_at(history.cursor), ref, supersample=2)
        with Image.open(ref) as expected:
            assert _rgba_hash(got) == _rgba_hash(expected)
        got.close()
    finally:
        source.close()


def _renderer(**overrides) -> PatchCacheRenderer:
    args = dict(
        width=320, height=240, background=(255, 255, 255, 255), scale=1, supersample=2,
        graphite=(36, 34, 32), grade=None, tooth=0.58, paper_scale=1.0, paper_seed=77,
        contact_profile=None,
        cache_contract={
            "profile_id": "test-profile", "renderer_id": "pillow-pencil-contact-v9",
            "renderer_version": "1", "material_profile": "builtin:pencil-contact",
            "seed_domain": "seed-v1", "compositing": "rgba-source-over-background-v1",
        },
    )
    args.update(overrides)
    return PatchCacheRenderer(**args)


def test_patch_cache_invalidation_matrix():
    stroke = _stroke("k", [(20, 40), (120, 90), (240, 130)], [0.3, 0.8, 0.4], layer=0)
    base = _renderer()
    same = _renderer()
    variants = [
        _renderer(supersample=3),
        _renderer(graphite=(35, 34, 32)),
        _renderer(tooth=0.61),
        _renderer(paper_scale=1.25),
        _renderer(paper_seed=78),
        _renderer(cache_contract={
            "profile_id": "test-profile", "renderer_id": "pillow-pencil-contact-v9",
            "renderer_version": "2", "material_profile": "builtin:pencil-contact",
            "seed_domain": "seed-v1", "compositing": "rgba-source-over-background-v1",
        }),
        _renderer(cache_contract={
            "profile_id": "other-profile", "renderer_id": "pillow-pencil-contact-v9",
            "renderer_version": "1", "material_profile": "builtin:pencil-contact",
            "seed_domain": "seed-v1", "compositing": "rgba-source-over-background-v1",
        }),
    ]
    try:
        base_key = base._fingerprint(stroke)
        assert base._fingerprint(stroke) == same._fingerprint(stroke)
        assert CACHE_SCHEMA.endswith(".v2")
        for variant in variants:
            assert variant._fingerprint(stroke) != base_key
    finally:
        base.close(); same.close()
        for variant in variants:
            variant.close()


def test_delta_pack_is_atomic_and_recovers_from_partial_or_corrupt_staging(tmp_path: Path):
    target = tmp_path / "frames.idp"
    red = Image.new("RGB", (16, 12), (255, 0, 0))
    blue = Image.new("RGB", (16, 12), (0, 0, 255))
    try:
        with pytest.raises(RuntimeError, match="interrupt"):
            with DeltaPackWriter(target, width=16, height=12, frame_count=2) as writer:
                writer.write_frame(red, [(0, 0, 16, 12)])
                raise RuntimeError("interrupt")
        assert not target.exists()
        assert not target.with_name(target.name + ".partial").exists()

        # A stale partial from a hard interruption is discarded on the next attempt.
        partial = target.with_name(target.name + ".partial")
        partial.write_bytes(b"stale-partial")
        with DeltaPackWriter(target, width=16, height=12, frame_count=2) as writer:
            assert partial.exists()
            writer.write_frame(red, [(0, 0, 16, 12)])
            writer.write_frame(blue, [(0, 0, 16, 12)])
        assert target.exists() and not partial.exists()
        assert read_info(target).frame_count == 2
        frames = list(iter_frames(target))
        try:
            assert frames[0].getpixel((0, 0)) == (255, 0, 0)
            assert frames[1].getpixel((0, 0)) == (0, 0, 255)
        finally:
            for frame in frames:
                frame.close()

        target.write_bytes(target.read_bytes()[:25])
        with pytest.raises(ValueError):
            read_info(target)
        # Re-running from source-of-truth state atomically replaces the corrupt disposable pack.
        with DeltaPackWriter(target, width=16, height=12, frame_count=1) as writer:
            writer.write_frame(red, [(0, 0, 16, 12)])
        assert read_info(target).frame_count == 1
    finally:
        red.close(); blue.close()
