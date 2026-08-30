from __future__ import annotations

import json
from pathlib import Path

import pytest
from PIL import Image

from img2drawing import (
    CONSTRUCTION_PHASES,
    ConstructionMark,
    DrawingSession,
    GroundGuide,
    Grid,
    InitialConstruct,
    PlumbLine,
    PoseObservation,
    ROI,
    Registration,
    author_initial_construct,
    inspect_initial_construct,
    observe_pose,
)


def _subject(tmp_path: Path) -> Path:
    path = tmp_path / "subject.png"
    Image.new("RGB", (96, 72), (236, 234, 228)).save(path)
    return path


def _observation() -> PoseObservation:
    return PoseObservation(
        support_side="image-left",
        flow="head-left to torso-right, reversing into the pelvis",
        head_ribcage_pelvis="head turns over a back-three-quarter ribcage above a tilted pelvis",
        shoulder_pelvis="shoulders and pelvis counter-tilt",
        silhouette_keys=("hair opening", "wide support foot"),
        negative_spaces=("arm-to-torso opening", "between legs"),
        ground_relation="both feet meet one ground plane",
        major_prop_axis="diagonal across the back",
        occluded_limb_evidence=("far arm continues behind the torso",),
        uncertain=("far elbow under clothing",),
    )


def _mark(mark_id: str, phase: str, part: str, x: float) -> ConstructionMark:
    return ConstructionMark(
        mark_id=mark_id,
        phase=phase,
        role="mass" if phase == "mass_blocking" else "structure",
        part=part,
        points=((x, 8.0), (x + 8.0, 20.0), (x + 12.0, 32.0)),
        confidence=0.8,
        layer=2,
    )


def _construct() -> InitialConstruct:
    return InitialConstruct(
        observation=_observation(),
        marks=(
            _mark("loa", "line_of_action", "body_flow", 8.0),
            _mark("head", "mass_blocking", "head", 18.0),
            _mark("ribcage", "mass_blocking", "ribcage", 28.0),
            _mark("pelvis", "mass_blocking", "pelvis", 38.0),
            _mark("shoulder", "joints_limbs", "shoulder_chain", 48.0),
            _mark("leg", "joints_limbs", "support_leg", 58.0),
        ),
        plumb=PlumbLine(anchor=(44.0, 22.0)),
        ground=GroundGuide(y=60.0, x_range=(12.0, 82.0)),
        rois=(ROI("head-torso", (10.0, 5.0, 64.0, 42.0)), ROI("pelvis-legs", (22.0, 34.0, 84.0, 68.0))),
    )


def test_pose_observation_is_short_portable_and_round_trips():
    observation = _observation()
    assert PoseObservation.from_dict(observation.to_dict()) == observation
    assert observation.to_dict()["format"] == "pose-observation/v1"
    assert observation.to_dict()["uncertain"] == ["far elbow under clothing"]


def test_construction_marks_validate_geometry_and_phase_order():
    with pytest.raises(ValueError, match="at least two points"):
        ConstructionMark("bad", "line_of_action", "gesture", "flow", ((1.0, 2.0),))
    with pytest.raises(ValueError, match="finite"):
        ConstructionMark("bad", "line_of_action", "gesture", "flow", ((1.0, 2.0), (float("nan"), 4.0)))
    with pytest.raises(ValueError, match="unknown construction phase"):
        ConstructionMark("bad", "not-a-stage", "gesture", "flow", ((1.0, 2.0), (3.0, 4.0)))
    with pytest.raises(ValueError, match="ordered construction phases"):
        InitialConstruct(
            observation=_observation(),
            marks=(_mark("mass", "mass_blocking", "head", 8.0), _mark("loa", "line_of_action", "flow", 18.0)),
        )


def test_author_initial_construct_observes_first_and_preserves_order(tmp_path: Path):
    subject = _subject(tmp_path)
    session = DrawingSession.create(subject=subject, output_dir=tmp_path / "run")
    construct = _construct()

    result = author_initial_construct(session, construct)

    assert result.observation_id == "observation-0001"
    assert result.action_ids == tuple(mark.mark_id for mark in construct.marks)
    actions = session._agent.history.to_dict()["actions"]
    assert [action["provenance"]["action_id"] for action in actions] == list(result.action_ids)
    assert [action["part"] for action in actions] == [mark.part for mark in construct.marks]
    assert len(session.current_ir().strokes) == len(construct.marks)
    checkpoint = json.loads(session.checkpoint_path.read_text(encoding="utf-8"))
    assert checkpoint["observations"][0]["payload"] == construct.observation.to_dict()
    assert all(action["stage"] == "__vnext_compat__" for action in actions)


def test_observe_pose_can_be_explicitly_bound_to_the_batch(tmp_path: Path):
    subject = _subject(tmp_path)
    session = DrawingSession.create(subject=subject, output_dir=tmp_path / "run")
    observation_id = observe_pose(session, _observation(), observation_id="pose-read-1")
    construct = _construct()

    result = author_initial_construct(session, construct, observation_id=observation_id)

    assert result.observation_id == "pose-read-1"
    checkpoint = json.loads(session.checkpoint_path.read_text(encoding="utf-8"))
    assert {action["provenance"]["observation_id"] for action in checkpoint["history"]["actions"]} == {"pose-read-1"}


def test_subject_space_registration_is_applied_without_new_renderer(tmp_path: Path):
    registration = Registration(
        subject_size=(96, 72),
        canvas_size=(192, 144),
        scale=(2.0, 2.0),
    )
    spec = _construct().marks[0].to_draw_spec(registration)
    assert spec["action_id"] == "loa"
    assert spec["points"][0] == (16.0, 16.0)
    assert spec["points"][-1] == (40.0, 64.0)


def test_first_construct_inspection_reuses_existing_sheet_with_guides_and_rois(tmp_path: Path):
    subject = _subject(tmp_path)
    output = tmp_path / "run"
    session = DrawingSession.create(subject=subject, output_dir=output)
    construct = _construct()
    author_initial_construct(session, construct)

    sheet = inspect_initial_construct(session, construct, grid=Grid(columns=6, rows=5))

    assert sheet.drawing_state_hash == session.drawing_state_hash()
    assert [guide.to_dict()["kind"] for guide in sheet.guides] == ["plumb_line", "ground_guide"]
    assert [roi.label for roi in sheet.rois] == ["head-torso", "pelvis-legs"]
    manifest = json.loads((output / "inspections" / "000001" / "inspection.json").read_text(encoding="utf-8"))
    assert manifest["grid"]["columns"] == 6
    assert manifest["guides"][0]["kind"] == "plumb_line"
    assert manifest["evidence_only"] is True


def test_resume_keeps_pose_observation_and_initial_construct_actions(tmp_path: Path):
    subject = _subject(tmp_path)
    session = DrawingSession.create(subject=subject, output_dir=tmp_path / "run")
    author_initial_construct(session, _construct())
    session.inspect()

    resumed = DrawingSession.resume(session.checkpoint_path, subject=subject)

    checkpoint = json.loads(resumed.checkpoint_path.read_text(encoding="utf-8"))
    assert checkpoint["observations"][0]["payload"]["flow"].startswith("head-left")
    assert resumed.drawing_state_hash() == session.drawing_state_hash()
    assert resumed.inspection_history == session.inspection_history


def test_explicit_observation_binding_rejects_mismatched_snapshot(tmp_path: Path):
    subject = _subject(tmp_path)
    session = DrawingSession.create(subject=subject, output_dir=tmp_path / "run")
    observe_pose(session, _observation(), observation_id="pose-read-1")
    original = _construct()
    mismatched = InitialConstruct(
        observation=PoseObservation(
            support_side="image-right",
            flow=original.observation.flow,
            head_ribcage_pelvis=original.observation.head_ribcage_pelvis,
            shoulder_pelvis=original.observation.shoulder_pelvis,
        ),
        marks=original.marks,
    )
    with pytest.raises(ValueError, match="does not match construct observation"):
        author_initial_construct(session, mismatched, observation_id="pose-read-1")


def test_initial_construct_batch_rolls_back_when_checkpoint_fails(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    subject = _subject(tmp_path)
    session = DrawingSession.create(subject=subject, output_dir=tmp_path / "run")
    observation_id = observe_pose(session, _observation())

    def fail_checkpoint(path):
        raise OSError("checkpoint storage unavailable")

    monkeypatch.setattr(session, "_write_checkpoint", fail_checkpoint)
    with pytest.raises(OSError, match="checkpoint storage unavailable"):
        author_initial_construct(session, _construct(), observation_id=observation_id)
    assert session.history_cursor == 0
    assert not session.current_ir().strokes
