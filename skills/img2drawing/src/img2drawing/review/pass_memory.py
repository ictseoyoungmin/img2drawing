from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .artifact import sha256_obj


CORRECTION_ACTION_KINDS = frozenset({
    "replace_stroke",
    "replace_segment",
    "soft_lift_segment",
    "soft_lift",
    "delete_stroke",
})


@dataclass(frozen=True)
class ActionMemory:
    action_id: str
    stage: str
    kind: str
    part: str | None
    target_stroke_id: str | None
    reason: str | None
    history_cursor: int
    is_correction_action: bool

    @classmethod
    def from_dict(cls,data: dict[str,Any]) -> "ActionMemory":
        return cls(
            action_id=str(data["action_id"]), stage=str(data["stage"]), kind=str(data["kind"]),
            part=data.get("part"), target_stroke_id=data.get("target_stroke_id"),
            reason=data.get("reason"), history_cursor=int(data["history_cursor"]),
            is_correction_action=bool(data.get("is_correction_action",False)),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "action_id": self.action_id,
            "stage": self.stage,
            "kind": self.kind,
            "part": self.part,
            "target_stroke_id": self.target_stroke_id,
            "reason": self.reason,
            "history_cursor": self.history_cursor,
            "is_correction_action": self.is_correction_action,
        }


@dataclass(frozen=True)
class StagePassMemory:
    stage: str
    next_pass_index: int
    state: str
    prior_review_count: int
    previous_review_digest: str | None
    previous_decision: str | None
    previous_remaining_concerns: tuple[str, ...]
    previous_reported_corrections: tuple[str, ...]
    carried_concerns: tuple[str, ...]
    inter_pass_actions: tuple[ActionMemory, ...]
    inter_pass_correction_actions: tuple[ActionMemory, ...]
    concern_history: tuple[dict[str, Any], ...]
    correction_history: tuple[dict[str, Any], ...]
    memory_policy: tuple[str, ...]
    reopen_context: dict[str, Any] | None = None

    def __post_init__(self):
        if self.state not in {"cold_start", "revision_continuation", "reopen_restart"}:
            raise ValueError(f"unsupported pass-memory state: {self.state!r}")
        if self.next_pass_index < 1:
            raise ValueError("next_pass_index must be >= 1")
        if self.state == "cold_start":
            if self.prior_review_count != 0 or self.previous_review_digest is not None:
                raise ValueError("cold_start memory cannot have previous review state")
        if self.state == "revision_continuation":
            if self.prior_review_count < 1 or not self.previous_review_digest:
                raise ValueError("revision_continuation requires a previous review")
            if self.previous_decision != "revise":
                raise ValueError(
                    "same-stage next-pass memory may only continue from a revise review"
                )
        if self.state == "reopen_restart":
            if self.prior_review_count != 0 or self.previous_review_digest is not None:
                raise ValueError("reopen_restart begins a fresh active review epoch")
            if not isinstance(self.reopen_context, dict):
                raise ValueError("reopen_restart requires reopen_context")

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "img2drawing.stage_pass_memory.v2",
            "stage": self.stage,
            "next_pass_index": self.next_pass_index,
            "state": self.state,
            "prior_review_count": self.prior_review_count,
            "previous_review_digest": self.previous_review_digest,
            "previous_decision": self.previous_decision,
            "previous_remaining_concerns": list(self.previous_remaining_concerns),
            "previous_reported_corrections": list(self.previous_reported_corrections),
            "carried_concerns": list(self.carried_concerns),
            "inter_pass_actions": [x.to_dict() for x in self.inter_pass_actions],
            "inter_pass_correction_actions": [
                x.to_dict() for x in self.inter_pass_correction_actions
            ],
            "concern_history": list(self.concern_history),
            "correction_history": list(self.correction_history),
            "reopen_context": self.reopen_context,
            "memory_policy": list(self.memory_policy),
        }

    def digest(self) -> str:
        return sha256_obj(self.to_dict())


def make_action_memory(action, *, history_cursor: int) -> ActionMemory:
    return ActionMemory(
        action_id=str(action.action_id),
        stage=str(action.stage),
        kind=str(action.kind),
        part=None if action.part is None else str(action.part),
        target_stroke_id=(
            None if action.target_stroke_id is None
            else str(action.target_stroke_id)
        ),
        reason=None if action.reason is None else str(action.reason),
        history_cursor=int(history_cursor),
        is_correction_action=str(action.kind) in CORRECTION_ACTION_KINDS,
    )


def build_stage_pass_memory(
    *,
    stage: str,
    next_pass_index: int,
    reviews,
    action_events,
    reopen_context=None,
) -> StagePassMemory:
    reviews=tuple(reviews)
    stage_actions=tuple(
        event for event in action_events
        if str(event.stage) == str(stage)
    )

    concern_history=tuple(
        {
            "pass_index": i,
            "decision": review.decision,
            "review_digest": review.digest(),
            "remaining_concerns": list(review.remaining_concerns),
        }
        for i,review in enumerate(reviews,1)
    )
    correction_history=tuple(
        {
            "pass_index": i,
            "review_digest": review.digest(),
            "reported_corrections": list(review.corrections),
        }
        for i,review in enumerate(reviews,1)
    )

    if not reviews:
        state="reopen_restart" if reopen_context is not None else "cold_start"
        policy=(
            (
                "This active review epoch was restarted by an upstream/downstream reopen; read reopen_context before drawing.",
                "Rebuild from the restored authoritative history, not from archived invalidated artifacts.",
                "The reopen reason is Agent-authored evidence; runtime does not invent the correction.",
                "Concern resolution must be stated by the Agent in a fresh review, not inferred by the runtime.",
            )
            if reopen_context is not None
            else (
                "No prior stage review exists; begin from the stage contract and references.",
                "Runtime memory never invents artistic conclusions.",
                "Concern resolution must be stated by the Agent in a fresh review, not inferred by the runtime.",
            )
        )
        return StagePassMemory(
            stage=str(stage),
            next_pass_index=int(next_pass_index),
            state=state,
            prior_review_count=0,
            previous_review_digest=None,
            previous_decision=None,
            previous_remaining_concerns=(),
            previous_reported_corrections=(),
            carried_concerns=(),
            inter_pass_actions=tuple(stage_actions),
            inter_pass_correction_actions=tuple(
                event for event in stage_actions if event.is_correction_action
            ),
            concern_history=(),
            correction_history=(),
            reopen_context=None if reopen_context is None else dict(reopen_context),
            memory_policy=policy,
        )

    previous=reviews[-1]
    if previous.decision != "revise":
        raise ValueError(
            f"cannot prepare another pass for {stage!r} after decision={previous.decision!r}"
        )

    inter_pass=tuple(
        event for event in stage_actions
        if int(event.history_cursor) > int(previous.history_cursor)
    )
    correction_actions=tuple(
        event for event in inter_pass if event.is_correction_action
    )

    return StagePassMemory(
        stage=str(stage),
        next_pass_index=int(next_pass_index),
        state="revision_continuation",
        prior_review_count=len(reviews),
        previous_review_digest=previous.digest(),
        previous_decision=previous.decision,
        previous_remaining_concerns=tuple(previous.remaining_concerns),
        previous_reported_corrections=tuple(previous.corrections),
        carried_concerns=tuple(previous.remaining_concerns),
        inter_pass_actions=inter_pass,
        inter_pass_correction_actions=correction_actions,
        concern_history=concern_history,
        correction_history=correction_history,
        reopen_context=None if reopen_context is None else dict(reopen_context),
        memory_policy=(
            "Start the next pass by re-checking carried_concerns against fresh artifacts.",
            "inter_pass_actions are mechanical action provenance, not proof that a concern was solved.",
            "Do not infer resolved concerns by set subtraction or scores; the Agent must make a fresh visual judgement.",
            "Use correction history to avoid repeating an ineffective edit without changing observation strategy.",
        ),
    )
