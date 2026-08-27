# Graphite

Material simulation should express pressure and contact without changing the intended geometry.

## Stroke weight / line hierarchy calibration

When the dominant gesture is readable but every other structural line is too faint, do **not**
keep a "dark centreline + ghost construction" hierarchy by default.

Preferred P1→P3 hierarchy:
- the dominant gesture remains the reference stroke;
- primary axes and primary mass contours may approach roughly the same *average* width;
- their pressure/opacity may stay slightly lower than the gesture;
- cross-contours and minor construction stay subordinate;
- within-stroke pressure variation, taper and graphite dynamics are preserved.

The distinction that matters is **average weight vs. expressive modulation**: a primary stroke
may be nearly as thick as the centreline while still changing pressure along its length. Do not
flatten per-point pressure into a constant width/darkness.

`render.line_weight.calibrate_line_weight()` is a deterministic mechanical utility for A/B
review. It does not decide geometry and is not an automatic artistic judge.

## Point spacing: round the curve without shaking the line

A stroke is a polyline, so a curve stated with a handful of control points renders with
visible corners. **Author the point list at the spacing the curve needs before it reaches
`draw`/`replace_stroke`** — the runtime records exactly the points it is given and never
resamples or rewrites them, so getting the spacing right is the Agent's job, not something
to fix downstream.

The renderer applies hand jitter **per point**. Resample a stroke to a very small spacing
and that gentle tremor fires ten times as often, turning into high-frequency wobble: the
line stops looking drawn and starts looking noisy, and its edges lose their crispness.

There is a working band, not a "smaller is better" rule:

| spacing | result |
|---|---|
| too coarse | visible corners; the curve reads as a polygon |
| the band | round curve, clean edge |
| too fine | round curve, but the line wobbles and softens |

On a ~512px canvas that band sits around **8px**. Scale it with the canvas rather than
copying the number. Judge it on the **raw render at zoom**, on both a long line and a small closed shape — the
two fail in opposite directions. A one-off resample (e.g. Catmull-Rom over a set of
observed anchor points) is a legitimate way to *generate* that point list before drawing;
what must not happen is resampling silently inside the drawing call itself, where the
recorded provenance would then describe points the Agent never actually placed.
