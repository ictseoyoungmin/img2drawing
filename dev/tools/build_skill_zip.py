"""Build the distributable skill zip from skills/img2drawing without build residue.

A prior manual zip picked up local, gitignored ``__pycache__``/``*.egg-info``
directories left behind by retired R23 modules, shipping bytecode with no
matching source under the interpreter that built it. This script excludes
that residue by construction instead of relying on someone remembering to.
"""

from __future__ import annotations

import argparse
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACKAGE_DIR = ROOT / "skills" / "img2drawing"


def _is_excluded(relative_parts: tuple[str, ...], suffix: str) -> bool:
    if suffix == ".pyc":
        return True
    return any(part == "__pycache__" or part.endswith(".egg-info") for part in relative_parts)


def build_skill_zip(package_dir: Path, out_path: Path) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(package_dir.rglob("*")):
            if path.is_dir():
                continue
            relative = path.relative_to(package_dir.parent)
            if _is_excluded(relative.parts, path.suffix):
                continue
            zf.write(path, relative.as_posix())
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
