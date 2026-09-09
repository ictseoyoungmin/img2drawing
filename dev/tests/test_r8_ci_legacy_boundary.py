from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _imports_retired_streaming_backend(path: Path) -> bool:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "img2drawing.provenance.streaming" or alias.name.startswith("img2drawing.provenance.streaming."):
                    return True
        elif isinstance(node, ast.ImportFrom):
            if node.module == "img2drawing.provenance.streaming":
                return True
            if node.module == "img2drawing.provenance":
                if any(alias.name == "export_timelapse_streaming" for alias in node.names):
                    return True
    return False


def test_active_dev_tests_do_not_import_retired_streaming_backend() -> None:
    offenders = []
    for path in sorted((ROOT / "dev" / "tests").glob("test_*.py")):
        if path.name == "test_r8_ci_legacy_boundary.py":
            continue
        if _imports_retired_streaming_backend(path):
            offenders.append(path.relative_to(ROOT).as_posix())
    assert offenders == []
