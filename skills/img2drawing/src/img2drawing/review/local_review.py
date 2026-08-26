from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from PIL import Image

from .artifact import sha256_file
from .comparison import labeled_multi_way, side_by_side, crop_registered_overlay, crop_registered_absdiff
from .reference_review import ReferenceReviewArtifacts


class LocalReviewError(ValueError):
    """Invalid Agent-authored local-review request."""


@dataclass(frozen=True)
class CropBox:
    left: int
    top: int
    right: int
    bottom: int

    def __post_init__(self):
        values=(self.left,self.top,self.right,self.bottom)
        if any(int(v) != v for v in values):
            raise LocalReviewError(f"crop coordinates must be integers: {values!r}")
        if self.left < 0 or self.top < 0:
            raise LocalReviewError(f"crop coordinates must be non-negative: {values!r}")
        if self.right <= self.left or self.bottom <= self.top:
            raise LocalReviewError(f"crop must have positive area: {values!r}")

    @classmethod
    def coerce(cls, value: "CropBox | Iterable[int]") -> "CropBox":
        if isinstance(value,cls):
            return value
        try:
            vals=tuple(value)
        except TypeError as exc:
            raise LocalReviewError("crop box must be CropBox or 4-item iterable") from exc
        if len(vals) != 4:
            raise LocalReviewError(f"crop box requires 4 coordinates, got {len(vals)}")
        return cls(*(int(v) for v in vals))

    def validate_for_image(self, path: str | Path, *, role: str) -> tuple[int,int]:
        p=Path(path)
        with Image.open(p) as im:
            w,h=im.size
        if self.right > w or self.bottom > h:
            raise LocalReviewError(
                f"{role} crop {self.to_tuple()} exceeds image bounds {(w,h)} for {p}"
            )
        return w,h

    def to_tuple(self) -> tuple[int,int,int,int]:
        return (self.left,self.top,self.right,self.bottom)

    def to_dict(self) -> dict:
        return {
            "left":self.left,"top":self.top,
            "right":self.right,"bottom":self.bottom,
        }


@dataclass(frozen=True)
class LocalCropArtifact:
    role: str
    source_path: Path
    source_sha256: str
    source_size: tuple[int,int]
    box: CropBox
    crop_path: Path
    crop_sha256: str

    @classmethod
    def from_dict(cls,data: dict) -> "LocalCropArtifact":
        box=data["box"]
        return cls(
            role=str(data["role"]), source_path=Path(data["source_path"]),
            source_sha256=str(data["source_sha256"]), source_size=tuple(map(int,data["source_size"])),
            box=CropBox(int(box["left"]),int(box["top"]),int(box["right"]),int(box["bottom"])),
            crop_path=Path(data["crop_path"]), crop_sha256=str(data["crop_sha256"]),
        )

    def to_dict(self) -> dict:
        return {
            "role":self.role,
            "source_path":str(self.source_path),
            "source_sha256":self.source_sha256,
            "source_size":list(self.source_size),
            "box":self.box.to_dict(),
            "crop_path":str(self.crop_path),
            "crop_sha256":self.crop_sha256,
        }


@dataclass(frozen=True)
class LocalReviewArtifacts:
    local_review_id: str
    stage: str
    pass_name: str
    label: str
    intent: str
    selection_authority: str
    auto_detection_used: bool
    drawing_state_sha256: str
    drawing_artifact_sha256: str
    history_cursor: int
    subject: LocalCropArtifact
    drawing: LocalCropArtifact
    task_target: LocalCropArtifact | None
    subject_vs_drawing: Path
    task_target_vs_drawing: Path | None
    subject_drawing_overlay: Path
    subject_drawing_absdiff: Path
    overview: Path

    @classmethod
    def from_dict(cls,data: dict) -> "LocalReviewArtifacts":
        crops=data["crops"]; comps=data["comparisons"]
        return cls(
            local_review_id=str(data["local_review_id"]), stage=str(data["stage"]),
            pass_name=str(data["pass_name"]), label=str(data["label"]), intent=str(data["intent"]),
            selection_authority=str(data["selection_authority"]), auto_detection_used=bool(data["auto_detection_used"]),
            drawing_state_sha256=str(data["drawing_state_sha256"]), drawing_artifact_sha256=str(data["drawing_artifact_sha256"]),
            history_cursor=int(data["history_cursor"]),
            subject=LocalCropArtifact.from_dict(crops["subject"]), drawing=LocalCropArtifact.from_dict(crops["drawing"]),
            task_target=None if crops.get("task_target") is None else LocalCropArtifact.from_dict(crops["task_target"]),
            subject_vs_drawing=Path(comps["subject_vs_drawing"]),
            task_target_vs_drawing=None if comps.get("task_target_vs_drawing") is None else Path(comps["task_target_vs_drawing"]),
            subject_drawing_overlay=Path(comps["subject_drawing_overlay"]),
            subject_drawing_absdiff=Path(comps["subject_drawing_absdiff"]),
            overview=Path(comps["overview"]),
        )

    def to_dict(self) -> dict:
        return {
            "schema":"img2drawing.local_review_artifacts.v2",
            "local_review_id":self.local_review_id,
            "stage":self.stage,
            "pass_name":self.pass_name,
            "label":self.label,
            "intent":self.intent,
            "selection_authority":self.selection_authority,
            "auto_detection_used":self.auto_detection_used,
            "drawing_state_sha256":self.drawing_state_sha256,
            "drawing_artifact_sha256":self.drawing_artifact_sha256,
            "history_cursor":self.history_cursor,
            "crops":{
                "subject":self.subject.to_dict(),
                "drawing":self.drawing.to_dict(),
                "task_target":None if self.task_target is None else self.task_target.to_dict(),
            },
            "comparisons":{
                "subject_vs_drawing":str(self.subject_vs_drawing),
                "task_target_vs_drawing":None if self.task_target_vs_drawing is None else str(self.task_target_vs_drawing),
                "subject_drawing_overlay":str(self.subject_drawing_overlay),
                "subject_drawing_absdiff":str(self.subject_drawing_absdiff),
                "overview":str(self.overview),
            },
            "semantic_authority":"agent",
            "automation_note":"Runtime crops/layouts the exact Agent-supplied boxes and may resize those paired crops for overlay/difference evidence; it does not locate anatomy, optimize registration, score similarity, or choose ROIs.",
        }

    def save(self,path: str | Path) -> Path:
        p=Path(path); p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text(json.dumps(self.to_dict(),indent=2,ensure_ascii=False,sort_keys=True),encoding="utf-8")
        return p


def _slug(label: str) -> str:
    raw=str(label).strip()
    if not raw:
        raise LocalReviewError("local review label must be non-empty")
    slug=re.sub(r"[^A-Za-z0-9._-]+","_",raw).strip("._-")
    if not slug:
        raise LocalReviewError(f"local review label cannot be converted to a safe id: {label!r}")
    return slug[:80]


def make_local_review_id(stage: str, pass_name: str, label: str) -> str:
    return f"{str(stage)}:{str(pass_name)}:{_slug(label)}"


def _crop(*, role: str, source: str | Path, box: CropBox, out: Path) -> LocalCropArtifact:
    source=Path(source).resolve()
    size=box.validate_for_image(source,role=role)
    with Image.open(source) as im:
        crop=im.convert("RGB").crop(box.to_tuple())
    out.parent.mkdir(parents=True,exist_ok=True)
    crop.save(out)
    return LocalCropArtifact(
        role=role,
        source_path=source,
        source_sha256=sha256_file(source),
        source_size=size,
        box=box,
        crop_path=out,
        crop_sha256=sha256_file(out),
    )


def build_local_review(
    *,
    stage_review: ReferenceReviewArtifacts,
    label: str,
    intent: str,
    subject_box: CropBox | Iterable[int],
    drawing_box: CropBox | Iterable[int],
    task_target_box: CropBox | Iterable[int] | None,
    out_dir: str | Path,
) -> LocalReviewArtifacts:
    """Build exact local comparisons from Agent-specified boxes only.

    No box inference, detector, landmark model, CV heuristic, or similarity score is
    used here. Choosing *what* to inspect remains an Agent responsibility.
    """
    slug=_slug(label)
    subject_box=CropBox.coerce(subject_box)
    drawing_box=CropBox.coerce(drawing_box)

    if stage_review.task_stage_target is not None:
        if task_target_box is None:
            raise LocalReviewError(
                "task_target_box is required because this stage has a task stage target"
            )
        task_target_box=CropBox.coerce(task_target_box)
    elif task_target_box is not None:
        raise LocalReviewError(
            "task_target_box was supplied but this stage has no task stage target"
        )

    pass_dir=stage_review.drawing.path.parent
    pass_name=pass_dir.name
    local_id=make_local_review_id(stage_review.stage,pass_name,label)
    out=Path(out_dir)/slug
    crops=out/"crops"

    subject=_crop(
        role="subject_reference",
        source=stage_review.subject_reference,
        box=subject_box,
        out=crops/"subject.png",
    )
    drawing=_crop(
        role="current_drawing",
        source=stage_review.drawing.path,
        box=drawing_box,
        out=crops/"drawing.png",
    )
    task=None
    if stage_review.task_stage_target is not None:
        assert task_target_box is not None
        task=_crop(
            role="task_stage_target",
            source=stage_review.task_stage_target,
            box=task_target_box,
            out=crops/"task_target.png",
        )

    subject_vs=side_by_side(
        subject.crop_path,drawing.crop_path,out/"subject_vs_drawing.png",
        left_label=f"SUBJECT ROI / {label}",right_label="DRAWING ROI",
    )
    subject_overlay=crop_registered_overlay(
        subject.crop_path,drawing.crop_path,out/"subject_drawing_overlay.png"
    )
    subject_absdiff=crop_registered_absdiff(
        subject.crop_path,drawing.crop_path,out/"subject_drawing_absdiff.png"
    )
    task_vs=None
    items=[]
    if task is not None:
        task_vs=side_by_side(
            task.crop_path,drawing.crop_path,out/"task_target_vs_drawing.png",
            left_label=f"TASK TARGET ROI / {label}",right_label="DRAWING ROI",
        )
        items.append(("TASK TARGET ROI",task.crop_path))
    items.append(("SUBJECT ROI",subject.crop_path))
    items.append(("DRAWING ROI",drawing.crop_path))
    overview=labeled_multi_way(items,out/"local_reference_overview.png",tile_w=360,tile_h=460)

    result=LocalReviewArtifacts(
        local_review_id=local_id,
        stage=stage_review.stage,
        pass_name=pass_name,
        label=str(label),
        intent=str(intent),
        selection_authority="agent_explicit_boxes",
        auto_detection_used=False,
        drawing_state_sha256=stage_review.drawing.state_sha256,
        drawing_artifact_sha256=stage_review.drawing.artifact_sha256,
        history_cursor=stage_review.drawing.history_cursor,
        subject=subject,
        drawing=drawing,
        task_target=task,
        subject_vs_drawing=subject_vs,
        task_target_vs_drawing=task_vs,
        subject_drawing_overlay=subject_overlay,
        subject_drawing_absdiff=subject_absdiff,
        overview=overview,
    )
    result.save(out/"local_review.json")
    return result
