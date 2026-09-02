#!/usr/bin/env python3
"""Validate one D01-D06 worker input and print its canonical SHA-256 seal."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from jsonschema import Draft7Validator


ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "dev" / "schemas" / "vnext_dogfood_sealed_input.schema.json"
PROHIBITED_REQUEST_HINTS = re.compile(
    r"\b(?:answer image|target drawing|authored coordinates?|landmark table|"
    r"previous session|prior residual|evaluator (?:rationale|verdict)|"
    r"worker packet|solution script|R23|P[1-6])\b",
    re.IGNORECASE,
)


def canonical_bytes(payload: dict) -> bytes:
    return (json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def validate_and_seal(path: Path) -> str:
    requested = path.absolute()
    if requested.is_symlink() or not requested.is_file():
        raise ValueError("sealed input must be a regular JSON file")
    candidate = requested.resolve()
    payload = json.loads(candidate.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft7Validator.check_schema(schema)
    Draft7Validator(schema).validate(payload)
    if PROHIBITED_REQUEST_HINTS.search(payload["user_request"]):
        raise ValueError("user_request contains prohibited prior-solution or legacy hints")

    allowed = {candidate.name}
    subject = payload["subject"]
    if subject is not None:
        subject_path = candidate.parent / subject["file"]
        if subject_path.is_symlink() or not subject_path.is_file():
            raise ValueError("declared subject must be a regular sibling file")
        actual = hashlib.sha256(subject_path.read_bytes()).hexdigest()
        if actual != subject["sha256"]:
            raise ValueError("declared subject SHA-256 does not match the supplied file")
        allowed.add(subject_path.name)

    extras = sorted(item.name for item in candidate.parent.iterdir() if item.name not in allowed)
    if extras:
        raise ValueError("sealed worker input directory contains undeclared files: " + ", ".join(extras))
    return hashlib.sha256(canonical_bytes(payload)).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    digest = validate_and_seal(args.input)
    print(f"SEALED_VNEXT_DOGFOOD_INPUT_OK sha256={digest}")


if __name__ == "__main__":
    main()
