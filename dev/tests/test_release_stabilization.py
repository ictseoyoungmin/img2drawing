"""Regression probes for the final authoring, GIF and profile boundaries."""
from dataclasses import asdict, replace
from pathlib import Path
import shutil

import pytest
from PIL import Image

from img2drawing import DrawingSession, RenderProfile
from img2drawing.core.action import AgentDrawingSession, DrawingAction
from img2drawing.timelapse.gif import gif_rgb, _set_full_frame_disposal


def make(tmp_path, profile=None):
    reference = tmp_path / 'reference.png'
    Image.new('RGB', (64, 64), 'white').save(reference)
    session = DrawingSession.create(subject=reference, output_dir=tmp_path / 'run',
        render_profile=profile or replace(RenderProfile.canonical(64, 64), supersample=2))
    oid = session.observe({'form': 'explicit crossing test'})
    return session, oid, reference


def snap(s):
    return (s.history_cursor, s.drawing_state_hash(), s.checkpoint_path.read_bytes(), s._agent.to_dict())


@pytest.mark.parametrize('points,kwargs', [
    ([(5, 5)], {}),
    ([(5, 5), (5, 5)], {}),
    ([(5, 5, 1), (20, 20, 2)], {}),
    ([(float('nan'), 5), (20, 20)], {}),
    ([(5, 5), (20, 20), (30, 30)], {'pressure': [0.3, 0.6]}),
    ([(5, 5), (20, 20)], {'pressure': [float('nan'), 0.5]}),
    ([(5, 5), (20, 20)], {'pressure': [-0.2, 1.2]}),
    ([(5, 5), (20, 20)], {'confidence': 2.0}),
    ([(5, 5), (20, 20)], {'role': ''}),
    ([(5, 5), (20, 20)], {'role': None}),
    ([(5, 5), (20, 20)], {'tool_overrides': {'width': float('inf')}}),
])
def test_bad_draw_fails_before_commit(tmp_path, points, kwargs):
    s, oid, _ = make(tmp_path)
    old = snap(s)
    with pytest.raises(ValueError):
        s.draw(points, observation_id=oid, **kwargs)
    assert snap(s) == old


def test_replacement_and_batch_fail_atomically(tmp_path):
    s, oid, ref = make(tmp_path)
    sid = s.draw([(5, 5), (20, 20), (30, 30)], observation_id=oid)
    old = snap(s)
    with pytest.raises(ValueError, match='correction reason'):
        s.replace_stroke(sid, [(6, 5), (20, 20)], reason=' ', observation_id=oid)
    assert snap(s) == old
    with pytest.raises(ValueError, match='pressure'):
        s.replace_segment(sid, 0, 1, [(5, 5), (20, 20)], pressure=[1.1, 0.5],
            reason='repair contour', observation_id=oid)
    assert snap(s) == old
    with pytest.raises(ValueError, match='distinct points'):
        s.draw_many([[(7, 7), (30, 40)], [(8, 8), (8, 8)]], observation_id=oid)
    assert snap(s) == old
    r = DrawingSession.resume(s.checkpoint(), subject=ref)
    assert r.history_cursor == old[0] and r.drawing_state_hash() == old[1]


@pytest.mark.parametrize('dict_input', [False, True])
def test_core_input_routes_share_validation(dict_input):
    s = AgentDrawingSession(64, 64)
    a = DrawingAction('bad', 'draw_stroke', 'test', role='contour', points=((4,4),(5,5)),
        pressure=(0.4, float('inf')), tool={'preset':'form_pencil','grade':'HB'},
        observation_id='o', source_observation='observed')
    before = s.to_dict()
    with pytest.raises(ValueError, match='pressure'):
        s.execute(asdict(a) if dict_input else a)
    assert s.to_dict() == before


def test_existing_profile_disposal_is_not_migrated(tmp_path):
    p = RenderProfile.canonical(64, 64)
    assert p.gif_disposal == 1
    old = replace(p, gif_disposal=2)
    s, _, ref = make(tmp_path, old)
    r = DrawingSession.resume(s.checkpoint(), subject=ref)
    assert r.render_profile == old and r.render_profile.digest() == old.digest()
    assert p.renderer_contract_digest == old.renderer_contract_digest


@pytest.mark.parametrize('backend', ['canonical', 'fast'])
@pytest.mark.parametrize('disposal', [1, 2, 3])
def test_bound_gif_policy_and_every_frame(tmp_path, backend, disposal):
    if backend == 'fast' and shutil.which('ffmpeg') is None:
        pytest.skip('ffmpeg unavailable')
    p = replace(RenderProfile.canonical(64, 64), supersample=2,
                gif_loop=3, gif_disposal=disposal, gif_palette_colors=64)
    s, oid, _ = make(tmp_path, p)
    a = s.draw([(4, 12), (56, 52)], tool='continuous_pencil', observation_id=oid)
    s.draw([(4, 52), (56, 12)], tool='continuous_pencil', observation_id=oid)
    s.delete_stroke(a, reason='remove crossing line', observation_id=oid)
    old = snap(s)
    r = s.export_timelapse(tmp_path / backend, backend=backend, every_n=1)
    assert snap(s) == old
    assert r.manifest['gif']['loop'] == 3
    assert r.manifest['gif']['disposal'] == disposal
    assert r.manifest['gif']['palette_colors_max'] == 64
    with Image.open(r.gif_path) as gif:
        assert gif.info['loop'] == 3 and gif.n_frames == s.history_cursor + 1
        for i in range(gif.n_frames):
            gif.seek(i)
            assert gif.disposal_method == disposal
            with gif.convert('RGB') as actual:
                assert len(actual.getcolors(256)) <= 64
                frame = s.render_at(i, tmp_path / f'cursor-{i}.png')
                with Image.open(frame.path) as png, gif_rgb(png) as expected:
                    from PIL import ImageChops
                    with ImageChops.difference(actual, expected) as diff:
                        assert max(v[1] for v in diff.getextrema()) <= 32
    if backend == 'fast':
        assert r.manifest['fast']['encode']['rectangle'] == (disposal == 1)


@pytest.mark.parametrize('alpha', [0, 120])
def test_alpha_gif_display_preserves_png_and_fails_closed_fast(tmp_path, alpha):
    p = replace(RenderProfile.canonical(64, 64), supersample=2, background_rgba=(80, 60, 40, alpha))
    s, oid, _ = make(tmp_path, p)
    s.draw([(10, 10), (50, 50)], observation_id=oid)
    old = snap(s)
    r = s.export_timelapse(tmp_path / 'auto', every_n=1)
    assert r.manifest['backend']['selected'] == 'canonical'
    assert 'transparent background' in r.manifest['backend']['fallback_reason']
    assert r.manifest['gif']['display_compositing'] == 'source-over-white'
    with Image.open(r.final_path) as png, Image.open(r.gif_path) as gif:
        assert png.mode == 'RGBA' and png.getpixel((0,0))[3] == alpha
        gif.seek(gif.n_frames - 1)
        with gif_rgb(png) as expected, gif_rgb(gif) as actual:
            assert actual.getpixel((0,0)) == expected.getpixel((0,0))
    with pytest.raises(ValueError, match='transparent background'):
        s.export_timelapse(tmp_path / 'strict', backend='fast', every_n=1)
    assert not (tmp_path / 'strict').exists() and snap(s) == old
