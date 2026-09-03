"""Validate the frozen R23 manifest and its preserved runtime compatibility boundary.

The current package is intentionally vNext. This historical validator checks that the
frozen R23 release remains internally identified and explicitly reachable through the
runtime compatibility namespace. It must not require the deployable skill instruction
graph to carry R23 stage or migration documentation.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "skills/img2drawing/src"))

import img2drawing
from img2drawing._version import (
    LEGACY_R23_PUBLIC_API,
    RELEASE_REVISION,
    RELEASE_SLICE,
)


if RELEASE_REVISION != "B17" or img2drawing.__version__ != "0.6.0rc2":
    raise SystemExit(f"release identity drift: {img2drawing.__version__} {RELEASE_REVISION}")
if RELEASE_SLICE != "B17_package_public_api_release_candidate":
    raise SystemExit("current release slice drift")
if LEGACY_R23_PUBLIC_API != "DrawingRun/0.5.2-r23":
    raise SystemExit("legacy R23 public API identity drift")

compatibility_root = ROOT / "dev/release/r23/compatibility/stages"
for filename in (
    "p4-structural-connections.md",
    "p5-clean-blockin.md",
    "p6-identity-finish.md",
):
    path = compatibility_root / filename
    if not path.is_file():
        raise SystemExit(f"missing preserved R23 compatibility asset: {path.relative_to(ROOT)}")

try:
    from img2drawing.legacy.r23 import DrawingRun
except Exception as exc:  # pragma: no cover - exercised by the release environment
    raise SystemExit(f"DrawingRun compatibility import failed: {exc}") from exc
if not hasattr(DrawingRun, "resume"):
    raise SystemExit("DrawingRun compatibility surface is missing resume")

manifest = ROOT / "dev/release/r23/release_manifest.json"
data = json.loads(manifest.read_text(encoding="utf-8"))
if data.get("version") != "0.5.2.dev23" or data.get("revision") != "R23":
    raise SystemExit("frozen R23 manifest identity mismatch")
for item in data.get("artifacts", []):
    path = ROOT / item["path"]
    if not path.is_file():
        raise SystemExit(f"missing release artifact: {path}")
print(f"R23_COMPATIBILITY_VALIDATION_PASS {data['version']} under {img2drawing.__version__}")
