# Broad graphite

Broad graphite is not merely a thicker version of a thin contour. Once contact becomes broad, the
visible material can include a denser core, softer shoulders, paper-tooth breakup, local deposition
variation, and pressure-dependent contact width.

Use this leaf only when the drawing actually contains broad graphite or a broad textured value
mark. Do not widen ordinary linework just to expose renderer texture.

## Canonical behavior

Under `canonical-pencil`, broad material may change edge texture and shoulder behavior, but it
should not casually erase a deliberately strong authored value. High authored pressure/opacity
remains meaningful even when width crosses into broad contact.

## Manga-light behavior

Under `manga-light`, a broad mark may intentionally stay airy and lighter through its center. This
can create a delicate monochrome or romance/shojo-like line language. Treat that as intentional
only when the active style requests it; otherwise route the lost value as a material-policy
residual.

## Dry-graphite-expressive behavior

Under `dry-graphite-expressive`, paper tooth, grain, shoulder breakup, and local deposition
variation are allowed to become visually prominent. Texture does not excuse bad geometry or weak
value organization.

## Core and shoulder are different concerns

Reason about broad contact as at least two perceptual regions:

```text
outer shoulder  -> grain, tooth, breakup, soft contact
inner core      -> authored value / pressure authority
```

The exact implementation is a renderer concern. The Agent only needs to inspect whether the
resulting core/shoulder relationship matches the active style and drawing intent.

## Performance awareness

Broad contact may cost more to build than ordinary thin strokes because the renderer has more
material structure to resolve. That is not a reason to avoid broad marks when the drawing needs
them. Reuse the supported runtime and persistent cache rather than replacing the effect with a
hand-built raster shortcut.

## Tonal-area authorship is not line thickening (v1.2.1)

For hair masses, broad dark garments, deep folds or other *areas*, distinguish
the **spatial area** from the **contact footprint of a single stroke**:

1. Observe and record the area boundary, plane or hair-clump owner, light
   direction and neighboring contacts before placing any value strokes.
2. Reserve observed highlights and reflected light as explicit negative
   spaces. Do not let progressively wider marks consume them accidentally.
3. Choose a directional stroke family for form/strand/fabric flow. Build tone
   through controlled density, pressure and layering, inspecting at the whole
   form and enlarged crop after each meaningful tonal group.
4. Count coverage by purpose. Several opaque, heavily overlapping strokes
   occupying the same region without explaining form are a **tonal-overdraw
   residual**; soften or retire them rather than add more width.
5. Reopen boundary, clump, garment-plane or overlap geometry if the only way
   to reproduce dark material is a single implausibly wide solid stripe.
6. A 4B `broad-graphite` mark remains pencil material. It is *not* an ink
   brush or automatic area fill. No generic width cutoff is a substitute for
   comparing the observed area's width, graphite core/shoulder and reserved light.

Keep the stroke group in the canonical history with semantic part and observed
area ownership recorded in the existing action metadata. The optional
`img2drawing.authoring.TonalAreaPlan` makes the observed boundary, direction,
intended density/value, pressure range and reserved highlights explicit. It
attaches only validated **planning metadata** to individual authored strokes;
it does not derive any marks, authorize raster fills or certify accurate
coverage. Inspect every resulting mark family at the current canvas scale.
Do not replace authored marks with pixel tracing.

### Override consistency

`broad-graphite` is a semantic resolver preset: it maps to the runtime
`accent_pencil` tool with 4B and specific hardness/grain/pressure/opacity.
Prefer `resolve_mark_for_intent(..., modifiers={...})` so the whole material is
settled before drawing. If a supported `tool_overrides` modifier is supplied
at `DrawingSession.draw()` time, it selectively updates the resolved map
while inherited grain/hardness remain intact. The stored markmaking
provenance must identify that **executed** material, not the earlier snapshot.

## Inspect and correct actual deposits

Use `inspect_tonal_interval` on canonical before/after cursors and selected
live `TonalAreaPlan` IDs. Read protected coverage, saturation and darkness
change relative to blank paper. Outside-area additions include all edits in
the interval, so isolate the responsible mark family before attributing leakage.
Current-stroke centerline exposure and direction/pressure reports are approximate
diagnostics, not the raster contribution of a stroke. Explicit disjoint area
pairs can report signed tonal separation; they do not rank artistic quality.
Select the responsible stroke and point interval yourself, prepare an explicit
`TonalPressureAdjustment`, then preview and apply via the existing edit path.
A pressure reduction may fail to recover the clump: reopen geometry and mark
placement instead of repeatedly darkening or weakening unrelated areas.

The inspection helper lives in `img2drawing.inspection` and accepts
`inspect_tonal_interval(session, before_cursor, after_cursor, area_ids=...)`.
Optional disjoint separation_pairs compare mean darkness. Optional cached_renders
maps requested cursor integers to trusted canonical PNG paths. Manifests, profile,
history prefix, cursor state and pixel hashes must match; invalid supplied evidence
fails closed. Missing cursors render normally. The correction proposal is an
explicit authoring helper, not an area-to-stroke generator.

When mean value improves but alternating bands remain on a continuous observed plane, use
`../description/value-edge-and-graphite.md` for explicit local value-continuity evidence before
repeating wider or darker strokes. The chain is diagnostic, not a smoothing or automatic fill tool.

On the optional normalized contract, retune explicit width/opacity and local pressure
together when a value family is too pale or its contact footprints separate into
stripes. Read actual overlap and soft turns first; a stronger midpoint with an abrupt
terminal may make the band more obvious. Use the existing prospective stroke-edit
preview and value-continuity checks; no preset is a universal exposure conversion.

## Explicit contact width along a stroke

For a new session choose `RenderProfile.opacity_normalized(w, h, contact_width=True)`
when a single continuous authored graphite mark needs independently controlled contact
width. This opt-in contract also supports pressure-shaped erasure. Old sessions are
not migrated. The nominal tool width remains the maximum; pressure, grade and hand
response resolve the usual diameter, then explicit arc-length factors in [.15, 1]
narrow that diameter without changing the authored pressure samples.

```python
from img2drawing.authoring import ContactWidthProfile, StrokeEdit
width = ContactWidthProfile(((0., .25), (.28, 1.), (.72, .82), (1., .2)))
# Supply width.metadata(existing_metadata) to ordinary session.draw or draw_many.
# To revise a chosen current mark without re-authoring its pressure:
current = session.current_stroke(stroke_id)
edit = StrokeEdit(stroke_id, tuple(current.points), contact_width_profile=width)
```

The width recipe is persisted material metadata, relative to the normalized rendered
path; the stroke remains an explicit authored path. `read_contact_width_profile`
recovers it. Whole-path geometry changes remap relative arc positions; split edits
restrict and renormalize the two subintervals. For a parametric curve edit combine
`CurveDefinition.draw_kwargs(metadata=width.metadata(...))` on creation, or preserve
its existing recipe with `StrokeEdit`. Width factors of one retain ordinary pixels.
The renderer still models graphite deposition; a narrower footprint can change
actual overlap and apparent density, so compare real renders rather than assuming
constant luminance. Do not infer a brush footprint from reference pixels or substitute
one wide stroke for observed overlap and form. Keep only visibly justified contacts.


## Optional side-of-pencil surface contact

Use `RenderProfile.opacity_normalized(w, h, surface_contact=True)` for a **new** session
only when the conventional narrow core on broad graphite makes observed soft planes read
as stripes. The opt-in contract includes width control and pressure-shaped lift; unmarked
strokes use the same v3 contact. Never migrate a finished session for this purpose.

```python
from img2drawing.authoring import SurfaceContactProfile, StrokeEdit
side = SurfaceContactProfile(shoulder=.85)
# Combine with existing explicit material/curve/width metadata on draw.
# Or compare a material-only candidate on a current stroke:
edit = StrokeEdit(stroke_id, tuple(session.current_stroke(stroke_id).points),
                  surface_contact_profile=side)
```

The tangent-oriented contact has a broad central interval and smooth transverse shoulder;
`shoulder` is the fraction of transverse radius used for that transition (.35–.85).
Longitudinal optical depth is integrated by traveled distance. Broad side marks do not
receive a separate narrow dark core; paper-fixed texture remains. Thin contacts retain
ordinary behavior. This changes footprint physics, not geometry or underlying pressure.
The persisted recipe is recoverable with `read_surface_contact_profile`; a `StrokeEdit`
with `clear_surface_contact=True` returns to ordinary contact in the same v4 session.

This is not a universal softening preset. Overlap depends on actual neighboring stroke
spacing, pressure, width and turns. Too much overlap produces dark rails; too little
produces gaps. Compare the same paths and values first, then calibrate tone and overlap
with explicitly chosen edits. Use matched strip-chain evidence and inspect the whole
plane; a smaller ripple achieved by making the entire plane pale is not a quality pass.
Do not fill reference-derived areas or generate automatic hatch paths.
