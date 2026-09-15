#!/usr/bin/env python3
"""Verify the S03 fresh-worker visual-quality evidence harness.

The harness may remain NOT_RUN while references/workers are being selected. Once a class claims
PASS or BLOCKED, it must provide a concrete review.md with provenance and artifact hashes. PASS
requires verified fresh-worker provenance; BLOCKED may truthfully record unverified/non-fresh
provenance when that provenance failure is itself part of the blocking evidence.
"""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
S03 = ROOT / "dev" / "dogfood" / "s03-quality-gates"
CLASSES = (
    "strong-perspective-close",
    "fullbody-3q-prop",
    "frontal-fullbody",
    "head-hair-closeup",
)
STATE_RE = re.compile(r"^State:\s*\*\*(NOT_RUN|BLOCKED|PASS)\*\*\s*$", re.MULTILINE)
ROOT_STATUS_RE = re.compile(r"^Status:\s*\*\*(.+?)\*\*\s*$", re.MULTILINE)
FRESH_RE = re.compile(r"^\s*-?\s*fresh-worker confirmation:\s*`?(yes|no|unverified)`?\s*(?:\([^\n]*\))?\s*$", re.MULTILINE | re.IGNORECASE)
SHA_RE = r"[0-9a-f]{64}"


def text(path: Path) -> str:
    assert path.is_file(), f"missing S03 evidence file: {path.relative_to(ROOT)}"
    return path.read_text(encoding="utf-8")


def class_state(readme: str, class_name: str) -> str:
    match = STATE_RE.search(readme)
    assert match, f"{class_name}: missing exact State: **NOT_RUN|BLOCKED|PASS** declaration"
    return match.group(1)


def root_status(readme: str) -> str:
    match = ROOT_STATUS_RE.search(readme)
    assert match, "S03 root README is missing its top-level Status declaration"
    return match.group(1).strip()


def require_executed_review(class_dir: Path, state: str) -> None:
    review_path = class_dir / "review.md"
    review = text(review_path)
    lower = review.lower()

    fresh = FRESH_RE.search(review)
    assert fresh, f"{class_dir.name}: executed review must declare fresh-worker confirmation"
    if state == "PASS":
        assert fresh.group(1).lower() == "yes", (
            f"{class_dir.name}: PASS requires verified fresh-worker confirmation"
        )

    assert "skill/source commit:" in lower, f"{class_dir.name}: skill/source commit missing"
    assert "renderer family:" in lower, f"{class_dir.name}: renderer family missing"
    assert "session id:" in lower, f"{class_dir.name}: session id missing"

    for label in ("session.json", "final.png", "timelapse.gif", "comparison"):
        assert re.search(rf"^{re.escape(label)}\s+\S+\s+{SHA_RE}\s*$", review, re.MULTILINE), (
            f"{class_dir.name}: {label} path + SHA-256 evidence missing"
        )

    assert "## keep / soften / retire audit" in lower, (
        f"{class_dir.name}: retirement audit section missing"
    )
    assert "## top remaining visible residuals" in lower, (
        f"{class_dir.name}: residual ranking section missing"
    )
    assert "blocking:" in lower, f"{class_dir.name}: residual blocking verdict missing"
    assert "responsible owner" in lower, f"{class_dir.name}: residual owner evidence missing"
    assert "## final class verdict" in lower, f"{class_dir.name}: final verdict section missing"
    assert re.search(rf"^`?{state}`?\s*$", review, re.MULTILINE), (
        f"{class_dir.name}: review verdict must agree with README state {state}"
    )

    # Executed reviews must not retain obvious template placeholders.
    forbidden = (
        "<s03.n / class name>",
        "<yyyy-mm-dd>",
        "<path>",
        "<sha256>",
        "`yes/no`",
        "`pass | blocked`",
    )
    for marker in forbidden:
        assert marker not in lower, f"{class_dir.name}: unresolved template marker {marker!r}"


def main() -> None:
    root_readme = text(S03 / "README.md")
    template = text(S03 / "REVIEW_TEMPLATE.md")

    for required in (
        "fresh-worker rule",
        "per-run evidence contract",
        "shared visual gates",
        "geometry vs material boundary",
        "missing artifacts are not equivalent to pass",
    ):
        assert required in root_readme.lower(), f"S03 root contract missing {required!r}"

    for required in (
        "fresh-worker confirmation",
        "session.json",
        "final.png",
        "timelapse.gif",
        "comparison",
        "keep / soften / retire audit",
        "top remaining visible residuals",
        "final class verdict",
    ):
        assert required in template.lower(), f"S03 review template missing {required!r}"

    states: dict[str, str] = {}
    for class_name in CLASSES:
        class_dir = S03 / class_name
        readme = text(class_dir / "README.md")
        state = class_state(readme, class_name)
        states[class_name] = state
        if state in {"PASS", "BLOCKED"}:
            require_executed_review(class_dir, state)

    all_pass = all(state == "PASS" for state in states.values())
    status = root_status(root_readme)
    if all_pass:
        assert status == "PASS / CLOSED", (
            "all S03 classes PASS but root harness status is not exactly PASS / CLOSED"
        )
    else:
        assert status != "PASS / CLOSED", (
            "S03 root cannot be CLOSED while any class is NOT_RUN/BLOCKED"
        )

    summary = ", ".join(f"{name}={state}" for name, state in states.items())
    print(f"S03_QUALITY_GATE_HARNESS_PASS: {summary}")


if __name__ == "__main__":
    main()
