from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACKAGE_SRC = ROOT / "skills" / "img2drawing" / "src"
LEGACY_RUNTIME_ROOTS = (
    "img2drawing.run",
    "img2drawing.stages",
    "img2drawing.exemplar",
    "img2drawing.review",
    "img2drawing.registration",
)


def _fresh_python(code: str) -> dict[str, object]:
    env = dict(os.environ)
    env["PYTHONPATH"] = str(PACKAGE_SRC)
    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def test_canonical_root_and_drawing_session_do_not_activate_r23_cluster() -> None:
    payload = _fresh_python(
        """
import json, sys
import img2drawing
from img2drawing import DrawingSession
roots = (
    'img2drawing.run', 'img2drawing.stages', 'img2drawing.exemplar',
    'img2drawing.review', 'img2drawing.registration',
)
def loaded(root):
    return any(name == root or name.startswith(root + '.') for name in sys.modules)
print(json.dumps({
    'drawing_session_module': DrawingSession.__module__,
    'legacy_loaded': {root: loaded(root) for root in roots},
}))
"""
    )
    assert payload["drawing_session_module"] == "img2drawing.vnext.session"
    assert not any(payload["legacy_loaded"].values())


def test_current_inspection_owns_registration_without_loading_historical_package() -> None:
    payload = _fresh_python(
        """
import json, sys
from img2drawing.inspection import Registration
print(json.dumps({
    'registration_module': Registration.__module__,
    'historical_registration_loaded': any(
        name == 'img2drawing.registration' or name.startswith('img2drawing.registration.')
        for name in sys.modules
    ),
}))
"""
    )
    assert str(payload["registration_module"]).startswith("img2drawing.inspection")
    assert payload["historical_registration_loaded"] is False


def test_retired_legacy_namespace_is_not_installable_or_root_reachable() -> None:
    payload = _fresh_python(
        """
import json, importlib.util, img2drawing, sys
legacy_spec = importlib.util.find_spec('img2drawing.legacy')
try:
    img2drawing.DrawingRun
except AttributeError:
    drawing_run = 'absent'
else:
    drawing_run = 'present'
print(json.dumps({
    'legacy_spec': None if legacy_spec is None else legacy_spec.name,
    'drawing_run': drawing_run,
    'legacy_loaded': any(name == 'img2drawing.legacy' or name.startswith('img2drawing.legacy.') for name in sys.modules),
}))
"""
    )
    assert payload["legacy_spec"] is None
    assert payload["drawing_run"] == "absent"
    assert payload["legacy_loaded"] is False


def test_canonical_session_source_has_no_direct_legacy_cluster_imports() -> None:
    source = (
        PACKAGE_SRC / "img2drawing" / "vnext" / "session.py"
    ).read_text(encoding="utf-8")
    for forbidden in (
        "from ..stages",
        "from ..exemplar",
        "from ..review",
        "from ..registration",
        "from ..run",
        "import img2drawing.stages",
        "import img2drawing.exemplar",
        "import img2drawing.review",
        "import img2drawing.registration",
        "import img2drawing.run",
    ):
        assert forbidden not in source


def test_a3_legacy_runtime_paths_are_not_canonical_root_exports() -> None:
    import img2drawing

    assert "DrawingSession" in img2drawing.__all__
    for name in ("DrawingRun", "StageContract", "StagePassMemory", "RegistrationGraph"):
        assert name not in img2drawing.__all__
