"""Tonal QA must measure explicit plans, not infer artwork or mutate history."""
import importlib.util
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
from PIL import Image
from img2drawing import DrawingSession, DrawingIntent
from img2drawing.authoring import TonalAreaPlan, resolve_mark_for_intent

path = Path(__file__).resolve().parents[1] / "benchmarks/tonal_qa/session_delta.py"
spec = importlib.util.spec_from_file_location("tonal_session_delta", path)
qa = importlib.util.module_from_spec(spec)
spec.loader.exec_module(qa)


def plan(**changes):
    fields = dict(area_id="test", part="swatch", reference_evidence="analytic QA",
                  boundary=((2,2),(8,2),(8,8),(2,8)), direction_degrees=90,
                  target_density=.5, target_value=.5, pressure_range=(.2,.7),
                  highlight_reserves=(((4,4),(6,4),(6,6),(4,6)),))
    fields.update(changes)
    return TonalAreaPlan(**fields)


def test_measurement_exact_masks_and_strict_threshold():
    white = np.ones((10, 10))
    before = white.copy()
    after = white.copy()
    after[2:8,2:8] = .2
    after[4:6,4:6] = 1
    result = qa.measure_plan(white, before, after, plan())
    assert result["target_pixels"] == 32
    assert result["protected_pixels"] == 4
    assert result["target_after"]["coverage"] == 1
    assert result["target_after"]["saturation"] == 1
    assert result["protected_after"]["coverage"] == 0
    assert result["outside_added_darkness_fraction"] == 0
    after[4:6,4:6] = 1 - 8/255
    assert qa.measure_plan(white, before, after, plan())["protected_after"]["coverage"] == 0
    after[4:6,4:6] = 1 - 9/255
    assert qa.measure_plan(white, before, after, plan())["protected_after"]["coverage"] == 1


def test_scale_removal_and_outside_change():
    white = np.ones((20,20))
    before = white.copy()
    before[4:16,4:16] = .1
    after = white.copy()
    after[0,0] = .2
    r = qa.measure_plan(white, before, after, plan(), scale=2)
    assert r["target_pixels"] == 128
    assert r["target_removed_mean"] == pytest.approx(.9)
    assert r["protected_after"]["mean_darkness"] == 0
    assert r["outside_added_darkness_fraction"] == 1
    assert qa.measure_plan(white, white, white, plan(), scale=2)["outside_added_darkness_fraction"] is None


def test_empty_and_outside_reserves_are_explicit():
    white = np.ones((10,10))
    r = qa.measure_plan(white, white, white, plan(highlight_reserves=()))
    assert r["protected_before"] is None and r["protected_pixels"] == 0
    r = qa.measure_plan(white, white, white,
                        plan(highlight_reserves=(((0,0),(4,0),(4,4),(0,4)),)))
    assert r["reserve_outside_area_pixels"] == 12
    with pytest.raises(ValueError):
        qa.measure_plan(white, white[:2], white, plan())


def test_plan_lookup_snapshot_and_digest_guard():
    p = plan()
    raw = p.stroke_metadata(stroke_family="one")["tonal_area"]
    stroke = SimpleNamespace(tool_state={"provenance":{"metadata":{"tonal_area":raw}}})
    class Session:
        calls = 0
        def current_ir(self):
            self.calls += 1
            return SimpleNamespace(strokes=[stroke]*100)
    s = Session()
    assert qa.plans_from_current_strokes(s)["test"].digest() == p.digest()
    assert s.calls == 1
    raw["digest"] = "bad"
    with pytest.raises(ValueError, match="digest"):
        qa.plans_from_current_strokes(s)


def test_canonical_session_audit_preserves_history(tmp_path):
    ref = tmp_path / "ref.png"
    Image.new("RGB", (32,32), "white").save(ref)
    s = DrawingSession.create(subject=ref, output_dir=tmp_path/"session",
                              intent=DrawingIntent(drawing_mode="croquis"))
    p = plan(boundary=((3,3),(29,3),(29,29),(3,29)),
             highlight_reserves=(((12,12),(20,12),(20,20),(12,20)),))
    m = resolve_mark_for_intent(s.intent, "value", tool_preset="broad-graphite",
                               modifiers={"width":4,"pressure":.6,"opacity":.7})
    sid = s.draw([(5,6),(16,16),(27,26)], part="swatch",
                 **m.draw_kwargs(metadata=p.stroke_metadata(stroke_family="one")))
    state, cursor = s.drawing_state_hash(), s.history_cursor
    r = qa.audit(s, 0, cursor)
    assert r["areas"][0]["target_after"]["coverage"] > 0
    assert r["areas"][0]["protected_after"]["coverage"] > 0
    assert (s.history_cursor, s.drawing_state_hash()) == (cursor, state)
    assert s.current_stroke(sid).part == "swatch"
    with pytest.raises(ValueError):
        qa.audit(s, 1, 1)
