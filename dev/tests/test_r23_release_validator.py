from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_r23_release_validator_accepts_stage_free_canonical_skill() -> None:
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
    assert "R23_RELEASE_VALIDATION_PASS 0.5.2.dev23" in result.stdout
