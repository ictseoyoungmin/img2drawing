#!/usr/bin/env python3
"""Keep new generated data out of Git and verify retired evidence remains recoverable."""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path, PurePosixPath

ROOT=Path(__file__).resolve().parents[2]
BASE="1127e673e05799040e802e9fd3a887d7781f2941"
MAX_NEW_BLOB=1024*1024
MAX_DEV_BINARY=512*1024
MAX_NEW_DEV_BINARY_TOTAL=2*1024*1024
BINARY={".png",".jpg",".jpeg",".webp",".gif",".zip",".gz",".whl",".mp4",".blend",".glb",".npz",".npy",".pdf"}


def read_tree(root, ref):
    raw=subprocess.check_output(["git","ls-tree","-r","-l","-z",ref],cwd=root)
    out={}
    for entry in raw.split(b"\0"):
        if not entry:
            continue
        meta,name=entry.split(b"\t",1)
        mode,kind,sha,size=meta.decode().split()
        if kind=="blob":
            out[name.decode("utf-8")]=(sha,int(size))
    return out


def generated(path):
    p=PurePosixPath(path)
    parts=p.parts
    if parts[0] in {"qa-results","private-qa","drawings","temp"}:
        return True
    if path.startswith(("dev/benchmarks/constructive_qa/runs/","dev/benchmarks/tonal_qa/runs/")):
        return True
    if parts[0]!="dev":
        return False
    return (p.name in {"session.json","session.checkpoint.json","timelapse.gif","canonical_final.png"}
            or p.name.endswith(".render.json")
            or any(x in {"frames","frame_packs","reopen_archive","runs"} for x in parts))


def policy_violations(before,after):
    violations=[]
    new_dev_binary=0
    for path,(sha,size) in sorted(after.items()):
        if before.get(path)==(sha,size):
            continue
        if generated(path):
            violations.append(f"generated output: {path}")
        if size>MAX_NEW_BLOB:
            violations.append(f"new/changed blob exceeds 1 MiB: {path}")
        if path.startswith("dev/") and PurePosixPath(path).suffix.lower() in BINARY:
            new_dev_binary+=size
            if size>MAX_DEV_BINARY:
                violations.append(f"dev binary exceeds 512 KiB: {path}")
    if new_dev_binary>MAX_NEW_DEV_BINARY_TOTAL:
        violations.append("new/changed dev binary total exceeds 2 MiB")
    return violations


def archive_violations(manifest,before,after):
    errors=[]
    if manifest.get("schema")!="img2drawing.historical_evidence_archive.v1" or manifest.get("source_commit")!=BASE:
        return ["invalid immutable archive authority"]
    entries=manifest["files"]
    if len(entries)!=manifest["archive_count"] or sum(x["bytes"] for x in entries)!=manifest["archive_bytes"]:
        errors.append("archive totals mismatch")
    seen=set()
    for entry in entries:
        path=entry["path"]
        if path in seen or before.get(path)!=(entry["git_blob_sha"],entry["bytes"]):
            errors.append(f"archive identity mismatch: {path}")
        if path in after:
            errors.append(f"archived path reintroduced: {path}")
        seen.add(path)
    return errors


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json",action="store_true")
    args=parser.parse_args()
    before,after=read_tree(ROOT,BASE),read_tree(ROOT,"HEAD")
    manifest=json.loads((ROOT/"dev/docs/historical-evidence-archive.json").read_text())
    errors=policy_violations(before,after)+archive_violations(manifest,before,after)
    summary={"baseline_bytes":sum(v[1] for v in before.values()),
             "current_bytes":sum(v[1] for v in after.values()),
             "archived_files":manifest["archive_count"],"archived_bytes":manifest["archive_bytes"],
             "violations":errors}
    if args.json or errors:
        print(json.dumps(summary,indent=2))
    else:
        print("REPOSITORY_GROWTH_AND_ARCHIVE_PASS",summary)
    if errors:
        raise SystemExit(1)


if __name__=="__main__":
    main()
