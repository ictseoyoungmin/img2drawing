"""Build the distributable skill zip from skills/img2drawing without local residue.

The skill archive is a source artifact, not a snapshot of a developer checkout.  Local
Python bytecode, build products, virtual environments, test caches, and editor/OS residue
must never become part of the published skill merely because they happen to exist under the
package directory.
"""

from __future__ import annotations

import argparse
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACKAGE_DIR = ROOT / "skills" / "img2drawing"

_EXCLUDED_DIR_NAMES = {
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".tox",
    ".nox",
    ".venv",
    "venv",
    "build",
    "dist",
}
_EXCLUDED_FILENAMES = {".DS_Store", ".coverage"}
_EXCLUDED_SUFFIXES = {".pyc", ".pyo"}


def _is_excluded(relative: Path) -> bool:
    parts = relative.parts
    if any(part in _EXCLUDED_DIR_NAMES for part in parts):
        return True
    if any(part.endswith(".egg-info") or part.endswith(".dist-info") for part in parts):
        return True
    if relative.name in _EXCLUDED_FILENAMES or relative.name.startswith(".coverage."):
        return True
    return relative.suffix.lower() in _EXCLUDED_SUFFIXES


def build_skill_zip(package_dir: Path, out_path: Path) -> Path:
    package_dir = Path(package_dir).resolve()
    out_path = Path(out_path).resolve()
    if not package_dir.is_dir():
        raise FileNotFoundError(package_dir)
    try:
        out_path.relative_to(package_dir)
    except ValueError:
        pass
    else:
        raise ValueError("skill zip output must live outside the package directory")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(package_dir.rglob("*")):
            if not path.is_file():
                continue
            archive_path = path.relative_to(package_dir.parent)
            package_relative = path.relative_to(package_dir)
            if _is_excluded(package_relative):
                continue
            zf.write(path, archive_path.as_posix())
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package-dir", type=Path, default=PACKAGE_DIR)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = build_skill_zip(args.package_dir, args.out)
    print(result)


if __name__ == "__main__":
    main()
