from __future__ import annotations

"""Integrity check for the authored and packaged exemplar trees."""

from dataclasses import dataclass
import hashlib
from pathlib import Path


DEFAULT_EXEMPLAR_FILES = (
    "manifest.json",
    "audit_manifest.json",
    "p1_gesture.png",
    "p2_axes.png",
    "p3_masses.png",
    "p4_structure.png",
    "p5_clean_blockin.png",
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


@dataclass(frozen=True)
class ExemplarTreeSyncReport:
    authoring_owner: Path
    packaged_copy: Path
    checked_files: tuple[str, ...]
    drift: tuple[str, ...]

    @property
    def valid(self) -> bool:
        return not self.drift

    def to_dict(self) -> dict:
        return {
            "schema": "img2drawing.exemplar_tree_sync.v1",
            "authoring_owner": str(self.authoring_owner),
            "packaged_copy": str(self.packaged_copy),
            "checked_files": list(self.checked_files),
            "drift": list(self.drift),
            "valid": self.valid,
            "policy": "top_level_authoring_owner_packaged_derived",
        }


class ExemplarTreeSyncError(ValueError):
    pass


def compare_exemplar_trees(
    authoring_owner: str | Path,
    packaged_copy: str | Path,
    *,
    filenames: tuple[str, ...] = DEFAULT_EXEMPLAR_FILES,
) -> ExemplarTreeSyncReport:
    """Compare canonical bytes and report drift without copying either tree."""
    owner = Path(authoring_owner).expanduser().resolve()
    packaged = Path(packaged_copy).expanduser().resolve()
    drift: list[str] = []
    checked: list[str] = []
    for name in filenames:
        checked.append(str(name))
        left = owner / name
        right = packaged / name
        if not left.exists():
            drift.append(f"authoring owner missing: {name}")
            continue
        if not right.exists():
            drift.append(f"packaged copy missing: {name}")
            continue
        if _sha256(left) != _sha256(right):
            drift.append(f"hash drift: {name}")
    return ExemplarTreeSyncReport(owner, packaged, tuple(checked), tuple(drift))


def assert_exemplar_trees_synced(
    authoring_owner: str | Path,
    packaged_copy: str | Path,
    *,
    filenames: tuple[str, ...] = DEFAULT_EXEMPLAR_FILES,
) -> ExemplarTreeSyncReport:
    report = compare_exemplar_trees(authoring_owner, packaged_copy, filenames=filenames)
    if not report.valid:
        raise ExemplarTreeSyncError("; ".join(report.drift))
    return report


__all__ = [
    "DEFAULT_EXEMPLAR_FILES",
    "ExemplarTreeSyncReport",
    "ExemplarTreeSyncError",
    "compare_exemplar_trees",
    "assert_exemplar_trees_synced",
]
