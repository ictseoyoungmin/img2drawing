from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "skills" / "img2drawing" / "src"
PACKAGE = SRC / "img2drawing"
FREEZE = ROOT / "dev" / "release" / "vnext" / "CONTRACT_FREEZE.json"
ARCHIVE = ROOT / "dev" / "legacy" / "r23_compat" / "README.md"


def _python(source: str) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(SRC)
    return subprocess.run(
        [sys.executable, "-c", source],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
    )


def test_installable_legacy_namespace_is_retired() -> None:
    assert not (PACKAGE / "legacy").exists()
    result = _python("import img2drawing.legacy")
    assert result.returncode != 0
    assert "ModuleNotFoundError" in result.stderr


def test_r23_root_names_no_longer_resolve_through_hidden_fallback() -> None:
    import img2drawing

    with pytest.raises(AttributeError):
        getattr(img2drawing, "DrawingRun")
    with pytest.raises(AttributeError):
        getattr(img2drawing, "StageContract")
    assert "DrawingRun" not in img2drawing.__all__
    assert "StageContract" not in img2drawing.__all__


def test_current_compat_shims_only_target_still_owned_namespaces() -> None:
    import img2drawing
    from img2drawing.core import CanvasHistory
    from img2drawing.inspection import ROI

    with pytest.warns(DeprecationWarning, match="root-compat shim"):
        assert img2drawing.CanvasHistory is CanvasHistory
    with pytest.warns(DeprecationWarning, match="root-compat shim"):
        assert img2drawing.ROI is ROI
    assert "CanvasHistory" not in dir(img2drawing)
    assert "ROI" not in dir(img2drawing)


def test_v102_freeze_preserves_historical_legacy_truth_without_requiring_current_code() -> None:
    frozen = json.loads(FREEZE.read_text(encoding="utf-8"))
    assert frozen["package_version"] == "1.0.2"
    assert frozen["ownership"]["legacy_namespace"] == "img2drawing.legacy.r23"
    assert frozen["legacy_checkpoint_schemas"] == [
        "img2drawing.run_checkpoint.v1",
        "img2drawing.run_checkpoint.v2",
        "img2drawing.run_checkpoint.v3",
    ]
    assert not (PACKAGE / "legacy").exists()


def test_retirement_archive_points_to_exact_historical_source() -> None:
    text = ARCHIVE.read_text(encoding="utf-8")
    assert "6b4a99431bdb402345fd3779cb16ba7ad1648cb7" in text
    assert "e8f4ce234bddc5e5481c41fefe4c356c478fd1cb" in text
    assert "skills/img2drawing/src/img2drawing/legacy/r23.py" in text
