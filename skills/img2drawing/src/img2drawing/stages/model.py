from __future__ import annotations
from dataclasses import dataclass, field

@dataclass(frozen=True)
class StageSpec:
    stage_id: str
    index: int
    title: str
    intent: str
    observe: tuple[str, ...]
    draw: tuple[str, ...]
    avoid: tuple[str, ...]
    review_questions: tuple[str, ...] = ()
    advance_when: tuple[str, ...] = ()
    suggested_crops: tuple[str, ...] = ()

    def worker_brief(self) -> dict:
        """Self-contained stage instructions for a fresh worker.

        These are guidance, not semantic booleans. The worker must still
        inspect the actual subject and drawing artifact.
        """
        return {
            "stage_id": self.stage_id,
            "index": self.index,
            "title": self.title,
            "intent": self.intent,
            "observe": list(self.observe),
            "draw": list(self.draw),
            "avoid": list(self.avoid),
            "review_questions": list(self.review_questions),
            "advance_when": list(self.advance_when),
            "suggested_crops": list(self.suggested_crops),
        }

class StageOrderError(RuntimeError):
    pass

@dataclass
class StageProgress:
    stage_ids: tuple[str, ...]
    current_index: int = 0
    started_cursor: dict[str, int] = field(default_factory=dict)
    advanced_reviews: dict[str, str] = field(default_factory=dict)

    @property
    def current_stage(self) -> str | None:
        if self.current_index >= len(self.stage_ids):
            return None
        return self.stage_ids[self.current_index]

    def require_current(self, stage: str) -> None:
        if self.current_stage != stage:
            raise StageOrderError(f"expected {self.current_stage!r}, got {stage!r}")

    def mark_started(self, stage: str, cursor: int) -> None:
        self.require_current(stage)
        self.started_cursor.setdefault(stage, int(cursor))

    def advance(self, stage: str, review_digest: str) -> None:
        self.require_current(stage)
        if stage not in self.started_cursor:
            raise StageOrderError(
                f"stage {stage!r} must be started with stage_start() before advance"
            )
        self.advanced_reviews[stage] = str(review_digest)
        self.current_index += 1
