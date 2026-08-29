#!/usr/bin/env python3
"""Prepare the minimal input envelope for an external strict fresh worker.

The output deliberately contains only a skill ZIP, a new subject and a user
goal.  It does not run a worker; a returned run must be produced in a separate
session and verified with ``verify_strict_fresh_worker.py``.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / "skills/img2drawing"


def _sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def _relative(path: Path, base: Path, label: str) -> str:
    path = path.resolve()
    try:
        return path.relative_to(base.resolve()).as_posix()
    except ValueError as exc:
        raise ValueError(f"{label} must be inside the output directory") from exc


def prepare(
    out_dir: Path,
    *,
    subject: Path,
    user_goal: str,
    worker_session_id: str,
    evaluator_session_id: str,
) -> Path:
    out_dir = out_dir.resolve()
    subject = subject.resolve()
    if out_dir.exists() and any(out_dir.iterdir()):
        raise FileExistsError(f"refusing to overwrite non-empty strict input directory: {out_dir}")
    if not subject.is_file():
        raise FileNotFoundError(subject)
    if not str(user_goal).strip():
        raise ValueError("user_goal must be non-empty")
    if not str(worker_session_id).strip() or not str(evaluator_session_id).strip():
        raise ValueError("worker and evaluator session IDs must be non-empty")
    if worker_session_id == evaluator_session_id:
        raise ValueError("worker and evaluator session IDs must be distinct")

    package_dir = out_dir / "input"
    package_dir.mkdir(parents=True, exist_ok=True)
    package = package_dir / "img2drawing-skill-r23-candidate.zip"
    files = []
    # Example subjects/targets are dogfood material, not part of a strict
    # fresh-worker package.  Excluding the whole examples tree prevents the
    # worker from receiving a duplicate or coordinate-bearing reference in
    # addition to the explicitly supplied subject.
    excluded = {"dist", "build", "examples", "__pycache__", ".pytest_cache"}
    for path in sorted(SKILL.rglob("*")):
        if not path.is_file():
            continue
        parts = set(path.relative_to(SKILL).parts)
        if parts & excluded or any(part.endswith(".egg-info") for part in parts):
            continue
        files.append(path)
    with zipfile.ZipFile(package, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in files:
            archive.write(path, Path("img2drawing") / path.relative_to(SKILL))

    subject_copy = package_dir / "subject.png"
    shutil.copyfile(subject, subject_copy)
    envelope = {
        "schema": "img2drawing.strict_fresh_worker_input.v1",
        "allowed_inputs": ["package", "subject", "user_goal"],
        "forbidden_context": ["repository", "material_sources", "dogfood_history", "prior_action_ids", "prior_coordinates"],
        "package": {"path": _relative(package, out_dir, "package"), "sha256": _sha(package)},
        "subject": {"path": _relative(subject_copy, out_dir, "subject"), "sha256": _sha(subject_copy)},
        "user_goal": str(user_goal).strip(),
        "worker_session_id": str(worker_session_id).strip(),
        "evaluator_session_id": str(evaluator_session_id).strip(),
    }
    (out_dir / "input_envelope.json").write_text(
        json.dumps(envelope, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8"
    )
    return out_dir / "input_envelope.json"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--subject", required=True, type=Path)
    parser.add_argument("--user-goal", required=True)
    parser.add_argument("--worker-session-id", required=True)
    parser.add_argument("--evaluator-session-id", required=True)
    args = parser.parse_args()
    print(prepare(
        args.out_dir,
        subject=args.subject,
        user_goal=args.user_goal,
        worker_session_id=args.worker_session_id,
        evaluator_session_id=args.evaluator_session_id,
    ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
