# Contour and overlap

Every contour should have ownership: know what lies on each side of the line.

Use exterior contour for the true visible boundary of the subject or part. Use internal
lines only when they describe overlap, material change, form turning, seam/fold structure,
or an identity-bearing feature.

Do not draw two nearly parallel contours for uncertainty. Re-observe and choose the better
boundary.

## Occlusion is not structural termination

When a background form disappears behind a foreground form, distinguish **visible contour
termination** from **structural continuation**.

The visible contour normally stops at the foreground occluder. That does not mean the background
form should be treated as structurally ending there. If its continuation materially affects pose,
topology, contact, depth, or a downstream visible anchor, infer the minimum hidden structure needed
to keep the visible fragments coherent. See `../foundation/occlusion-inference.md`.

Use this separation:

```text
visible boundary before occlusion   → render
provisional hidden continuation     → reason with it; render only as temporary construction if useful
foreground occluder boundary        → render with correct ownership
visible reappearance after occlusion → render from the observed point
```

Do not continue a jaw under hair, a sleeve under a foreground object, a limb through another
form, or a component through a housing as a **final visible contour** merely because you inferred
its hidden continuation. A temporary construction cue may cross the occluder when it helps test
continuity, but it should be retired or softened before it can read as observed appearance.

At overlaps, prioritize the foreground edge and let the background form disappear cleanly. The
reappearance point matters: it defines depth and should match the observed relation. When both
entry and reappearance are visible, test whether one plausible hidden continuation can connect
them without forcing an unsupported bend or moving either visible anchor. If not, reopen the
parent structure or occlusion-order premise rather than polishing the local edge.

When there is no visible reappearance, reduce certainty instead of either inventing a complete
hidden terminal or pretending the part has no continuation. Infer only enough parent relation to
support the visible structure.

Contact lines—foot/ground, hand/prop, garment/body compression, part/part attachment—should state
where forms actually meet rather than merely touching symbolically. A hidden contact relation may
be inferred when visible geometry requires it, but its exact invisible contour or attachment detail
must not be fabricated.
