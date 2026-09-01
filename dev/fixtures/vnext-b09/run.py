"""Build the deterministic B09 finish-authoring contract fixture."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "skills" / "img2drawing" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from img2drawing import DrawingIntent, DrawingSession, resolve_finish_guide


INTENTS = ("pose", "subject", "form_light", "expressive")


def _synthetic_subject(path: Path) -> None:
    image = Image.new("RGB", (96, 96), (244, 242, 236))
    draw = ImageDraw.Draw(image)
    draw.ellipse((34, 8, 55, 29), fill=(180, 180, 176))
    draw.polygon(((29, 29), (61, 27), (67, 68), (23, 70)), fill=(154, 156, 158))
    draw.polygon(((56, 30), (78, 39), (70, 74), (57, 62)), fill=(118, 121, 124))
    draw.rectangle((53, 55, 68, 69), fill=(92, 95, 98))
    draw.line(((61, 34), (68, 56), (63, 67)), fill=(46, 47, 48), width=5)
    image.save(path)


def _actions_since(session: DrawingSession, cursor: int) -> list[dict]:
    payload = json.loads(session.checkpoint_path.read_text(encoding="utf-8"))
    return payload["history"]["actions"][cursor:]


def run_fixture(output_dir: str | Path) -> dict:
    output = Path(output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)
    subject = output / "synthetic-subject.png"
    _synthetic_subject(subject)

    session = DrawingSession.create(
        subject=subject,
        output_dir=output / "session",
        session_id="vnext-b09-finish-authoring",
        metadata={"fixture": "B09", "quality_claim": "mechanical-only"},
        intent=DrawingIntent(finish_intent="pose"),
    )
    decisions: dict[str, dict] = {}

    def capture(finish_intent: str, author) -> None:
        if session.intent is None or session.intent.finish_intent != finish_intent:
            assert session.intent is not None
            session.set_intent(
                DrawingIntent(
                    reference_mode=session.intent.reference_mode,
                    drawing_mode=session.intent.drawing_mode,
                    finish_intent=finish_intent,
                    style_profile=session.intent.style_profile,
                ),
                reason=f"B09 fixture selects {finish_intent} authoring policy",
            )
        before = session.history_cursor
        author()
        actions = _actions_since(session, before)
        decisions[finish_intent] = {
            "guide_id": resolve_finish_guide(finish_intent).guide_id,
            "cursor_before": before,
            "cursor_after": session.history_cursor,
            "actions": [
                {
                    "kind": action["action"],
                    "part": action.get("part"),
                    "role": action.get("role"),
                    "finish_intent": (
                        (action.get("provenance") or {}).get("metadata") or {}
                    ).get("finish_intent"),
                }
                for action in actions
            ],
        }

    capture(
        "pose",
        lambda: session.draw(
            ((43, 21), (45, 41), (42, 64), (39, 84)),
            action_id="finish-pose-weight-path",
            role="selected_contour",
            part="whole_pose/weight_path",
            source_observation="synthetic dominant flow and support path",
            metadata={"finish_intent": "pose", "decision": "retain economical weight path"},
        ),
    )
    capture(
        "subject",
        lambda: session.draw(
            ((61, 51), (67, 57), (63, 67)),
            action_id="finish-subject-pocket-hand",
            role="identity_relation",
            part="hands_and_feet/pocket_contact",
            source_observation="synthetic forearm terminates partly inside pocket opening",
            metadata={
                "finish_intent": "subject",
                "decision": "show visible contact and stop at occlusion",
            },
        ),
    )
    capture(
        "form_light",
        lambda: session.fill_region(
            ((48, 30), (67, 34), (65, 68), (45, 65)),
            value=126,
            part="light_shadow_families/arm_shadow",
            fill_id="finish-form-light-arm-shadow",
            source_observation="synthetic arm belongs to one connected shadow family",
            reason="one broad observed value family after line-only form preflight",
            metadata={
                "finish_intent": "form_light",
                "decision": "group one broad calibrated value region",
            },
        ),
    )
    capture(
        "expressive",
        lambda: session.draw(
            ((27, 31), (38, 26), (56, 27), (66, 34)),
            action_id="finish-expressive-shoulder-rhythm",
            role="focal_accent",
            part="rhythm_and_simplification/shoulder_arc",
            pressure=(0.35, 0.65, 0.9, 0.5),
            source_observation="synthetic shoulder-to-arm arc is the selected focal rhythm",
            metadata={
                "finish_intent": "expressive",
                "decision": "accent focal arc while preserving arm contact",
                "preserved_constraints": ["arm thickness", "pocket contact"],
            },
        ),
    )

    payload = json.loads(session.checkpoint_path.read_text(encoding="utf-8"))
    trace = {
        "schema": "img2drawing.vnext.b09_finish_fixture.v1",
        "quality_claim": "mechanical-only",
        "session_id": session.session_id,
        "session_schema": payload["schema"],
        "renderer": payload["renderer"],
        "history_cursor": session.history_cursor,
        "intent_event_count": len(session.intent_history),
        "intent_order": list(INTENTS),
        "decisions": decisions,
    }
    (output / "b09_finish_trace.json").write_text(
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
