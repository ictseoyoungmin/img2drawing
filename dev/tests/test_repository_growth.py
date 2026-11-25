import importlib.util
from pathlib import Path

path=Path(__file__).resolve().parents[1]/"tools/verify_repository_growth.py"
spec=importlib.util.spec_from_file_location("growth",path)
growth=importlib.util.module_from_spec(spec)
spec.loader.exec_module(growth)

def test_unchanged_frozen_large_artifacts_allowed_new_outputs_rejected():
    old={"dev/dogfood/old/timelapse.gif":("a",10_000_000)}
    assert growth.policy_violations(old,old)==[]
    new={**old,"dev/benchmarks/constructive_qa/runs/one/preview.png":("b",100)}
    assert any("generated output" in v for v in growth.policy_violations(old,new))
    assert growth.policy_violations(old,{"dev/tests/fixture.py":("c",1024)})==[]

def test_budget_and_archive_identity():
    assert growth.policy_violations({},{"dev/evidence/new.png":("x",600_000)})
    manifest={"schema":"img2drawing.historical_evidence_archive.v1","source_commit":growth.BASE,
              "archive_count":1,"archive_bytes":10,
              "files":[{"path":"old.png","git_blob_sha":"abc","bytes":10}]}
    before={"old.png":("abc",10)}
    assert growth.archive_violations(manifest,before,{})==[]
    assert growth.archive_violations(manifest,before,before)
    assert growth.archive_violations(manifest,{"old.png":("bad",10)},{})
