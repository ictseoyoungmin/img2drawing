from __future__ import annotations

import json
from pathlib import Path

import pytest
from PIL import Image

from img2drawing import (
    AuthoredElement,
    DrawingSession,
    replace_fill_region,
)


def _subject(tmp_path: Path) -> Path:
    path = tmp_path / "subject.png"
    Image.new("RGB", (96, 72), (243, 241, 237)).save(path)
    return path


def _session(tmp_path: Path) -> tuple[DrawingSession, str]:
    session = DrawingSession.create(subject=_subject(tmp_path), output_dir=tmp_path / "run")
    observation_id = session.observe(
        {"question": "which authored element carries the shoulder-to-elbow relation"},
        observation_id="body-read",
    )
    return session, observation_id


def test_authored_element_is_portable_immutable_context() -> None:
    element = AuthoredElement(
        element_type="stroke",
        element_id="arm-1",
        status="current",
        part="near_arm",
        role="contour",
        created_seq=1,
        latest_seq=2,
        created_action_id="draw-arm",
        latest_action_id="lift-arm",
        latest_action_kind="stroke.soft_lift",
        action_ids=("draw-arm", "lift-arm"),
        observation_ids=("body-read",),
        reason="reduce a duplicate inner edge",
        revision_count=1,
    )
    assert AuthoredElement.from_dict(element.to_dict()) == element
    with pytest.raises(ValueError, match="superseded_by"):
        AuthoredElement.from_dict({**element.to_dict(), "status": "superseded"})


def test_query_finds_current_authored_decisions_by_responsibility_and_provenance(
    tmp_path: Path,
) -> None:
    session, observation_id = _session(tmp_path)
    session.draw(
        ((10, 12), (30, 25), (49, 42)),
        action_id="draw-near-arm",
        stroke_id="near-arm",
        part="near_arm",
        role="structure",
        observation_id=observation_id,
    )
    session.draw(
        ((52, 14), (66, 28), (77, 48)),
        action_id="draw-far-arm",
        stroke_id="far-arm",
        part="far_arm",
        role="contour",
        observation_id=observation_id,
    )
    session.fill_region(
        ((18, 20), (52, 20), (52, 56), (18, 56)),
        value=160,
        part="torso",
        fill_id="torso-value",
        action_id="fill-torso",
        observation_id=observation_id,
    )

    assert [item.element_id for item in session.authored_elements(part="near_arm")] == [
        "near-arm"
    ]
    assert [item.element_id for item in session.authored_elements(role="contour")] == [
        "far-arm"
    ]
    assert [item.element_id for item in session.authored_elements(element_type="fill")] == [
        "torso-value"
    ]
    assert {
        item.element_id
        for item in session.authored_elements(observation_id=observation_id)
    } == {"near-arm", "far-arm", "torso-value"}
    assert session.authored_elements(action_id="draw-near-arm")[0].element_id == "near-arm"


def test_replacement_chain_resolves_current_and_stale_edits_fail_atomically(tmp_path: Path) -> None:
    session, observation_id = _session(tmp_path)
    session.draw(
        ((8, 10), (30, 27), (55, 46)),
        action_id="draw-arm-1",
        stroke_id="arm-1",
        part="near_arm",
        observation_id=observation_id,
    )
    session.replace_stroke(
        "arm-1",
        ((8, 10), (34, 25), (57, 45)),
        action_id="replace-arm-2",
        stroke_id="arm-2",
        part="near_arm",
        reason="restore observed upper-arm thickness",
        observation_id=observation_id,
    )
    session.replace_stroke(
        "arm-2",
        ((8, 10), (35, 24), (58, 44)),
        action_id="replace-arm-3",
        stroke_id="arm-3",
        part="near_arm",
        reason="clarify the elbow turn",
        observation_id=observation_id,
    )

    all_elements = {item.element_id: item for item in session.authored_elements(status=None)}
    assert all_elements["arm-1"].status == "superseded"
    assert all_elements["arm-1"].superseded_by == "arm-2"
    assert all_elements["arm-2"].status == "superseded"
    assert all_elements["arm-2"].superseded_by == "arm-3"
    assert all_elements["arm-3"].status == "current"
    assert session.resolve_authored_element("arm-1", element_type="stroke").element_id == "arm-3"
    assert session.current_stroke("arm-1").stroke_id == "arm-3"

    before_cursor = session.history_cursor
    for operation in (
        lambda: session.replace_stroke(
            "arm-1",
            ((8, 10), (32, 24)),
            stroke_id="bad-replacement",
            reason="stale target",
        ),
        lambda: session.soft_lift("arm-1", reason="stale target"),
        lambda: session.delete_stroke("arm-1", reason="stale target"),
    ):
        with pytest.raises(ValueError, match="missing stroke"):
            operation()
        assert session.history_cursor == before_cursor

    session.delete_stroke(
        "arm-3",
        action_id="delete-arm-3",
        reason="remove disproved arm premise",
        observation_id=observation_id,
    )
    assert session.resolve_authored_element("arm-1", element_type="stroke") is None
    with pytest.raises(ValueError, match="deleted"):
        session.current_stroke("arm-1")


def test_duplicate_stroke_identity_is_rejected_without_partial_history(tmp_path: Path) -> None:
    session, observation_id = _session(tmp_path)
    session.draw(
        ((8, 8), (30, 30)),
        stroke_id="unique-mark",
        observation_id=observation_id,
    )
    before_cursor = session.history_cursor
    with pytest.raises(ValueError, match="stroke_id already exists"):
        session.draw(
            ((12, 8), (34, 30)),
            stroke_id="unique-mark",
            observation_id=observation_id,
        )
    assert session.history_cursor == before_cursor


def test_local_segment_edits_preserve_identity_and_accumulate_provenance(tmp_path: Path) -> None:
    session, observation_id = _session(tmp_path)
    session.draw(
        ((8, 12), (24, 20), (42, 32), (62, 46)),
        pressure=(0.3, 0.5, 0.7, 0.4),
        action_id="draw-contour",
        stroke_id="contour-1",
        part="torso_contour",
        role="contour",
        observation_id=observation_id,
    )
    session.replace_segment(
        "contour-1",
        1,
        2,
        ((24, 20), (34, 23), (42, 32)),
        action_id="replace-contour-segment",
        reason="restore the observed inward turn",
        observation_id=observation_id,
    )
    session.soft_lift(
        "contour-1",
        action_id="lift-contour",
        reason="subordinate the non-focal contour",
        observation_id=observation_id,
    )
    element = session.authored_elements(element_type="stroke")[0]
    assert element.element_id == "contour-1"
    assert element.status == "current"
    assert element.revision_count == 2
    assert element.action_ids == (
        "draw-contour",
        "replace-contour-segment",
        "lift-contour",
    )
    assert session.current_stroke("contour-1").stroke_id == "contour-1"


def test_fill_revision_uses_same_query_and_session_edit_surface(tmp_path: Path) -> None:
    session, observation_id = _session(tmp_path)
    fill_id = session.fill_region(
        ((12, 14), (70, 14), (70, 58), (12, 58)),
        value=165,
        part="coat",
        fill_id="coat-value",
        action_id="fill-coat",
        observation_id=observation_id,
    )
    action_id = session.replace_fill_region(
        fill_id,
        value=95,
        reason="inspection shows a darker connected coat family",
        action_id="revise-coat-1",
        observation_id=observation_id,
    )
    assert action_id == "revise-coat-1"
    compatibility_action = replace_fill_region(
        session,
        fill_id,
        value=105,
        reason="retain a little more reflected light",
        action_id="revise-coat-2",
        observation_id=observation_id,
    )
    assert compatibility_action == "revise-coat-2"
    element = session.authored_elements(element_type="fill")[0]
    assert element.element_id == fill_id
    assert element.status == "current"
    assert element.revision_count == 2
    assert element.action_ids == ("fill-coat", "revise-coat-1", "revise-coat-2")
    assert session.current_fill_region(fill_id).fill_id == fill_id


def test_summary_is_bounded_derived_truth_and_excludes_generated_fill_contacts(
    tmp_path: Path,
) -> None:
    session, observation_id = _session(tmp_path)
    for index in range(3):
        session.draw(
            ((8 + index * 3, 8), (30 + index * 3, 35)),
            stroke_id=f"line-{index}",
            part="figure",
            observation_id=observation_id,
        )
    session.fill_region(
        ((12, 14), (72, 14), (72, 60), (12, 60)),
        value=145,
        part="figure",
        fill_id="figure-value",
        observation_id=observation_id,
    )
    session.inspect()
    residual_id = session.record_residual(
        observation_id=observation_id,
        observation="the near arm is too narrow",
        scope="near_arm",
        severity="high",
        impact_rationale="the silhouette loses the observed rotation and weight",
        responsible_premise="initial arm envelope",
        responsible_stroke_ids=("line-0",),
        planned_edit="replace the responsible arm contour",
        before_inspection_id=session.inspection_history[-1]["inspection_id"],
    )

    summary = session.authoring_summary(limit=2, part="figure")
    assert summary.current_strokes == 3
    assert summary.current_fills == 1
    assert summary.total_matching_elements == 4
    assert len(summary.elements) == 2 and summary.truncated
    assert summary.open_residual_ids == (residual_id,)
    assert summary.history_cursor == session.history_cursor
    assert summary.drawing_state_hash == session.drawing_state_hash()
    assert len(session.current_ir().strokes) > summary.current_strokes
    payload = json.loads(session.checkpoint_path.read_text(encoding="utf-8"))
    assert "authoring_summary" not in payload
    assert "authored_elements" not in payload

    resumed = DrawingSession.resume(session.checkpoint_path, subject=session.subject)
    assert resumed.authoring_summary(limit=2, part="figure").to_dict() == summary.to_dict()


def test_query_validation_and_ambiguous_cross_type_identity_are_explicit(tmp_path: Path) -> None:
    session, observation_id = _session(tmp_path)
    session.draw(
        ((10, 10), (35, 38)),
        stroke_id="shared-id",
        observation_id=observation_id,
    )
    session.fill_region(
        ((15, 15), (65, 15), (65, 55), (15, 55)),
        value=155,
        part="torso",
        fill_id="shared-id",
        observation_id=observation_id,
    )
    with pytest.raises(ValueError, match="ambiguous"):
        session.resolve_authored_element("shared-id")
    assert session.resolve_authored_element("shared-id", element_type="fill").element_type == "fill"
    with pytest.raises(ValueError, match="unsupported element_type"):
        session.authored_elements(element_type="pixel")
    with pytest.raises(ValueError, match="unsupported element status"):
        session.authored_elements(status="hidden")
    with pytest.raises(ValueError, match="limit"):
        session.authoring_summary(limit=101)
