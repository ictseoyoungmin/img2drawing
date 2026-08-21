from __future__ import annotations
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any

@dataclass(frozen=True)
class ObservationContract:
    """Agent-authored semantic memory.

    The runtime validates shape only. It never infers pose, anatomy, or correctness.
    """
    subject_summary: str
    global_relations: dict[str, Any] = field(default_factory=dict)
    parts: dict[str, Any] = field(default_factory=dict)
    uncertainties: tuple[str, ...] = ()
    drawing_priorities: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()

    def __post_init__(self):
        if not self.subject_summary.strip():
            raise ValueError("subject_summary must be non-empty")
        if not isinstance(self.global_relations, dict):
            raise TypeError("global_relations must be a dict")
        if not isinstance(self.parts, dict):
            raise TypeError("parts must be a dict")

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "img2drawing.observation.v2",
            "semantic_authority": "agent",
            "automatic_semantic_inference": False,
            "subject_summary": self.subject_summary,
            "global_relations": deepcopy(self.global_relations),
            "parts": deepcopy(self.parts),
            "uncertainties": list(self.uncertainties),
            "drawing_priorities": list(self.drawing_priorities),
            "evidence_refs": list(self.evidence_refs),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ObservationContract":
        return cls(
            subject_summary=str(data["subject_summary"]),
            global_relations=deepcopy(data.get("global_relations", {})),
            parts=deepcopy(data.get("parts", {})),
            uncertainties=tuple(map(str, data.get("uncertainties", ()))),
            drawing_priorities=tuple(map(str, data.get("drawing_priorities", ()))),
            evidence_refs=tuple(map(str, data.get("evidence_refs", ()))),
        )
