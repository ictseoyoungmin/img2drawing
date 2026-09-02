from __future__ import annotations

import hashlib
import json
from dataclasses import fields
from pathlib import Path

from PIL import Image

from img2drawing import (
    DRAWING_MODES,
    DrawingIntent,
    DrawingSession,
    ModeGuide,
    ReferenceAuthority,
    ReferenceConstraint,
    resolve_mode_guide,
)


EXPECTED_MODES = (
    "croquis",
    "figure_drawing",
    "tonal_study",
    "line_study",
    "free_draw",
)


def _subject(tmp_path: Path) -> Path:
    path = tmp_path / "subject.png"
    Image.new("RGB", (64, 48), (242, 240, 236)).save(path)
    return path


def _guide_text(guide: ModeGuide) -> str:
    return " ".join(
        (
            *guide.primary_observations,
            *guide.recommended_grammar,
            *guide.omissions,
            *guide.finish_emphasis,
            *guide.completion_questions,
        )
    ).lower()


def test_mode_surface_is_small_distinct_and_portable() -> None:
    assert DRAWING_MODES == EXPECTED_MODES
    guides = tuple(resolve_mode_guide(mode) for mode in DRAWING_MODES)
    assert tuple(guide.drawing_mode for guide in guides) == EXPECTED_MODES
    assert len({guide.guide_id for guide in guides}) == len(guides)
    assert len({_guide_text(guide) for guide in guides}) == len(guides)
    for guide in guides:
        assert ModeGuide.from_dict(guide.to_dict()) == guide


def test_mode_guides_have_no_lifecycle_or_runtime_ownership_surface() -> None:
    assert {field.name for field in fields(ModeGuide)} == {
        "guide_id",
        "drawing_mode",
        "primary_observations",
        "recommended_grammar",
        "omissions",
        "finish_emphasis",
        "completion_questions",
    }
    for forbidden in (
        "advance",
        "close",
        "pass_fail",
        "phase",
        "pipeline",
        "renderer",
        "session",
        "stage",
        "cursor",
        "verdict",
    ):
        assert not hasattr(ModeGuide, forbidden)


def test_retained_modes_express_their_distinct_authoring_contracts() -> None:
    croquis = _guide_text(resolve_mode_guide("croquis"))
    figure = _guide_text(resolve_mode_guide("figure_drawing"))
    tonal = _guide_text(resolve_mode_guide("tonal_study"))
    line = _guide_text(resolve_mode_guide("line_study"))
    free = _guide_text(resolve_mode_guide("free_draw"))

    assert all(term in croquis for term in ("gesture", "balance", "line economy"))
    assert all(term in figure for term in ("anatomy", "garment", "hands", "feet", "contact"))
    assert all(term in tonal for term in ("fill_region", "form before value", "edge hierarchy"))
    assert "renderer filters" in tonal and "microhatching" in tonal
    assert all(term in line for term in ("contour ownership", "overlap", "negative space"))
    assert all(term in free for term in ("composition", "focal", "shape language", "authority"))


def test_session_mode_guide_is_derived_and_resumes_without_geometry_change(tmp_path: Path) -> None:
    subject = _subject(tmp_path)
    session = DrawingSession.create(
        subject=subject,
        output_dir=tmp_path / "run",
        intent=DrawingIntent(drawing_mode="croquis"),
    )
    session.draw(((4, 5), (24, 22), (48, 34)), part="gesture")
    before_hash = session.drawing_state_hash()
    before_cursor = session.history_cursor
    assert session.mode_guide == resolve_mode_guide("croquis")

    session.set_intent(
        DrawingIntent(drawing_mode="line_study"),
        reason="inspect contour ownership",
    )
    assert session.mode_guide == resolve_mode_guide("line_study")
    assert session.drawing_state_hash() == before_hash
    assert session.history_cursor == before_cursor

    resumed = DrawingSession.resume(session.checkpoint_path, subject=subject)
    assert resumed.mode_guide == resolve_mode_guide("line_study")
    assert resumed.drawing_state_hash() == before_hash

    unselected = DrawingSession.create(subject=subject, output_dir=tmp_path / "unselected")
    assert unselected.mode_guide is None


def test_every_mode_uses_one_session_history_inspection_and_output_core(tmp_path: Path) -> None:
    subject = _subject(tmp_path)
    sessions = []
    for mode in DRAWING_MODES:
        session = DrawingSession.create(
            subject=subject,
            output_dir=tmp_path / mode,
            intent=DrawingIntent(drawing_mode=mode),
        )
        observation_id = session.observe({"mode": mode, "read": "dominant relation"})
        session.draw(
            ((5, 7), (25, 19), (51, 37)),
            part=f"{mode}_relation",
            observation_id=observation_id,
        )
        if mode == "tonal_study":
            session.fill_region(
                ((8, 9), (34, 9), (34, 31), (8, 31)),
                value=150,
                part="large_shadow_family",
                observation_id=observation_id,
            )
        session.inspect()
        rendered = session.render_final(tmp_path / mode / "final.png")
        resumed = DrawingSession.resume(session.checkpoint_path, subject=subject)
        manifest_path = session.output_dir / session.inspection_history[-1]["manifest"]
        assert manifest_path.is_file()
        assert rendered.path.is_file()
        assert resumed.drawing_state_hash() == session.drawing_state_hash()
        assert resumed.mode_guide == session.mode_guide
        sessions.append(session)

    assert len({type(session) for session in sessions}) == 1
    assert len({type(session._agent) for session in sessions}) == 1


def test_free_draw_uses_observed_imaginative_and_hybrid_authority(tmp_path: Path) -> None:
    subject = _subject(tmp_path)
    subject_sha256 = hashlib.sha256(subject.read_bytes()).hexdigest()
    sessions = (
        DrawingSession.create(
            subject=subject,
            output_dir=tmp_path / "observed",
            intent=DrawingIntent(reference_mode="observed", drawing_mode="free_draw"),
        ),
        DrawingSession.create(
            canvas=(64, 48),
            output_dir=tmp_path / "imaginative",
            intent=DrawingIntent(reference_mode="imaginative", drawing_mode="free_draw"),
            reference_authority=ReferenceAuthority.imaginative(
                ("large rising shape against a small counter-shape",)
            ),
        ),
        DrawingSession.create(
            subject=subject,
            output_dir=tmp_path / "hybrid",
            intent=DrawingIntent(reference_mode="hybrid", drawing_mode="free_draw"),
            reference_authority=ReferenceAuthority.hybrid(
                subject_sha256,
                (
                    ReferenceConstraint("gesture", "preserve the rising gesture", "preserved"),
                    ReferenceConstraint(
                        "silhouette",
                        "transform the outer silhouette",
                        "transformed",
                        transformation="widen the upper arc",
                        rationale="test a deliberate shape-language change",
                    ),
                ),
            ),
        ),
    )

    artifact_sets = []
    for session in sessions:
        session.draw(((6, 38), (27, 14), (55, 28)), part="declared_shape")
        session.inspect()
        manifest_path = session.output_dir / session.inspection_history[-1]["manifest"]
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        artifact_sets.append(set(manifest["artifacts"]))
        assert session.mode_guide == resolve_mode_guide("free_draw")
    assert len({type(session) for session in sessions}) == 1
    assert "contrast_overlay" in artifact_sets[0]
    assert artifact_sets[1] == {"sheet", "raw_drawing", "manifest"}
    assert "contrast_overlay" in artifact_sets[2]
