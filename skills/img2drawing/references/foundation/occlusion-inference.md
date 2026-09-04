# Occlusion inference boundary

**Infer hidden structure when continuity requires it; do not fabricate hidden appearance.**

Occlusion removes visible evidence, not necessarily the need for a structural hypothesis. A form
may disappear behind another form and still determine pose, topology, contact, depth, balance, or
the placement of a visible part on the far side. The Agent may therefore infer a hidden
continuation when that inference is needed to keep the visible drawing coherent.

The critical distinction is between **structure that is inferred for reasoning** and **appearance
that is claimed as visible**.

## Keep three layers separate

### 1. Visible evidence

This is what the reference actually shows. It may include:

- the last visible point before a form enters an occluder;
- the first visible point where it reappears;
- incoming and outgoing direction or tangent;
- visible width, taper, plane exposure, or centerline tendency near the occlusion;
- the foreground edge that owns the overlap;
- visible contact, compression, attachment, or alignment cues;
- neighboring anchors whose positions constrain the hidden relation.

Visible evidence has the strongest authority. Do not move a visible anchor merely to make a
preferred hidden construction look elegant.

### 2. Provisional hidden structure

This is an Agent hypothesis used to preserve continuity. It may include only as much hidden
information as the visible relationships require, for example:

- a likely centerline or connected-part path;
- approximate continuation of width, taper, or mass;
- a joint or chain relation needed to connect visible anchors;
- topology such as “these visible fragments belong to the same part”;
- relative depth and occlusion order;
- a hidden support, attachment, or contact relation when the visible arrangement depends on it.

Treat this layer like any other construction: provisional, revisable, and lower-authority than
visible evidence. Use the simplest continuation that can satisfy all visible anchors and known
structural constraints. Do not add unsupported bends, joints, terminals, or decorative geometry
merely because the subject category suggests them.

### 3. Rendered visible description

The final visible linework should describe the boundaries that are actually visible. A hidden
construction hypothesis does **not** authorize a visible contour through the occluder.

Normally:

```text
visible form → stops at foreground occluder
hidden continuation → may exist as reasoning/construction
visible form → resumes at the observed reappearance point
```

If a temporary construction line through the occluder helps reasoning, keep it clearly
provisional and retire or soften it before it can read as a claimed visible edge. Do not draw an
unobserved seam, fingertip, hair tip, fold path, fastener, surface corner, or hidden terminal as if
it had been seen.

## When hidden inference is required

Infer enough hidden structure when at least one of these is true:

- a connected form disappears and reappears, and both visible fragments must belong to one
  coherent structure;
- the hidden segment materially determines the placement or orientation of a visible downstream
  anchor;
- pose, balance, reach, support, contact, topology, or depth cannot be evaluated without a
  continuation hypothesis;
- two visible endpoints cannot be judged for consistency unless the relation between them is
  considered through the occlusion;
- an attached object or articulated part crosses behind another form and the attachment/depth
  relation would otherwise become arbitrary.

Do **not** infer hidden structure merely to fill empty space or make every object complete. If the
hidden relation has no material effect on visible structure, leaving it unspecified is valid.

## How to infer without overclaiming

Use this procedure when the hidden relation matters:

1. **Mark the visible anchors.** Identify entry, reappearance, nearby joint/attachment/contact, or
   other visible points that constrain the hidden segment.
2. **Read the local approach on both sides.** Compare direction, tangent, width/taper, plane turn,
   and depth order immediately before disappearance and after reappearance.
3. **Form the minimum continuation hypothesis.** Connect the anchors with the fewest structural
   assumptions needed for a coherent part, chain, mass, or topology.
4. **Check the whole relation.** Ask whether the inferred continuation makes the visible pose,
   spacing, overlap, contact, and connected parts more coherent without contradicting any visible
   cue.
5. **Keep uncertainty proportional to evidence.** If only one side is visible, infer only enough
   parent continuity to support what is visible; do not invent an exact hidden endpoint or path.
6. **Revalidate after downstream changes.** If a later visible correction makes the hidden
   continuation implausible, revise or discard the hypothesis rather than bending visible
   geometry to protect it.

Category knowledge may constrain plausibility, but it cannot outrank the reference. Anatomy,
mechanical linkage expectations, garment construction, or object familiarity can suggest a family
of continuations; they do not reveal the exact hidden contour.

## Partial and one-sided occlusion

When a form disappears and **does not reappear**, the evidence is weaker. Do not force a complete
hidden terminal. Infer only what is necessary for the visible parent relation.

Examples of valid limited inference include:

- maintaining the likely direction of an arm behind an object so the visible shoulder and wrist
  relationship remains plausible;
- maintaining a garment or hair mass behind a foreground form without deciding the exact hidden
  edge;
- maintaining a mechanical connection behind a housing without inventing the concealed fastener
  layout.

The absence of a reappearance point is a reason to reduce specificity, not a reason to abandon all
structural inference.

## Hidden contact

A contact may be partly or fully occluded. Distinguish the **existence and role of contact** from
its exact invisible shape.

You may infer that two parts must connect, support, grip, attach, or compress one another when the
visible geometry depends on that relation. Do not invent an exact hidden contact contour, finger
placement, seam path, or attachment detail unless visible evidence supports it.

## Failure signals

Reopen the parent structure instead of polishing locally when:

- the visible fragments on opposite sides of an occluder cannot be connected by one plausible
  continuation without a sharp unsupported bend;
- the inferred hidden path forces a visible anchor away from the reference;
- the drawing treats an occluded chain as if it ends at the occluder, causing downstream pose,
  reach, spacing, or depth to drift;
- a temporary hidden construction line survives into the final drawing and reads as a visible
  boundary;
- hidden appearance keeps becoming more detailed even though the reference provides no new
  evidence;
- different local fixes require mutually incompatible hidden continuations.

In those cases, revisit visible anchors, parent orientation, connected-part relations, and
occlusion order. The repair is not “draw more of the hidden part.”

## Measurement boundary

Measurement tools stop at occlusion. A profile, edge detector, crop, or pixel measurement cannot
measure through an occluder or prove a hidden terminal. This does **not** prohibit Agent inference.
It means the inference must be justified relationally from visible anchors and structural
constraints, and must remain explicitly provisional.

## Output rule

A good observed drawing can reason through an occlusion without drawing through it. Hidden
structure may constrain the visible result while remaining absent from the final visible contour.
That is different from pretending the hidden structure does not exist.