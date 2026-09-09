"""Dev-only bridge for historical R23 tests.

The installable package no longer ships ``img2drawing.legacy.r23``. A subset of old tests still
exercise the R23 implementation roots that remain in ``src`` pending their coordinated removal.
During pytest collection only, expose the former import path as a lazy alias to the real owning
modules. Fresh subprocess tests and installed-wheel checks do not see this bridge.
"""

from __future__ import annotations

from importlib import import_module
import sys
from types import ModuleType


_R23_TEST_EXPORTS: dict[str, tuple[str, str]] = {
    "DrawingRun": ("img2drawing.run", "DrawingRun"),
    "DrawingRunResult": ("img2drawing.run", "DrawingRunResult"),
    "ObservationContract": ("img2drawing.observation", "ObservationContract"),
    "ViewObservation": ("img2drawing.observation", "ViewObservation"),
    "FrozenObservationRecord": ("img2drawing.observation", "FrozenObservationRecord"),
    "ObservationReopenRecord": ("img2drawing.observation", "ObservationReopenRecord"),
    "ModularGrammarCard": ("img2drawing.exemplar.ablation", "ModularGrammarCard"),
    "consume_grammar_card": ("img2drawing.exemplar.ablation", "consume_grammar_card"),
    "AblationTrial": ("img2drawing.exemplar.ablation", "AblationTrial"),
    "ExemplarAblationReport": ("img2drawing.exemplar.ablation", "ExemplarAblationReport"),
    "run_exemplar_ablation": ("img2drawing.exemplar.ablation", "run_exemplar_ablation"),
    "AcceptedResidual": ("img2drawing.review", "AcceptedResidual"),
    "AdaptiveEvidencePolicy": ("img2drawing.review", "AdaptiveEvidencePolicy"),
    "AssistiveROIProposal": ("img2drawing.review", "AssistiveROIProposal"),
    "ExcludedRegion": ("img2drawing.review", "ExcludedRegion"),
    "PreviewArtifact": ("img2drawing.review", "PreviewArtifact"),
    "RegionClosureEntry": ("img2drawing.review", "RegionClosureEntry"),
    "RegionClosureManifest": ("img2drawing.review", "RegionClosureManifest"),
    "VisualFidelityReviewRecord": ("img2drawing.review", "VisualFidelityReviewRecord"),
    "P4_RESOLVED_REGIONS": ("img2drawing.review", "P4_RESOLVED_REGIONS"),
    "P5_RESOLVED_REGIONS": ("img2drawing.review", "P5_RESOLVED_REGIONS"),
    "ResolvedFormEntry": ("img2drawing.review", "ResolvedFormEntry"),
    "ResolvedFormManifest": ("img2drawing.review", "ResolvedFormManifest"),
    "ResolvedFormReviewRecord": ("img2drawing.review", "ResolvedFormReviewRecord"),
    "ConstructionRetirementRecord": ("img2drawing.review", "ConstructionRetirementRecord"),
    "IdentityFinishProfile": ("img2drawing.review", "IdentityFinishProfile"),
    "CalibrationSheet": ("img2drawing.review", "CalibrationSheet"),
    "IdentityPreflightResult": ("img2drawing.review", "IdentityPreflightResult"),
    "preflight_identity_finish": ("img2drawing.review", "preflight_identity_finish"),
    "IdentityFinishManifest": ("img2drawing.review", "IdentityFinishManifest"),
    "build_resolved_form_blind_packet": ("img2drawing.review", "build_resolved_form_blind_packet"),
    "EnvelopeStation": ("img2drawing.registration", "EnvelopeStation"),
    "RegionEnvelopeObservation": ("img2drawing.registration", "RegionEnvelopeObservation"),
    "RegionEnvelopeIntegrityError": ("img2drawing.registration", "RegionEnvelopeIntegrityError"),
    "EnvelopeIntegrity": ("img2drawing.registration", "EnvelopeIntegrity"),
    "AxisEnvelopeEvidence": ("img2drawing.registration", "AxisEnvelopeEvidence"),
    "StationEnvelopeEvidence": ("img2drawing.registration", "StationEnvelopeEvidence"),
    "RegionGeometryComparison": ("img2drawing.registration", "RegionGeometryComparison"),
    "compare_region_envelopes": ("img2drawing.registration", "compare_region_envelopes"),
    "TorsoOrientationObservation": ("img2drawing.registration", "TorsoOrientationObservation"),
    "TorsoOrientationIntegrityError": ("img2drawing.registration", "TorsoOrientationIntegrityError"),
    "TorsoOrientationComparison": ("img2drawing.registration", "TorsoOrientationComparison"),
    "compare_torso_orientation": ("img2drawing.registration", "compare_torso_orientation"),
    "LowerBodyObservation": ("img2drawing.registration", "LowerBodyObservation"),
    "LowerBodyIntegrityError": ("img2drawing.registration", "LowerBodyIntegrityError"),
    "LowerBodyComparison": ("img2drawing.registration", "LowerBodyComparison"),
    "compare_lower_body": ("img2drawing.registration", "compare_lower_body"),
    "HeadHairObservation": ("img2drawing.registration", "HeadHairObservation"),
    "HeadHairIntegrityError": ("img2drawing.registration", "HeadHairIntegrityError"),
    "HeadHairComparison": ("img2drawing.registration", "HeadHairComparison"),
    "compare_head_hair": ("img2drawing.registration", "compare_head_hair"),
    "PropWidthChangePoint": ("img2drawing.registration", "PropWidthChangePoint"),
    "PropTerminalMass": ("img2drawing.registration", "PropTerminalMass"),
    "PropBodyOverlapPoint": ("img2drawing.registration", "PropBodyOverlapPoint"),
    "PropTopologyObservation": ("img2drawing.registration", "PropTopologyObservation"),
    "PropTopologyIntegrityError": ("img2drawing.registration", "PropTopologyIntegrityError"),
    "PropTopologyComparison": ("img2drawing.registration", "PropTopologyComparison"),
    "compare_prop_topology": ("img2drawing.registration", "compare_prop_topology"),
}


def _getattr(name: str):
    try:
        module_name, attribute_name = _R23_TEST_EXPORTS[name]
    except KeyError as exc:
        raise AttributeError(name) from exc
    return getattr(import_module(module_name), attribute_name)


legacy = ModuleType("img2drawing.legacy")
legacy.__path__ = []  # type: ignore[attr-defined]
r23 = ModuleType("img2drawing.legacy.r23")
r23.__getattr__ = _getattr  # type: ignore[attr-defined]
legacy.r23 = r23  # type: ignore[attr-defined]
sys.modules.setdefault("img2drawing.legacy", legacy)
sys.modules.setdefault("img2drawing.legacy.r23", r23)
