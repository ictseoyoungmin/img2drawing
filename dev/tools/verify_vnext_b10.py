#!/usr/bin/env python3
"""Verification gates for the B10 intent-aware completion slice."""

from __future__ import annotations

import inspect
import sys

from vnext_verification import ROOT, SRC, run_cli, run_pytest


def focused() -> None:
    run_pytest(
        "dev/tests/test_vnext_completion.py",
        "dev/tests/test_vnext_session.py",
        "dev/tests/test_vnext_intent.py",
    )
    print("B10_FOCUSED_VERIFICATION_PASS")


def contract() -> None:
    sys.path.insert(0, str(SRC))
    from img2drawing import FINISH_RECORD_SCHEMA, DrawingSession, FinishRecord

    assert FINISH_RECORD_SCHEMA == "img2drawing.vnext.finish_record.v1"
    record_fields = set(FinishRecord.__dataclass_fields__)
    assert record_fields == {
        "record_id",
        "intent_digest",
        "drawing_state_hash",
        "final_inspection_id",
        "history_cursor",
        "accepted_limitations",
        "unresolved_nonmaterial_notes",
        "rationale",
    }
    for forbidden in ("stage", "phase", "advance", "close", "reopen", "verdict", "score"):
        assert forbidden not in record_fields
        assert not hasattr(FinishRecord, forbidden)
    finish_source = inspect.getsource(DrawingSession.finish)
    assert "open_residual_ids" in finish_source
    assert "final inspection is stale" in finish_source
    assert "automatic" not in finish_source.lower()
    print("B10_CONTRACT_VERIFICATION_PASS")


def full() -> None:
    run_pytest("dev/tests")
    print("B10_FULL_REGRESSION_PASS")


def closure() -> None:
    required = (
        ROOT / "skills/img2drawing/references/review/completion.md",
        ROOT / "dev/fixtures/vnext-b10/run.py",
        ROOT / "dev/planning/vnext/capsules/B10.md",
        ROOT / "dev/planning/vnext/slices/B10.md",
        ROOT / "dev/planning/vnext/slices/B11.md",
    )
    assert all(path.is_file() for path in required)
    b10 = required[3].read_text(encoding="utf-8")
    b11 = required[4].read_text(encoding="utf-8")
    status = (ROOT / "dev/planning/vnext/STATUS.md").read_text(encoding="utf-8")
    assert "State: **CLOSED**" in b10 and "- [ ]" not in b10
    assert "State: **ACTIVE**" in b11
    assert "ACTIVE:   B11" in status and "B10" in status
    print("B10_CLOSURE_VERIFICATION_PASS")


def main() -> None:
    run_cli(
        __doc__ or "B10 verification",
        {"focused": focused, "contract": contract, "full": full, "closure": closure},
    )


if __name__ == "__main__":
    main()
