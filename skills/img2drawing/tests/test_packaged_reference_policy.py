from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGED = ROOT / "src" / "img2drawing" / "data" / "exemplars" / "full_body_croquis"


def test_packaged_reference_manifest_is_complete():
    manifest = json.loads((PACKAGED / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["purpose"] == "representation_only"
    for stage in (
        "P1_gesture",
        "P2_primary_axes",
        "P3_primary_masses",
        "P4_structural_connections",
        "P5_clean_blockin",
    ):
        path = PACKAGED / manifest["stages"][stage]
        assert path.is_file(), path
