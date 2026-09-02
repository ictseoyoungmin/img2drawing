#!/usr/bin/env python3
"""Audit B17 source, artifacts, clean install, and canonical examples.

This is a packaging/integration verifier. It deliberately makes no visual-quality claim.
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
VERSION = "0.6.0rc1"
PUBLIC_API = "DrawingSession/0.6.0-vnext"
TEXT_SUFFIXES = {".md", ".py", ".json", ".toml", ".txt", ".yml", ".yaml"}
FORBIDDEN_ARCHIVE_PARTS = {
    ".git", ".github", ".pytest_cache", ".unlazy", "__pycache__", "dev",
    "dogfood", "drawings", "showcase", "temp",
}


def _run(command: list[str], *, cwd: Path, env: dict[str, str] | None = None) -> str:
    completed = subprocess.run(
        command,
        cwd=cwd,
        env=env,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return completed.stdout


def _safe_member(name: str) -> PurePosixPath:
    path = PurePosixPath(name)
    if path.is_absolute() or ".." in path.parts or "" in path.parts:
        raise AssertionError(f"unsafe archive path: {name}")
    return path


def _canonical_docs() -> list[Path]:
    documents = [ROOT / "README.md"]
    documents.extend(PACKAGE.glob("*.md"))
    documents.extend(
        path for path in (PACKAGE / "references").rglob("*.md")
        if "stages" not in path.parts
        and path.name not in {
            "dual-reference-review.md", "fresh-worker-defect-closure.md",
            "local-review-api.md", "reopen-recovery.md", "self-visual-audit.md",
            "when-to-advance.md", "worker-pass-memory.md",
        }
    )
    documents.extend((PACKAGE / "examples" / name / "README.md") for name in ("observed", "subjectless"))
    return sorted(set(documents))


def check_source() -> None:
    version_text = (PACKAGE / "src" / "img2drawing" / "_version.py").read_text()
    assert f'__version__ = "{VERSION}"' in version_text
    assert 'RELEASE_REVISION = "B17"' in version_text
    assert (ROOT / "LICENSE").read_bytes() == (PACKAGE / "LICENSE").read_bytes()
    pyproject = (PACKAGE / "pyproject.toml").read_text()
    assert '"numpy>=1.24"' in pyproject and '"Pillow>=10"' in pyproject
    assert "svgwrite" not in pyproject
    workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text()
    assert "verify_vnext_b17.py" in workflow
    assert "validate_r23_release.py" not in workflow

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


def check_artifacts(work: Path) -> tuple[Path, Path, Path]:
    dist = work / "dist"
    _run(
        [sys.executable, "-m", "build", "--no-isolation", "--outdir", str(dist)],
        cwd=PACKAGE,
    )
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
            value for value in metadata.get_all("Requires-Dist", [])
            if "extra ==" not in value
        ]
        assert any(value.lower().startswith("numpy>=") for value in runtime_requires)
        assert any(value.lower().startswith("pillow>=") for value in runtime_requires)
        assert len(runtime_requires) == 2
        assert any(name.endswith(".dist-info/licenses/LICENSE") for name in wheel_names)
        assert any(name.endswith(".dist-info/licenses/NOTICE") for name in wheel_names)

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
            assert "full_body_croquis" not in relative and "p1_target.png" not in relative
            if member.isfile():
                stream = archive.extractfile(member)
                assert stream is not None
                _scan_text(member.name, stream.read())
        required = {
            "SKILL.md", "SUPPORT.md", "MIGRATION.md", "RELEASE.md",
            "references/reference-authority.md", "references/legacy-r23.md",
            "examples/mechanical_workflows.py", "examples/observed/run.py",
            "examples/subjectless/run.py",
        }
        relative_names = {"/".join(PurePosixPath(name).parts[1:]) for name in names}
        assert required.issubset(relative_names), sorted(required - relative_names)
        archive.extractall(work / "sdist")
    extracted = next((work / "sdist").iterdir())
    return wheel, sdist, extracted


def check_clean_install(work: Path, wheel: Path, extracted: Path) -> None:
    environment = work / "venv"
    # Debian's minimal Python may omit ensurepip. Build an isolated interpreter and
    # install the wheel into its own purelib with the invoking interpreter's pip.
    venv.EnvBuilder(with_pip=False, system_site_packages=True).create(environment)
    python = environment / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    clean_env = os.environ.copy()
    clean_env.pop("PYTHONPATH", None)
    purelib = _run(
        [str(python), "-c", "import sysconfig; print(sysconfig.get_paths()['purelib'])"],
        cwd=work,
        env=clean_env,
    ).strip()
    _run(
        [sys.executable, "-m", "pip", "install", "--no-deps", "--target", purelib, str(wheel)],
        cwd=work,
        env=clean_env,
    )
    _run([str(python), "-c", "import numpy, PIL"], cwd=work, env=clean_env)

    source_env = os.environ.copy()
    source_env["PYTHONPATH"] = str(PACKAGE / "src")
    source = _probe(Path(sys.executable), cwd=work, env=source_env)
    installed = _probe(python, cwd=work, env=clean_env)
    for field in ("version", "api", "revision", "exports"):
        assert source[field] == installed[field], f"source/install {field} mismatch"
    assert installed["version"] == VERSION and installed["api"] == PUBLIC_API
    assert str(installed["file"]).startswith(str(environment)), installed["file"]
    assert "DrawingSession" in installed["exports"] and "DrawingRun" not in installed["exports"]

    for example in ("observed", "subjectless"):
        output = work / f"{example}-output"
        result = _run(
            [str(python), str(extracted / "examples" / example / "run.py"), "--output", str(output)],
            cwd=work,
            env=clean_env,
        )
        payload = json.loads(result)
        assert payload["version"] == VERSION
        assert payload["finish_current_after_resume"] is True
        assert (output / "canonical_final.png").is_file()
        assert (output / "replay" / "timelapse.gif").is_file()


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
        wheel, _sdist, extracted = check_artifacts(work)
        check_clean_install(work, wheel, extracted)
    print("B17 package/API/clean-install/examples/supply-chain audit: PASS")


if __name__ == "__main__":
    main()
