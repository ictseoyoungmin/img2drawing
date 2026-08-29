"""Release-identity validator for img2drawing R23."""
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
for phrase in ("P4", "P5", "P6", "face", "hair", "pressure"):
    if phrase.lower() not in skill.lower():
        raise SystemExit(f"R23 doctrine missing from SKILL.md: {phrase}")

manifest = ROOT / "dev/release/r23/release_manifest.json"
data = json.loads(manifest.read_text(encoding="utf-8"))
if data.get("version") != img2drawing.__version__ or data.get("revision") != RELEASE_REVISION:
    raise SystemExit("release manifest identity mismatch")
for item in data.get("artifacts", []):
    path = ROOT / item["path"]
    if not path.is_file():
        raise SystemExit(f"missing release artifact: {path}")
print(f"R23_RELEASE_VALIDATION_PASS {img2drawing.__version__}")
