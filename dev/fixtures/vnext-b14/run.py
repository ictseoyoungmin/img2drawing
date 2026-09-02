"""Build deterministic B14 mode and authority integration sessions."""

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
    DRAWING_MODES,
    DrawingIntent,
    DrawingSession,
    ReferenceAuthority,
    ReferenceConstraint,
)


def _exercise(session: DrawingSession, case_dir: Path) -> dict:
    mode = session.intent.drawing_mode
    observation_id = session.observe(
        {
            "mode": mode,
            "authority": session.reference_authority.mode,
            "question": "dominant authored relation",
        }
    )
    session.draw(
        ((6, 39), (27, 13), (56, 29)),
        part=f"{mode}_dominant_relation",
        observation_id=observation_id,
    )
    if mode == "tonal_study":
        session.fill_region(
            ((9, 10), (37, 10), (37, 34), (9, 34)),
            value=150,
            part="large_shadow_family",
            observation_id=observation_id,
        )
    session.inspect()
    render = session.render_final(case_dir / "final.png")
    resumed = DrawingSession.resume(session.checkpoint_path, subject=session.subject)
    manifest_path = case_dir / session.inspection_history[-1]["manifest"]
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    return {
        "mode": mode,
        "authority": session.reference_authority.mode,
        "guide_id": session.mode_guide.guide_id,
        "history_cursor": session.history_cursor,
        "action_kinds": [action.action for action in session._agent.history.actions],
        "artifacts": sorted(manifest["artifacts"]),
        "resume_state_match": resumed.drawing_state_hash() == session.drawing_state_hash(),
        "resume_guide_match": resumed.mode_guide == session.mode_guide,
        "final_png": render.path.name,
        "session_type": f"{type(session).__module__}.{type(session).__qualname__}",
        "history_type": f"{type(session._agent.history).__module__}.{type(session._agent.history).__qualname__}",
    }


def run_fixture(output_dir: str | Path) -> dict:
    output = Path(output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)
    subject = output / "synthetic-subject.png"
    Image.new("RGB", (64, 48), (241, 239, 235)).save(subject)
    subject_sha256 = hashlib.sha256(subject.read_bytes()).hexdigest()

    sessions: list[tuple[str, DrawingSession]] = []
    for mode in DRAWING_MODES:
        case = f"observed-{mode.replace('_', '-')}"
        sessions.append(
            (
                case,
                DrawingSession.create(
                    subject=subject,
                    output_dir=output / case,
                    session_id=f"b14-{case}",
                    intent=DrawingIntent(reference_mode="observed", drawing_mode=mode),
                ),
            )
        )

    sessions.extend(
        (
            (
                "imaginative-free-draw",
                DrawingSession.create(
                    canvas=(64, 48),
                    output_dir=output / "imaginative-free-draw",
                    session_id="b14-imaginative-free-draw",
                    intent=DrawingIntent(reference_mode="imaginative", drawing_mode="free_draw"),
                    reference_authority=ReferenceAuthority.imaginative(
                        ("large rising shape against a small counter-shape",)
                    ),
                ),
            ),
            (
                "hybrid-free-draw",
                DrawingSession.create(
                    subject=subject,
                    output_dir=output / "hybrid-free-draw",
                    session_id="b14-hybrid-free-draw",
                    intent=DrawingIntent(reference_mode="hybrid", drawing_mode="free_draw"),
                    reference_authority=ReferenceAuthority.hybrid(
                        subject_sha256,
                        (
                            ReferenceConstraint(
                                "gesture", "preserve the rising gesture", "preserved"
                            ),
                            ReferenceConstraint(
                                "silhouette",
                                "transform the outer silhouette",
                                "transformed",
                                transformation="widen the upper arc",
                                rationale="fixture shape-language variation",
                            ),
                        ),
                    ),
                ),
            ),
        )
    )

    cases = [{"case": name, **_exercise(session, output / name)} for name, session in sessions]
    trace = {
        "schema": "img2drawing.vnext.b14_fixture.v1",
        "quality_claim": "mechanical-only",
        "declared_modes": list(DRAWING_MODES),
        "resolved_modes": sorted({case["mode"] for case in cases}),
        "one_session_type": len({case["session_type"] for case in cases}) == 1,
        "one_history_type": len({case["history_type"] for case in cases}) == 1,
        "cases": cases,
    }
    (output / "b14_trace.json").write_text(
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
