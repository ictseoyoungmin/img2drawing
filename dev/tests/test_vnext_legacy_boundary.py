from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest
from PIL import Image

from img2drawing.core.session import sha256_obj
from img2drawing.legacy.r23 import (
    LEGACY_CHECKPOINT_SCHEMAS,
    LegacyCheckpointError,
    inspect_checkpoint,
    migrate_checkpoint,
)


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "skills" / "img2drawing" / "src"


def _python(source: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-c", source],
        check=True,
        capture_output=True,
        text=True,
        env={"PYTHONPATH": str(SRC)},
    )


def _legacy_run(tmp_path: Path):
    from img2drawing.legacy.r23 import DrawingRun, ObservationContract, ViewObservation

    subject = tmp_path / "subject.png"
    Image.new("RGB", (64, 80), (236, 234, 229)).save(subject)
    run = DrawingRun.create(
        subject,
        tmp_path / "legacy-run",
        session_id="r23-migration-test",
        working_supersample=2,
    )
    run.lock_observation(
        ObservationContract(
            subject_summary="A synthetic subject for compatibility-boundary testing.",
            view=ViewObservation(
                body_view="front",
                torso_turn="none",
                near_side="unknown",
                arm_visibility={"subject_left": "visible", "subject_right": "visible"},
                arm_occlusion={"subject_left": (), "subject_right": ()},
            ),
        )
    )
    run.stage_start("P1_gesture")
    run.draw(
        {
            "action_id": "legacy-line-1",
            "kind": "draw_stroke",
            "stage": "P1_gesture",
            "role": "gesture",
            "part": "line_of_action",
            "points": [[12, 8], [28, 38], [42, 70]],
            "stroke_id": "legacy-stroke-1",
            "confidence": 0.9,
            "layer": 10,
            "tool": {
                "preset": "construction_pencil",
                "grade": "HB",
                "overrides": {"pressure": 0.3, "width": 1.2, "opacity": 0.4},
            },
            "observation_id": "legacy-observation-1",
            "source_observation": "Synthetic compatibility observation.",
        }
    )
    return subject, run


def test_canonical_and_wildcard_imports_do_not_load_or_advertise_r23():
    result = _python(
        """
import sys
import img2drawing
assert 'DrawingRun' not in img2drawing.__all__
assert 'StageSpec' not in img2drawing.__all__
assert 'img2drawing.legacy.r23' not in sys.modules
assert 'img2drawing.run' not in sys.modules
assert 'img2drawing.stages' not in sys.modules
assert 'img2drawing.review' not in sys.modules
namespace = {}
exec('from img2drawing import *', namespace)
assert 'DrawingRun' not in namespace
assert 'img2drawing.legacy.r23' not in sys.modules
assert 'img2drawing.run' not in sys.modules
assert 'img2drawing.stages' not in sys.modules
assert 'img2drawing.review' not in sys.modules
"""
    )
    assert result.stdout == ""


def test_explicit_namespace_is_lazy_until_a_historical_name_is_requested():
    result = _python(
        """
import sys
import img2drawing.legacy.r23 as r23
assert 'img2drawing.run' not in sys.modules
assert 'img2drawing.stages' not in sys.modules
assert 'img2drawing.review' not in sys.modules
assert r23.DrawingRun.__name__ == 'DrawingRun'
assert 'img2drawing.run' in sys.modules
assert 'img2drawing.stages' in sys.modules
assert 'img2drawing.review' in sys.modules
"""
    )
    assert result.stdout == ""


def test_root_legacy_name_is_a_nonadvertised_deprecated_identity_shim():
    result = _python(
        """
import warnings
import img2drawing
from img2drawing.legacy.r23 import DrawingRun as explicit
with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter('always')
    shim = img2drawing.DrawingRun
assert shim is explicit
assert len(caught) == 1
assert issubclass(caught[0].category, DeprecationWarning)
assert 'img2drawing.legacy.r23' in str(caught[0].message)
assert 'DrawingRun' not in img2drawing.__all__
"""
    )
    assert result.stdout == ""


@pytest.mark.parametrize("schema", LEGACY_CHECKPOINT_SCHEMAS)
def test_supported_r23_checkpoint_migrates_shared_truth_and_provenance(
    tmp_path: Path, schema: str
):
    subject, run = _legacy_run(tmp_path)
    checkpoint = run.output_dir / "session" / "checkpoint.json"
    source_payload = json.loads(checkpoint.read_text(encoding="utf-8"))
    source_payload["schema"] = schema
    if schema == "img2drawing.run_checkpoint.v1":
        source_payload.pop("observation_lock", None)
        source_payload.pop("observation_reopens", None)
    checkpoint.write_text(
        json.dumps(source_payload, indent=2, ensure_ascii=False, sort_keys=True),
        encoding="utf-8",
    )
    source_actions = source_payload["agent_session"]["history"]["actions"]
    source_action_digest = sha256_obj(source_actions)

    info = inspect_checkpoint(checkpoint)
    assert info.schema == schema
    assert info.schema in LEGACY_CHECKPOINT_SCHEMAS
    assert info.can_resume and info.can_migrate
    assert info.session_id == "r23-migration-test"
    assert info.subject_name == subject.name

    migrated = migrate_checkpoint(checkpoint, output_dir=tmp_path / "vnext")
    target_payload = json.loads(migrated.checkpoint_path.read_text(encoding="utf-8"))
    migration = target_payload["metadata"]["migration"]
    assert migrated.session_id == run.session_id
    assert target_payload["subject"] == {
        "name": subject.name,
        "sha256": hashlib.sha256(subject.read_bytes()).hexdigest(),
    }
    assert target_payload["history"]["actions"] == source_actions
    assert target_payload["digests"]["action_log_sha256"] == source_action_digest
    assert migration["source"]["action_log_sha256"] == source_action_digest
    assert migration["source"]["drawing_state_sha256"] == source_payload["state_sha256"]
    assert migration["source"]["renderer"] == {
        "identity": None,
        "status": "not-persisted-by-r23-checkpoint",
    }
    assert migration["target"]["renderer"]["id"] == target_payload["renderer"]["id"]
    assert migration["target"]["drawing_state_sha256"] == migrated.drawing_state_hash()
    assert [stroke.stage for stroke in migrated.current_ir().strokes] == [None]
    assert target_payload["history"]["actions"][-1]["stage"] == "P1_gesture"
    assert target_payload["observations"][0]["observation_id"] == "legacy-observation-1"
    assert "progress" not in target_payload
    assert "reviews" not in target_payload

    from img2drawing import DrawingSession

    resumed = DrawingSession.resume(migrated.checkpoint_path, subject=subject)
    assert resumed.history_cursor == migrated.history_cursor
    assert resumed.drawing_state_hash() == migrated.drawing_state_hash()


def test_migration_refuses_unknown_or_vnext_schema_with_actionable_guidance(tmp_path: Path):
    unknown = tmp_path / "unknown.json"
    unknown.write_text(json.dumps({"schema": "img2drawing.run_checkpoint.v99"}), encoding="utf-8")
    info = inspect_checkpoint(unknown)
    assert not info.can_resume and not info.can_migrate
    assert "supported schemas" in info.guidance
    with pytest.raises(LegacyCheckpointError, match="Export with a supported R23 runtime"):
        migrate_checkpoint(unknown, output_dir=tmp_path / "out")

    vnext = tmp_path / "vnext.json"
    vnext.write_text(json.dumps({"schema": "img2drawing.vnext.session.v2"}), encoding="utf-8")
    info = inspect_checkpoint(vnext)
    assert not info.can_resume
    assert "DrawingSession.resume" in info.guidance


def test_single_legacy_export_authority_and_no_parallel_core_tree():
    package = ROOT / "skills" / "img2drawing" / "src" / "img2drawing"
    root_source = (package / "__init__.py").read_text(encoding="utf-8")
    legacy_source = (package / "legacy" / "r23.py").read_text(encoding="utf-8")
    assert "_LAZY_EXPORTS" not in root_source
    assert legacy_source.count("LEGACY_EXPORTS") >= 2
    assert not any(path.name in {"core_v2", "vnext_core"} for path in package.iterdir())
    from img2drawing.legacy.r23 import LEGACY_EXPORTS

    assert LEGACY_EXPORTS
    for module, _ in LEGACY_EXPORTS.values():
        relative = Path(module.removeprefix("img2drawing.").replace(".", "/"))
        assert (package / relative).is_dir() or (package / relative.with_suffix(".py")).is_file()


def test_package_api_identity_is_canonical_while_r23_identity_stays_historical():
    from img2drawing._version import LEGACY_R23_PUBLIC_API, PUBLIC_API

    assert PUBLIC_API.startswith("DrawingSession/")
    assert LEGACY_R23_PUBLIC_API.startswith("DrawingRun/")
