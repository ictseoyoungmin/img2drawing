from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from img2drawing import (
    FINISH_GUIDE_SCHEMA,
    FINISH_INTENTS,
    FinishGuide,
    FinishRelation,
    resolve_finish_guide,
)


ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "dev" / "fixtures" / "vnext-b09" / "run.py"
LIFECYCLE_KEYS = {"phase", "phase_count", "stage", "cursor", "advance", "close", "verdict", "pass_fail"}


def _load_fixture():
    spec = importlib.util.spec_from_file_location("img2drawing_vnext_b09_fixture", FIXTURE)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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
    tonal = " ".join(sum((relation.authoring_policy + relation.avoid for relation in resolve_finish_guide("form_light").relations), ()))
    assert "line-only" in tonal
    assert "one-off opacity guessing" in tonal
    expressive = resolve_finish_guide("expressive")
    assert "explicit reference constraints" in expressive.preserve
    assert any("silent sacrifice" in item for item in expressive.relations[0].avoid)


def test_fixture_authors_distinct_decisions_through_one_session(tmp_path: Path) -> None:
    trace = _load_fixture().run_fixture(tmp_path / "fixture")
    assert trace["quality_claim"] == "mechanical-only"
    assert trace["session_schema"] == "img2drawing.vnext.session.v2"
    assert trace["intent_event_count"] == 4
    assert trace["intent_order"] == list(FINISH_INTENTS)
    assert set(trace["decisions"]) == set(FINISH_INTENTS)
    assert {decision["actions"][0]["finish_intent"] for decision in trace["decisions"].values()} == set(FINISH_INTENTS)
    assert {decision["actions"][0]["kind"] for decision in trace["decisions"].values()} == {
        "stroke.add", "region.fill"
    }
    assert len({decision["actions"][0]["part"] for decision in trace["decisions"].values()}) == 4
    assert trace["decisions"]["subject"]["actions"][0]["part"] == "hands_and_feet/pocket_contact"
    assert trace["decisions"]["form_light"]["actions"][0]["kind"] == "region.fill"
