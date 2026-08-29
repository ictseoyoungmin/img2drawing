from __future__ import annotations

import json
import re
from pathlib import Path

from img2drawing.run import _resolve_checkpoint_paths


ROOT = Path(__file__).resolve().parents[2]
PUBLIC_RUN = ROOT / "dev" / "p1_reference_run"
MACHINE_PATH = re.compile(
    r"(?<![A-Za-z0-9_.-])/(?!/)(?:[A-Za-z0-9_.-]+/){2,}[A-Za-z0-9_.-]+"
    r"|(?<![A-Za-z0-9_.-])[A-Za-z]:[\\/]"
)


def test_public_reference_run_contains_no_machine_absolute_paths():
    leaks = []
    for path in PUBLIC_RUN.rglob("*"):
        if path.is_file() and path.suffix.lower() in {".json", ".md"}:
            matches = MACHINE_PATH.findall(path.read_text(encoding="utf-8"))
            if matches:
                leaks.append((str(path.relative_to(ROOT)), matches[:3]))
    assert leaks == []


def test_relative_checkpoint_paths_resolve_from_checkpoint_directory(tmp_path):
    checkpoint_dir = tmp_path / "run" / "session"
    checkpoint_dir.mkdir(parents=True)
    payload = {
        "init": {
            "reference_path": "../../subject.png",
            "output_dir": "..",
            "task_stage_targets": {"P1_gesture": "../../target.png"},
        },
        "local_reviews": {
            "one": {"comparisons": {"overview": "../reviews/overview.png"}},
        },
    }

    resolved = _resolve_checkpoint_paths(payload, base=checkpoint_dir)

    assert Path(resolved["init"]["reference_path"]).is_absolute()
    assert Path(resolved["init"]["output_dir"]) == checkpoint_dir.parent.resolve()
    assert Path(resolved["init"]["task_stage_targets"]["P1_gesture"]).is_absolute()
    assert Path(resolved["local_reviews"]["one"]["comparisons"]["overview"]).is_absolute()


def test_checkpoint_init_is_portable_after_public_build():
    checkpoint = PUBLIC_RUN / "run" / "session" / "checkpoint.json"
    data = json.loads(checkpoint.read_text(encoding="utf-8"))
    init = data["init"]

    assert not Path(init["reference_path"]).is_absolute()
    assert not Path(init["output_dir"]).is_absolute()
    assert all(not Path(path).is_absolute() for path in init["task_stage_targets"].values())
