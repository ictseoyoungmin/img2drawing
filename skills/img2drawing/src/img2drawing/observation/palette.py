"""Ask what a boundary separates before trusting where it is.

A single luminance threshold answers one question: "is this darker than N?" On a
subject in dark clothing that question cannot see a bare hand, because skin and
a grey background sit at nearly the same luminance while the jacket sits far
below both. Profiling such a subject on darkness alone silently reports the body
as ending where the skin begins.

This module does not classify anything on its own. The Agent samples the regions
it has already identified by eye - background here, garment there, skin there -
and the palette then reports which of *those* each pixel is nearest, in a space
where hue and chroma count as much as lightness.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Sequence

import numpy as np
from PIL import Image

Box = tuple[int, int, int, int]


def _features(rgb: np.ndarray) -> np.ndarray:
    """(lightness, warmth, chroma) - the axes that separate skin from grey."""
    rgb = rgb.astype(np.float64)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    lightness = (0.299 * r + 0.587 * g + 0.114 * b)
    warmth = r - b
    chroma = rgb.max(axis=-1) - rgb.min(axis=-1)
    return np.stack([lightness, warmth * 2.0, chroma * 2.0], axis=-1)


@dataclass
class MaterialSample:
    name: str
    box: Box
    mean_rgb: tuple[float, float, float]
    feature: tuple[float, float, float]
    spread: float

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "box": list(self.box),
                "mean_rgb": [round(v, 1) for v in self.mean_rgb],
                "feature": [round(v, 1) for v in self.feature],
                "spread": round(self.spread, 1)}


@dataclass
class SubjectPalette:
    """Agent-authored material references for one subject."""

    subject: Path
    samples: dict[str, MaterialSample] = field(default_factory=dict)
    _rgb: np.ndarray | None = field(default=None, repr=False)

    def __post_init__(self) -> None:
        self.subject = Path(self.subject)
        with Image.open(self.subject) as im:
            self._rgb = np.asarray(im.convert("RGB"))

    @property
    def rgb(self) -> np.ndarray:
        assert self._rgb is not None
        return self._rgb

    def sample(self, name: str, box: Box) -> MaterialSample:
        """Record one region the Agent has already identified as this material."""
        x0, y0, x1, y1 = (int(v) for v in box)
        if not (0 <= x0 < x1 <= self.rgb.shape[1] and 0 <= y0 < y1 <= self.rgb.shape[0]):
            raise ValueError(f"sample box out of bounds: {box}")
        patch = self.rgb[y0:y1, x0:x1].reshape(-1, 3)
        if patch.size == 0:
            raise ValueError("sample box selects no pixels")
        feat = _features(patch)
        mean = feat.mean(axis=0)
        spread = float(np.linalg.norm(feat - mean, axis=-1).mean())
        record = MaterialSample(
            name=str(name), box=(x0, y0, x1, y1),
            mean_rgb=tuple(float(v) for v in patch.mean(axis=0)),
            feature=tuple(float(v) for v in mean), spread=spread,
        )
        self.samples[record.name] = record
        return record

    def _matrix(self) -> tuple[list[str], np.ndarray]:
        if len(self.samples) < 2:
            raise ValueError("a palette needs at least two sampled materials to separate anything")
        names = list(self.samples)
        return names, np.array([self.samples[n].feature for n in names], dtype=np.float64)

    def separation(self) -> list[tuple[str, str, float]]:
        """Distance between every pair. Small distances are the traps."""
        names, mat = self._matrix()
        out = []
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                out.append((names[i], names[j], float(np.linalg.norm(mat[i] - mat[j]))))
        return sorted(out, key=lambda t: t[2])

    def ambiguous_pairs(self, threshold: float = 40.0) -> list[tuple[str, str, float]]:
        """Material pairs this subject cannot reliably tell apart by colour alone."""
        return [row for row in self.separation() if row[2] < threshold]

    def classify(self, x: int, y: int) -> tuple[str, float]:
        names, mat = self._matrix()
        feat = _features(self.rgb[int(y), int(x)])
        d = np.linalg.norm(mat - feat, axis=-1)
        i = int(d.argmin())
        return names[i], float(d[i])

    def classify_row(self, y: int, x_range: tuple[int, int], *, min_run: int = 3) -> list[tuple[str, int, int]]:
        """Segment one scanline into runs of the sampled materials."""
        names, mat = self._matrix()
        x0, x1 = int(x_range[0]), int(x_range[1])
        feat = _features(self.rgb[int(y), x0:x1])
        idx = np.linalg.norm(feat[:, None, :] - mat[None, :, :], axis=-1).argmin(axis=1)
        runs: list[tuple[str, int, int]] = []
        start = 0
        for i in range(1, len(idx) + 1):
            if i == len(idx) or idx[i] != idx[start]:
                if i - start >= min_run:
                    runs.append((names[int(idx[start])], x0 + start, x0 + i - 1))
                start = i
        return runs

    def boundary_kind(self, a: tuple[int, int], b: tuple[int, int]) -> dict[str, Any]:
        """Name what the edge between two points actually separates."""
        na, da = self.classify(*a)
        nb, db = self.classify(*b)
        fa = _features(self.rgb[a[1], a[0]])
        fb = _features(self.rgb[b[1], b[0]])
        d = np.abs(fa - fb)
        axis = ("lightness", "warmth", "chroma")[int(d.argmax())]
        return {"a": na, "b": nb, "separates": None if na == nb else (na, nb),
                "dominant_axis": axis,
                "luminance_step": float(d[0]), "warmth_step": float(d[1]) / 2.0,
                "visible_to_luminance_threshold": bool(d[0] >= 25.0)}

    def to_dict(self) -> dict[str, Any]:
        return {"format": "subject-palette/v1", "subject": self.subject.name,
                "samples": [s.to_dict() for s in self.samples.values()],
                "ambiguous_pairs": [[a, b, round(v, 1)] for a, b, v in self.ambiguous_pairs()]}
