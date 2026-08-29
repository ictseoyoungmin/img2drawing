#!/usr/bin/env python3
"""Create reproducible R23 skill/tree manifests from current source."""
from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / "skills/img2drawing"
OUT = ROOT / "dev/release/r23"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def build() -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    zip_path = OUT / "img2drawing-skill-0.5.2-r23.zip"
    excluded = {"dist", "build", "__pycache__", ".pytest_cache", "*.egg-info"}
    files = []
    for path in sorted(SKILL.rglob("*")):
        if not path.is_file():
            continue
        rel_parts = set(path.relative_to(SKILL).parts)
        if rel_parts & excluded or any(part.endswith(".egg-info") for part in rel_parts):
            continue
        files.append(path)
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in files:
            archive.write(path, Path("img2drawing") / path.relative_to(SKILL))
    (OUT / (zip_path.name + ".sha256")).write_text(f"{digest(zip_path)}  {zip_path.name}\n", encoding="utf-8")

    wheel = OUT / "img2drawing-0.5.2.dev23-py3-none-any.whl"
    if not wheel.is_file():
        raise FileNotFoundError(wheel)
    tree = OUT / "img2drawing-0.5.2-r23-TREE.md"
    tree.write_text("# img2drawing R23 source tree\n\n" + "\n".join(f"- `skills/img2drawing/{p.relative_to(SKILL).as_posix()}`" for p in files) + "\n", encoding="utf-8")
    artifacts = []
    for path in (zip_path, wheel, tree):
        artifacts.append({"path": str(path.relative_to(ROOT)), "sha256": digest(path), "bytes": path.stat().st_size})
    manifest = {
        "schema": "img2drawing.release_manifest.v1",
        "version": "0.5.2.dev23",
        "revision": "R23",
        "release_slice": "R23_material_integrated_visual_quality",
        "source_authority": "skills/img2drawing",
        "artifacts": artifacts,
        "visual_evidence": "dev/evidence/material-integration and dev/evidence/fresh-worker",
        "mechanical_quality_authority": "dev/tools/verify_bottleneck_completion.py",
    }
    (OUT / "release_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")
    (OUT / "release_manifest.sha256").write_text(f"{digest(OUT / 'release_manifest.json')}  release_manifest.json\n", encoding="utf-8")
    return zip_path


if __name__ == "__main__":
    print(build())
