"""Exercise stress-result comparison without executing the rendering workload."""
import json
from pathlib import Path
import subprocess
import sys

import pytest


SCRIPT = Path(__file__).resolve().parents[1] / "benchmarks/mixed_media_stress/compare.py"


@pytest.fixture
def metrics():
    common = {
        "protocol_sha256": "1" * 64,
        "script_sha256": "2" * 64,
        "python": "3.10.19",
        "numpy": "2.2.6",
        "pillow": "11.3.0",
        "counts": {"paths": 2},
        "actions": 2,
        "frames": 3,
        "profile_digest": "3" * 64,
        "drawing_state_hash": "4" * 64,
        "action_log_sha256": "5" * 64,
        "final_pixel_sha256": "6" * 64,
        "frame_rgb_hashes": ["7" * 64, "8" * 64, "9" * 64],
        "mechanical_gate": "PASS",
        "gif_sha256": "a" * 64,
        "total_sec": 1.0,
    }
    return [
        {**json.loads(json.dumps(common)), "version": version, "mode": mode}
        for version, mode in (("1.3.0", "graphite"), ("1.4.0", "graphite"), ("1.4.0", "ink"))
    ]


def compare(tmp_path, metrics, expected_version="1.4.0"):
    paths = []
    for name, payload in zip(("baseline", "graphite", "ink"), metrics):
        path = tmp_path / f"{name}.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        paths.append(str(path))
    command = [sys.executable, str(SCRIPT), *paths]
    if expected_version is not None:
        command.extend(["--expected-candidate-version", expected_version])
    return subprocess.run(command, text=True, capture_output=True)


def test_promoted_candidate_version_preserves_graphite_comparison(tmp_path, metrics):
    result = compare(tmp_path, metrics)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "PINNED_V130_GRAPHITE_PARITY_PASS" in result.stdout


@pytest.mark.parametrize("candidates", [(1,), (2,), (1, 2)])
def test_mismatched_candidate_version_is_rejected(tmp_path, metrics, candidates):
    for candidate in candidates:
        metrics[candidate]["version"] = "1.3.1"
    result = compare(tmp_path, metrics)
    assert result.returncode != 0
    assert "candidate version mismatch" in result.stderr


def test_changed_intermediate_graphite_frame_is_rejected(tmp_path, metrics):
    metrics[1]["frame_rgb_hashes"][1] = "b" * 64
    result = compare(tmp_path, metrics)
    assert result.returncode != 0
    assert "frame_rgb_hashes" in result.stderr


def test_candidate_version_must_be_explicit(tmp_path, metrics):
    result = compare(tmp_path, metrics, expected_version=None)
    assert result.returncode == 2
    assert "--expected-candidate-version" in result.stderr
