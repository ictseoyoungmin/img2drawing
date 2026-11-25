from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path


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
    # Preserve the original full P1 portability check after archiving its retired run.
    frozen = '1127e673e05799040e802e9fd3a887d7781f2941'
    names = subprocess.check_output(['git','ls-tree','-r','--name-only','-z',frozen,'dev/p1_reference_run'], cwd=ROOT).decode().split('\0')
    archived_leaks = []
    for name in names:
        if name.endswith(('.md','.json')):
            content = subprocess.check_output(['git','show',f'{frozen}:{name}'], cwd=ROOT).decode('utf-8')
            if MACHINE_PATH.findall(content):
                archived_leaks.append(name)
    assert not archived_leaks, archived_leaks


def test_frozen_public_checkpoint_init_remains_portable_evidence():
    """Historical public evidence stays portable without importing its retired runtime."""

    checkpoint = PUBLIC_RUN / "run" / "session" / "checkpoint.json"
    data = json.loads(checkpoint.read_text(encoding="utf-8"))
    init = data["init"]

    assert not Path(init["reference_path"]).is_absolute()
    assert not Path(init["output_dir"]).is_absolute()
    assert all(not Path(path).is_absolute() for path in init["task_stage_targets"].values())
