from __future__ import annotations

"""Visual closure records for resolved form and optional identity work.

The P3 fidelity records deliberately stop at occupied volume.  This module adds
the next two review boundaries without teaching the runtime to infer anatomy or
to score a raster.  All findings remain authored by an independent evaluator;
the runtime only checks identity, freshness, budgets, and provenance bindings.
"""

from dataclasses import dataclass, replace as dataclass_replace
import hashlib
import json
import re
from pathlib import Path
from typing import Any, Mapping, Sequence

from ..core.session import sha256_obj


P4_RESOLVED_REGIONS = (
    "head_hair_connection",
    "face_opening",
    "torso_garment_hang",
    "near_arm_joint_chain",
    "far_arm_joint_chain",
    "waist_leg_openings",
    "footwear_connection",
    "attached_object_structure",
)
P5_RESOLVED_REGIONS = (
    "face_feature_scaffold",
    "hair_silhouette_grouping",
    "garment_contour_and_folds",
    "joint_contour_continuity",
    "hands_and_footwear",
    "prop_final_topology",
    "contour_ownership",
    "construction_retirement_and_line_hierarchy",
)
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_DECISIONS = frozenset({"closed", "revise", "accept-with-rationale"})
_REVIEW_DECISIONS = frozenset({"revise", "advance"})


def _digest(value: str, *, label: str) -> str:
    value = str(value).lower()
    if not _SHA256.fullmatch(value):
        raise ValueError(f"{label} must be a 64-character lowercase hex digest")
    return value


def _strings(value: Sequence[Any] | None) -> tuple[str, ...]:
    return tuple(item for item in (str(v).strip() for v in (value or ())) if item)


def _relative_refs(value: Sequence[Any] | None) -> tuple[str, ...]:
    refs = _strings(value)
    for ref in refs:
        if ref.startswith("/") or re.match(r"^[A-Za-z]:[\\/]", ref):
            raise ValueError("resolved-form evidence refs must be checkout-relative")
        if any(part == ".." for part in Path(ref).parts):
            raise ValueError("resolved-form evidence refs cannot traverse outside the artifact root")
    return refs


@dataclass(frozen=True)
class ResolvedFormEntry:
    """One fresh subject-vs-drawing finding for a P4 or P5 region."""

    region_id: str
    subject_finding: str
    drawing_finding: str
    evidence_refs: tuple[str, ...]
    decision: str
    blocker: bool = False
    rationale: str = ""
    rationale_basis: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        region = str(self.region_id).strip()
        if not region:
            raise ValueError("resolved-form region_id must be non-empty")
        if not str(self.subject_finding).strip() or not str(self.drawing_finding).strip():
            raise ValueError(f"resolved-form region {region!r} requires subject and drawing findings")
        refs = _relative_refs(self.evidence_refs)
        if not refs:
            raise ValueError(f"resolved-form region {region!r} requires evidence_refs")
        decision = str(self.decision).strip()
        if decision not in _DECISIONS:
            raise ValueError(f"decision must be one of {sorted(_DECISIONS)}")
        basis = _strings(self.rationale_basis)
        if decision == "accept-with-rationale":
            if not str(self.rationale).strip():
                raise ValueError("accept-with-rationale requires rationale")
            if not {"uncertainty", "occlusion"}.intersection(basis):
                raise ValueError("accept-with-rationale requires uncertainty or occlusion basis")
        object.__setattr__(self, "region_id", region)
        object.__setattr__(self, "subject_finding", str(self.subject_finding).strip())
        object.__setattr__(self, "drawing_finding", str(self.drawing_finding).strip())
        object.__setattr__(self, "evidence_refs", refs)
        object.__setattr__(self, "decision", decision)
        object.__setattr__(self, "blocker", bool(self.blocker))
        object.__setattr__(self, "rationale", str(self.rationale).strip())
        object.__setattr__(self, "rationale_basis", basis)

    @property
    def blocks_advance(self) -> bool:
        return bool(self.blocker or self.decision == "revise")

    def to_dict(self) -> dict[str, Any]:
        return {
            "region_id": self.region_id,
            "subject_finding": self.subject_finding,
            "drawing_finding": self.drawing_finding,
            "evidence_refs": list(self.evidence_refs),
            "decision": self.decision,
            "blocker": self.blocker,
            "rationale": self.rationale,
            "rationale_basis": list(self.rationale_basis),
        }

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "ResolvedFormEntry":
        return cls(
            region_id=str(raw["region_id"]),
            subject_finding=str(raw["subject_finding"]),
            drawing_finding=str(raw["drawing_finding"]),
            evidence_refs=tuple(raw.get("evidence_refs", ())),
            decision=str(raw["decision"]),
            blocker=bool(raw.get("blocker", False)),
            rationale=str(raw.get("rationale", "")),
            rationale_basis=tuple(raw.get("rationale_basis", ())),
        )


@dataclass(frozen=True)
class ResolvedFormManifest:
    """Artifact-bound P4/P5 region closure, separate from process review."""

    stage: str
    drawing_state_sha256: str
    drawing_artifact_sha256: str
    history_cursor: int
    observation_lock_digest: str
    regions: tuple[ResolvedFormEntry, ...]
    evaluator_id: str
    blind_packet_digest: str
    manifest_id: str = ""

    def __post_init__(self) -> None:
        stage = str(self.stage)
        if stage not in {"P4_structural_connections", "P5_clean_blockin"}:
            raise ValueError("resolved-form manifests are defined for P4 or P5")
        expected = set(P4_RESOLVED_REGIONS if stage.startswith("P4") else P5_RESOLVED_REGIONS)
        regions = tuple(
            item if isinstance(item, ResolvedFormEntry) else ResolvedFormEntry.from_dict(item)
            for item in self.regions
        )
        ids = [item.region_id for item in regions]
        if set(ids) != expected or len(ids) != len(expected):
            raise ValueError(
                f"{stage} resolved-form manifest must contain exactly eight regions; "
                f"missing={sorted(expected - set(ids))}, extra={sorted(set(ids) - expected)}"
            )
        if len(ids) != len(set(ids)):
            raise ValueError("resolved-form manifest cannot contain duplicate regions")
        if int(self.history_cursor) < 0:
            raise ValueError("history_cursor must be >= 0")
        evaluator = str(self.evaluator_id).strip()
        if not evaluator:
            raise ValueError("resolved-form manifest requires evaluator_id")
        object.__setattr__(self, "stage", stage)
        object.__setattr__(self, "drawing_state_sha256", _digest(self.drawing_state_sha256, label="drawing_state_sha256"))
        object.__setattr__(self, "drawing_artifact_sha256", _digest(self.drawing_artifact_sha256, label="drawing_artifact_sha256"))
        object.__setattr__(self, "observation_lock_digest", _digest(self.observation_lock_digest, label="observation_lock_digest"))
        object.__setattr__(self, "blind_packet_digest", _digest(self.blind_packet_digest, label="blind_packet_digest"))
        object.__setattr__(self, "history_cursor", int(self.history_cursor))
        object.__setattr__(self, "regions", regions)
        object.__setattr__(self, "evaluator_id", evaluator)
        object.__setattr__(self, "manifest_id", str(self.manifest_id).strip() or f"resolved_{sha256_obj([r.to_dict() for r in regions])[:12]}")

    @property
    def blockers(self) -> tuple[str, ...]:
        return tuple(region.region_id for region in self.regions if region.blocks_advance)

    @property
    def can_advance(self) -> bool:
        return not self.blockers

    def digest(self) -> str:
        return sha256_obj(self.to_dict())

    def save(self, path: str | Path) -> Path:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(self.to_dict(), indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")
        return target

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "img2drawing.resolved_form_manifest.v1",
            "stage": self.stage,
            "drawing_state_sha256": self.drawing_state_sha256,
            "drawing_artifact_sha256": self.drawing_artifact_sha256,
            "history_cursor": self.history_cursor,
            "observation_lock_digest": self.observation_lock_digest,
            "regions": [region.to_dict() for region in self.regions],
            "evaluator_id": self.evaluator_id,
            "blind_packet_digest": self.blind_packet_digest,
            "manifest_id": self.manifest_id,
            "blockers": list(self.blockers),
        }

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "ResolvedFormManifest":
        if raw.get("schema") not in (None, "img2drawing.resolved_form_manifest.v1"):
            raise ValueError(f"unsupported resolved-form manifest schema: {raw.get('schema')!r}")
        return cls(
            stage=str(raw["stage"]),
            drawing_state_sha256=str(raw["drawing_state_sha256"]),
            drawing_artifact_sha256=str(raw["drawing_artifact_sha256"]),
            history_cursor=int(raw["history_cursor"]),
            observation_lock_digest=str(raw["observation_lock_digest"]),
            regions=tuple(ResolvedFormEntry.from_dict(item) for item in raw["regions"]),
            evaluator_id=str(raw["evaluator_id"]),
            blind_packet_digest=str(raw["blind_packet_digest"]),
            manifest_id=str(raw.get("manifest_id", "")),
        )

def build_resolved_form_blind_packet(
    *,
    stage: str,
    observation_lock_digest: str,
    subject_reference_path: str,
    drawing_artifact: Mapping[str, Any],
    stage_contract: Mapping[str, Any],
    evidence_refs: Sequence[str] = (),
) -> dict[str, Any]:
    """Build a rationale-free P4/P5 packet for an independent evaluator."""

    if stage not in {"P4_structural_connections", "P5_clean_blockin"}:
        raise ValueError("resolved-form blind packet is defined for P4 or P5")
    packet = {
        "schema": "img2drawing.resolved_form_blind_packet.v1",
        "stage": stage,
        "subject_reference_path": str(subject_reference_path),
        "observation_lock_digest": _digest(observation_lock_digest, label="observation_lock_digest"),
        "drawing_artifact": dict(drawing_artifact),
        "stage_contract": dict(stage_contract),
        "evidence_refs": list(_relative_refs(evidence_refs)),
        "hidden_from_evaluator": ["worker_rationale", "previous_review_findings", "previous_advance_claim"],
        "evaluator_instruction": "Inspect subject and current drawing independently before reading any process rationale or prior verdict.",
    }
    packet["packet_digest"] = sha256_obj(packet)
    return packet


@dataclass(frozen=True)
class ResolvedFormReviewRecord:
    stage: str
    manifest_digest: str
    drawing_state_sha256: str
    drawing_artifact_sha256: str
    history_cursor: int
    observation_lock_digest: str
    evaluator_id: str
    decision: str
    findings: tuple[str, ...]
    rationale: str
    blind_packet_digest: str

    def __post_init__(self) -> None:
        if self.stage not in {"P4_structural_connections", "P5_clean_blockin"}:
            raise ValueError("resolved-form review is defined for P4 or P5")
        for value, label in (
            (self.manifest_digest, "manifest_digest"),
            (self.drawing_state_sha256, "drawing_state_sha256"),
            (self.drawing_artifact_sha256, "drawing_artifact_sha256"),
            (self.observation_lock_digest, "observation_lock_digest"),
            (self.blind_packet_digest, "blind_packet_digest"),
        ):
            _digest(value, label=label)
        if int(self.history_cursor) < 0:
            raise ValueError("history_cursor must be >= 0")
        if not str(self.evaluator_id).strip():
            raise ValueError("resolved-form review requires evaluator_id")
        decision = str(self.decision)
        if decision not in _REVIEW_DECISIONS:
            raise ValueError(f"decision must be one of {sorted(_REVIEW_DECISIONS)}")
        findings = _strings(self.findings)
        if not findings:
            raise ValueError("resolved-form review requires findings")
        if decision == "advance" and not str(self.rationale).strip():
            raise ValueError("resolved-form advance requires rationale")
        object.__setattr__(self, "stage", str(self.stage))
        object.__setattr__(self, "manifest_digest", str(self.manifest_digest).lower())
        object.__setattr__(self, "drawing_state_sha256", str(self.drawing_state_sha256).lower())
        object.__setattr__(self, "drawing_artifact_sha256", str(self.drawing_artifact_sha256).lower())
        object.__setattr__(self, "observation_lock_digest", str(self.observation_lock_digest).lower())
        object.__setattr__(self, "blind_packet_digest", str(self.blind_packet_digest).lower())
        object.__setattr__(self, "history_cursor", int(self.history_cursor))
        object.__setattr__(self, "evaluator_id", str(self.evaluator_id).strip())
        object.__setattr__(self, "decision", decision)
        object.__setattr__(self, "findings", findings)
        object.__setattr__(self, "rationale", str(self.rationale).strip())

    def digest(self) -> str:
        return sha256_obj(self.to_dict())

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "img2drawing.resolved_form_review.v1",
            "stage": self.stage,
            "manifest_digest": self.manifest_digest,
            "drawing_state_sha256": self.drawing_state_sha256,
            "drawing_artifact_sha256": self.drawing_artifact_sha256,
            "history_cursor": self.history_cursor,
            "observation_lock_digest": self.observation_lock_digest,
            "evaluator_id": self.evaluator_id,
            "decision": self.decision,
            "findings": list(self.findings),
            "rationale": self.rationale,
            "blind_packet_digest": self.blind_packet_digest,
        }

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "ResolvedFormReviewRecord":
        if raw.get("schema") != "img2drawing.resolved_form_review.v1":
            raise ValueError(f"unsupported resolved-form review schema: {raw.get('schema')!r}")
        return cls(
            stage=str(raw["stage"]),
            manifest_digest=str(raw["manifest_digest"]),
            drawing_state_sha256=str(raw["drawing_state_sha256"]),
            drawing_artifact_sha256=str(raw["drawing_artifact_sha256"]),
            history_cursor=int(raw["history_cursor"]),
            observation_lock_digest=str(raw["observation_lock_digest"]),
            evaluator_id=str(raw["evaluator_id"]),
            decision=str(raw["decision"]),
            findings=tuple(raw.get("findings", ())),
            rationale=str(raw.get("rationale", "")),
            blind_packet_digest=str(raw["blind_packet_digest"]),
        )

    def save(self, path: str | Path) -> Path:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(self.to_dict(), indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")
        return target


@dataclass(frozen=True)
class ConstructionRetirementRecord:
    """History-preserving P5 handoff from construction to selected contour."""

    retired_stroke_ids: tuple[str, ...]
    retained_ghost_stroke_ids: tuple[str, ...]
    contour_stroke_ids: tuple[str, ...]
    reason: str
    history_cursor: int

    def __post_init__(self) -> None:
        retired = _strings(self.retired_stroke_ids)
        ghosts = _strings(self.retained_ghost_stroke_ids)
        contours = _strings(self.contour_stroke_ids)
        if not retired:
            raise ValueError("construction retirement requires at least one retired stroke")
        if set(retired) & set(ghosts):
            raise ValueError("a stroke cannot be both retired and retained as a ghost")
        if not contours:
            raise ValueError("construction retirement requires contour ownership")
        if not str(self.reason).strip():
            raise ValueError("construction retirement requires a reason")
        if int(self.history_cursor) < 0:
            raise ValueError("history_cursor must be >= 0")
        object.__setattr__(self, "retired_stroke_ids", retired)
        object.__setattr__(self, "retained_ghost_stroke_ids", ghosts)
        object.__setattr__(self, "contour_stroke_ids", contours)
        object.__setattr__(self, "reason", str(self.reason).strip())
        object.__setattr__(self, "history_cursor", int(self.history_cursor))

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "img2drawing.construction_retirement.v1",
            "retired_stroke_ids": list(self.retired_stroke_ids),
            "retained_ghost_stroke_ids": list(self.retained_ghost_stroke_ids),
            "contour_stroke_ids": list(self.contour_stroke_ids),
            "retired_count": len(self.retired_stroke_ids),
            "reason": self.reason,
            "history_cursor": self.history_cursor,
        }

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "ConstructionRetirementRecord":
        if raw.get("schema") != "img2drawing.construction_retirement.v1":
            raise ValueError(f"unsupported construction retirement schema: {raw.get('schema')!r}")
        return cls(
            retired_stroke_ids=tuple(raw.get("retired_stroke_ids", ())),
            retained_ghost_stroke_ids=tuple(raw.get("retained_ghost_stroke_ids", ())),
            contour_stroke_ids=tuple(raw.get("contour_stroke_ids", ())),
            reason=str(raw["reason"]),
            history_cursor=int(raw["history_cursor"]),
        )


@dataclass(frozen=True)
class IdentityFinishProfile:
    """Bounded optional P6 policy translated to the current pencil API."""

    profile_id: str = "p6_selective_identity_v1"
    max_identity_strokes: int = 48
    max_confirmation_strokes: int = 12
    max_accent_fraction: float = 0.25
    max_micro_fold_strokes: int = 8
    require_calibration: bool = True
    allowed_roles: tuple[str, ...] = ("identity", "form", "accent", "fold", "restatement")

    def __post_init__(self) -> None:
        if not str(self.profile_id).strip():
            raise ValueError("identity profile_id must be non-empty")
        if int(self.max_identity_strokes) < 1 or int(self.max_confirmation_strokes) < 0:
            raise ValueError("identity stroke budgets must be non-negative")
        if not 0.0 < float(self.max_accent_fraction) <= 1.0:
            raise ValueError("max_accent_fraction must be in (0,1]")
        if int(self.max_micro_fold_strokes) < 0:
            raise ValueError("max_micro_fold_strokes must be >= 0")
        roles = _strings(self.allowed_roles)
        if not roles:
            raise ValueError("identity profile requires allowed roles")
        object.__setattr__(self, "profile_id", str(self.profile_id).strip())
        object.__setattr__(self, "max_identity_strokes", int(self.max_identity_strokes))
        object.__setattr__(self, "max_confirmation_strokes", int(self.max_confirmation_strokes))
        object.__setattr__(self, "max_accent_fraction", float(self.max_accent_fraction))
        object.__setattr__(self, "max_micro_fold_strokes", int(self.max_micro_fold_strokes))
        object.__setattr__(self, "allowed_roles", roles)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "img2drawing.identity_finish_profile.v1",
            "profile_id": self.profile_id,
            "max_identity_strokes": self.max_identity_strokes,
            "max_confirmation_strokes": self.max_confirmation_strokes,
            "max_accent_fraction": self.max_accent_fraction,
            "max_micro_fold_strokes": self.max_micro_fold_strokes,
            "require_calibration": self.require_calibration,
            "allowed_roles": list(self.allowed_roles),
        }

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "IdentityFinishProfile":
        if raw.get("schema") not in (None, "img2drawing.identity_finish_profile.v1"):
            raise ValueError(f"unsupported identity profile schema: {raw.get('schema')!r}")
        return cls(
            profile_id=str(raw.get("profile_id", "p6_selective_identity_v1")),
            max_identity_strokes=int(raw.get("max_identity_strokes", 48)),
            max_confirmation_strokes=int(raw.get("max_confirmation_strokes", 12)),
            max_accent_fraction=float(raw.get("max_accent_fraction", 0.25)),
            max_micro_fold_strokes=int(raw.get("max_micro_fold_strokes", 8)),
            require_calibration=bool(raw.get("require_calibration", True)),
            allowed_roles=tuple(raw.get("allowed_roles", ("identity", "form", "accent", "fold", "restatement"))),
        )


@dataclass(frozen=True)
class CalibrationSheet:
    """Serializable pressure/curve calibration evidence for the actual canvas."""

    canvas_size: tuple[int, int]
    samples: tuple[Mapping[str, Any], ...]
    selected_profile: str
    rationale: str
    artifact_sha256: str | None = None
    artifact_50pct_sha256: str | None = None
    artifact_size: tuple[int, int] | None = None
    artifact_50pct_size: tuple[int, int] | None = None

    def __post_init__(self) -> None:
        width, height = map(int, self.canvas_size)
        if width <= 0 or height <= 0:
            raise ValueError("calibration canvas_size must be positive")
        samples = tuple(dict(sample) for sample in self.samples)
        if len(samples) < 5:
            raise ValueError("calibration sheet requires at least five pressure samples")
        if not str(self.selected_profile).strip() or not str(self.rationale).strip():
            raise ValueError("calibration sheet requires selected_profile and rationale")
        for sample in samples:
            pressure = float(sample.get("pressure", -1))
            if not 0.0 <= pressure <= 1.0:
                raise ValueError("calibration pressure must be in [0,1]")
            points = sample.get("points") or []
            if len(points) < 2:
                raise ValueError("each calibration sample needs a curve with at least two points")
        for value, label in (
            (self.artifact_sha256, "artifact_sha256"),
            (self.artifact_50pct_sha256, "artifact_50pct_sha256"),
        ):
            if value is not None:
                _digest(value, label=label)
        for value, label in (
            (self.artifact_size, "artifact_size"),
            (self.artifact_50pct_size, "artifact_50pct_size"),
        ):
            if value is not None:
                if len(value) != 2 or int(value[0]) <= 0 or int(value[1]) <= 0:
                    raise ValueError(f"{label} must contain positive width and height")
        object.__setattr__(self, "canvas_size", (width, height))
        object.__setattr__(self, "samples", samples)
        object.__setattr__(self, "selected_profile", str(self.selected_profile).strip())
        object.__setattr__(self, "rationale", str(self.rationale).strip())
        object.__setattr__(self, "artifact_sha256", None if self.artifact_sha256 is None else str(self.artifact_sha256).lower())
        object.__setattr__(self, "artifact_50pct_sha256", None if self.artifact_50pct_sha256 is None else str(self.artifact_50pct_sha256).lower())
        object.__setattr__(self, "artifact_size", None if self.artifact_size is None else (int(self.artifact_size[0]), int(self.artifact_size[1])))
        object.__setattr__(self, "artifact_50pct_size", None if self.artifact_50pct_size is None else (int(self.artifact_50pct_size[0]), int(self.artifact_50pct_size[1])))

    @classmethod
    def default(cls, width: int, height: int, *, selected_profile: str = "pencil-contact-v9") -> "CalibrationSheet":
        width, height = int(width), int(height)
        x0, x1 = width * 0.10, width * 0.90
        y0 = height * 0.10
        row = max(18.0, height * 0.075)
        curves = ("straight", "c_curve", "s_curve", "taper_in", "taper_out")
        pressures = (0.24, 0.40, 0.56, 0.72, 0.88)
        samples = []
        for index, (pressure, curve) in enumerate(zip(pressures, curves)):
            yy = y0 + index * row
            if curve == "straight":
                points = [[x0, yy], [width * 0.50, yy], [x1, yy]]
            elif curve == "c_curve":
                points = [[x0, yy], [width * 0.34, yy - row * 0.55], [width * 0.65, yy - row * 0.55], [x1, yy]]
            elif curve == "s_curve":
                points = [[x0, yy], [width * 0.34, yy - row * 0.55], [width * 0.66, yy + row * 0.55], [x1, yy]]
            elif curve == "taper_in":
                points = [[x0, yy], [width * 0.34, yy - row * 0.25], [width * 0.66, yy], [x1, yy + row * 0.10]]
            else:
                points = [[x0, yy + row * 0.10], [width * 0.34, yy], [width * 0.66, yy - row * 0.25], [x1, yy]]
            samples.append({
                "sample_id": f"{curve}_{index + 1:02d}",
                "curve": curve,
                "pressure": pressure,
                "role": ("construction", "construction", "form", "form", "accent")[index],
                "points": points,
                "taper": {"start": 0.20 + pressure * 0.25, "peak": pressure, "end": 0.16 + pressure * 0.18},
            })
        return cls(
            canvas_size=(width, height),
            samples=tuple(samples),
            selected_profile=selected_profile,
            rationale="Profile pending inspection of the rendered actual-size and 50%-scale calibration artifacts.",
        )

    def render_artifacts(self, directory: str | Path, *, supersample: int = 3) -> "CalibrationSheet":
        """Render calibration samples at actual size and 50% scale, then bind hashes.

        Calibration is guidance evidence, not drawing geometry.  The samples are
        rendered through the same pencil-contact path as review artifacts so a
        worker can inspect the material at the scale it will actually use.
        """
        from PIL import Image
        from ..core.ir import Stroke, StrokeIR
        from ..render.pillow_pencil_contact import render as render_pencil

        out = Path(directory)
        out.mkdir(parents=True, exist_ok=True)
        ir = StrokeIR(self.canvas_size[0], self.canvas_size[1], metadata={"calibration": True})
        grades = {"construction": "2H", "form": "HB", "accent": "B"}
        for sample in self.samples:
            role = str(sample.get("role", "form"))
            pressure = float(sample["pressure"])
            points = [tuple(map(float, point)) for point in sample["points"]]
            taper = sample.get("taper") or {}
            count = len(points)
            pressures = [
                float(taper.get("start", pressure * 0.55))
                + (float(taper.get("peak", pressure)) - float(taper.get("start", pressure * 0.55))) * (i / max(1, count - 1))
                for i in range(count)
            ]
            if count > 1:
                end = float(taper.get("end", pressure * 0.45))
                pressures = [
                    (p if i < count - 1 else end)
                    for i, p in enumerate(pressures)
                ]
            ir.add(Stroke(
                points=points,
                width={"construction": 1.2, "form": 1.5, "accent": 1.8}.get(role, 1.5),
                opacity={"construction": 0.42, "form": 0.58, "accent": 0.72}.get(role, 0.58),
                role=role,
                pressure=pressures,
                tool_state={"pencil_grade": grades.get(role, "HB"), "taper_in": 0.6, "taper_out": 0.6},
                part=str(sample.get("sample_id", "calibration")),
                stage="calibration",
                stroke_id=str(sample.get("sample_id", "calibration")),
            ))
        actual = out / "calibration_sheet.png"
        half = out / "calibration_sheet_50pct.png"
        render_pencil(ir, actual, supersample=max(2, int(supersample)))
        with Image.open(actual) as image:
            resized = image.resize((max(1, image.width // 2), max(1, image.height // 2)), Image.Resampling.LANCZOS)
            resized.save(half)

        def digest(path: Path) -> str:
            h = hashlib.sha256()
            with path.open("rb") as handle:
                for block in iter(lambda: handle.read(1 << 20), b""):
                    h.update(block)
            return h.hexdigest()

        with Image.open(actual) as image:
            actual_size = tuple(image.size)
        with Image.open(half) as image:
            half_size = tuple(image.size)
        return dataclass_replace(
            self,
            artifact_sha256=digest(actual),
            artifact_50pct_sha256=digest(half),
            artifact_size=actual_size,
            artifact_50pct_size=half_size,
        )

    def digest(self) -> str:
        return sha256_obj(self._payload())

    def _payload(self) -> dict[str, Any]:
        payload = {
            "schema": "img2drawing.calibration_sheet.v1",
            "canvas_size": list(self.canvas_size),
            "samples": [dict(sample) for sample in self.samples],
            "selected_profile": self.selected_profile,
            "rationale": self.rationale,
        }
        # Preserve the digest of pre-hardening v1 JSON when no rendered artifact
        # binding exists; newly rendered sheets include the binding fields.
        if self.artifact_sha256 is not None:
            payload["artifact_sha256"] = self.artifact_sha256
        if self.artifact_50pct_sha256 is not None:
            payload["artifact_50pct_sha256"] = self.artifact_50pct_sha256
        if self.artifact_size is not None:
            payload["artifact_size"] = list(self.artifact_size)
        if self.artifact_50pct_size is not None:
            payload["artifact_50pct_size"] = list(self.artifact_50pct_size)
        return payload

    def to_dict(self) -> dict[str, Any]:
        payload = self._payload()
        payload["digest"] = self.digest()
        return payload

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "CalibrationSheet":
        if raw.get("schema") != "img2drawing.calibration_sheet.v1":
            raise ValueError(f"unsupported calibration sheet schema: {raw.get('schema')!r}")
        sheet = cls(
            canvas_size=tuple(raw["canvas_size"]),
            samples=tuple(raw["samples"]),
            selected_profile=str(raw["selected_profile"]),
            rationale=str(raw["rationale"]),
            artifact_sha256=raw.get("artifact_sha256"),
            artifact_50pct_sha256=raw.get("artifact_50pct_sha256"),
            artifact_size=None if raw.get("artifact_size") is None else tuple(raw["artifact_size"]),
            artifact_50pct_size=None if raw.get("artifact_50pct_size") is None else tuple(raw["artifact_50pct_size"]),
        )
        if raw.get("digest") and str(raw["digest"]) != sheet.digest():
            raise ValueError("calibration sheet digest mismatch")
        return sheet

    def save(self, path: str | Path) -> Path:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(self.to_dict(), indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")
        return target


@dataclass(frozen=True)
class IdentityPreflightResult:
    allowed: bool
    blockers: tuple[str, ...]
    required_reopens: tuple[str, ...]
    profile_id: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "img2drawing.identity_preflight.v1",
            "allowed": self.allowed,
            "blockers": list(self.blockers),
            "required_reopens": list(self.required_reopens),
            "profile_id": self.profile_id,
        }

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "IdentityPreflightResult":
        if raw.get("schema") not in (None, "img2drawing.identity_preflight.v1"):
            raise ValueError(f"unsupported identity preflight schema: {raw.get('schema')!r}")
        return cls(
            allowed=bool(raw["allowed"]),
            blockers=tuple(raw.get("blockers", ())),
            required_reopens=tuple(raw.get("required_reopens", ())),
            profile_id=str(raw["profile_id"]),
        )


def preflight_identity_finish(
    upstream_decisions: Mapping[str, Any],
    *,
    profile: IdentityFinishProfile | None = None,
) -> IdentityPreflightResult:
    """Fail closed when any P1–P5 structural responsibility is unresolved."""

    profile = profile or IdentityFinishProfile()
    blockers: list[str] = []
    reopens: list[str] = []
    for stage, raw in upstream_decisions.items():
        decision = raw.get("decision") if isinstance(raw, Mapping) else raw
        if str(decision) != "advance":
            blockers.append(f"{stage}: decision={decision!r}")
            if str(stage).startswith("P"):
                reopens.append(str(stage))
        stage_blockers = raw.get("blockers", ()) if isinstance(raw, Mapping) else ()
        for blocker in _strings(stage_blockers):
            blockers.append(f"{stage}: blocker={blocker}")
            if str(stage) not in reopens:
                reopens.append(str(stage))
    return IdentityPreflightResult(
        allowed=not blockers,
        blockers=tuple(blockers),
        required_reopens=tuple(reopens),
        profile_id=profile.profile_id,
    )


@dataclass(frozen=True)
class IdentityFinishManifest:
    """Bounded P6 visual record; it never promotes detail into geometry truth."""

    drawing_state_sha256: str
    drawing_artifact_sha256: str
    history_cursor: int
    observation_lock_digest: str
    profile: IdentityFinishProfile
    calibration_sheet_digest: str
    face_relation: str
    hair_group_count: int
    garment_mark_count: int
    identity_stroke_count: int
    confirmation_stroke_count: int
    accent_stroke_count: int
    fold_stroke_count: int
    evidence_refs: tuple[str, ...]
    evaluator_id: str
    decision: str = "revise"
    rationale: str = ""

    def __post_init__(self) -> None:
        for value, label in (
            (self.drawing_state_sha256, "drawing_state_sha256"),
            (self.drawing_artifact_sha256, "drawing_artifact_sha256"),
            (self.observation_lock_digest, "observation_lock_digest"),
            (self.calibration_sheet_digest, "calibration_sheet_digest"),
        ):
            _digest(value, label=label)
        if int(self.history_cursor) < 0:
            raise ValueError("history_cursor must be >= 0")
        if not isinstance(self.profile, IdentityFinishProfile):
            raise TypeError("profile must be IdentityFinishProfile")
        if not str(self.face_relation).strip():
            raise ValueError("identity manifest requires face_relation")
        for value, label in (
            (self.hair_group_count, "hair_group_count"),
            (self.garment_mark_count, "garment_mark_count"),
            (self.identity_stroke_count, "identity_stroke_count"),
            (self.confirmation_stroke_count, "confirmation_stroke_count"),
            (self.accent_stroke_count, "accent_stroke_count"),
            (self.fold_stroke_count, "fold_stroke_count"),
        ):
            if int(value) < 0:
                raise ValueError(f"{label} must be >= 0")
        if int(self.identity_stroke_count) > self.profile.max_identity_strokes:
            raise ValueError("identity stroke budget exceeded")
        if int(self.confirmation_stroke_count) > self.profile.max_confirmation_strokes:
            raise ValueError("confirmation stroke budget exceeded; blanket restatement is forbidden")
        if int(self.fold_stroke_count) > self.profile.max_micro_fold_strokes:
            raise ValueError("micro-fold stroke budget exceeded")
        if int(self.accent_stroke_count) > max(1, int(self.identity_stroke_count * self.profile.max_accent_fraction)):
            raise ValueError("accent fraction exceeds selective-restatement budget")
        refs = _relative_refs(self.evidence_refs)
        if not refs:
            raise ValueError("identity manifest requires evidence refs")
        if str(self.evaluator_id).strip() == "":
            raise ValueError("identity manifest requires evaluator_id")
        decision = str(self.decision)
        if decision not in _REVIEW_DECISIONS:
            raise ValueError(f"decision must be one of {sorted(_REVIEW_DECISIONS)}")
        if decision == "advance" and not str(self.rationale).strip():
            raise ValueError("identity advance requires rationale")
        object.__setattr__(self, "drawing_state_sha256", str(self.drawing_state_sha256).lower())
        object.__setattr__(self, "drawing_artifact_sha256", str(self.drawing_artifact_sha256).lower())
        object.__setattr__(self, "observation_lock_digest", str(self.observation_lock_digest).lower())
        object.__setattr__(self, "calibration_sheet_digest", str(self.calibration_sheet_digest).lower())
        object.__setattr__(self, "history_cursor", int(self.history_cursor))
        object.__setattr__(self, "evidence_refs", refs)
        object.__setattr__(self, "evaluator_id", str(self.evaluator_id).strip())
        object.__setattr__(self, "decision", decision)
        object.__setattr__(self, "rationale", str(self.rationale).strip())

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "img2drawing.identity_finish_manifest.v1",
            "drawing_state_sha256": self.drawing_state_sha256,
            "drawing_artifact_sha256": self.drawing_artifact_sha256,
            "history_cursor": self.history_cursor,
            "observation_lock_digest": self.observation_lock_digest,
            "profile": self.profile.to_dict(),
            "calibration_sheet_digest": self.calibration_sheet_digest,
            "face_relation": self.face_relation,
            "hair_group_count": int(self.hair_group_count),
            "garment_mark_count": int(self.garment_mark_count),
            "identity_stroke_count": int(self.identity_stroke_count),
            "confirmation_stroke_count": int(self.confirmation_stroke_count),
            "accent_stroke_count": int(self.accent_stroke_count),
            "fold_stroke_count": int(self.fold_stroke_count),
            "evidence_refs": list(self.evidence_refs),
            "evaluator_id": self.evaluator_id,
            "decision": self.decision,
            "rationale": self.rationale,
        }

    @classmethod
    def from_dict(cls, raw: Mapping[str, Any]) -> "IdentityFinishManifest":
        if raw.get("schema") != "img2drawing.identity_finish_manifest.v1":
            raise ValueError(f"unsupported identity manifest schema: {raw.get('schema')!r}")
        return cls(
            drawing_state_sha256=str(raw["drawing_state_sha256"]),
            drawing_artifact_sha256=str(raw["drawing_artifact_sha256"]),
            history_cursor=int(raw["history_cursor"]),
            observation_lock_digest=str(raw["observation_lock_digest"]),
            profile=IdentityFinishProfile.from_dict(raw["profile"]),
            calibration_sheet_digest=str(raw["calibration_sheet_digest"]),
            face_relation=str(raw["face_relation"]),
            hair_group_count=int(raw["hair_group_count"]),
            garment_mark_count=int(raw["garment_mark_count"]),
            identity_stroke_count=int(raw["identity_stroke_count"]),
            confirmation_stroke_count=int(raw["confirmation_stroke_count"]),
            accent_stroke_count=int(raw["accent_stroke_count"]),
            fold_stroke_count=int(raw["fold_stroke_count"]),
            evidence_refs=tuple(raw.get("evidence_refs", ())),
            evaluator_id=str(raw["evaluator_id"]),
            decision=str(raw.get("decision", "revise")),
            rationale=str(raw.get("rationale", "")),
        )

    def digest(self) -> str:
        return sha256_obj(self.to_dict())

    def save(self, path: str | Path) -> Path:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(self.to_dict(), indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")
        return target


__all__ = [
    "P4_RESOLVED_REGIONS", "P5_RESOLVED_REGIONS", "ResolvedFormEntry",
    "ResolvedFormManifest", "ResolvedFormReviewRecord", "ConstructionRetirementRecord",
    "IdentityFinishProfile", "CalibrationSheet", "IdentityPreflightResult",
    "preflight_identity_finish", "IdentityFinishManifest", "build_resolved_form_blind_packet",
]
