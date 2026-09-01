#!/usr/bin/env python3
"""Verification gates for B11 canonical render/replay/GIF parity."""

from __future__ import annotations

import inspect
import sys

from vnext_verification import ROOT, SRC, run_cli, run_pytest


def focused() -> None:
    run_pytest(
        "dev/tests/test_vnext_rendering.py",
        "dev/tests/test_timelapse.py",
        "dev/tests/test_vnext_session.py",
    )
    print("B11_FOCUSED_VERIFICATION_PASS")


def contract() -> None:
    sys.path.insert(0, str(SRC))
    from img2drawing import DrawingSession, RenderProfile
    from img2drawing.core import session as core_session
    from img2drawing.render import pillow_pencil_contact
    from img2drawing.vnext import output

    profile = RenderProfile.canonical(32, 32)
    assert profile.renderer_id == pillow_pencil_contact.RENDERER_ID
    assert profile.renderer_version == pillow_pencil_contact.RENDERER_VERSION
    assert core_session.RENDERER_ID == pillow_pencil_contact.RENDERER_ID
    assert core_session.RENDERER_VERSION == pillow_pencil_contact.RENDERER_VERSION
    assert output.render is pillow_pencil_contact.render
    assert "style_profile" not in profile.to_dict()
    assert "post_filter" not in profile.to_dict()
    for method in ("render_at", "render_final", "export_timelapse", "migrate_render_profile"):
        assert hasattr(DrawingSession, method)
    assert "history.state_at" in inspect.getsource(output._render_at)
    print("B11_CONTRACT_VERIFICATION_PASS")


def full() -> None:
    run_pytest("dev/tests")
    print("B11_FULL_REGRESSION_PASS")


def closure() -> None:
    required = (
        ROOT / "skills/img2drawing/references/output/render-profile-and-replay.md",
        ROOT / "dev/fixtures/vnext-b11/run.py",
        ROOT / "dev/planning/vnext/capsules/B11.md",
        ROOT / "dev/planning/vnext/slices/B11.md",
        ROOT / "dev/planning/vnext/slices/B12.md",
    )
    assert all(path.is_file() for path in required)
    b11 = required[3].read_text(encoding="utf-8")
    b12 = required[4].read_text(encoding="utf-8")
    status = (ROOT / "dev/planning/vnext/STATUS.md").read_text(encoding="utf-8")
    assert "State: **CLOSED**" in b11 and "- [ ]" not in b11
    assert "State: **ACTIVE**" in b12
    assert "ACTIVE:   B12" in status and "B11" in status
    print("B11_CLOSURE_VERIFICATION_PASS")


def main() -> None:
    run_cli(
        __doc__ or "B11 verification",
        {"focused": focused, "contract": contract, "full": full, "closure": closure},
    )


if __name__ == "__main__":
    main()
