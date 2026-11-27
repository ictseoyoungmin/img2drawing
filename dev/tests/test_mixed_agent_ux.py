"""S05 public guide exercise and mixed worker completion/provenance regressions."""
from pathlib import Path
import re
import subprocess
import sys
from dataclasses import replace

import pytest

from img2drawing import DrawingSession, DrawingIntent, ReferenceAuthority, RenderProfile
from img2drawing.authoring import InkAction, InkElement, solid_ink, dot_screentone, apply_ink_actions
from img2drawing.runtime import runtime_capabilities

ROOT=Path(__file__).resolve().parents[2]
SKILL=ROOT/"skills"/"img2drawing"
GUIDE=SKILL/"references"/"api"/"mixed-media.md"


def test_exact_guide_smoke_runs_in_fresh_process(tmp_path):
    text=GUIDE.read_text(encoding="utf-8")
    blocks=re.findall(r"```python\n(# mixed-media-smoke\n.*?)\n```",text,flags=re.S)
    assert len(blocks)==1
    code=blocks[0]
    assert "._agent" not in code and "img2drawing.core" not in code
    assert "img2drawing.render" not in code and "PIL" not in code
    program=tmp_path/"run.py"
    program.write_text(code,encoding="utf-8")
    result=subprocess.run([sys.executable,str(program)],cwd=tmp_path,capture_output=True,
                          text=True,check=False,timeout=120)
    assert result.returncode==0,result.stdout+result.stderr
    assert "MIXED_MEDIA_PUBLIC_EXAMPLE_PASS" in result.stdout
    assert (tmp_path/"mixed-demo"/"timelapse"/"timelapse.gif").is_file()


def _session(tmp_path,mixed=True):
    return DrawingSession.create(canvas=(80,64),output_dir=tmp_path/"session",
        intent=DrawingIntent(reference_mode="imaginative",drawing_mode="free_draw"),
        reference_authority=ReferenceAuthority.imaginative(("synthetic mechanics fixture",)),
        render_profile=RenderProfile.mixed_media(80,64) if mixed else None)


def _read(s):
    s.inspect()
    iid=s.inspection_history[-1]["inspection_id"]
    # Mechanical test only: ensure generated fixture artifact is readable, not
    # claim that a real drawing worker has evaluated the art.
    s.record_evidence_read(iid)
    return iid


def _rect():
    return ((10,10),(60,10),(60,50),(10,50),(10,10))


def test_ink_only_finish_resume_and_summary(tmp_path):
    s=_session(tmp_path)
    oid=s.observe({"fixture":"ink-only completion"})
    el=InkElement("mass",solid_ink(_rect()),"value")
    apply_ink_actions(s,[InkAction("a","ink.add","mass",el,oid,"fixture","author")])
    counts=s.authoring_summary().to_dict()["counts"]
    assert counts["current_strokes"]==0 and counts["current_ink"]==1 and counts["deleted_ink"]==0
    iid=_read(s)
    record=s.finish(final_inspection_id=iid,rationale="mechanical ink-only finish fixture")
    resumed=DrawingSession.resume(s.checkpoint())
    assert resumed.finish_is_current and resumed.finish_record==record
    apply_ink_actions(resumed,[InkAction("b","ink.delete","mass",None,oid,"fixture","retire")])
    assert not resumed.finish_is_current
    counts=resumed.authoring_summary().to_dict()["counts"]
    assert counts["current_ink"]==0 and counts["deleted_ink"]==1
    iid=_read(resumed)
    with pytest.raises(ValueError,match="canvas is blank"):
        resumed.finish(final_inspection_id=iid,rationale="blank fixture must reject")


def test_legacy_summary_keys_and_default_discovery_unchanged(tmp_path):
    s=_session(tmp_path,mixed=False)
    assert set(s.authoring_summary().to_dict()["counts"])=={
        "current_strokes","superseded_strokes","deleted_strokes","open_residuals"}
    assert not s.render_profile.is_mixed_media
    assert "ink-add" not in runtime_capabilities().authoring_operations


def test_ink_residual_uses_action_identity_and_current_evidence(tmp_path):
    s=_session(tmp_path)
    oid=s.observe({"fixture":"tone value residual"})
    el=InkElement("tone",dot_screentone(_rect(),coverage=.8),"value")
    apply_ink_actions(s,[InkAction("a","ink.add","tone",el,oid,"fixture","author")])
    before=_read(s)
    rid=s.record_residual(observation_id=oid,observation="tone too dark for declared fixture",
        scope="tone",severity="material",impact_rationale="value contrast",
        responsible_premise="explicit coverage",responsible_stroke_ids=("tone",),
        planned_edit="reduce coverage",before_inspection_id=before)
    other=s.observe({"fixture":"other observation"})
    new=replace(el,mark=replace(el.mark,coverage=.4))
    wrong=InkAction("b","ink.replace","tone",new,other,"fixture","wrong observation")
    apply_ink_actions(s,[wrong])
    iid=_read(s)
    with pytest.raises(ValueError,match="correction action observation mismatch"):
        s.resolve_residual(rid,action_ids=("b",),after_inspection_id=iid,rationale="must reject")
    fixed=replace(el,mark=replace(el.mark,coverage=.35))
    ids=apply_ink_actions(s,[InkAction("c","ink.replace","tone",fixed,oid,"fixture","correct")])
    iid=_read(s)
    assert s.resolve_residual(rid,action_ids=ids,after_inspection_id=iid,
                              rationale="mechanical correction fixture").action_ids==("c",)
    assert s.finish(final_inspection_id=iid,rationale="mechanical fixture").history_cursor==3


def test_conditional_routes_are_bounded_and_preserve_authority():
    skill=(SKILL/"SKILL.md").read_text()
    index=(SKILL/"references"/"INDEX.md").read_text()
    visual=(SKILL/"references"/"markmaking"/"mixed-media.md").read_text()
    api=GUIDE.read_text()
    assert "conditional mixed-media route" in skill and "canonical pencil default" in skill
    assert index.count("`markmaking/mixed-media.md`")==1
    assert index.count("`api/mixed-media.md`")==1
    assert "not an artistic verdict" in visual
    assert "No automatic closure" in api and "No dot-per-action expansion" in api
    assert "TonalAreaPlan" in (SKILL/"references"/"api"/"public-surface.md").read_text()
    assert len(visual.encode())<=5000 and len(api.encode())<=10500
