from __future__ import annotations
from dataclasses import dataclass, asdict

@dataclass(frozen=True)
class ToolState:
    tool: str
    width: float
    pressure: float
    opacity: float
    hardness: float
    grain: float
    taper_in: float
    taper_out: float
    jitter: float
    mode: str = "draw"
    erase_strength: float = 0.0

    def to_dict(self) -> dict:
        return asdict(self)

    def validated(self) -> "ToolState":
        if self.width <= 0:
            raise ValueError("tool width must be positive")
        for name in ("pressure", "opacity", "hardness", "grain", "taper_in", "taper_out", "jitter", "erase_strength"):
            v = getattr(self, name)
            if not 0.0 <= v <= 1.0:
                raise ValueError(f"{name} must be in [0,1]")
        return self


def construction_pencil() -> ToolState:
    return ToolState(
        tool="construction_pencil",
        width=1.8,
        pressure=0.30,
        opacity=0.30,
        hardness=0.58,
        grain=0.30,
        taper_in=0.34,
        taper_out=0.42,
        jitter=0.06,
    )


def form_pencil() -> ToolState:
    return ToolState(
        tool="form_pencil",
        width=3.2,
        pressure=0.58,
        opacity=0.70,
        hardness=0.66,
        grain=0.36,
        taper_in=0.24,
        taper_out=0.30,
        jitter=0.045,
    )


def accent_pencil() -> ToolState:
    return ToolState(
        tool="accent_pencil",
        width=4.8,
        pressure=0.82,
        opacity=0.94,
        hardness=0.78,
        grain=0.24,
        taper_in=0.18,
        taper_out=0.24,
        jitter=0.025,
    )


def soft_eraser() -> ToolState:
    return ToolState(
        tool="soft_eraser",
        width=18.0,
        pressure=0.45,
        opacity=1.0,
        hardness=0.18,
        grain=0.08,
        taper_in=0.10,
        taper_out=0.10,
        jitter=0.02,
        mode="erase",
        erase_strength=0.55,
    )


def hard_eraser() -> ToolState:
    return ToolState(
        tool="hard_eraser",
        width=14.0,
        pressure=0.82,
        opacity=1.0,
        hardness=0.96,
        grain=0.0,
        taper_in=0.05,
        taper_out=0.05,
        jitter=0.0,
        mode="erase",
        erase_strength=1.0,
    )


TOOL_PRESETS = {
    "construction_pencil": construction_pencil,
    "form_pencil": form_pencil,
    "accent_pencil": accent_pencil,
    "soft_eraser": soft_eraser,
    "hard_eraser": hard_eraser,
}


def get_tool(name: str) -> ToolState:
    try:
        return TOOL_PRESETS[name]().validated()
    except KeyError as exc:
        raise ValueError(f"unknown tool preset: {name}") from exc
