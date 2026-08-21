from __future__ import annotations
from pathlib import Path
from ..core.history import CanvasHistory
from ..render.pillow_pencil_contact import render

class CanvasRuntime:
    def __init__(self, history: CanvasHistory):
        self.history=history
    def sync(self, history: CanvasHistory):
        self.history=history
    def render(self, path: str|Path, *, supersample: int=3) -> Path:
        p=Path(path); p.parent.mkdir(parents=True,exist_ok=True)
        render(self.history.state_at(),p,supersample=supersample)
        return p
