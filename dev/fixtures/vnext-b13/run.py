"""Build deterministic observed, imaginative, and hybrid B13 sessions."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "skills" / "img2drawing" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from img2drawing import (  # noqa: E402
    DrawingIntent,
    DrawingSession,
    ReferenceAuthority,
    ReferenceConstraint,
)


def _exercise(session: DrawingSession, root: Path) -> dict:
    observation_id = session.observe(
        {"authority": session.reference_authority.mode, "question": "major diagonal balance"},
        observation_id=f"{session.reference_authority.mode}-read",
    )
    session.draw(
        ((6, 8), (24, 22), (50, 38)),
        part="major_diagonal",
        observation_id=observation_id,
    )
    session.inspect()
    render = session.render_final(root / "final.png")
    resumed = DrawingSession.resume(
        session.checkpoint_path,
        subject=session.subject,
    )
    manifest_path = root / "inspections" / "000001" / "inspection.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    return {
        "mode": session.reference_authority.mode,
        "has_reference": session.has_reference,
        "authority_digest": session.reference_authority.digest(),
        "drawing_state_sha256": session.drawing_state_hash(),
        "resume_state_match": resumed.drawing_state_hash() == session.drawing_state_hash(),
        "artifacts": sorted(manifest["artifacts"]),
        "subject_input": manifest["inputs"]["subject"],
        "final_png": render.path.name,
    }


def run_fixture(output_dir: str | Path) -> dict:
    output = Path(output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)
    subject = output / "synthetic-subject.png"
    Image.new("RGB", (64, 48), (240, 238, 232)).save(subject)
    subject_sha256 = hashlib.sha256(subject.read_bytes()).hexdigest()

    observed = DrawingSession.create(
        subject=subject,
        output_dir=output / "observed",
        session_id="b13-observed",
        intent=DrawingIntent(reference_mode="observed"),
    )
    imaginative = DrawingSession.create(
        canvas=(64, 48),
        output_dir=output / "imaginative",
        session_id="b13-imaginative",
        intent=DrawingIntent(reference_mode="imaginative", drawing_mode="free_draw"),
        reference_authority=ReferenceAuthority.imaginative(
            ("a strong ascending diagonal balances a small lower-right counter-shape",)
        ),
    )
    hybrid = DrawingSession.create(
        subject=subject,
        output_dir=output / "hybrid",
        session_id="b13-hybrid",
        intent=DrawingIntent(reference_mode="hybrid", drawing_mode="figure_drawing"),
        reference_authority=ReferenceAuthority.hybrid(
            subject_sha256,
            (
                ReferenceConstraint("pose", "preserve the weight-bearing diagonal", "preserved"),
                ReferenceConstraint(
                    "prop",
                    "transform the photographed prop",
                    "transformed",
                    transformation="replace it with a flowing ribbon",
                    rationale="fixture concept transformation",
                ),
            ),
        ),
    )
    trace = {
        "schema": "img2drawing.vnext.b13_fixture.v1",
        "quality_claim": "mechanical-only",
        "sessions": [
            _exercise(observed, output / "observed"),
            _exercise(imaginative, output / "imaginative"),
            _exercise(hybrid, output / "hybrid"),
        ],
        "one_session_type": len({type(observed), type(imaginative), type(hybrid)}) == 1,
    }
    (output / "b13_trace.json").write_text(
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
