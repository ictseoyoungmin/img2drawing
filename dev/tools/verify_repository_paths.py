"""Check repository text for machine-local absolute filesystem paths."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

# Detect common machine-local roots without embedding any complete host path.
# Repository-relative paths do not begin with a slash and are allowed.
_MACHINE_ROOTS = ("home", "mnt", "tmp", "Users", "root", "workspace", "var", "opt")
MACHINE_PATH = re.compile(
    r"(?<![A-Za-z0-9_.-])/(?:"
    + "|".join(_MACHINE_ROOTS)
    + r")/(?:[A-Za-z0-9_.-]+/)+[A-Za-z0-9_.-]+"
    r"|(?<![A-Za-z0-9_.-])[A-Za-z]:[\\/]"
)


def _is_binary(path: Path) -> bool:
    try:
        sample = path.read_bytes()[:4096]
    except OSError:
        return True
    return b"\x00" in sample


def _repository_files(root: Path):
    result = subprocess.run(
        ["git", "-C", str(root), "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        check=True,
        capture_output=True,
    )
    for raw_path in result.stdout.split(b"\0"):
        if not raw_path:
            continue
        path = root / raw_path.decode("utf-8")
        if path.is_file():
            yield path


def _text_files(root: Path = ROOT):
    for path in _repository_files(root):
        if _is_binary(path):
            continue
        yield path


def find_machine_path_leaks(root: Path = ROOT) -> list[tuple[Path, int]]:
    leaks: list[tuple[Path, int]] = []
    for path in _text_files(root):
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for line_number, line in enumerate(text.splitlines(), 1):
            if MACHINE_PATH.search(line):
                leaks.append((path.relative_to(root), line_number))
    return leaks


def check_json(root: Path = ROOT) -> list[tuple[Path, str]]:
    failures: list[tuple[Path, str]] = []
    for path in _repository_files(root):
        if path.suffix.lower() != ".json":
            continue
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            failures.append((path.relative_to(root), str(exc)))
    return failures


def check_python(root: Path = ROOT) -> list[tuple[Path, str]]:
    failures: list[tuple[Path, str]] = []
    for path in _repository_files(root):
        if path.suffix.lower() != ".py":
            continue
        try:
            compile(path.read_text(encoding="utf-8"), str(path), "exec")
        except (OSError, UnicodeDecodeError, SyntaxError) as exc:
            failures.append((path.relative_to(root), str(exc)))
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", dest="check_json_files")
    parser.add_argument("--python", action="store_true", dest="check_python_files")
    args = parser.parse_args()

    leaks = find_machine_path_leaks()
    if leaks:
        for path, line_number in leaks:
            print(f"{path}:{line_number}: machine-local path detected")
        print(f"REPOSITORY_PATH_SANITIZATION_FAIL ({len(leaks)} lines)")
        return 1
    print("REPOSITORY_PATH_SANITIZATION_PASS")

    if args.check_json_files:
        failures = check_json()
        if failures:
            for path, error in failures:
                print(f"{path}: {error}")
            print(f"REPOSITORY_JSON_PARSE_FAIL ({len(failures)} files)")
            return 1
        print("REPOSITORY_JSON_PARSE_PASS")

    if args.check_python_files:
        failures = check_python()
        if failures:
            for path, error in failures:
                print(f"{path}: {error}")
            print(f"REPOSITORY_PYTHON_COMPILE_FAIL ({len(failures)} files)")
            return 1
        print("REPOSITORY_PYTHON_COMPILE_PASS")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
