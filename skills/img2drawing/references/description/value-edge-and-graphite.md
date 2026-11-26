# Value, edge, and graphite

Value and pencil material should reinforce structure rather than compensate for uncertain
geometry.

## Value

Group large value families before texture. Preserve reserved lights inside darker masses
instead of erasing them back after indiscriminate fill. A value region should correspond to
an observed or intentionally declared region, not a cloud of independent dark strokes.

## Edge

Use harder edges where the subject shows a decisive boundary or contact and softer edges
where form turns, atmosphere, hair, or material calls for a transition. Edge hierarchy
should agree with overlap and depth.

## Graphite marks

Vary pressure and width according to function. Construction can remain lighter; decisive
contour/contact may carry more weight; accents should be selective. Do not simulate
fidelity by scribbling many identical dark strokes over a weak boundary.

When value obscures shape, repair shape first, then rebuild the value region.

## Local value continuity

An area-average value or total coverage cannot show whether a turning plane has acquired
unobserved alternating bright and dark bands. When the whole-form read suggests this problem,
select an ordered chain of small visible patches along the same observed plane or clump.
Keep the correspondence explicit, including independently selected subject and canvas boxes.
Compare the direction and magnitude of adjacent changes, not photographic brightness as an
absolute drawing target. Keep a real highlight, shadow boundary, or occlusion if the subject
supports it; do not force every chain to be smooth.

```python
from img2drawing.inspection import TonalPatch, inspect_tonal_patches

# Choose actual subject/canvas rectangles yourself, in order along the observed form.
patches = [TonalPatch(label, subject_box, canvas_box) for label, subject_box, canvas_box in observed_patches]
report = inspect_tonal_patches(session, patches, cursors=[before_cursor, after_cursor])
```

The boxes are (left, top, right, bottom), in original subject and unscaled canvas pixels.
Use 2–64 unique labels, 1–8 distinct valid cursors, and optionally a declared deadband
(default 8/255). The report gives per-patch mean and 10/50/90 percentiles, adjacent signed
changes, opposite directions, total absolute adjacent variation, and direction reversals
(ignoring deadband-flat steps). The chain summary is equally weighted by patch, not image area.
Reference values are grayscale darkness; drawing values are relative to blank paper. The
inspection is read-only, with existing verified render-cache semantics. For saved PNG-only
comparisons use `compare_tonal_patches(subject, drawing, paper, patches, output_scale=1)`;
it explicitly reports unverified external image provenance. Neither function certifies a
likeness, assigns a correction, authorizes pixel copying, or issues an artistic PASS.

On a smooth observed plane, reopen invented ribbon-like marks instead of darkening the
whole region to reach a mean. Rebuild the underlying value family with explicitly authored
light, controlled deposits and preserve actual soft turns. Use selective stronger contact
only where an observed boundary warrants it; render and reassess both the local chain and
whole form. Route material defects through the existing markmaking residual path only if
correctly placed explicit strokes still fail the intended contact.
