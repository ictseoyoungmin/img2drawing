from __future__ import annotations
import hashlib
from pathlib import Path
import importlib.util
import img2drawing
from img2drawing.provenance import export_timelapse, export_fast_timelapse
from img2drawing.provenance.fast_timelapse import FastTimelapseExport

BASELINE = {
    'provenance/timelapse.py': '893d3eadadebe980b6132167f1d9a676528d46677e97ed8698a04f94f9b50b61',
    'render/pillow_pencil_contact.py': 'c4b56582a25bbefbd38de7ea896b0dfd62d044bd168a64c346f9bdc2b2d9edd0',
    'provenance/replay.py': '1f8081bf7f536fa9c524b3b300b06f6ef8cbf358c09367766497d5580a2404bd',
    '__init__.py': '73e749fe00c7954b64d614eb3ae8b45b47338580a20fbe758baf4dc48dced2b2',
}

def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def test_v102_version_and_public_identity():
    assert img2drawing.__version__ == '1.0.2'
    from img2drawing._version import PUBLIC_API, DEFAULT_SESSION_ID, RELEASE_REVISION, RELEASE_SLICE
    assert PUBLIC_API == 'DrawingSession/1.0.2-vnext'
    assert DEFAULT_SESSION_ID == 'img2drawing-102-vnext'
    assert RELEASE_REVISION == 'A10'
    assert RELEASE_SLICE == 'v1.0.2_local_first_exact_timelapse'

def test_root_surface_stays_narrow_and_fast_path_is_specialized():
    assert callable(export_timelapse)
    assert callable(export_fast_timelapse)
    assert FastTimelapseExport.__module__.startswith('img2drawing.provenance.fast_timelapse')
    assert 'export_fast_timelapse' not in dir(img2drawing)
    assert 'export_fast_timelapse' not in img2drawing.__all__
    import img2drawing.provenance as provenance
    assert not hasattr(provenance, 'export_timelapse_streaming')
    assert importlib.util.find_spec('img2drawing.provenance.streaming') is None

def test_canonical_renderer_and_legacy_exporter_are_byte_preserved():
    pkg = Path(img2drawing.__file__).resolve().parent
    for rel, digest in BASELINE.items():
        assert sha(pkg / rel) == digest, rel

def test_required_runtime_json_is_present():
    pkg = Path(img2drawing.__file__).resolve().parent
    for name in ('pencil_presets.json','pencil_contact_profile.json','registration_profile.json','tone_scale.json'):
        assert (pkg/'data'/name).is_file(), name
