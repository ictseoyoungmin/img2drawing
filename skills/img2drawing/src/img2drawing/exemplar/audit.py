from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import hashlib
import json


class ExemplarAuditError(ValueError):
    pass


def sha256_file(path: str | Path) -> str:
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for block in iter(lambda:f.read(1<<20),b''):
            h.update(block)
    return h.hexdigest()


@dataclass(frozen=True)
class ExemplarAuditFinding:
    finding_id: str
    kind: str
    description: str
    contract_clause: str
    severity: str='major'

    def __post_init__(self):
        if self.kind not in {'missing_required','forbidden_present','scope_warning','quality_note'}:
            raise ExemplarAuditError(f'unknown audit finding kind: {self.kind!r}')
        if self.severity not in {'blocker','major','minor'}:
            raise ExemplarAuditError(f'unknown severity: {self.severity!r}')
        if not self.finding_id.strip() or not self.description.strip() or not self.contract_clause.strip():
            raise ExemplarAuditError('audit finding fields must be non-empty')

    def to_dict(self):
        return {
            'finding_id':self.finding_id,
            'kind':self.kind,
            'description':self.description,
            'contract_clause':self.contract_clause,
            'severity':self.severity,
        }


@dataclass(frozen=True)
class ExemplarAuditRecord:
    stage_id: str
    contract_id: str
    exemplar_path: Path
    exemplar_sha256: str
    status: str
    must_show_observed: tuple[str,...]
    may_show_observed: tuple[str,...]
    forbidden_observed: tuple[str,...]
    findings: tuple[ExemplarAuditFinding,...]
    note: str=''
    auditor: str='agent_visual_review'

    def __post_init__(self):
        if self.status not in {'pass','fail'}:
            raise ExemplarAuditError('status must be pass or fail')
        if not self.stage_id.strip() or not self.contract_id.strip():
            raise ExemplarAuditError('stage_id and contract_id are required')
        kinds={f.kind for f in self.findings}
        has_failure=('missing_required' in kinds or 'forbidden_present' in kinds)
        if self.status=='pass' and has_failure:
            raise ExemplarAuditError('PASS audit cannot contain missing_required/forbidden_present')
        if self.status=='fail' and not has_failure:
            raise ExemplarAuditError('FAIL audit requires missing_required or forbidden_present finding')

    def validate_binding(self, *, expected_contract_id: str, expected_path: str | Path):
        p=Path(expected_path).resolve()
        if self.contract_id != expected_contract_id:
            raise ExemplarAuditError(
                f'{self.stage_id}: contract drift {self.contract_id!r} != {expected_contract_id!r}'
            )
        if self.exemplar_path.resolve() != p:
            raise ExemplarAuditError(
                f'{self.stage_id}: exemplar path drift {self.exemplar_path} != {p}'
            )
        actual=sha256_file(p)
        if actual != self.exemplar_sha256:
            raise ExemplarAuditError(
                f'{self.stage_id}: exemplar hash drift {actual} != {self.exemplar_sha256}'
            )

    def to_dict(self):
        return {
            'schema':'img2drawing.exemplar_audit.v1',
            'stage_id':self.stage_id,
            'contract_id':self.contract_id,
            'exemplar_path':str(self.exemplar_path),
            'exemplar_sha256':self.exemplar_sha256,
            'status':self.status,
            'must_show_observed':list(self.must_show_observed),
            'may_show_observed':list(self.may_show_observed),
            'forbidden_observed':list(self.forbidden_observed),
            'findings':[f.to_dict() for f in self.findings],
            'note':self.note,
            'auditor':self.auditor,
            'semantic_authority':'agent',
            'automation_note':'Runtime validates binding/consistency only; audit status is Agent-authored visual judgement.',
        }


@dataclass(frozen=True)
class ExemplarAuditRegistry:
    records: tuple[ExemplarAuditRecord,...]

    def __post_init__(self):
        ids=[r.stage_id for r in self.records]
        if len(ids)!=len(set(ids)):
            raise ExemplarAuditError('duplicate stage audit record')

    def for_stage(self, stage_id: str) -> ExemplarAuditRecord:
        for r in self.records:
            if r.stage_id==stage_id:
                return r
        raise ExemplarAuditError(f'no exemplar audit for {stage_id!r}')

    @property
    def overall_status(self) -> str:
        return 'audited' if all(r.status=='pass' for r in self.records) else 'audited_with_failures'

    def to_dict(self):
        return {
            'schema':'img2drawing.exemplar_audit_registry.v1',
            'overall_status':self.overall_status,
            'records':[r.to_dict() for r in self.records],
        }


def load_exemplar_audit_registry(path: str | Path) -> ExemplarAuditRegistry:
    manifest_path=Path(path).resolve()
    payload=json.loads(manifest_path.read_text(encoding='utf-8'))
    base=manifest_path.parent
    records=[]
    for raw in payload.get('records',[]):
        records.append(ExemplarAuditRecord(
            stage_id=raw['stage_id'],
            contract_id=raw['contract_id'],
            exemplar_path=(Path(raw['exemplar_path']) if Path(raw['exemplar_path']).is_absolute() else base/Path(raw['exemplar_path'])).resolve(),
            exemplar_sha256=raw['exemplar_sha256'],
            status=raw['status'],
            must_show_observed=tuple(raw.get('must_show_observed',())),
            may_show_observed=tuple(raw.get('may_show_observed',())),
            forbidden_observed=tuple(raw.get('forbidden_observed',())),
            findings=tuple(ExemplarAuditFinding(**f) for f in raw.get('findings',())),
            note=raw.get('note',''),
            auditor=raw.get('auditor','agent_visual_review'),
        ))
    return ExemplarAuditRegistry(tuple(records))
