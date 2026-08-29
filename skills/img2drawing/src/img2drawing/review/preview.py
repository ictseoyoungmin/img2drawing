from __future__ import annotations

"""Fast, explicitly non-authoritative render previews."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..core.session import sha256_obj, strokeir_canonical_dict
from ..render.pillow_pencil_contact import render as render_pencil


@dataclass(frozen=True)
class PreviewArtifact:
    path: Path
    state_sha256: str
    renderer_id: str
    supersample: int
    evidence_role: str = "preview_only"

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "img2drawing.preview_artifact.v1",
            "path": str(self.path),
            "state_sha256": self.state_sha256,
            "renderer_id": self.renderer_id,
            "supersample": self.supersample,
            "evidence_role": self.evidence_role,
            "authority": "preview_not_review_final_replay_or_timelapse_evidence",
        }


def render_preview(ir, path: str | Path, *, supersample: int = 1) -> PreviewArtifact:
    """Render a quick view without changing the supplied IR or review state."""

    factor = max(1, int(supersample))
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    render_pencil(ir, target, supersample=factor)
    return PreviewArtifact(
        path=target.resolve(),
        state_sha256=sha256_obj(strokeir_canonical_dict(ir)),
        renderer_id="pillow-pencil-contact-v9",
        supersample=factor,
    )


__all__ = ["PreviewArtifact", "render_preview"]
