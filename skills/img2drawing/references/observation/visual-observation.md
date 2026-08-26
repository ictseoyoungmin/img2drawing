# Visual observation

Read whole → region → part → relation. Evidence maps are aids, not semantic deciders.

## Pre-draw lock

Before drawing, record the subject’s view as an agent-authored
`ViewObservation` inside an `ObservationContract`, then freeze it with
`DrawingRun.lock_observation()`.

At minimum, observe and record:

- body view and torso turn (`front`, `back`, `side`, or a qualified three-quarter view);
- near-side role, using subject-side or image-side language when anatomy labels are uncertain;
- visibility of both arms and what occludes each one;
- major prop/body overlap order;
- explicit uncertainties that a later region review must not silently resolve.

This lock prevents a later drawing review from changing the interpretation of the
subject without invalidating the drawing branch. It does not infer pose or decide
whether the drawing is correct. If the view observation changes after drawing
starts, use `DrawingRun.reopen_observation()` so P1 and downstream evidence are
reopened together.

## Region observation

For later fidelity slices, preserve the distinction between an axis and an
occupied envelope. An arm can have a plausible shoulder→elbow axis while its
upper/mid/lower widths or visible length are badly under-drawn. Record those as
separate region evidence; do not let a landmark delta stand in for silhouette
measurement.

The S02 evidence utility uses an evaluator-selected normalized axis and paired
contour samples at up to 16 increasing stations:

```python
from img2drawing import EnvelopeStation, RegionEnvelopeObservation

near_arm = RegionEnvelopeObservation(
    region_id="near_arm",
    side_role="near",
    axis_start=(0.5, 0.2),
    axis_end=(0.5, 0.7),
    stations=(
        EnvelopeStation(0.2, (0.45, 0.3), (0.55, 0.3)),
        EnvelopeStation(0.5, (0.46, 0.45), (0.54, 0.45)),
        EnvelopeStation(0.8, (0.47, 0.6), (0.53, 0.6)),
    ),
    visible_fraction=0.9,
    occlusion=(),
    source_surface="reference",  # use "drawing" for the independent drawing profile
    observation_id="reference-near-arm-01",
    source_artifact_sha256="...64 lowercase hex characters...",
    observation_lock_digest="...the frozen pre-draw lock digest...",
)
```

`compare_region_envelopes()` returns width ratios, local-axis normalized widths,
visible-fraction drift, and occlusion-order changes. It is evidence only: it
does not emit an artistic `PASS` or `FAIL`. Drawing evidence must carry a
current drawing-state digest when compared, so stale measurements are rejected.

At P3, feed region evidence into all eight required region entries
(`head_hair`, `torso_orientation`, `near_arm`, `far_arm`, `pelvis`, `leg_A`,
`leg_B`, `attached_object`). The visual evaluator receives a blind packet with
the frozen observation, current drawing, stage contract, and evidence refs; it
does not receive worker rationale or any prior verdict. Process PASS and visual
PASS remain separate until the runtime's dual gate checks both.

For side/three-quarter ambiguity, add `TorsoOrientationObservation` evidence:
record the view label, torso turn, near-side role, shoulder pair, torso bounds,
and independent near/far arm exposure. A similar torso width with a large
orientation or exposure delta is still a structural discrepancy; do not let
width alone close the region.

For lower-body review, keep pelvis bounds/turn, `leg_A` and `leg_B` station
profiles, support leg, counterbalance direction, and inter-leg negative-space
stations in one `LowerBodyObservation`. Parallel rails can preserve two leg
axes while collapsing both taper and the negative space between them.

For head identity at primary-mass level, use `HeadHairObservation` before face
features: head top/chin, left/right cranial and jaw contours, head bounds, bob
hair envelope, hair occlusion, and anatomical uncertainty. This separates a
large spherical head or helmet-like hair mass from later eye/nose/mouth detail.

Attached objects use `PropTopologyObservation`, never rifle-specific semantics:
record the major axis, width-change points, terminal masses, body overlap points,
visible interruptions, and occlusion order. A prop axis that matches while its
width transitions or body overlap changes is still unresolved topology.
