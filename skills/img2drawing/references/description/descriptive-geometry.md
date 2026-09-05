# Descriptive geometry

Descriptive geometry converts observation into a small set of lines that state the real
shape and form.

A descriptive line may carry several facts at once: silhouette, width change, plane turn,
material edge, overlap, contact, topology, or identity. The goal is not more lines; it is more
information per line.

## Select lines by information value

Prefer lines that establish:
- a decisive exterior curvature or corner;
- a thickness or width transition;
- an overlap that establishes depth;
- a form turn that explains volume;
- an identity-bearing feature or asymmetry;
- a seam, fold, joint, boundary, or contact that explains construction or force.

## Preserve complexity

Do not flatten a compound curve into a generic arc because the drawing is sparse. Do not
turn an irregular shoe into a box, a face into icons, or a connected object into generic circles
and rails. Simplify the number of marks while keeping the geometry those marks encode.

## Smoothness must follow observed topology

A smooth spline is not automatically a better line. Use a continuous curve only where the
observed boundary is itself continuous through the interval. Split the authoring interval when the
subject contains a real cusp, corner, tangency break, insertion, component join, folded edge, or
other topology change.

Do not let a curve helper round away a sharp hair terminal, garment break, shoe corner, housing
edge, or equivalent observed event. Conversely, do not approximate a genuinely smooth contour by
a chain of short straight segments merely because those segments are easier to author.

Control points and curve samplers are reasoning/authoring aids. The sampled points that enter the
drawing history are the authored geometry; the helper does not become reference authority.

## Inherit only credible construction

A descriptive pass must not promote a provisional construction primitive into accepted geometry
merely because it already exists. Before refining around an earlier mass, axis, envelope, or
anchor, compare the parent relation against the current authority again.

If the parent structure is wrong, replace it first. Adding a cleaner contour, texture, seam,
value region, or local accent around an incorrect premise makes the error harder to see; it does
not make the premise more accurate.

## Separate geometry correction from material correction

When the path, overlap, and ownership are correct but the rendered line reads broken because of
endpoint taper, width, opacity, pressure, or graphite behavior, preserve the geometry and retune
the stroke material. When the path itself is wrong, replace or locally edit the geometry instead.

Do not resample, simplify, or redraw an already-correct curve merely to change its appearance.
That can silently turn a correct smooth path into a polyline or otherwise introduce a new geometry
error while claiming to make only a rendering correction.

## Stop before noise

When a new line does not introduce a new relationship, it is likely redundant. Retire,
replace, or omit it instead of accumulating search marks.