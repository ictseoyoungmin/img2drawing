"""S07 worker-envelope privacy and input parity tests; no artistic verdict."""
import importlib.util
import json
from pathlib import Path
import zipfile

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "prepare_s07_blind_workers.py"
SPEC = importlib.util.spec_from_file_location("s07_pair", SCRIPT)
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


def fixture(tmp_path):
    ref = tmp_path / "reference.png"
    ref.write_bytes(bytes.fromhex("89504e470d0a1a0a0000000d494844520000080000000800") + b"private-fake-extent")
    goal = tmp_path / "goal.txt"
    goal.write_text("Draw faithfully using direct authored marks.\n", encoding="utf-8")
    budget = tmp_path / "budget.json"
    budget.write_text(json.dumps({"canvas": [2048, 2048], "supersample": 2,
                                  "max_actions": 1358, "max_wall_sec": 14400}))
    archives = []
    for tag in ("a", "b"):
        skill = tmp_path / f"{tag}-skill.zip"
        with zipfile.ZipFile(skill, "w") as zf:
            zf.writestr("img2drawing/SKILL.md", "explicit direct drawing")
        wheel = tmp_path / f"img2drawing-{tag}.whl"
        with zipfile.ZipFile(wheel, "w") as zf:
            zf.writestr(f"img2drawing-1.3.{tag}.dist-info/METADATA", "metadata")
            zf.writestr("img2drawing/__init__.py", tag)
        archives.append((skill, wheel))
    old, new = archives
    return {
        "reference": ref, "goal_file": goal, "budget_file": budget,
        "graphite_skill": old[0], "graphite_wheel": old[1],
        "mixed_skill": new[0], "mixed_wheel": new[1],
        "out_dir": tmp_path / "sealed",
        "expected_graphite_wheel_sha": module.sha256(old[1]),
        "expected_mixed_wheel_sha": module.sha256(new[1]),
    }


def test_worker_pair_isolated_and_identical_reference_budget(tmp_path):
    args = fixture(tmp_path)
    result = module.prepare(**args)
    root = args["out_dir"]
    evaluator = json.loads((root / "evaluator_only.json").read_text())
    assert result["status"] == evaluator["status"] == "PREPARED_NOT_RUN"
    assert len(result["worker_codes"]) == 2
    assert {v["medium"] for v in evaluator["assignments"]} == {"graphite", "mixed"}
    assert {v["worker_code"] for v in evaluator["assignments"]} == set(result["worker_codes"])
    prompts = []
    for code in result["worker_codes"]:
        folder = root / "workers" / code
        assert {p.name for p in folder.iterdir()} == module.ALLOWED
        assert not (folder / "evaluator_only.json").exists()
        spec = json.loads((folder / "worker.json").read_text())
        assert spec["reference_sha256"] == module.sha256(args["reference"])
        assert spec["shared_goal_sha256"] == module.sha256(args["goal_file"])
        assert spec["budget_sha256"] == module.sha256(folder / "budget.json")
        assert spec["skill_sha256"] == module.sha256(folder / "skill.zip")
        assert spec["runtime_sha256"] == module.sha256(folder / "runtime.whl")
        assert "end-to-end GIF" in spec["required_outputs"]
        assert spec["visual_verdict"] == "REVIEWER_ONLY_NOT_RUN"
        assert "evaluator" not in {p.name for p in folder.iterdir()}
        prompts.append((folder / "goal.md").read_text())
    assert all(s.startswith(args["goal_file"].read_text().rstrip()) for s in prompts)
    assert prompts[0] != prompts[1]
    assert len({module.sha256(root / "workers" / code / "runtime.whl")
                for code in result["worker_codes"]}) == 2


def test_mismatched_pin_fails_without_outputs(tmp_path):
    args = fixture(tmp_path)
    args["expected_graphite_wheel_sha"] = "0" * 64
    with pytest.raises(ValueError, match="SHA-256"):
        module.prepare(**args)
    assert not args["out_dir"].exists()


def test_invalid_budget_fails_before_output(tmp_path):
    args = fixture(tmp_path)
    args["budget_file"].write_text(json.dumps({"canvas": [2048, 2048], "supersample": 2,
                                               "max_actions": True, "max_wall_sec": 1000}))
    with pytest.raises(ValueError, match="max_actions"):
        module.prepare(**args)
    assert not args["out_dir"].exists()


def test_no_overwrite_existing_output(tmp_path):
    args = fixture(tmp_path)
    args["out_dir"].mkdir()
    (args["out_dir"] / "keep").write_text("original")
    with pytest.raises(FileExistsError):
        module.prepare(**args)
    assert (args["out_dir"] / "keep").read_text() == "original"


def test_reject_invalid_png_and_unsafe_zip(tmp_path):
    args = fixture(tmp_path)
    args["reference"].write_bytes(b"no-image")
    with pytest.raises(ValueError, match="valid IHDR"):
        module.prepare(**args)
    assert not args["out_dir"].exists()
    args["reference"].write_bytes(bytes.fromhex("89504e470d0a1a0a0000000d494844520000080000000800"))
    with zipfile.ZipFile(args["graphite_skill"], "w") as zf:
        zf.writestr("img2drawing/SKILL.md", "yes")
        zf.writestr("../private/session.json", "no")
    with pytest.raises(ValueError, match="unsafe path"):
        module.prepare(**args)
    assert not args["out_dir"].exists()
