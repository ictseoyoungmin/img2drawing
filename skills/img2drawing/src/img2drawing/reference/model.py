from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import hashlib

from PIL import Image


def _sha256_file(path: str | Path) -> str:
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for block in iter(lambda:f.read(1<<20),b""):
            h.update(block)
    return h.hexdigest()


class ReferenceBundleError(ValueError):
    """Raised when reference authority is ambiguous or internally inconsistent."""


def _image_path(path: str | Path, *, label: str) -> Path:
    p=Path(path).expanduser().resolve()
    if not p.exists():
        raise FileNotFoundError(p)
    if not p.is_file():
        raise ReferenceBundleError(f"{label} must be a file: {p}")
    try:
        with Image.open(p) as im:
            im.verify()
    except Exception as exc:
        raise ReferenceBundleError(f"{label} is not a readable image: {p}") from exc
    return p


@dataclass(frozen=True)
class SubjectReference:
    path: Path
    sha256: str
    authority: str = "geometry_truth"

    @classmethod
    def from_path(cls, path: str | Path) -> "SubjectReference":
        p=_image_path(path,label="subject reference")
        return cls(path=p,sha256=_sha256_file(p))

    def to_dict(self) -> dict:
        return {
            "role":"subject_reference",
            "path":str(self.path),
            "sha256":self.sha256,
            "authority":self.authority,
            "decides":[
                "pose",
                "proportion",
                "perspective",
                "overlap",
                "weight distribution",
                "subject-specific silhouette",
            ],
            "must_not_decide":[
                "stage abstraction vocabulary",
                "which construction convention belongs to a stage",
            ],
        }


@dataclass(frozen=True)
class TaskStageTarget:
    stage_id: str
    path: Path
    sha256: str
    authority: str = "task_stage_truth"

    @classmethod
    def from_path(cls, stage_id: str, path: str | Path) -> "TaskStageTarget":
        if not str(stage_id).strip():
            raise ReferenceBundleError("task stage target requires a stage_id")
        p=_image_path(path,label=f"task stage target {stage_id}")
        return cls(stage_id=str(stage_id),path=p,sha256=_sha256_file(p))

    def to_dict(self) -> dict:
        mandatory_path_policy = (
            "unproven_until_ablation"
            if self.stage_id == "P3_primary_masses"
            else "mandatory_positive_reference"
        )
        return {
            "role":"task_stage_target",
            "stage_id":self.stage_id,
            "path":str(self.path),
            "sha256":self.sha256,
            "authority":self.authority,
            "decides":[
                "same-task stage-specific expected abstraction",
                "same-subject stage-specific placement and relationships",
            ],
            "must_not_decide":[
                "facts that contradict the subject reference",
                "generic stage grammar outside the current task",
            ],
        }


@dataclass(frozen=True)
class StageReferenceView:
    stage_id: str
    subject: SubjectReference
    task_stage_target: TaskStageTarget | None
    authority_order: tuple[str, ...]

    @property
    def has_task_stage_target(self) -> bool:
        return self.task_stage_target is not None

    @property
    def reference_mode(self) -> str:
        return (
            "task_stage_target_augmented"
            if self.task_stage_target is not None
            else "subject_only"
        )

    def to_dict(self) -> dict:
        return {
            "stage_id":self.stage_id,
            "reference_mode":self.reference_mode,
            "authority_order":list(self.authority_order),
            "subject_reference":self.subject.to_dict(),
            "task_stage_target":None if self.task_stage_target is None else self.task_stage_target.to_dict(),
            "subject_only_rule":(
                None if self.task_stage_target is not None else
                "Derive stage geometry from the subject and verified prior drawing state."
            ),
        }


@dataclass(frozen=True)
class ReferenceBundle:
    subject: SubjectReference
    task_stage_targets: dict[str, TaskStageTarget]

    def __post_init__(self):
        for stage_id, item in self.task_stage_targets.items():
            if stage_id != item.stage_id:
                raise ReferenceBundleError(
                    f"task target key/stage mismatch: {stage_id!r} != {item.stage_id!r}"
                )

    def for_stage(self, stage_id: str) -> StageReferenceView:
        task=self.task_stage_targets.get(stage_id)
        order=(
            ("task_stage_target","subject_reference")
            if task is not None
            else ("subject_reference",)
        )
        return StageReferenceView(
            stage_id=stage_id,
            subject=self.subject,
            task_stage_target=task,
            authority_order=order,
        )

    def to_dict(self) -> dict:
        return {
            "schema":"img2drawing.reference_bundle.v1",
            "default_reference_mode":"subject_only",
            "authority_policy":{
                "with_task_stage_target":[
                    "task_stage_target",
                    "subject_reference",
                ],
                "without_task_stage_target":[
                    "subject_reference",
                ],
                "notes":[
                    "Task stage targets are strongest only when they belong to the same task/subject.",
                    "Subject reference remains geometry truth and resolves contradictions about pose/proportion/perspective.",
                ],
            },
            "subject_reference":self.subject.to_dict(),
            "task_stage_targets":{
                k:v.to_dict() for k,v in sorted(self.task_stage_targets.items())
            },
        }
