#!/usr/bin/env python3
"""Verification gates for B13 reference authority and subjectless runtime."""

from __future__ import annotations

import inspect
import sys

from vnext_verification import ROOT, SRC, run_cli, run_pytest


def focused() -> None:
    run_pytest(
        "dev/tests/test_vnext_reference_authority.py",
        "dev/tests/test_vnext_session.py",
        "dev/tests/test_vnext_intent.py",
        "dev/tests/test_vnext_correction.py",
        "dev/tests/test_inspection_foundation.py",
        "dev/tests/test_vnext_rendering.py",
    )
    print("B13_FOCUSED_VERIFICATION_PASS")


def contract() -> None:
    sys.path.insert(0, str(SRC))
    from img2drawing import DrawingSession, ReferenceAuthority, ReferenceConstraint
    from img2drawing.inspection import InspectionSheet
    from img2drawing.vnext import reference_authority, session

    assert "subject: str | Path | None" in inspect.getsource(DrawingSession.create)
    assert "canvas: Sequence[int] | None" in inspect.getsource(DrawingSession.create)
    assert "ReferenceAuthority" in inspect.getsource(session.DrawingSession)
    drawing_only_source = inspect.getsource(InspectionSheet._write_drawing_only)
    assert "invented reference" in drawing_only_source
    assert "contrast_overlay" not in drawing_only_source
    assert "registered_drawing" not in drawing_only_source
    assert ReferenceAuthority.__module__ == reference_authority.__name__
    assert ReferenceConstraint.__module__ == reference_authority.__name__
    package = SRC / "img2drawing"
    for forbidden in ("ObservedSession", "ImaginativeSession", "HybridSession"):
        assert not any(forbidden in path.read_text(encoding="utf-8") for path in package.rglob("*.py"))
    assert not (package / "subjectless").exists()
    assert not (package / "hybrid").exists()
    print("B13_CONTRACT_VERIFICATION_PASS")


def full() -> None:
    run_pytest("dev/tests")
    print("B13_FULL_REGRESSION_PASS")


def closure() -> None:
    required = (
        ROOT / "skills/img2drawing/references/reference-authority.md",
        ROOT / "dev/fixtures/vnext-b13/run.py",
        ROOT / "dev/planning/vnext/capsules/B13.md",
        ROOT / "dev/planning/vnext/slices/B13.md",
        ROOT / "dev/planning/vnext/slices/B14.md",
    )
    assert all(path.is_file() for path in required)
    b13 = required[3].read_text(encoding="utf-8")
    b14 = required[4].read_text(encoding="utf-8")
    status = (ROOT / "dev/planning/vnext/STATUS.md").read_text(encoding="utf-8")
    assert "State: **CLOSED**" in b13 and "- [ ]" not in b13
    assert "State: **ACTIVE**" in b14
    assert "ACTIVE:   B14" in status and "B13" in status
    for path in (ROOT / "skills/img2drawing").rglob("*"):
        if path.is_file() and path.suffix in {".md", ".py", ".json"}:
            assert not any("\uac00" <= char <= "\ud7a3" for char in path.read_text(encoding="utf-8"))
    print("B13_CLOSURE_VERIFICATION_PASS")


def main() -> None:
    run_cli(
        __doc__ or "B13 verification",
        {"focused": focused, "contract": contract, "full": full, "closure": closure},
    )


if __name__ == "__main__":
    main()
