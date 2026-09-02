#!/usr/bin/env python3
"""Verification gates for B16 Agent authoring and editing ergonomics."""

from __future__ import annotations

import importlib.util
import inspect
import sys
import tempfile
from dataclasses import fields

from vnext_verification import ROOT, SRC, run_cli, run_pytest


def focused() -> None:
    run_pytest(
        "dev/tests/test_vnext_editing.py",
        "dev/tests/test_vnext_correction.py",
        "dev/tests/test_vnext_fill.py",
        "dev/tests/test_vnext_fill_hardening.py",
        "dev/tests/test_vnext_session.py",
        "dev/tests/test_vnext_rendering.py",
    )
    print("B16_FOCUSED_VERIFICATION_PASS")


def contract() -> None:
    sys.path.insert(0, str(SRC))
    from img2drawing import AuthoredElement, DrawingSession, replace_fill_region
    from img2drawing.vnext import editing

    assert {field.name for field in fields(AuthoredElement)} == {
        "element_type", "element_id", "status", "part", "role", "created_seq",
        "latest_seq", "created_action_id", "latest_action_id", "latest_action_kind",
        "action_ids", "observation_ids", "reason", "superseded_by", "revision_count",
    }
    assert "history.actions[: history.cursor]" in inspect.getsource(editing.authored_elements)
    assert "_derived_authored_elements" in inspect.getsource(DrawingSession.authored_elements)
    checkpoint_source = inspect.getsource(DrawingSession._checkpoint_payload)
    assert "authoring_summary" not in checkpoint_source and "authored_elements" not in checkpoint_source
    wrapper_source = inspect.getsource(replace_fill_region)
    assert "session.replace_fill_region" in wrapper_source and "session._agent" not in wrapper_source
    vnext_source = "\n".join(
        path.read_text(encoding="utf-8") for path in (SRC / "img2drawing/vnext").glob("*.py")
    )
    assert vnext_source.count('kind="replace_fill_region"') == 1
    for forbidden in ("EditSession", "OwnershipStage", "EditHistory", "ResponsibilityRegistry"):
        assert forbidden not in vnext_source
    assert "render" not in inspect.getsource(editing)
    print("B16_CONTRACT_VERIFICATION_PASS")


def fixture() -> None:
    path = ROOT / "dev/fixtures/vnext-b16/run.py"
    spec = importlib.util.spec_from_file_location("vnext_b16_fixture", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    with tempfile.TemporaryDirectory(prefix="img2drawing-b16-") as temporary:
        trace = module.run_fixture(temporary)
    assert trace["quality_claim"] == "mechanical-only"
    assert [item["element_id"] for item in trace["located_before"]] == ["near-arm-v1"]
    assert trace["resolved_old_arm_id"] == "near-arm-v2"
    assert trace["current_arm_id"] == "near-arm-v2"
    assert trace["current_fill_id"] == "coat-value"
    assert trace["fill_action_id"] == "revise-coat-value"
    assert trace["correction_action_ids"] == ["replace-near-arm-v2"]
    assert "missing stroke" in trace["stale_edit_error"]
    assert trace["stale_edit_preserved_cursor"]
    assert trace["summary"]["truncated"]
    assert trace["generated_contacts_excluded"]
    assert trace["checkpoint_has_no_derived_index"]
    assert trace["resume_state_match"] and trace["resume_summary_match"]
    print("B16_FIXTURE_VERIFICATION_PASS")


def full() -> None:
    run_pytest("dev/tests")
    print("B16_FULL_REGRESSION_PASS")


def closure() -> None:
    required = (
        ROOT / "skills/img2drawing/references/review/authored-element-navigation.md",
        ROOT / "dev/fixtures/vnext-b16/run.py",
        ROOT / "dev/planning/vnext/capsules/B16.md",
        ROOT / "dev/planning/vnext/slices/B16.md",
        ROOT / "dev/planning/vnext/slices/B17.md",
    )
    assert all(path.is_file() for path in required)
    b16 = required[3].read_text(encoding="utf-8")
    b17 = required[4].read_text(encoding="utf-8")
    status = (ROOT / "dev/planning/vnext/STATUS.md").read_text(encoding="utf-8")
    assert "State: **CLOSED**" in b16 and "- [ ]" not in b16
    assert "State: **ACTIVE**" in b17
    assert "ACTIVE:   B17" in status and "B16" in status
    for path in (ROOT / "skills/img2drawing").rglob("*"):
        if path.is_file() and path.suffix in {".md", ".py", ".json"}:
            assert not any("\uac00" <= char <= "\ud7a3" for char in path.read_text(encoding="utf-8"))
    print("B16_CLOSURE_VERIFICATION_PASS")


def main() -> None:
    run_cli(
        __doc__ or "B16 verification",
        {"focused": focused, "contract": contract, "fixture": fixture, "full": full, "closure": closure},
    )


if __name__ == "__main__":
    main()
