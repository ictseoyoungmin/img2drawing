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
class GrammarExemplar:
    stage_id: str
    path: Path
    sha256: str
    purpose: str = "representation_only"
    authority: str = "representation_guidance"
    audit_status: str = "not_audited"
    audit_contract_id: str | None = None
    audit_findings: tuple[str, ...] = ()
    audit_note: str = ""

    @classmethod
    def from_path(
        cls,
        stage_id: str,
        path: str | Path,
        *,
        purpose: str = "representation_only",
        audit_status: str = "not_audited",
        audit_contract_id: str | None = None,
        audit_findings=(),
        audit_note: str = "",
    ) -> "GrammarExemplar":
        if purpose != "representation_only":
            raise ReferenceBundleError(
                f"grammar exemplar {stage_id!r} must be representation_only, got {purpose!r}"
            )
        p=_image_path(path,label=f"grammar exemplar {stage_id}")
        if audit_status == "fail":
            raise ReferenceBundleError(
                f"grammar exemplar {stage_id!r} failed its contract audit; "
                "remove it from the manifest instead of bundling a broken reference"
            )
        if audit_status not in {"not_audited","pass"}:
            raise ReferenceBundleError(f"unknown grammar exemplar audit status: {audit_status!r}")
        return cls(
            stage_id=str(stage_id),path=p,sha256=_sha256_file(p),purpose=purpose,
            audit_status=str(audit_status),
            audit_contract_id=None if audit_contract_id is None else str(audit_contract_id),
            audit_findings=tuple(map(str,audit_findings)),
            audit_note=str(audit_note),
        )

    def to_dict(self) -> dict:
        mandatory_path_policy = (
            "unproven_until_ablation"
            if self.stage_id == "P3_primary_masses"
            else "mandatory_positive_reference"
        )
        return {
            "role":"grammar_exemplar",
            "stage_id":self.stage_id,
            "path":str(self.path),
            "sha256":self.sha256,
            "purpose":self.purpose,
            "authority":self.authority,
            "audit_status":self.audit_status,
            "audit_contract_id":self.audit_contract_id,
            "audit_findings":list(self.audit_findings),
            "audit_note":self.audit_note,
            "mandatory_path_policy":mandatory_path_policy,
            "decides":[
                "stage abstraction vocabulary",
                "stroke economy",
                "line hierarchy",
                "detail budget",
                "construction convention",
            ],
            "must_not_decide":[
                "subject pose",
                "subject coordinates",
                "subject-specific proportions",
                "subject-specific perspective",
            ],
        }


@dataclass(frozen=True)
class StageReferenceView:
    stage_id: str
    subject: SubjectReference
    grammar_exemplar: GrammarExemplar | None
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
            "grammar_exemplar":None if self.grammar_exemplar is None else self.grammar_exemplar.to_dict(),
            "subject_only_rule":(
                None if self.task_stage_target is not None else
                "Derive stage geometry from the subject and verified prior drawing; grammar exemplar is representation-only."
            ),
        }


@dataclass(frozen=True)
class ReferenceBundle:
    subject: SubjectReference
    grammar_exemplars: dict[str, GrammarExemplar]
    task_stage_targets: dict[str, TaskStageTarget]

    def __post_init__(self):
        for stage_id, item in self.grammar_exemplars.items():
            if stage_id != item.stage_id:
                raise ReferenceBundleError(
                    f"grammar exemplar key/stage mismatch: {stage_id!r} != {item.stage_id!r}"
                )
        for stage_id, item in self.task_stage_targets.items():
            if stage_id != item.stage_id:
                raise ReferenceBundleError(
                    f"task target key/stage mismatch: {stage_id!r} != {item.stage_id!r}"
                )

    def for_stage(self, stage_id: str) -> StageReferenceView:
        grammar=self.grammar_exemplars.get(stage_id)
        task=self.task_stage_targets.get(stage_id)
        order=tuple(
            part for part in ("task_stage_target","subject_reference","grammar_exemplar")
            if (part != "task_stage_target" or task is not None)
            and (part != "grammar_exemplar" or grammar is not None)
        )
        return StageReferenceView(
            stage_id=stage_id,
            subject=self.subject,
            grammar_exemplar=grammar,
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
                    "grammar_exemplar",
                ],
                "without_task_stage_target":[
                    "subject_reference",
                    "grammar_exemplar",
                ],
                "notes":[
                    "Task stage targets are strongest only when they belong to the same task/subject.",
                    "Subject reference remains geometry truth and resolves contradictions about pose/proportion/perspective.",
                    "Grammar exemplars are representation-only and must never donate pose or coordinates.",
                ],
            },
            "subject_reference":self.subject.to_dict(),
            "task_stage_targets":{
                k:v.to_dict() for k,v in sorted(self.task_stage_targets.items())
            },
            "grammar_exemplars":{
                k:v.to_dict() for k,v in sorted(self.grammar_exemplars.items())
            },
        }
