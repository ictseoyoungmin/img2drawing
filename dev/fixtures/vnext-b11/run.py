"""Build the deterministic B11 render/replay/GIF parity fixture."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "skills" / "img2drawing" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from img2drawing import DrawingIntent, DrawingSession, RenderProfile


def run_fixture(output_dir: str | Path) -> dict:
    output = Path(output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)
    subject = output / "synthetic-subject.png"
    Image.new("RGB", (64, 64), (244, 242, 236)).save(subject)
    profile = RenderProfile.from_dict(
        {**RenderProfile.canonical(64, 64).to_dict(), "supersample": 2}
    )
    session = DrawingSession.create(
        subject=subject,
        output_dir=output / "session",
        session_id="vnext-b11-render-replay",
        intent=DrawingIntent(finish_intent="form_light"),
        render_profile=profile,
    )
    session.draw(((8, 10), (25, 29), (31, 54)), part="gesture")
    session.draw(((33, 9), (44, 27), (51, 53)), part="selected_contour")
    session.fill_region(
        ((17, 23), (44, 20), (49, 49), (20, 52)),
        value=146,
        part="shadow_family",
        fill_id="fixture-shadow",
    )
    before_hash = session.drawing_state_hash()
    export = session.export_timelapse(output / "export", mode="action")
    direct = session.render_final(output / "direct-final.png")
    trace = {
        "schema": "img2drawing.vnext.b11_fixture.v1",
        "quality_claim": "mechanical-only",
        "session_id": session.session_id,
        "history_cursor": session.history_cursor,
        "history_unchanged": session.drawing_state_hash() == before_hash,
        "render_profile": profile.to_dict(),
        "render_profile_digest": profile.digest(),
        "frame_cursors": [frame["cursor"] for frame in export.manifest["frames"]],
        "frame_actions": [frame["action"] for frame in export.manifest["frames"]],
        "final_png_pixel_match": (
            direct.pixel_sha256 == export.manifest["final"]["pixel_sha256"]
        ),
        "gif": export.manifest["gif"],
        "sampling": export.manifest["sampling"],
        "timing": export.manifest["timing"],
        "budget": export.manifest["budget"],
    }
    (output / "b11_trace.json").write_text(
        json.dumps(trace, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8"
    )
    return trace


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(run_fixture(args.output), indent=2, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
