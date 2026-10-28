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

## Tonal-area authorship is not line thickening (v1.2.1 development)

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
