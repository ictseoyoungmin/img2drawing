"""Deterministic release-candidate workflows used by docs and clean-install smoke.

These fixtures exercise persistence and artifact mechanics. They are not visual-quality
benchmarks and intentionally contain no answer image or authored solution coordinates
for a real subject.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from PIL import Image, ImageDraw

from img2drawing import DrawingIntent, DrawingSession, ReferenceAuthority


def _fresh(path: Path) -> Path:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True)
    return path


def _complete_correction(
    session: DrawingSession,
    *,
    observation_id: str,
    stroke_id: str,
    corrected_points: tuple[tuple[float, float], ...],
) -> None:
    session.inspect(mode="quick")
    before = session.inspection_history[-1]
    residual_id = session.record_residual(
        observation_id=observation_id,
        observation="the first contour misses the declared terminal relationship",
        scope="whole composition",
        severity="material",
        impact_rationale="the primary relationship is not represented",
        responsible_premise="first contour reach",
        responsible_stroke_ids=(stroke_id,),
        planned_edit="replace the contour with the declared terminal relationship",
        before_inspection_id=before["inspection_id"],
    )
    replacement_action = session.replace_stroke(
        stroke_id,
        corrected_points,
        reason="represent the observed or declared terminal relationship",
        observation_id=observation_id,
    )
    session.inspect(mode="quick")
    after = session.inspection_history[-1]
    session.resolve_residual(
        residual_id,
        action_ids=(replacement_action,),
        after_inspection_id=after["inspection_id"],
        rationale="fresh inspection shows the revised terminal relationship",
    )
    session.finish(
        final_inspection_id=after["inspection_id"],
        rationale="the fixture's declared mechanical relationship is represented",
        accepted_limitations=("synthetic fixture; no artistic quality claim",),
    )


def _artifacts(session: DrawingSession, output: Path) -> dict[str, object]:
    final = session.render_final(output / "canonical_final.png")
    replay = session.export_timelapse(output / "replay", mode="action")
    resumed = DrawingSession.resume(
        session.checkpoint_path,
        subject=session.subject,
    )
    if resumed.drawing_state_hash() != session.drawing_state_hash():
        raise RuntimeError("resumed drawing state differs from the completed session")
    if not resumed.finish_is_current:
        raise RuntimeError("resumed finish provenance is not current")
    return {
        "version": __import__("img2drawing").__version__,
        "session_id": session.session_id,
        "authority": session.reference_authority.mode,
        "history_cursor": session.history_cursor,
        "drawing_state_hash": session.drawing_state_hash(),
        "checkpoint": session.checkpoint_path.name,
        "final_png": final.path.name,
        "replay_gif": replay.gif_path.relative_to(output).as_posix(),
        "finish_current_after_resume": resumed.finish_is_current,
    }


def run_observed(output_dir: str | Path) -> dict[str, object]:
    """Exercise the observed-authority lifecycle against a synthetic reference."""

    output = _fresh(Path(output_dir).resolve())
    subject = output / "synthetic_subject.png"
    image = Image.new("RGB", (96, 72), "white")
    draw = ImageDraw.Draw(image)
    draw.line(((12, 14), (45, 32), (82, 55)), fill=(45, 45, 45), width=5)
    image.save(subject)

    session = DrawingSession.create(
        subject=subject,
        output_dir=output,
        session_id="b17-observed-mechanical",
        intent=DrawingIntent(
            reference_mode="observed",
            drawing_mode="line_study",
            finish_intent="pose",
            style_profile="pencil_loose",
        ),
    )
    observation_id = session.observe(
        {
            "authority": "synthetic readable subject",
            "relationship": "one diagonal contour reaches the lower-right terminal",
        },
        observation_id="observed-read-1",
    )
    stroke_id = session.draw(
        ((12, 14), (43, 31), (69, 47)),
        stroke_id="primary-contour",
        part="primary_contour",
        observation_id=observation_id,
    )
    _complete_correction(
        session,
        observation_id=observation_id,
        stroke_id=stroke_id,
        corrected_points=((12, 14), (45, 32), (82, 55)),
    )
    result = _artifacts(session, output)
    (output / "result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


def run_subjectless(output_dir: str | Path) -> dict[str, object]:
    """Exercise the same lifecycle with honest drawing-only evidence."""

    output = _fresh(Path(output_dir).resolve())
    authority = ReferenceAuthority.imaginative(
        (
            "one rising arc reaches toward the lower-right corner",
            "the open field around it remains dominant",
        )
    )
    session = DrawingSession.create(
        canvas=(96, 72),
        output_dir=output,
        session_id="b17-subjectless-mechanical",
        intent=DrawingIntent(
            reference_mode="imaginative",
            drawing_mode="free_draw",
            finish_intent="expressive",
            style_profile="pencil_loose",
        ),
        reference_authority=authority,
    )
    observation_id = session.observe(
        {
            "authority": "declared goals",
            "relationship": "the rising arc should activate the lower-right field",
        },
        observation_id="goal-read-1",
    )
    stroke_id = session.draw(
        ((10, 55), (36, 31), (62, 22)),
        stroke_id="rising-arc",
        part="dominant_arc",
        observation_id=observation_id,
    )
    _complete_correction(
        session,
        observation_id=observation_id,
        stroke_id=stroke_id,
        corrected_points=((10, 55), (38, 30), (84, 17)),
    )
    result = _artifacts(session, output)
    (output / "result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


__all__ = ["run_observed", "run_subjectless"]
