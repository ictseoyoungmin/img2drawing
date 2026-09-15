# Visual quality gates

Use these gates for observed drawings that are expected to read as a finished or substantially resolved image.

These are **reversible evidence gates**, not lifecycle stages. Passing a gate never makes earlier geometry immutable. Fresh observation may reopen any parent premise.

The purpose is to convert existing drawing principles into decisions the worker must actually demonstrate before a semantic group is accepted.

## Semantic-group evidence packet

Before accepting a connected group of marks, state the smallest useful packet:

1. **Visible authority** — what reference evidence supports this group?
2. **Anchors** — which 2–5 neighboring landmarks constrain placement, scale, direction, or contact?
3. **Owner** — what physical boundary/form/relation owns each surviving line?
4. **Geometry claim** — what curvature, taper, overlap, width/depth change, contact, or topology is being asserted?
5. **Mark language** — why does this role/weight/terminal/material express the geometry without hiding it?
6. **Disproof test** — what fresh visual evidence would make this group wrong enough to replace or reopen?

Do not turn this into paperwork. One compact observation can answer several fields. The packet exists to stop category-recognition and convenient shorthand from becoming accepted geometry without comparison.

## Reference-fidelity / anti-normalization gate

The canonical authority rule lives in `../foundation/reference-authority.md`. This gate owns only
the acceptance test.

Before accepting a correction, compare it to the supplied authority. If it is cleaner, more
conventional, more symmetric, or more familiar **but less faithful to the readable reference**,
classify it as **authority drift** and reject/reopen it. Handedness, terminal orientation, feature
spacing, identity-bearing shape, hairstyle, costume/accessory design, pose, silhouette, and strong
foreshortening are common places to check.

When the evidence is genuinely ambiguous, reopen observation through
`../observation/visual-observation.md` rather than accepting a confident template substitution. If
a higher-priority constraint prevents faithful preservation, surface the limitation instead of
silently substituting another result.

## Line ownership gate

Every surviving final stroke needs one primary owner, for example:

- silhouette boundary;
- overlap/occlusion boundary;
- form turn or plane break;
- seam/component boundary;
- hair-mass or clump boundary;
- identity-bearing feature;
- structural contact;
- value/hatch family;
- environment plane or visible edge.

One stroke may carry several facts only when those facts belong to the **same continuous physical relation**.

Do not continue one convenience stroke across an ownership change such as hair → arm, jaw → collar, garment → background, prop → body contour, or one component → another. Split the authoring interval at the ownership handoff even if the screen-space tangent happens to align.

An unowned final mark is either provisional/search information that should be retired or decoration that should not have been authored.

## Anti-symbol gate

Ask whether the smallest surviving line set preserves the instance-specific geometry rather than merely naming the category.

Reject these as finished shorthand when the reference supports more information:

- head = circle plus facial ticks;
- hair = parallel strand field;
- arm/leg = parallel rail pair or uniform tube;
- hand = mitten plus finger ticks;
- foot/shoe = rectangle, wedge, or rounded block without its observed orientation/construction;
- rifle/prop = rails plus generic circles/rectangles without thickness/contact/topology;
- clothing = outline plus decorative zigzag/hatch noise;
- environment = arbitrary perspective rays without a visible/intended plane or edge owner.

Recognition is not sufficient. Preserve the curvature, taper, orientation, overlap, contact, asymmetry, and width/depth relations that distinguish this subject from a generic symbol.

## Perspective-propagation gate

When the camera/view is strongly foreshortened, identify coarse depth groups before local finish:

```text
near
mid
far
```

For each important connected chain, verify where evidence allows:

- projected spacing;
- apparent width change;
- overlap order;
- near/far exposure;
- terminal orientation;
- continuity through occlusion.

A convincing enlarged near head does not prove the whole perspective solution. If torso, pelvis, limbs, or props remain flat/diagrammatic, reopen the parent depth hypothesis.

## Hair gate

Use the order:

```text
head + hair outer mass
→ major parting / clump boundaries
→ whole-head inspection
→ selected strand accents
```

Do not use repeated strand lines to carry an unresolved silhouette, jaw/neck handoff, parting, or clump overlap. If removing the strand accents destroys the hair read, the mass/clump solution is not finished.

## Limb gate

Two side lines connecting joint A to joint B do not close a limb.

Where visible evidence allows, at least one instance-specific relation must read:

- taper/width change;
- near/far edge asymmetry;
- joint insertion or overlap;
- bend/rotation cue;
- foreshortened spacing;
- garment compression/tension that explains the underlying form;
- terminal orientation/contact.

This applies to bare limbs, sleeves, trouser legs, and similar articulated chains.

## Prop/body gate

Solve an attached/held object and its body relation together. Verify:

- principal axis and thickness;
- major component/topology breaks;
- attachment/grip/strap/support contacts;
- front/behind ownership;
- negative spaces;
- continuation through occlusion;
- scale against neighboring body anchors.

Do not finish the prop independently and place it beside the body afterward.

## Hierarchy gate

Use at least three semantic dominance levels conceptually:

```text
primary   decisive silhouette / overlap / focal identity
secondary internal form / seam / clump / prop structure
tertiary  intentional construction remnant / hatch / context accent
```

The exact numeric pressure is style-dependent. The requirement is perceptual: at final output scale, these roles must actually read with different priority. If they do not, retune or retire marks instead of trusting nominal tool names.

## Retirement gate

Before calling a drawing clean/final, classify each surviving provisional mark:

- **KEEP** — it contributes unique information intentionally visible in the requested finish;
- **SOFTEN** — it remains useful but must stay subordinate;
- **RETIRE** — stronger description already carries its information, or the mark is contradicted/redundant/noisy.

Default to **RETIRE after replacement**. A large field of faint construction/search marks is still visual clutter even if no individual mark is dark.

Read `stroke-retirement.md` for the edit behavior.

## Hatch/context ownership gate

Hatching must serve at least one causal relation:

- value family;
- plane turn;
- material direction;
- fold tension/compression;
- cast/contact shadow;
- explicit requested style.

Environment lines likewise need an owned visible/intended plane, edge, contact, or scale/depth relation. Do not add generic perspective rays merely to make an image look more complete.

## Whole-read return gate

After every accepted local semantic group, inspect the fresh whole drawing and answer:

- Did the whole become more specific or merely busier?
- Did pose, silhouette, depth, balance, scale, or identity drift?
- Did a new tangent, accidental merge, or ownership conflict appear?
- Is the next highest-impact residual genuinely local?

If the drawing became more generic, flatter, more parallel, or more symmetric, reopen the parent premise immediately.

If a correction passed local plausibility but failed the reference-fidelity gate, treat that as
authority drift rather than progress.

## Finish gate

Before final finish, name the three largest remaining visible mismatches, or explicitly state that fewer than three remain.

For each remaining mismatch record:

```text
owner
blocking? yes/no
why it remains
why it is acceptable if non-blocking
```

For `finish_intent="subject"`, explicitly account for:

- whole pose/composition/depth;
- face/head/hair;
- hands/feet;
- clothing;
- prop/body relations when present;
- grounding/context when present;
- line hierarchy;
- construction retirement;
- reference-fidelity / anti-normalization.

A recognizable subject with unresolved generic rails, symbolic terminals, ownerless lines, dominant search construction, or silent identity/anatomy normalization is not finished merely because all categories can be named.

## Relationship to runtime checks

Runtime freshness/provenance checks are mechanical. They do not decide any gate above. The Agent must actually inspect the current render and make the visual decision.
