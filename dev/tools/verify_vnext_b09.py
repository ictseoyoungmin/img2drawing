#!/usr/bin/env python3
"""Verification gates for the B09 finish/recognition slice."""

from __future__ import annotations

import sys

from vnext_verification import ROOT, SRC, run_cli, run_pytest


def focused() -> None:
    run_pytest("dev/tests/test_vnext_finish.py", "dev/tests/test_vnext_intent.py")
    print("B09_FOCUSED_VERIFICATION_PASS")


def contract() -> None:
    sys.path.insert(0, str(SRC))
    from img2drawing import FINISH_INTENTS, DrawingSession, resolve_finish_guide

    assert tuple(FINISH_INTENTS) == ("pose", "subject", "form_light", "expressive")
    for finish_intent in FINISH_INTENTS:
        guide = resolve_finish_guide(finish_intent)
        payload = guide.to_dict()
        serialized = repr(payload).lower()
        for forbidden in ("finishstage", "phase_count", "pass_fail", "likeness_score"):
            assert forbidden not in serialized
    for forbidden_method in ("advance", "close", "reopen", "submit_verdict"):
        assert not hasattr(resolve_finish_guide("pose"), forbidden_method)
    assert DrawingSession.__module__ == "img2drawing.vnext.session"
    print("B09_CONTRACT_VERIFICATION_PASS")


def full() -> None:
    run_pytest("dev/tests")
    print("B09_FULL_REGRESSION_PASS")


def closure() -> None:
    required = (
        ROOT / "skills/img2drawing/references/finish/identity-and-value.md",
        ROOT / "skills/img2drawing/references/intent.md",
        ROOT / "dev/planning/vnext/capsules/B09.md",
        ROOT / "dev/planning/vnext/slices/B09.md",
        ROOT / "dev/planning/vnext/slices/B10.md",
    )
    assert all(path.is_file() for path in required)
    b09 = required[3].read_text(encoding="utf-8")
    b10 = required[4].read_text(encoding="utf-8")
    status = (ROOT / "dev/planning/vnext/STATUS.md").read_text(encoding="utf-8")
    assert "State: **CLOSED**" in b09 and "- [ ]" not in b09
    assert "State: **ACTIVE**" in b10
    assert "ACTIVE:   B10" in status and "B09" in status
    print("B09_CLOSURE_VERIFICATION_PASS")


def main() -> None:
    run_cli(
        __doc__ or "B09 verification",
        {"focused": focused, "contract": contract, "full": full, "closure": closure},
    )


if __name__ == "__main__":
    main()
