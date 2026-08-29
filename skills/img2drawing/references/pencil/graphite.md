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
- Calibrate construction/form/accent profiles on the actual output canvas before an
  identity-sensitive pass. A useful starting observation is three distinct pressure
  families (light construction, middle form, selective accent), but the run records the
  chosen values rather than importing numbers from another drawing engine.
- Accent is selective: reserve the darkest/highest-pressure treatment for roughly the
  most informative 15–25% of marks. Broad value bands and blanket confirmation are not
  pencil-line closure.

The distinction that matters is **average weight vs. expressive modulation**: a primary stroke
may be nearly as thick as the centreline while still changing pressure along its length. Do not
flatten per-point pressure into a constant width/darkness.

`render.line_weight.calibrate_line_weight()` is a deterministic mechanical utility for A/B
review. It does not decide geometry and is not an automatic artistic judge.
