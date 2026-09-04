# Measuring boundaries

Measure only when the question can be answered by the measurement.

Before trusting an edge, ask:

1. What does this line separate? Name both sides.
2. Can the chosen measurement actually distinguish those materials or values?
3. Is the apparent ending observed, or inferred from category knowledge?
4. If the form is occluded, am I measuring a visible anchor or pretending to measure the hidden interval?

A luminance transition is not automatically a body contour. Dark clothing, hair, skin,
shadow, and background may produce misleading profiles. Use material/context reading to
interpret measurements rather than treating them as semantic detectors.

Useful bounded checks include angle, relative distance, plumb, ground relation, sampled
value, and a focused horizontal/vertical profile. Use them to test an Agent hypothesis,
not to manufacture one.

## Occlusion boundary

Occlusion is a hard boundary for **measurement**, not for all structural reasoning.

When evidence disappears behind another form:

- do not extend a profile, edge detector, ruler, or pixel measurement through the occluder;
- do not report an exact hidden endpoint, contour, joint position, seam, or contact point as a
  measured fact;
- do preserve the visible entry anchor and reappearance anchor when one exists;
- do compare the visible directions, widths/tapers, depths, and neighboring anchors on both sides;
- do allow the Agent to form a provisional hidden-continuity hypothesis when pose, topology,
  contact, depth, or a downstream visible anchor depends on it.

The inference must come from relationships among visible evidence and structural constraints, not
from a measurement that never observed the hidden region. Keep the statements separate:

```text
measured/observed:  visible entry + visible reappearance + visible local relations
inferred:           minimum hidden continuation needed to make them coherent
not justified:      exact hidden appearance merely supplied by category knowledge
```

When only one side of the occlusion is visible, measurement can constrain that visible side only.
The Agent may still infer enough parent continuity to keep the visible structure plausible, but the
exact hidden terminal should remain unspecified unless additional evidence supports it.

See `../foundation/occlusion-inference.md` for the full inference/rendering boundary.
