from __future__ import annotations

from pathlib import Path
from typing import Mapping

from .model import (
    ReferenceBundle,
    ReferenceBundleError,
    SubjectReference,
    TaskStageTarget,
)


def build_reference_bundle(
    *,
    subject_reference: str | Path,
    stage_ids,
    task_stage_targets: Mapping[str, str | Path] | None = None,
) -> ReferenceBundle:
    allowed=set(map(str,stage_ids))
    if not allowed:
        raise ReferenceBundleError("stage_ids must be non-empty")

    raw_targets=dict(task_stage_targets or {})
    unknown=sorted(set(raw_targets)-allowed)
    if unknown:
        raise ReferenceBundleError(
            "task_stage_targets contains unknown stage ids: "+", ".join(unknown)
        )

    return ReferenceBundle(
        subject=SubjectReference.from_path(subject_reference),
        task_stage_targets={
            stage:TaskStageTarget.from_path(stage,path)
            for stage,path in raw_targets.items()
        },
    )
