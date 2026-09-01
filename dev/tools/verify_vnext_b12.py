#!/usr/bin/env python3
"""Verification gates for B12 legacy runtime and persistence isolation."""

from __future__ import annotations

import json
import subprocess
import sys

from vnext_verification import ROOT, SRC, run_cli, run_pytest


def focused() -> None:
    run_pytest(
        "dev/tests/test_vnext_legacy_boundary.py",
        "dev/tests/test_vnext_session.py",
        "dev/tests/test_observation_lock.py",
        "dev/tests/test_timelapse.py",
    )
    print("B12_FOCUSED_VERIFICATION_PASS")


def contract() -> None:
    code = """
import sys
import img2drawing
assert 'DrawingRun' not in img2drawing.__all__
assert 'StageSpec' not in img2drawing.__all__
assert 'img2drawing.legacy.r23' not in sys.modules
assert 'img2drawing.run' not in sys.modules
assert 'img2drawing.stages' not in sys.modules
assert 'img2drawing.review' not in sys.modules
namespace = {}
exec('from img2drawing import *', namespace)
assert 'DrawingRun' not in namespace
assert 'img2drawing.legacy.r23' not in sys.modules
assert 'img2drawing.run' not in sys.modules
assert 'img2drawing.stages' not in sys.modules
assert 'img2drawing.review' not in sys.modules
"""
    subprocess.run(
        [sys.executable, "-c", code],
        cwd=ROOT,
        env={"PYTHONPATH": str(SRC)},
        check=True,
    )
    package = SRC / "img2drawing"
    root_source = (package / "__init__.py").read_text(encoding="utf-8")
    legacy_source = (package / "legacy/r23.py").read_text(encoding="utf-8")
    assert "_LAZY_EXPORTS" not in root_source
    assert "LEGACY_EXPORTS: Mapping" in legacy_source
    for path in (package / "vnext").rglob("*.py"):
        source = path.read_text(encoding="utf-8")
        assert "from ..run" not in source
        assert "from ..stages" not in source
        assert "from ..review" not in source
    assert not (package / "core_v2").exists()
    assert not (package / "vnext_core").exists()
    assert (package / "run.py").is_file()
    assert (package / "stages").is_dir()
    assert (package / "review").is_dir()
    print("B12_CONTRACT_VERIFICATION_PASS")


def full() -> None:
    run_pytest("dev/tests")
    print("B12_FULL_REGRESSION_PASS")


def closure() -> None:
    required = (
        ROOT / "skills/img2drawing/references/legacy-r23.md",
        ROOT / "dev/fixtures/vnext-b12/run.py",
        ROOT / "dev/fixtures/vnext-b12/compatibility.json",
        ROOT / "dev/planning/vnext/capsules/B12.md",
        ROOT / "dev/planning/vnext/slices/B12.md",
        ROOT / "dev/planning/vnext/slices/B13.md",
    )
    assert all(path.is_file() for path in required)
    matrix = json.loads(required[2].read_text(encoding="utf-8"))
    assert [row["checkpoint_schema"] for row in matrix["legacy"]] == [
        "img2drawing.run_checkpoint.v1",
        "img2drawing.run_checkpoint.v2",
        "img2drawing.run_checkpoint.v3",
    ]
    b12 = required[4].read_text(encoding="utf-8")
    b13 = required[5].read_text(encoding="utf-8")
    status = (ROOT / "dev/planning/vnext/STATUS.md").read_text(encoding="utf-8")
    assert "State: **CLOSED**" in b12 and "- [ ]" not in b12
    assert "State: **ACTIVE**" in b13
    assert "ACTIVE:   B13" in status and "B12" in status
    for path in (ROOT / "skills/img2drawing").rglob("*"):
        if path.is_file() and path.suffix in {".md", ".py", ".json"}:
            assert not any("\uac00" <= char <= "\ud7a3" for char in path.read_text(encoding="utf-8"))
    print("B12_CLOSURE_VERIFICATION_PASS")


def main() -> None:
    run_cli(
        __doc__ or "B12 verification",
        {"focused": focused, "contract": contract, "full": full, "closure": closure},
    )


if __name__ == "__main__":
    main()
