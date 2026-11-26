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

## Recalibrate value when changing material contract

When creating a session with the optional opacity-normalized profile, do not reuse a
v11 shading recipe as a calibrated value target. Broad width alone does not determine
value. Read a small actual stroke family, choose light/middle/dark relationships from
visible form, then preview explicitly selected changes with the existing StrokeEdit
batch (see `../markmaking/stroke-dynamics.md`). In a continuous plane, use gradual
pressure approaches and departures and controlled overlapping deposits. Preserve real
contact boundaries; do not stack stronger round-ended bands to raise an area mean.
Compare a patch chain both to the original observation and to the previous render:
reaching the right local mean while increasing false reversals is not closure.
Reject an unhelpful preview and re-preview only the intended subset before committing.
For bright thin hardware, preserve the visible interval during the surrounding value
construction; broad along-path pressure troughs can make a dark plane into alternating
cells, so they do not automatically express a narrow metallic highlight. Do not draw
unseen hardware or manufacture white pixels with a separate raster path.

## Reserve narrow light intervals before rebuilding dark marks

For a narrow light edge on a dark plane, explicitly decide which visible light interval
belongs to the object, and where the surrounding graphite contacts must stop. Work in
small reviewed value families rather than cutting broad pressure troughs at every detail.
Wide rounded strokes across adjacent bays may produce isolated oval shadows; fine adjacent
marks can retain a brighter seam but may introduce coarse repetitive texture. Neither is
a universal material recipe. Use a local three-patch comparison (light center and the two
adjacent dark shoulders) plus a whole-plane reading; high contrast alone is not a pass.
If changing the family, preview retirement and explicit new marks together using the
mixed stroke-edit batch. Reject candidates that erase ownership edges, cross occluders,
create false bright gaps, or replace continuous dark tone with mechanical striping.
