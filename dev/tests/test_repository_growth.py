import importlib.util
import sys
from pathlib import Path

import pytest

path=Path(__file__).resolve().parents[1]/"tools/verify_repository_growth.py"
sys.path.insert(0,str(path.parent))
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


def test_path_budget_applies_to_unchanged_files_and_windows_code_units():
    long_path="dev/"+"a"*97
    current={long_path:("abc",10)}
    assert any("relative path" in v for v in growth.policy_violations(current,current))
    assert not growth.policy_violations({},{"dev/"+"a"*96:("abc",10)})
    assert growth.policy_violations({},{"dev/"+"😀"*49:("abc",10)})


def test_retired_tree_identity_and_reintroduced_paths():
    old={}
    ids={}
    entries=[]
    for i,path in enumerate(growth.RETIRED_PATHS):
        kind="tree" if path in growth.RETIRED_TREES else "blob"
        old[path+"/old.json" if kind=="tree" else path]=(str(i),10)
        ids[path]=str(i)
        entries.append({"path":path,"kind":kind,"git_sha":str(i),"files":1,"bytes":10})
    manifest={"schema":"img2drawing.retired_evidence.v1","source_commit":growth.RETIRED_SOURCE,
              "archive_count":len(entries),"archive_bytes":10*len(entries),"entries":entries}
    assert growth.retired_violations(manifest,old,{},ids)==[]
    assert growth.retired_violations(manifest,old,old,ids)
    bad_ids={**ids,growth.RETIRED_PATHS[0]:"wrong"}
    assert growth.retired_violations(manifest,old,{},bad_ids)
    extra={growth.RETIRED_TREES[0]+"/new.json":("new",1)}
    assert growth.retired_violations(manifest,old,extra,ids)
    assert growth.retired_violations({**manifest,"entries":entries[:-1]},old,{},ids)


def test_archived_reader_refuses_unrelated_and_traversal_paths():
    from historical_evidence import read_archived_blob
    for path in ("README.md","dev/release/r23/../../README.md"):
        with pytest.raises(ValueError,match="declared retired"):
            read_archived_blob(path)
