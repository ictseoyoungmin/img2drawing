"""Read retired developer evidence from its immutable Git commit, not the checkout.

No history is rewritten. Only explicitly retired paths can be retrieved. A
temporary snapshot is for legacy validators needing files; it is never installed
in the skill or restored in the working tree.
"""
from __future__ import annotations

from contextlib import contextmanager
from io import BytesIO
from pathlib import Path, PurePosixPath
import subprocess
import tarfile
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[2]
RETIRED_SOURCE = "1895e0b1ff5d38e27cb66a7fb5e5e25e36bc412b"
RETIRED_TREES = (
    "dev/dogfood/croquis-sniper-girl",
    "dev/dogfood/target-subject",
    "dev/dogfood/vnext-b05",
    "dev/evidence/material-integration",
    "dev/evidence/fresh-worker",
    "dev/evidence/vnext",
    "dev/release/r23",
)
RETIRED_SCRIPTS = (
    "dev/tools/build_r23_release.py",
    "dev/tools/build_material_quality_run.py",
    "dev/tools/run_fresh_worker_generalization.py",
    "dev/release/validate_r22_release.py",
)
RETIRED_PATHS = tuple(sorted(RETIRED_TREES + RETIRED_SCRIPTS))


def is_retired(path: str) -> bool:
    return path in RETIRED_SCRIPTS or any(
        path == prefix or path.startswith(prefix + "/") for prefix in RETIRED_TREES
    )


def read_archived_blob(path: str, *, root: Path = ROOT) -> bytes:
    p = PurePosixPath(path)
    if p.is_absolute() or ".." in p.parts or p.as_posix() != path or not is_retired(path):
        raise ValueError("path is not a declared retired evidence file")
    return subprocess.check_output(["git", "show", f"{RETIRED_SOURCE}:{path}"], cwd=root)


@contextmanager
def archived_snapshot(prefix: str, *, root: Path = ROOT):
    """Materialize one pinned historical subtree outside the repository.

    Used only by historical checks that need actual files. The Git archive is
    read from the pinned commit, not from the current branch. Reject links and
    traversal; retain the original relative paths for legacy reports.
    """
    if prefix not in RETIRED_TREES:
        raise ValueError("unknown retired evidence directory")
    payload = subprocess.check_output(
        ["git", "archive", "--format=tar", RETIRED_SOURCE, prefix], cwd=root
    )
    with TemporaryDirectory(prefix="i2d-archive-") as folder:
        destination = Path(folder)
        seen = set()
        with tarfile.open(fileobj=BytesIO(payload), mode="r:") as archive:
            for member in archive:
                if member.isdir():
                    continue
                path = PurePosixPath(member.name)
                if (not member.isfile() or path.is_absolute() or ".." in path.parts
                        or not path.as_posix().startswith(prefix + "/")
                        or path in seen):
                    raise ValueError("unexpected entry in retired evidence archive")
                seen.add(path)
                target = destination.joinpath(*path.parts)
                target.parent.mkdir(parents=True, exist_ok=True)
                fileobj = archive.extractfile(member)
                if fileobj is None:
                    raise ValueError("missing archived file content")
                with fileobj:
                    target.write_bytes(fileobj.read())
        if not seen:
            raise ValueError("empty retired evidence archive")
        yield destination
