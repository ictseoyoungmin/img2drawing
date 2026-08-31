"""Evidence presentation/read-budget and observation telemetry primitives for vNext.

The policy controls inspection presentation and read budget; it never chooses a residual
or judges artistic quality.  Telemetry counts observable work only and deliberately has
no score, pass/fail, or completion field.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, replace
from typing import Any, Mapping, Sequence

from ..core.session import sha256_obj


EVIDENCE_MODES = ("quick", "focused", "deep")
MAX_PRIORITIZED_ROIS = 3
INSPECTION_ARTIFACTS = (
    "sheet",
    "raw_drawing",
    "registered_drawing",
    "contrast_overlay",
    "manifest",
    "measurements",
)
VISUAL_INSPECTION_ARTIFACTS = ("sheet", "raw_drawing", "registered_drawing", "contrast_overlay")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def _text(value: Any, field: str) -> str:
    result = str(value).strip()
    if not result:
        raise ValueError(f"{field} must be non-empty")
    return result


def _digest(value: Any, field: str) -> str:
    result = str(value).lower().strip()
    if not _SHA256.fullmatch(result):
        raise ValueError(f"{field} must be a SHA-256 digest")
    return result


@dataclass(frozen=True)
class EvidencePolicy:
    """Agent-selected evidence budget for one inspection sheet."""

    mode: str = "quick"
    escalation_reason: str | None = None
    roi_count: int = 0
    guide_count: int = 0
    measurement_count: int = 0
    grid_count: int = 0

    @classmethod
    def from_inputs(
        cls,
        *,
        mode: str | None,
        rois: Sequence[Any],
        guides: Sequence[Any],
        measurements: Sequence[Any],
        escalation_reason: str | None,
        grid: Any = None,
    ) -> "EvidencePolicy":
        roi_count = len(rois)
        guide_count = len(guides)
        measurement_count = len(measurements)
        grid_count = 0 if grid is None or grid is False else 1
        if roi_count > MAX_PRIORITIZED_ROIS:
            raise ValueError(
                f"vNext inspection permits at most {MAX_PRIORITIZED_ROIS} prioritized ROIs"
            )
        explicit_mode = None if mode is None else _text(mode, "mode").lower()
        has_guides_or_measurements = bool(guide_count or measurement_count or grid_count)
        selected_mode = explicit_mode or (
            "quick"
            if not (roi_count or has_guides_or_measurements)
            else ("deep" if has_guides_or_measurements else "focused")
        )
        if selected_mode not in EVIDENCE_MODES:
            raise ValueError(f"unsupported evidence mode: {selected_mode}")
        reason = None if escalation_reason is None else _text(escalation_reason, "escalation_reason")
        has_extras = bool(roi_count or guide_count or measurement_count or grid_count)
        if selected_mode == "quick" and has_extras:
            raise ValueError("quick evidence budget allows no ROIs, guides, or measurements")
        if selected_mode == "focused":
            if not 1 <= roi_count <= MAX_PRIORITIZED_ROIS:
                raise ValueError("focused evidence budget requires 1-3 prioritized ROIs")
            if guide_count or measurement_count or grid_count:
                raise ValueError("focused evidence budget allows ROIs only")
        if selected_mode == "deep" and reason is None:
            raise ValueError("deep evidence escalation requires escalation_reason")
        return cls(
            mode=selected_mode,
            escalation_reason=reason,
            roi_count=roi_count,
            guide_count=guide_count,
            measurement_count=measurement_count,
            grid_count=grid_count,
        )

    def __post_init__(self) -> None:
        mode = _text(self.mode, "mode").lower()
        if mode not in EVIDENCE_MODES:
            raise ValueError(f"unsupported evidence mode: {mode}")
        object.__setattr__(self, "mode", mode)
        reason = None if self.escalation_reason is None else _text(self.escalation_reason, "escalation_reason")
        object.__setattr__(self, "escalation_reason", reason)
        for field in ("roi_count", "guide_count", "measurement_count", "grid_count"):
            value = int(getattr(self, field))
            if value < 0:
                raise ValueError(f"{field} must be >= 0")
            object.__setattr__(self, field, value)
        if self.roi_count > MAX_PRIORITIZED_ROIS:
            raise ValueError(f"roi_count must be <= {MAX_PRIORITIZED_ROIS}")
        if self.mode == "quick" and (
            self.roi_count or self.guide_count or self.measurement_count or self.grid_count
        ):
            raise ValueError("quick evidence budget allows no ROIs, guides, or measurements")
        if self.mode == "focused":
            if not 1 <= self.roi_count <= MAX_PRIORITIZED_ROIS:
                raise ValueError("focused evidence budget requires 1-3 prioritized ROIs")
            if self.guide_count or self.measurement_count or self.grid_count:
                raise ValueError("focused evidence budget allows ROIs only")
        if self.mode == "deep" and self.escalation_reason is None:
            raise ValueError("deep evidence escalation requires escalation_reason")

    @property
    def escalated(self) -> bool:
        return self.mode == "deep" or bool(self.guide_count or self.measurement_count or self.grid_count)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "img2drawing.vnext.evidence_policy.v1",
            "mode": self.mode,
            "escalation_reason": self.escalation_reason,
            "roi_count": self.roi_count,
            "guide_count": self.guide_count,
            "measurement_count": self.measurement_count,
            "grid_count": self.grid_count,
            "max_prioritized_rois": MAX_PRIORITIZED_ROIS,
        }

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "EvidencePolicy":
        if raw.get("schema") not in (None, "img2drawing.vnext.evidence_policy.v1"):
            raise ValueError(f"unsupported evidence policy schema: {raw.get('schema')!r}")
        return cls(
            mode=str(raw.get("mode", "quick")),
            escalation_reason=raw.get("escalation_reason"),
            roi_count=int(raw.get("roi_count", 0)),
            guide_count=int(raw.get("guide_count", 0)),
            measurement_count=int(raw.get("measurement_count", 0)),
            grid_count=int(raw.get("grid_count", 0)),
        )


@dataclass(frozen=True)
class EvidenceReadRecord:
    """One observable artifact read, explicitly marked when its snapshot is stale."""

    event_id: str
    inspection_id: str
    artifact: str
    stale: bool
    inspection_drawing_state_hash: str
    current_drawing_state_hash: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "event_id", _text(self.event_id, "event_id"))
        object.__setattr__(self, "inspection_id", _text(self.inspection_id, "inspection_id"))
        object.__setattr__(self, "artifact", _text(self.artifact, "artifact"))
        object.__setattr__(self, "stale", bool(self.stale))
        object.__setattr__(
            self,
            "inspection_drawing_state_hash",
            _digest(self.inspection_drawing_state_hash, "inspection_drawing_state_hash"),
        )
        object.__setattr__(
            self,
            "current_drawing_state_hash",
            _digest(self.current_drawing_state_hash, "current_drawing_state_hash"),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "img2drawing.vnext.evidence_read.v1",
            "event_id": self.event_id,
            "inspection_id": self.inspection_id,
            "artifact": self.artifact,
            "stale": self.stale,
            "inspection_drawing_state_hash": self.inspection_drawing_state_hash,
            "current_drawing_state_hash": self.current_drawing_state_hash,
        }

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "EvidenceReadRecord":
        if raw.get("schema") not in (None, "img2drawing.vnext.evidence_read.v1"):
            raise ValueError(f"unsupported evidence read schema: {raw.get('schema')!r}")
        return cls(
            event_id=str(raw["event_id"]),
            inspection_id=str(raw["inspection_id"]),
            artifact=str(raw["artifact"]),
            stale=bool(raw.get("stale", False)),
            inspection_drawing_state_hash=str(raw["inspection_drawing_state_hash"]),
            current_drawing_state_hash=str(raw["current_drawing_state_hash"]),
        )


@dataclass(frozen=True)
class EvidenceTelemetry:
    """Portable counters for observable evidence work, without artistic judgement."""

    inspection_calls: int = 0
    review_turns: int = 0
    image_reads: int = 0
    generated_artifacts: int = 0
    visual_artifacts: int = 0
    elapsed_seconds: float = 0.0
    read_events: tuple[EvidenceReadRecord, ...] = ()

    def __post_init__(self) -> None:
        for field in (
            "inspection_calls",
            "review_turns",
            "image_reads",
            "generated_artifacts",
            "visual_artifacts",
        ):
            value = int(getattr(self, field))
            if value < 0:
                raise ValueError(f"{field} must be >= 0")
            object.__setattr__(self, field, value)
        elapsed = float(self.elapsed_seconds)
        if elapsed < 0.0 or not math.isfinite(elapsed):
            raise ValueError("elapsed_seconds must be finite and >= 0")
        object.__setattr__(self, "elapsed_seconds", elapsed)
        events = tuple(
            event if isinstance(event, EvidenceReadRecord) else EvidenceReadRecord.from_dict(event)
            for event in self.read_events
        )
        if len({event.event_id for event in events}) != len(events):
            raise ValueError("duplicate evidence read event_id")
        if self.image_reads != len(events):
            raise ValueError("image_reads must equal the number of read_events")
        object.__setattr__(self, "read_events", events)

    def after_inspection(
        self,
        *,
        artifact_count: int,
        visual_artifact_count: int,
        elapsed_seconds: float,
    ) -> "EvidenceTelemetry":
        artifact_count = int(artifact_count)
        visual_artifact_count = int(visual_artifact_count)
        elapsed_seconds = float(elapsed_seconds)
        if artifact_count < 0 or visual_artifact_count < 0:
            raise ValueError("artifact counts must be >= 0")
        if elapsed_seconds < 0.0 or not math.isfinite(elapsed_seconds):
            raise ValueError("elapsed_seconds must be finite and >= 0")
        return replace(
            self,
            inspection_calls=self.inspection_calls + 1,
            review_turns=self.review_turns + 1,
            generated_artifacts=self.generated_artifacts + artifact_count,
            visual_artifacts=self.visual_artifacts + visual_artifact_count,
            elapsed_seconds=self.elapsed_seconds + elapsed_seconds,
        )

    def with_read(self, event: EvidenceReadRecord) -> "EvidenceTelemetry":
        if not isinstance(event, EvidenceReadRecord):
            raise TypeError("evidence telemetry requires an EvidenceReadRecord")
        return replace(self, image_reads=self.image_reads + 1, read_events=self.read_events + (event,))

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "img2drawing.vnext.evidence_telemetry.v1",
            "inspection_calls": self.inspection_calls,
            "review_turns": self.review_turns,
            "image_reads": self.image_reads,
            "generated_artifacts": self.generated_artifacts,
            "visual_artifacts": self.visual_artifacts,
            "elapsed_seconds": self.elapsed_seconds,
            "read_events": [event.to_dict() for event in self.read_events],
        }

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any] | None) -> "EvidenceTelemetry":
        values = {} if raw is None else dict(raw)
        if values.get("schema") not in (None, "img2drawing.vnext.evidence_telemetry.v1"):
            raise ValueError(f"unsupported evidence telemetry schema: {values.get('schema')!r}")
        events = tuple(EvidenceReadRecord.from_dict(item) for item in values.get("read_events", ()))
        return cls(
            inspection_calls=int(values.get("inspection_calls", 0)),
            review_turns=int(values.get("review_turns", 0)),
            image_reads=int(values.get("image_reads", len(events))),
            generated_artifacts=int(values.get("generated_artifacts", 0)),
            visual_artifacts=int(values.get("visual_artifacts", 0)),
            elapsed_seconds=float(values.get("elapsed_seconds", 0.0)),
            read_events=events,
        )

    def digest(self) -> str:
        return sha256_obj(self.to_dict())


__all__ = [
    "EVIDENCE_MODES",
    "EvidencePolicy",
    "EvidenceReadRecord",
    "EvidenceTelemetry",
    "INSPECTION_ARTIFACTS",
    "MAX_PRIORITIZED_ROIS",
    "VISUAL_INSPECTION_ARTIFACTS",
]
