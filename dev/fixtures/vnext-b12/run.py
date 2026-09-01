"""Build the deterministic B12 R23-to-vNext compatibility fixture."""

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

from img2drawing.legacy.r23 import (  # noqa: E402
    DrawingRun,
    ObservationContract,
    ViewObservation,
    inspect_checkpoint,
    migrate_checkpoint,
)


def run_fixture(output_dir: str | Path) -> dict:
    output = Path(output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)
    subject = output / "synthetic-subject.png"
    Image.new("RGB", (64, 80), (238, 236, 231)).save(subject)
    legacy = DrawingRun.create(
        subject,
        output / "legacy",
        session_id="vnext-b12-legacy-boundary",
        working_supersample=2,
    )
    legacy.lock_observation(
        ObservationContract(
            subject_summary="Synthetic compatibility subject.",
            view=ViewObservation(
                body_view="front",
                torso_turn="none",
                near_side="unknown",
                arm_visibility={"subject_left": "visible", "subject_right": "visible"},
                arm_occlusion={"subject_left": (), "subject_right": ()},
            ),
        )
    )
    legacy.stage_start("P1_gesture")
    legacy.draw(
        {
            "action_id": "fixture-line-1",
            "kind": "draw_stroke",
            "stage": "P1_gesture",
            "role": "gesture",
            "part": "line_of_action",
            "points": [[12, 8], [28, 38], [42, 70]],
            "stroke_id": "fixture-stroke-1",
            "tool": {
                "preset": "construction_pencil",
                "grade": "HB",
                "overrides": {"pressure": 0.3, "width": 1.2, "opacity": 0.4},
            },
            "observation_id": "fixture-observation-1",
            "source_observation": "Synthetic compatibility observation.",
        }
    )
    source_checkpoint = legacy.output_dir / "session" / "checkpoint.json"
    info = inspect_checkpoint(source_checkpoint)
    migrated = migrate_checkpoint(source_checkpoint, output_dir=output / "vnext")
    payload = json.loads(migrated.checkpoint_path.read_text(encoding="utf-8"))
    trace = {
        "schema": "img2drawing.vnext.b12_fixture.v1",
        "quality_claim": "mechanical-only",
        "source": info.to_dict(),
        "target_checkpoint": migrated.checkpoint_path.name,
        "session_id_preserved": migrated.session_id == legacy.session_id,
        "history_cursor_preserved": migrated.history_cursor == legacy.session.history.cursor,
        "action_log_preserved": (
            payload["history"]["actions"]
            == json.loads(source_checkpoint.read_text(encoding="utf-8"))["agent_session"]["history"]["actions"]
        ),
        "target_state_sha256": migrated.drawing_state_hash(),
        "source_renderer_provenance": payload["metadata"]["migration"]["source"]["renderer"],
        "target_render_profile": payload["render_profile"],
        "legacy_orchestration_absent": all(
            key not in payload for key in ("progress", "reviews", "reopens", "stage_registry")
        ),
    }
    # Keep the fixture trace portable even though the inspection helper returns
    # an absolute convenience path to callers.
    trace["source"]["checkpoint"] = source_checkpoint.name
    (output / "b12_trace.json").write_text(
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
