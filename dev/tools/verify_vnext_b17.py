#!/usr/bin/env python3
"""Audit the current package, clean install, instruction graph, and supply-chain boundary.

B17 is a *current package* verifier. Historical release identity belongs to B18 and
``dev/release/vnext/CONTRACT_FREEZE.json``; do not use that frozen v1.0.2 record as the
version authority for a later RC package.
"""

from __future__ import annotations

import argparse
import email.parser
import os
import re
import runpy
import subprocess
import sys
import tarfile
import tempfile
import venv
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "skills" / "img2drawing"
VERSION_FILE = PACKAGE / "src" / "img2drawing" / "_version.py"
VERSION_NS = runpy.run_path(str(VERSION_FILE))
VERSION = str(VERSION_NS["__version__"])
PUBLIC_API = str(VERSION_NS["PUBLIC_API"])
RELEASE_REVISION = str(VERSION_NS["RELEASE_REVISION"])
TEXT_SUFFIXES = {".md", ".py", ".json", ".toml", ".txt", ".yml", ".yaml"}
FORBIDDEN_ARCHIVE_PARTS = {
    ".git", ".github", ".pytest_cache", ".unlazy", "__pycache__", "dev",
    "dogfood", "drawings", "showcase", "temp", "examples",
}
CONTROL_PLANE_FILES = {
    "CONTRACT_FREEZE.json", "FREEZE.md", "MIGRATION.md", "NOTICE", "NOTICE.md",
    "RELEASE.md", "SUPPORT.md",
}
REQUIRED_GRAPH_FILES = {
    "SKILL.md",
    "references/INDEX.md",
    "references/foundation/line-economy.md",
    "references/foundation/reference-authority.md",
    "references/foundation/scope-and-precedence.md",
    "references/modes/croquis.md",
    "references/modes/gesture-drawing.md",
    "references/observation/visual-observation.md",
    "references/construction/gesture-and-masses.md",
    "references/construction/foreshortening-and-depth.md",
    "references/description/descriptive-geometry.md",
    "references/figure/head-face-hair.md",
    "references/figure/hands-and-grip.md",
    "references/figure/legs-feet.md",
    "references/figure/clothing-folds.md",
    "references/props/attached-objects.md",
    "references/environment/ground-and-context.md",
    "references/review/residual-correction.md",
    "references/review/residual-routing.md",
    "references/review/markmaking-residuals.md",
    "references/output/render-profile-and-replay.md",
    "references/api/public-surface.md",
    "references/api/runtime-discovery.md",
    "references/markmaking/broad-graphite.md",
    "references/markmaking/stroke-dynamics.md",
    "references/markmaking/style-policy.md",
}


def _run(command: list[str], *, cwd: Path, env: dict[str, str] | None = None) -> str:
    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            env=env,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
    except subprocess.CalledProcessError as exc:
        if exc.stdout:
            print(exc.stdout, file=sys.stderr, end="" if exc.stdout.endswith("\n") else "\n")
        raise
    return completed.stdout


def _safe_member(name: str) -> PurePosixPath:
    path = PurePosixPath(name)
    if path.is_absolute() or ".." in path.parts or "" in path.parts:
        raise AssertionError(f"unsafe archive path: {name}")
    return path


def _canonical_docs() -> list[Path]:
    documents = [ROOT / "README.md"]
    documents.extend(PACKAGE.glob("*.md"))
    documents.extend((PACKAGE / "references").rglob("*.md"))
    return sorted(set(documents))


def check_source() -> None:
    version_text = VERSION_FILE.read_text(encoding="utf-8")
    assert f'__version__ = "{VERSION}"' in version_text
    assert f'RELEASE_REVISION = "{RELEASE_REVISION}"' in version_text
    assert (ROOT / "LICENSE").read_bytes() == (PACKAGE / "LICENSE").read_bytes()

    pyproject = (PACKAGE / "pyproject.toml").read_text(encoding="utf-8")
    assert '"numpy>=1.24"' in pyproject and '"Pillow>=10"' in pyproject
    assert "svgwrite" not in pyproject
    assert 'license-files = ["LICENSE"]' in pyproject

    workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "verify_vnext_b17.py" in workflow
    assert "verify_v103_rc_promotion.py" in workflow
    assert "validate_r23_release.py" not in workflow

    assert not (PACKAGE / "examples").exists(), "uncurated examples leaked into deployable skill"
    for name in CONTROL_PLANE_FILES:
        assert not (PACKAGE / name).exists(), f"control-plane file leaked into skill root: {name}"
    assert not (PACKAGE / "playbooks").exists()
    assert not (PACKAGE / "references" / "stages").exists()
    assert not (PACKAGE / "src" / "img2drawing" / "legacy").exists()

    for relative in REQUIRED_GRAPH_FILES:
        assert (PACKAGE / relative).is_file(), f"missing instruction-graph leaf: {relative}"

    link_pattern = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
    missing: list[str] = []
    for document in _canonical_docs():
        text = document.read_text(encoding="utf-8")
        if re.search(r"[\uac00-\ud7a3]", text):
            raise AssertionError(f"shipped canonical guidance is not English-only: {document}")
        for raw in link_pattern.findall(text):
            target = raw.strip().strip("<>").split("#", 1)[0]
            if not target or re.match(r"^[a-z][a-z0-9+.-]*:", target):
                continue
            if not (document.parent / target).resolve().exists():
                missing.append(f"{document.relative_to(ROOT)} -> {raw}")
    assert not missing, "broken canonical documentation links:\n" + "\n".join(missing)


def _scan_text(name: str, payload: bytes) -> None:
    if Path(name).suffix.lower() not in TEXT_SUFFIXES:
        return
    text = payload.decode("utf-8")
    for token in ("/home/", "/mnt/", "BEGIN PRIVATE KEY", "BEGIN OPENSSH PRIVATE KEY"):
        assert token not in text, f"artifact contains local/secret token {token!r}: {name}"
    assert not re.search(r"AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{30,}", text), f"secret-like token: {name}"


def _probe(python: Path, *, cwd: Path, env: dict[str, str]) -> dict[str, object]:
    code = (
        "import json,img2drawing; from img2drawing._version import PUBLIC_API,RELEASE_REVISION; "
        "print(json.dumps({'version':img2drawing.__version__,'api':PUBLIC_API,"
        "'revision':RELEASE_REVISION,'exports':sorted(img2drawing.__all__),"
        "'file':img2drawing.__file__}))"
    )
    return __import__("json").loads(_run([str(python), "-c", code], cwd=cwd, env=env).strip())


def check_artifacts(work: Path) -> tuple[Path, Path]:
    dist = work / "dist"
    _run([sys.executable, "-m", "build", "--outdir", str(dist)], cwd=PACKAGE)
    wheel = next(dist.glob("*.whl"))
    sdist = next(dist.glob("*.tar.gz"))

    assert VERSION.replace("-", "_") in wheel.name
    with zipfile.ZipFile(wheel) as archive:
        names = archive.namelist()
        for name in names:
            path = _safe_member(name)
            assert path.parts[0] == "img2drawing" or ".dist-info" in path.parts[0], name
            assert not FORBIDDEN_ARCHIVE_PARTS.intersection(path.parts), name
            _scan_text(name, archive.read(name))
        metadata_name = next(name for name in names if name.endswith(".dist-info/METADATA"))
        metadata = email.parser.Parser().parsestr(archive.read(metadata_name).decode())
        assert metadata["Version"] == VERSION
        runtime_requires = [v for v in metadata.get_all("Requires-Dist", []) if "extra ==" not in v]
        assert any(v.lower().startswith("numpy>=") for v in runtime_requires)
        assert any(v.lower().startswith("pillow>=") for v in runtime_requires)
        assert len(runtime_requires) == 2
        assert any(name.endswith(".dist-info/licenses/LICENSE") for name in names)

    with tarfile.open(sdist, "r:gz") as archive:
        relative_names: set[str] = set()
        for member in archive.getmembers():
            path = _safe_member(member.name)
            assert member.isfile() or member.isdir(), f"unsupported archive member type: {member.name}"
            relative = path.parts[1:]
            assert not FORBIDDEN_ARCHIVE_PARTS.intersection(relative), member.name
            if relative:
                relative_names.add("/".join(relative))
            if relative and relative[-1] in CONTROL_PLANE_FILES:
                raise AssertionError(f"control-plane file shipped in sdist: {member.name}")
            if member.isfile():
                stream = archive.extractfile(member)
                assert stream is not None
                _scan_text(member.name, stream.read())
        assert REQUIRED_GRAPH_FILES.issubset(relative_names), sorted(REQUIRED_GRAPH_FILES - relative_names)
        assert not any(name.startswith("examples/") for name in relative_names)
    return wheel, sdist


def check_clean_install(work: Path, wheel: Path) -> None:
    environment = work / "venv"
    venv.EnvBuilder(with_pip=True, system_site_packages=False).create(environment)
    python = environment / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    clean_env = os.environ.copy()
    clean_env.pop("PYTHONPATH", None)
    _run([str(python), "-m", "pip", "install", "--no-input", str(wheel)], cwd=work, env=clean_env)

    dependency_locations = __import__("json").loads(
        _run(
            [str(python), "-c", "import json,numpy,PIL; print(json.dumps({'numpy':numpy.__file__,'PIL':PIL.__file__}))"],
            cwd=work,
            env=clean_env,
        ).strip()
    )
    for name, location in dependency_locations.items():
        assert Path(str(location)).resolve().is_relative_to(environment.resolve()), (
            f"clean install leaked host dependency {name}: {location}"
        )

    source_env = os.environ.copy()
    source_env["PYTHONPATH"] = str(PACKAGE / "src")
    source = _probe(Path(sys.executable), cwd=work, env=source_env)
    installed = _probe(python, cwd=work, env=clean_env)
    for field in ("version", "api", "revision", "exports"):
        assert source[field] == installed[field], f"source/install {field} mismatch"
    assert installed["version"] == VERSION
    assert installed["api"] == PUBLIC_API
    assert installed["revision"] == RELEASE_REVISION
    assert str(installed["file"]).startswith(str(environment)), installed["file"]
    assert "DrawingSession" in installed["exports"] and "DrawingRun" not in installed["exports"]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-only", action="store_true")
    args = parser.parse_args()
    check_source()
    if args.source_only:
        print(f"B17 current source/docs/CI audit: PASS ({VERSION})")
        return
    with tempfile.TemporaryDirectory(prefix="img2drawing-b17-") as temporary:
        work = Path(temporary)
        wheel, _sdist = check_artifacts(work)
        check_clean_install(work, wheel)
    print(f"B17 current package/API/clean-install/instruction-graph/supply-chain audit: PASS ({VERSION})")


if __name__ == "__main__":
    main()
