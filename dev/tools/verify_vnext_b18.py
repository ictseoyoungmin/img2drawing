#!/usr/bin/env python3
"""Verify the immutable v1.0.2/B18 historical freeze against Git history.

B18 is historical evidence, not the version authority for current mutable source. Later RCs may
change package identity, renderer defaults, and compatibility surface without rewriting what
v1.0.2 shipped. Current-package verification belongs to B17.
"""

from __future__ import annotations

import ast
import copy
import json
import re
import subprocess
from pathlib import Path

from jsonschema import Draft7Validator

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "skills" / "img2drawing"
SOURCE = PACKAGE / "src" / "img2drawing"
RELEASE_RECORDS = ROOT / "dev" / "release" / "vnext"
FREEZE = RELEASE_RECORDS / "CONTRACT_FREEZE.json"
TEMPLATE = ROOT / "dev" / "dogfood" / "vnext-template"


def _load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict), path
    return value


def _git_show(spec: str) -> str:
    return subprocess.check_output(["git", "show", spec], cwd=ROOT, text=True)


def check_contract_snapshot() -> None:
    frozen = _load(FREEZE)
    assert frozen["schema"] == "img2drawing.vnext.contract_freeze.v1"
    assert frozen["freeze_id"] == "v1.0.2-A10-2026-09-09"
    assert frozen["package_version"] == "1.0.2"
    assert frozen["public_api"] == "DrawingSession/1.0.2-vnext"
    assert frozen["release_revision"] == "A10"
    assert frozen["release_slice"] == "v1.0.2_local_first_exact_timelapse"

    # The immutable tag, not today's package version, is the authority for released identity.
    tagged_version = _git_show("v1.0.2:skills/img2drawing/src/img2drawing/_version.py")
    for marker in (
        '__version__ = "1.0.2"',
        'RELEASE_REVISION = "A10"',
        'RELEASE_SLICE = "v1.0.2_local_first_exact_timelapse"',
    ):
        assert marker in tagged_version, marker

    tagged_freeze = json.loads(_git_show("v1.0.2:dev/release/vnext/CONTRACT_FREEZE.json"))
    assert tagged_freeze == frozen, "mutable source rewrote the immutable v1.0.2 freeze"

    historical_profile = frozen["canonical_render_profile"]
    assert historical_profile["renderer_id"] == "pillow-pencil-contact-v9"
    assert historical_profile["renderer_version"] == "1"
    assert frozen["legacy_checkpoint_schemas"] == [
        "img2drawing.run_checkpoint.v1",
        "img2drawing.run_checkpoint.v2",
        "img2drawing.run_checkpoint.v3",
    ]
    assert frozen["ownership"]["legacy_namespace"] == "img2drawing.legacy.r23"

    # Current source is allowed to move forward, but retired implementation must not reappear.
    import img2drawing
    from img2drawing._version import PUBLIC_API, RELEASE_REVISION
    from img2drawing.vnext.render_profile import RenderProfile

    assert img2drawing.__version__ != frozen["package_version"]
    assert PUBLIC_API != frozen["public_api"]
    assert RELEASE_REVISION != frozen["release_revision"]
    assert RenderProfile.canonical(96, 72).renderer_id == "pillow-pencil-contact-v10"
    assert not (SOURCE / "legacy").exists()
    for retired_name in ("DrawingRun", "StageContract", "RegistrationGraph"):
        try:
            getattr(img2drawing, retired_name)
        except AttributeError:
            pass
        else:
            raise AssertionError(f"retired R23 root name still resolves: {retired_name}")


def check_planning_and_completeness() -> None:
    slices = ROOT / "dev" / "planning" / "vnext" / "slices"
    for number in range(9, 19):
        text = (slices / f"B{number:02d}.md").read_text(encoding="utf-8")
        assert "State: **CLOSED**" in text, f"B{number:02d} is not closed"
    active = [
        card.name
        for card in slices.glob("B*.md")
        if "State: **ACTIVE**" in card.read_text(encoding="utf-8")
    ]
    assert active == [], active

    status = (ROOT / "dev" / "planning" / "vnext" / "STATUS.md").read_text(encoding="utf-8")
    assert "frozen through B18" in status
    assert "D01–D06 not started" in status

    inventory = (ROOT / "dev" / "planning" / "vnext" / "B18_IMPLEMENTATION_INVENTORY.md").read_text(encoding="utf-8")
    for number in range(9, 18):
        assert f"B{number:02d}" in inventory
    for marker in (
        "img2drawing.vnext.session.DrawingSession",
        "img2drawing.core.session.DrawingSession",
        "vnext.value.replace_fill_region()",
    ):
        assert marker in inventory

    forbidden_text = re.compile(r"\b(?:TODO|FIXME|TBD)\b|NotImplementedError")
    for path in SOURCE.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        assert not forbidden_text.search(text), path
        tree = ast.parse(text, filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                assert not (len(node.body) == 1 and isinstance(node.body[0], ast.Pass)), (
                    f"empty function: {path}:{node.lineno}"
                )
                assert not (
                    len(node.body) == 1
                    and isinstance(node.body[0], ast.Expr)
                    and isinstance(node.body[0].value, ast.Constant)
                    and node.body[0].value.value is Ellipsis
                ), f"ellipsis function: {path}:{node.lineno}"


def _assert_invalid(validator: Draft7Validator, value: dict) -> None:
    assert list(validator.iter_errors(value)), "negative control unexpectedly validated"


def check_dogfood_contracts() -> None:
    sealed_schema = _load(ROOT / "dev" / "schemas" / "vnext_dogfood_sealed_input.schema.json")
    evaluator_schema = _load(ROOT / "dev" / "schemas" / "vnext_dogfood_evaluator.schema.json")
    Draft7Validator.check_schema(sealed_schema)
    Draft7Validator.check_schema(evaluator_schema)
    sealed_validator = Draft7Validator(sealed_schema)
    evaluator_validator = Draft7Validator(evaluator_schema)

    sealed = _load(TEMPLATE / "input" / "sealed_input.template.json")
    evaluator = _load(TEMPLATE / "evaluator" / "evaluator_brief.template.json")
    sealed_validator.validate(sealed)
    evaluator_validator.validate(evaluator)

    forbidden_keys = {
        "answer_image", "target_drawing", "coordinates", "landmarks", "previous_session",
        "action_ids", "prior_residuals", "evaluator_rationale", "verdict", "pn_packet",
        "solution_script",
    }

    def keys(value):
        if isinstance(value, dict):
            for key, item in value.items():
                yield key
                yield from keys(item)
        elif isinstance(value, list):
            for item in value:
                yield from keys(item)

    assert not forbidden_keys.intersection(keys(sealed))
    assert not forbidden_keys.intersection(keys(evaluator))
    assert not re.search(r"\bP[1-6]\b|R23", json.dumps(sealed))

    leaked = copy.deepcopy(sealed)
    leaked["answer_image"] = "answer.png"
    _assert_invalid(sealed_validator, leaked)
    traversal = copy.deepcopy(sealed)
    traversal["subject"]["file"] = "../subject.png"
    _assert_invalid(sealed_validator, traversal)

    template_files = [path for path in TEMPLATE.rglob("*") if path.is_file()]
    assert template_files
    assert all(path.suffix in {".md", ".json"} for path in template_files)
    readme = (TEMPLATE / "README.md").read_text(encoding="utf-8")
    for case in ("D01", "D02", "D03", "D04", "D05-A", "D05-B", "D06"):
        assert case in readme


def check_package_boundary() -> None:
    manifest = (PACKAGE / "MANIFEST.in").read_text(encoding="utf-8")
    for forbidden in (
        "FREEZE.md", "CONTRACT_FREEZE.json", "SUPPORT.md", "RELEASE.md", "MIGRATION.md", "NOTICE"
    ):
        assert f"include {forbidden}" not in manifest
        assert not (PACKAGE / forbidden).exists(), forbidden
    assert not (PACKAGE / "playbooks").exists()
    assert not (PACKAGE / "references" / "stages").exists()
    assert not (SOURCE / "legacy").exists()
    assert FREEZE.is_file()
    workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "verify_vnext_b18.py" in workflow


def main() -> None:
    check_contract_snapshot()
    check_planning_and_completeness()
    check_dogfood_contracts()
    check_package_boundary()
    print("B18_FROZEN_V1_0_2_HISTORY_PASS")


if __name__ == "__main__":
    main()
