from __future__ import annotations

from typing import Iterable, Mapping

from .model import RegistrationConnection, RegistrationGraph, RegistrationLandmark

# Stable human-pose vocabulary inspired by common pose-estimation layouts, but owned by
# img2drawing and extended with drawing-specific construction landmarks.
HUMAN_POSE_LANDMARKS = (
    "nose", "neck_base", "shoulder_R", "elbow_R", "wrist_R",
    "shoulder_L", "elbow_L", "wrist_L", "pelvis_center", "hip_R",
    "knee_R", "ankle_R", "hip_L", "knee_L", "ankle_L",
    "eye_R", "eye_L", "ear_R", "ear_L", "big_toe_L", "small_toe_L",
    "heel_L", "big_toe_R", "small_toe_R", "heel_R",
)

DRAWING_LANDMARKS = (
    "head_top", "chin", "ribcage_center", "ribcage_bottom", "sternum",
    "pelvis_top", "pelvis_bottom", "hand_extent_L", "hand_extent_R",
    "foot_extent_L", "foot_extent_R", "support_point", "center_of_mass_hint",
    "silhouette_leftmost", "silhouette_rightmost", "subject_top", "subject_bottom",
)

HUMAN_POSE_CONNECTIONS = (
    ("neck_base", "pelvis_center", "torso_axis"),
    ("neck_base", "shoulder_R", "skeleton"), ("shoulder_R", "elbow_R", "skeleton"), ("elbow_R", "wrist_R", "skeleton"),
    ("neck_base", "shoulder_L", "skeleton"), ("shoulder_L", "elbow_L", "skeleton"), ("elbow_L", "wrist_L", "skeleton"),
    ("pelvis_center", "hip_R", "skeleton"), ("hip_R", "knee_R", "skeleton"), ("knee_R", "ankle_R", "skeleton"),
    ("pelvis_center", "hip_L", "skeleton"), ("hip_L", "knee_L", "skeleton"), ("knee_L", "ankle_L", "skeleton"),
    ("neck_base", "nose", "head_axis"),
    ("nose", "eye_R", "face"), ("eye_R", "ear_R", "face"),
    ("nose", "eye_L", "face"), ("eye_L", "ear_L", "face"),
    ("ankle_L", "big_toe_L", "foot"), ("big_toe_L", "small_toe_L", "foot"), ("ankle_L", "heel_L", "foot"),
    ("ankle_R", "big_toe_R", "foot"), ("big_toe_R", "small_toe_R", "foot"), ("ankle_R", "heel_R", "foot"),
    ("shoulder_R", "shoulder_L", "shoulder_axis"), ("hip_R", "hip_L", "pelvis_axis"),
)


def human_connections(available: Iterable[str]) -> tuple[RegistrationConnection, ...]:
    names = set(map(str, available))
    return tuple(RegistrationConnection(a, b, role) for a, b, role in HUMAN_POSE_CONNECTIONS if a in names and b in names)


def make_human_pose_registration(
    *, source_size: tuple[int, int], landmarks: Mapping[str, RegistrationLandmark],
    subject_bounds: tuple[float, float, float, float] | None = None,
    provenance: Mapping | None = None,
) -> RegistrationGraph:
    unknown = set(landmarks) - set(HUMAN_POSE_LANDMARKS) - set(DRAWING_LANDMARKS)
    if unknown:
        raise ValueError(f"unknown human registration landmark(s): {sorted(unknown)}")
    return RegistrationGraph(
        source_size=source_size, landmarks=dict(landmarks),
        connections=human_connections(landmarks), subject_bounds=subject_bounds,
        graph_type="human_pose", provenance=dict(provenance or {}),
    ).validated()
