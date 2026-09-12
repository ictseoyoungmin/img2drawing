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
