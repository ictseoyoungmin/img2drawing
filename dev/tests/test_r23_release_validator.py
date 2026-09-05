from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import img2drawing


ROOT = Path(__file__).resolve().parents[2]


def test_r23_release_validator_checks_frozen_manifest_under_current_vnext() -> None:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT / "skills/img2drawing/src")
    result = subprocess.run(
        [sys.executable, "dev/release/validate_r23_release.py"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert (
        f"R23_COMPATIBILITY_VALIDATION_PASS 0.5.2.dev23 under {img2drawing.__version__}"
        in result.stdout
    )
