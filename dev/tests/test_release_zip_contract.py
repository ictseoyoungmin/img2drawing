from __future__ import annotations

import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
BUILD_SCRIPT = ROOT / "dev" / "tools" / "build_skill_zip.py"
SOURCE_PACKAGE = ROOT / "skills" / "img2drawing"
RETIRED_MODULES = (
    "img2drawing.stages",
    "img2drawing.exemplar",
    "img2drawing.review",
    "img2drawing.registration",
    "img2drawing.canvas",
    "img2drawing.reference",
    "img2drawing.legacy",
)


def _package_copy(tmp_path: Path) -> Path:
    package = tmp_path / "workspace" / "img2drawing"
    shutil.copytree(SOURCE_PACKAGE, package)
    return package


def _build(package: Path, out: Path) -> list[str]:
    subprocess.run(
        [
            sys.executable,
            str(BUILD_SCRIPT),
            "--package-dir",
            str(package),
            "--out",
            str(out),
        ],
        check=True,
        cwd=ROOT,
    )
    with zipfile.ZipFile(out) as zf:
        return zf.namelist()


def test_built_zip_excludes_local_build_cache_and_bytecode_residue(tmp_path: Path) -> None:
    package = _package_copy(tmp_path)
    residue = {
        "build/junk.bin": b"build",
        "dist/junk.whl": b"dist",
        ".pytest_cache/state": b"pytest",
        ".mypy_cache/state": b"mypy",
        ".ruff_cache/state": b"ruff",
        ".venv/marker": b"venv",
        "src/img2drawing/__pycache__/ghost.pyc": b"bytecode",
        "src/img2drawing/ghost.pyo": b"optimized-bytecode",
        "src/img2drawing.egg-info/PKG-INFO": b"egg-info",
        "src/ghost.dist-info/METADATA": b"dist-info",
        ".DS_Store": b"finder",
        ".coverage": b"coverage",
        ".coverage.worker": b"coverage-worker",
    }
    for relative, payload in residue.items():
        path = package / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)

    out = tmp_path / "img2drawing-release.zip"
    names = _build(package, out)
    assert names, "build produced an empty zip"
    assert all(name.startswith("img2drawing/") for name in names)
    for relative in residue:
        assert f"img2drawing/{relative}" not in names, relative
    assert not any("__pycache__" in name for name in names)
    assert not any(name.endswith((".pyc", ".pyo")) for name in names)
    assert not any(".egg-info" in name or ".dist-info" in name for name in names)


def test_built_zip_is_importable_and_excludes_retired_modules(tmp_path: Path) -> None:
    package = _package_copy(tmp_path)
    out = tmp_path / "img2drawing-release.zip"
    _build(package, out)
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
    payload = json.loads(result.stdout.strip().splitlines()[-1])
    assert not any(payload.values()), payload


def test_builder_rejects_output_inside_package_tree(tmp_path: Path) -> None:
    package = _package_copy(tmp_path)
    result = subprocess.run(
        [
            sys.executable,
            str(BUILD_SCRIPT),
            "--package-dir",
            str(package),
            "--out",
            str(package / "dist" / "self.zip"),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "outside the package directory" in result.stderr
    assert not (package / "dist" / "self.zip").exists()
