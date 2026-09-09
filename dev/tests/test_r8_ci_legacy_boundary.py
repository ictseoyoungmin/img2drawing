from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_active_dev_tests_do_not_import_retired_streaming_backend() -> None:
    offenders = []
    for path in sorted((ROOT / "dev" / "tests").glob("test_*.py")):
        if path.name == "test_r8_ci_legacy_boundary.py":
            continue
        text = path.read_text(encoding="utf-8")
        if "img2drawing.provenance.streaming" in text or "from img2drawing.provenance import export_timelapse_streaming" in text:
            offenders.append(path.relative_to(ROOT).as_posix())
    assert offenders == []
