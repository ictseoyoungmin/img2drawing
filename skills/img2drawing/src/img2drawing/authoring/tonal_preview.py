"""Measure explicit alternative stroke batches against the same observed tonal chains."""
from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from tempfile import TemporaryDirectory

from ..inspection.tonal import _delta_arrays, _measure_delta, _verified_cached_renders, gray
from ..inspection.tonal_patches import _inputs, _measure, _slices
from .stroke_edits import preview_stroke_edits
from .tonal_area import TonalAreaPlan


def inspect_tonal_proposals(session, proposals, chains, out_dir, *, reason, observation_id,
                            plans=(), deadband=8/255, cached_renders=None, max_pixel_work=100_000_000):
    """Compare 1–4 caller-authored alternatives without applying or ranking them.

    Each proposal is a mapping of edits/retire_ids/additions/erasures. Chains and
    plans are explicitly selected, identical for every alternative. Candidate
    reports bind the existing preview action digest, state and pixel hash.
    Measurements are evidence, not a stroke optimizer or artistic verdict.
    """
    if not isinstance(proposals, Mapping) or not 1<=len(proposals)<=4:
        raise ValueError("choose 1–4 named proposals")
    if not isinstance(chains, Mapping) or not 1<=len(chains)<=8:
        raise ValueError("choose 1–8 named tonal chains")
    for name in (*proposals,*chains):
        if not isinstance(name,str) or not name.strip() or len(name)>128:
            raise ValueError("bounded nonempty names required")
    plans=tuple(plans)
    if len(plans)>8 or any(not isinstance(p,TonalAreaPlan) for p in plans) or len({p.area_id for p in plans})!=len(plans):
        raise ValueError("choose at most eight distinct explicit area plans")
    allowed={"edits","retire_ids","additions","erasures"}
    if any(not isinstance(p,Mapping) or set(p)-allowed for p in proposals.values()):
        raise ValueError("proposals contain unsupported edit fields")
    folder=Path(out_dir)
    with session._lock:
        subject_path=session.require_reference("tonal proposal comparison")
        session._assert_subject_current()
        cursor,state=session.history_cursor,session.drawing_state_hash()
        profile=session.render_profile
        scale=profile.output_scale
        chain_inputs={name:_inputs(patches,deadband,scale)[0] for name,patches in chains.items()}
        work=(len(proposals)+2)*profile.canvas_width*profile.canvas_height*(scale*profile.supersample)**2
        if type(max_pixel_work) is not int or max_pixel_work<=0 or work>max_pixel_work:
            raise ValueError(f"tonal proposal pixel-work budget exceeded: {work}")
        cache=_verified_cached_renders(session,profile,cached_renders,{0,cursor})
        subject=gray(subject_path)
        shape=(profile.canvas_height*scale,profile.canvas_width*scale)
        for patches in chain_inputs.values():
            for p in patches:
                _slices(p.subject_box,subject.shape)
                _slices(p.canvas_box,shape,scale)
        # Never overwrite an existing evidence directory or its artifacts.
        folder.mkdir(parents=True,exist_ok=False)
        with TemporaryDirectory() as tmp:
            def load(n):
                path=cache.get(n,Path(tmp)/f"{n}.png")
                if n not in cache and not path.exists():
                    session.render_at(n,path)
                return gray(path)
            paper,before=load(0),load(cursor)
            baseline={name:_measure(subject,before,paper,patches,float(deadband),scale) for name,patches in chain_inputs.items()}
            results={}
            for i,(name,proposal) in enumerate(proposals.items()):
                path=folder/f"candidate-{i+1:02d}.png"
                args=dict(proposal)
                edits=args.pop("edits",())
                preview=preview_stroke_edits(session,edits,path,reason=reason,observation_id=observation_id,**args)
                after=gray(path)
                arrays=_delta_arrays(paper,before,after,scale,8/255,.65)
                results[name]={"image":str(path),"preview":preview,
                    "chains":{label:_measure(subject,after,paper,patches,float(deadband),scale) for label,patches in chain_inputs.items()},
                    "areas":[_measure_delta(arrays,p,scale=scale,coverage_threshold=8/255,saturation_threshold=.65) for p in plans]}
        session._assert_subject_current()
        if session.history_cursor!=cursor or session.drawing_state_hash()!=state or session.render_profile.digest()!=profile.digest():
            raise RuntimeError("session changed during proposal inspection")
        return {"base_cursor":cursor,"base_state_hash":state,"profile_digest":profile.digest(),
                "baseline":baseline,"proposals":results,"pixel_work_upper_bound":work,
                "evidence_binding":"detached previews, not committed renders","artistic_verdict":"NOT_EVALUATED"}
