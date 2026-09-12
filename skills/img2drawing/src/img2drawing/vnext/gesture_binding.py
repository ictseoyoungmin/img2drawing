"""Bind the user-facing gesture mode into the stage-free intent runtime.

Gesture was introduced first as an instruction-graph mode. This binding keeps that user-facing
mode and the public ``DrawingIntent`` vocabulary aligned without introducing a workflow stage.
The operation is idempotent because package imports may be repeated by tooling.
"""

from __future__ import annotations

from . import intent as _intent


def bind_gesture_intent_runtime() -> tuple[str, ...]:
    """Register ``gesture`` as a public drawing-mode selection and return the mode tuple."""

    if "gesture" not in _intent.DRAWING_MODES:
        _intent.DRAWING_MODES = ("gesture", *_intent.DRAWING_MODES)

    if "gesture" not in _intent._MODE_GUIDES:
        _intent._MODE_GUIDES["gesture"] = _intent.ModeGuide(
            "mode-gesture-v1",
            "gesture",
            (
                "whole-pose action, support, and balance before local description",
                "head facing and cranial-to-jaw direction",
                "ribcage/pelvis turn, asymmetry, and width transition",
                "major limb chains, decisive negative spaces, and prop/body anchors",
            ),
            (
                "line of action and support relation",
                "directional head volume rather than a circle symbol",
                "specific asymmetric ribcage and pelvic masses rather than boxes or rounded blobs",
                "connected limb chains with joint direction and width transition",
                "selective outer envelope only where it strengthens the pose read",
            ),
            (
                "facial, garment, and surface detail that does not change the gesture read",
                "generic circle, box, bean, capsule, or polygon symbols left as finished masses",
                "uniform contour polishing before the whole action and support read",
            ),
            (
                "whole-pose readability with economical marks",
                "reference-specific direction, asymmetry, support, and occupied volume",
            ),
            (
                "Does the whole pose read without mentally borrowing missing relations from the reference?",
                "Does the head preserve facing and jaw/profile direction instead of collapsing to a circle?",
                "Do torso and pelvis preserve observed asymmetry and attachment directions instead of becoming a box or smooth blob?",
                "Are both major limb chains, support, negative spaces, and decisive prop/body anchors present?",
            ),
        )

    return _intent.DRAWING_MODES


__all__ = ["bind_gesture_intent_runtime"]
