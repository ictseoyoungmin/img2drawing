#!/usr/bin/env python3
"""Read-only verification of the frozen R23 baseline pin."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BASELINE_SHA = "25ec454"
BASELINE_FULL_SHA = "25ec4544e86fe37fc28d64575df145a1b711d63a"
EXPECTED_SUBJECT = "feat: harden R23 evidence provenance"


def git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    return result.stdout.strip()


def main() -> int:
    resolved = git("rev-parse", f"{BASELINE_SHA}^{{commit}}")
    if resolved != BASELINE_FULL_SHA:
        raise SystemExit(
            f"baseline resolution drifted: expected {BASELINE_FULL_SHA}, got {resolved}"
        )

    subject = git("show", "-s", "--format=%s", BASELINE_FULL_SHA)
    if subject != EXPECTED_SUBJECT:
        raise SystemExit(
            f"baseline subject drifted: expected {EXPECTED_SUBJECT!r}, got {subject!r}"
        )

    head = git("rev-parse", "HEAD")
    ancestor = subprocess.run(
        ["git", "merge-base", "--is-ancestor", BASELINE_FULL_SHA, head],
        cwd=ROOT,
    )
    if ancestor.returncode != 0:
        raise SystemExit(f"current HEAD {head} is not based on frozen baseline {BASELINE_FULL_SHA}")

    print("BASELINE_VERIFICATION_PASS")
    print(f"baseline_sha={BASELINE_FULL_SHA}")
    print(f"baseline_subject={subject}")
    print(f"current_head={head}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
