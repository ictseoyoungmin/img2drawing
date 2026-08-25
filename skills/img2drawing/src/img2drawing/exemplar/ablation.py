from __future__ import annotations

"""A/B/C exemplar-transfer ablation records."""

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from ..core.session import sha256_obj


ABLATION_CONDITIONS = (
    "A_subject_contract",
    "B_full_body_exemplar",
    "C_modular_cards",
)


@dataclass(frozen=True)
class ModularGrammarCard:
    card_id: str
    stage: str
    polarity: str
    scope: tuple[str, ...]
    transfer_mapping: tuple[str, ...]
    source_audit_status: str

    def __post_init__(self) -> None:
        if not str(self.card_id).strip() or not str(self.stage).strip():
            raise ValueError("grammar card requires card_id and stage")
        polarity = str(self.polarity)
        if polarity not in {"positive", "negative"}:
            raise ValueError("grammar card polarity must be positive or negative")
        scope = tuple(item for item in (str(x).strip() for x in self.scope) if item)
        mapping = tuple(item for item in (str(x).strip() for x in self.transfer_mapping) if item)
        if not scope or not mapping:
            raise ValueError("grammar card requires scope and transfer_mapping")
        audit = str(self.source_audit_status)
        if audit not in {"pass", "fail", "unproven", "not_audited"}:
            raise ValueError("unknown source_audit_status")
        if polarity == "positive" and audit == "fail":
            raise ValueError("FAIL exemplar cannot become a positive grammar card")
        object.__setattr__(self, "card_id", str(self.card_id).strip())
        object.__setattr__(self, "stage", str(self.stage).strip())
        object.__setattr__(self, "polarity", polarity)
        object.__setattr__(self, "scope", scope)
        object.__setattr__(self, "transfer_mapping", mapping)
        object.__setattr__(self, "source_audit_status", audit)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "img2drawing.modular_grammar_card.v1",
            "card_id": self.card_id,
            "stage": self.stage,
            "polarity": self.polarity,
            "scope": list(self.scope),
            "transfer_mapping": list(self.transfer_mapping),
            "source_audit_status": self.source_audit_status,
        }

    def stroke_plan_metadata(
        self,
        *,
        part: str | None = None,
        role: str | None = None,
    ) -> dict[str, Any]:
        """Return deterministic, non-geometric consumption metadata.

        A card describes *what to look for* when authoring a stroke plan; it
        does not describe where pixels belong.  The returned tokens therefore
        carry the ordered transfer mappings and their provenance, but contain
        no points, dimensions, or coordinate transforms.  A runner may use
        the tokens while consulting the frozen subject observation for all
        geometry decisions.
        """
        normalized_part = None if part is None else str(part).strip()
        normalized_role = None if role is None else str(role).strip()
        if part is not None and not normalized_part:
            raise ValueError("part must be non-empty when supplied")
        if role is not None and not normalized_role:
            raise ValueError("role must be non-empty when supplied")

        payload = self.to_dict()
        tokens = [
            {
                "token_id": f"{self.card_id}:transfer:{index:02d}",
                "stage": self.stage,
                "part": normalized_part,
                "role": normalized_role,
                "mapping": mapping,
                "scope": list(self.scope),
                "polarity": self.polarity,
                "geometry_authority": "frozen_subject_observation",
            }
            for index, mapping in enumerate(self.transfer_mapping, start=1)
        ]
        return {
            "schema": "img2drawing.grammar_card_stroke_plan.v1",
            "card_id": self.card_id,
            "card_digest": sha256_obj(payload),
            "stage": self.stage,
            "polarity": self.polarity,
            "source_audit_status": self.source_audit_status,
            "scope": list(self.scope),
            "geometry_authority": "frozen_subject_observation",
            "geometry_mutation": "forbidden",
            "transfer_tokens": tokens,
        }

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "ModularGrammarCard":
        return cls(
            card_id=str(raw["card_id"]),
            stage=str(raw["stage"]),
            polarity=str(raw["polarity"]),
            scope=tuple(map(str, raw.get("scope", ()))),
            transfer_mapping=tuple(map(str, raw.get("transfer_mapping", ()))),
            source_audit_status=str(raw.get("source_audit_status", "not_audited")),
        )


def consume_grammar_card(
    card: ModularGrammarCard | Mapping[str, Any],
    *,
    part: str | None = None,
    role: str | None = None,
) -> dict[str, Any]:
    """Build stroke-plan guidance from one grammar card.

    This is an explicit opt-in boundary for a runner.  It consumes only the
    card's ordered ``transfer_mapping`` and never mutates a drawing plan or
    supplies geometry.  ``part`` and ``role`` merely scope the returned
    tokens so a caller can attach them to the intended authored strokes.
    """
    if isinstance(card, ModularGrammarCard):
        normalized = card
    elif isinstance(card, Mapping):
        normalized = ModularGrammarCard.from_dict(card)
    else:
        raise TypeError("card must be a ModularGrammarCard or mapping")
    return normalized.stroke_plan_metadata(part=part, role=role)


@dataclass(frozen=True)
class AblationTrial:
    condition: str
    region_blockers: int
    reopen_count: int
    residual_discrepancy: float
    p4_structural_errors: int
    p4_tracked: bool
    evidence_refs: tuple[str, ...]
    notes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        condition = str(self.condition)
        if condition not in ABLATION_CONDITIONS:
            raise ValueError(f"condition must be one of {ABLATION_CONDITIONS}")
        for value, label in (
            (self.region_blockers, "region_blockers"),
            (self.reopen_count, "reopen_count"),
            (self.p4_structural_errors, "p4_structural_errors"),
        ):
            if int(value) < 0:
                raise ValueError(f"{label} must be >= 0")
        discrepancy = float(self.residual_discrepancy)
        if discrepancy < 0.0:
            raise ValueError("residual_discrepancy must be >= 0")
        if not bool(self.p4_tracked):
            raise ValueError("A/B/C trial must be tracked through P4")
        refs = tuple(item for item in (str(x).strip() for x in self.evidence_refs) if item)
        if not refs:
            raise ValueError("ablation trial requires evidence_refs")
        object.__setattr__(self, "condition", condition)
        object.__setattr__(self, "region_blockers", int(self.region_blockers))
        object.__setattr__(self, "reopen_count", int(self.reopen_count))
        object.__setattr__(self, "residual_discrepancy", discrepancy)
        object.__setattr__(self, "p4_structural_errors", int(self.p4_structural_errors))
        object.__setattr__(self, "p4_tracked", True)
        object.__setattr__(self, "evidence_refs", refs)
        object.__setattr__(self, "notes", tuple(map(str, self.notes)))

    @property
    def metric_tuple(self) -> tuple[float, ...]:
        return (
            float(self.region_blockers),
            float(self.reopen_count),
            float(self.residual_discrepancy),
            float(self.p4_structural_errors),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "condition": self.condition,
            "region_blockers": self.region_blockers,
            "reopen_count": self.reopen_count,
            "residual_discrepancy": self.residual_discrepancy,
            "p4_structural_errors": self.p4_structural_errors,
            "p4_tracked": self.p4_tracked,
            "evidence_refs": list(self.evidence_refs),
            "notes": list(self.notes),
        }

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "AblationTrial":
        return cls(
            condition=str(raw["condition"]),
            region_blockers=int(raw["region_blockers"]),
            reopen_count=int(raw["reopen_count"]),
            residual_discrepancy=float(raw["residual_discrepancy"]),
            p4_structural_errors=int(raw["p4_structural_errors"]),
            p4_tracked=bool(raw["p4_tracked"]),
            evidence_refs=tuple(map(str, raw.get("evidence_refs", ()))),
            notes=tuple(map(str, raw.get("notes", ()))),
        )


@dataclass(frozen=True)
class ExemplarAblationReport:
    trials: tuple[AblationTrial, ...]
    best_condition: str
    recommendation: str
    metric_order: tuple[str, ...]
    rationale: str

    def __post_init__(self) -> None:
        trials = tuple(item if isinstance(item, AblationTrial) else AblationTrial.from_dict(item) for item in self.trials)
        if {item.condition for item in trials} != set(ABLATION_CONDITIONS):
            raise ValueError("A/B/C report requires exactly one trial for each condition")
        if len(trials) != len(ABLATION_CONDITIONS):
            raise ValueError("A/B/C report cannot contain duplicate conditions")
        if self.best_condition not in ABLATION_CONDITIONS:
            raise ValueError("best_condition must be an A/B/C condition")
        if self.recommendation not in {"adopt_modular_cards", "retain_subject_contract", "unproven"}:
            raise ValueError("unknown ablation recommendation")
        if not str(self.rationale).strip():
            raise ValueError("ablation report requires rationale")
        object.__setattr__(self, "trials", trials)
        object.__setattr__(self, "metric_order", tuple(map(str, self.metric_order)))
        object.__setattr__(self, "rationale", str(self.rationale).strip())

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "img2drawing.exemplar_ablation.v1",
            "conditions": list(ABLATION_CONDITIONS),
            "trials": [item.to_dict() for item in self.trials],
            "best_condition": self.best_condition,
            "recommendation": self.recommendation,
            "metric_order": list(self.metric_order),
            "rationale": self.rationale,
            "authority": "structural_metrics_not_prettiness",
        }

    def save(self, path: str | Path) -> Path:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(self.to_dict(), indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")
        return target


def run_exemplar_ablation(trials: Sequence[AblationTrial]) -> ExemplarAblationReport:
    trials = tuple(item if isinstance(item, AblationTrial) else AblationTrial.from_dict(item) for item in trials)
    if len(trials) != 3 or {item.condition for item in trials} != set(ABLATION_CONDITIONS):
        raise ValueError("run_exemplar_ablation requires A, B, and C trials")
    ordered = sorted(trials, key=lambda item: (item.metric_tuple, item.condition))
    best = ordered[0]
    baseline = next(item for item in trials if item.condition == "A_subject_contract")
    modular = next(item for item in trials if item.condition == "C_modular_cards")
    full_exemplar = next(item for item in trials if item.condition == "B_full_body_exemplar")
    modular_beats_baseline = all(a < b for a, b in zip(modular.metric_tuple, baseline.metric_tuple))
    modular_beats_full = all(a < b for a, b in zip(modular.metric_tuple, full_exemplar.metric_tuple))
    if modular_beats_baseline and modular_beats_full:
        recommendation = "adopt_modular_cards"
        rationale = "C modular cards strictly improve all ordered structural metrics relative to A and B."
    elif all(a <= b for a, b in zip(baseline.metric_tuple, full_exemplar.metric_tuple)) and all(a <= b for a, b in zip(baseline.metric_tuple, modular.metric_tuple)):
        recommendation = "retain_subject_contract"
        rationale = "A subject+contract is no worse than exemplar/card conditions on the ordered structural metrics."
    else:
        recommendation = "unproven"
        rationale = "No condition provides a strict, clean structural win; keep exemplar transfer unproven."
    return ExemplarAblationReport(
        trials=trials,
        best_condition=best.condition,
        recommendation=recommendation,
        metric_order=("region_blockers", "reopen_count", "residual_discrepancy", "p4_structural_errors"),
        rationale=rationale,
    )


__all__ = [
    "ABLATION_CONDITIONS", "ModularGrammarCard", "consume_grammar_card", "AblationTrial",
    "ExemplarAblationReport", "run_exemplar_ablation",
]
