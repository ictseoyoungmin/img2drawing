from __future__ import annotations

import json
import time
import warnings
from pathlib import Path

import pytest
from jsonschema import validators

from img2drawing.legacy.r23 import (
    EnvelopeStation,
    RegionEnvelopeIntegrityError,
    RegionEnvelopeObservation,
    compare_region_envelopes,
)


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas" / "region_envelope.schema.json"
LOCK_DIGEST = "d" * 64
DRAWING_STATE = "e" * 64


def _stations(widths: tuple[float, ...]) -> tuple[EnvelopeStation, ...]:
    out = []
    for t, width in zip((0.2, 0.5, 0.8), widths):
        y = 0.2 + t * 0.5
        out.append(
            EnvelopeStation(
                t=t,
                contour_a=(0.5 - width / 2, y),
                contour_b=(0.5 + width / 2, y),
                visibility="visible",
            )
        )
    return tuple(out)


def _region(
    *,
    surface: str,
    widths: tuple[float, ...] = (0.10, 0.08, 0.06),
    artifact: str | None = None,
    observation_id: str | None = None,
    lock_digest: str = LOCK_DIGEST,
    state: str | None = None,
    visible_fraction: float = 1.0,
) -> RegionEnvelopeObservation:
    return RegionEnvelopeObservation(
        region_id="near_arm",
        side_role="near",
        axis_start=(0.5, 0.2),
        axis_end=(0.5, 0.7),
        stations=_stations(widths),
        visible_fraction=visible_fraction,
        occlusion=(),
        source_surface=surface,
        observation_id=observation_id or f"{surface}-near-arm-01",
        source_artifact_sha256=artifact or ("a" * 64 if surface == "reference" else "b" * 64),
        observation_lock_digest=lock_digest,
        source_state_sha256=state if surface == "drawing" else None,
        subject_height=0.8,
    )


def test_near_arm_width_and_visible_fraction_are_evidence_not_a_decision():
    reference = _region(surface="reference")
    drawing = _region(
        surface="drawing",
        widths=(0.04, 0.03, 0.025),
        visible_fraction=0.62,
        state=DRAWING_STATE,
    )
    comparison = compare_region_envelopes(
        reference,
        drawing,
        current_drawing_state_sha256=DRAWING_STATE,
    )
    payload = comparison.to_dict()
    assert payload["authority"] == "evidence_not_pass_fail"
    assert comparison.stations[0].width_ratio < 0.5
    assert comparison.visible_fraction_delta < 0.0
    assert comparison.integrity.valid
    assert comparison.integrity.drawing_state_current is True


def test_region_envelope_roundtrip_and_schema():
    region = _region(surface="reference")
    restored = RegionEnvelopeObservation.from_dict(region.to_dict())
    assert restored == region
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        validator = validators.validator_for(schema)(schema)
    validator.validate(region.to_dict())


def test_same_artifact_and_lock_mismatch_are_rejected():
    reference = _region(surface="reference", artifact="a" * 64)
    same_artifact = _region(surface="drawing", artifact="a" * 64, state=DRAWING_STATE)
    with pytest.raises(RegionEnvelopeIntegrityError, match="distinct source artifacts"):
        compare_region_envelopes(reference, same_artifact, current_drawing_state_sha256=DRAWING_STATE)

    mismatched_lock = _region(surface="drawing", lock_digest="f" * 64, state=DRAWING_STATE)
    with pytest.raises(RegionEnvelopeIntegrityError, match="lock digest"):
        compare_region_envelopes(reference, mismatched_lock, current_drawing_state_sha256=DRAWING_STATE)


def test_stale_drawing_state_is_rejected():
    reference = _region(surface="reference")
    drawing = _region(surface="drawing", state=DRAWING_STATE)
    with pytest.raises(RegionEnvelopeIntegrityError, match="stale"):
        compare_region_envelopes(
            reference,
            drawing,
            current_drawing_state_sha256="c" * 64,
        )


def test_duplicate_station_t_and_too_many_stations_are_rejected():
    with pytest.raises(ValueError, match="strictly increasing"):
        RegionEnvelopeObservation(
            region_id="arm",
            side_role="near",
            axis_start=(0.5, 0.2),
            axis_end=(0.5, 0.7),
            stations=(
                EnvelopeStation(0.5, (0.45, 0.4), (0.55, 0.4)),
                EnvelopeStation(0.5, (0.44, 0.5), (0.56, 0.5)),
            ),
            visible_fraction=1.0,
            occlusion=(),
            source_surface="reference",
            observation_id="bad",
            source_artifact_sha256="a" * 64,
            observation_lock_digest=LOCK_DIGEST,
        )

    stations = tuple(
        EnvelopeStation(
            t=(index + 1) / 17,
            contour_a=(0.45, 0.2 + index / 20),
            contour_b=(0.55, 0.2 + index / 20),
        )
        for index in range(17)
    )
    with pytest.raises(ValueError, match="2..16"):
        RegionEnvelopeObservation(
            region_id="arm",
            side_role="near",
            axis_start=(0.5, 0.2),
            axis_end=(0.5, 0.7),
            stations=stations,
            visible_fraction=1.0,
            occlusion=(),
            source_surface="reference",
            observation_id="too-many",
            source_artifact_sha256="a" * 64,
            observation_lock_digest=LOCK_DIGEST,
        )


def test_drawing_requires_state_digest():
    with pytest.raises(ValueError, match="source_state_sha256"):
        _region(surface="drawing", state=None)


def test_sixteen_station_comparison_stays_within_budget():
    def sixteen(surface: str, state: str | None):
        stations = tuple(
            EnvelopeStation(
                t=(index + 1) / 17,
                contour_a=(0.45, 0.2 + index / 24),
                contour_b=(0.55, 0.2 + index / 24),
            )
            for index in range(16)
        )
        return RegionEnvelopeObservation(
            region_id="near_arm",
            side_role="near",
            axis_start=(0.5, 0.2),
            axis_end=(0.5, 0.9),
            stations=stations,
            visible_fraction=1.0,
            occlusion=(),
            source_surface=surface,
            observation_id=surface + "-16",
            source_artifact_sha256=("1" if surface == "reference" else "2") * 64,
            observation_lock_digest=LOCK_DIGEST,
            source_state_sha256=state if surface == "drawing" else None,
        )

    reference = sixteen("reference", None)
    drawing = sixteen("drawing", DRAWING_STATE)
    start = time.perf_counter()
    for _ in range(100):
        compare_region_envelopes(
            reference,
            drawing,
            current_drawing_state_sha256=DRAWING_STATE,
        )
    elapsed = time.perf_counter() - start
    assert elapsed < 0.1, f"100 comparisons took {elapsed:.4f}s"
