from __future__ import annotations

import json
import math
import statistics
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "dev" / "release" / "vnext" / "V1_0_3_RC1_PROMOTION.json"


def _git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def _close(a: float, b: float, tol: float = 1e-9) -> bool:
    return math.isclose(float(a), float(b), rel_tol=0.0, abs_tol=tol)


def main() -> None:
    payload = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    assert payload["schema"] == "img2drawing.v1_0_3_rc1_promotion.v1"
    assert payload["state"] == "PROMOTION_EVIDENCE_COMPLETE"

    measured_commit = payload["measured_commit"]
    measured_tree = payload["measured_tree"]
    assert _git("show", "-s", "--format=%T", measured_commit) == measured_tree

    # Promotion evidence may be followed by docs/tests/version-only commits, but the
    # measured renderer/timelapse implementation must remain byte-identical.
    runtime_paths = [
        "skills/img2drawing/src/img2drawing/provenance/fast_timelapse",
        "skills/img2drawing/src/img2drawing/render/pillow_pencil_contact_v10.py",
        "skills/img2drawing/src/img2drawing/render/renderer_contracts.py",
        "skills/img2drawing/src/img2drawing/render/renderer_dispatch.py",
        "skills/img2drawing/src/img2drawing/render/renderer_registry.py",
        "skills/img2drawing/src/img2drawing/render/v10_value_authority.py",
        "skills/img2drawing/src/img2drawing/vnext/render_profile.py",
        "skills/img2drawing/src/img2drawing/vnext/renderer_binding.py",
    ]
    subprocess.run(
        ["git", "diff", "--quiet", measured_commit, "HEAD", "--", *runtime_paths],
        cwd=ROOT,
        check=True,
    )

    fixture = payload["fixture"]
    assert fixture["actions"] == 1272
    assert fixture["sampled_frames"] == 637
    assert fixture["every_n"] == 2
    assert _close(fixture["width_scale"], 3.0)

    measurements = payload["measurements"]
    for key in ("v9", "v10"):
        record = measurements[key]
        assert len(record["cold_render_pack_sec"]) == 3
        assert len(record["warm_render_pack_sec"]) == 3
        assert len(record["cold_patch_build_sec"]) == 3
        assert _close(record["cold_median_sec"], statistics.median(record["cold_render_pack_sec"]))
        assert _close(record["warm_median_sec"], statistics.median(record["warm_render_pack_sec"]))
        assert _close(record["patch_build_median_sec"], statistics.median(record["cold_patch_build_sec"]))
        assert record["pixel_exact"] is True
        assert record["fast_rgb_sha256"] == record["canonical_rgb_sha256"]

    v9 = measurements["v9"]
    v10 = measurements["v10"]
    expected = {
        "cold_render_pack": (v10["cold_median_sec"] / v9["cold_median_sec"] - 1.0) * 100.0,
        "warm_render_pack": (v10["warm_median_sec"] / v9["warm_median_sec"] - 1.0) * 100.0,
        "cold_patch_build": (v10["patch_build_median_sec"] / v9["patch_build_median_sec"] - 1.0) * 100.0,
    }
    for name, value in expected.items():
        assert _close(measurements["v10_vs_v9_delta_pct"][name], value)

    promotion = payload["promotion"]
    assert promotion["historical_v9_preserved"] is True
    assert promotion["v9_fast_canonical_exact"] is True
    assert promotion["v10_fast_canonical_exact"] is True
    assert promotion["verdict"] == "PASS_FOR_1.0.3rc1_VERSION_DECLARATION"

    print(
        "v1.0.3rc1 promotion evidence PASS: "
        f"cold={expected['cold_render_pack']:.3f}% "
        f"warm={expected['warm_render_pack']:.3f}%"
    )


if __name__ == "__main__":
    main()
