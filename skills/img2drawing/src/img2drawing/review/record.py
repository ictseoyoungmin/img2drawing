from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .artifact import sha256_obj
from .reference_review import ReferenceReviewArtifacts
from .pass_memory import StagePassMemory



def normalize_findings(value, *, field: str = "findings") -> tuple[str, ...]:
    """Normalize review findings without splitting a scalar string into characters."""
    if value is None:
        return ()
    if isinstance(value, str):
        item=value.strip()
        return (item,) if item else ()
    try:
        items=tuple(value)
    except TypeError as exc:
        raise TypeError(f"{field} must be a string or iterable of strings") from exc
    out=[]
    for raw in items:
        item=str(raw).strip()
        if item:
            out.append(item)
    return tuple(out)


@dataclass(frozen=True)
class StageReviewRecord:
    stage: str
    stage_contract_id: str
    drawing_state_sha256: str
    drawing_artifact_sha256: str
    history_cursor: int

    pass_memory_digest: str
    parent_review_digest: str | None
    carried_concerns: tuple[str, ...]
    inter_pass_action_ids: tuple[str, ...]

    subject_reference: str
    task_stage_target: str | None
    reference_authority_order: tuple[str, ...]

    contract_findings: tuple[str,...]
    subject_findings: tuple[str,...]
    grammar_findings: tuple[str,...]
    drawing_findings: tuple[str,...]
    task_target_findings: tuple[str,...] = ()
    local_review_ids: tuple[str,...] = ()

    corrections: tuple[str,...] = ()
    remaining_concerns: tuple[str,...] = ()
    decision: str = "revise"
    advance_rationale: str = ""

    def __post_init__(self):
        if self.decision not in {"revise","advance"}:
            raise ValueError("decision must be 'revise' or 'advance'")
        if not self.stage_contract_id.strip():
            raise ValueError("review requires stage_contract_id")
        if not self.pass_memory_digest.strip():
            raise ValueError("review requires pass_memory_digest")
        if self.parent_review_digest is None and self.carried_concerns:
            raise ValueError(
                "cold-start review cannot carry concerns without a parent review"
            )
        if not self.contract_findings:
            raise ValueError("review requires contract_findings")
        if not self.subject_findings:
            raise ValueError("review requires subject_findings")
        if not self.grammar_findings:
            raise ValueError("review requires grammar_findings")
        if not self.drawing_findings:
            raise ValueError("review requires drawing_findings")
        if self.task_stage_target is not None and not self.task_target_findings:
            raise ValueError(
                "review with a task stage target requires task_target_findings"
            )
        if self.decision == "advance":
            if self.remaining_concerns:
                raise ValueError("advance requires remaining_concerns to be empty")
            if not self.advance_rationale.strip():
                raise ValueError("advance requires a concrete advance_rationale")

    @classmethod
    def from_dict(cls,data):
        return cls(
            stage=str(data["stage"]),
            stage_contract_id=str(data["stage_contract_id"]),
            drawing_state_sha256=str(data["drawing_state_sha256"]),
            drawing_artifact_sha256=str(data["drawing_artifact_sha256"]),
            history_cursor=int(data["history_cursor"]),
            pass_memory_digest=str(data["pass_memory_digest"]),
            parent_review_digest=data.get("parent_review_digest"),
            carried_concerns=normalize_findings(data.get("carried_concerns",()), field="carried_concerns"),
            inter_pass_action_ids=normalize_findings(data.get("inter_pass_action_ids",()), field="inter_pass_action_ids"),
            subject_reference=str(data["subject_reference"]),
            task_stage_target=data.get("task_stage_target"),
            reference_authority_order=normalize_findings(data.get("reference_authority_order",()), field="reference_authority_order"),
            contract_findings=normalize_findings(data.get("contract_findings",()), field="contract_findings"),
            subject_findings=normalize_findings(data.get("subject_findings",()), field="subject_findings"),
            grammar_findings=normalize_findings(
                data.get("grammar_findings", data.get("exemplar_findings",())),
                field="grammar_findings",
            ),
            drawing_findings=normalize_findings(data.get("drawing_findings",()), field="drawing_findings"),
            task_target_findings=normalize_findings(data.get("task_target_findings",()), field="task_target_findings"),
            local_review_ids=normalize_findings(data.get("local_review_ids",()), field="local_review_ids"),
            corrections=normalize_findings(data.get("corrections",()), field="corrections"),
            remaining_concerns=normalize_findings(data.get("remaining_concerns",()), field="remaining_concerns"),
            decision=str(data.get("decision","revise")),
            advance_rationale=str(data.get("advance_rationale","")),
        )

    @property
    def observations(self) -> tuple[str,...]:
        return (
            self.contract_findings
            + self.task_target_findings
            + self.subject_findings
            + self.grammar_findings
            + self.drawing_findings
        )

    def to_dict(self):
        return {
            "schema":"img2drawing.stage_review.v6",
            "stage":self.stage,
            "stage_contract_id":self.stage_contract_id,
            "drawing_state_sha256":self.drawing_state_sha256,
            "drawing_artifact_sha256":self.drawing_artifact_sha256,
            "history_cursor":self.history_cursor,
            "pass_memory_digest":self.pass_memory_digest,
            "parent_review_digest":self.parent_review_digest,
            "carried_concerns":list(self.carried_concerns),
            "inter_pass_action_ids":list(self.inter_pass_action_ids),
            "reference_authority_order":list(self.reference_authority_order),
            "subject_reference":self.subject_reference,
            "task_stage_target":self.task_stage_target,
            "contract_findings":list(self.contract_findings),
            "task_target_findings":list(self.task_target_findings),
            "local_review_ids":list(self.local_review_ids),
            "subject_findings":list(self.subject_findings),
            "grammar_findings":list(self.grammar_findings),
            "drawing_findings":list(self.drawing_findings),
            "observations":list(self.observations),
            "corrections":list(self.corrections),
            "remaining_concerns":list(self.remaining_concerns),
            "decision":self.decision,
            "advance_rationale":self.advance_rationale,
            "semantic_authority":"agent",
        }

    def digest(self) -> str:
        return sha256_obj(self.to_dict())

    def save(self,path: str|Path) -> Path:
        p=Path(path); p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text(
            json.dumps(self.to_dict(),indent=2,ensure_ascii=False,sort_keys=True),
            encoding="utf-8",
        )
        return p


def record_from_artifacts(
    artifacts: ReferenceReviewArtifacts,
    *,
    stage_contract_id: str,
    pass_memory: StagePassMemory,
    contract_findings,
    subject_findings,
    grammar_findings,
    drawing_findings,
    task_target_findings=(),
    local_review_ids=(),
    corrections=(),
    remaining_concerns=(),
    decision="revise",
    advance_rationale="",
):
    d=artifacts.drawing
    return StageReviewRecord(
        stage=artifacts.stage,
        stage_contract_id=str(stage_contract_id),
        drawing_state_sha256=d.state_sha256,
        drawing_artifact_sha256=d.artifact_sha256,
        history_cursor=d.history_cursor,
        pass_memory_digest=pass_memory.digest(),
        parent_review_digest=pass_memory.previous_review_digest,
        carried_concerns=tuple(pass_memory.carried_concerns),
        inter_pass_action_ids=tuple(
            action.action_id for action in pass_memory.inter_pass_actions
        ),
        subject_reference=str(artifacts.subject_reference),
        task_stage_target=(
            None if artifacts.task_stage_target is None
            else str(artifacts.task_stage_target)
        ),
        reference_authority_order=tuple(artifacts.authority_order),
        contract_findings=normalize_findings(contract_findings, field="contract_findings"),
        task_target_findings=normalize_findings(task_target_findings, field="task_target_findings"),
        local_review_ids=normalize_findings(local_review_ids, field="local_review_ids"),
        subject_findings=normalize_findings(subject_findings, field="subject_findings"),
        grammar_findings=normalize_findings(grammar_findings, field="grammar_findings"),
        drawing_findings=normalize_findings(drawing_findings, field="drawing_findings"),
        corrections=normalize_findings(corrections, field="corrections"),
        remaining_concerns=normalize_findings(remaining_concerns, field="remaining_concerns"),
        decision=str(decision),
        advance_rationale=str(advance_rationale),
    )
