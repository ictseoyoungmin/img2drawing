from __future__ import annotations

import pytest
from PIL import Image

from img2drawing import RenderProfile
from img2drawing.core.ir import Stroke, StrokeIR
from img2drawing.render import (
    RENDERER_CONTRACT_DIGEST,
    RENDERER_ID,
    RENDERER_VERSION,
    UnsupportedRendererError,
    render_image,
)


def _v103_profile_dict(**overrides) -> dict:
    raw = {
        "schema": "img2drawing.vnext.render_profile.v1",
        "profile_id": "pencil-contact-canonical-v1",
        "renderer_id": "pillow-pencil-contact-v11",
        "renderer_version": "1",
        "canvas_width": 64,
        "canvas_height": 48,
        "material_profile": "builtin:pencil-contact",
        "paper_tooth": 0.46,
        "paper_scale": 1.0,
        "paper_seed": 170817,
        "supersample": 4,
        "output_scale": 1,
        "background_rgba": [255, 255, 255, 255],
        "graphite_rgb": [36, 34, 32],
        "seed_domain": "pencil-contact-stroke-and-paper-coordinate-v1",
        "compositing": "rgba-source-over-background-v1",
        "png_mode": "RGBA",
        "gif_palette_colors": 256,
        "gif_loop": 0,
        "gif_disposal": 2,
    }
    raw.update(overrides)
    return raw


def test_canonical_profile_binds_current_identity_and_contract_digest() -> None:
    profile = RenderProfile.canonical(64, 48)
    assert (profile.renderer_id, profile.renderer_version) == (RENDERER_ID, RENDERER_VERSION)
    assert profile.renderer_contract_digest == RENDERER_CONTRACT_DIGEST
    assert profile.to_dict()["renderer_contract_digest"] == RENDERER_CONTRACT_DIGEST
    assert RenderProfile.from_dict(profile.to_dict()) == profile


def test_v103_v11_profile_resumes_under_current_renderer() -> None:
    profile = RenderProfile.from_dict(_v103_profile_dict())
    assert (profile.renderer_id, profile.renderer_version) == (RENDERER_ID, RENDERER_VERSION)
    assert profile.renderer_contract_digest == RENDERER_CONTRACT_DIGEST


@pytest.mark.parametrize("identity", [("pillow-pencil-contact-v9", "1"), ("pillow-pencil-contact-v10", "1"), ("unknown", "7")])
def test_historical_renderer_identities_fail_closed_with_release_hint(identity) -> None:
    with pytest.raises(UnsupportedRendererError, match="img2drawing==1.0.3"):
        RenderProfile.from_dict(_v103_profile_dict(renderer_id=identity[0], renderer_version=identity[1]))


def test_foreign_contract_digest_fails_closed() -> None:
    raw = RenderProfile.canonical(64, 48).to_dict()
    raw["renderer_contract_digest"] = "0" * 64
    with pytest.raises(UnsupportedRendererError, match="different renderer contract"):
        RenderProfile.from_dict(raw)


def test_broad_stroke_clipped_by_canvas_edge_renders() -> None:
    """v1.0.3 closed the returned mask when a broad patch had no active pixels."""

    ir = StrokeIR(80, 40, [
        Stroke([(10.0, 39.0), (70.0, 45.0)], width=16.0, opacity=0.9, stroke_id="edge"),
        Stroke([(10.0, 60.0), (70.0, 70.0)], width=16.0, opacity=0.9, stroke_id="outside"),
    ])
    image = render_image(ir, supersample=2)
    assert image.size == (80, 40)
    assert isinstance(image, Image.Image)


def test_region_fill_history_points_to_last_supporting_release() -> None:
    from img2drawing.core.history import CanvasAction, CanvasHistory

    history = CanvasHistory(32, 32)
    history.actions.append(CanvasAction(1, "region.fill", "vnext", {"region": {}}))
    history.cursor = 1
    with pytest.raises(ValueError, match="img2drawing==1.0.3"):
        history.state_at()
