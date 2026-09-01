"""Material palette: name what a boundary separates before trusting where it is."""

from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from img2drawing import SubjectPalette

GARMENT = (22, 25, 32)      # near-black jacket
SKIN = (167, 143, 137)      # warm
BACKGROUND = (160, 145, 140)  # nearly the same lightness as skin, less warm
HAIR = (238, 238, 240)


@pytest.fixture
def subject(tmp_path: Path) -> Path:
    """A subject built to contain the trap: skin and background share lightness."""
    a = np.zeros((200, 200, 3), dtype=np.uint8)
    a[:, :] = BACKGROUND
    a[40:180, 60:140] = GARMENT          # body
    a[150:170, 100:130] = SKIN           # a bare hand emerging from the garment
    a[10:40, 70:130] = HAIR
    p = tmp_path / "subject.png"
    Image.fromarray(a).save(p)
    return p


def _palette(subject: Path) -> SubjectPalette:
    p = SubjectPalette(subject)
    p.sample("background", (5, 5, 40, 40))
    p.sample("garment", (65, 60, 95, 100))
    p.sample("skin", (105, 155, 125, 168))
    p.sample("hair", (75, 15, 125, 35))
    return p


def test_palette_names_skin_that_a_darkness_threshold_calls_background(subject):
    p = _palette(subject)
    name, _ = p.classify(115, 160)
    assert name == "skin", "the hand must not read as background"
    # and confirm the trap is real: on lightness alone skin and background are together
    lit = np.asarray(Image.open(subject).convert("L")).astype(int)
    assert abs(int(lit[160, 115]) - int(lit[10, 10])) < 20


def test_row_segmentation_finds_the_hand_inside_the_garment(subject):
    p = _palette(subject)
    runs = p.classify_row(160, (0, 200))
    names = [r[0] for r in runs]
    assert "skin" in names, f"scanline lost the hand: {runs}"
    skin = [r for r in runs if r[0] == "skin"][0]
    assert 95 <= skin[1] <= 105 and 125 <= skin[2] <= 135


def test_ambiguous_pairs_warns_about_the_pair_that_causes_the_error(subject):
    p = _palette(subject)
    pairs = {frozenset((a, b)) for a, b, _ in p.ambiguous_pairs(threshold=60.0)}
    assert frozenset(("skin", "background")) in pairs, \
        "the palette must say which materials this subject cannot separate"
    assert frozenset(("garment", "skin")) not in pairs


def test_boundary_kind_names_both_sides(subject):
    p = _palette(subject)
    edge = p.boundary_kind((80, 160), (115, 160))
    assert edge["separates"] == ("garment", "skin")
    assert edge["visible_to_luminance_threshold"] is True


def test_boundary_kind_flags_an_edge_a_darkness_scan_would_miss(subject):
    """skin -> background is the edge that a luminance profile cannot see."""
    p = _palette(subject)
    edge = p.boundary_kind((115, 160), (190, 160))
    assert edge["separates"] == ("skin", "background")
    assert edge["visible_to_luminance_threshold"] is False
    assert edge["dominant_axis"] in {"warmth", "chroma"}


def test_same_material_on_both_sides_reports_no_boundary(subject):
    p = _palette(subject)
    assert p.boundary_kind((70, 100), (90, 100))["separates"] is None


def test_palette_requires_two_materials_before_it_will_separate_anything(subject):
    p = SubjectPalette(subject)
    p.sample("garment", (65, 60, 95, 100))
    with pytest.raises(ValueError):
        p.classify(115, 160)


def test_sample_box_must_be_inside_the_subject(subject):
    p = SubjectPalette(subject)
    with pytest.raises(ValueError):
        p.sample("nope", (150, 150, 400, 400))


def test_palette_is_portable(subject):
    p = _palette(subject)
    d = p.to_dict()
    assert d["format"] == "subject-palette/v1"
    assert {s["name"] for s in d["samples"]} == {"background", "garment", "skin", "hair"}
    assert d["ambiguous_pairs"]
