# Portrait likeness review

Open this leaf when a face must resemble a specific observed person rather than merely read as a
plausible generic face.

This leaf owns **local portrait fidelity review**. It complements, but does not replace,
`visual-quality-gates.md`.

## Local normalization

Do not normalize portrait errors by the entire figure height when the practical concern is the face.
Use an explicitly chosen local facial span such as:

- head width;
- crown-to-chin height;
- pupil-to-pupil distance;
- nose-base to chin distance.

A small face error can materially change identity while remaining tiny under full-body normalization.

## Useful portrait comparison packet

Compare the visible, relevant relationships below; record ambiguous or occluded ones as unmeasured, not invented:

1. head envelope and jaw/chin silhouette;
2. eye envelopes, spacing, tilt, and iris visibility;
3. nose bridge / tip / wing / base relation;
4. mouth width, corner direction, and mouth-to-chin distance;
5. cheek volume and smile deformation;
6. hairline / temple / ear / neck handoffs.

Do not claim likeness closure from recognition alone.

## Ranking residuals

Rank residuals by identity impact rather than by line neatness.

High-impact examples:

- wrong eye spacing or tilt;
- wrong jaw width or chin height;
- mouth corners placed too high/low;
- brow-to-eye relation missing;
- genericized hairline or parting.

Lower-impact examples:

- a slightly rough strand accent;
- a non-critical texture mark;
- a minor tonal patch away from identity anchors.

## What counts as improvement

A correction is portrait improvement when it makes the drawing more faithful to the observed person,
not merely cleaner or more conventionally attractive.

Reject changes that:

- regularize asymmetry;
- enlarge eyes because it looks nicer;
- sharpen a nose edge that is only a soft value turn;
- substitute a tidy mouth shape for the observed smile.

## Finish check

Before calling a portrait substantially resolved, explicitly name the largest remaining identity
mismatches. If any of them still dominate the read, the portrait is not finished even if the drawing
is otherwise polished.

## Explicit local measurement and correction

Use `img2drawing.observation.compare_portrait_landmarks()` or `portrait_likeness_packet()` with
independently observed reference/current-render LandmarkSets and the same explicit Registration.
Choose a visible face-width span and optionally a visible head-height span. Use named groups for
each eye, nose, mouth and jaw where readable; report per-group error and the largest local mismatch,
not only one average. Freeze reference anchors and normalizers when comparing alternatives. A point
from an authored stroke is not evidence that its visible rendered position is correct. Re-observe
the actual pixels at the same crop and scale. The packet provides distances, ratios and axes, not
a likeness score, identity recognition, or automatic correction.

For full-figure drawings with a readable, likeness-bearing face this same review applies even when
no portrait was explicitly requested. Keep the face-local result separate from full-body proportion
error. Use [facial construction](../figure/facial-construction.md), [features](../figure/facial-features.md),
[expression](../figure/facial-expression.md) and [values](../figure/facial-values.md) only as needed.
Preview an explicit correction with the existing stroke-edit API, compare at both scales, then apply
only a visually justified candidate; otherwise preserve the earlier state and reopen.

Example (labels are agent-declared, not a detection vocabulary):

```python
from img2drawing.observation import portrait_likeness_packet

review = portrait_likeness_packet(
    reference_points, current_render_points, registration=registration,
    feature_labels=("left_outer", "left_inner", "right_inner", "right_outer",
                    "mouth_left", "mouth_right"),
    width_axis=("visible_left_cheek", "visible_right_cheek"),
    feature_groups={"left_eye": ("left_outer", "left_inner"),
                    "right_eye": ("right_inner", "right_outer"),
                    "mouth": ("mouth_left", "mouth_right")},
    ratio_checks=(( ("mouth_left", "mouth_right"),
                    ("visible_left_cheek", "visible_right_cheek") ),),
    axis_checks=(("mouth_left", "mouth_right"),),
)
```

Ratio and axis computations reuse the existing `compare_ratios()` and `compare_axes()`; the
packet retains their inputs. If height anchors are unavailable, omit `height_axis` rather than
inventing a diagonal normalizer.
