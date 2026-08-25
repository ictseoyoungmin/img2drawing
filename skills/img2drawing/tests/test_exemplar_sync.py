from __future__ import annotations

from pathlib import Path
import shutil

import pytest

from img2drawing import (
    ExemplarTreeSyncError,
    assert_exemplar_trees_synced,
    compare_exemplar_trees,
)


ROOT = Path(__file__).resolve().parents[1]
AUTHORING = ROOT / "exemplars" / "full_body_croquis"
PACKAGED = ROOT / "src" / "img2drawing" / "data" / "exemplars" / "full_body_croquis"


def test_authoring_owner_and_packaged_copy_are_synced():
    report = assert_exemplar_trees_synced(AUTHORING, PACKAGED)
    assert report.valid
    assert report.drift == ()
    assert report.to_dict()["policy"] == "top_level_authoring_owner_packaged_derived"


def test_packaged_drift_is_reported_and_rejected(tmp_path: Path):
    copied = tmp_path / "packaged"
    shutil.copytree(PACKAGED, copied)
    (copied / "p3_masses.png").write_bytes((copied / "p3_masses.png").read_bytes() + b"drift")
    report = compare_exemplar_trees(AUTHORING, copied)
    assert report.valid is False
    assert "hash drift: p3_masses.png" in report.drift
    with pytest.raises(ExemplarTreeSyncError, match="p3_masses.png"):
        assert_exemplar_trees_synced(AUTHORING, copied)


def test_missing_packaged_file_is_reported(tmp_path: Path):
    copied = tmp_path / "packaged"
    shutil.copytree(PACKAGED, copied)
    (copied / "p4_structure.png").unlink()
    report = compare_exemplar_trees(AUTHORING, copied)
    assert "packaged copy missing: p4_structure.png" in report.drift
