from __future__ import annotations
from ..core.action import AgentDrawingSession, DrawingAction

class CanvasEditor:
    def __init__(self, session: AgentDrawingSession):
        self.session=session
    def apply(self, action: DrawingAction|dict):
        return self.session.execute(action)
    def apply_many(self, actions):
        return self.session.execute_many_atomic(actions,label="canvas-edit")
