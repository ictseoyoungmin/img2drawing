"""Opt-in exact fast timelapse exporter.

This package is staged for promotion; the canonical ``export_timelapse`` remains unchanged.
"""

from .exporter import FastTimelapseExport, export_fast_timelapse
from .frame_source import (
    CanonicalFrameSource,
    FastFrameSource,
    FastPathIneligible,
    FrameRenderConfig,
    inspect_fast_path_eligibility,
)

__all__ = [
    "FastTimelapseExport",
    "export_fast_timelapse",
    "FastFrameSource",
    "CanonicalFrameSource",
    "FastPathIneligible",
    "FrameRenderConfig",
    "inspect_fast_path_eligibility",
]
