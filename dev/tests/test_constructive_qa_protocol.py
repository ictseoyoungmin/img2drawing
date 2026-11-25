"""S00 contract validates matched evidence without awarding artistic PASS."""
import copy
import importlib.util
from pathlib import Path

import pytest

module = Path(__file__).resolve().parents[1] / "benchmarks/constructive_qa/protocol.py"
spec = importlib.util.spec_from_file_location("constructive_protocol", module)
qa = importlib.util.module_from_spec(spec)
spec.loader.exec_module(qa)


def case_spec():
    return dict(case_id="fixture", subject_class="portrait",
                user_request="Draw the supplied reference with explicit strokes.",
                intent=dict(reference_mode="observed", drawing_mode="croquis",
                            finish_intent="subject", style_profile="pencil_loose"),
                worker=dict(model="test-model", configuration={"effort": "fixed"}),
                budget=dict(max_actions=500, max_wall_seconds=900, max_tokens=50000),
                canvas=dict(width=1024, height=559))


def make_case(tmp_path):
    ref = tmp_path / "reference.bin"
    ref.write_bytes(b"test reference bytes")
    return ref, qa.seal_case(case_spec(), ref)


def make_run(root, case, arm, worker_id):
    root.mkdir()
    artifacts = {}
    for key in qa.ARTIFACTS:
        file = root / (key + ".bin")
        file.write_bytes((key + worker_id).encode())
        artifacts[key] = {"file": file.name, "sha256": qa.file_digest(file)}
    return dict(schema=qa.RUN_SCHEMA, case_digest=case["case_digest"], arm=arm,
                commit=qa.BASELINES[arm], worker_run_id=worker_id,
                freshness=dict(status="unverified", evidence="fixture"),
                usage=dict(actions=300, wall_seconds=100.5, tokens=5000),
                artifacts=artifacts)


def test_seal_rejects_reference_or_condition_drift(tmp_path):
    ref, case = make_case(tmp_path)
    assert qa.validate_case(case, ref) == case["case_digest"]
    drift = copy.deepcopy(case)
    drift["spec"]["budget"]["max_actions"] += 1
    with pytest.raises(ValueError, match="mismatch"):
        qa.validate_case(drift, ref)
    ref.write_bytes(b"changed")
    with pytest.raises(ValueError, match="mismatch"):
        qa.validate_case(case, ref)


def test_seal_rejects_answer_payload_and_invalid_budget(tmp_path):
    ref, _ = make_case(tmp_path)
    bad = case_spec()
    bad["prior_solution"] = "must not travel with sealed input"
    with pytest.raises(ValueError):
        qa.seal_case(bad, ref)
    bad = case_spec()
    bad["budget"]["max_actions"] = True
    with pytest.raises(ValueError):
        qa.seal_case(bad, ref)


def test_paired_evidence_is_not_visual_pass(tmp_path):
    ref, case = make_case(tmp_path)
    a, b = tmp_path / "a", tmp_path / "b"
    left = make_run(a, case, "v1.2.0", "a")
    right = make_run(b, case, "v1.2.1", "b")
    result = qa.compare_pair(case, ref, left, a, right, b)
    assert result["metadata_and_artifact_hashes"] == "verified"
    assert result["visual_verdict"] == "NOT_EVALUATED"
    assert result["freshness_attestations"] == ["unverified", "unverified"]
    right["worker_run_id"] = "a"
    with pytest.raises(ValueError, match="separate worker"):
        qa.compare_pair(case, ref, left, a, right, b)


def test_pair_rejects_wrong_commit_budget_and_tampered_artifact(tmp_path):
    ref, case = make_case(tmp_path)
    a, b = tmp_path / "a", tmp_path / "b"
    left = make_run(a, case, "v1.2.0", "a")
    right = make_run(b, case, "v1.2.1", "b")
    bad = copy.deepcopy(right)
    bad["commit"] = "0" * 40
    with pytest.raises(ValueError, match="baseline commit drift"):
        qa.compare_pair(case, ref, left, a, bad, b)
    bad = copy.deepcopy(right)
    bad["usage"]["actions"] = 501
    with pytest.raises(ValueError, match="budget exceeded"):
        qa.compare_pair(case, ref, left, a, bad, b)
    (b / right["artifacts"]["review"]["file"]).write_bytes(b"tamper")
    with pytest.raises(ValueError, match="digest mismatch"):
        qa.compare_pair(case, ref, left, a, right, b)


def test_artifact_path_rejects_escape(tmp_path):
    root = tmp_path / "run"
    root.mkdir()
    (tmp_path / "private.bin").write_bytes(b"outside")
    with pytest.raises(ValueError, match="escapes"):
        qa.artifact_path(root, "../private.bin")
    with pytest.raises(ValueError, match="escapes"):
        qa.artifact_path(root, str(tmp_path / "private.bin"))
