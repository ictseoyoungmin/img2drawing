from __future__ import annotations
import pytest
from PIL import Image
from img2drawing import DrawingSession
from img2drawing.authoring import (SemanticGroup, record_semantic_groups, inspect_semantic_groups,
    review_semantic_group, prepare_group_transform, retire_group_guides,
    apply_stroke_edits, preview_stroke_edits, StrokeEdit)


def session_fixture(tmp_path):
    ref=tmp_path/"ref.png"
    Image.new("RGB",(64,64),"white").save(ref)
    s=DrawingSession.create(subject=ref,output_dir=tmp_path/"run")
    oid=s.observe({"test":"declared physical relations"})
    for sid, y in (("head",10),("eye",20),("guide",30),("unrelated",40)):
        s.draw([(10,y),(20,y),(30,y)],stroke_id=sid,observation_id=oid)
    return s,oid,ref


def declaration(s):
    return record_semantic_groups(s,[SemanticGroup("head",("head","guide"),guide_ids=("guide",)),
        SemanticGroup("eye",("eye",),depends_on=("head",))],evidence="explicit geometry ownership")


def read(s):
    s.inspect(supersample=1)
    iid=s.inspection_history[-1]["inspection_id"]
    s.record_evidence_read(iid)
    return iid


def test_graph_validation_before_mutation(tmp_path):
    s,oid,ref=session_fixture(tmp_path)
    before=s.checkpoint_path.read_bytes()
    for groups in [
        [SemanticGroup("a",("head",),depends_on=("b",)),SemanticGroup("b",("eye",),depends_on=("a",))],
        [SemanticGroup("a",("head",)),SemanticGroup("b",("head",))],
        [SemanticGroup("a",("missing",))],
        [SemanticGroup("a",("head",),depends_on=("missing",))],
    ]:
        with pytest.raises(ValueError):
            record_semantic_groups(s,groups,evidence="test")
        assert s.checkpoint_path.read_bytes()==before


def test_review_dependency_and_unrelated_changes(tmp_path):
    s,oid,ref=session_fixture(tmp_path)
    plan=declaration(s)
    iid=read(s)
    with pytest.raises(ValueError,match="dependency"):
        review_semantic_group(s,plan,"eye",inspection_id=iid,evidence="review")
    review_semantic_group(s,plan,"head",inspection_id=iid,evidence="visible head relation")
    review_semantic_group(s,plan,"eye",inspection_id=iid,evidence="visible eye relation")
    assert not any(g["review_required"] for g in inspect_semantic_groups(s,plan)["groups"].values())
    s.replace_segment("unrelated",0,1,[(10,40),(15,41),(20,40)],observation_id=oid,reason="unrelated")
    assert not any(g["review_required"] for g in inspect_semantic_groups(s,plan)["groups"].values())
    edit=prepare_group_transform(s,plan,"head",(1,0,0,1,2,1))
    apply_stroke_edits(s,edit["edits"],reason="correct head",observation_id=oid,
                       expected_cursor=edit["base_cursor"],expected_state_hash=edit["base_state_hash"])
    rows=inspect_semantic_groups(s,plan)["groups"]
    assert rows["head"]["review_required"] and "dependency_review_required" in rows["eye"]["reasons"]
    with pytest.raises(ValueError,match="current inspection"):
        review_semantic_group(s,plan,"head",inspection_id=iid,evidence="stale")
    iid=read(s)
    review_semantic_group(s,plan,"head",inspection_id=iid,evidence="head rechecked")
    assert inspect_semantic_groups(s,plan)["groups"]["eye"]["review_required"]
    review_semantic_group(s,plan,"eye",inspection_id=iid,evidence="eye rechecked")
    resumed=DrawingSession.resume(s.checkpoint(),subject=ref)
    assert inspect_semantic_groups(resumed,plan)==inspect_semantic_groups(s,plan)


def test_guide_retirement_preserves_descriptive_marks(tmp_path):
    s,oid,ref=session_fixture(tmp_path)
    plan=declaration(s)
    before=s.checkpoint_path.read_bytes()
    with pytest.raises(ValueError,match="only explicitly"):
        retire_group_guides(s,plan,"head",["guide","head"],reason="retire",observation_id=oid)
    assert before==s.checkpoint_path.read_bytes()
    ids=retire_group_guides(s,plan,"head",["guide"],reason="description replaced guide",observation_id=oid)
    assert len(ids)==1 and s.history_cursor==5
    row=inspect_semantic_groups(s,plan)["groups"]["head"]
    assert row["current_ids"]==["head"] and row["retired_guide_ids"]==["guide"]
    assert row["review_required"]
    assert set(v.stroke_id for v in s.current_ir().strokes)=={"head","eye","unrelated"}


def test_replacement_descendants_and_split_are_not_silent_members(tmp_path):
    s,oid,ref=session_fixture(tmp_path)
    plan=declaration(s)
    s.replace_stroke("head",[(12,10),(22,10),(32,10)],stroke_id="head-v2",
                     observation_id=oid,reason="parent shape")
    row=inspect_semantic_groups(s,plan)["groups"]["head"]
    assert row["current_ids"]==["head-v2","guide"]
    current=s.current_stroke("head-v2")
    apply_stroke_edits(s,[StrokeEdit("head-v2",tuple(current.points),split_at=1,new_stroke_id="tail")],
                       reason="split",observation_id=oid)
    row=inspect_semantic_groups(s,plan)["groups"]["head"]
    assert row["unassigned_split_ids"]==["tail"]
    with pytest.raises(ValueError,match="redeclare"):
        prepare_group_transform(s,plan,"head",(1,0,0,1,1,0))
    s.replace_segment("tail",0,1,[tuple(s.current_stroke("tail").points[0]),(27,11),tuple(s.current_stroke("tail").points[-1])],observation_id=oid,reason="edit tail")
    assert inspect_semantic_groups(s,plan)["groups"]["head"]["unassigned_split_ids"]==["tail"]
    new=record_semantic_groups(s,[SemanticGroup("head",("head-v2","guide","tail"),guide_ids=("guide",)),
        SemanticGroup("eye",("eye",),depends_on=("head",))],evidence="explicit membership after split")
    assert not inspect_semantic_groups(s,new)["groups"]["head"]["unassigned_split_ids"]


def test_deleted_descriptive_member_remains_blocking(tmp_path):
    s,oid,ref=session_fixture(tmp_path)
    plan=declaration(s)
    s.delete_stroke("head",reason="reopen structure",observation_id=oid)
    row=inspect_semantic_groups(s,plan)["groups"]["head"]
    assert row["missing_ids"]==["head"]
    with pytest.raises(ValueError,match="missing"):
        review_semantic_group(s,plan,"head",inspection_id=read(s),evidence="not resolved")
