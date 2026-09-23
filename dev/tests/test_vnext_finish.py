from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image

from img2drawing import DrawingIntent, DrawingSession
from img2drawing.session import FINISH_GUIDE_SCHEMA, FINISH_INTENTS, FinishGuide, FinishRelation, resolve_finish_guide


LIFECYCLE_KEYS = {"phase", "phase_count", "stage", "cursor", "advance", "close", "verdict", "pass_fail"}


def _keys(value):
    if isinstance(value, dict):
        for key, item in value.items():
            yield key
            yield from _keys(item)
    elif isinstance(value, list):
        for item in value:
            yield from _keys(item)


def test_finish_guides_are_strict_immutable_plain_data() -> None:
    for finish_intent in FINISH_INTENTS:
        guide = resolve_finish_guide(finish_intent)
        payload = guide.to_dict()
        assert payload["schema"] == FINISH_GUIDE_SCHEMA
        assert FinishGuide.from_dict(payload) == guide
        assert guide.finish_intent == finish_intent
        assert not LIFECYCLE_KEYS.intersection(_keys(payload))
        with pytest.raises(AttributeError):
            guide.finish_intent = "pose"

    with pytest.raises(ValueError, match="lifecycle fields"):
        FinishGuide.from_dict({**resolve_finish_guide("pose").to_dict(), "stage": "finish"})
    with pytest.raises(ValueError, match="unsupported fields"):
        FinishRelation.from_dict({**resolve_finish_guide("pose").relations[0].to_dict(), "score": 1})
    with pytest.raises(ValueError, match="unsupported finish_intent"):
        resolve_finish_guide("complete")


def test_finish_intents_have_distinct_authoring_policy_signatures() -> None:
    signatures = {
        finish_intent: (
            resolve_finish_guide(finish_intent).mark_policy,
            resolve_finish_guide(finish_intent).value_policy,
            resolve_finish_guide(finish_intent).edge_policy,
            tuple(relation.part for relation in resolve_finish_guide(finish_intent).relations),
        )
        for finish_intent in FINISH_INTENTS
    }
    assert len(set(signatures.values())) == len(FINISH_INTENTS)
    assert "hands_and_feet" in {relation.part for relation in resolve_finish_guide("subject").relations}
    assert "geometry_preflight" in {relation.part for relation in resolve_finish_guide("form_light").relations}
    assert "preserved_constraints" in {relation.part for relation in resolve_finish_guide("expressive").relations}


def test_subject_finish_is_relational_and_macro_first() -> None:
    guide = resolve_finish_guide("subject")
    assert {relation.part for relation in guide.relations} == {
        "face", "hair", "hands_and_feet", "clothing", "prop"
    }
    relation_text = " ".join(
        text
        for relation in guide.relations
        for text in (*relation.observations, *relation.authoring_policy, *relation.avoid)
    )
    for concept in ("spacing", "direction", "contact", "overlap", "termination", "topology"):
        assert concept in relation_text
    assert "macro pose, proportion, mass, and contact" in guide.preserve
    assert any("detail" in item and "macro" in item for item in resolve_finish_guide("pose").relations[0].avoid)


def test_form_light_and_expressive_preserve_structural_truth() -> None:
    tonal = " ".join(
        sum((relation.authoring_policy + relation.avoid for relation in resolve_finish_guide("form_light").relations), ())
    )
    assert "line-only" in tonal
    assert "one-off opacity guessing" in tonal
    assert "explicit observed strokes" in tonal
    expressive = resolve_finish_guide("expressive")
    assert "explicit reference constraints" in expressive.preserve
    assert any("silent sacrifice" in item for item in expressive.relations[0].avoid)


def test_finish_intents_author_distinct_stroke_decisions_through_one_session(tmp_path: Path) -> None:
    subject = tmp_path / "subject.png"
    Image.new("RGB", (96, 72), (244, 242, 236)).save(subject)
    session = DrawingSession.create(
        subject=subject,
        output_dir=tmp_path / "run",
        intent=DrawingIntent(finish_intent="pose"),
    )
    observation_id = session.observe(
        {"read": "synthetic current-state fixture for finish-intent mechanics"},
        observation_id="finish-read",
    )

    decisions = (
        ("pose", "whole_pose/gesture", ((8, 12), (25, 30), (42, 58)), "structure"),
        ("subject", "hands_and_feet/pocket_contact", ((44, 30), (53, 38), (59, 35)), "contour"),
        ("form_light", "light_shadow_families/arm_shadow", ((20, 28), (38, 26), (55, 31)), "value"),
        ("expressive", "composition_and_focal/focal_arc", ((16, 18), (34, 10), (63, 24)), "accent"),
    )
    action_ids = []
    for index, (finish_intent, part, points, role) in enumerate(decisions):
        if index:
            session.set_intent(
                DrawingIntent(finish_intent=finish_intent),
                reason=f"exercise {finish_intent} authoring policy",
            )
        stroke_id = session.draw(
            points,
            action_id=f"finish-{finish_intent}-action",
            stroke_id=f"finish-{finish_intent}-stroke",
            part=part,
            role=role,
            observation_id=observation_id,
            metadata={"finish_intent": finish_intent},
        )
        action_ids.append(stroke_id)

    assert len(session.intent_history) == 4
    assert [event.intent.finish_intent for event in session.intent_history] == list(FINISH_INTENTS)
    assert len(action_ids) == 4
    history = session._agent.history.actions
    assert {action.action for action in history} == {"stroke.add"}
    assert len({action.part for action in history}) == 4
    assert history[1].part == "hands_and_feet/pocket_contact"
    assert history[2].part == "light_shadow_families/arm_shadow"
    assert (history[2].provenance or {})["metadata"]["finish_intent"] == "form_light"
