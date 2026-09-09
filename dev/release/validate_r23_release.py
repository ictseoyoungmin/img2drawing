"""Validate the frozen R23 release after current-source compatibility retirement.

R23 is historical evidence, not a current runtime promise. This validator checks the frozen
manifest/assets and verifies that the exact retired compatibility module remains recoverable from
the immutable v1.0.2 Git tag. It intentionally does not import ``img2drawing.legacy.r23`` from the
mutable post-release source tree.
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "skills/img2drawing/src"))

import img2drawing
from img2drawing._version import LEGACY_R23_PUBLIC_API


if LEGACY_R23_PUBLIC_API != "DrawingRun/0.5.2-r23":
    raise SystemExit("legacy R23 public API identity drift")
if not hasattr(img2drawing, "DrawingSession"):
    raise SystemExit("current package no longer exposes the canonical DrawingSession")
if importlib.util.find_spec("img2drawing.legacy") is not None:
    raise SystemExit("retired img2drawing.legacy namespace unexpectedly remains installable")

compatibility_root = ROOT / "dev/release/r23/compatibility/stages"
for filename in (
    "p4-structural-connections.md",
    "p5-clean-blockin.md",
    "p6-identity-finish.md",
):
    path = compatibility_root / filename
    if not path.is_file():
        raise SystemExit(f"missing preserved R23 compatibility asset: {path.relative_to(ROOT)}")

historical_path = "skills/img2drawing/src/img2drawing/legacy/r23.py"
expected_blob = "e8f4ce234bddc5e5481c41fefe4c356c478fd1cb"
result = subprocess.run(
    ["git", "rev-parse", f"v1.0.2:{historical_path}"],
    cwd=ROOT,
    capture_output=True,
    text=True,
)
if result.returncode != 0:
    raise SystemExit(f"cannot resolve historical R23 source from v1.0.2 tag: {result.stderr.strip()}")
if result.stdout.strip() != expected_blob:
    raise SystemExit("historical R23 compatibility blob identity drift")

manifest = ROOT / "dev/release/r23/release_manifest.json"
data = json.loads(manifest.read_text(encoding="utf-8"))
if data.get("version") != "0.5.2.dev23" or data.get("revision") != "R23":
    raise SystemExit("frozen R23 manifest identity mismatch")
for item in data.get("artifacts", []):
    path = ROOT / item["path"]
    if not path.is_file():
        raise SystemExit(f"missing release artifact: {path}")

print(
    f"R23_HISTORICAL_RELEASE_VALIDATION_PASS {data['version']} under "
    f"{img2drawing.__version__} blob={expected_blob}"
)
