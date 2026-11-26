#!/usr/bin/env python3
"""Small, fail-closed completion checks for the material-integration slices."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageChops

from verify_repository_paths import MACHINE_PATH
from historical_evidence import archived_snapshot


ROOT = Path(__file__).resolve().parents[2]
R23_PRE_RETIREMENT_COMMIT = "4074a2080ad739acdf179bb0784869a8831c5ef0"


def _load(path: Path):
    if not path.is_file():
        raise AssertionError(f"missing evidence: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def _git_blob(ref: str, path: str) -> str:
    result = subprocess.run(
        ["git", "rev-parse", f"{ref}:{path}"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        raise AssertionError(
            f"cannot resolve frozen Git evidence {ref}:{path}: {result.stderr.strip()}"
        )
    return result.stdout.strip()


def _nonblank(path: Path) -> None:
    with Image.open(path) as image:
        gray = image.convert("L")
        if ImageChops.invert(gray).getbbox() is None:
            raise AssertionError(f"blank image: {path}")


def _relative_text_scan(root: Path) -> None:
    # Historical evidence lives in a temporary, non-Git directory.
    # Use the same portability rule and binary detection as the live-tree check.
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        raw = path.read_bytes()
        if b"\x00" in raw[:4096]:
            continue
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            continue
        for line_number, line in enumerate(text.splitlines(), 1):
            if MACHINE_PATH.search(line):
                raise AssertionError(f"non-portable absolute path in {path.relative_to(root)}:{line_number}")


def check_s10() -> None:
    with archived_snapshot("dev/evidence/material-integration") as root:
        _check_s10(root)


def _check_s10(root: Path) -> None:
    base = root / "dev/evidence/material-integration"
    report = _load(base / "s10-quality-run/quality_run_report.json")
    if report.get("status") != "closed" or report.get("current_stage") is not None:
        raise AssertionError("S10 quality run is not closed")
    final = base / "s10-quality-run/final/drawing.png"
    _nonblank(final)
    expected_final_sha = str(report.get("final_drawing_sha256", ""))
    if not expected_final_sha or _sha(final) != expected_final_sha:
        raise AssertionError("S10 final artifact hash drifted or is absent from the evidence report")
    gate = _load(base / "s10_residual_gate.json")
    if gate.get("status") != "closed" or len(gate.get("regions", [])) != 8:
        raise AssertionError("S10 residual gate is incomplete")
    if gate.get("state_binding", {}).get("observation_lock_digest") != report.get("observation_lock_digest"):
        raise AssertionError("S10 observation lock binding mismatch")
    for stage in ("P4_structural_connections", "P5_clean_blockin"):
        pass_dir = base / "s10-quality-run/reviews" / stage / "pass_01"
        _load(pass_dir / "resolved_form_manifest.json")
        _load(pass_dir / "resolved_form_review.json")
    _load(base / "s10-quality-run/identity/identity_finish_manifest.json")
    _relative_text_scan(base)


def check_s11_s12() -> None:
    """Verify closed S11/S12 evidence without requiring retired R23 code in current src."""

    frozen_blobs = {
        "skills/img2drawing/src/img2drawing/review/resolved_form.py": "491eeb6d59b9a8848becba5ace9a441f030bf34f",
        "skills/img2drawing/src/img2drawing/review/adaptive_evidence.py": "ad4765d8a2e241f2a5d79b9fa6bc9cf358599cce",
        "skills/img2drawing/src/img2drawing/review/preview.py": "88175bb780d551499506eadbd5da469b5be3b0f7",
        "skills/img2drawing/src/img2drawing/stages/identity_finish.py": "83dc34071cef136b55929a07e79a570543b0d962",
        "dev/tests/test_resolved_form.py": "bcbb87d59f04478900c867b02309f7599ba4c5a6",
    }
    for path, expected_blob in frozen_blobs.items():
        actual_blob = _git_blob(R23_PRE_RETIREMENT_COMMIT, path)
        if actual_blob != expected_blob:
            raise AssertionError(
                f"S11/S12 frozen implementation/test blob drift: {path}: {actual_blob} != {expected_blob}"
            )

    # These schemas and the closed evidence remain repository-level historical records.
    for rel in ("resolved_form.schema.json", "identity_finish.schema.json", "adaptive_evidence.schema.json"):
        _load(ROOT / "dev/schemas" / rel)

    # Current mutable source must not re-grow the retired implementations merely to satisfy
    # a historical completion gate.
    source = ROOT / "skills/img2drawing/src/img2drawing"
    for rel in ("review", "stages"):
        if (source / rel).exists():
            raise AssertionError(f"retired S11/S12 runtime unexpectedly returned to current src: {rel}")


def check_s14() -> None:
    with archived_snapshot("dev/evidence/fresh-worker") as root:
        _check_s14(root)


def _check_s14(root: Path) -> None:
    report_path = root / "dev/evidence/fresh-worker/generalization_report.json"
    report = _load(report_path)
    if report.get("status") != "closed" or report.get("mechanical_artistic_separation") is not True:
        raise AssertionError("fresh-worker report is not closed or conflates mechanical/artistic PASS")
    final = root / report["final_drawing"]
    _nonblank(final)
    if report.get("prohibited_coordinate_or_action_ids"):
        raise AssertionError("fresh-worker report contains prohibited material coordinates/action IDs")
    _relative_text_scan(report_path.parent)


def check_s14b(evidence_dir: Path | None = None) -> None:
    """Verify a real packaged fresh-worker return, if one was supplied.

    Unlike ``check_s14`` this path never treats the repository's scripted fixture
    as a fresh-worker run.  The strict verifier is intentionally fail-closed when
    the external evidence directory has not been returned yet.
    """
    tools_dir = ROOT / "dev/tools"
    if str(tools_dir) not in sys.path:
        sys.path.insert(0, str(tools_dir))
    from verify_strict_fresh_worker import verify

    verify((ROOT / "dev/evidence/strict-fresh-worker") if evidence_dir is None else evidence_dir)


def check_s15() -> None:
    with archived_snapshot("dev/release/r23") as root:
        _check_s15(root)


def _check_s15(root: Path) -> None:
    report = _load(root / "dev/release/r23/release_manifest.json")
    if report.get("version") != "0.5.2.dev23" or report.get("revision") != "R23":
        raise AssertionError("release identity is not R23")
    for item in report.get("artifacts", []):
        path = root / item["path"]
        if not path.is_file() or _sha(path) != item["sha256"]:
            raise AssertionError(f"release artifact hash mismatch: {path}")
    _relative_text_scan(root / "dev/release/r23")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", required=True, choices=("s10", "s11-s12", "s14", "s14b", "s15"))
    parser.add_argument(
        "--evidence-dir", type=Path,
        help="returned strict fresh-worker evidence directory (used by --check s14b)",
    )
    args = parser.parse_args()
    try:
        checks = {"s10": check_s10, "s11-s12": check_s11_s12, "s14": check_s14, "s15": check_s15}
        if args.check == "s14b":
            check_s14b(args.evidence_dir)
        else:
            checks[args.check]()
    except Exception as exc:
        print(f"{args.check.upper().replace('-', '_')}_VERIFICATION_FAIL: {exc}", file=sys.stderr)
        return 1
    marker = {"s10": "S10_VERIFICATION_PASS", "s11-s12": "S11_S12_VERIFICATION_PASS", "s14": "S14_VERIFICATION_PASS", "s14b": "S14B_VERIFICATION_PASS", "s15": "S15_VERIFICATION_PASS"}[args.check]
    print(marker)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
