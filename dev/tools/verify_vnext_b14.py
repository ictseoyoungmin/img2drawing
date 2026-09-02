#!/usr/bin/env python3
"""Verification gates for B14 drawing-mode capability completion."""

from __future__ import annotations

import importlib.util
import inspect
import sys
import tempfile
from dataclasses import fields

from vnext_verification import ROOT, SRC, run_cli, run_pytest


EXPECTED_MODES = (
    "croquis",
    "figure_drawing",
    "tonal_study",
    "line_study",
    "free_draw",
)


def focused() -> None:
    run_pytest(
        "dev/tests/test_vnext_modes.py",
        "dev/tests/test_vnext_intent.py",
        "dev/tests/test_vnext_reference_authority.py",
        "dev/tests/test_vnext_session.py",
        "dev/tests/test_vnext_fill.py",
        "dev/tests/test_vnext_fill_hardening.py",
        "dev/tests/test_vnext_rendering.py",
    )
    print("B14_FOCUSED_VERIFICATION_PASS")


def contract() -> None:
    sys.path.insert(0, str(SRC))
    from img2drawing import DRAWING_MODES, DrawingSession, ModeGuide, resolve_mode_guide

    assert DRAWING_MODES == EXPECTED_MODES
    assert {field.name for field in fields(ModeGuide)} == {
        "guide_id",
        "drawing_mode",
        "primary_observations",
        "recommended_grammar",
        "omissions",
        "finish_emphasis",
        "completion_questions",
    }
    guides = tuple(resolve_mode_guide(mode) for mode in DRAWING_MODES)
    assert len({guide.guide_id for guide in guides}) == len(guides)
    assert all(ModeGuide.from_dict(guide.to_dict()) == guide for guide in guides)
    assert "resolve_mode_guide" in inspect.getsource(DrawingSession.mode_guide.fget)
    tonal = " ".join(sum((list(value) for value in resolve_mode_guide("tonal_study").to_dict().values() if isinstance(value, list)), []))
    assert "fill_region" in tonal and "renderer filters" in tonal
    package = SRC / "img2drawing"
    for forbidden in (
        "CroquisSession",
        "FigureDrawingSession",
        "TonalStudySession",
        "LineStudySession",
        "FreeDrawSession",
        "ModeStage",
    ):
        assert not any(forbidden in path.read_text(encoding="utf-8") for path in package.rglob("*.py"))
    assert not (package / "modes").exists()
    print("B14_CONTRACT_VERIFICATION_PASS")


def fixture() -> None:
    path = ROOT / "dev/fixtures/vnext-b14/run.py"
    spec = importlib.util.spec_from_file_location("vnext_b14_fixture", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    with tempfile.TemporaryDirectory(prefix="img2drawing-b14-") as temporary:
        trace = module.run_fixture(temporary)
    assert trace["quality_claim"] == "mechanical-only"
    assert trace["declared_modes"] == list(EXPECTED_MODES)
    assert trace["resolved_modes"] == sorted(EXPECTED_MODES)
    assert trace["one_session_type"] and trace["one_history_type"]
    assert all(case["resume_state_match"] and case["resume_guide_match"] for case in trace["cases"])
    tonal = next(case for case in trace["cases"] if case["mode"] == "tonal_study")
    assert "region.fill" in tonal["action_kinds"]
    imaginative = next(case for case in trace["cases"] if case["authority"] == "imaginative")
    assert imaginative["artifacts"] == ["manifest", "raw_drawing", "sheet"]
    print("B14_FIXTURE_VERIFICATION_PASS")


def full() -> None:
    run_pytest("dev/tests")
    print("B14_FULL_REGRESSION_PASS")


def closure() -> None:
    required = (
        ROOT / "skills/img2drawing/references/modes/line-study.md",
        ROOT / "dev/fixtures/vnext-b14/run.py",
        ROOT / "dev/planning/vnext/capsules/B14.md",
        ROOT / "dev/planning/vnext/slices/B14.md",
        ROOT / "dev/planning/vnext/slices/B15.md",
    )
    assert all(path.is_file() for path in required)
    b14 = required[3].read_text(encoding="utf-8")
    b15 = required[4].read_text(encoding="utf-8")
    status = (ROOT / "dev/planning/vnext/STATUS.md").read_text(encoding="utf-8")
    assert "State: **CLOSED**" in b14 and "- [ ]" not in b14
    assert "State: **ACTIVE**" in b15
    assert "ACTIVE:   B15" in status and "B14" in status
    for path in (ROOT / "skills/img2drawing").rglob("*"):
        if path.is_file() and path.suffix in {".md", ".py", ".json"}:
            assert not any("\uac00" <= char <= "\ud7a3" for char in path.read_text(encoding="utf-8"))
    print("B14_CLOSURE_VERIFICATION_PASS")


def main() -> None:
    run_cli(
        __doc__ or "B14 verification",
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
