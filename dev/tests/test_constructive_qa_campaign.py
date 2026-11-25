import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from zipfile import ZipFile

import pytest
from PIL import Image

from img2drawing import DrawingIntent, DrawingSession, RenderProfile

folder=Path(__file__).resolve().parents[1]/"benchmarks/constructive_qa"
sys.path.insert(0,str(folder))
try:
    import campaign
    import protocol
finally:
    sys.path.remove(str(folder))


def case(ref):
    return protocol.seal_case({"case_id":"test","subject_class":"still_life",
        "user_request":"Draw the supplied reference with explicit strokes.",
        "intent":{"reference_mode":"observed","drawing_mode":"croquis","finish_intent":"subject","style_profile":"pencil_loose"},
        "worker":{"model":"fixture","configuration":{}},
        "budget":{"max_actions":100,"max_wall_seconds":120,"max_tokens":None},
        "canvas":{"width":64,"height":64}},ref)


def test_packet_from_git_contains_only_skill_and_target(tmp_path):
    repo=tmp_path/"git"
    repo.mkdir()
    def git(*a):
        return subprocess.check_output(["git",*a],cwd=repo,text=True).strip()
    git("init","-q")
    git("config","user.email","fixture@example.com")
    git("config","user.name","fixture")
    skill=repo/"skills/img2drawing"
    skill.mkdir(parents=True)
    (skill/"SKILL.md").write_text("read skill")
    (repo/"answer.json").write_text("must not be delivered")
    git("add",".");git("commit","-qm","fixture")
    commit=git("rev-parse","HEAD")
    ref=tmp_path/"ref.png";Image.new("RGB",(64,64),"white").save(ref)
    out=tmp_path/"worker.zip"
    result=campaign.prepare_worker_packet(repo,case(ref),ref,"v1.3.0",commit,"fresh-1",out)
    assert result["status"]=="PREPARED_NOT_EXECUTED"
    with ZipFile(out) as z:
        assert set(z.namelist())=={"task.json","reference.png","skills/img2drawing/SKILL.md"}
        assert z.read("reference.png")==ref.read_bytes()
        assert "answer.json" not in z.namelist()
    with pytest.raises(ValueError):
        campaign.prepare_worker_packet(repo,case(ref),ref,"v1.2.0",commit,"fresh-1",tmp_path/"wrong.zip")


def test_actual_replay_verification_and_tampering(tmp_path):
    ref=tmp_path/"ref.png";Image.new("RGB",(64,64),"white").save(ref)
    case_record=case(ref)
    evidence=tmp_path/"evidence";evidence.mkdir()
    profile=RenderProfile.from_dict({**RenderProfile.canonical(64,64).to_dict(),"supersample":2})
    s=DrawingSession.create(subject=ref,output_dir=evidence,session_id="replay-fixture",
        intent=DrawingIntent(**case_record["spec"]["intent"]),render_profile=profile)
    oid=s.observe({"fixture":"explicit test"})
    s.draw([(10,10),(25,20),(40,14)],observation_id=oid)
    s.draw([(10,30),(25,37),(40,28)],observation_id=oid)
    s.soft_lift("h0001",strength=.4,reason="correct",observation_id=oid)
    s.inspect(supersample=2)
    s.record_evidence_read(s.inspection_history[-1]["inspection_id"])
    replay=s.export_timelapse(evidence/"replay",backend="canonical",every_n=2)
    final=s.render_final(evidence/"final.png")
    Image.new("RGB",(64,64),"white").save(evidence/"comparison.png")
    (evidence/"review.md").write_text("fixture metadata, not visual proof")
    paths={"session":s.checkpoint_path,"final_png":final.path,"timelapse_gif":replay.gif_path,
           "comparison":evidence/"comparison.png","review":evidence/"review.md"}
    run={"schema":protocol.RUN_SCHEMA,"case_digest":case_record["case_digest"],
         "arm":"v1.3.0","commit":"1"*40,"worker_run_id":"not-fresh-fixture",
         "freshness":{"status":"not_fresh","evidence":"developer fixture"},
         "usage":{"actions":3,"wall_seconds":2,"tokens":None},
         "artifacts":{k:{"file":v.relative_to(evidence).as_posix(),"sha256":protocol.file_digest(v)} for k,v in paths.items()}}
    report=campaign.verify_submitted_replay(case_record,ref,run,evidence,replay.manifest_path)
    assert report["status"]=="ENDPOINTS_VERIFIED"
    assert report["visual_verdict"]=="NOT_EVALUATED"
    assert report["freshness_attestation"]=="not_fresh"
    audited=campaign.verify_submitted_replay(case_record,ref,run,evidence,replay.manifest_path,
                                             sample_audit_budget=1_000_000)
    assert audited["all_intermediate_frames"]=="ALL_SAMPLES_VERIFIED"
    assert audited["sample_audit"]["sample_count"]==3
    assert audited["sample_audit"]["sampled_hashes_matched"]==3
    manifest=json.loads(replay.manifest_path.read_text())
    with pytest.raises(ValueError,match="pixel-work budget"):
        campaign.verify_sampled_frames(s,manifest,replay.gif_path,max_pixel_work=1)
    from copy import deepcopy
    corrupted=deepcopy(manifest)
    corrupted["frames"][1]["pixel_sha256"]="0"*64
    with pytest.raises(ValueError,match="regenerated sample hash mismatch"):
        campaign.verify_sampled_frames(s,corrupted,replay.gif_path,max_pixel_work=1_000_000)
    # A forged GIF may retain valid endpoints and an updated file hash, but its
    # wrong middle frame must fail strict sampled-frame verification.
    forged=evidence/"forged.gif"
    with Image.open(replay.gif_path) as image:
        image.seek(0); first=image.convert("RGB")
        image.seek(image.n_frames-1); last=image.convert("RGB")
    with first,last,Image.new("RGB",first.size,"black") as bad:
        first.save(forged,save_all=True,append_images=[bad,last],duration=100,loop=0)
    corrupted=deepcopy(manifest)
    corrupted["gif"].update(sha256=protocol.file_digest(forged),bytes=forged.stat().st_size)
    result=campaign.verify_sampled_frames(s,corrupted,forged,max_pixel_work=1_000_000)
    assert result["status"]=="SAMPLE_TOLERANCE_FAILED"
    assert any(row["cursor"]==2 for row in result["out_of_tolerance"])
    m=json.loads(replay.manifest_path.read_text());m["frames"][0]["cursor"]=1
    replay.manifest_path.write_text(json.dumps(m))
    with pytest.raises(ValueError,match="sampling"):
        campaign.verify_submitted_replay(case_record,ref,run,evidence,replay.manifest_path)
