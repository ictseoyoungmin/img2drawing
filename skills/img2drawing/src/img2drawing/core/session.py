from __future__ import annotations
import hashlib, json, platform
from copy import deepcopy
from dataclasses import dataclass
from importlib.metadata import version as pkg_version, PackageNotFoundError
from pathlib import Path
from typing import Any

from .history import CanvasHistory

SESSION_SCHEMA_VERSION="1.0"
RENDERER_ID="pillow-pencil-contact-v9"
TOOLSET_ID="atelier-core-a2"


def _pkg(name: str) -> str:
    try:
        return pkg_version(name)
    except PackageNotFoundError:
        return "unknown"


def canonical_json_bytes(obj: Any) -> bytes:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",",":"), allow_nan=False).encode("utf-8")


def sha256_obj(obj: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(obj)).hexdigest()


def sha256_file(path: str | Path) -> str:
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for chunk in iter(lambda:f.read(1<<20),b""):
            h.update(chunk)
    return h.hexdigest()


def strokeir_canonical_dict(ir) -> dict[str,Any]:
    # history_cursor belongs to edit UI state, not drawing content.
    meta={k:v for k,v in ir.metadata.items() if k!="history_cursor"}
    return {"width":ir.width,"height":ir.height,"metadata":meta,"strokes":ir.to_dict()["strokes"]}


@dataclass
class DrawingSession:
    session_id: str
    history: CanvasHistory
    metadata: dict[str,Any]
    schema_version: str=SESSION_SCHEMA_VERSION

    @classmethod
    def create(cls, session_id: str, width: int, height: int, metadata: dict|None=None) -> "DrawingSession":
        md=deepcopy(metadata or {})
        h=CanvasHistory(width,height,metadata=deepcopy(md.get("canvas_metadata",{})))
        return cls(str(session_id),h,md)


    @classmethod
    def from_agent_session(
        cls, agent_session, *, session_id: str = "img2drawing-run", metadata: dict | None = None
    ) -> "DrawingSession":
        """Bridge the direct AgentDrawingSession into persisted replay/timelapse state.

        This is the supported bridge; callers should not manually reconstruct session schemas.
        CanvasHistory remains the shared authority and is cloned through its canonical dict form.
        """
        h = CanvasHistory.from_dict(agent_session.history.to_dict())
        md = deepcopy(metadata or {})
        md.setdefault("source", "AgentDrawingSession")
        md.setdefault("canvas_metadata", deepcopy(agent_session.history.metadata))
        return cls(str(session_id), h, md)

    def state_hash(self) -> str:
        return sha256_obj(strokeir_canonical_dict(self.history.state_at()))

    def action_hash(self) -> str:
        return sha256_obj([a.to_dict() for a in self.history.actions])

    def environment(self) -> dict[str,str]:
        return {
            "python":platform.python_version(),
            "pillow":_pkg("Pillow"),
            "numpy":_pkg("numpy"),
        }

    def to_dict(self) -> dict[str,Any]:
        return {
            "schema_version":self.schema_version,
            "session_id":self.session_id,
            "renderer":{"id":RENDERER_ID,"version":"1"},
            "toolset":{"id":TOOLSET_ID,"version":"1"},
            "environment":self.environment(),
            "canvas":{"width":self.history.width,"height":self.history.height},
            "metadata":deepcopy(self.metadata),
            "cursor":self.history.cursor,
            "actions":[a.to_dict() for a in self.history.actions],
            "digests":{"action_log_sha256":self.action_hash(),"state_sha256":self.state_hash()},
        }

    def save(self, path: str|Path) -> Path:
        p=Path(path)
        p.write_text(json.dumps(self.to_dict(),indent=2,ensure_ascii=False,sort_keys=True),encoding="utf-8")
        return p

    @classmethod
    def from_dict(cls, data: dict[str,Any], *, verify: bool=True) -> "DrawingSession":
        if data.get("schema_version") != SESSION_SCHEMA_VERSION:
            raise ValueError(f"unsupported session schema: {data.get('schema_version')}")
        if verify:
            renderer=data.get("renderer",{})
            toolset=data.get("toolset",{})
            if renderer.get("id") != RENDERER_ID or str(renderer.get("version")) != "1":
                raise ValueError("renderer version mismatch")
            if toolset.get("id") != TOOLSET_ID or str(toolset.get("version")) != "1":
                raise ValueError("toolset version mismatch")
        canvas=data.get("canvas",{})
        h=CanvasHistory.from_dict({
            "width":canvas["width"],"height":canvas["height"],
            "metadata":deepcopy(data.get("metadata",{}).get("canvas_metadata",{})),
            "cursor":data.get("cursor",len(data.get("actions",[]))),
            "actions":deepcopy(data.get("actions",[])),
        })
        obj=cls(str(data["session_id"]),h,deepcopy(data.get("metadata",{})),str(data["schema_version"]))
        if verify:
            expected=data.get("digests",{})
            if expected.get("action_log_sha256") and expected["action_log_sha256"] != obj.action_hash():
                raise ValueError("action log digest mismatch")
            if expected.get("state_sha256") and expected["state_sha256"] != obj.state_hash():
                raise ValueError("state digest mismatch")
        return obj

    @classmethod
    def load(cls, path: str|Path, *, verify: bool=True) -> "DrawingSession":
        return cls.from_dict(json.loads(Path(path).read_text(encoding="utf-8")),verify=verify)
