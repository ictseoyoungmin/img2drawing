from __future__ import annotations

import json
from pathlib import Path
import warnings

import pytest
from jsonschema import validators

from img2drawing import AblationTrial, ModularGrammarCard, run_exemplar_ablation


ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas"


def _trial(condition: str, blockers: int, reopens: int, residual: float, p4: int) -> AblationTrial:
    return AblationTrial(
        condition=condition,
        region_blockers=blockers,
        reopen_count=reopens,
        residual_discrepancy=residual,
        p4_structural_errors=p4,
        p4_tracked=True,
        evidence_refs=(f"evidence/{condition}.json",),
    )


def test_fail_exemplar_cannot_become_positive_card():
    with pytest.raises(ValueError, match="FAIL exemplar"):
        ModularGrammarCard(
            card_id="bad",
            stage="P3_primary_masses",
            polarity="positive",
            scope=("mass",),
            transfer_mapping=("subject envelope only",),
            source_audit_status="fail",
        )
    card = ModularGrammarCard(
        card_id="negative-p1",
        stage="P1_gesture",
        polarity="negative",
        scope=("gesture economy",),
        transfer_mapping=("warn against copying failed continuity",),
        source_audit_status="fail",
    )
    assert card.to_dict()["polarity"] == "negative"


def test_ablation_prefers_modular_cards_only_on_strict_structural_win():
    report = run_exemplar_ablation(
        (
            _trial("A_subject_contract", 4, 3, 0.40, 3),
            _trial("B_full_body_exemplar", 5, 4, 0.55, 4),
            _trial("C_modular_cards", 2, 1, 0.20, 1),
        )
    )
    assert report.best_condition == "C_modular_cards"
    assert report.recommendation == "adopt_modular_cards"
    assert report.to_dict()["authority"] == "structural_metrics_not_prettiness"


def test_ablation_keeps_transfer_unproven_without_clean_win():
    report = run_exemplar_ablation(
        (
            _trial("A_subject_contract", 2, 1, 0.20, 1),
            _trial("B_full_body_exemplar", 2, 1, 0.20, 1),
            _trial("C_modular_cards", 2, 1, 0.20, 1),
        )
    )
    assert report.recommendation == "retain_subject_contract"


def test_ablation_schema_roundtrip():
    report = run_exemplar_ablation(
        (
            _trial("A_subject_contract", 3, 2, 0.30, 2),
            _trial("B_full_body_exemplar", 4, 3, 0.50, 3),
            _trial("C_modular_cards", 2, 1, 0.15, 1),
        )
    )
    schema = json.loads((SCHEMAS / "exemplar_ablation.schema.json").read_text())
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        validators.validator_for(schema)(schema).validate(report.to_dict())
    card_schema = json.loads((SCHEMAS / "modular_grammar_card.schema.json").read_text())
    card = ModularGrammarCard("p2-axis", "P2_primary_axes", "positive", ("axis",), ("subject endpoints",), "pass")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        validators.validator_for(card_schema)(card_schema).validate(card.to_dict())
