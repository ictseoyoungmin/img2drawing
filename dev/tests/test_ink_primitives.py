"""S01a primitive tests; no claim of mixed-session/replay support yet."""
from dataclasses import replace
import json
import math

import numpy as np
import pytest

from img2drawing.core.material import InkArea, InkPath, decode_ink_mark
from img2drawing.render import ink
from img2drawing.render.ink import build_ink_patch


def rect(x0, y0, x1, y1):
    return ((x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0))


def canvas(mark, size=(80, 60), factor=1):
    bounds, patch = build_ink_patch(mark, factor=factor, hi_size=size)
    with patch:
        out = np.zeros((size[1], size[0], 4), dtype=np.uint8)
        x0, y0, x1, y1 = bounds
        if x0 < x1 and y0 < y1:
            out[y0:y1, x0:x1] = np.asarray(patch)
    return out


def test_ink_mark_strict_portable_roundtrip():
    for mark in (InkPath(((5, 15), (25, 30)), (0.25, 0.9), 0.5, 8, 1.3),
                 InkArea(rect(4, 4, 50, 40), (rect(12, 12, 21, 21),), "white")):
        raw = json.loads(json.dumps(mark.to_dict()))
        other = decode_ink_mark(raw)
        assert other == mark
        assert other.digest() == mark.digest()
        with pytest.raises(ValueError, match="fields"):
            decode_ink_mark({**raw, "raster_mask": "not allowed"})
        with pytest.raises(ValueError, match="schema"):
            decode_ink_mark({**raw, "schema": "future"})
        assert mark.digest() != replace(mark, paint="white" if mark.paint == "black" else "black").digest()


@pytest.mark.parametrize("points,pressure", [
    (((1, 1), (1, 1)), (0, 1)),
    (((1, 1), (2, 2)), (1,)),
    (((1, 1), (2, 2)), (True, 1)),
    (((1, 1), (2, 2)), (float("nan"), 1)),
    (((1, 1), (float("inf"), 2)), (0, 1)),
    (((1, 1), (999999, 2)), (0, 1)),
])
def test_invalid_path(points, pressure):
    with pytest.raises(ValueError):
        InkPath(points, pressure, 0, 8)


@pytest.mark.parametrize("kw", [{"min_width": -1}, {"max_width": 0},
                                  {"gamma": 0}, {"gamma": float("inf")}, {"paint": "gray"}])
def test_invalid_material(kw):
    args = {"points": ((5, 10), (20, 10)), "pressure": (0, 1), "min_width": 0,
            "max_width": 8, "gamma": 1, "paint": "black"}
    with pytest.raises(ValueError):
        InkPath(**{**args, **kw})


def test_gpen_width_varies_without_density_change():
    mark = InkPath(((10, 30), (30, 30), (50, 30), (70, 30)), (0, .25, .75, 1), 2, 10)
    assert mark.diameters() == (2, 4, 8, 10)
    a = canvas(mark)
    counts = [(a[:, x, 3] == 255).sum() for x in (15, 30, 50, 65)]
    assert counts == sorted(counts) and counts[-1] > counts[0]
    assert set(np.unique(a[:, :, 3])) == {0, 255}
    assert np.all(a[a[:, :, 3] == 255, :3] == 0)


def test_fineliner_and_collinear_resampling_exact():
    a = InkPath(((5, 30), (75, 30)), (0, 1), 6, 6)
    b = InkPath(((5, 30), (40, 30), (75, 30)), (1, 0, .3), 6, 6)
    assert np.array_equal(canvas(a), canvas(b))
    c = canvas(a)
    assert (c[:, 20, 3] == 255).sum() == 6
    assert (c[:, 60, 3] == 255).sum() == 6


def test_variable_sweep_split_exact_and_self_overlap_union():
    a = InkPath(((8, 10), (72, 42)), (0, 1), 2, 10)
    b = InkPath(((8, 10), (40, 26), (72, 42)), (0, .5, 1), 2, 10)
    assert np.array_equal(canvas(a), canvas(b))
    cross = InkPath(((8, 8), (60, 50), (8, 50), (60, 8)), (1, 1, 1, 1), 4, 4)
    c = canvas(cross)
    assert c[29, 34, 3] == 255
    assert set(np.unique(c[:, :, 3])) == {0, 255}


def test_fast_radius_change_containment_and_zero_coverage():
    # Endpoint disk contains the smaller endpoint and the entire variable sweep.
    m = InkPath(((30, 30), (31, 30)), (0, 1), 0, 10)
    a = canvas(m)
    y, x = np.ogrid[:60, :80]
    expected = ((x + .5 - 31) ** 2 + (y + .5 - 30) ** 2) <= 25
    assert np.array_equal(a[:, :, 3] == 255, expected)
    z = InkPath(((5, 5), (40, 20)), (0, 0), 0, 4)
    assert not canvas(z).any()


def test_area_concavity_hole_winding_and_white_paint():
    outer = ((4, 4), (70, 4), (70, 50), (42, 50), (42, 25), (4, 25), (4, 4))
    hole = rect(10, 10, 18, 20)
    mark = InkArea(outer, (hole,))
    a = canvas(mark)
    b = canvas(InkArea(tuple(reversed(outer)), (tuple(reversed(hole)),)))
    assert np.array_equal(a, b)
    assert a[12, 14, 3] == 0
    assert a[40, 20, 3] == 0
    assert a[40, 55, 3] == 255
    white = canvas(replace(mark, paint="white"))
    assert np.array_equal(a[:, :, 3], white[:, :, 3])
    assert np.all(white[white[:, :, 3] == 255, :3] == 255)


@pytest.mark.parametrize("outer,holes", [
    (rect(4, 4, 50, 50)[:-1], ()),
    (((4, 4), (40, 40), (4, 40), (40, 4), (4, 4)), ()),
    (((4, 4), (10, 4), (7, 4), (30, 30), (4, 4)), ()),
    (rect(4, 4, 50, 50), (rect(4, 10, 15, 20),)),
    (rect(4, 4, 50, 50), (rect(60, 10, 70, 20),)),
    (rect(4, 4, 50, 50), (rect(8, 8, 30, 30), rect(20, 20, 40, 40))),
    (rect(4, 4, 50, 50), (rect(8, 8, 30, 30), rect(10, 10, 20, 20))),
])
def test_invalid_area(outer, holes):
    with pytest.raises(ValueError):
        InkArea(outer, holes)


def test_clipping_and_supersample_local_bbox():
    mark = InkArea(rect(-3, -4, 5, 6))
    bounds, patch = build_ink_patch(mark, factor=4, hi_size=(1000, 1000))
    with patch:
        assert bounds == (0, 0, 20, 24)
        assert patch.size == (20, 24)
        assert patch.getchannel("A").getextrema() == (255, 255)
    b, p = build_ink_patch(InkArea(rect(2000, 2000, 2005, 2005)), factor=1, hi_size=(100, 100))
    with p:
        assert b == (0, 0, 0, 0) and p.getchannel("A").getextrema() == (0, 0)


def test_preflight_budget_rejects_before_mask_allocation(monkeypatch):
    monkeypatch.setattr(ink, "MAX_PATCH_PIXELS", 64)
    def forbidden(*a, **kw):
        pytest.fail("mask allocated before preflight")
    monkeypatch.setattr(ink, "_path_mask", forbidden)
    monkeypatch.setattr(ink, "_area_mask", forbidden)
    for mark in (InkPath(((5, 5), (40, 40)), (1, 1), 8, 8), InkArea(rect(1, 1, 40, 40))):
        with pytest.raises(ValueError, match="budget"):
            build_ink_patch(mark, factor=4, hi_size=(1000, 1000))
    with pytest.raises(ValueError, match="factor"):
        build_ink_patch(InkArea(rect(1, 1, 4, 4)), factor=1e50, hi_size=(100, 100))


def test_session_legacy_authority_does_not_advertise_unintegrated_ink():
    from img2drawing import RenderProfile
    from img2drawing.runtime import runtime_capabilities
    assert RenderProfile.canonical(16, 16).renderer_version == "11"
    assert not any("ink" in op for op in runtime_capabilities().authoring_operations)


def test_edge_sweep_retains_exact_narrow_phase_hits():
    import random
    from img2drawing.core.material import _edge_candidates,_intersects
    rng=random.Random(6401)
    for _ in range(180):
        n=rng.randint(4,32)
        ring=[(rng.uniform(-100,100),rng.uniform(-100,100)) for _ in range(n)]
        ring.append(ring[0])
        es=tuple(zip(ring,ring[1:]))
        brute={(i,j) for i,e in enumerate(es) for j in range(i+2,n)
               if not (i==0 and j==n-1) and _intersects(*e,*es[j])}
        candidates=list(_edge_candidates(es))
        pairs=[(i,j) for i,j,_,_ in candidates]
        assert len(pairs)==len(set(pairs))
        actual={(i,j) for i,j,a,b in candidates if _intersects(*a,*b)}
        assert actual==brute
        # Two different rings, including overlaps and disjoint edges.
        other=tuple(((x+2.5,y-3.5),(u+2.5,v-3.5)) for (x,y),(u,v) in es)
        cross={(i,j) for i,e in enumerate(es) for j,q in enumerate(other) if _intersects(*e,*q)}
        assert {(i,j) for i,j,a,b in _edge_candidates(es,other) if _intersects(*a,*b)}==cross


def test_edge_sweep_sparse_ring_and_epsilon_touches():
    import math
    from img2drawing.core.material import _edge_candidates,_intersects
    n=663
    ring=tuple((100*math.cos(2*math.pi*i/n),100*math.sin(2*math.pi*i/n)) for i in range(n))
    ring=ring+(ring[0],)
    es=tuple(zip(ring,ring[1:]))
    pairs=list(_edge_candidates(es))
    assert len(pairs)<n*4
    assert not any(_intersects(*a,*b) for _,_,a,b in pairs)
    mark=InkArea(ring)
    assert mark.outer==ring
    # Epsilon-inclusive cross-ring contact and exact boundary touch.
    a=(((0.,0.),(1.,0.)),)
    for delta in (0.,5e-10,2e-9):
        b=(((1.+delta,0.),(2.,0.)),)
        assert any(_intersects(*p,*q) for _,_,p,q in _edge_candidates(a,b))==_intersects(*a[0],*b[0])


def test_self_intersection_error_names_authored_edges():
    with pytest.raises(ValueError,match=r"self-intersects or touches at edges 0 and 2"):
        InkArea(((0,0),(20,20),(0,20),(20,0),(0,0)))
