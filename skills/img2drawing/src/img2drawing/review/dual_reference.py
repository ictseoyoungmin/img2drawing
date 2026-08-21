"""Backward-compatible facade for 0.5.1 dual-reference callers.

New code should use `reference_review.ReferenceReviewArtifacts` and
`DrawingRun.references`.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path

from .artifact import DrawingArtifact
from .comparison import side_by_side, split_compare, three_way

@dataclass(frozen=True)
class DualReferenceReviewArtifacts:
    stage: str
    drawing: DrawingArtifact
    subject_reference: Path
    stage_exemplar: Path
    subject_vs_drawing: Path
    subject_split: Path
    exemplar_vs_drawing: Path
    three_way: Path

    def to_dict(self):
        return {
            "stage":self.stage,
            "drawing":self.drawing.to_dict(),
            "subject_reference":str(self.subject_reference),
            "stage_exemplar":str(self.stage_exemplar),
            "subject_vs_drawing":str(self.subject_vs_drawing),
            "subject_split":str(self.subject_split),
            "exemplar_vs_drawing":str(self.exemplar_vs_drawing),
            "three_way":str(self.three_way),
        }

def build_dual_reference_review(*, stage: str, drawing: DrawingArtifact, subject_reference: str|Path, stage_exemplar: str|Path, out_dir: str|Path):
    out=Path(out_dir); out.mkdir(parents=True,exist_ok=True)
    subject=Path(subject_reference); exemplar=Path(stage_exemplar)
    return DualReferenceReviewArtifacts(
        stage=stage, drawing=drawing, subject_reference=subject, stage_exemplar=exemplar,
        subject_vs_drawing=side_by_side(subject,drawing.path,out/"subject_vs_drawing.png",left_label="SUBJECT",right_label="DRAWING"),
        subject_split=split_compare(subject,drawing.path,out/"subject_split.png"),
        exemplar_vs_drawing=side_by_side(exemplar,drawing.path,out/"exemplar_vs_drawing.png",left_label="STAGE EXEMPLAR",right_label="DRAWING"),
        three_way=three_way(subject,exemplar,drawing.path,out/"three_way.png"),
    )
