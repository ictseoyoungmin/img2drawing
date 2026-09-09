from __future__ import annotations
import shutil
from pathlib import Path
import pytest
from PIL import Image
from img2drawing import DrawingIntent, DrawingSession, RenderProfile
from img2drawing.vnext.output import export_session_timelapse


def _session(tmp_path: Path, *, paper_tooth: float = 0.5) -> DrawingSession:
    subject = tmp_path / 'subject.png'
    Image.new('RGB', (64, 48), (244, 242, 236)).save(subject)
    profile = RenderProfile.from_dict({
        **RenderProfile.canonical(64, 48).to_dict(),
        'supersample': 2,
        'paper_tooth': paper_tooth,
    })
    s = DrawingSession.create(
        subject=subject,
        output_dir=tmp_path / 'session',
        intent=DrawingIntent(finish_intent='form_light'),
        render_profile=profile,
    )
    s.draw(((6, 8), (18, 22), (25, 40)), part='gesture')
    s.draw(((26, 8), (34, 20), (39, 39)), part='contour')
    return s


@pytest.mark.skipif(shutil.which('ffmpeg') is None, reason='ffmpeg unavailable')
def test_default_backend_is_fast_and_does_not_spool_png_frames(tmp_path: Path):
    s = _session(tmp_path)
    out = tmp_path / 'replay'
    r = s.export_timelapse(out, mode='every_n', every_n=1, max_pixel_work=10**9)
    assert r.manifest['backend']['selected'] == 'fast'
    assert r.manifest['backend']['materialize_frames'] is False
    assert r.manifest['final']['last_frame_pixel_match'] is True
    assert not list(r.frame_dir.glob('*.png'))
    assert r.gif_path.is_file() and r.final_path.is_file()


def test_explicit_canonical_backend_preserves_legacy_export_contract(tmp_path: Path):
    s = _session(tmp_path)
    r = export_session_timelapse(s, tmp_path / 'canonical', mode='action', max_pixel_work=10**9, backend='canonical')
    assert r.manifest['backend']['selected'] == 'canonical'
    assert list(r.frame_dir.glob('*.png'))
    assert r.manifest['final']['last_frame_pixel_match'] is True


def test_unsupported_fill_fails_closed_to_whole_canonical_export(tmp_path: Path):
    s = _session(tmp_path)
    s.fill_region(((10, 15), (40, 15), (42, 35), (12, 36)), value=150, part='shadow', fill_id='f1')
    r = s.export_timelapse(tmp_path / 'fallback', mode='action', max_pixel_work=10**9)
    assert r.manifest['backend']['selected'] == 'canonical-fallback'
    assert 'unsupported actions' in r.manifest['backend']['fallback_reason']
    assert list(r.frame_dir.glob('*.png'))
    assert r.manifest['final']['last_frame_pixel_match'] is True


@pytest.mark.skipif(shutil.which('ffmpeg') is None, reason='ffmpeg unavailable')
def test_render_profile_paper_state_is_authority_for_fast_final(tmp_path: Path):
    s = _session(tmp_path, paper_tooth=0.63)
    r = s.export_timelapse(tmp_path / 'paper', mode='action', max_pixel_work=10**9)
    assert r.manifest['backend']['selected'] == 'fast'
    assert r.manifest['render_profile']['paper_tooth'] == 0.63
    assert r.manifest['final']['last_frame_pixel_match'] is True


@pytest.mark.skipif(shutil.which('ffmpeg') is None, reason='ffmpeg unavailable')
def test_materialize_frames_is_explicit_opt_in(tmp_path: Path):
    s = _session(tmp_path)
    r = export_session_timelapse(s, tmp_path / 'materialized', mode='action', max_pixel_work=10**9, materialize_frames=True)
    files = list(r.frame_dir.glob('*.png'))
    assert len(files) == len(r.manifest['frames'])
    assert all(frame['file'] is not None for frame in r.manifest['frames'])


def test_pixel_work_gate_applies_before_fast_export(tmp_path: Path):
    s = _session(tmp_path)
    out = tmp_path / 'too-large'
    with pytest.raises(ValueError, match='pixel-work budget'):
        s.export_timelapse(out, mode='action', max_pixel_work=1)
    assert not (out / 'timelapse.gif').exists()
