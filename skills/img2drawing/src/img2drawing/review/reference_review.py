from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ..reference import StageReferenceView
from .artifact import DrawingArtifact
from .comparison import labeled_multi_way, side_by_side, split_compare, crop_registered_overlay, crop_registered_absdiff


@dataclass(frozen=True)
class ReferenceReviewArtifacts:
    stage: str
    drawing: DrawingArtifact
    subject_reference: Path
    grammar_exemplar: Path
    task_stage_target: Path | None
    authority_order: tuple[str, ...]
    subject_vs_drawing: Path
    subject_split: Path
    subject_drawing_overlay: Path
    subject_drawing_absdiff: Path
    grammar_vs_drawing: Path | None
    task_target_vs_drawing: Path | None
    task_target_split: Path | None
    overview: Path
    grammar_exemplar_policy: str = "mandatory_positive_reference"
    grammar_exemplar_warning: str | None = None

    # 0.5.1 compatibility names.
    @property
    def stage_exemplar(self) -> Path:
        return self.grammar_exemplar

    @property
    def exemplar_vs_drawing(self) -> Path | None:
        return self.grammar_vs_drawing

    @property
    def three_way(self) -> Path:
        # When a task target exists this property intentionally points at
        # the 4-way authority board; callers should prefer `overview`.
        return self.overview

    @property
    def has_task_stage_target(self) -> bool:
        return self.task_stage_target is not None

    def to_dict(self) -> dict:
        return {
            "schema":"img2drawing.reference_review_artifacts.v2",
            "stage":self.stage,
            "drawing":self.drawing.to_dict(),
            "authority_order":list(self.authority_order),
            "subject_reference":str(self.subject_reference),
            "task_stage_target":None if self.task_stage_target is None else str(self.task_stage_target),
            "grammar_exemplar":str(self.grammar_exemplar),
            # compatibility fields:
            "stage_exemplar":str(self.grammar_exemplar),
            "subject_vs_drawing":str(self.subject_vs_drawing),
            "subject_split":str(self.subject_split),
            "subject_drawing_overlay":str(self.subject_drawing_overlay),
            "subject_drawing_absdiff":str(self.subject_drawing_absdiff),
            "grammar_vs_drawing":None if self.grammar_vs_drawing is None else str(self.grammar_vs_drawing),
            "exemplar_vs_drawing":None if self.grammar_vs_drawing is None else str(self.grammar_vs_drawing),
            "task_target_vs_drawing":None if self.task_target_vs_drawing is None else str(self.task_target_vs_drawing),
            "task_target_split":None if self.task_target_split is None else str(self.task_target_split),
            "overview":str(self.overview),
            "three_way":str(self.overview),
            "grammar_exemplar_policy":self.grammar_exemplar_policy,
            "grammar_exemplar_warning":self.grammar_exemplar_warning,
        }


def build_reference_review(
    *,
    stage: str,
    drawing: DrawingArtifact,
    references: StageReferenceView,
    out_dir: str | Path,
) -> ReferenceReviewArtifacts:
    if references.stage_id != stage:
        raise ValueError(
            f"reference stage mismatch: {references.stage_id!r} != {stage!r}"
        )
    out=Path(out_dir)
    out.mkdir(parents=True,exist_ok=True)

    subject=references.subject.path
    grammar=references.grammar_exemplar.path
    task=None if references.task_stage_target is None else references.task_stage_target.path

    subject_vs=side_by_side(
        subject,drawing.path,out/"subject_vs_drawing.png",
        left_label="SUBJECT / GEOMETRY TRUTH",
        right_label="DRAWING",
    )
    subject_split=split_compare(subject,drawing.path,out/"subject_split.png")
    subject_overlay=crop_registered_overlay(subject,drawing.path,out/"subject_drawing_overlay.png")
    subject_absdiff=crop_registered_absdiff(subject,drawing.path,out/"subject_drawing_absdiff.png")
    grammar_is_fail = references.grammar_exemplar.audit_status == "fail"
    grammar_vs = None
    grammar_warning = None
    if grammar_is_fail:
        grammar_warning = (
            "FAIL exemplar excluded from the mandatory grammar_vs_drawing path; "
            "retain only as a negative/reference warning."
        )
    else:
        grammar_vs=side_by_side(
            grammar,drawing.path,out/"grammar_vs_drawing.png",
            left_label="GRAMMAR / REPRESENTATION ONLY",
            right_label="DRAWING",
        )

    task_vs=None
    task_split=None
    if task is not None:
        task_vs=side_by_side(
            task,drawing.path,out/"task_target_vs_drawing.png",
            left_label="TASK STAGE TARGET / SAME-TASK TRUTH",
            right_label="DRAWING",
        )
        task_split=split_compare(task,drawing.path,out/"task_target_split.png")
        overview=labeled_multi_way(
            [
                ("TASK TARGET / highest stage authority",task),
                ("SUBJECT / geometry truth",subject),
                *([] if grammar_is_fail else [("GRAMMAR / representation only",grammar)]),
                ("CURRENT DRAWING",drawing.path),
            ],
            out/"reference_authority_overview.png",
        )
    else:
        overview=labeled_multi_way(
            [
                ("SUBJECT / geometry truth",subject),
                *([] if grammar_is_fail else [("GRAMMAR / representation only",grammar)]),
                ("CURRENT DRAWING",drawing.path),
            ],
            out/"reference_authority_overview.png",
        )

    grammar_policy = (
        "negative_reference_warning_only" if grammar_is_fail
        else "unproven_until_ablation" if stage == "P3_primary_masses"
        else "mandatory_positive_reference"
    )
    return ReferenceReviewArtifacts(
        stage=stage,
        drawing=drawing,
        subject_reference=subject,
        grammar_exemplar=grammar,
        task_stage_target=task,
        authority_order=references.authority_order,
        subject_vs_drawing=subject_vs,
        subject_split=subject_split,
        subject_drawing_overlay=subject_overlay,
        subject_drawing_absdiff=subject_absdiff,
        grammar_vs_drawing=grammar_vs,
        task_target_vs_drawing=task_vs,
        task_target_split=task_split,
        overview=overview,
        grammar_exemplar_policy=grammar_policy,
        grammar_exemplar_warning=grammar_warning,
    )
