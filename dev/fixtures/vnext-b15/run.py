"""Build deterministic B15 style selection and explicit-edit evidence."""

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
    STYLE_PROFILES,
    DrawingIntent,
    DrawingSession,
    StyleGuide,
    resolve_style_guide,
)


POINTS = ((7, 9), (27, 19), (54, 36))


def _digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _preset_case(subject: Path, root: Path, profile: str) -> tuple[DrawingSession, dict]:
    session = DrawingSession.create(
        subject=subject,
        output_dir=root,
        session_id=f"b15-{profile.replace('_', '-')}",
        intent=DrawingIntent(style_profile=profile),
    )
    session.draw(POINTS, stroke_id="shared-geometry", part="gesture")
    artifact = session.render_final(root / "final.png")
    resumed = DrawingSession.resume(session.checkpoint_path, subject=subject)
    guide = resolve_style_guide(profile)
    return session, {
        "style_profile": profile,
        "style_guide": guide.to_dict(),
        "drawing_state_hash": session.drawing_state_hash(),
        "render_profile_digest": session.render_profile.digest(),
        "png_sha256": _digest(artifact.path),
        "history_cursor": session.history_cursor,
        "resume_state_match": resumed.drawing_state_hash() == session.drawing_state_hash(),
        "session_type": f"{type(session).__module__}.{type(session).__qualname__}",
        "history_type": f"{type(session._agent.history).__module__}.{type(session._agent.history).__qualname__}",
    }


def _custom_guide() -> StyleGuide:
    return StyleGuide.custom(
        "custom:angular-quiet",
        line_behavior=("use angular deliberate line changes",),
        construction_visibility=("retain only composition-bearing axes",),
        detail_policy=("keep detail sparse outside the focal shape",),
        value_policy=("use one quiet supporting value family",),
        edge_policy=("reserve the sharpest edge for the focal turn",),
        authoring_notes=("preserve subject geometry and declared constraints",),
    )


def run_fixture(output_dir: str | Path) -> dict:
    output = Path(output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)
    subject = output / "synthetic-subject.png"
    Image.new("RGB", (64, 48), (242, 240, 236)).save(subject)

    preset_pairs = [
        _preset_case(subject, output / profile, profile) for profile in STYLE_PROFILES
    ]
    sessions = [pair[0] for pair in preset_pairs]
    preset_cases = [pair[1] for pair in preset_pairs]

    edited = DrawingSession.create(
        subject=subject,
        output_dir=output / "mid-session-edit",
        session_id="b15-mid-session-edit",
        intent=DrawingIntent(style_profile="pencil_loose"),
    )
    edited.draw(POINTS, stroke_id="style-target", part="gesture")
    before_hash = edited.drawing_state_hash()
    before_cursor = edited.history_cursor
    before_profile = edited.render_profile.digest()
    event = edited.set_intent(
        DrawingIntent(style_profile="graphite_tonal"),
        reason="continue with grouped tonal authoring",
    )
    after_selection_hash = edited.drawing_state_hash()
    after_selection_cursor = edited.history_cursor
    edited.replace_stroke(
        "style-target",
        ((7, 9), (31, 17), (54, 36)),
        stroke_id="style-target-revised",
        part="gesture",
        reason="explicitly revise the focal turn under the new authoring policy",
    )
    resumed = DrawingSession.resume(edited.checkpoint_path, subject=subject)

    custom = _custom_guide()
    trace = {
        "schema": "img2drawing.vnext.b15_fixture.v1",
        "quality_claim": "mechanical-only",
        "preset_cases": preset_cases,
        "preset_geometry_equal": len({case["drawing_state_hash"] for case in preset_cases}) == 1,
        "preset_render_profiles_equal": len({case["render_profile_digest"] for case in preset_cases}) == 1,
        "preset_pngs_equal": len({case["png_sha256"] for case in preset_cases}) == 1,
        "one_session_type": len({case["session_type"] for case in preset_cases}) == 1,
        "one_history_type": len({case["history_type"] for case in preset_cases}) == 1,
        "mid_session": {
            "event_cursor": event.history_cursor,
            "selection_preserved_state": after_selection_hash == before_hash,
            "selection_preserved_cursor": after_selection_cursor == before_cursor,
            "selection_preserved_render_profile": edited.render_profile.digest() == before_profile,
            "explicit_edit_advanced_cursor": edited.history_cursor == before_cursor + 1,
            "explicit_edit_changed_state": edited.drawing_state_hash() != before_hash,
            "resume_state_match": resumed.drawing_state_hash() == edited.drawing_state_hash(),
            "resume_style_profile": resumed.intent.style_profile,
        },
        "custom_guide": custom.to_dict(),
        "custom_roundtrip": StyleGuide.from_dict(custom.to_dict()) == custom,
    }
    (output / "b15_trace.json").write_text(
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
