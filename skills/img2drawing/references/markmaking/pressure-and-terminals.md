# Pressure and terminals

Pressure and terminal behavior are separate decisions. A stroke can carry strong pressure through
most of its path and still end with a fast flick, a gentle release, a contact stop, or a dry
residue. Do not encode every terminal as one generic length-proportional fade.

## Terminal intents

Use these semantic terminal modes when the public runtime supports them:

- `contact` — the mark stops while still carrying material contact;
- `gentle` — a controlled soft release over a short physical span;
- `flick` — rapid pressure collapse for hair, whisker, grass, or other fast directional release;
- `residue` — dry graphite trails out with material breakup rather than a clean geometric taper.

The terminal mode does not choose the path or invent a hidden tip. It only changes how an already
justified visible interval deposits material near its end.

## Physical-span rule

Terminal behavior should be judged in visible physical pixels, not only as a fraction of total
stroke length. Very long strokes should not receive proportionally enormous fades merely because a
single normalized taper parameter is large.

## Thin-flick specialization

A narrow fast flick may need a dedicated terminal behavior so it remains continuous before the
release and sharp at the visible tip. Preserve that specialization when the active style intends
it; do not force a broad-contact model onto every thin stroke.

## Inspection

When a line appears broken, blunt, swollen, or prematurely pale, first verify that its path is
correct. If the geometry is correct, route the residual here or to `stroke-dynamics.md` and retune
material behavior through the public runtime rather than moving points unnecessarily.
