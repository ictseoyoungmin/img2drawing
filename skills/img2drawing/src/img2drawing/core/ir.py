from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Iterable
import json

@dataclass
class Stroke:
    points: list[tuple[float, float]]
    width: float = 1.5
    opacity: float = 1.0
    role: str = "structure"
    confidence: float = 1.0
    layer: int = 0
    pressure: list[float] | None = None
    tool_state: dict | None = None
    part: str | None = None
    stage: str | None = None
    stroke_id: str | None = None

    def cleaned(self) -> "Stroke":
        # Preserve pressure alignment while removing consecutive duplicate points.
        if self.pressure is not None and len(self.pressure) == len(self.points):
            pts: list[tuple[float, float]] = []
            pressure: list[float] = []
            for p, pr in zip(self.points, self.pressure):
                q = (float(p[0]), float(p[1]))
                if not pts or q != pts[-1]:
                    pts.append(q)
                    pressure.append(float(pr))
            self.points = pts
            self.pressure = pressure
        else:
            pts = []
            for p in self.points:
                q = (float(p[0]), float(p[1]))
                if not pts or q != pts[-1]:
                    pts.append(q)
            self.points = pts
            if self.pressure is not None and len(self.pressure) != len(self.points):
                self.pressure = None
        if self.pressure is not None:
            self.pressure = [max(0.0, min(1.0, float(v))) for v in self.pressure]
        return self

@dataclass
class StrokeIR:
    width: int
    height: int
    strokes: list[Stroke] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def add(self, stroke: Stroke) -> None:
        stroke.cleaned()
        if len(stroke.points) >= 2:
            if stroke.stroke_id is None:
                stroke.stroke_id = f"s{len(self.strokes)+1:04d}"
            self.strokes.append(stroke)

    def extend(self, strokes: Iterable[Stroke]) -> None:
        for s in strokes:
            self.add(s)

    def to_dict(self) -> dict:
        return {
            "width": self.width,
            "height": self.height,
            "metadata": self.metadata,
            "strokes": [asdict(s) for s in self.strokes],
        }

    def to_json(self, path: str | None = None) -> str:
        text = json.dumps(self.to_dict(), indent=2, ensure_ascii=False)
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)
        return text
