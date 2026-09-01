"""Lazy R23 runtime compatibility and checkpoint migration.

Importing this module does not import the stage registry, review runtime, or
``DrawingRun``. Individual historical names are resolved only when requested.
The migration adapter deliberately reuses the existing R23 resume validator and
the shared action/history implementation; it does not reconstruct either.
"""

from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import asdict, dataclass
from importlib import import_module
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping


LEGACY_CHECKPOINT_SCHEMAS = (
    "img2drawing.run_checkpoint.v1",
    "img2drawing.run_checkpoint.v2",
    "img2drawing.run_checkpoint.v3",
)
LEGACY_MIGRATION_SCHEMA = "img2drawing.legacy_r23_migration.v1"

# This is the sole authority for the historical public-name mapping. The root
# package may resolve these names as deprecated shims, but never advertises them.
LEGACY_EXPORTS: Mapping[str, tuple[str, str]] = MappingProxyType({
    "DrawingRun": ("img2drawing.run", "DrawingRun"),
    "DrawingRunResult": ("img2drawing.run", "DrawingRunResult"),
    "ObservationContract": ("img2drawing.observation", "ObservationContract"),
    "ViewObservation": ("img2drawing.observation", "ViewObservation"),
    "FrozenObservationRecord": ("img2drawing.observation", "FrozenObservationRecord"),
    "ObservationReopenRecord": ("img2drawing.observation", "ObservationReopenRecord"),
    "StageSpec": ("img2drawing.stages", "StageSpec"),
    "StageContract": ("img2drawing.stages", "StageContract"),
    "StageContractRegistry": ("img2drawing.stages", "StageContractRegistry"),
    "StageContractError": ("img2drawing.stages", "StageContractError"),
    "get_stage_registry": ("img2drawing.stages", "get_stage_registry"),
    "get_stage_contract_registry": ("img2drawing.stages", "get_stage_contract_registry"),
    "SubjectReference": ("img2drawing.reference", "SubjectReference"),
    "TaskStageTarget": ("img2drawing.reference", "TaskStageTarget"),
    "StageReferenceView": ("img2drawing.reference", "StageReferenceView"),
    "ReferenceBundle": ("img2drawing.reference", "ReferenceBundle"),
    "ReferenceBundleError": ("img2drawing.reference", "ReferenceBundleError"),
    "build_reference_bundle": ("img2drawing.reference", "build_reference_bundle"),
    "ABLATION_CONDITIONS": ("img2drawing.exemplar.ablation", "ABLATION_CONDITIONS"),
    "ModularGrammarCard": ("img2drawing.exemplar.ablation", "ModularGrammarCard"),
    "consume_grammar_card": ("img2drawing.exemplar.ablation", "consume_grammar_card"),
    "AblationTrial": ("img2drawing.exemplar.ablation", "AblationTrial"),
    "ExemplarAblationReport": ("img2drawing.exemplar.ablation", "ExemplarAblationReport"),
    "run_exemplar_ablation": ("img2drawing.exemplar.ablation", "run_exemplar_ablation"),
    "CropBox": ("img2drawing.review", "CropBox"),
    "LocalReviewError": ("img2drawing.review", "LocalReviewError"),
    "LocalReviewArtifacts": ("img2drawing.review", "LocalReviewArtifacts"),
    "ActionMemory": ("img2drawing.review", "ActionMemory"),
    "StagePassMemory": ("img2drawing.review", "StagePassMemory"),
    "ReopenRecord": ("img2drawing.review", "ReopenRecord"),
    "StageReviewRecord": ("img2drawing.review", "StageReviewRecord"),
    "ReferenceReviewArtifacts": ("img2drawing.review", "ReferenceReviewArtifacts"),
    "StaleReviewError": ("img2drawing.review", "StaleReviewError"),
    "REQUIRED_P3_REGIONS": ("img2drawing.review", "REQUIRED_P3_REGIONS"),
    "RegionClosureEntry": ("img2drawing.review", "RegionClosureEntry"),
    "RegionClosureManifest": ("img2drawing.review", "RegionClosureManifest"),
    "VisualFidelityReviewRecord": ("img2drawing.review", "VisualFidelityReviewRecord"),
    "blind_observation_projection": ("img2drawing.review", "blind_observation_projection"),
    "build_blind_visual_packet": ("img2drawing.review", "build_blind_visual_packet"),
    "P4_RESOLVED_REGIONS": ("img2drawing.review", "P4_RESOLVED_REGIONS"),
    "P5_RESOLVED_REGIONS": ("img2drawing.review", "P5_RESOLVED_REGIONS"),
    "ResolvedFormEntry": ("img2drawing.review", "ResolvedFormEntry"),
    "ResolvedFormManifest": ("img2drawing.review", "ResolvedFormManifest"),
    "ResolvedFormReviewRecord": ("img2drawing.review", "ResolvedFormReviewRecord"),
    "ConstructionRetirementRecord": ("img2drawing.review", "ConstructionRetirementRecord"),
    "IdentityFinishProfile": ("img2drawing.review", "IdentityFinishProfile"),
    "CalibrationSheet": ("img2drawing.review", "CalibrationSheet"),
    "IdentityPreflightResult": ("img2drawing.review", "IdentityPreflightResult"),
    "preflight_identity_finish": ("img2drawing.review", "preflight_identity_finish"),
    "IdentityFinishManifest": ("img2drawing.review", "IdentityFinishManifest"),
    "build_resolved_form_blind_packet": ("img2drawing.review", "build_resolved_form_blind_packet"),
    "AssistiveROIProposal": ("img2drawing.review", "AssistiveROIProposal"),
    "ExcludedRegion": ("img2drawing.review", "ExcludedRegion"),
    "AcceptedResidual": ("img2drawing.review", "AcceptedResidual"),
    "AdaptiveEvidencePolicy": ("img2drawing.review", "AdaptiveEvidencePolicy"),
    "PreviewArtifact": ("img2drawing.review", "PreviewArtifact"),
    "render_preview": ("img2drawing.review", "render_preview"),
    "EnvelopeStation": ("img2drawing.registration", "EnvelopeStation"),
    "RegionEnvelopeObservation": ("img2drawing.registration", "RegionEnvelopeObservation"),
    "RegionEnvelopeIntegrityError": ("img2drawing.registration", "RegionEnvelopeIntegrityError"),
    "EnvelopeIntegrity": ("img2drawing.registration", "EnvelopeIntegrity"),
    "AxisEnvelopeEvidence": ("img2drawing.registration", "AxisEnvelopeEvidence"),
    "StationEnvelopeEvidence": ("img2drawing.registration", "StationEnvelopeEvidence"),
    "RegionGeometryComparison": ("img2drawing.registration", "RegionGeometryComparison"),
    "compare_region_envelopes": ("img2drawing.registration", "compare_region_envelopes"),
    "TorsoOrientationObservation": ("img2drawing.registration", "TorsoOrientationObservation"),
    "TorsoOrientationIntegrityError": ("img2drawing.registration", "TorsoOrientationIntegrityError"),
    "TorsoOrientationComparison": ("img2drawing.registration", "TorsoOrientationComparison"),
    "compare_torso_orientation": ("img2drawing.registration", "compare_torso_orientation"),
    "LowerBodyObservation": ("img2drawing.registration", "LowerBodyObservation"),
    "LowerBodyIntegrityError": ("img2drawing.registration", "LowerBodyIntegrityError"),
    "LowerBodyComparison": ("img2drawing.registration", "LowerBodyComparison"),
    "compare_lower_body": ("img2drawing.registration", "compare_lower_body"),
    "HeadHairObservation": ("img2drawing.registration", "HeadHairObservation"),
    "HeadHairIntegrityError": ("img2drawing.registration", "HeadHairIntegrityError"),
    "HeadHairComparison": ("img2drawing.registration", "HeadHairComparison"),
    "compare_head_hair": ("img2drawing.registration", "compare_head_hair"),
    "PropWidthChangePoint": ("img2drawing.registration", "PropWidthChangePoint"),
    "PropTerminalMass": ("img2drawing.registration", "PropTerminalMass"),
    "PropBodyOverlapPoint": ("img2drawing.registration", "PropBodyOverlapPoint"),
    "PropTopologyObservation": ("img2drawing.registration", "PropTopologyObservation"),
    "PropTopologyIntegrityError": ("img2drawing.registration", "PropTopologyIntegrityError"),
    "PropTopologyComparison": ("img2drawing.registration", "PropTopologyComparison"),
    "compare_prop_topology": ("img2drawing.registration", "compare_prop_topology"),
})


class LegacyCheckpointError(ValueError):
    """An R23 checkpoint cannot be handled without explicit caller action."""


@dataclass(frozen=True)
class LegacyCheckpointInfo:
    checkpoint: Path
    schema: str
    version: str | None
    release_slice: str | None
    session_id: str | None
    subject_name: str | None
    subject_sha256: str | None
    state_sha256: str | None
    can_resume: bool
    can_migrate: bool
    guidance: str

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["checkpoint"] = str(self.checkpoint)
        return result


def _checkpoint_path(checkpoint_or_output_dir: str | Path) -> Path:
    candidate = Path(checkpoint_or_output_dir).expanduser().resolve()
    return candidate / "session" / "checkpoint.json" if candidate.is_dir() else candidate


def _read_checkpoint(checkpoint_or_output_dir: str | Path) -> tuple[Path, dict[str, Any]]:
    checkpoint = _checkpoint_path(checkpoint_or_output_dir)
    if not checkpoint.is_file():
        raise FileNotFoundError(
            f"R23 checkpoint is unavailable: {checkpoint}; pass checkpoint.json or its run directory"
        )
    try:
        payload = json.loads(checkpoint.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise LegacyCheckpointError(f"R23 checkpoint is not readable JSON: {checkpoint}") from exc
    if not isinstance(payload, dict):
        raise LegacyCheckpointError("R23 checkpoint root must be a JSON object")
    return checkpoint, payload


def inspect_checkpoint(checkpoint_or_output_dir: str | Path) -> LegacyCheckpointInfo:
    """Classify a checkpoint without importing any R23 orchestration module."""

    checkpoint, payload = _read_checkpoint(checkpoint_or_output_dir)
    schema = str(payload.get("schema", ""))
    supported = schema in LEGACY_CHECKPOINT_SCHEMAS
    if schema.startswith("img2drawing.vnext.session"):
        guidance = "Use img2drawing.DrawingSession.resume(); this is already a vNext checkpoint."
    elif supported:
        guidance = (
            "Resume through img2drawing.legacy.r23.resume_checkpoint() or migrate once through "
            "img2drawing.legacy.r23.migrate_checkpoint()."
        )
    else:
        guidance = (
            f"Unsupported R23 checkpoint schema {schema!r}; supported schemas are "
            f"{', '.join(LEGACY_CHECKPOINT_SCHEMAS)}. Export with a supported R23 runtime first."
        )
    init = payload.get("init") if isinstance(payload.get("init"), dict) else {}
    reference = str(init.get("reference_path", "")).strip()
    return LegacyCheckpointInfo(
        checkpoint=checkpoint,
        schema=schema,
        version=None if payload.get("version") is None else str(payload["version"]),
        release_slice=None if payload.get("slice") is None else str(payload["slice"]),
        session_id=None if init.get("session_id") is None else str(init["session_id"]),
        subject_name=Path(reference).name if reference else None,
        subject_sha256=None if init.get("reference_sha256") is None else str(init["reference_sha256"]),
        state_sha256=None if payload.get("state_sha256") is None else str(payload["state_sha256"]),
        can_resume=supported,
        can_migrate=supported,
        guidance=guidance,
    )


def _require_supported(info: LegacyCheckpointInfo) -> None:
    if not info.can_resume:
        raise LegacyCheckpointError(info.guidance)


def resume_checkpoint(
    checkpoint_or_output_dir: str | Path,
    *,
    reference: str | Path | None = None,
    grammar_cards: Any = None,
    require_grammar_card_bindings: bool | None = None,
):
    """Resume a supported R23 run through the existing R23 validator."""

    info = inspect_checkpoint(checkpoint_or_output_dir)
    _require_supported(info)
    drawing_run = getattr(import_module("img2drawing.run"), "DrawingRun")
    return drawing_run.resume(
        info.checkpoint,
        reference=reference,
        grammar_cards=grammar_cards,
        require_grammar_card_bindings=require_grammar_card_bindings,
    )


def _legacy_observation_tokens(agent: Any) -> list[dict[str, Any]]:
    from ..core.session import sha256_obj

    records: list[dict[str, Any]] = []
    seen: set[str] = set()
    for action in agent.history.actions:
        provenance = action.provenance or {}
        observation_id = str(provenance.get("observation_id", "")).strip()
        if not observation_id or observation_id == "vnext-unobserved" or observation_id in seen:
            continue
        authority = {
            "kind": "legacy-provenance-token",
            "observation_id": observation_id,
            "claim": "identity continuity only; no vNext visual-authority claim",
        }
        records.append({**authority, "digest": sha256_obj(authority)})
        seen.add(observation_id)
    return records


def migrate_checkpoint(
    checkpoint_or_output_dir: str | Path,
    *,
    output_dir: str | Path,
    reference: str | Path | None = None,
):
    """Migrate R23 drawing truth into one stage-free vNext checkpoint.

    Stage progress, reviews, reopen state, and finish claims stay in the source
    checkpoint as historical evidence. Shared action/history data is cloned
    exactly, while stage labels remain inert compatibility provenance.
    """

    from ..core.action import AgentDrawingSession
    from ..core.session import sha256_file, sha256_obj
    from ..render.pillow_pencil_contact import RENDERER_ID, RENDERER_VERSION
    from ..vnext import DrawingSession, RenderProfile

    info = inspect_checkpoint(checkpoint_or_output_dir)
    _require_supported(info)
    destination = Path(output_dir).expanduser().resolve()
    target_checkpoint = destination / "session.checkpoint.json"
    if target_checkpoint.exists():
        raise FileExistsError(
            f"migration target already contains {target_checkpoint.name}; choose a new output_dir"
        )

    legacy_run = resume_checkpoint(info.checkpoint, reference=reference)
    source_agent_payload = legacy_run.session.to_dict()
    agent = AgentDrawingSession.from_dict(deepcopy(source_agent_payload))
    source_canvas_metadata = deepcopy(agent.history.metadata)
    source_action_digest = sha256_obj([action.to_dict() for action in agent.history.actions])
    source_checkpoint_digest = sha256_file(info.checkpoint)
    source_subject_hash = str(legacy_run.references.subject.sha256)

    # Canvas metadata carried R23 runtime paths and orchestration descriptors. Keep
    # their digest as provenance instead of leaking them into the canonical payload.
    agent.history.metadata = {
        "drawing_authority": "agent_actions",
        "migration_source": "r23",
        "source_canvas_metadata_sha256": sha256_obj(source_canvas_metadata),
    }
    profile = RenderProfile.canonical(agent.width, agent.height)
    migration = {
        "schema": LEGACY_MIGRATION_SCHEMA,
        "source": {
            "checkpoint_schema": info.schema,
            "checkpoint_sha256": source_checkpoint_digest,
            "version": info.version,
            "release_slice": info.release_slice,
            "session_id": legacy_run.session_id,
            "subject": {"name": legacy_run.reference_path.name, "sha256": source_subject_hash},
            "action_log_sha256": source_action_digest,
            "drawing_state_sha256": info.state_sha256,
            "renderer": {
                "status": "not-persisted-by-r23-checkpoint",
                "identity": None,
            },
        },
        "target": {
            "renderer": {
                "id": RENDERER_ID,
                "version": RENDERER_VERSION,
                "render_profile": profile.to_dict(),
            },
        },
        "excluded_orchestration": [
            "stage progress",
            "stage reviews",
            "reopen state",
            "legacy finish claims",
        ],
    }
    session = DrawingSession(
        session_id=legacy_run.session_id,
        subject=legacy_run.reference_path,
        output_dir=destination,
        agent_session=agent,
        metadata={"migration": migration},
        observations=_legacy_observation_tokens(agent),
        checkpoint_path=target_checkpoint,
        subject_sha256=source_subject_hash,
        render_profile=profile,
    )
    migration["target"]["action_log_sha256"] = source_action_digest
    migration["target"]["drawing_state_sha256"] = session.drawing_state_hash()
    session.metadata["migration"] = migration
    session.checkpoint()
    return session


def __getattr__(name: str):
    try:
        module_name, attribute = LEGACY_EXPORTS[name]
    except KeyError as exc:
        raise AttributeError(name) from exc
    value = getattr(import_module(module_name), attribute)
    globals()[name] = value
    return value


__all__ = [
    "LEGACY_CHECKPOINT_SCHEMAS",
    "LEGACY_MIGRATION_SCHEMA",
    "LegacyCheckpointError",
    "LegacyCheckpointInfo",
    "inspect_checkpoint",
    "resume_checkpoint",
    "migrate_checkpoint",
    *LEGACY_EXPORTS,
]
