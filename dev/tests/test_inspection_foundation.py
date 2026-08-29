from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageChops

from img2drawing import Stroke, StrokeIR
from img2drawing.inspection import (
    GroundGuide,
    Grid,
    InspectionSheet,
    PlumbLine,
    ROI,
    Registration,
    angle,
    distance,
    drawing_state_hash,
    grid,
    horizontal_profile,
    map_subject_to_canvas,
    sample_pixel,
    vertical_profile,
)


def _ir(stage: str | None = "P1_gesture") -> StrokeIR:
    return StrokeIR(
        120,
        100,
        strokes=[
            Stroke(
                points=[(12.0, 15.0), (40.0, 45.0)],
                width=3.0,
                role="structure",
                part="torso",
                stage=stage,
                stroke_id="s0001",
            )
        ],
        metadata={"history_cursor": 4, "material": "graphite"},
    )


def _images(tmp_path: Path) -> tuple[Path, Path]:
    subject = Image.new("RGB", (120, 100), (235, 235, 230))
    subject_draw = ImageDraw.Draw(subject)
    subject_draw.rectangle((28, 14, 92, 86), fill=(38, 42, 46))
    subject_draw.ellipse((42, 24, 77, 61), fill=(70, 75, 78))
    subject_path = tmp_path / "subject.png"
    subject.save(subject_path)

    drawing = Image.new("RGB", (120, 100), "white")
    drawing_draw = ImageDraw.Draw(drawing)
    drawing_draw.line((34, 18, 85, 80), fill=(8, 8, 8), width=5)
    drawing_draw.line((80, 18, 40, 75), fill=(65, 65, 65), width=2)
    drawing_path = tmp_path / "current_drawing.png"
    drawing.save(drawing_path)
    return subject_path, drawing_path


def test_drawing_state_hash_ignores_only_workflow_stage_and_cursor():
    assert drawing_state_hash(_ir("P1_gesture")) == drawing_state_hash(_ir("P5_clean_blockin"))
    changed = _ir("P1_gesture")
    changed.strokes[0].points[1] = (41.0, 45.0)
    assert drawing_state_hash(changed) != drawing_state_hash(_ir("P1_gesture"))


def test_registration_and_read_only_measurements_are_explicit():
    registration = Registration((120, 100), (240, 200), scale=(2.0, 2.0), offset=(5.0, 7.0))
    mapped = map_subject_to_canvas(registration, (10.0, 11.0))
    assert mapped.to_dict() == {"kind": "point_mapping", "subject": [10.0, 11.0], "canvas": [25.0, 29.0]}
    assert distance((0, 0), (3, 4)).value == 5.0
    assert distance((0, 0), (3, 4), space="canvas", registration=registration).value == 10.0
    assert round(angle((0, 0), (1, 0), (1, 1)).value, 6) == 90.0
    grid_result = grid(Grid(columns=4, rows=5), (120, 100))
    assert len(grid_result.vertical) == 5
    assert len(grid_result.horizontal) == 6


def test_one_call_sheet_writes_portable_whole_and_roi_evidence(tmp_path: Path):
    subject_path, drawing_path = _images(tmp_path)
    registration = Registration.identity((120, 100))
    subject_before = subject_path.read_bytes()
    ir = _ir()
    measurements = [
        distance((10, 10), (20, 25)),
        angle((10, 10), (20, 10), (20, 20)),
        grid(Grid(columns=6, rows=5), (120, 100)),
        horizontal_profile(subject_path, 40),
        vertical_profile(subject_path, 50),
        sample_pixel(subject_path, (30, 30)),
    ]
    output = tmp_path / "inspection"
    sheet = InspectionSheet.create(
        subject=subject_path,
        drawing=drawing_path,
        drawing_ir=ir,
        registration=registration,
        rois=[ROI("dark-mismatch", (25, 12, 94, 88), scale=4.0)],
        grid=Grid(columns=6, rows=5),
        guides=[PlumbLine((60, 0)), GroundGuide(80)],
        measurements=measurements,
        out_dir=output,
    )

    expected = {
        "inspection_sheet.png",
        "raw_drawing.png",
        "registered_drawing.png",
        "contrast_overlay.png",
        "inspection.json",
        "measurements.json",
    }
    assert {path.name for path in output.iterdir()} == expected
    assert (output / "raw_drawing.png").read_bytes() == drawing_path.read_bytes()
    assert subject_path.read_bytes() == subject_before
    assert sheet.drawing_state_hash == drawing_state_hash(ir)

    manifest_text = (output / "inspection.json").read_text(encoding="utf-8")
    manifest = json.loads(manifest_text)
    assert str(tmp_path) not in manifest_text
    assert "PASS" not in manifest_text and "FAIL" not in manifest_text
    assert manifest["inputs"] == {"subject": "subject.png", "drawing": "current_drawing.png"}
    assert manifest["artifacts"]["sheet"] == "inspection_sheet.png"
    assert manifest["rois"][0]["space"] == "subject"

    with Image.open(output / "registered_drawing.png") as registered:
        assert registered.size == (120, 100)
    with Image.open(output / "raw_drawing.png") as raw, Image.open(output / "contrast_overlay.png") as overlay:
        assert ImageChops.difference(raw.convert("RGB"), overlay.convert("RGB")).getbbox() is not None

    measurement_text = (output / "measurements.json").read_text(encoding="utf-8")
    assert str(tmp_path) not in measurement_text
    assert "PASS" not in measurement_text and "FAIL" not in measurement_text
    assert "current_drawing.png" not in measurement_text
