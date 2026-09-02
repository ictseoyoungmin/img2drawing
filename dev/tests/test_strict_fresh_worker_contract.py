from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import zipfile

import pytest
from jsonschema import validators


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT.parent
SUBJECT = ROOT / "fixtures" / "r23" / "full_body_croquis" / "subject.png"


def _load_tool(name: str):
    path = ROOT / "tools" / f"{name}.py"
    if str(ROOT / "tools") not in sys.path:
        sys.path.insert(0, str(ROOT / "tools"))
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_strict_worker_schemas_are_valid_and_accept_prepared_envelope(tmp_path: Path):
    schemas = {}
    for path in sorted((ROOT / "schemas").glob("strict_fresh_worker_*.schema.json")):
        schema = json.loads(path.read_text(encoding="utf-8"))
        validator = validators.validator_for(schema)
        validator.check_schema(schema)
        schemas[path.stem] = schema

    prep = _load_tool("prepare_strict_fresh_worker_input")
    envelope_path = prep.prepare(
        tmp_path,
        subject=SUBJECT,
        user_goal="Produce a complete packaged fresh-worker drawing run.",
        worker_session_id="worker-contract-test",
        evaluator_session_id="evaluator-contract-test",
    )
    envelope = json.loads(envelope_path.read_text(encoding="utf-8"))
    validators.validator_for(schemas["strict_fresh_worker_input.schema"])(
        schemas["strict_fresh_worker_input.schema"]
    ).validate(envelope)
    assert tuple(envelope["allowed_inputs"]) == ("package", "subject", "user_goal")
    assert set((tmp_path / "input").iterdir()) == {
        tmp_path / "input" / "img2drawing-skill-r23-candidate.zip",
        tmp_path / "input" / "subject.png",
    }
    assert envelope["package"]["sha256"] == _sha(tmp_path / envelope["package"]["path"])
    assert envelope["subject"]["sha256"] == _sha(tmp_path / envelope["subject"]["path"])
    with zipfile.ZipFile(tmp_path / envelope["package"]["path"]) as archive:
        assert not any(name.startswith("img2drawing/examples/") for name in archive.namelist())


def test_scripted_fixture_audit_is_mechanical_and_not_visual_authority():
    audit_tool = _load_tool("audit_fresh_worker")
    result = audit_tool.audit(PROJECT / "dev/evidence/fresh-worker")
    assert result["complete"] is True
    assert result["stage_registry"] == "full_body_croquis_with_p6"
    assert result["semantic_visual_audit_required"] is True
    assert result["package_sha256"] is None


def test_strict_verifier_does_not_promote_scripted_fixture():
    verifier = _load_tool("verify_strict_fresh_worker")
    with pytest.raises(AssertionError, match="strict fresh-worker artifact"):
        verifier.verify(PROJECT / "dev/evidence/fresh-worker")
