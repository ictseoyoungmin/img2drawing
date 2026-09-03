#!/usr/bin/env python3
"""Verify the B18 dogfood-ready contract freeze without running visual dogfood."""

from __future__ import annotations

import ast
import copy
import inspect
import json
import re
import sys
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


def _schema_of(value) -> str:
    schema = value.to_dict().get("schema")
    assert isinstance(schema, str) and schema
    return schema


def _public_members(cls) -> list[str]:
    return sorted(
        name
        for name, value in inspect.getmembers(cls)
        if not name.startswith("_")
        and (inspect.isfunction(value) or inspect.ismethod(value) or isinstance(value, property))
    )


def check_contract_snapshot() -> None:
    preexisting = set(sys.modules)
    import img2drawing
    from img2drawing import CanvasHistory, DrawingSession, InspectionSheet, RenderProfile
    from img2drawing._version import PUBLIC_API, RELEASE_REVISION, RELEASE_SLICE
    from img2drawing.vnext.completion import FINISH_RECORD_SCHEMA
    from img2drawing.vnext.correction import CorrectionRecord, ResidualRecord
    from img2drawing.vnext.editing import AUTHORED_ELEMENT_SCHEMA, AUTHORING_SUMMARY_SCHEMA
    from img2drawing.vnext.evidence import EvidencePolicy, EvidenceReadRecord, EvidenceTelemetry
    from img2drawing.vnext.intent import (
        DRAWING_MODES,
        FINISH_GUIDE_SCHEMA,
        FINISH_INTENTS,
        FINISH_RELATION_SCHEMA,
        INTENT_EVENT_SCHEMA,
        INTENT_SCHEMA,
        MODE_GUIDE_SCHEMA,
        REFERENCE_MODES,
        STYLE_GUIDE_SCHEMA,
        STYLE_PROFILES,
    )
    from img2drawing.vnext.output import RENDER_ARTIFACT_SCHEMA, REPLAY_EXPORT_SCHEMA
    from img2drawing.vnext.reference_authority import (
        REFERENCE_AUTHORITY_SCHEMA,
        REFERENCE_CONSTRAINT_SCHEMA,
    )
    from img2drawing.vnext.render_profile import RENDER_PROFILE_SCHEMA
    from img2drawing.vnext.session import SESSION_SCHEMA

    newly_loaded = set(sys.modules).difference(preexisting)
    forbidden_root_loads = {
        "img2drawing.run", "img2drawing.stages", "img2drawing.review",
        "img2drawing.registration", "img2drawing.exemplar",
    }
    assert not forbidden_root_loads.intersection(newly_loaded)

    frozen = _load(FREEZE)
    assert frozen["schema"] == "img2drawing.vnext.contract_freeze.v1"
    assert frozen["package_version"] == img2drawing.__version__
    assert frozen["public_api"] == PUBLIC_API
    assert frozen["release_revision"] == RELEASE_REVISION
    assert frozen["release_slice"] == RELEASE_SLICE
    assert frozen["root_exports"] == sorted(img2drawing.__all__)
    for name in img2drawing.__all__:
        getattr(img2drawing, name)
    assert frozen["drawing_session_members"] == _public_members(DrawingSession)
    assert img2drawing.DrawingSession is DrawingSession
    assert img2drawing.VNextDrawingSession is DrawingSession
    assert frozen["ownership"] == {
        "session": f"{DrawingSession.__module__}.{DrawingSession.__name__}",
        "history": f"{CanvasHistory.__module__}.{CanvasHistory.__name__}",
        "inspection": f"{InspectionSheet.__module__}.{InspectionSheet.__name__}",
        "renderer": "img2drawing.render.pillow_pencil_contact",
        "legacy_namespace": "img2drawing.legacy.r23",
    }

    actual_axes = {
        "reference_modes": list(REFERENCE_MODES),
        "drawing_modes": list(DRAWING_MODES),
        "finish_intents": list(FINISH_INTENTS),
        "style_profiles": list(STYLE_PROFILES),
    }
    assert frozen["intent_axes"] == actual_axes

    zero = "0" * 64
    one = "1" * 64
    actual_schemas = {
        "session": SESSION_SCHEMA,
        "intent": INTENT_SCHEMA,
        "intent_event": INTENT_EVENT_SCHEMA,
        "mode_guide": MODE_GUIDE_SCHEMA,
        "style_guide": STYLE_GUIDE_SCHEMA,
        "finish_guide": FINISH_GUIDE_SCHEMA,
        "finish_relation": FINISH_RELATION_SCHEMA,
        "finish_record": FINISH_RECORD_SCHEMA,
        "residual": _schema_of(ResidualRecord(
            residual_id="r", observation_id="o", observation="mismatch", scope="whole",
            severity="material", impact_rationale="changes reading",
            responsible_premise=None, responsible_stroke_ids=(), planned_edit="revise",
            before_inspection_id="000001", before_drawing_state_hash=zero,
        )),
        "correction": _schema_of(CorrectionRecord(
            correction_id="c", residual_id="r", observation_id="o",
            before_inspection_id="000001", before_drawing_state_hash=zero,
            before_history_cursor=0, action_ids=("a",), after_inspection_id="000002",
            after_drawing_state_hash=one, decision="keep", rationale="fresh evidence",
        )),
        "evidence_policy": _schema_of(EvidencePolicy.from_inputs(
            mode="quick", rois=(), guides=(), measurements=(), escalation_reason=None,
        )),
        "evidence_read": _schema_of(EvidenceReadRecord(
            event_id="e", inspection_id="000001", artifact="sheet", stale=False,
            inspection_drawing_state_hash=zero, current_drawing_state_hash=zero,
        )),
        "evidence_telemetry": _schema_of(EvidenceTelemetry()),
        "reference_authority": REFERENCE_AUTHORITY_SCHEMA,
        "reference_constraint": REFERENCE_CONSTRAINT_SCHEMA,
        "render_profile": RENDER_PROFILE_SCHEMA,
        "render_artifact": RENDER_ARTIFACT_SCHEMA,
        "replay_export": REPLAY_EXPORT_SCHEMA,
        "authored_element": AUTHORED_ELEMENT_SCHEMA,
        "authoring_summary": AUTHORING_SUMMARY_SCHEMA,
    }
    assert frozen["schemas"] == actual_schemas

    profile = RenderProfile.canonical(96, 72).to_dict()
    profile.pop("canvas_width")
    profile.pop("canvas_height")
    assert frozen["canonical_render_profile"] == profile

    from img2drawing.legacy.r23 import LEGACY_CHECKPOINT_SCHEMAS, LEGACY_EXPORTS

    assert frozen["legacy_checkpoint_schemas"] == list(LEGACY_CHECKPOINT_SCHEMAS)
    assert not set(img2drawing.__all__).intersection(LEGACY_EXPORTS)


def check_planning_and_completeness() -> None:
    slices = ROOT / "dev" / "planning" / "vnext" / "slices"
    for number in range(9, 19):
        text = (slices / f"B{number:02d}.md").read_text(encoding="utf-8")
        assert "State: **CLOSED**" in text, f"B{number:02d} is not closed"
    active = []
    for card in slices.glob("B*.md"):
        if "State: **ACTIVE**" in card.read_text(encoding="utf-8"):
            active.append(card.name)
    assert active == [], active

    # B18 owns the frozen implementation boundary, not the mutable next-task label.
    # Current planning may insert post-freeze cleanup before D01 without invalidating B18.
    status = (ROOT / "dev" / "planning" / "vnext" / "STATUS.md").read_text(encoding="utf-8")
    assert "frozen through B18" in status
    assert "D01–D06 not started" in status

    inventory = ROOT / "dev" / "planning" / "vnext" / "B18_IMPLEMENTATION_INVENTORY.md"
    inventory_text = inventory.read_text(encoding="utf-8")
    for number in range(9, 18):
        assert f"B{number:02d}" in inventory_text
    for marker in (
        "img2drawing.vnext.session.DrawingSession",
        "img2drawing.core.session.DrawingSession",
        "vnext.value.replace_fill_region()",
    ):
        assert marker in inventory_text

    forbidden_text = re.compile(r"\b(?:TODO|FIXME|TBD)\b|NotImplementedError")
    for path in SOURCE.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        assert not forbidden_text.search(text), path
        tree = ast.parse(text, filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                assert not (len(node.body) == 1 and isinstance(node.body[0], ast.Pass)), f"empty function: {path}:{node.lineno}"
                assert not (
                    len(node.body) == 1
                    and isinstance(node.body[0], ast.Expr)
                    and isinstance(node.body[0].value, ast.Constant)
                    and node.body[0].value.value is Ellipsis
                ), f"ellipsis function: {path}:{node.lineno}"

    session_tree = ast.parse((SOURCE / "vnext" / "session.py").read_text(encoding="utf-8"))
    canonical_classes = [
        node for node in session_tree.body
        if isinstance(node, ast.ClassDef) and node.name == "DrawingSession"
    ]
    assert len(canonical_classes) == 1
    value_text = (SOURCE / "vnext" / "value.py").read_text(encoding="utf-8")
    assert "return session.replace_fill_region(" in value_text
    assert "session._agent" not in value_text
    freeze_text = (RELEASE_RECORDS / "FREEZE.md").read_text(encoding="utf-8")
    assert "core.session.DrawingSession" in freeze_text and "not root-exported" in freeze_text


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
    imaginative = copy.deepcopy(sealed)
    imaginative["case_id"] = "D05-A"
    imaginative["intent"]["reference_mode"] = "imaginative"
    imaginative["subject"] = None
    imaginative["authority"] = {
        "mode": "imaginative", "declared_goals": ["one dominant rising arc"], "constraints": [],
    }
    sealed_validator.validate(imaginative)
    fake_subject = copy.deepcopy(imaginative)
    fake_subject["subject"] = sealed["subject"]
    _assert_invalid(sealed_validator, fake_subject)
    hybrid = copy.deepcopy(sealed)
    hybrid["case_id"] = "D05-B"
    hybrid["intent"]["reference_mode"] = "hybrid"
    hybrid["authority"] = {
        "mode": "hybrid",
        "declared_goals": ["transform one object"],
        "constraints": [
            {"constraint_id": "pose", "description": "keep pose", "disposition": "preserved"},
            {
                "constraint_id": "object", "description": "change object",
                "disposition": "transformed", "transformation": "make it a ribbon",
                "rationale": "requested concept",
            },
        ],
    }
    sealed_validator.validate(hybrid)
    verdict = copy.deepcopy(evaluator)
    verdict["verdict"] = "PASS"
    _assert_invalid(evaluator_validator, verdict)

    template_files = [path for path in TEMPLATE.rglob("*") if path.is_file()]
    assert template_files
    assert all(path.suffix in {".md", ".json"} for path in template_files)
    readme = (TEMPLATE / "README.md").read_text(encoding="utf-8")
    for case in ("D01", "D02", "D03", "D04", "D05-A", "D05-B", "D06"):
        assert case in readme
    validation = (ROOT / "dev" / "planning" / "vnext" / "VALIDATION_RELEASE.md").read_text(encoding="utf-8")
    assert "vnext-template" in validation
    assert "dev/release/vnext/CONTRACT_FREEZE.json" in validation


def check_package_boundary() -> None:
    manifest = (PACKAGE / "MANIFEST.in").read_text(encoding="utf-8")
    for forbidden in (
        "FREEZE.md", "CONTRACT_FREEZE.json", "SUPPORT.md", "RELEASE.md", "MIGRATION.md", "NOTICE"
    ):
        assert f"include {forbidden}" not in manifest
        assert not (PACKAGE / forbidden).exists(), forbidden
    assert not (PACKAGE / "playbooks").exists()
    assert not (PACKAGE / "references" / "stages").exists()
    assert FREEZE.is_file()
    workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "verify_vnext_b18.py" in workflow
    assert (ROOT / "dev" / "tools" / "seal_vnext_dogfood_input.py").is_file()


def main() -> None:
    check_contract_snapshot()
    check_planning_and_completeness()
    check_dogfood_contracts()
    check_package_boundary()
    print("B18_SYSTEM_FREEZE_VERIFICATION_PASS")


if __name__ == "__main__":
    main()
