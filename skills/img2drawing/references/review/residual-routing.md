# Residual routing

Route by **cause**, not by the noun that looks wrong.

A visible mismatch often appears in a small part while the responsible premise lives one or
more relationships upstream. Start with the smallest guide that can genuinely repair the
problem, but escalate immediately when the local part is only a symptom.

Use this question:

`what relationship would have to become true for this residual to disappear?`

Then choose the leaf that owns that relationship.

## Routing rule

1. Name the visible mismatch as a relationship.
2. Ask whether the parent structure is already credible.
3. If yes, use the smallest local leaf that owns the mismatch.
4. If no, route upstream to construction, observation, contour/contact, or environment.
5. After the edit, render and inspect again. A surviving residual may reveal a different
   upstream premise than the first correction assumed.

Do not read every branch below. Use only the branch matching the current residual.

## Foot or shoe looks wrong

```text
foot/shoe residual
├─ hip → knee → ankle axis, stance, or support is wrong
│  └─ construction/balance-and-limbs.md
├─ ground plane, weight-bearing region, or contact is wrong
│  └─ environment/ground-and-context.md
├─ ankle → heel → sole → toe geometry is wrong
│  └─ figure/legs-feet.md
└─ overlap/contact edge is ambiguous or doubled
   └─ description/contour-and-overlap.md
```

A repeated attempt to redraw the shoe without improving the pose is evidence that the
terminal is not the responsible scope.

## Head or face looks wrong

```text
head/face residual
├─ head placement, tilt, or relation to torso is wrong
│  └─ construction/gesture-and-masses.md
├─ visible cranial/jaw shape, feature spacing, or hair mass is locally wrong
│  └─ figure/head-face-hair.md
├─ jaw/hair/neck ownership or reappearance is wrong
│  └─ description/contour-and-overlap.md
└─ the reference boundary/orientation is still uncertain
   └─ observation/visual-observation.md
```

Do not polish eyes or hair strands when the head orientation or cranial-to-jaw proportion is
the actual mismatch.

## Hand or grip looks wrong

```text
hand/grip residual
├─ shoulder → elbow → wrist chain is wrong
│  └─ construction/balance-and-limbs.md
├─ visible palm/finger grouping or wrist-to-hand shape is locally wrong
│  └─ figure/torso-arms-hands.md
├─ prop axis/contact disagrees with the hand or body anchor
│  └─ props/attached-objects.md
└─ foreground/background ownership at the contact is wrong
   └─ description/contour-and-overlap.md
```

Do not invent hidden fingers to make a grip look plausible. If the contact cannot be
explained from visible evidence, return to observation rather than completing it from memory.

## Prop looks wrong

```text
prop residual
├─ dominant axis, thickness, topology, or component break is wrong
│  └─ props/attached-objects.md
├─ hand/body anchors disagree with the prop position
│  └─ construction/balance-and-limbs.md + figure/torso-arms-hands.md
├─ piercing, floating, or occlusion order is wrong
│  └─ description/contour-and-overlap.md
└─ the object's visible boundary is uncertain
   └─ observation/visual-observation.md
```

For a long prop, fix the relation between both ends and their body anchors rather than
nudging one endpoint repeatedly.

## Silhouette or overlap looks wrong

```text
silhouette/overlap residual
├─ one local boundary or reappearance point is wrong
│  └─ description/contour-and-overlap.md
├─ several neighboring boundaries disagree coherently
│  └─ construction/gesture-and-masses.md
├─ a limb/body negative space is wrong
│  └─ construction/balance-and-limbs.md
└─ ownership cannot be read confidently from the reference
   └─ observation/visual-observation.md
```

Multiple local contour failures around the same mass usually indicate that the mass premise
is wrong, not that every contour needs independent cleanup.

## Clothing or folds look wrong

```text
clothing residual
├─ observed anchor, tension, compression, or drape line is locally wrong
│  └─ figure/clothing-folds.md
├─ the body mass or limb beneath the garment is wrong
│  └─ construction/gesture-and-masses.md or construction/balance-and-limbs.md
├─ garment/body/prop overlap ownership is wrong
│  └─ description/contour-and-overlap.md
└─ the issue is value/edge separation rather than geometry
   └─ description/value-edge-and-graphite.md
```

Do not add more folds to hide a wrong torso, arm, or leg premise.

## Grounding or environment looks wrong

```text
ground/context residual
├─ support side, stance, or limb chain does not carry weight
│  └─ construction/balance-and-limbs.md
├─ foot geometry itself is wrong
│  └─ figure/legs-feet.md
├─ ground plane, contact edge, perspective, or contextual placement is wrong
│  └─ environment/ground-and-context.md
└─ foreground/background contact ownership is wrong
   └─ description/contour-and-overlap.md
```

Background detail is never the repair for an unresolved support or contact problem.

## Value or tonal residual

```text
value/tonal residual
├─ form boundary or overlap is actually wrong
│  └─ description/descriptive-geometry.md or description/contour-and-overlap.md
├─ value family, edge behavior, or graphite handling is wrong
│  └─ description/value-edge-and-graphite.md
└─ the value problem comes from a wrong major mass or pose
   └─ construction/gesture-and-masses.md
```

Do not use darker tone to conceal uncertain geometry.

## Escalation signals

Escalate upstream when any of these occur:

- the same local residual survives a deliberate local correction;
- two or more neighboring parts fail in a coherent direction;
- fixing one endpoint breaks the other endpoint of the same relation;
- contact cannot be made credible without moving its parent chain or mass;
- a local contour requires invented geometry to connect cleanly;
- the correction would merely cover the mismatch with texture, tone, or extra strokes.

Escalation is not a stage reset. It is a change of responsible scope inside the same
`observe → draw → inspect → correct` loop.
