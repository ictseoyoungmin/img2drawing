"""Region fill, tone calibration, and compact canonical serialization."""

import json
import math
from pathlib import Path

import pytest

from img2drawing import (
    DrawingSession, FillRegion, PoseObservation, ReservedLight, available_values,
    expand_fill, resolve_tone,
)
from img2drawing.core.fill import _scanline_spans

SQUARE = [(0.0, 0.0), (200.0, 0.0), (200.0, 200.0), (0.0, 200.0)]


def _session(tmp_path: Path, subject: Path) -> DrawingSession:
    s = DrawingSession.create(subject=subject, output_dir=Path(tmp_path) / "out")
    s.observe(PoseObservation(
        support_side="left", flow="down", head_ribcage_pelvis="stacked",
        shoulder_pelvis="level",
    ), observation_id="observation-0001")
    return s


@pytest.fixture
def subject(tmp_path: Path) -> Path:
    from PIL import Image
    p = tmp_path / "subject.png"
    Image.new("RGB", (240, 240), "white").save(p)
    return p


# ---------------------------------------------------------------- geometry ----------
def test_straight_hatch_is_two_points_not_a_sampled_polyline():
    region = FillRegion(fill_id="f", polygon=SQUARE, angle=90.0, spacing=10.0, part="t")
    lines = expand_fill(region)
    assert lines, "a filled square must produce hatch"
    assert {len(l["points"]) for l in lines} == {2}, "a straight run stores its endpoints only"


def test_concave_region_splits_into_separate_runs():
    u = [(0, 0), (200, 0), (200, 200), (140, 200), (140, 60), (60, 60), (60, 200), (0, 200)]
    region = FillRegion(fill_id="f", polygon=u, angle=0.0, spacing=10.0, part="t")
    upper = [l for l in expand_fill(region) if l["points"][0][1] > 70]
    assert len(upper) >= 20, "the notch must break each line above it into two runs"
    for line in expand_fill(region):
        mid = ((line["points"][0][0] + line["points"][1][0]) / 2,
               (line["points"][0][1] + line["points"][1][1]) / 2)
        assert not (60 < mid[0] < 140 and mid[1] > 60), "hatch escaped into the notch"


def test_expansion_is_deterministic():
    region = FillRegion(fill_id="f", polygon=SQUARE, angle=37.0, spacing=7.0, part="t")
    assert expand_fill(region) == expand_fill(region)


def test_scanline_pairs_every_entry_with_an_exit():
    for angle in (0.0, 23.0, 90.0, 154.0):
        ux, uy = math.cos(math.radians(angle)), math.sin(math.radians(angle))
        for offset in (-50.0, 0.0, 37.5, 199.0):
            spans = _scanline_spans(SQUARE, ux, uy, offset)
            assert all(a <= b for a, b in spans)


def test_reserved_light_is_left_in_the_paper():
    plain = FillRegion(fill_id="f", polygon=SQUARE, angle=90.0, spacing=8.0, part="t")
    with_light = FillRegion(
        fill_id="f", polygon=SQUARE, angle=90.0, spacing=8.0, part="t",
        reserved=(ReservedLight(path=((100.0, 0.0), (100.0, 200.0)), width=40.0, strength=1.0),),
    )
    assert len(expand_fill(with_light)) < len(expand_fill(plain))
    for line in expand_fill(with_light):
        assert not (80 < line["points"][0][0] < 120), "reserved band still carries hatch"


def test_partial_reserve_thins_rather_than_clears():
    region = FillRegion(
        fill_id="f", polygon=SQUARE, angle=90.0, spacing=8.0, part="t",
        reserved=(ReservedLight(path=((100.0, 0.0), (100.0, 200.0)), width=40.0, strength=0.5),),
    )
    inside = [l for l in expand_fill(region) if 80 < l["points"][0][0] < 120]
    assert inside and all(l["attenuation"] == pytest.approx(0.5) for l in inside)


# ---------------------------------------------------------------- tone scale --------
def test_tone_scale_is_monotonic_and_reaches_dark():
    values = available_values()
    assert list(values) == sorted(values, reverse=True)
    assert min(values) <= 40, "the scale must reach a usable black"


def test_resolve_tone_picks_the_nearest_measured_step():
    assert resolve_tone(120).measured == pytest.approx(120.0, abs=12)
    assert resolve_tone(35).measured < resolve_tone(200).measured


def test_resolve_tone_rejects_values_outside_the_canvas_range():
    with pytest.raises(ValueError):
        resolve_tone(-1)


# ---------------------------------------------------------------- session ----------
def test_one_fill_is_one_canonical_action_and_many_strokes(tmp_path, subject):
    s = _session(tmp_path, subject)
    before = len(s.current_ir().strokes)
    s.fill_region([(20, 20), (200, 20), (200, 200), (20, 200)], value=95, part="coat",
                  angle=74.0, observation_id="observation-0001", reason="black coat")
    assert len(s._agent.history.actions) == 1, "a value region is one authored action"
    assert len(s.current_ir().strokes) - before > 20, "and still renders as real strokes"


def test_fill_survives_checkpoint_resume(tmp_path, subject):
    s = _session(tmp_path, subject)
    s.fill_region([(20, 20), (200, 20), (200, 200), (20, 200)], value=95, part="coat",
                  angle=74.0, observation_id="observation-0001", reason="black coat")
    expected = [(st.stroke_id, st.points) for st in s.current_ir().strokes]
    again = DrawingSession.resume(s.checkpoint_path, subject=subject, output_dir=tmp_path / "out")
    assert [(st.stroke_id, st.points) for st in again.current_ir().strokes] == expected


def test_generated_fill_strokes_remain_individually_addressable(tmp_path, subject):
    s = _session(tmp_path, subject)
    fid = s.fill_region([(20, 20), (200, 20), (200, 200), (20, 200)], value=95, part="coat",
                        angle=90.0, observation_id="observation-0001", reason="black coat")
    target = next(st for st in s.current_ir().strokes if st.stroke_id.startswith(fid))
    before = target.opacity
    s.soft_lift(target.stroke_id, observation_id="observation-0001", strength=0.5,
                reason="reserve a light after the fact")
    after = next(st for st in s.current_ir().strokes if st.stroke_id == target.stroke_id)
    assert after.opacity < before


def test_fill_requires_observation_provenance(tmp_path, subject):
    s = _session(tmp_path, subject)
    with pytest.raises(ValueError):
        s.fill_region([(20, 20), (200, 20), (200, 200)], value=95, part="coat",
                      observation_id="nope", reason="x")


def test_fill_rejects_a_polygon_off_canvas(tmp_path, subject):
    s = _session(tmp_path, subject)
    with pytest.raises(ValueError):
        s.fill_region([(20, 20), (9000, 20), (9000, 200), (20, 200)], value=95, part="coat",
                      observation_id="observation-0001", reason="off canvas")


# ------------------------------------------------- compact canonical session --------
def test_derived_pressure_is_not_persisted_but_is_restored(tmp_path, subject):
    s = _session(tmp_path, subject)
    s.draw([(10, 10), (60, 60), (120, 30)], part="axis", observation_id="observation-0001")
    payload = json.loads(s.checkpoint_path.read_text())
    stored = payload["history"]["actions"][0]["payload"]["stroke"]
    assert stored["pressure"] is None, "the tool's own taper is arithmetic, not provenance"
    restored = s.current_ir().strokes[0]
    assert restored.pressure is not None and len(restored.pressure) == 3


def test_authored_pressure_is_preserved_verbatim(tmp_path, subject):
    s = _session(tmp_path, subject)
    s.draw([(10, 10), (60, 60), (120, 30)], part="axis", observation_id="observation-0001",
           pressure=[0.11, 0.62, 0.24])
    payload = json.loads(s.checkpoint_path.read_text())
    stored = payload["history"]["actions"][0]["payload"]["stroke"]
    assert stored["pressure"] == [0.11, 0.62, 0.24], "an authored curve is a decision; keep it"


def test_tool_state_is_stored_once_per_action(tmp_path, subject):
    s = _session(tmp_path, subject)
    s.draw([(10, 10), (60, 60)], part="axis", observation_id="observation-0001")
    action = json.loads(s.checkpoint_path.read_text())["history"]["actions"][0]
    assert action["tool_state"], "the action still records its material"
    assert action["payload"]["stroke"].get("tool_state") is None, "and does not repeat it"
    assert s.current_ir().strokes[0].tool_state["pencil_grade"]


def test_legacy_sessions_with_inline_pressure_still_load(tmp_path, subject):
    """A pre-compaction file wrote pressure and tool_state into the stroke payload."""
    from img2drawing import drawing_state_hash
    from img2drawing.core import AgentDrawingSession

    s = _session(tmp_path, subject)
    s.draw([(10, 10), (60, 60), (120, 30)], part="axis", observation_id="observation-0001")
    raw = json.loads(s.checkpoint_path.read_text())
    stroke = raw["history"]["actions"][0]["payload"]["stroke"]
    stroke["pressure"] = [0.4, 0.9, 0.3]
    stroke["tool_state"] = raw["history"]["actions"][0]["tool_state"]

    # a genuine legacy file carries the digest of its own content
    agent = AgentDrawingSession.from_dict({
        "schema": "img2drawing.agent_drawing_session.v1",
        "history": raw["history"],
        "executed_action_ids": raw.get("executed_action_ids", []),
    })
    from img2drawing.core.session import sha256_obj
    raw["digests"]["drawing_state_hash"] = drawing_state_hash(
        DrawingSession._stage_free_projection(agent.current_ir())
    )
    raw["digests"]["action_log_sha256"] = sha256_obj([a.to_dict() for a in agent.history.actions])
    path = tmp_path / "legacy.json"
    path.write_text(json.dumps(raw))

    revived = DrawingSession.resume(path, subject=subject, output_dir=tmp_path / "out2")
    assert revived.current_ir().strokes[0].pressure == [0.4, 0.9, 0.3]


# ------------------------------------------------------- render contract ------------
@pytest.mark.parametrize("value", [195, 120, 70, 35])
def test_a_filled_region_renders_near_the_requested_value(tmp_path, subject, value):
    """The whole point of the tone scale: ask for a value, get that value.

    This is the check that catches a deposition regression - including the one where a
    two-point fill line spent its entire length on the tool's entry and exit taper and
    rendered near-blank.
    """
    import numpy as np
    from PIL import Image
    from img2drawing.render.pillow_pencil_contact import render

    s = _session(tmp_path, subject)
    s.fill_region([(20, 20), (220, 20), (220, 220), (20, 220)], value=value, part="patch",
                  angle=74.0, observation_id="observation-0001", reason="flat tone patch")
    out = tmp_path / f"patch_{value}.png"
    render(s.current_ir(), out, supersample=2)
    measured = np.asarray(Image.open(out).convert("L")).astype(float)[70:170, 70:170].mean()
    assert abs(measured - value) <= 22, f"asked for {value}, rendered {measured:.0f}"


def test_fill_lines_carry_the_tools_constant_pressure(tmp_path, subject):
    s = _session(tmp_path, subject)
    fid = s.fill_region([(20, 20), (220, 20), (220, 220), (20, 220)], value=70, part="patch",
                        angle=90.0, observation_id="observation-0001", reason="flat tone")
    line = next(st for st in s.current_ir().strokes if st.stroke_id.startswith(fid))
    assert line.pressure is None, "a tone line must not taper away to nothing over two points"


def test_darker_request_renders_darker(tmp_path, subject):
    import numpy as np
    from PIL import Image
    from img2drawing.render.pillow_pencil_contact import render

    values = []
    for value in (195, 95):
        s = _session(tmp_path / f"v{value}", subject)
        s.fill_region([(20, 20), (220, 20), (220, 220), (20, 220)], value=value, part="patch",
                      angle=74.0, observation_id="observation-0001", reason="flat tone")
        out = tmp_path / f"ordered_{value}.png"
        render(s.current_ir(), out, supersample=2)
        values.append(np.asarray(Image.open(out).convert("L")).astype(float)[70:170, 70:170].mean())
    assert values[0] > values[1], "the scale must be monotonic on the canvas, not just in the table"
