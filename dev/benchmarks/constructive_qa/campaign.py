#!/usr/bin/env python3
"""Prepare isolated worker packets and check submitted replay evidence.

The coordinator does not run an agent, establish freshness from an ID, or
award artistic acceptance. The evaluator uses the pinned arm's installed runtime.
"""
from __future__ import annotations

import argparse
from io import BytesIO
import json
from pathlib import Path, PurePosixPath
import subprocess
import tarfile
from tempfile import TemporaryDirectory
from zipfile import ZipFile, ZIP_DEFLATED

import numpy as np
from PIL import Image

from protocol import (ARMS, BASELINES, GIT_SHA, artifact_path, file_digest,
                      nonempty, read_json, validate_case, validate_run)

SKILL="skills/img2drawing"
PACKET_SCHEMA="img2drawing.constructive_qa.worker_packet.v1"
SUPPORTED_REFERENCE_FORMATS={"PNG":".png","JPEG":".jpg","WEBP":".webp"}


def _write_json(path,value):
    with Path(path).open("x",encoding="utf-8") as f:
        json.dump(value,f,indent=2,ensure_ascii=False,allow_nan=False)
        f.write("\n")


def validate_arm(arm,commit):
    if arm not in ARMS or not isinstance(commit,str) or not GIT_SHA.fullmatch(commit):
        raise ValueError("explicit arm and full commit SHA required")
    if arm in BASELINES and commit!=BASELINES[arm]:
        raise ValueError("baseline commit drift")
    if arm=="v1.3.0" and commit in BASELINES.values():
        raise ValueError("candidate must differ from the baseline commits")


def _skill_members(repository,commit):
    actual=subprocess.check_output(["git","rev-parse",commit+"^{commit}"],cwd=repository,text=True).strip()
    if actual!=commit:
        raise ValueError("commit pin mismatch")
    data=subprocess.check_output(["git","archive","--format=tar",commit,SKILL],cwd=repository)
    with tarfile.open(fileobj=BytesIO(data),mode="r:") as archive:
        for member in archive.getmembers():
            path=PurePosixPath(member.name)
            if member.isdir():
                continue
            if (not member.isfile() or path.is_absolute() or ".." in path.parts
                    or tuple(path.parts[:2])!=("skills","img2drawing")
                    or "__pycache__" in path.parts or ".git" in path.parts
                    or path.suffix in {".pyc",".zip",".gif"}):
                raise ValueError("unexpected file in deployable skill archive")
            yield path.as_posix(), archive.extractfile(member).read()


def prepare_worker_packet(repository,case,reference,arm,commit,worker_run_id,output):
    """One ZIP with only the selected skill, original reference and ordinary task."""
    validate_case(case,reference)
    validate_arm(arm,commit)
    nonempty(worker_run_id,"worker_run_id")
    output=Path(output)
    if output.suffix.lower()!=".zip" or output.exists():
        raise ValueError("worker packet requires a new ZIP")
    with Image.open(reference) as image:
        ext=SUPPORTED_REFERENCE_FORMATS.get(image.format)
        if ext is None:
            raise ValueError("PNG/JPEG/WEBP reference required")
        image.verify()
    refname="reference"+ext
    spec=case["spec"]
    task={"schema":PACKET_SCHEMA,"case_digest":case["case_digest"],"arm":arm,
          "commit":commit,"worker_run_id":worker_run_id,
          "reference":refname,"reference_sha256":case["reference"]["sha256"],
          "user_request":spec["user_request"],"intent":spec["intent"],
          "canvas":spec["canvas"],"worker":spec["worker"],"budget":spec["budget"],
          "instructions":"Use only the supplied reference and packaged skill. Read SKILL.md and the public API route. Start a new DrawingSession, author explicit strokes, inspect and correct. No image generation, tracing, prior output, or evaluator geometry. Keep session, final PNG, complete action-0-to-latest GIF, replay_manifest.json, comparison and review. Report actual resource use and freshness evidence. Do not award your own independent visual verdict."}
    members=list(_skill_members(repository,commit))
    names=[name for name,_ in members]
    if len(set(names))!=len(names) or SKILL+"/SKILL.md" not in names:
        raise ValueError("invalid skill member set")
    output.parent.mkdir(parents=True,exist_ok=True)
    try:
        with ZipFile(output,"x",compression=ZIP_DEFLATED) as z:
            z.writestr("task.json",json.dumps(task,indent=2,ensure_ascii=False,allow_nan=False)+"\n")
            z.write(reference,refname)
            for name,data in members:
                z.writestr(name,data)
    except BaseException:
        output.unlink(missing_ok=True)
        raise
    return {"case_digest":case["case_digest"],"arm":arm,"commit":commit,
            "worker_run_id":worker_run_id,"packet_sha256":file_digest(output),
            "files":len(members)+2,"status":"PREPARED_NOT_EXECUTED"}


def _rgba(path):
    with Image.open(path) as im:
        return np.asarray(im.convert("RGBA"))


def _rgb_error(a,b):
    if a.shape!=b.shape:
        raise ValueError("GIF frame size differs from canonical render")
    diff=np.abs(a.astype(np.int16)-b.astype(np.int16))
    return {"max":int(diff.max()),"mean":float(diff.mean())}


def verify_submitted_replay(case,reference,run,evidence_root,replay_manifest):
    """Check actual checkpoint/PNG/GIF endpoints and sampling metadata.

    This is intentionally NOT an all-frame audit, worker isolation attestation,
    or visual quality verdict. The coordinator must select the correct pinned
    runtime separately, with trusted worker and evaluator provenance.
    """
    from img2drawing import DrawingSession, __version__
    from img2drawing.render.artifact import rgb_sha256
    from img2drawing.timelapse import sample_cursors
    from img2drawing.timelapse.export import (_FAST_GIF_TOLERANCE,
        _CANONICAL_GIF_TOLERANCE, REPLAY_EXPORT_SCHEMA)

    validate_case(case,reference)
    validate_run(run,case,evidence_root)
    validate_arm(run["arm"],run["commit"])
    if run["arm"] in BASELINES and __version__!=run["arm"][1:]:
        raise ValueError("evaluator must use the pinned baseline runtime")
    paths={k:artifact_path(evidence_root,v["file"]) for k,v in run["artifacts"].items()}
    mp=Path(replay_manifest).resolve()
    if not mp.is_relative_to(Path(evidence_root).resolve()) or not mp.is_file():
        raise ValueError("replay manifest must be inside evidence root")
    manifest=read_json(mp)
    checkpoint=read_json(paths["session"])
    if manifest["schema"]!=REPLAY_EXPORT_SCHEMA:
        raise ValueError("unsupported replay manifest schema")
    before=file_digest(paths["session"])
    with TemporaryDirectory() as folder:
        # Resume in an isolated scratch output; never write into worker evidence.
        session=DrawingSession.resume(paths["session"],subject=reference,output_dir=folder)
        cursor=session.history_cursor
        spec=case["spec"]
        if cursor!=run["usage"]["actions"] or len(checkpoint["history"]["actions"])!=cursor:
            raise ValueError("action count/cursor differs from submitted usage")
        if (session.width,session.height)!=(spec["canvas"]["width"],spec["canvas"]["height"]):
            raise ValueError("canvas differs from sealed case")
        if session.intent is None or any(getattr(session.intent,k)!=v for k,v in spec["intent"].items()):
            raise ValueError("intent differs from sealed case")
        if (manifest["session_id"]!=session.session_id or manifest["history"]["latest_cursor"]!=cursor
                or manifest["history"]["action_count"]!=cursor
                or manifest["history"]["action_log_sha256"]!=checkpoint["digests"]["action_log_sha256"]
                or manifest["render_profile"]!=session.render_profile.to_dict()
                or manifest["render_profile_digest"]!=session.render_profile.digest()):
            raise ValueError("replay manifest does not bind to submitted canonical history")
        sampling=manifest["sampling"]
        step=1 if sampling["mode"]=="action" else sampling["every_n"]
        cursors=sample_cursors(cursor,sampling["mode"],step)
        if (not sampling["action_zero_included"] or not sampling["latest_included"]
                or [f["cursor"] for f in manifest["frames"]]!=cursors):
            raise ValueError("replay sampling does not cover canonical history")
        root=Path(folder)
        start=session.render_at(0,root/"blank.png")
        final=session.render_final(root/"final.png")
        if not np.array_equal(_rgba(final.path),_rgba(paths["final_png"])):
            raise ValueError("submitted final PNG differs from independently rendered history")
        with Image.open(final.path) as im:
            final_rgb=rgb_sha256(im)
        f=manifest["final"]
        if (not f["last_frame_pixel_match"] or f["pixel_sha256"]!=final.pixel_sha256
                or f["rgb_sha256"]!=final_rgb):
            raise ValueError("final replay hash mismatch")
        last=manifest["frames"][-1]
        if last["pixel_hash_mode"] not in ("RGB","RGBA"):
            raise ValueError("unknown replay frame hash mode")
        if last["pixel_sha256"]!=(final_rgb if last["pixel_hash_mode"]=="RGB" else final.pixel_sha256):
            raise ValueError("last unquantized frame mismatch")
        gif=manifest["gif"]
        if gif["sha256"]!=file_digest(paths["timelapse_gif"]) or gif["bytes"]!=paths["timelapse_gif"].stat().st_size:
            raise ValueError("GIF hash/size mismatch")
        backend=manifest["backend"]["selected"]
        if backend not in ("canonical","fast"):
            raise ValueError("unknown selected backend")
        tolerance=_FAST_GIF_TOLERANCE if backend=="fast" else _CANONICAL_GIF_TOLERANCE
        with Image.open(paths["timelapse_gif"]) as im:
            if im.format!="GIF":
                raise ValueError("submitted replay is not a GIF")
            frames=im.n_frames
            if frames<1:
                raise ValueError("empty GIF")
            first=np.asarray(im.convert("RGB"))
            im.seek(frames-1)
            last_frame=np.asarray(im.convert("RGB"))
        errors=[_rgb_error(first,_rgba(start.path)[:,:,:3]),
                _rgb_error(last_frame,_rgba(final.path)[:,:,:3])]
        if any(e["max"]>tolerance["max_channel_error"] or e["mean"]>tolerance["mean_channel_error"] for e in errors):
            raise ValueError("actual GIF endpoint fidelity exceeds pinned runtime tolerance")
    if file_digest(paths["session"])!=before:
        raise RuntimeError("verification modified submitted checkpoint")
    return {"status":"ENDPOINTS_VERIFIED","case_digest":case["case_digest"],
            "arm":run["arm"],"commit":run["commit"],"runtime_version":__version__,
            "cursor":cursor,"manifest_sample_count":len(cursors),"decoded_gif_frames":frames,
            "first_frame_error":errors[0],"last_frame_error":errors[1],
            "freshness_attestation":run["freshness"]["status"],
            "all_intermediate_frames":"NOT_VERIFIED","visual_verdict":"NOT_EVALUATED",
            "replay_manifest_sha256":file_digest(mp)}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    sub=p.add_subparsers(dest="command",required=True)
    packet=sub.add_parser("packet")
    for name in ("repository","case","reference","arm","commit","worker_run_id","output","receipt"):
        packet.add_argument(name)
    replay=sub.add_parser("verify-replay")
    for name in ("case","reference","run","evidence_root","replay_manifest","report"):
        replay.add_argument(name)
    a=p.parse_args()
    if a.command=="packet":
        result=prepare_worker_packet(a.repository,read_json(a.case),a.reference,a.arm,a.commit,a.worker_run_id,a.output)
        _write_json(a.receipt,result)
    else:
        result=verify_submitted_replay(read_json(a.case),a.reference,read_json(a.run),a.evidence_root,a.replay_manifest)
        _write_json(a.report,result)
    print(json.dumps(result,indent=2))


if __name__=="__main__":
    main()
