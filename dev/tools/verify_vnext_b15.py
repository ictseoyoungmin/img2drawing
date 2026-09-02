#!/usr/bin/env python3
"""Verification gates for B15 style authoring completion."""

from __future__ import annotations

import importlib.util
import inspect
import sys
import tempfile
from dataclasses import fields

from vnext_verification import ROOT, SRC, run_cli, run_pytest


EXPECTED_STYLES = ("pencil_loose", "graphite_academic", "graphite_tonal")


def focused() -> None:
    run_pytest(
        "dev/tests/test_vnext_styles.py",
        "dev/tests/test_vnext_intent.py",
        "dev/tests/test_vnext_modes.py",
        "dev/tests/test_vnext_session.py",
        "dev/tests/test_vnext_rendering.py",
        "dev/tests/test_vnext_fill.py",
        "dev/tests/test_vnext_fill_hardening.py",
    )
    print("B15_FOCUSED_VERIFICATION_PASS")


def contract() -> None:
    sys.path.insert(0, str(SRC))
    from img2drawing import STYLE_PROFILES, RenderProfile, StyleGuide, resolve_style_guide

    assert STYLE_PROFILES == EXPECTED_STYLES
    assert {field.name for field in fields(StyleGuide)} == {
        "style_profile",
        "line_behavior",
        "construction_visibility",
        "detail_policy",
        "value_policy",
        "edge_policy",
        "authoring_notes",
    }
    guides = tuple(resolve_style_guide(profile) for profile in STYLE_PROFILES)
    assert len({guide.to_dict().__repr__() for guide in guides}) == len(guides)
    assert all(StyleGuide.from_dict(guide.to_dict()) == guide for guide in guides)
    assert "RenderProfile" not in inspect.getsource(resolve_style_guide)
    assert not ({"renderer_id", "renderer_version", "supersample", "seed"} & set(guides[0].to_dict()))
    assert not ({"style_profile", "line_behavior", "value_policy", "edge_policy"} & set(RenderProfile.canonical(32, 32).to_dict()))
    package = SRC / "img2drawing"
    for forbidden in (
        "PencilLooseSession",
        "GraphiteAcademicSession",
        "GraphiteTonalSession",
        "StyleStage",
        "StylePipeline",
    ):
        assert not any(forbidden in path.read_text(encoding="utf-8") for path in package.rglob("*.py"))
    assert not (package / "styles").exists()
    print("B15_CONTRACT_VERIFICATION_PASS")


def fixture() -> None:
    path = ROOT / "dev/fixtures/vnext-b15/run.py"
    spec = importlib.util.spec_from_file_location("vnext_b15_fixture", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    with tempfile.TemporaryDirectory(prefix="img2drawing-b15-") as temporary:
        trace = module.run_fixture(temporary)
    assert trace["quality_claim"] == "mechanical-only"
    assert [case["style_profile"] for case in trace["preset_cases"]] == list(EXPECTED_STYLES)
    assert trace["preset_geometry_equal"] and trace["preset_render_profiles_equal"]
    assert trace["preset_pngs_equal"]
    assert trace["one_session_type"] and trace["one_history_type"]
    assert all(case["resume_state_match"] for case in trace["preset_cases"])
    mid = trace["mid_session"]
    assert mid["event_cursor"] == 1
    assert mid["selection_preserved_state"]
    assert mid["selection_preserved_cursor"]
    assert mid["selection_preserved_render_profile"]
    assert mid["explicit_edit_advanced_cursor"]
    assert mid["explicit_edit_changed_state"]
    assert mid["resume_state_match"]
    assert mid["resume_style_profile"] == "graphite_tonal"
    assert trace["custom_roundtrip"]
    print("B15_FIXTURE_VERIFICATION_PASS")


def full() -> None:
    run_pytest("dev/tests")
    print("B15_FULL_REGRESSION_PASS")


def closure() -> None:
    required = (
        ROOT / "skills/img2drawing/references/styles/authoring-styles.md",
        ROOT / "dev/fixtures/vnext-b15/run.py",
        ROOT / "dev/planning/vnext/capsules/B15.md",
        ROOT / "dev/planning/vnext/slices/B15.md",
        ROOT / "dev/planning/vnext/slices/B16.md",
    )
    assert all(path.is_file() for path in required)
    b15 = required[3].read_text(encoding="utf-8")
    b16 = required[4].read_text(encoding="utf-8")
    status = (ROOT / "dev/planning/vnext/STATUS.md").read_text(encoding="utf-8")
    assert "State: **CLOSED**" in b15 and "- [ ]" not in b15
    assert "State: **ACTIVE**" in b16
    assert "ACTIVE:   B16" in status and "B15" in status
    for path in (ROOT / "skills/img2drawing").rglob("*"):
        if path.is_file() and path.suffix in {".md", ".py", ".json"}:
            assert not any("\uac00" <= char <= "\ud7a3" for char in path.read_text(encoding="utf-8"))
    print("B15_CLOSURE_VERIFICATION_PASS")


def main() -> None:
    run_cli(
        __doc__ or "B15 verification",
        {
            "focused": focused,
            "contract": contract,
            "fixture": fixture,
            "full": full,
            "closure": closure,
        },
    )


if __name__ == "__main__":
    main()
