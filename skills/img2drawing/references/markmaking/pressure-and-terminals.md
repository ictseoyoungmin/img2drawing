# Pressure and terminals

Pressure and terminal behavior are separate decisions. A stroke can carry strong pressure through
most of its path and still end with a fast flick, a gentle release, a contact stop, or a dry
residue. Do not encode every terminal as one generic length-proportional fade.

## Geometry and ownership first

Choose terminal behavior only after the visible path and its physical owner are justified.
A terminal mode cannot repair:

- a wrong contour path;
- an accidental hair→arm or garment→background merge;
- an unresolved limb rail;
- an invented hidden tip;
- a prop/body ownership error.

If geometry or ownership is wrong, fix that upstream. Do not use taper/flick/fade to disguise it.

## Terminal intents

Use these semantic terminal modes when the public runtime supports them:

- `contact` — the mark stops while still carrying material contact;
- `gentle` — a controlled soft release over a short physical span;
- `flick` — rapid pressure collapse for hair, whisker, grass, or other fast directional release;
- `residue` — dry graphite trails out with material breakup rather than a clean geometric taper.

The terminal mode does not choose the path or invent a hidden tip. It only changes how an already
justified visible interval deposits material near its end.

A semantic terminal name is a drawing/material decision, **not a renderer-generation boundary**.
Correcting terminal behavior in unreleased development does not, by itself, justify creating a new
renderer family number.

## Physical-span rule

Terminal behavior should be judged in visible physical pixels, not only as a fraction of total
stroke length. Very long strokes should not receive proportionally enormous fades merely because a
single normalized taper parameter is large.

A terminal/material correction should remain spatially bounded to the intended visible interval.
It must not move already-correct authored points merely to obtain a different appearance.

## Thin-flick specialization

A narrow fast flick may need a dedicated terminal behavior so it remains continuous before the
release and sharp at the visible tip. Preserve that specialization when the active style intends
it; do not force a broad-contact model onto every thin stroke.

For hair, do not use flick terminals as a substitute for mass/clump construction. Strand accents
come only after the hair mass and major clumps survive whole-head inspection. See
`../figure/head-face-hair.md`.

## Inspection

When a line appears broken, blunt, swollen, or prematurely pale, first verify that its path and
owner are correct. If they are correct, route the residual here or to `stroke-dynamics.md` and
retune material behavior through the public runtime rather than moving points unnecessarily.

After retuning, inspect the whole semantic group and verify that unrelated stroke-body regions did
not change merely because the terminal/material setting changed. Use
`../review/visual-quality-gates.md` for the surrounding ownership and hierarchy checks.
