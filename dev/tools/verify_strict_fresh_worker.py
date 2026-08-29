#!/usr/bin/env python3
"""Fail-closed verifier for a genuinely isolated packaged fresh-worker return.

This verifier intentionally does not create or claim a fresh worker run.  It
checks the envelope and returned artifacts produced by that worker, then runs
the mechanical audit against the returned checkpoint.  Artistic acceptance is
kept in a separate evaluator record.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

from jsonschema import validators

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "skills/img2drawing/src"))
from audit_fresh_worker import audit  # noqa: E402

SHA256 = re.compile(r"^[0-9a-f]{64}$")
ALLOWED_INPUTS = ("package", "subject", "user_goal")
FORBIDDEN_CONTEXT = frozenset({"repository", "material_sources", "dogfood_history", "prior_action_ids", "prior_coordinates"})


def _load(path: Path) -> dict:
    if not path.is_file():
        raise AssertionError(f"missing strict fresh-worker artifact: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"strict fresh-worker artifact must be an object: {path}")
    return value


def _validate_schema(name: str, value: dict) -> None:
    schema_path = ROOT / "dev/schemas" / name
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validator = validators.validator_for(schema)
    validator.check_schema(schema)
    validator(schema).validate(value)


def _sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def _relative_path(raw: object, *, base: Path, label: str) -> Path:
    value = str(raw or "")
    path = Path(value)
    if not value or path.is_absolute() or any(part == ".." for part in path.parts):
        raise AssertionError(f"{label} must be a relative path inside the evidence root")
    resolved = (base / path).resolve()
    try:
        resolved.relative_to(base.resolve())
    except ValueError as exc:
        raise AssertionError(f"{label} escapes the evidence root") from exc
    return resolved


def _portable_text_scan(root: Path) -> None:
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() in {".png", ".gif", ".zip", ".whl"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for token in ("/home/claude/", "/home/ymin/.codex/attachments/", "REPLACE_FROM_"):
            if token in text:
                raise AssertionError(f"non-portable token {token!r} in {path}")


def verify(evidence_dir: Path) -> dict:
    evidence_dir = evidence_dir.resolve()
    envelope_path = evidence_dir / "input_envelope.json"
    report_path = evidence_dir / "strict_fresh_worker_report.json"
    audit_path = evidence_dir / "mechanical_audit.json"
    envelope = _load(envelope_path)
    report = _load(report_path)
    persisted_audit = _load(audit_path)
    _validate_schema("strict_fresh_worker_input.schema.json", envelope)
    _validate_schema("strict_fresh_worker_report.schema.json", report)

    if envelope.get("schema") != "img2drawing.strict_fresh_worker_input.v1":
        raise AssertionError("unsupported strict fresh-worker input envelope schema")
    if tuple(envelope.get("allowed_inputs") or ()) != ALLOWED_INPUTS:
        raise AssertionError("strict fresh-worker envelope must expose only package, subject and user_goal")
    if not FORBIDDEN_CONTEXT.issubset(set(envelope.get("forbidden_context") or ())):
        raise AssertionError("strict fresh-worker envelope does not forbid repository/material/history leakage")
    if not str(envelope.get("user_goal") or "").strip():
        raise AssertionError("strict fresh-worker envelope requires a user goal")

    package = envelope.get("package") or {}
    subject = envelope.get("subject") or {}
    package_path = _relative_path(package.get("path"), base=evidence_dir, label="package.path")
    subject_path = _relative_path(subject.get("path"), base=evidence_dir, label="subject.path")
    package_sha = str(package.get("sha256") or "").lower()
    subject_sha = str(subject.get("sha256") or "").lower()
    if not SHA256.fullmatch(package_sha) or _sha(package_path) != package_sha:
        raise AssertionError("strict fresh-worker package hash mismatch")
    if not SHA256.fullmatch(subject_sha) or _sha(subject_path) != subject_sha:
        raise AssertionError("strict fresh-worker subject hash mismatch")

    worker_session = str(envelope.get("worker_session_id") or "").strip()
    evaluator_session = str(envelope.get("evaluator_session_id") or "").strip()
    if not worker_session or not evaluator_session or worker_session == evaluator_session:
        raise AssertionError("fresh worker and independent evaluator must have distinct non-empty sessions")
    if report.get("schema") != "img2drawing.strict_fresh_worker_report.v1":
        raise AssertionError("unsupported strict fresh-worker report schema")
    if report.get("status") != "closed" or report.get("mechanical_artistic_separation") is not True:
        raise AssertionError("strict fresh-worker report is not a separated closed return")
    if report.get("worker_session_id") != worker_session or report.get("evaluator_session_id") != evaluator_session:
        raise AssertionError("strict report session IDs do not match the input envelope")
    if str(report.get("package_sha256") or "").lower() != package_sha:
        raise AssertionError("strict report package identity mismatch")
    if str(report.get("subject_sha256") or "").lower() != subject_sha:
        raise AssertionError("strict report subject identity mismatch")

    run_dir = _relative_path(report.get("run_dir"), base=evidence_dir, label="report.run_dir")
    visual_path = _relative_path(report.get("visual_review_path"), base=evidence_dir, label="report.visual_review_path")
    visual = _load(visual_path)
    _validate_schema("strict_fresh_worker_visual_review.schema.json", visual)
    if visual.get("schema") != "img2drawing.strict_fresh_worker_visual_review.v1":
        raise AssertionError("unsupported independent visual review schema")
    if visual.get("evaluator_session_id") != evaluator_session or visual.get("decision") != "advance":
        raise AssertionError("independent evaluator session/decision is missing")
    if visual.get("worker_session_id") != worker_session:
        raise AssertionError("visual review is not bound to the returned worker session")

    mechanical = audit(
        run_dir,
        expected_package_sha256=package_sha,
        expected_subject_sha256=subject_sha,
        forbidden_action_ids=tuple(str(x) for x in envelope.get("forbidden_action_ids") or ()),
    )
    for key in ("complete", "subject_sha256", "package_sha256", "stage_registry"):
        if persisted_audit.get(key) != mechanical.get(key):
            raise AssertionError(f"persisted mechanical audit drifted for {key}")
    if persisted_audit.get("semantic_visual_audit_required") is not True:
        raise AssertionError("mechanical audit must not claim artistic authority")
    _portable_text_scan(evidence_dir)
    return {
        "schema": "img2drawing.strict_fresh_worker_verification.v1",
        "status": "closed",
        "package_sha256": package_sha,
        "subject_sha256": subject_sha,
        "worker_session_id": worker_session,
        "evaluator_session_id": evaluator_session,
        "mechanical_audit": mechanical,
        "mechanical_artistic_separation": True,
        "semantic_visual_authority": "independent evaluator",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence-dir", required=True, type=Path)
    args = parser.parse_args()
    try:
        result = verify(args.evidence_dir)
    except Exception as exc:
        print(f"S14B_VERIFICATION_FAIL: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True))
    print("S14B_VERIFICATION_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
