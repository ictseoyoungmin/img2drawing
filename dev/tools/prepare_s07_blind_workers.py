#!/usr/bin/env python3
"""Seal separate S07 fresh-worker input packets; never draw or judge images.

Only the evaluator holds the medium mapping. Callers verify package provenance;
executors enforce the worker read policy without prior solutions or evaluator notes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import secrets
import shutil
import struct
import tempfile
import zipfile

SCHEMA = "img2drawing.v1.4.s07.blind_pair.v1"
POLICIES = {
    "graphite": "Use the supplied stable graphite runtime and graphite tools only. Do not use mixed-media features.",
    "mixed": "Use the supplied candidate runtime, explicit ink/white/area/tone where justified, and the supported DrawingSession API.",
}
ALLOWED = frozenset({"reference.png", "skill.zip", "goal.md", "budget.json", "worker.json"})
SKILL_READS = ("img2drawing/SKILL.md", "img2drawing/README.txt", "img2drawing/references/**/*.md")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def png_size(path: Path) -> tuple[int, int]:
    with path.open("rb") as fh:
        header = fh.read(24)
    if len(header) != 24 or header[:8] != b"\x89PNG\r\n\x1a\n" or header[8:16] != b"\x00\x00\x00\rIHDR":
        raise ValueError("reference must be a PNG with a valid IHDR")
    w, h = struct.unpack(">II", header[16:24])
    if not (1 <= w <= 16384 and 1 <= h <= 16384):
        raise ValueError("invalid PNG dimensions")
    return w, h


def checked_archive(path: Path, suffix: str) -> None:
    if not path.is_file() or path.suffix.lower() != suffix:
        raise ValueError(f"expected an existing {suffix} file: {path}")
    if suffix == ".whl" and not re.fullmatch(
            r"[\w.]+-[\w.!+]+(?:-\d[\w.]*)?-[\w.]+-[\w.]+-[\w.]+\.whl", path.name, re.ASCII):
        raise ValueError("wheel needs a safe distribution-version-tags filename")
    with zipfile.ZipFile(path) as zf:
        names = zf.namelist()
        if not names:
            raise ValueError("empty archive")
        for name in names:
            item = PurePosixPath(name)
            if not item.parts or name.startswith("/") or "\\" in name or ".." in item.parts:
                raise ValueError("archive contains unsafe path")
        if suffix == ".zip" and not any(n == "img2drawing/SKILL.md" for n in names):
            raise ValueError("skill archive has no root img2drawing/SKILL.md")
        if suffix == ".whl" and not any(n.endswith(".dist-info/METADATA") for n in names):
            raise ValueError("wheel has no .dist-info/METADATA")


def checked_budget(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or set(value) != {"canvas", "supersample", "max_actions", "max_wall_sec", "worker_model", "max_tokens"}:
        raise ValueError("budget needs canvas, supersample, max_actions, max_wall_sec, worker_model, max_tokens")
    canvas = value["canvas"]
    if not isinstance(canvas, list) or len(canvas) != 2 or any(type(x) is not int or not 64 <= x <= 8192 for x in canvas):
        raise ValueError("invalid canvas budget")
    if type(value["supersample"]) is not int or value["supersample"] not in (1, 2, 4, 8):
        raise ValueError("invalid supersample")
    if type(value["max_actions"]) is not int or not 1 <= value["max_actions"] <= 100000:
        raise ValueError("invalid max_actions")
    if type(value["max_wall_sec"]) is not int or not 1 <= value["max_wall_sec"] <= 86400:
        raise ValueError("invalid max_wall_sec")
    if not isinstance(value["worker_model"], str) or not value["worker_model"].strip() or len(value["worker_model"]) > 128:
        raise ValueError("invalid worker_model")
    if type(value["max_tokens"]) is not int or not 1 <= value["max_tokens"] <= 10_000_000:
        raise ValueError("invalid max_tokens")
    return value


def _seal_file(folder: Path, name: str, source: Path, expected_sha: str) -> str:
    shutil.copyfile(source, folder / name)
    digest = sha256(folder / name)
    if digest != expected_sha:
        raise ValueError("input changed while sealing worker packet")
    return digest


def prepare(*, reference: Path, goal_file: Path, budget_file: Path,
            graphite_skill: Path, graphite_wheel: Path,
            mixed_skill: Path, mixed_wheel: Path, out_dir: Path,
            expected_graphite_wheel_sha: str, expected_mixed_wheel_sha: str) -> dict:
    sources = (reference, goal_file, budget_file, graphite_skill, graphite_wheel, mixed_skill, mixed_wheel)
    if any(not p.is_file() for p in sources):
        raise FileNotFoundError("all reference, goal, budget, skill and runtime files must exist")
    dimensions = png_size(reference)
    goal = goal_file.read_text(encoding="utf-8")
    if not goal.strip():
        raise ValueError("goal must be nonempty")
    budget = checked_budget(budget_file)
    for archive in (graphite_skill, mixed_skill):
        checked_archive(archive, ".zip")
    for archive in (graphite_wheel, mixed_wheel):
        checked_archive(archive, ".whl")
    wheel_hashes = {}
    for runtime, expected in ((graphite_wheel, expected_graphite_wheel_sha), (mixed_wheel, expected_mixed_wheel_sha)):
        if len(expected) != 64 or any(c not in "0123456789abcdef" for c in expected.lower()) or sha256(runtime) != expected.lower():
            raise ValueError("wheel SHA-256 does not match pinned expectation")
        wheel_hashes[runtime] = expected.lower()
    if wheel_hashes[graphite_wheel] == wheel_hashes[mixed_wheel]:
        raise ValueError("worker runtimes must be distinct")
    out_dir = out_dir.absolute()
    if out_dir.exists() or out_dir.is_symlink():
        raise FileExistsError("will not overwrite an existing S07 output")
    out_dir.parent.mkdir(parents=True, exist_ok=True)
    codes = [secrets.token_hex(8), secrets.token_hex(8)]
    if codes[0] == codes[1]:
        raise RuntimeError("opaque worker code collision")
    # The assignment is evaluator-only; order is randomized, not fixed A=old.
    choices = ("graphite", "mixed") if secrets.randbelow(2) == 0 else ("mixed", "graphite")
    assignment = dict(zip(codes, choices))
    ref_hash = sha256(reference)
    skill_hashes = {path: sha256(path) for path in (graphite_skill, mixed_skill)}
    base_goal_hash = sha256(goal_file)
    result = {"schema": SCHEMA, "status": "PREPARED_NOT_RUN", "worker_codes": codes,
              "reference_sha256": ref_hash, "shared_budget": budget}
    # Validate and stage off-path. copytree reserves a new destination exclusively;
    # copying is not atomic, so consumers wait for successful prepare completion.
    with tempfile.TemporaryDirectory(prefix=".s07-staging-", dir=out_dir.parent) as tmp:
        root = Path(tmp)
        workers = root / "workers"
        workers.mkdir()
        evaluator_assignments = []
        for code, medium in assignment.items():
            worker_dir = workers / code
            worker_dir.mkdir()
            skill = graphite_skill if medium == "graphite" else mixed_skill
            runtime = graphite_wheel if medium == "graphite" else mixed_wheel
            allowed = ALLOWED | {runtime.name}
            ref_copy = _seal_file(worker_dir, "reference.png", reference, ref_hash)
            skill_hash = _seal_file(worker_dir, "skill.zip", skill, skill_hashes[skill])
            runtime_hash = _seal_file(worker_dir, runtime.name, runtime, wheel_hashes[runtime])
            (worker_dir / "goal.md").write_text(goal.rstrip() + "\n\n" + POLICIES[medium] + "\n", encoding="utf-8")
            (worker_dir / "budget.json").write_text(json.dumps(budget, sort_keys=True, indent=2) + "\n", encoding="utf-8")
            worker = {"schema": SCHEMA, "worker_code": code,
                      "allowed_inputs": sorted(allowed),
                      "allowed_skill_reads": list(SKILL_READS),
                      "runtime_filename": runtime.name,
                      "runtime_access": "Install wheel and use public API/discovery; do not read implementation source.",
                      "forbidden_inputs": ["repository", "implementation_source", "examples", "past_runs", "prior_strokes", "answer_geometry", "evaluator_notes"],
                      "reference_sha256": ref_copy, "reference_dimensions": dimensions,
                      "shared_goal_sha256": base_goal_hash,
                      "budget_sha256": sha256(worker_dir / "budget.json"),
                      "skill_sha256": skill_hash, "runtime_sha256": runtime_hash,
                      "required_outputs": ["full action history", "current final PNG", "end-to-end GIF", "mechanical QA"],
                      "visual_verdict": "REVIEWER_ONLY_NOT_RUN"}
            (worker_dir / "worker.json").write_text(json.dumps(worker, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            if {f.name for f in worker_dir.iterdir()} != allowed:
                raise RuntimeError("unexpected worker packet file")
            evaluator_assignments.append({"worker_code": code, "medium": medium,
                                          "skill_sha256": skill_hash, "runtime_sha256": runtime_hash})
        # Reviewers must receive anonymized outputs only; not this mapping.
        evaluator = {"schema": SCHEMA, "status": "PREPARED_NOT_RUN", "assignments": evaluator_assignments,
                     "shared_reference_sha256": ref_hash, "shared_goal_sha256": base_goal_hash,
                     "shared_budget": budget,
                     "blind_review": ["whole composition", "face and expression", "hair mass and clumps",
                                      "hand and finger contact", "occlusion and silhouette",
                                      "black-white hierarchy", "tone and white ink intent"],
                     "decision": "NOT_RUN", "warning": "Never send this file to workers or blinded reviewers."}
        secret = root / "evaluator_only.json"
        fd = os.open(secret, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(evaluator, f, indent=2, ensure_ascii=False)
            f.write("\n")
        shutil.copytree(root, out_dir)
    return {**result, "output": str(out_dir)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("reference", "goal-file", "budget-file", "graphite-skill", "graphite-wheel",
                 "mixed-skill", "mixed-wheel", "out-dir"):
        parser.add_argument("--" + name, required=True, type=Path)
    for name in ("expected-graphite-wheel-sha", "expected-mixed-wheel-sha"):
        parser.add_argument("--" + name, required=True)
    args = vars(parser.parse_args())
    print(json.dumps(prepare(**args), indent=2))


if __name__ == "__main__":
    main()
