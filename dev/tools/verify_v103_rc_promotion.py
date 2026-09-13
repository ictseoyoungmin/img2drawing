from __future__ import annotations

import json
import math
import statistics
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "dev" / "release" / "vnext" / "V1_0_3_RC1_PROMOTION.json"
CONTRACTS = "skills/img2drawing/src/img2drawing/render/renderer_contracts.py"


def _git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def _git_show(commit: str, path: str) -> str:
    return subprocess.check_output(["git", "show", f"{commit}:{path}"], cwd=ROOT, text=True)


def _blob(commit: str, path: str) -> str:
    return _git("rev-parse", f"{commit}:{path}")


def _close(a: float, b: float, tol: float = 1e-9) -> bool:
    return math.isclose(float(a), float(b), rel_tol=0.0, abs_tol=tol)


def _assignment_block(text: str, name: str) -> str:
    marker = f"{name} = RendererContract("
    start = text.index(marker)
    open_pos = text.index("(", start)
    depth = 0
    for index in range(open_pos, len(text)):
        char = text[index]
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                return text[start : index + 1]
    raise AssertionError(f"unterminated {name} assignment")


def main() -> None:
    payload = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    assert payload["schema"] == "img2drawing.v1_0_3_rc1_promotion.v1"
    assert payload["state"] == "PROMOTION_EVIDENCE_COMPLETE"
    measured_commit = payload["measured_commit"]
    assert _git("show", "-s", "--format=%T", measured_commit) == payload["measured_tree"]

    immutable_same_paths = [
        "skills/img2drawing/src/img2drawing/provenance/fast_timelapse",
        "skills/img2drawing/src/img2drawing/render/renderer_dispatch.py",
        "skills/img2drawing/src/img2drawing/vnext/render_profile.py",
        "skills/img2drawing/src/img2drawing/vnext/renderer_binding.py",
    ]
    subprocess.run(
        ["git", "diff", "--quiet", measured_commit, "HEAD", "--", *immutable_same_paths],
        cwd=ROOT,
        check=True,
    )
    renamed_immutable_paths = {
        "skills/img2drawing/src/img2drawing/render/pillow_pencil_contact_v10.py":
            "skills/img2drawing/src/img2drawing/render/pillow_pencil_contact_core.py",
        "skills/img2drawing/src/img2drawing/render/v10_value_authority.py":
            "skills/img2drawing/src/img2drawing/render/pencil_value_authority.py",
    }
    for historical_path, current_path in renamed_immutable_paths.items():
        assert _blob(measured_commit, historical_path) == _blob("HEAD", current_path)

    historical_contracts = _git_show(measured_commit, CONTRACTS)
    current_contracts = (ROOT / CONTRACTS).read_text(encoding="utf-8")
    assert _assignment_block(current_contracts, "V10_CONTRACT") == _assignment_block(historical_contracts, "V10_CONTRACT")

    from img2drawing.render.renderer_registry import registered_renderer_identities
    identities = set(registered_renderer_identities())
    assert ("pillow-pencil-contact-v9", "1") in identities
    assert ("pillow-pencil-contact-v10", "1") in identities

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
    print(f"v1.0.3rc1 historical promotion evidence PASS: cold={expected['cold_render_pack']:.3f}% warm={expected['warm_render_pack']:.3f}%")


if __name__ == "__main__":
    main()
