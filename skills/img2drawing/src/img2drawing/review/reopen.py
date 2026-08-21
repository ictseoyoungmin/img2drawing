from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .artifact import sha256_obj


@dataclass(frozen=True)
class ReopenRecord:
    reopen_id: str
    target_stage: str
    discovered_in_stage: str | None
    reason: str
    findings: tuple[str, ...]
    source_cursor: int
    restored_cursor: int
    source_state_sha256: str
    restored_state_sha256: str
    invalidated_stages: tuple[str, ...]
    abandoned_review_digests: dict[str, tuple[str, ...]]
    abandoned_local_review_ids: tuple[str, ...]
    abandoned_action_ids: tuple[str, ...]
    trigger_review_digest: str | None
    archive_dir: str

    @classmethod
    def from_dict(cls,data: dict[str,Any]) -> "ReopenRecord":
        return cls(
            reopen_id=str(data["reopen_id"]), target_stage=str(data["target_stage"]),
            discovered_in_stage=data.get("discovered_in_stage"), reason=str(data["reason"]),
            findings=tuple(map(str,data.get("findings",()))), source_cursor=int(data["source_cursor"]),
            restored_cursor=int(data["restored_cursor"]), source_state_sha256=str(data["source_state_sha256"]),
            restored_state_sha256=str(data["restored_state_sha256"]),
            invalidated_stages=tuple(map(str,data.get("invalidated_stages",()))),
            abandoned_review_digests={str(k):tuple(map(str,v)) for k,v in data.get("abandoned_review_digests",{}).items()},
            abandoned_local_review_ids=tuple(map(str,data.get("abandoned_local_review_ids",()))),
            abandoned_action_ids=tuple(map(str,data.get("abandoned_action_ids",()))),
            trigger_review_digest=data.get("trigger_review_digest"), archive_dir=str(data["archive_dir"]),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema":"img2drawing.reopen_record.v1",
            "reopen_id":self.reopen_id,
            "target_stage":self.target_stage,
            "discovered_in_stage":self.discovered_in_stage,
            "reason":self.reason,
            "findings":list(self.findings),
            "source_cursor":self.source_cursor,
            "restored_cursor":self.restored_cursor,
            "source_state_sha256":self.source_state_sha256,
            "restored_state_sha256":self.restored_state_sha256,
            "invalidated_stages":list(self.invalidated_stages),
            "abandoned_review_digests":{
                k:list(v) for k,v in self.abandoned_review_digests.items()
            },
            "abandoned_local_review_ids":list(self.abandoned_local_review_ids),
            "abandoned_action_ids":list(self.abandoned_action_ids),
            "trigger_review_digest":self.trigger_review_digest,
            "archive_dir":self.archive_dir,
            "policy":"reopen_earliest_responsible_stage",
            "semantic_authority":"agent",
        }

    def digest(self) -> str:
        return sha256_obj(self.to_dict())

    def save(self,path: str|Path) -> Path:
        p=Path(path); p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text(
            json.dumps(self.to_dict(),indent=2,ensure_ascii=False,sort_keys=True),
            encoding="utf-8",
        )
        return p
