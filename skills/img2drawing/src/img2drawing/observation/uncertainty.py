from dataclasses import dataclass

@dataclass(frozen=True)
class UncertaintyNote:
    claim: str
    reason: str
    confidence: float
    def __post_init__(self):
        if not 0.0 <= float(self.confidence) <= 1.0:
            raise ValueError("confidence must be in [0,1]")
