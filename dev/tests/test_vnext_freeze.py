from __future__ import annotations

import copy
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

from jsonschema import Draft7Validator


ROOT = Path(__file__).resolve().parents[2]


def test_b18_freeze_verifier_accepts_current_contract_and_templates():
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT / "skills" / "img2drawing" / "src")
    result = subprocess.run(
        [sys.executable, "dev/tools/verify_vnext_b18.py"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "B18_SYSTEM_FREEZE_VERIFICATION_PASS" in result.stdout


def test_sealed_input_schema_rejects_solution_leakage_and_fake_subject():
    schema = json.loads(
        (ROOT / "dev" / "schemas" / "vnext_dogfood_sealed_input.schema.json").read_text()
    )
    template = json.loads(
        (
            ROOT
            / "dev"
            / "dogfood"
            / "vnext-template"
            / "input"
            / "sealed_input.template.json"
        ).read_text()
    )
    validator = Draft7Validator(schema)
    validator.validate(template)

    leaked = copy.deepcopy(template)
    leaked["answer_image"] = "answer.png"
    assert list(validator.iter_errors(leaked))

    imaginative = copy.deepcopy(template)
    imaginative["case_id"] = "D05-A"
    imaginative["intent"]["reference_mode"] = "imaginative"
    imaginative["authority"] = {
        "mode": "imaginative",
        "declared_goals": ["one rising arc"],
        "constraints": [],
    }
    assert list(validator.iter_errors(imaginative)), "subjectless input accepted a fake subject"


def test_sealing_tool_binds_subject_and_rejects_undeclared_answer_file(tmp_path: Path):
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    subject = input_dir / "subject.png"
    subject.write_bytes(b"fresh-subject-fixture")
    payload = json.loads(
        (
            ROOT
            / "dev"
            / "dogfood"
            / "vnext-template"
            / "input"
            / "sealed_input.template.json"
        ).read_text()
    )
    payload["subject"]["sha256"] = hashlib.sha256(subject.read_bytes()).hexdigest()
    sealed = input_dir / "sealed_input.json"
    sealed.write_text(json.dumps(payload), encoding="utf-8")
    command = [sys.executable, "dev/tools/seal_vnext_dogfood_input.py", str(sealed)]
    accepted = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    assert accepted.returncode == 0, accepted.stdout + accepted.stderr
    assert "SEALED_VNEXT_DOGFOOD_INPUT_OK" in accepted.stdout

    (input_dir / "answer.png").write_bytes(b"prohibited")
    rejected = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    assert rejected.returncode != 0
    assert "undeclared files" in rejected.stderr
