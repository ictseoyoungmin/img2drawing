from __future__ import annotations

import subprocess
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILD_SCRIPT = ROOT / "dev" / "tools" / "build_skill_zip.py"
RETIRED_MODULES = (
    "img2drawing.stages",
    "img2drawing.exemplar",
    "img2drawing.review",
    "img2drawing.registration",
    "img2drawing.canvas",
    "img2drawing.reference",
    "img2drawing.legacy",
)


def test_built_zip_excludes_pycache_and_egg_info_residue(tmp_path: Path) -> None:
    out = tmp_path / "img2drawing-release.zip"
    subprocess.run(
        [sys.executable, str(BUILD_SCRIPT), "--out", str(out)],
        check=True,
        cwd=ROOT,
    )
    with zipfile.ZipFile(out) as zf:
        names = zf.namelist()
    assert names, "build produced an empty zip"
    for name in names:
        assert "__pycache__" not in name, name
        assert not name.endswith(".pyc"), name
        assert ".egg-info" not in name, name


def test_built_zip_is_importable_and_excludes_retired_modules(tmp_path: Path) -> None:
    out = tmp_path / "img2drawing-release.zip"
    subprocess.run(
        [sys.executable, str(BUILD_SCRIPT), "--out", str(out)],
        check=True,
        cwd=ROOT,
    )
    extracted = tmp_path / "extracted"
    with zipfile.ZipFile(out) as zf:
        zf.extractall(extracted)
    src = extracted / "img2drawing" / "src"

    probe = f"""
import importlib.util, json
import sys
sys.path.insert(0, {str(src)!r})
import img2drawing
from img2drawing import DrawingSession, DrawingIntent, RenderProfile
retired = {list(RETIRED_MODULES)!r}
print(json.dumps({{name: importlib.util.find_spec(name) is not None for name in retired}}))
"""
    result = subprocess.run(
        [sys.executable, "-c", probe],
        check=True,
        capture_output=True,
        text=True,
    )
    import json

    payload = json.loads(result.stdout.strip().splitlines()[-1])
    assert not any(payload.values()), payload
