# Stroke dynamics

Stroke dynamics are the explicitly authored changes that happen along one mark: pressure, width,
opacity, taper, contact, and related local behavior. They belong below semantic role and tool preset
in the authority hierarchy.

Do not treat dynamics as decoration. They can communicate weight, release, overlap, softness,
acceleration, material contact, and focal hierarchy.

## Authoring order

For a mark whose path is already justified:

1. choose its semantic role;
2. choose the nearest public tool preset;
3. author the local pressure/width/opacity behavior required by the observed or declared relation;
4. render and inspect the actual pixels;
5. retune dynamics without changing geometry when the path is already correct.

## Common dynamics patterns

These are reusable patterns, not fixed curves:

- **light-flat** — low, nearly stable pressure for provisional construction;
- **swell-release** — low to stronger pressure, then a controlled release for gesture/form flow;
- **weighted-contour** — stronger only around the ownership/contact interval that needs emphasis;
- **short-dark-accent** — high local deposition over a short interval, then a clean stop or release;
- **push-flick** — moderate/strong contact followed by rapid pressure collapse for hair-like terminals;
- **broad-contact** — broad diameter with pressure that controls contact/deposition without assuming a
  filled opaque band;
- **hatch-repeat** — repeated related strokes whose small variation still reads as one value family.

## Preserve explicit dynamics in replay

If pressure or another dynamic was explicitly authored, it is part of the drawing decision. A tool
retune or preset revision must not silently regenerate it as though it were derived data.

Preset names explain intent; the resolved tool state and explicit authored dynamics are the replay
authority. Historical output must not change merely because a newer preset definition exists.

## Retune rather than redraw

When geometry is correct but the mark reads wrong because of weight, taper, opacity, pressure, or
material contact, keep the authored points and retune the material through the public runtime.
Do not redraw a different path to compensate for a material defect.
