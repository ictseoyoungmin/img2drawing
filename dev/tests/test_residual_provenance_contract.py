from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image

from img2drawing import DrawingIntent, DrawingSession


def _subject(tmp_path: Path) -> Path:
    path = tmp_path / "subject.png"
    Image.new("RGB", (64, 64), (242, 240, 235)).save(path)
    return path


def test_later_observation_cannot_implicitly_own_an_older_residual_fix(tmp_path: Path) -> None:
    session = DrawingSession.create(
        subject=_subject(tmp_path),
        output_dir=tmp_path / "run",
        intent=DrawingIntent(drawing_mode="croquis", finish_intent="subject"),
    )
    finding_observation = session.observe(
        {"jaw": "contour sits too low at the cheek handoff"}
    )
    stroke_id = session.draw(
        ((14, 12), (20, 25), (24, 42)),
        part="head/jaw",
        observation_id=finding_observation,
    )
    session.inspect()
    before_id = session.inspection_history[-1]["inspection_id"]
    residual_id = session.record_residual(
        observation_id=finding_observation,
        observation="jaw contour sits too low at the cheek handoff",
        scope="head/jaw",
        severity="material",
        impact_rationale="the face reads heavier than the reference",
        responsible_premise="jaw contour placement",
        responsible_stroke_ids=(stroke_id,),
        planned_edit="raise the jaw contour while preserving the cheek anchor",
        before_inspection_id=before_id,
    )

    later_observation = session.observe({"jacket": "near-side folds need cleanup"})
    assert later_observation != finding_observation

    # Omitting observation_id here binds the mutation to the latest observation. That is
    # valid authoring provenance in general, but it cannot resolve the older jaw residual.
    mismatched_action = session.replace_stroke(
        stroke_id,
        ((14, 12), (19, 24), (22, 41)),
        reason="first jaw repair attempt",
    )
    session.inspect()
    mismatched_after = session.inspection_history[-1]["inspection_id"]
    with pytest.raises(ValueError, match="correction action observation mismatch"):
        session.resolve_residual(
            residual_id,
            action_ids=(mismatched_action,),
            after_inspection_id=mismatched_after,
            rationale="must not accept provenance from the jacket observation",
        )
    assert session.residual_history[0].status == "open"
    assert session.correction_history == ()

    current_stroke_id = session.current_ir().strokes[0].stroke_id
    matching_action = session.replace_stroke(
        current_stroke_id,
        ((14, 12), (18, 23), (21, 40)),
        observation_id=finding_observation,
        reason="repair the jaw under the observation that owns the residual",
    )
    session.inspect()
    matching_after = session.inspection_history[-1]["inspection_id"]
    correction = session.resolve_residual(
        residual_id,
        action_ids=(matching_action,),
        after_inspection_id=matching_after,
        rationale="fresh inspection confirms the jaw handoff under the original finding",
    )

    assert correction.observation_id == finding_observation
    assert session.residual_history[0].status == "resolved"
    assert session.correction_history == (correction,)
