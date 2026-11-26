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

## Inspect a turning value family in two directions

When a broad turning surface reads flat or tubular, inspect an across-form patch chain at a
representative visible section and a separate along-form chain through successive visible
sections. Choose corresponding patches yourself; include a light-facing plane, turn and
shadow only where actually visible, and distinguish a contact shadow at an overlap from a
soft form turn. Do not force a symmetric or fixed number of bands. Use the existing
`inspect_tonal_patches` separately on each chain at the same before/after cursors. Check
relative value order and unexpected reversals in both directions; also inspect the boundary
ownership and whole-form read at the requested output scale. A smooth single chain or a
stronger highlight does not compensate for a missing turn or an invented overlap.

If the wide dark family fails, preview retirement and replacement of that family with
explicit strokes of controlled width, density and pressure. Reserve the larger light plane
first; add a local lift only for an observed narrow residual light. Do not repair a flat
volume by adding more bright marks to its center.

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

For thin light hardware or reflected hair highlights, an alternative to leaving
white gaps between graphite strokes is an explicitly observed ordered lift
through the opt-in normalized profile. Construct a coherent dark mass with
strokes aligned to the material/form, then use small reviewed eraser paths
(see stroke dynamics). Prefer a restrained value family over a repetitive
cross-grain hatch; do not infer an unobserved line, treat the whole plane as a
uniform raster fill, or use strong lifts as a substitute for correct geometry.
Inspect both contact ends and surviving marks. If rounded ends create scallops,
reconsider the contact paths and soften their contribution rather than outlining
every endpoint. A bright highlight alone does not certify natural form.

### Compare explicit tonal alternatives without applying them

Use `inspect_tonal_proposals` from `img2drawing.authoring` when two or more reviewed stroke
edits compete. Supply named proposals (`edits`, `retire_ids`, `additions`, `erasures`), named
ordered chains of `TonalPatch`, and optional explicit `TonalAreaPlan` objects. All alternatives
share the same blank paper, canonical starting render and reference. The helper returns each
preview's existing action digest/state/pixel binding, chain relations and area changes; it
never commits or ranks the candidates. Example:

```python
report = inspect_tonal_proposals(session, {"gentle": {"edits": gentle_edits},
    "rebuild": {"retire_ids": retired_ids, "additions": replacement_marks}},
    {"across": across_patches, "along": along_patches}, "new-preview-dir",
    reason=reason, observation_id=oid, plans=(plan,))
```

Use 1–4 alternatives, 1–8 chains and at most eight area plans; adjust the explicit
`max_pixel_work` budget only when warranted. A fresh directory is required. Compare actual
preview images and evidence, then apply only the chosen exact batch with its base cursor,
state and action digest. Measurements diagnose, not select artistic correctness.

## Strip inspection of repeated tonal bands

When stripes or abrupt stroke shoulders recur within one visibly continuous plane,
choose matching subject and canvas rectangles spanning that plane, excluding true
boundaries. `TonalBandProbe(label, subject_box, canvas_box, axis="x", bins=16)` divides
them into explicit equal-width vertical strips (use `axis="y"` for horizontal strips).
`inspect_tonal_bands(session, probe, cursors=..., cached_renders=...)` uses the same
canonical patch inspection and validated cached renders. `probe.patches()` can also
be passed as a chain to `inspect_tonal_proposals`; `probe.summarize(chain_result)`
then reports local turns, absolute second differences and unmatched turn positions.
This avoids hand-defining dozens of adjacent boxes, not the duty to identify a form.
An unmatched turn may reflect incorrect registration, a true fold, or a misplaced
highlight. Treat the quantities as diagnostic evidence, not a loss to minimize, and
review the actual image before committing a replacement family. Do not erase real
folds merely to flatten the measured signal. For oblique or curving planes choose
explicit TonalPatch chains instead of an axis-aligned strip probe.
