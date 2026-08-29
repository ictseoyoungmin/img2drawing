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


ROOT = Path(__file__).resolve().parents[2]


def _load(path: Path):
    if not path.is_file():
        raise AssertionError(f"missing evidence: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def _sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def _nonblank(path: Path) -> None:
    with Image.open(path) as image:
        gray = image.convert("L")
        if ImageChops.invert(gray).getbbox() is None:
            raise AssertionError(f"blank image: {path}")


def _relative_text_scan(root: Path) -> None:
    forbidden = ("/home/claude/", "/home/ymin/.codex/attachments/", "REPLACE_FROM_")
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() in {".png", ".gif", ".zip", ".whl"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for token in forbidden:
            if token in text:
                raise AssertionError(f"non-portable or placeholder token {token!r} in {path}")


def check_s10() -> None:
    base = ROOT / "dev/evidence/material-integration"
    report = _load(base / "s10-quality-run/quality_run_report.json")
    if report.get("status") != "closed" or report.get("current_stage") is not None:
        raise AssertionError("S10 quality run is not closed")
    final = base / "s10-quality-run/final/drawing.png"
    _nonblank(final)
    if _sha(final) != "9fb40326de73d3d70f682a4424e786b1b606f3f685cd6608b69317afb479f3e5":
        raise AssertionError("S10 final artifact hash drifted; refresh the evidence report")
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
    source = ROOT / "skills/img2drawing/src/img2drawing"
    for rel in ("review/resolved_form.py", "review/adaptive_evidence.py", "review/preview.py", "stages/identity_finish.py"):
        if not (source / rel).is_file():
            raise AssertionError(f"missing S11/S12 implementation: {rel}")
    for rel in ("resolved_form.schema.json", "identity_finish.schema.json", "adaptive_evidence.schema.json"):
        _load(ROOT / "dev/schemas" / rel)
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT / "skills/img2drawing/src")
    env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "dev/tests/test_resolved_form.py"],
        cwd=ROOT, env=env, text=True, capture_output=True,
    )
    if result.returncode != 0 or "passed" not in result.stdout:
        raise AssertionError(f"S11/S12 tests failed:\n{result.stdout}\n{result.stderr}")


def check_s14() -> None:
    report_path = ROOT / "dev/evidence/fresh-worker/generalization_report.json"
    report = _load(report_path)
    if report.get("status") != "closed" or report.get("mechanical_artistic_separation") is not True:
        raise AssertionError("fresh-worker report is not closed or conflates mechanical/artistic PASS")
    final = ROOT / report["final_drawing"]
    _nonblank(final)
    if report.get("prohibited_coordinate_or_action_ids"):
        raise AssertionError("fresh-worker report contains prohibited material coordinates/action IDs")
    _relative_text_scan(report_path.parent)


def check_s15() -> None:
    report = _load(ROOT / "dev/release/r23/release_manifest.json")
    if report.get("version") != "0.5.2.dev23" or report.get("revision") != "R23":
        raise AssertionError("release identity is not R23")
    for item in report.get("artifacts", []):
        path = ROOT / item["path"]
        if not path.is_file() or _sha(path) != item["sha256"]:
            raise AssertionError(f"release artifact hash mismatch: {path}")
    _relative_text_scan(ROOT / "dev/release/r23")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", required=True, choices=("s10", "s11-s12", "s14", "s15"))
    args = parser.parse_args()
    try:
        {"s10": check_s10, "s11-s12": check_s11_s12, "s14": check_s14, "s15": check_s15}[args.check]()
    except Exception as exc:
        print(f"{args.check.upper().replace('-', '_')}_VERIFICATION_FAIL: {exc}", file=sys.stderr)
        return 1
    marker = {"s10": "S10_VERIFICATION_PASS", "s11-s12": "S11_S12_VERIFICATION_PASS", "s14": "S14_VERIFICATION_PASS", "s15": "S15_VERIFICATION_PASS"}[args.check]
    print(marker)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
