#!/usr/bin/env python3
"""Audit the release-candidate package, clean install, instruction graph, and supply-chain boundary.

This verifier checks packaging and integration only. It deliberately makes no visual-quality
claim and does not require drawing examples in the deployable skill.
"""

from __future__ import annotations

import argparse
import email.parser
import json
import os
import re
import subprocess
import sys
import tarfile
import tempfile
import venv
import zipfile
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "skills" / "img2drawing"
RELEASE_RECORDS = ROOT / "dev" / "release" / "vnext"
VERSION = "0.6.0rc1"
PUBLIC_API = "DrawingSession/0.6.0-vnext"
TEXT_SUFFIXES = {".md", ".py", ".json", ".toml", ".txt", ".yml", ".yaml"}
FORBIDDEN_ARCHIVE_PARTS = {
    ".git", ".github", ".pytest_cache", ".unlazy", "__pycache__", "dev",
    "dogfood", "drawings", "showcase", "temp", "examples",
}
CONTROL_PLANE_FILES = {
    "CONTRACT_FREEZE.json", "FREEZE.md", "MIGRATION.md", "NOTICE", "NOTICE.md",
    "RELEASE.md", "SUPPORT.md",
}
LEGACY_REVIEW_FILES = {
    "dual-reference-review.md", "fresh-worker-defect-closure.md", "local-review-api.md",
    "reopen-recovery.md", "self-visual-audit.md", "when-to-advance.md",
    "worker-pass-memory.md",
}
REQUIRED_GRAPH_FILES = {
    "SKILL.md",
    "references/INDEX.md",
    "references/foundation/line-economy.md",
    "references/foundation/reference-authority.md",
    "references/foundation/scope-and-precedence.md",
    "references/modes/croquis.md",
    "references/observation/visual-observation.md",
    "references/construction/gesture-and-masses.md",
    "references/description/descriptive-geometry.md",
    "references/figure/head-face-hair.md",
    "references/figure/legs-feet.md",
    "references/figure/clothing-folds.md",
    "references/props/attached-objects.md",
    "references/environment/ground-and-context.md",
    "references/review/residual-correction.md",
    "references/output/render-profile-and-replay.md",
    "references/api/public-surface.md",
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
    documents.extend(path for path in (PACKAGE / "references").rglob("*.md"))
    return sorted(set(documents))


def check_source() -> None:
    version_text = (PACKAGE / "src" / "img2drawing" / "_version.py").read_text()
    assert f'__version__ = "{VERSION}"' in version_text
    assert 'RELEASE_REVISION = "B17"' in version_text
    assert (ROOT / "LICENSE").read_bytes() == (PACKAGE / "LICENSE").read_bytes()
    pyproject = (PACKAGE / "pyproject.toml").read_text()
    assert '"numpy>=1.24"' in pyproject and '"Pillow>=10"' in pyproject
    assert "svgwrite" not in pyproject
    assert 'license-files = ["LICENSE"]' in pyproject
    workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text()
    assert "verify_vnext_b17.py" in workflow
    assert "validate_r23_release.py" not in workflow

    assert not (PACKAGE / "examples").exists(), "uncurated examples leaked into deployable skill"
    for name in CONTROL_PLANE_FILES:
        assert not (PACKAGE / name).exists(), f"control-plane file leaked into skill root: {name}"
    assert not (PACKAGE / "playbooks").exists(), "legacy playbooks leaked into deployable skill"
    assert not (PACKAGE / "references" / "stages").exists(), "legacy stage references leaked into deployable skill"
    for name in LEGACY_REVIEW_FILES:
        assert not (PACKAGE / "references" / "review" / name).exists(), f"legacy review doc leaked: {name}"
    for name in ("CONTRACT_FREEZE.json", "FREEZE.md", "MIGRATION.md", "RELEASE.md", "SUPPORT.md"):
        assert (RELEASE_RECORDS / name).is_file(), f"missing maintainer release record: {name}"
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


def _probe(python: Path, *, cwd: Path, env: dict[str, str]) -> dict[str, object]:
    code = (
        "import json,img2drawing; from img2drawing._version import PUBLIC_API,RELEASE_REVISION; "
        "print(json.dumps({'version':img2drawing.__version__,'api':PUBLIC_API,"
        "'revision':RELEASE_REVISION,'exports':sorted(img2drawing.__all__),"
        "'file':img2drawing.__file__}))"
    )
    return json.loads(_run([str(python), "-c", code], cwd=cwd, env=env).strip())


def _scan_text(name: str, payload: bytes) -> None:
    if Path(name).suffix.lower() not in TEXT_SUFFIXES:
        return
    text = payload.decode("utf-8")
    forbidden = ("/home/", "/mnt/", "BEGIN PRIVATE KEY", "BEGIN OPENSSH PRIVATE KEY")
    for token in forbidden:
        assert token not in text, f"artifact contains local/secret token {token!r}: {name}"
    assert not re.search(r"AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{30,}", text), f"secret-like token: {name}"


def check_artifacts(work: Path) -> tuple[Path, Path]:
    dist = work / "dist"
    _run([sys.executable, "-m", "build", "--outdir", str(dist)], cwd=PACKAGE)
    wheel = next(dist.glob("*.whl"))
    sdist = next(dist.glob("*.tar.gz"))

    with zipfile.ZipFile(wheel) as archive:
        wheel_names = archive.namelist()
        for name in wheel_names:
            path = _safe_member(name)
            assert path.parts[0] == "img2drawing" or ".dist-info" in path.parts[0], name
            assert not FORBIDDEN_ARCHIVE_PARTS.intersection(path.parts), name
            _scan_text(name, archive.read(name))
        metadata_name = next(name for name in wheel_names if name.endswith(".dist-info/METADATA"))
        metadata = email.parser.Parser().parsestr(archive.read(metadata_name).decode())
        assert metadata["Version"] == VERSION
        runtime_requires = [
            value for value in metadata.get_all("Requires-Dist", []) if "extra ==" not in value
        ]
        assert any(value.lower().startswith("numpy>=") for value in runtime_requires)
        assert any(value.lower().startswith("pillow>=") for value in runtime_requires)
        assert len(runtime_requires) == 2
        assert any(name.endswith(".dist-info/licenses/LICENSE") for name in wheel_names)
        assert not any(
            name.endswith(".dist-info/licenses/NOTICE") or name.endswith(".dist-info/licenses/NOTICE.md")
            for name in wheel_names
        )

    with tarfile.open(sdist, "r:gz") as archive:
        members = archive.getmembers()
        names = [member.name for member in members]
        for member in members:
            path = _safe_member(member.name)
            assert member.isfile() or member.isdir(), f"unsupported archive member type: {member.name}"
            relative = path.parts[1:]
            assert not FORBIDDEN_ARCHIVE_PARTS.intersection(relative), member.name
            assert relative[:1] != ("playbooks",), member.name
            assert relative[:2] != ("references", "stages"), member.name
            if relative and relative[-1] in CONTROL_PLANE_FILES:
                raise AssertionError(f"control-plane file shipped in sdist: {member.name}")
            if len(relative) >= 3 and relative[:2] == ("references", "review") and relative[-1] in LEGACY_REVIEW_FILES:
                raise AssertionError(f"legacy review file shipped in sdist: {member.name}")
            if member.isfile():
                stream = archive.extractfile(member)
                assert stream is not None
                _scan_text(member.name, stream.read())
        relative_names = {"/".join(PurePosixPath(name).parts[1:]) for name in names}
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
    dependency_locations = json.loads(
        _run(
            [
                str(python), "-c",
                "import json,numpy,PIL; print(json.dumps({'numpy':numpy.__file__,'PIL':PIL.__file__}))",
            ],
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
    assert installed["version"] == VERSION and installed["api"] == PUBLIC_API
    assert str(installed["file"]).startswith(str(environment)), installed["file"]
    assert "DrawingSession" in installed["exports"] and "DrawingRun" not in installed["exports"]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-only", action="store_true")
    args = parser.parse_args()
    check_source()
    if args.source_only:
        print("B17 source/docs/CI audit: PASS")
        return
    with tempfile.TemporaryDirectory(prefix="img2drawing-b17-") as temporary:
        work = Path(temporary)
        wheel, _sdist = check_artifacts(work)
        check_clean_install(work, wheel)
    print("B17 package/API/clean-install/instruction-graph/supply-chain audit: PASS")


if __name__ == "__main__":
    main()
