#!/usr/bin/env python3
"""Developer-only matched-input evidence contract; never an artistic judge."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from pathlib import Path

SCHEMA = "img2drawing.constructive_qa.case.v1"
RUN_SCHEMA = "img2drawing.constructive_qa.run.v1"
CLASSES = ("portrait", "full_body", "hand_object", "hair", "still_life", "environment")
ARMS = ("v1.2.0", "v1.2.1", "v1.3.0")
BASELINES = {
    "v1.2.0": "2816696a96057e1792be9b98c39c2ef8c2264e69",
    "v1.2.1": "1127e673e05799040e802e9fd3a887d7781f2941",
}
ARTIFACTS = ("session", "final_png", "timelapse_gif", "comparison", "review")
HEX = re.compile(r"^[0-9a-f]{64}$")
GIT_SHA = re.compile(r"^[0-9a-f]{40}$")


def canonical_digest(value):
    data = json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def file_digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def require_keys(value, expected, label):
    if not isinstance(value, dict) or set(value) != set(expected):
        raise ValueError(f"{label}: expected exactly {sorted(expected)}")


def nonempty(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label}: nonempty string required")


def validate_spec(spec):
    require_keys(spec, ("case_id", "subject_class", "user_request", "intent",
                        "worker", "budget", "canvas"), "case spec")
    nonempty(spec["case_id"], "case_id")
    if spec["subject_class"] not in CLASSES:
        raise ValueError("unknown subject class")
    nonempty(spec["user_request"], "user_request")
    intent = spec["intent"]
    require_keys(intent, ("reference_mode", "drawing_mode", "finish_intent",
                          "style_profile"), "intent")
    if intent["reference_mode"] != "observed":
        raise ValueError("matched reference comparison requires observed intent")
    if intent["drawing_mode"] not in ("croquis", "figure_drawing", "tonal_study",
                                     "line_study", "free_draw"):
        raise ValueError("invalid drawing mode")
    if intent["finish_intent"] not in ("pose", "subject", "form_light", "expressive"):
        raise ValueError("invalid finish intent")
    nonempty(intent["style_profile"], "style_profile")
    worker = spec["worker"]
    require_keys(worker, ("model", "configuration"), "worker")
    nonempty(worker["model"], "worker.model")
    if not isinstance(worker["configuration"], dict):
        raise ValueError("worker.configuration must be a JSON object")
    budget = spec["budget"]
    require_keys(budget, ("max_actions", "max_wall_seconds", "max_tokens"), "budget")
    for key, value in budget.items():
        if key == "max_tokens" and value is None:
            continue  # Explicitly unmetered, not zero cost.
        if type(value) is not int or value <= 0:
            raise ValueError(f"budget.{key}: positive integer required")
    canvas = spec["canvas"]
    require_keys(canvas, ("width", "height"), "canvas")
    if any(type(v) is not int or v <= 0 for v in canvas.values()):
        raise ValueError("canvas dimensions must be positive integers")
    canonical_digest(spec)  # reject non-finite JSON values


def seal_case(spec, reference):
    validate_spec(spec)
    reference = Path(reference)
    body = {"schema": SCHEMA, "spec": spec,
            "reference": {"sha256": file_digest(reference),
                          "bytes": reference.stat().st_size}}
    # Return a detached JSON snapshot, not a view into caller-owned mutable data.
    body = json.loads(json.dumps(body, allow_nan=False))
    return {**body, "case_digest": canonical_digest(body)}


def validate_case(case, reference):
    require_keys(case, ("schema", "spec", "reference", "case_digest"), "sealed case")
    if case["schema"] != SCHEMA:
        raise ValueError("unsupported case schema")
    expected = seal_case(case["spec"], reference)
    if case != expected:
        raise ValueError("sealed case or reference mismatch")
    return case["case_digest"]


def artifact_path(root, name):
    nonempty(name, "artifact name")
    root = Path(root).resolve()
    rel = Path(name)
    if rel.is_absolute() or ".." in rel.parts:
        raise ValueError("artifact path escapes evidence root")
    path = (root / rel).resolve()
    if not path.is_relative_to(root) or not path.is_file():
        raise ValueError("artifact missing or outside evidence root")
    return path


def validate_run(run, case, root):
    require_keys(run, ("schema", "case_digest", "arm", "commit", "worker_run_id",
                       "freshness", "usage", "artifacts"), "run")
    if run["schema"] != RUN_SCHEMA or run["case_digest"] != case["case_digest"]:
        raise ValueError("run is not bound to this case")
    if run["arm"] not in ARMS or not isinstance(run["commit"], str) or not GIT_SHA.fullmatch(run["commit"]):
        raise ValueError("invalid version arm or commit")
    if run["arm"] in BASELINES and run["commit"] != BASELINES[run["arm"]]:
        raise ValueError("baseline commit drift")
    nonempty(run["worker_run_id"], "worker_run_id")
    require_keys(run["freshness"], ("status", "evidence"), "freshness")
    if run["freshness"]["status"] not in ("verified", "unverified", "not_fresh"):
        raise ValueError("invalid freshness state")
    nonempty(run["freshness"]["evidence"], "freshness evidence")
    usage = run["usage"]
    require_keys(usage, ("actions", "wall_seconds", "tokens"), "usage")
    budget = case["spec"]["budget"]
    for key, limit_key in (("actions", "max_actions"), ("wall_seconds", "max_wall_seconds"), ("tokens", "max_tokens")):
        value, limit = usage[key], budget[limit_key]
        if key == "tokens" and value is None and limit is None:
            continue
        valid = (type(value) in (int, float) and math.isfinite(value) and value >= 0)
        if not valid or (key != "wall_seconds" and type(value) is not int):
            raise ValueError(f"invalid usage: {key}")
        if limit is not None and value > limit:
            raise ValueError(f"budget exceeded: {key}")
    require_keys(run["artifacts"], ARTIFACTS, "artifacts")
    paths = set()
    for key in ARTIFACTS:
        entry = run["artifacts"][key]
        require_keys(entry, ("file", "sha256"), key)
        if not isinstance(entry["sha256"], str) or not HEX.fullmatch(entry["sha256"]):
            raise ValueError(f"invalid digest: {key}")
        path = artifact_path(root, entry["file"])
        if path in paths or file_digest(path) != entry["sha256"]:
            raise ValueError(f"duplicate artifact or digest mismatch: {key}")
        paths.add(path)


def compare_pair(case, reference, left, left_root, right, right_root):
    validate_case(case, reference)
    validate_run(left, case, left_root)
    validate_run(right, case, right_root)
    if left["arm"] == right["arm"] or left["commit"] == right["commit"]:
        raise ValueError("comparison requires distinct arms and commits")
    if left["worker_run_id"] == right["worker_run_id"]:
        raise ValueError("comparison requires separate worker runs")
    return {
        "case_digest": case["case_digest"],
        "arms": [left["arm"], right["arm"]],
        "metadata_and_artifact_hashes": "verified",
        "freshness_attestations": [left["freshness"]["status"], right["freshness"]["status"]],
        "visual_verdict": "NOT_EVALUATED",
        "limits": "Metadata and hash checks do not prove independence, replay fidelity, or drawing quality.",
    }


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    seal = commands.add_parser("seal")
    seal.add_argument("spec")
    seal.add_argument("reference")
    seal.add_argument("output")
    verify = commands.add_parser("verify")
    verify.add_argument("case")
    verify.add_argument("reference")
    pair = commands.add_parser("pair")
    for field in ("case", "reference", "left", "left_root", "right", "right_root"):
        pair.add_argument(field)
    args = parser.parse_args()
    if args.command == "seal":
        value = seal_case(read_json(args.spec), args.reference)
        # Never replace a previously sealed case in place.
        with Path(args.output).open("x", encoding="utf-8") as file:
            json.dump(value, file, ensure_ascii=False, indent=2, allow_nan=False)
            file.write("\n")
        print(value["case_digest"])
    elif args.command == "verify":
        print(validate_case(read_json(args.case), args.reference))
    else:
        print(json.dumps(compare_pair(read_json(args.case), args.reference,
                                     read_json(args.left), args.left_root,
                                     read_json(args.right), args.right_root), indent=2))


if __name__ == "__main__":
    main()
