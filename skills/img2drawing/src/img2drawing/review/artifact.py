from __future__ import annotations
import hashlib, json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

def sha256_file(path: str | Path) -> str:
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for block in iter(lambda:f.read(1<<20), b""):
            h.update(block)
    return h.hexdigest()

def sha256_obj(obj: Any) -> str:
    raw=json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=False,allow_nan=False).encode()
    return hashlib.sha256(raw).hexdigest()

@dataclass(frozen=True)
class DrawingArtifact:
    stage: str
    path: Path
    artifact_sha256: str
    state_sha256: str
    history_cursor: int

    def to_dict(self):
        return {
            "stage":self.stage, "path":str(self.path),
            "artifact_sha256":self.artifact_sha256,
            "state_sha256":self.state_sha256,
            "history_cursor":self.history_cursor,
        }
