from __future__ import annotations

from img2drawing.runtime import runtime_capabilities


def test_runtime_capability_manifest_is_source_opaque() -> None:
    caps = runtime_capabilities()
    assert caps.orchestration == "DrawingSession"
    assert caps.final_authoring_runtime is True
    assert caps.implementation_read_required is False
    assert caps.bespoke_raster_authoring_supported is False
    assert caps.capability_gap_policy == "report-not-bypass"

    payload = caps.to_dict()
    text = str(payload).lower()
    assert "renderer class" not in text
    assert "cache path" not in text
    assert "src/" not in text
    assert "private module" not in text


def test_manifest_exposes_public_authoring_not_private_implementation() -> None:
    caps = runtime_capabilities()
    assert "draw" in caps.supported_authoring_operations
    assert "inspect" in caps.supported_authoring_operations
    assert "replay" in caps.supported_authoring_operations
    assert "timelapse" in caps.supported_authoring_operations
    assert "img2drawing.vnext" in caps.public_namespaces
    assert "img2drawing.runtime" in caps.public_namespaces
    assert all("._" not in name for name in caps.public_namespaces)


def test_bespoke_raster_authoring_is_explicitly_not_supported() -> None:
    caps = runtime_capabilities()
    bypasses = " ".join(caps.prohibited_final_authoring_bypasses).lower()
    assert "pillow" in bypasses
    assert "opencv" in bypasses
    assert "svg" in bypasses or "canvas" in bypasses
