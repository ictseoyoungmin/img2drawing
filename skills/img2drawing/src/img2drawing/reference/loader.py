from __future__ import annotations

import json
from pathlib import Path
from typing import Mapping

from ..exemplar.audit import load_exemplar_audit_registry

from .model import (
    GrammarExemplar,
    ReferenceBundle,
    ReferenceBundleError,
    SubjectReference,
    TaskStageTarget,
)


def build_reference_bundle(
    *,
    subject_reference: str | Path,
    stage_ids,
    grammar_exemplar_dir: str | Path,
    task_stage_targets: Mapping[str, str | Path] | None = None,
) -> ReferenceBundle:
    stage_ids=tuple(map(str,stage_ids))
    allowed=set(stage_ids)
    if not allowed:
        raise ReferenceBundleError("stage_ids must be non-empty")

    grammar_dir=Path(grammar_exemplar_dir).expanduser().resolve()
    manifest_path=grammar_dir/"manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(manifest_path)
    manifest=json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("purpose") != "representation_only":
        raise ReferenceBundleError("grammar exemplar manifest must be representation_only")

    declared=manifest.get("stages") or {}
    unknown=sorted(set(declared)-allowed)
    if unknown:
        raise ReferenceBundleError(
            "grammar exemplar manifest declares unknown stages: "+", ".join(unknown)
        )

    audit_by_stage={}
    audit_path=grammar_dir/str(manifest.get("audit_manifest","audit_manifest.json"))
    if audit_path.exists():
        audit_registry=load_exemplar_audit_registry(audit_path)
        audit_by_stage={r.stage_id:r for r in audit_registry.records}

    grammar={}
    contract_map=manifest.get("contracts") or {}
    for stage in stage_ids:
        if stage not in declared:
            continue
        audit=audit_by_stage.get(stage)
        if audit is not None:
            expected_contract=contract_map.get(stage)
            if expected_contract and audit.contract_id != expected_contract:
                raise ReferenceBundleError(
                    f"grammar exemplar audit contract drift for {stage}: "
                    f"{audit.contract_id!r} != {expected_contract!r}"
                )
            exemplar_path=(grammar_dir/declared[stage]).resolve()
            audit.validate_binding(
                expected_contract_id=audit.contract_id,
                expected_path=exemplar_path,
            )
            findings=tuple(f.description for f in audit.findings)
            audit_status=audit.status
            audit_contract_id=audit.contract_id
            audit_note=audit.note
        else:
            findings=()
            audit_status="not_audited"
            audit_contract_id=None
            audit_note=""
        grammar[stage]=GrammarExemplar.from_path(
            stage,
            grammar_dir/declared[stage],
            purpose=manifest.get("purpose",""),
            audit_status=audit_status,
            audit_contract_id=audit_contract_id,
            audit_findings=findings,
            audit_note=audit_note,
        )

    raw_targets=dict(task_stage_targets or {})
    unknown=sorted(set(raw_targets)-allowed)
    if unknown:
        raise ReferenceBundleError(
            "task_stage_targets contains unknown stage ids: "+", ".join(unknown)
        )

    targets={
        stage:TaskStageTarget.from_path(stage,path)
        for stage,path in raw_targets.items()
    }

    return ReferenceBundle(
        subject=SubjectReference.from_path(subject_reference),
        grammar_exemplars=grammar,
        task_stage_targets=targets,
    )
