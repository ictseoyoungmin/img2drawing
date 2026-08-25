from __future__ import annotations

import json
import os
import shutil
from dataclasses import dataclass, replace as dataclass_replace
from copy import deepcopy
from importlib import resources
from pathlib import Path
from typing import Any, Iterable, Mapping

from PIL import Image

from .canvas import CanvasEditor, CanvasInspector, CanvasRuntime
from .core.action import AgentDrawingSession, DrawingAction
from .core.session import sha256_obj, strokeir_canonical_dict
from .provenance.timelapse import export_timelapse, select_cursors
from .reference import ReferenceBundle, build_reference_bundle
from .render.pillow_pencil_contact import RENDERER_ID, render as render_pencil
from .render.scale_guidance import canvas_scale_guidance
from .observation import ObservationContract, FrozenObservationRecord, ObservationReopenRecord
from .review.artifact import DrawingArtifact, sha256_file
from .review.correction import assert_review_artifact_current, assert_review_current, assert_local_review_current
from .review.record import StageReviewRecord, record_from_artifacts, normalize_findings
from .review.reference_review import ReferenceReviewArtifacts, build_reference_review
from .review.local_review import LocalReviewArtifacts, build_local_review, make_local_review_id
from .review.worker_protocol import build_worker_packet
from .review.fidelity import (
    RegionClosureManifest, VisualFidelityReviewRecord,
    build_blind_visual_packet,
)
from .review.pass_memory import ActionMemory, build_stage_pass_memory, make_action_memory
from .review.reopen import ReopenRecord
from .exemplar.ablation import consume_grammar_card as build_grammar_card_consumption
from .stages import StageProgress, get_stage_registry, get_stage_contract_registry
from ._version import __version__, RELEASE_REVISION, RELEASE_SLICE, PUBLIC_API, DEFAULT_SESSION_ID


def _normalize_grammar_cards(cards):
    """Normalize stage-scoped grammar cards for runtime provenance binding.

    Cards are deliberately treated as representation guidance, not geometry.
    The runtime only records which audited card was active for a stage so a
    condition cannot claim card usage from metadata written after the drawing.
    """
    if cards is None:
        return ()
    normalized = []
    seen_ids = set()
    seen_stages = set()
    for raw in cards:
        if hasattr(raw, "to_dict"):
            raw = raw.to_dict()
        if not isinstance(raw, Mapping):
            raise TypeError("grammar_cards entries must be mappings or expose to_dict()")
        card = {
            "schema": str(raw.get("schema", "img2drawing.modular_grammar_card.v1")),
            "card_id": str(raw.get("card_id", "")).strip(),
            "stage": str(raw.get("stage", "")).strip(),
            "polarity": str(raw.get("polarity", "")).strip(),
            "scope": [str(item).strip() for item in raw.get("scope", ()) if str(item).strip()],
            "transfer_mapping": [
                str(item).strip() for item in raw.get("transfer_mapping", ()) if str(item).strip()
            ],
            "source_audit_status": str(raw.get("source_audit_status", "not_audited")).strip(),
        }
        if not card["card_id"] or not card["stage"]:
            raise ValueError("grammar card requires card_id and stage")
        if card["card_id"] in seen_ids:
            raise ValueError(f"duplicate grammar card id: {card['card_id']}")
        if card["stage"] in seen_stages:
            raise ValueError(f"multiple grammar cards bound to stage: {card['stage']}")
        if card["polarity"] not in {"positive", "negative"}:
            raise ValueError("grammar card polarity must be positive or negative")
        if card["polarity"] == "positive" and card["source_audit_status"] == "fail":
            raise ValueError("FAIL exemplar cannot become a positive grammar card")
        if not card["scope"] or not card["transfer_mapping"]:
            raise ValueError("grammar card requires scope and transfer_mapping")
        card["digest"] = sha256_obj(card)
        normalized.append(card)
        seen_ids.add(card["card_id"])
        seen_stages.add(card["stage"])
    return tuple(normalized)


@dataclass(frozen=True)
class DrawingRunResult:
    final_drawing: Path
    session: Path
    timelapse_gif: Path | None
    review_manifest: Path
    final_subject_compare: Path
    timelapse_manifest: Path | None = None
    timelapse_status: str = "unknown"


class DrawingRun:
    """Current img2drawing public orchestration authority.

    DrawingRun orchestrates. ReferenceBundle owns reference-role separation.
    Stage specs guide. Reviews preserve agent judgement.

    No semantic boolean gate is allowed to decide whether a pose is correct.
    """

    def __init__(
        self,
        *,
        reference_path,
        output_dir,
        session_id,
        width,
        height,
        stage_registry="full_body_croquis",
        grammar_exemplar_dir=None,
        exemplar_dir=None,
        grammar_cards=None,
        require_grammar_card_bindings=False,
        task_stage_targets: Mapping[str, str | Path] | None = None,
        stage_targets: Mapping[str, str | Path] | None = None,
        working_supersample=3,
    ):
        self.reference_path=Path(reference_path).resolve()
        if not self.reference_path.exists():
            raise FileNotFoundError(self.reference_path)

        if task_stage_targets is not None and stage_targets is not None:
            raise ValueError(
                "use either task_stage_targets or stage_targets alias, not both"
            )
        if task_stage_targets is None:
            task_stage_targets=stage_targets

        if grammar_exemplar_dir is not None and exemplar_dir is not None:
            raise ValueError(
                "use either grammar_exemplar_dir or legacy exemplar_dir, not both"
            )
        if grammar_exemplar_dir is None:
            grammar_exemplar_dir=exemplar_dir
        if grammar_exemplar_dir is None:
            grammar_exemplar_dir=resources.files("img2drawing.data").joinpath(
                "exemplars/full_body_croquis"
            )

        self.output_dir=Path(output_dir).resolve()
        self.output_dir.mkdir(parents=True,exist_ok=True)
        self.session_id=str(session_id)

        self.stage_registry_name=str(stage_registry)
        self.stage_specs=tuple(get_stage_registry(stage_registry))
        self.stage_contracts=get_stage_contract_registry(stage_registry)
        self.stage_by_id={s.stage_id:s for s in self.stage_specs}
        self.progress=StageProgress(tuple(s.stage_id for s in self.stage_specs))
        self.working_supersample=max(2,int(working_supersample))

        self.grammar_exemplar_dir=Path(str(grammar_exemplar_dir)).resolve()
        # 0.5.1 compatibility
        self.exemplar_dir=self.grammar_exemplar_dir
        self.grammar_cards=_normalize_grammar_cards(grammar_cards)
        self._grammar_cards_by_stage={card["stage"]: card for card in self.grammar_cards}
        self.require_grammar_card_bindings=bool(require_grammar_card_bindings)
        if self.require_grammar_card_bindings:
            expected_stages={spec.stage_id for spec in self.stage_specs}
            actual_stages=set(self._grammar_cards_by_stage)
            if actual_stages != expected_stages:
                missing=sorted(expected_stages-actual_stages)
                extra=sorted(actual_stages-expected_stages)
                raise ValueError(
                    "strict grammar-card binding requires exactly one card per stage; "
                    f"missing={missing}, extra={extra}"
                )

        self.references: ReferenceBundle=build_reference_bundle(
            subject_reference=self.reference_path,
            stage_ids=tuple(s.stage_id for s in self.stage_specs),
            grammar_exemplar_dir=self.grammar_exemplar_dir,
            task_stage_targets=task_stage_targets,
        )
        # Compatibility surface for callers that inspect the manifest.
        self.exemplar_manifest=json.loads(
            (self.grammar_exemplar_dir/"manifest.json").read_text(encoding="utf-8")
        )

        self.session=AgentDrawingSession(
            int(width),
            int(height),
            metadata={
                "public_api":PUBLIC_API,
                "reference_path":str(self.reference_path),
                "reference_bundle":self.references.to_dict(),
                "grammar_cards":[dict(card) for card in self.grammar_cards],
                "require_grammar_card_bindings":self.require_grammar_card_bindings,
            },
        )
        self.canvas=CanvasRuntime(self.session.history)
        self.inspector=CanvasInspector(self.canvas)
        self.editor=CanvasEditor(self.session)

        self._prepared: dict[str,ReferenceReviewArtifacts]={}
        self._prepared_memory={}
        self._reviews: dict[str,list[StageReviewRecord]]={}
        self._local_reviews: dict[str,LocalReviewArtifacts]={}
        self._action_events=[]
        self._reopens: list[ReopenRecord]=[]
        self._reopen_contexts: dict[str,dict[str,Any]]={}
        self._observation_lock: FrozenObservationRecord | None = None
        self._observation_reopens: list[ObservationReopenRecord] = []
        self._region_closure_manifests: dict[str, RegionClosureManifest] = {}
        self._visual_fidelity_reviews: dict[str, VisualFidelityReviewRecord] = {}
        self._blind_packets: dict[str, dict[str, Any]] = {}

    @classmethod
    def create(
        cls,
        reference,
        output_dir,
        *,
        session_id=DEFAULT_SESSION_ID,
        width=None,
        height=None,
        **kwargs,
    ):
        with Image.open(reference) as im:
            rw,rh=im.size
        return cls(
            reference_path=reference,
            output_dir=output_dir,
            session_id=session_id,
            width=rw if width is None else width,
            height=rh if height is None else height,
            **kwargs,
        )

    @property
    def current_stage(self):
        return self.progress.current_stage

    def stage_spec(self,stage=None):
        sid=stage or self.current_stage
        if sid is None:
            return None
        return self.stage_by_id[sid]

    def stage_references(self,stage=None):
        sid=stage or self.current_stage
        if sid is None:
            return None
        return self.references.for_stage(sid)

    def grammar_card_for_stage(self, stage=None):
        """Return a detached bound grammar card for a stage, if any.

        The detached mapping is safe for a worker to annotate or pass to
        :func:`img2drawing.consume_grammar_card`; mutating it cannot alter the
        run's provenance contract.  This lookup never changes the drawing.
        """
        sid = stage or self.current_stage
        if sid is None:
            return None
        if sid not in self.stage_by_id:
            raise KeyError(f"unknown stage: {sid!r}")
        card = self._grammar_cards_by_stage.get(sid)
        return None if card is None else deepcopy(card)

    def consume_grammar_card(self, stage=None, *, part=None, role=None):
        """Build explicit stroke-plan guidance for a bound stage card.

        Consumption is opt-in: this returns ordered transfer tokens and does
        not author, alter, or transform any geometry.  A caller must continue
        to derive points from the frozen subject observation.
        """
        card = self.grammar_card_for_stage(stage)
        if card is None:
            sid = stage or self.current_stage
            raise RuntimeError(f"no grammar card is bound to stage {sid!r}")
        return build_grammar_card_consumption(card, part=part, role=role)

    def stage_contract(self,stage=None):
        sid=stage or self.current_stage
        if sid is None:
            return None
        return self.stage_contracts.for_stage(sid)

    def stage_start(self,stage: str):
        self._require_observation_lock()
        self.progress.require_current(stage)
        self.progress.mark_started(stage,self.session.history.cursor)
        self.session.history.marker(
            f"stage_start:{stage}",
            stage=stage,
            provenance={"api":PUBLIC_API},
        )
        self.canvas.sync(self.session.history)
        # Durability invariant: any successful state mutation is resumable.
        self.save_checkpoint()

    def _execute_draw(self,action: DrawingAction|dict[str,Any]):
        self._require_observation_lock()
        if self.current_stage is None:
            raise RuntimeError("all stages already advanced")

        if isinstance(action,dict):
            raw=dict(action)
            raw.setdefault("stage",self.current_stage)
            normalized=DrawingAction.from_dict(raw)
        else:
            normalized=action

        if normalized.stage != self.current_stage:
            raise ValueError(
                f"drawing action belongs to {normalized.stage}, "
                f"current stage is {self.current_stage}"
            )

        card = self._grammar_cards_by_stage.get(normalized.stage)
        binding_kinds={"draw_stroke", "replace_stroke", "replace_segment"}
        if self.require_grammar_card_bindings and normalized.kind in binding_kinds and card is None:
            raise RuntimeError(f"no grammar card is bound to stage {normalized.stage!r}")
        if card is not None and normalized.kind in binding_kinds:
            metadata = dict(normalized.metadata or {})
            existing = metadata.get("grammar_card")
            if existing is not None:
                existing_id = existing.get("card_id") if isinstance(existing, Mapping) else None
                if existing_id != card["card_id"]:
                    raise ValueError(
                        f"action grammar card {existing_id!r} does not match bound stage card {card['card_id']!r}"
                    )
            existing_ids=metadata.get("grammar_card_ids")
            if existing_ids is not None and list(existing_ids) != [card["card_id"]]:
                raise ValueError(
                    f"action grammar_card_ids {existing_ids!r} do not match bound stage card {card['card_id']!r}"
                )
            metadata["grammar_card_ids"] = [card["card_id"]]
            metadata["grammar_card"] = {
                "card_id": card["card_id"],
                "stage": card["stage"],
                "digest": card["digest"],
                "scope": list(card["scope"]),
                "transfer_mapping": list(card["transfer_mapping"]),
            }
            normalized = dataclass_replace(normalized, metadata=metadata)

        result=self.session.execute(normalized)
        self.canvas.sync(self.session.history)
        self._action_events.append(
            make_action_memory(
                normalized,
                history_cursor=self.session.history.cursor,
            )
        )
        return result

    def draw(self,action: DrawingAction|dict[str,Any]):
        result=self._execute_draw(action)
        # Persist the exact authored state before control returns to the worker.
        self.save_checkpoint()
        return result

    def draw_many(self,actions: Iterable[DrawingAction|dict[str,Any]]):
        self._require_observation_lock()
        results=[self._execute_draw(a) for a in actions]
        # Batch durability without N checkpoint writes.
        self.save_checkpoint()
        return results

    def _state_sha(self):
        return sha256_obj(strokeir_canonical_dict(self.session.current_ir()))

    @property
    def observation_lock(self) -> FrozenObservationRecord | None:
        return self._observation_lock

    @property
    def observation_reopens(self) -> tuple[ObservationReopenRecord, ...]:
        return tuple(self._observation_reopens)

    def _require_observation_lock(self) -> FrozenObservationRecord:
        if self._observation_lock is None:
            raise RuntimeError(
                "pre-draw observation lock is required before stage_start or draw; "
                "call DrawingRun.lock_observation() first"
            )
        return self._observation_lock

    def _write_json_atomic(self, path: str | Path, payload: Mapping[str, Any]) -> Path:
        p=Path(path).resolve()
        p.parent.mkdir(parents=True,exist_ok=True)
        tmp=p.with_name(p.name+".tmp")
        tmp.write_text(
            json.dumps(payload,indent=2,ensure_ascii=False,sort_keys=True),
            encoding="utf-8",
        )
        os.replace(tmp,p)
        return p

    def _persist_observation_artifacts(self) -> None:
        if self._observation_lock is not None:
            self._write_json_atomic(
                self.output_dir/"observation"/"pre_draw_observation.json",
                self._observation_lock.to_dict(),
            )
        if self._observation_reopens:
            self._write_json_atomic(
                self.output_dir/"observation"/"observation_reopens.json",
                {
                    "schema":"img2drawing.observation_reopens.v1",
                    "records":[item.to_dict() for item in self._observation_reopens],
                },
            )

    def lock_observation(self, observation: ObservationContract) -> FrozenObservationRecord:
        """Freeze the agent-authored pre-draw observation for this run.

        A lock is allowed only before the first stage marker or drawing action.  A
        later correction must use ``reopen_observation`` so downstream evidence is
        audibly invalidated instead of silently changing its semantic basis.
        """
        if not isinstance(observation, ObservationContract):
            raise TypeError("lock_observation requires an ObservationContract")
        if observation.view is None:
            raise ValueError("lock_observation requires typed ViewObservation data")
        if self._observation_lock is not None:
            raise RuntimeError(
                "observation is already locked; use reopen_observation() for a replacement"
            )
        legacy_adoption = bool(
            self._reopens
            and self.current_stage == "P1_gesture"
            and "P1_gesture" not in self.progress.started_cursor
            and self._reopens[-1].target_stage == "P1_gesture"
        )
        if (self.session.history.cursor or self.progress.started_cursor) and not legacy_adoption:
            raise RuntimeError(
                "observation can only be initially locked before stage_start or draw; "
                "reopen P1 before replacing a legacy/unlocked run"
            )
        observation_id = f"{self.session_id}:observation:01"
        if legacy_adoption:
            observation_id = f"{self.session_id}:observation:legacy-adoption:01"
        record=FrozenObservationRecord.create(
            observation,
            subject_reference_sha256=self.references.subject.sha256,
            observation_id=observation_id,
            locked_at_cursor=self.session.history.cursor,
            locked_at_stage=self.current_stage or "P1_gesture",
        )
        self._observation_lock=record
        self._persist_observation_artifacts()
        self.save_checkpoint()
        return record

    def reopen_observation(
        self,
        *,
        reason: str,
        replacement: ObservationContract,
    ) -> ObservationReopenRecord:
        """Replace a frozen observation and invalidate affected drawing evidence."""
        old=self._require_observation_lock()
        reason=str(reason).strip()
        if not reason:
            raise ValueError("observation replacement requires a concrete reason")
        if not isinstance(replacement, ObservationContract):
            raise TypeError("replacement requires an ObservationContract")
        if replacement.view is None:
            raise ValueError("replacement requires typed ViewObservation data")

        source_cursor=int(self.session.history.cursor)
        stage_reopen=None
        if source_cursor or self.progress.started_cursor:
            if "P1_gesture" not in self.progress.started_cursor:
                raise RuntimeError(
                    "observation replacement requires an explicitly started P1 so "
                    "reopen_stage can invalidate the drawing branch"
                )
            stage_reopen=self.reopen_stage(
                "P1_gesture",
                reason=reason,
                discovered_in_stage=self.current_stage,
                findings=("pre-draw observation lock replaced",),
            )

        replacement_record=FrozenObservationRecord.create(
            replacement,
            subject_reference_sha256=self.references.subject.sha256,
            observation_id=f"{self.session_id}:observation:{len(self._observation_reopens)+2:02d}",
            locked_at_cursor=self.session.history.cursor,
            locked_at_stage=self.current_stage or "P1_gesture",
            replacement_of=old.observation_digest,
        )
        self._observation_lock=replacement_record
        reopen_record=ObservationReopenRecord(
            reopen_id=f"observation_reopen_{len(self._observation_reopens)+1:02d}",
            reason=reason,
            previous_observation_digest=old.observation_digest,
            replacement_observation_digest=replacement_record.observation_digest,
            source_cursor=source_cursor,
            restored_cursor=int(self.session.history.cursor),
            target_stage="P1_gesture",
            invalidated_stages=()
            if stage_reopen is None else tuple(stage_reopen.invalidated_stages),
        )
        self._observation_reopens.append(reopen_record)
        self._persist_observation_artifacts()
        self.save_checkpoint()
        return reopen_record

    @property
    def region_closure_manifest(self) -> RegionClosureManifest | None:
        return self._region_closure_manifests.get("P3_primary_masses")

    @property
    def visual_fidelity_review(self) -> VisualFidelityReviewRecord | None:
        return self._visual_fidelity_reviews.get("P3_primary_masses")

    @property
    def blind_visual_packet(self) -> dict[str, Any] | None:
        packet = self._blind_packets.get("P3_primary_masses")
        return None if packet is None else dict(packet)

    def _require_current_p3_artifacts(self):
        if self.current_stage != "P3_primary_masses":
            raise RuntimeError("visual fidelity closure is only available at P3_primary_masses")
        artifacts = self._prepared.get("P3_primary_masses")
        if artifacts is None:
            raise RuntimeError("prepare_stage_review() must be called before visual fidelity review")
        assert_review_artifact_current(
            artifacts,
            current_state_sha256=self._state_sha(),
            current_cursor=self.session.history.cursor,
        )
        return artifacts

    def submit_region_closure_manifest(
        self,
        manifest: RegionClosureManifest,
    ) -> RegionClosureManifest:
        """Persist the eight-region visual evidence manifest for the current P3 pass."""
        artifacts = self._require_current_p3_artifacts()
        if not isinstance(manifest, RegionClosureManifest):
            raise TypeError("submit_region_closure_manifest requires RegionClosureManifest")
        lock = self._require_observation_lock()
        if manifest.drawing_state_sha256 != artifacts.drawing.state_sha256:
            raise RuntimeError("region closure manifest is stale for the current drawing state")
        if manifest.drawing_artifact_sha256 != artifacts.drawing.artifact_sha256:
            raise RuntimeError("region closure manifest is stale for the current drawing artifact")
        if manifest.history_cursor != artifacts.drawing.history_cursor:
            raise RuntimeError("region closure manifest is stale for the current history cursor")
        if manifest.observation_lock_digest != lock.observation_digest:
            raise RuntimeError("region closure manifest is bound to a different observation lock")
        self._region_closure_manifests["P3_primary_masses"] = manifest
        pass_dir = artifacts.drawing.path.parent
        manifest.save(pass_dir / "region_closure_manifest.json")
        packet = build_blind_visual_packet(
            observation_lock=lock,
            stage_contract=self.stage_contracts.for_stage("P3_primary_masses").to_dict(),
            drawing_artifact=artifacts.drawing.to_dict(),
            subject_reference_path=str(self.reference_path),
            region_evidence_refs=(
                ref
                for region in manifest.regions
                for ref in region.evidence_refs
            ),
        )
        (pass_dir / "blind_visual_packet.json").write_text(
            json.dumps(packet, indent=2, ensure_ascii=False, sort_keys=True),
            encoding="utf-8",
        )
        self._blind_packets["P3_primary_masses"] = packet
        self.save_checkpoint()
        return manifest

    def submit_visual_fidelity_review(
        self,
        *,
        manifest: RegionClosureManifest | None = None,
        evaluator_id: str,
        findings,
        decision: str = "revise",
        rationale: str = "",
    ) -> VisualFidelityReviewRecord:
        """Submit an independent visual decision for the current P3 pass."""
        artifacts = self._require_current_p3_artifacts()
        if manifest is None:
            manifest = self._region_closure_manifests.get("P3_primary_masses")
        if manifest is None:
            raise RuntimeError("submit a region closure manifest before visual fidelity review")
        if manifest is not self._region_closure_manifests.get("P3_primary_masses"):
            self.submit_region_closure_manifest(manifest)
        if decision == "advance" and not manifest.can_advance:
            raise RuntimeError(
                "visual fidelity cannot advance while region blockers/revise decisions remain: "
                + ", ".join(manifest.blockers)
            )
        packet = self._blind_packets.get("P3_primary_masses")
        if packet is None:
            raise RuntimeError("blind visual packet is missing; submit the manifest again")
        record = VisualFidelityReviewRecord(
            stage="P3_primary_masses",
            manifest_digest=manifest.digest(),
            drawing_state_sha256=artifacts.drawing.state_sha256,
            drawing_artifact_sha256=artifacts.drawing.artifact_sha256,
            history_cursor=artifacts.drawing.history_cursor,
            observation_lock_digest=self._require_observation_lock().observation_digest,
            evaluator_id=str(evaluator_id),
            decision=str(decision),
            findings=tuple(findings) if not isinstance(findings, str) else (findings,),
            rationale=str(rationale),
            blind_packet_digest=str(packet["packet_digest"]),
        )
        record.save(artifacts.drawing.path.parent / "visual_fidelity_review.json")
        self._visual_fidelity_reviews["P3_primary_masses"] = record
        self.save_checkpoint()
        return record

    def _stage_exemplar_path(self,stage: str) -> Path:
        """0.5.1 compatibility alias for the grammar exemplar."""
        return self.references.for_stage(stage).grammar_exemplar.path

    def _task_stage_target_path(self,stage: str) -> Path | None:
        item=self.references.for_stage(stage).task_stage_target
        return None if item is None else item.path

    def prepare_stage_review(self,stage: str|None=None) -> ReferenceReviewArtifacts:
        stage=stage or self.current_stage
        if stage is None:
            raise RuntimeError("no active stage")
        self.progress.require_current(stage)

        out=self.output_dir/"reviews"/stage/f"pass_{len(self._reviews.get(stage,[]))+1:02d}"
        out.mkdir(parents=True,exist_ok=True)
        drawing_path=out/"current_drawing.png"
        render_pencil(
            self.session.current_ir(),
            drawing_path,
            supersample=self.working_supersample,
        )
        artifact=DrawingArtifact(
            stage=stage,
            path=drawing_path,
            artifact_sha256=sha256_file(drawing_path),
            state_sha256=self._state_sha(),
            history_cursor=self.session.history.cursor,
        )
        pass_index=len(self._reviews.get(stage,[]))+1
        pass_memory=build_stage_pass_memory(
            stage=stage,
            next_pass_index=pass_index,
            reviews=self._reviews.get(stage,()),
            action_events=self._action_events,
            reopen_context=self._reopen_contexts.get(stage),
        )
        (out/"pass_memory.json").write_text(
            json.dumps(pass_memory.to_dict(),indent=2,ensure_ascii=False,sort_keys=True),
            encoding="utf-8",
        )

        stage_refs=self.references.for_stage(stage)
        stage_contract=self.stage_contracts.for_stage(stage)
        (out/"grammar_exemplar_audit.json").write_text(
            json.dumps({
                "stage_id":stage,
                "contract_id":stage_refs.grammar_exemplar.audit_contract_id,
                "status":stage_refs.grammar_exemplar.audit_status,
                "findings":list(stage_refs.grammar_exemplar.audit_findings),
                "note":stage_refs.grammar_exemplar.audit_note,
                "mandatory_path_policy":stage_refs.grammar_exemplar.to_dict().get("mandatory_path_policy"),
                "exemplar_path":str(stage_refs.grammar_exemplar.path),
                "exemplar_sha256":stage_refs.grammar_exemplar.sha256,
            },indent=2,ensure_ascii=False,sort_keys=True),
            encoding="utf-8",
        )
        (out/"stage_contract.json").write_text(
            json.dumps(stage_contract.to_dict(),indent=2,ensure_ascii=False,sort_keys=True),
            encoding="utf-8",
        )
        artifacts=build_reference_review(
            stage=stage,
            drawing=artifact,
            references=stage_refs,
            out_dir=out,
        )
        (out/"artifacts.json").write_text(
            json.dumps(artifacts.to_dict(),indent=2,ensure_ascii=False),
            encoding="utf-8",
        )
        scale_guidance=canvas_scale_guidance(
            self.session.width,self.session.height,stage
        ).to_dict()
        packet=build_worker_packet(
            stage_spec=self.stage_by_id[stage],
            stage_contract=stage_contract,
            pass_memory=pass_memory,
            artifacts=artifacts,
            references=stage_refs,
            pass_index=pass_index,
            canvas_scale_guidance=scale_guidance,
            checkpoint_resume={
                "checkpoint_path":str(self.output_dir/"session"/"checkpoint.json"),
                "auto_checkpoint_after_mutation":True,
                "auto_checkpoint_after_prepare":True,
                "auto_checkpoint_after_review":True,
                "atomic_replace":True,
                "resume_method":"DrawingRun.resume",
            },
            grammar_cards=(self._grammar_cards_by_stage[stage],)
            if stage in self._grammar_cards_by_stage else (),
        )
        packet.save_json(out/"worker_packet.json")
        packet.save_markdown(out/"worker_packet.md")
        if stage == "P3_primary_masses":
            # A new pass gets a fresh blind packet and cannot reuse a prior visual
            # decision. Region evidence is added later when the manifest is submitted.
            self._region_closure_manifests.pop(stage, None)
            self._visual_fidelity_reviews.pop(stage, None)
            blind_packet = build_blind_visual_packet(
                observation_lock=self._require_observation_lock(),
                stage_contract=stage_contract.to_dict(),
                drawing_artifact=artifact.to_dict(),
                subject_reference_path=str(self.reference_path),
            )
            (out / "blind_visual_packet.json").write_text(
                json.dumps(blind_packet, indent=2, ensure_ascii=False, sort_keys=True),
                encoding="utf-8",
            )
            self._blind_packets[stage] = blind_packet
        self._prepared[stage]=artifacts
        self._prepared_memory[stage]=pass_memory
        # If prepare_stage_review() returns successfully, its drawing artifact and the
        # resumable checkpoint are guaranteed to describe the same cursor/state.
        self.save_checkpoint()
        return artifacts

    def prepare_local_review(
        self,
        *,
        label: str,
        intent: str,
        subject_box,
        drawing_box,
        grammar_box,
        task_target_box=None,
        stage: str|None=None,
    ) -> LocalReviewArtifacts:
        """Create local comparison artifacts from explicit Agent-selected boxes.

        This method performs no anatomy/landmark detection and no similarity scoring.
        The caller owns ROI selection; the runtime only validates, crops, hashes and
        lays out the selected evidence.
        """
        stage=stage or self.current_stage
        if stage is None:
            raise RuntimeError("no active stage")
        self.progress.require_current(stage)
        artifacts=self._prepared.get(stage)
        if artifacts is None:
            raise RuntimeError(
                "prepare_stage_review() must be called before prepare_local_review()"
            )
        assert_review_artifact_current(
            artifacts,
            current_state_sha256=self._state_sha(),
            current_cursor=self.session.history.cursor,
        )

        pass_dir=artifacts.drawing.path.parent
        prospective_id=make_local_review_id(stage,pass_dir.name,label)
        if prospective_id in self._local_reviews:
            raise ValueError(
                f"duplicate local review id for this pass: {prospective_id}; use a distinct label"
            )
        local=build_local_review(
            stage_review=artifacts,
            label=label,
            intent=intent,
            subject_box=subject_box,
            drawing_box=drawing_box,
            grammar_box=grammar_box,
            task_target_box=task_target_box,
            out_dir=pass_dir/"local_reviews",
        )
        self._local_reviews[local.local_review_id]=local

        same_pass=[
            item.to_dict()
            for item in self._local_reviews.values()
            if item.stage==stage and item.pass_name==pass_dir.name
        ]
        (pass_dir/"local_reviews_manifest.json").write_text(
            json.dumps({
                "schema":"img2drawing.local_review_manifest.v1",
                "stage":stage,
                "pass_name":pass_dir.name,
                "selection_authority":"agent_explicit_boxes",
                "auto_detection_used":False,
                "reviews":same_pass,
            },indent=2,ensure_ascii=False,sort_keys=True),
            encoding="utf-8",
        )
        return local

    def submit_stage_review(
        self,
        *,
        stage: str|None=None,
        contract_findings=None,
        task_target_findings=None,
        subject_findings=None,
        local_review_ids=(),
        exemplar_findings=None,
        drawing_findings=None,
        observations=None,
        corrections=(),
        remaining_concerns=(),
        decision="revise",
        advance_rationale="",
    ) -> StageReviewRecord:
        stage=stage or self.current_stage
        if stage is None:
            raise RuntimeError("no active stage")
        self.progress.require_current(stage)

        artifacts=self._prepared.get(stage)
        if artifacts is None:
            raise RuntimeError(
                "prepare_stage_review() must be called before submit_stage_review()"
            )
        pass_memory=self._prepared_memory.get(stage)
        if pass_memory is None:
            raise RuntimeError(
                "prepared stage review is missing pass memory; prepare_stage_review() again"
            )
        assert_review_artifact_current(
            artifacts,
            current_state_sha256=self._state_sha(),
            current_cursor=self.session.history.cursor,
        )

        if stage == "P3_primary_masses" and decision == "advance":
            manifest = self._region_closure_manifests.get(stage)
            visual = self._visual_fidelity_reviews.get(stage)
            if manifest is None or visual is None:
                raise RuntimeError(
                    "P3 advance requires an independent region closure manifest and visual fidelity review"
                )
            if visual.decision != "advance":
                raise RuntimeError("P3 advance requires visual fidelity decision='advance'")
            if not manifest.can_advance:
                raise RuntimeError(
                    "P3 advance is blocked by region decisions: "
                    + ", ".join(manifest.blockers)
                )
            if visual.manifest_digest != manifest.digest():
                raise RuntimeError("visual fidelity review is bound to a stale region closure manifest")
            if (
                visual.drawing_state_sha256 != artifacts.drawing.state_sha256
                or visual.drawing_artifact_sha256 != artifacts.drawing.artifact_sha256
                or visual.history_cursor != artifacts.drawing.history_cursor
                or visual.observation_lock_digest != self._require_observation_lock().observation_digest
            ):
                raise RuntimeError("visual fidelity review is stale for the current process review artifact")

        # 0.5.0/0.5.1 compatibility. This shortcut is not allowed when a
        # same-task stage target exists because that authority needs its
        # own explicit findings.
        if observations is not None:
            if artifacts.has_task_stage_target:
                raise ValueError(
                    "generic observations= is not allowed when a task stage target exists; "
                    "provide task_target_findings, subject_findings, exemplar_findings "
                    "and drawing_findings separately"
                )
            obs=normalize_findings(observations, field="observations")
            contract_findings=contract_findings or (
                "Legacy review path: current drawing was checked against the frozen stage representation contract.",
            )
            subject_findings=subject_findings or obs
            exemplar_findings=exemplar_findings or (
                "Grammar exemplar inspected; see drawing_findings for representation judgement.",
            )
            drawing_findings=drawing_findings or obs

        if artifacts.has_task_stage_target and not task_target_findings:
            raise ValueError(
                "review with a task stage target requires task_target_findings"
            )
        if not contract_findings:
            raise ValueError(
                "review requires contract_findings against the frozen stage representation contract"
            )

        local_review_ids=normalize_findings(local_review_ids, field="local_review_ids")
        if len(local_review_ids) != len(set(local_review_ids)):
            raise ValueError("local_review_ids must be unique")
        for local_id in local_review_ids:
            try:
                local=self._local_reviews[local_id]
            except KeyError as exc:
                raise ValueError(f"unknown local_review_id: {local_id}") from exc
            if local.stage != stage:
                raise ValueError(
                    f"local review {local_id!r} belongs to {local.stage}, not {stage}"
                )
            if local.pass_name != artifacts.drawing.path.parent.name:
                raise ValueError(
                    f"local review {local_id!r} belongs to {local.pass_name}, "
                    f"not current {artifacts.drawing.path.parent.name}"
                )
            if local.drawing_artifact_sha256 != artifacts.drawing.artifact_sha256:
                raise ValueError(f"local review {local_id!r} is bound to a different drawing artifact")
            assert_local_review_current(
                local,
                current_state_sha256=self._state_sha(),
                current_cursor=self.session.history.cursor,
            )

        record=record_from_artifacts(
            artifacts,
            stage_contract_id=self.stage_contracts.for_stage(stage).contract_id,
            pass_memory=pass_memory,
            contract_findings=contract_findings or (),
            task_target_findings=task_target_findings or (),
            local_review_ids=local_review_ids,
            subject_findings=subject_findings or (),
            exemplar_findings=exemplar_findings or (),
            drawing_findings=drawing_findings or (),
            corrections=corrections,
            remaining_concerns=remaining_concerns,
            decision=decision,
            advance_rationale=advance_rationale,
        )
        assert_review_current(
            record,
            current_state_sha256=self._state_sha(),
            current_cursor=self.session.history.cursor,
        )

        reviews=self._reviews.setdefault(stage,[])
        reviews.append(record)
        out=self.output_dir/"reviews"/stage/f"pass_{len(reviews):02d}"/"review.json"
        record.save(out)

        if decision=="advance":
            self.session.history.marker(
                f"stage_end:{stage}",
                stage=stage,
                provenance={"review_digest":record.digest()},
            )
            self.progress.advance(stage,record.digest())
            self._reopen_contexts.pop(stage,None)
            self.canvas.sync(self.session.history)
        self.save_checkpoint()
        return record

    def reopen_stage(
        self,
        stage: str,
        *,
        reason: str,
        discovered_in_stage: str | None = None,
        findings=(),
    ) -> ReopenRecord:
        """Rewind to the earliest responsible stage and invalidate downstream evidence.

        Reopen is a branch operation, not an in-place patch:
        - drawing history rewinds to the target stage start;
        - target/downstream active reviews and local reviews are archived;
        - downstream action-memory events are pruned from the active branch;
        - stage progress restarts at the target;
        - fresh worker packets receive explicit reopen_restart context.

        The Agent chooses the target stage and writes the reason/findings. Runtime only
        performs deterministic invalidation and provenance.
        """
        reason=str(reason).strip()
        if not reason:
            raise ValueError("reopen requires a concrete reason")
        findings=tuple(str(x).strip() for x in findings if str(x).strip())

        stage_ids=tuple(s.stage_id for s in self.stage_specs)
        if stage not in self.progress.started_cursor:
            raise ValueError(f"stage {stage!r} was never started")
        target_idx=stage_ids.index(stage)

        if discovered_in_stage is None:
            discovered_in_stage=self.current_stage
        if discovered_in_stage is not None:
            if discovered_in_stage not in stage_ids:
                raise ValueError(f"unknown discovered_in_stage: {discovered_in_stage!r}")
            if stage_ids.index(discovered_in_stage) < target_idx:
                raise ValueError(
                    "discovered_in_stage cannot precede the reopen target"
                )

        source_cursor=int(self.session.history.cursor)
        source_state_sha256=self._state_sha()
        restored_target_cursor=int(self.progress.started_cursor[stage])

        invalidated_stages=tuple(
            sid for sid in stage_ids[target_idx:]
            if (
                sid in self.progress.started_cursor
                or sid in self._reviews
                or sid in self.progress.advanced_reviews
                or sid == self.current_stage
            )
        )
        if stage not in invalidated_stages:
            invalidated_stages=(stage,)+invalidated_stages

        abandoned_review_digests={
            sid:tuple(review.digest() for review in self._reviews.get(sid,()))
            for sid in invalidated_stages
            if self._reviews.get(sid)
        }
        trigger_review_digest=None
        if discovered_in_stage is not None and self._reviews.get(discovered_in_stage):
            trigger_review_digest=self._reviews[discovered_in_stage][-1].digest()

        abandoned_local_review_ids=tuple(
            local_id
            for local_id,local in self._local_reviews.items()
            if local.stage in invalidated_stages
        )
        abandoned_action_ids=tuple(
            event.action_id
            for event in self._action_events
            if int(event.history_cursor) > restored_target_cursor
        )

        reopen_id=f"reopen_{len(self._reopens)+1:02d}"
        archive_dir=self.output_dir/"reopen_archive"/reopen_id
        archive_reviews=archive_dir/"reviews"
        archive_reviews.mkdir(parents=True,exist_ok=True)

        # Preserve the invalidated visual/review evidence before the active pass numbers reset.
        for sid in invalidated_stages:
            src=self.output_dir/"reviews"/sid
            if src.exists():
                dst=archive_reviews/sid
                if dst.exists():
                    shutil.rmtree(dst)
                shutil.move(str(src),str(dst))

        # Rewind authoritative drawing history. The marker append truncates the abandoned
        # future branch in CanvasHistory before writing the reopen provenance marker.
        self.session.history.cursor=restored_target_cursor
        self.session.history.marker(
            f"stage_reopen:{stage}",
            stage=stage,
            provenance={
                "reason":reason,
                "discovered_in_stage":discovered_in_stage,
                "findings":list(findings),
                "reopen_id":reopen_id,
            },
        )
        self.canvas.sync(self.session.history)
        restored_cursor=int(self.session.history.cursor)
        restored_state_sha256=self._state_sha()

        # Active action/review memory must describe the restored branch only.
        self._action_events=[
            event for event in self._action_events
            if int(event.history_cursor) <= restored_target_cursor
        ]
        active_action_ids=set()
        for item in self.session.history.actions[:self.session.history.cursor]:
            if item.provenance and item.provenance.get("action_id"):
                active_action_ids.add(str(item.provenance["action_id"]))
        self.session.executed_action_ids=active_action_ids

        for sid in invalidated_stages:
            self._reviews.pop(sid,None)
            self._prepared.pop(sid,None)
            self._prepared_memory.pop(sid,None)
            self._region_closure_manifests.pop(sid, None)
            self._visual_fidelity_reviews.pop(sid, None)
            self._blind_packets.pop(sid, None)
            self.progress.advanced_reviews.pop(sid,None)
            self.progress.started_cursor.pop(sid,None)
        for local_id in abandoned_local_review_ids:
            self._local_reviews.pop(local_id,None)

        self.progress.current_index=target_idx

        record=ReopenRecord(
            reopen_id=reopen_id,
            target_stage=stage,
            discovered_in_stage=discovered_in_stage,
            reason=reason,
            findings=findings,
            source_cursor=source_cursor,
            restored_cursor=restored_cursor,
            source_state_sha256=source_state_sha256,
            restored_state_sha256=restored_state_sha256,
            invalidated_stages=invalidated_stages,
            abandoned_review_digests=abandoned_review_digests,
            abandoned_local_review_ids=abandoned_local_review_ids,
            abandoned_action_ids=abandoned_action_ids,
            trigger_review_digest=trigger_review_digest,
            archive_dir=str(archive_dir),
        )
        self._reopens.append(record)
        reopen_dir=self.output_dir/"reopens"
        record.save(reopen_dir/f"{reopen_id}.json")
        (reopen_dir/"reopen_manifest.json").write_text(
            json.dumps({
                "schema":"img2drawing.reopen_manifest.v1",
                "reopens":[item.to_dict() for item in self._reopens],
            },indent=2,ensure_ascii=False,sort_keys=True),
            encoding="utf-8",
        )

        # Every invalidated stage gets a fresh-worker context. Target is the correction
        # stage; downstream stages know they must rebuild from the corrected upstream branch.
        for sid in invalidated_stages:
            self._reopen_contexts[sid]={
                "reopen_id":reopen_id,
                "role":"reopened_target" if sid==stage else "invalidated_downstream",
                "target_stage":stage,
                "stage":sid,
                "discovered_in_stage":discovered_in_stage,
                "reason":reason,
                "findings":list(findings),
                "trigger_review_digest":trigger_review_digest,
                "abandoned_review_digests":list(abandoned_review_digests.get(sid,())),
                "archive_dir":str(archive_dir),
            }

        self.canvas.sync(self.session.history)
        self.save_checkpoint()
        return record

    def _checkpoint_payload(self):
        return {
            "schema":"img2drawing.run_checkpoint.v3",
            "version":__version__,
            "slice":RELEASE_SLICE,
            "init":{
                "reference_path":str(self.reference_path),
                "reference_sha256":self.references.subject.sha256,
                "output_dir":str(self.output_dir),
                "session_id":self.session_id,
                "width":self.session.width,
                "height":self.session.height,
                "stage_registry":self.stage_registry_name,
                "grammar_exemplar_dir":str(self.grammar_exemplar_dir),
                "task_stage_targets":{
                    k:str(v.path) for k,v in self.references.task_stage_targets.items()
                },
                "grammar_cards":[dict(card) for card in self.grammar_cards],
                "require_grammar_card_bindings":self.require_grammar_card_bindings,
                "working_supersample":self.working_supersample,
            },
            "agent_session":self.session.to_dict(),
            "state_sha256":self._state_sha(),
            "progress":{
                "current_index":self.progress.current_index,
                "started_cursor":dict(self.progress.started_cursor),
                "advanced_reviews":dict(self.progress.advanced_reviews),
            },
            "reviews":{k:[r.to_dict() for r in v] for k,v in self._reviews.items()},
            "local_reviews":{k:v.to_dict() for k,v in self._local_reviews.items()},
            "action_memory_events":[x.to_dict() for x in self._action_events],
            "reopens":[x.to_dict() for x in self._reopens],
            "reopen_contexts":self._reopen_contexts,
            "observation_lock":(
                None if self._observation_lock is None else self._observation_lock.to_dict()
            ),
            "observation_reopens":[x.to_dict() for x in self._observation_reopens],
            "region_closure_manifests":{
                k:v.to_dict() for k,v in self._region_closure_manifests.items()
            },
            "visual_fidelity_reviews":{
                k:v.to_dict() for k,v in self._visual_fidelity_reviews.items()
            },
            "blind_packets":dict(self._blind_packets),
        }

    def save_checkpoint(self,path: str|Path|None=None) -> Path:
        """Atomically persist the current authoritative run state.

        A successful mutation/resume boundary is durable: checkpoint bytes are
        written and fsynced to a sibling temporary file, then atomically replaced.
        """
        p=Path(path) if path is not None else self.output_dir/"session"/"checkpoint.json"
        p=p.resolve(); p.parent.mkdir(parents=True,exist_ok=True)
        payload=json.dumps(
            self._checkpoint_payload(),indent=2,ensure_ascii=False,sort_keys=True
        )
        tmp=p.with_name(p.name+".tmp")
        with tmp.open("w",encoding="utf-8") as f:
            f.write(payload)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp,p)
        return p

    @classmethod
    def resume(
        cls,
        checkpoint_or_output_dir,
        *,
        reference=None,
        grammar_exemplar_dir=None,
        grammar_cards=None,
        require_grammar_card_bindings=None,
    ):
        """Resume a partially reviewed DrawingRun from a current-version checkpoint.

        `submit_stage_review()` writes the checkpoint automatically. Prepared review
        objects are intentionally not restored; after new edits, prepare fresh evidence.
        """
        base=Path(checkpoint_or_output_dir).expanduser().resolve()
        checkpoint=base/"session"/"checkpoint.json" if base.is_dir() else base
        data=json.loads(checkpoint.read_text(encoding="utf-8"))
        if data.get("schema") not in {
            "img2drawing.run_checkpoint.v1",
            "img2drawing.run_checkpoint.v2",
            "img2drawing.run_checkpoint.v3",
        }:
            raise ValueError(f"unsupported run checkpoint schema: {data.get('schema')!r}")
        init=data["init"]
        ref=Path(reference).expanduser().resolve() if reference is not None else Path(init["reference_path"]).expanduser().resolve()
        if not ref.exists():
            raise FileNotFoundError(
                f"checkpoint subject is unavailable: {ref}; pass reference=... to DrawingRun.resume"
            )
        if sha256_file(ref)!=str(init["reference_sha256"]):
            raise ValueError("resume reference sha256 does not match checkpoint subject")
        grammar=(
            Path(grammar_exemplar_dir).expanduser().resolve()
            if grammar_exemplar_dir is not None else Path(init["grammar_exemplar_dir"]).expanduser().resolve()
        )
        cards = grammar_cards if grammar_cards is not None else init.get("grammar_cards")
        strict_cards = (
            bool(require_grammar_card_bindings)
            if require_grammar_card_bindings is not None
            else bool(init.get("require_grammar_card_bindings", False))
        )
        targets={k:Path(v) for k,v in (init.get("task_stage_targets") or {}).items()}
        obj=cls(
            reference_path=ref, output_dir=init["output_dir"], session_id=init["session_id"],
            width=int(init["width"]), height=int(init["height"]),
            stage_registry=init.get("stage_registry","full_body_croquis"),
            grammar_exemplar_dir=grammar, task_stage_targets=targets,
            grammar_cards=cards,
            require_grammar_card_bindings=strict_cards,
            working_supersample=int(init.get("working_supersample",3)),
        )
        obj.session=AgentDrawingSession.from_dict(data["agent_session"])
        obj.canvas=CanvasRuntime(obj.session.history)
        obj.inspector=CanvasInspector(obj.canvas)
        obj.editor=CanvasEditor(obj.session)
        progress=data.get("progress") or {}
        obj.progress.current_index=int(progress.get("current_index",0))
        obj.progress.started_cursor={str(k):int(v) for k,v in (progress.get("started_cursor") or {}).items()}
        obj.progress.advanced_reviews={str(k):str(v) for k,v in (progress.get("advanced_reviews") or {}).items()}
        obj._reviews={
            str(k):[StageReviewRecord.from_dict(x) for x in v]
            for k,v in (data.get("reviews") or {}).items()
        }
        obj._local_reviews={
            str(k):LocalReviewArtifacts.from_dict(v)
            for k,v in (data.get("local_reviews") or {}).items()
        }
        obj._action_events=[ActionMemory.from_dict(x) for x in data.get("action_memory_events",())]
        obj._reopens=[ReopenRecord.from_dict(x) for x in data.get("reopens",())]
        obj._reopen_contexts={str(k):dict(v) for k,v in (data.get("reopen_contexts") or {}).items()}
        lock_data=data.get("observation_lock")
        obj._observation_lock=(
            None if lock_data is None else FrozenObservationRecord.from_dict(lock_data)
        )
        obj._observation_reopens=[
            ObservationReopenRecord.from_dict(x)
            for x in data.get("observation_reopens",())
        ]
        obj._region_closure_manifests={
            str(k): RegionClosureManifest.from_dict(v)
            for k,v in (data.get("region_closure_manifests") or {}).items()
        }
        obj._visual_fidelity_reviews={
            str(k): VisualFidelityReviewRecord.from_dict(v)
            for k,v in (data.get("visual_fidelity_reviews") or {}).items()
        }
        obj._blind_packets={
            str(k): dict(v) for k,v in (data.get("blind_packets") or {}).items()
        }
        obj._prepared={}
        obj._prepared_memory={}
        obj.canvas.sync(obj.session.history)
        if obj._state_sha()!=str(data["state_sha256"]):
            raise ValueError("resumed drawing state does not match checkpoint hash")
        return obj

    def finish(
        self,
        *,
        final_supersample=4,
        allow_incomplete=False,
        timelapse="auto",
        timelapse_mode="every_n",
        timelapse_every_n=4,
        max_timelapse_pixel_work=20_000_000,
    ) -> DrawingRunResult:
        """Persist a reliable closeout before optional expensive timelapse work.

        `timelapse="auto"` keeps the bounded export policy, but the default GIF
        samples the persisted action log every four actions. Use
        ``timelapse_mode="stage"`` for a sparse stage summary, or
        ``timelapse_mode="action"`` for every action cursor. ``timelapse="full"``
        forces export; ``timelapse="none"`` skips it.
        """
        if self.current_stage is not None and not allow_incomplete:
            raise RuntimeError(
                "cannot finish before all stages are reviewed and advanced; "
                f"current={self.current_stage}"
            )
        policy=str(timelapse).lower().strip()
        if policy not in {"auto","full","none"}:
            raise ValueError("timelapse must be 'auto', 'full', or 'none'")
        mode=str(timelapse_mode).lower().strip()
        if mode not in {"stage", "action", "every_n", "critic"}:
            raise ValueError(
                "timelapse_mode must be 'stage', 'action', 'every_n', or 'critic'"
            )
        every_n=int(timelapse_every_n)
        if every_n < 1:
            raise ValueError("timelapse_every_n must be >= 1")

        # Checkpoint first: a later optional timelapse failure must never erase the job.
        self.save_checkpoint()
        final_dir=self.output_dir/"final"
        final_dir.mkdir(parents=True,exist_ok=True)
        final_path=final_dir/"drawing.png"
        render_pencil(self.session.current_ir(),final_path,supersample=int(final_supersample))

        from .review.comparison import side_by_side
        final_compare=side_by_side(
            self.references.subject.path,final_path,
            self.output_dir/"compare"/"subject_vs_final.png",
            left_label="SUBJECT",right_label="FINAL DRAWING",
        )

        persisted=self.session.to_drawing_session(
            session_id=self.session_id,
            metadata={
                "version":__version__,
                "slice":RELEASE_SLICE,
                "reference_sha256":self.references.subject.sha256,
                "reference_bundle":self.references.to_dict(),
                "grammar_cards":[dict(card) for card in self.grammar_cards],
                "require_grammar_card_bindings":self.require_grammar_card_bindings,
                "stage_contract_registry":self.stage_contracts.to_dict(),
                "stage_reviews":{k:[r.to_dict() for r in v] for k,v in self._reviews.items()},
                "local_reviews":{k:v.to_dict() for k,v in self._local_reviews.items()},
                "action_memory_events":[x.to_dict() for x in self._action_events],
                "reopens":[x.to_dict() for x in self._reopens],
                "observation_lock":(
                    None if self._observation_lock is None else self._observation_lock.to_dict()
                ),
                "observation_reopens":[x.to_dict() for x in self._observation_reopens],
                "region_closure_manifests":{
                    k:v.to_dict() for k,v in self._region_closure_manifests.items()
                },
                "visual_fidelity_reviews":{
                    k:v.to_dict() for k,v in self._visual_fidelity_reviews.items()
                },
            },
        )
        session_dir=self.output_dir/"session"; session_dir.mkdir(parents=True,exist_ok=True)
        session_path=persisted.save(session_dir/"session.json")

        manifest=self.output_dir/"review_manifest.json"
        manifest.write_text(json.dumps({
            "schema":"img2drawing.review_manifest.v9",
            "version":__version__,
            "slice":RELEASE_SLICE,
            "reference_bundle":self.references.to_dict(),
            "grammar_cards":[dict(card) for card in self.grammar_cards],
            "require_grammar_card_bindings":self.require_grammar_card_bindings,
            "stage_contract_registry":self.stage_contracts.to_dict(),
            "progress":{"current_stage":self.current_stage,"advanced_reviews":self.progress.advanced_reviews},
            "reviews":{k:[r.to_dict() for r in v] for k,v in self._reviews.items()},
            "local_reviews":{k:v.to_dict() for k,v in self._local_reviews.items()},
            "reopens":[x.to_dict() for x in self._reopens],
            "observation_lock":(
                None if self._observation_lock is None else self._observation_lock.to_dict()
            ),
            "observation_reopens":[x.to_dict() for x in self._observation_reopens],
            "region_closure_manifests":{
                k:v.to_dict() for k,v in self._region_closure_manifests.items()
            },
            "visual_fidelity_reviews":{
                k:v.to_dict() for k,v in self._visual_fidelity_reviews.items()
            },
        },indent=2,ensure_ascii=False,sort_keys=True),encoding="utf-8")

        tl_manifest=None; tl_gif=None; tl_status="disabled"
        tl_dir=self.output_dir/"timelapse"; tl_dir.mkdir(parents=True,exist_ok=True)
        frame_ss=2
        frame_count=len(select_cursors(persisted,mode,every_n=every_n))
        pixel_work=self.session.width*self.session.height*(frame_ss**2)*frame_count
        should_export=(policy=="full") or (policy=="auto" and pixel_work<=int(max_timelapse_pixel_work))
        if should_export:
            make_gif=(policy=="full") or (self.session.width*self.session.height < 500_000)
            try:
                tl=export_timelapse(
                    session_path,tl_dir,mode=mode,every_n=every_n,gif=make_gif,
                    renderer=render_pencil,renderer_kwargs={"supersample":frame_ss},
                    final_renderer_kwargs={"supersample":int(final_supersample)},
                    renderer_id=RENDERER_ID,expected_final_path=final_path,
                )
                tl_manifest=tl.manifest_path; tl_gif=tl.gif_path
                tl_status="exported_gif" if tl.gif_path is not None else "exported_frames"
            except Exception as exc:
                if policy=="full":
                    raise
                tl_manifest=tl_dir/"manifest.json"
                tl_status="optional_export_failed"
                tl_manifest.write_text(json.dumps({
                    "schema":"img2drawing.timelapse.skip.v1",
                    "status":tl_status,
                    "policy":policy,
                    "error_type":type(exc).__name__,
                    "error":str(exc),
                    "note":"Optional timelapse failed after final drawing/session/review artifacts were safely persisted.",
                },indent=2),encoding="utf-8")
        else:
            tl_manifest=tl_dir/"manifest.json"
            tl_status="skipped_budget" if policy=="auto" else "disabled"
            tl_manifest.write_text(json.dumps({
                "schema":"img2drawing.timelapse.skip.v1",
                "status":tl_status,
                "policy":policy,
                "estimated_pixel_work":pixel_work,
                "max_timelapse_pixel_work":int(max_timelapse_pixel_work),
                "frame_count_if_exported":frame_count,
                "frame_supersample":frame_ss,
                "note":"Final drawing, compare, session, checkpoint and review manifest were persisted before optional timelapse work.",
            },indent=2),encoding="utf-8")

        return DrawingRunResult(
            final_path,session_path,tl_gif,manifest,final_compare,
            timelapse_manifest=tl_manifest,timelapse_status=tl_status,
        )
