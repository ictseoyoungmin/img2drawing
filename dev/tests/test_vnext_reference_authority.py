from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest
from PIL import Image

from img2drawing import (
    DrawingIntent,
    DrawingSession,
    ReferenceAuthority,
    ReferenceConstraint,
    ReferenceUnavailableError,
    Measurement,
    Registration,
    ROI,
)


def _subject(tmp_path: Path) -> Path:
    path = tmp_path / "subject.png"
    Image.new("RGB", (64, 48), (240, 238, 232)).save(path)
    return path


def _imaginative(tmp_path: Path) -> DrawingSession:
    return DrawingSession.create(
        canvas=(64, 48),
        output_dir=tmp_path / "imaginative",
        session_id="subjectless-authority",
        intent=DrawingIntent(
            reference_mode="imaginative",
            drawing_mode="free_draw",
            finish_intent="expressive",
        ),
        reference_authority=ReferenceAuthority.imaginative(
            (
                "a broad ascending arc anchors the composition",
                "a small counter-shape keeps the lower-right corner active",
            )
        ),
    )


def test_reference_authority_modes_are_portable_and_strict(tmp_path: Path):
    subject = _subject(tmp_path)
    digest = hashlib.sha256(subject.read_bytes()).hexdigest()
    observed = ReferenceAuthority.observed(digest)
    imaginative = ReferenceAuthority.imaginative(("one dominant circular mass",))
    hybrid = ReferenceAuthority.hybrid(
        digest,
        (
            ReferenceConstraint("pose", "preserve the torso turn", "preserved"),
            ReferenceConstraint(
                "prop",
                "replace the photographed prop",
                "transformed",
                transformation="turn it into a long ribbon",
                rationale="the requested concept changes object identity",
            ),
        ),
        declared_goals=("keep the original weight distribution",),
    )
    for authority in (observed, imaginative, hybrid):
        restored = ReferenceAuthority.from_dict(authority.checkpoint_dict())
        assert restored == authority
        assert restored.digest() == authority.digest()
    assert [item.constraint_id for item in hybrid.preserved_constraints] == ["pose"]
    assert [item.constraint_id for item in hybrid.transformed_constraints] == ["prop"]

    with pytest.raises(ValueError, match="declared_goals"):
        ReferenceAuthority.imaginative(())
    with pytest.raises(ValueError, match="both preserved and transformed"):
        ReferenceAuthority.hybrid(
            digest,
            (ReferenceConstraint("pose", "keep pose", "preserved"),),
        )
    with pytest.raises(ValueError, match="transformation and rationale"):
        ReferenceConstraint("prop", "change prop", "transformed")
    tampered = imaginative.checkpoint_dict()
    tampered["declared_goals"] = ["different goal"]
    with pytest.raises(ValueError, match="digest"):
        ReferenceAuthority.from_dict(tampered)


def test_subjectless_creation_requires_canvas_intent_and_honest_authority(tmp_path: Path):
    with pytest.raises(ValueError, match="requires canvas"):
        DrawingSession.create(output_dir=tmp_path / "missing")
    with pytest.raises(TypeError, match="reference_authority"):
        DrawingSession.create(
            canvas=(64, 48),
            output_dir=tmp_path / "no-authority",
            intent=DrawingIntent(reference_mode="imaginative"),
        )
    with pytest.raises(ValueError, match="declared DrawingIntent"):
        DrawingSession.create(
            canvas=(64, 48),
            output_dir=tmp_path / "no-intent",
            reference_authority=ReferenceAuthority.imaginative(("a centered mass",)),
        )
    with pytest.raises(ValueError, match="does not match"):
        DrawingSession.create(
            canvas=(64, 48),
            output_dir=tmp_path / "mismatch",
            intent=DrawingIntent(reference_mode="observed"),
            reference_authority=ReferenceAuthority.imaginative(("a centered mass",)),
        )

    session = _imaginative(tmp_path)
    assert not session.has_reference
    assert session.subject is None
    assert session.reference_authority.mode == "imaginative"
    assert (session.width, session.height) == (64, 48)
    payload = json.loads(session.checkpoint_path.read_text(encoding="utf-8"))
    assert payload["subject"] is None
    assert payload["reference_authority"]["digest"] == session.reference_authority.digest()


def test_subjectless_inspection_is_drawing_only_and_reference_tools_refuse(tmp_path: Path):
    session = _imaginative(tmp_path)
    session.draw(((5, 8), (25, 20), (50, 38)), part="dominant_arc")
    sheet = session.inspect()
    manifest_path = tmp_path / "imaginative" / "inspections" / "000001" / "inspection.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert sheet.subject is None and sheet.registration is None
    assert manifest["inputs"] == {"subject": None, "drawing": "raw_drawing.png"}
    assert manifest["subject_sha256"] is None
    assert manifest["registration"] is None
    assert manifest["overlay"] is None
    assert manifest["reference_authority"] == {
        "mode": "imaginative",
        "digest": session.reference_authority.digest(),
    }
    assert manifest["artifacts"] == {
        "sheet": "inspection_sheet.png",
        "raw_drawing": "raw_drawing.png",
        "manifest": "inspection.json",
    }
    assert not (manifest_path.parent / "contrast_overlay.png").exists()
    assert not (manifest_path.parent / "registered_drawing.png").exists()
    assert session.evidence_telemetry.generated_artifacts == 3
    assert session.evidence_telemetry.visual_artifacts == 2

    with pytest.raises(ReferenceUnavailableError, match="requires a readable subject"):
        session.require_reference("pixel sampling")
    with pytest.raises(ReferenceUnavailableError, match="subject-space"):
        session.inspect(rois=(ROI("fake", (1, 1, 20, 20)),))
    with pytest.raises(ReferenceUnavailableError, match="registration"):
        session.inspect(registration=Registration.identity((64, 48)))
    with pytest.raises(ReferenceUnavailableError, match="measurements"):
        session.inspect(
            measurements=(Measurement("distance", 12.0, coordinate_space="subject"),)
        )


def test_subjectless_inspect_correct_finish_replay_and_resume_share_one_core(tmp_path: Path):
    session = _imaginative(tmp_path)
    observation_id = session.observe(
        {
            "authority": "declared goals",
            "comparison": "the ascending arc is too centered to activate the lower-right counter-shape",
        },
        observation_id="intent-read-1",
    )
    stroke_id = session.draw(
        ((8, 8), (24, 20), (40, 35)),
        stroke_id="arc-1",
        part="dominant_arc",
        observation_id=observation_id,
    )
    session.inspect()
    before = session.inspection_history[-1]
    residual_id = session.record_residual(
        observation_id=observation_id,
        observation="the dominant arc does not reach far enough toward the declared counter-shape",
        scope="composition",
        severity="high",
        impact_rationale="the declared asymmetrical balance is absent",
        responsible_premise="dominant arc placement",
        responsible_stroke_ids=(stroke_id,),
        planned_edit="replace the arc with a farther lower-right reach",
        before_inspection_id=before["inspection_id"],
    )
    replacement = session.replace_stroke(
        stroke_id,
        ((8, 8), (28, 18), (54, 40)),
        reason="restore the declared asymmetrical balance",
        observation_id=observation_id,
    )
    session.inspect()
    after = session.inspection_history[-1]
    session.resolve_residual(
        residual_id,
        action_ids=(replacement,),
        after_inspection_id=after["inspection_id"],
        rationale="the fresh drawing-only inspection now carries the arc into the counter-shape",
    )
    finish = session.finish(
        final_inspection_id=after["inspection_id"],
        rationale="the declared compositional relationship is materially present",
    )
    final = session.render_final(tmp_path / "subjectless-final.png")
    replay = session.export_timelapse(tmp_path / "subjectless-replay", mode="action")
    assert final.path.is_file() and replay.gif_path.is_file()
    assert finish.intent_digest == session.intent.digest()
    assert session.residual_history[0].status == "resolved"

    resumed = DrawingSession.resume(session.checkpoint_path)
    assert resumed.reference_authority == session.reference_authority
    assert resumed.drawing_state_hash() == session.drawing_state_hash()
    assert resumed.correction_history == session.correction_history
    assert resumed.finish_is_current


def test_hybrid_authority_preserves_and_transforms_distinct_constraints(tmp_path: Path):
    subject = _subject(tmp_path)
    digest = hashlib.sha256(subject.read_bytes()).hexdigest()
    authority = ReferenceAuthority.hybrid(
        digest,
        (
            ReferenceConstraint("turn", "preserve the three-quarter torso turn", "preserved"),
            ReferenceConstraint(
                "silhouette",
                "change the coat silhouette",
                "transformed",
                transformation="extend it into a triangular cape",
                rationale="requested fantasy transformation",
            ),
        ),
    )
    session = DrawingSession.create(
        subject=subject,
        output_dir=tmp_path / "hybrid",
        intent=DrawingIntent(reference_mode="hybrid", drawing_mode="figure_drawing"),
        reference_authority=authority,
    )
    session.draw(((10, 8), (28, 20), (45, 40)), part="torso_turn")
    session.inspect()
    payload = json.loads(session.checkpoint_path.read_text(encoding="utf-8"))
    assert payload["reference_authority"]["constraints"][0]["disposition"] == "preserved"
    assert payload["reference_authority"]["constraints"][1]["disposition"] == "transformed"
    resumed = DrawingSession.resume(session.checkpoint_path, subject=subject)
    assert resumed.reference_authority == authority
    assert resumed.has_reference

    payload.pop("reference_authority")
    session.checkpoint_path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="pre-B13 checkpoint"):
        DrawingSession.resume(session.checkpoint_path, subject=subject)
    upgraded = DrawingSession.resume(
        session.checkpoint_path,
        subject=subject,
        reference_authority=authority,
    )
    assert upgraded.reference_authority == authority


def test_pre_b13_observed_checkpoint_resumes_without_state_hash_drift(tmp_path: Path):
    subject = _subject(tmp_path)
    session = DrawingSession.create(subject=subject, output_dir=tmp_path / "observed")
    session.draw(((5, 5), (25, 20), (50, 40)))
    expected_hash = session.drawing_state_hash()
    payload = json.loads(session.checkpoint_path.read_text(encoding="utf-8"))
    expected_action_digest = payload["digests"]["action_log_sha256"]
    assert payload["subject"]["sha256"] == hashlib.sha256(subject.read_bytes()).hexdigest()
    payload.pop("reference_authority")
    session.checkpoint_path.write_text(json.dumps(payload), encoding="utf-8")
    resumed = DrawingSession.resume(session.checkpoint_path, subject=subject)
    assert resumed.reference_authority.mode == "observed"
    assert resumed.drawing_state_hash() == expected_hash
    resumed.checkpoint()
    restored_payload = json.loads(session.checkpoint_path.read_text(encoding="utf-8"))
    assert restored_payload["digests"]["action_log_sha256"] == expected_action_digest
    assert restored_payload["digests"]["drawing_state_hash"] == expected_hash


def test_resume_rejects_tampered_subjectless_authority(tmp_path: Path):
    session = _imaginative(tmp_path)
    payload = json.loads(session.checkpoint_path.read_text(encoding="utf-8"))
    payload["reference_authority"]["declared_goals"] = ["silently replaced goal"]
    session.checkpoint_path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="authority digest"):
        DrawingSession.resume(session.checkpoint_path)


def test_reference_mode_is_immutable_within_one_authoritative_session(tmp_path: Path):
    session = DrawingSession.create(
        subject=_subject(tmp_path),
        output_dir=tmp_path / "observed",
        intent=DrawingIntent(reference_mode="observed"),
    )
    with pytest.raises(ValueError, match="immutable reference authority"):
        session.set_intent(
            DrawingIntent(reference_mode="hybrid"),
            reason="would silently redefine comparison truth",
        )
