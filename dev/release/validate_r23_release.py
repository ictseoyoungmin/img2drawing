"""Validate R23 release identity and preserved legacy compatibility assets.

The canonical skill is intentionally stage-free.  This validator therefore checks that
R23 remains reachable and importable, rather than requiring Pn doctrine to be copied into
the canonical ``SKILL.md`` reading route.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "skills/img2drawing/src"))

import img2drawing
from img2drawing._version import RELEASE_REVISION, RELEASE_SLICE


if RELEASE_REVISION != "R23" or img2drawing.__version__ != "0.5.2.dev23":
    raise SystemExit(f"release identity drift: {img2drawing.__version__} {RELEASE_REVISION}")
if RELEASE_SLICE != "R23_material_integrated_visual_quality":
    raise SystemExit("R23 release slice drift")

skill = (ROOT / "skills/img2drawing/SKILL.md").read_text(encoding="utf-8")
for marker in ("DrawingSession", "references/legacy-r23.md"):
    if marker not in skill:
        raise SystemExit(f"canonical SKILL.md compatibility marker missing: {marker}")

gateway = ROOT / "skills/img2drawing/references/legacy-r23.md"
if not gateway.is_file():
    raise SystemExit(
        "missing R23 compatibility gateway: "
        "skills/img2drawing/references/legacy-r23.md"
    )

for relative in (
    "skills/img2drawing/references/stages/p4-structural-connections.md",
    "skills/img2drawing/references/stages/p5-clean-blockin.md",
    "skills/img2drawing/references/stages/p6-identity-finish.md",
):
    if not (ROOT / relative).is_file():
        raise SystemExit(f"missing preserved R23 compatibility asset: {relative}")

try:
    from img2drawing.run import DrawingRun
except Exception as exc:  # pragma: no cover - exercised by the release environment
    raise SystemExit(f"DrawingRun compatibility import failed: {exc}") from exc
if not hasattr(DrawingRun, "resume"):
    raise SystemExit("DrawingRun compatibility surface is missing resume")

manifest = ROOT / "dev/release/r23/release_manifest.json"
data = json.loads(manifest.read_text(encoding="utf-8"))
if data.get("version") != img2drawing.__version__ or data.get("revision") != RELEASE_REVISION:
    raise SystemExit("release manifest identity mismatch")
for item in data.get("artifacts", []):
    path = ROOT / item["path"]
    if not path.is_file():
        raise SystemExit(f"missing release artifact: {path}")
print(f"R23_RELEASE_VALIDATION_PASS {img2drawing.__version__}")
