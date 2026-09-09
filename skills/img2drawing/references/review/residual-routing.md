# Residual routing

Route by **cause**, not by the noun that looks wrong.

A visible mismatch often appears in a small part while the responsible premise lives one or
more relationships upstream. Start with the smallest guide that can genuinely repair the
problem, but escalate immediately when the local part is only a symptom.

Use this question:

`what relationship would have to become true for this residual to disappear?`

Then choose the leaf that owns that relationship.

## Fast routing kernel

Use this before opening a subject-specific leaf. It is a decision aid inside the existing drawing
loop, not a new stage or runtime state.

```text
fresh inspection + reference / declared intent
                │
                ▼
1. Can the mismatch be read confidently?
   ├─ no  → observation/visual-observation.md
   │        (+ measuring-boundaries.md only for a bounded measurement question)
   └─ yes
        │
        ▼
2. Is the visible part only one symptom of a wider relation?
   ├─ several parts drift together / whole turn or balance is wrong
   │      → construction owner
   ├─ hidden continuity materially controls visible anchors
   │      → foundation/occlusion-inference.md
   ├─ contact / grounding / attached-object relation is wrong
   │      → environment, props, or contour/contact owner
   ├─ geometry is credible and only line/value/material behavior is wrong
   │      → description/value-edge-and-graphite.md or residual-correction.md
   └─ one local visible form is wrong while its parents remain credible
          → smallest local description / subject leaf
                │
                ▼
3. State one responsible relationship before editing.
                │
                ▼
4. Make one coherent correction that can actually falsify that hypothesis.
                │
                ▼
5. Render and inspect fresh evidence.
   ├─ residual materially improved → keep scope; continue only if still highest-impact
   ├─ residual unchanged           → parent premise is suspect; escalate upstream
   ├─ neighboring relations worsen → scope was too local or wrong; revert/re-route
   └─ residual changed class       → route the new residual from the top again
```

Do not descend through every node. The purpose of the kernel is to identify **one responsible
scope** quickly enough that a fresh worker does not polish the visible symptom while the causal
relationship remains wrong.

## Five-way cause test

Classify the residual by its **causal spread**, not its screen location.

| Causal pattern | Primary owner | Typical signal | Do not default to |
| --- | --- | --- | --- |
| Evidence uncertain | `observation/` | you cannot confidently state the visible relation, ownership, turn, or anchor | guessing a geometry fix |
| Global / multi-part | `construction/` | several contours, anchors, negative spaces, or terminals drift coherently | editing each local part independently |
| Hidden-continuity | `foundation/occlusion-inference.md` | a visible downstream anchor depends on a form that disappears behind another | drawing a complete hidden contour or pretending the chain terminates |
| Local geometry / contact | `description/`, `figure/`, `props/`, `environment/` | parents remain credible and one bounded visible relation is wrong | reopening the whole pose without evidence |
| Material only | `description/value-edge-and-graphite.md` + `review/residual-correction.md` | authored points are correct but taper, opacity, weight, tone, or graphite behavior reads wrong | moving correct geometry |

A small-looking residual can still be global. A shoe that is misplaced because the support leg
axis is wrong belongs to construction even if the visible mismatch occupies only a few pixels.
Likewise, a whole drawing can contain a genuinely local residual when all parent relations remain
credible and one overlap edge or feature placement is the only mismatch.

## Parent-credibility test

Before a local correction, test the shortest parent chain that constrains it. Ask:

- If this local part disappeared, would the remaining anchors still imply the correct placement,
  turn, support, depth, and connection?
- Are both endpoints of the relation already credible, or would fixing one require moving the
  other?
- Do neighboring negative spaces and overlaps agree with the same parent premise?
- Can the local correction be made without inventing hidden geometry or distorting a correct
  visible anchor?

If the answer is no, the local leaf is not the owner. Route to the earliest parent relation that
must change. Do not preserve an upstream premise merely because it already has downstream detail.

## One-owner rule

Choose one primary owner for the next mutation. A second leaf may support the diagnosis, but do not
open a cluster of unrelated guides and average their advice.

Before editing, be able to say all three of these in plain language:

1. **Residual:** what visible relationship is wrong?
2. **Owner:** which leaf owns the relationship that must change?
3. **Proof:** what fresh visual evidence would show that this correction worked?

This is not paperwork and does not need a new runtime record. It is a guard against aimless local
polish. If you cannot state the proof condition, the residual is probably not routed precisely
enough yet.

## Retry and escalation rule

A deliberate local correction gets one chance to test its causal hypothesis. After fresh
inspection:

- if the same residual is materially unchanged, **do not repeat the same kind of local edit**;
  escalate to its parent relation;
- make a second correction at the same scope only when fresh evidence supports a genuinely
  different local hypothesis;
- if two neighboring residuals move together, treat them as one coupled upstream problem rather
  than two local tasks;
- if a correction improves the local feature while worsening the whole pose, balance, depth,
  contact, or silhouette, reject the local win and reopen the parent premise.

Repeated search strokes are not additional hypotheses. More marks at the same wrong scope are a
routing failure.

## Routing rule

1. Name the visible mismatch as a relationship.
2. Ask whether the parent structure is already credible.
3. If yes, use the smallest local leaf that owns the mismatch.
4. If no, route upstream to construction, observation, contour/contact, or environment.
5. After the edit, render and inspect again. A surviving residual may reveal a different
   upstream premise than the first correction assumed.

Do not read every branch below. Use only the branch matching the current residual.

## Whole pose feels flatter, more frontal, or more symmetric

Use this branch when several local contours are individually plausible but the subject's turn,
twist, asymmetry, or depth relation has been normalized away.

```text
whole-pose flattening residual
├─ head / ribcage / pelvis turns or relative twist disagree coherently
│  └─ construction/orientation-and-twist.md
├─ shoulder / pelvis relation, support, or several limb anchors drift together
│  └─ construction/gesture-and-masses.md + construction/balance-and-limbs.md
├─ near/far side or plane exposure is still uncertain in the reference
│  └─ observation/visual-observation.md
├─ several negative spaces became generic or symmetric
│  └─ construction/balance-and-limbs.md
└─ prop reads pasted onto the body instead of crossing believable depth
   └─ construction/orientation-and-twist.md + props/attached-objects.md
```

Do **not** polish local contours, folds, eyes, or value until the whole spatial relation is
credible. Clean local geometry is not progress if the drawing has become a more frontal or
symmetrical pose than the subject.

## Occluded relation looks disconnected or ends at the occluder

Use this branch when a form disappears behind another form and the drawing either treats it as if
it structurally terminates there or invents a full hidden contour to force continuity.

```text
occlusion residual
├─ visible entry/reappearance anchors or local directions were read incorrectly
│  └─ observation/visual-observation.md
├─ the hidden interval materially affects pose, topology, contact, depth, or a downstream anchor
│  └─ foundation/occlusion-inference.md
├─ the parent chain/mass/connected-part relation is wrong even before the overlap
│  └─ relevant construction leaf
├─ the structural continuation is plausible but the visible stop/reappearance edge is wrong
│  └─ description/contour-and-overlap.md
├─ a measurement/profile is being treated as if it proves the hidden interval
│  └─ observation/measuring-boundaries.md
└─ hidden appearance is being completed from category knowledge
   └─ foundation/occlusion-inference.md + relevant subject leaf
```

Do not choose between “draw the whole hidden part” and “do not infer anything.” First determine
whether hidden continuity matters structurally. If it does, infer the minimum provisional relation
needed to keep visible anchors coherent, then render only what is actually visible. If only one
side of the occlusion is visible, reduce certainty and leave the exact hidden terminal unspecified.

A hidden hypothesis that requires moving a correct visible anchor, introduces an unsupported sharp
bend, or conflicts with another visible relation is evidence that the parent premise is wrong. Do
not protect the inference by distorting visible geometry.

## Foot or shoe looks wrong

```text
foot/shoe residual
├─ hip → knee → ankle axis, stance, or support is wrong
│  └─ construction/balance-and-limbs.md
├─ strong depth compression/projected chain is wrong
│  └─ construction/foreshortening-and-depth.md
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
├─ head placement or relation to torso is wrong
│  └─ construction/gesture-and-masses.md
├─ head turn, near/far side, or relation to ribcage turn is wrong
│  └─ construction/orientation-and-twist.md
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
├─ shoulder → elbow → wrist chain or reach is wrong
│  └─ construction/balance-and-limbs.md
├─ strong projected compression/depth order is wrong
│  └─ construction/foreshortening-and-depth.md
├─ the grip depends on an occluded hand/prop continuation that was ignored or over-invented
│  └─ foundation/occlusion-inference.md
├─ visible hand envelope, thumb/finger grouping, or local grip geometry is wrong
│  └─ figure/hands-and-grip.md
├─ prop axis/contact disagrees with the hand or body anchor
│  └─ props/attached-objects.md
└─ foreground/background ownership at the contact is wrong
   └─ description/contour-and-overlap.md
```

Do not invent exact hidden fingers to make a grip look plausible. When the visible grip depends on
an occluded hand/contact relation, infer only enough hidden structure to keep the visible wrist,
palm/prop relation, and contact coherent. If the contact cannot be explained even with a plausible
minimal continuation, return to the parent arm/prop relation rather than completing it from
memory. Repeated finger marks on the same mitten-like envelope are a signal to replace the
terminal geometry or escalate upstream.

## Foreshortening or depth compression looks wrong

```text
foreshortening/depth residual
├─ near/far anchors, projected joint spacing, or depth order is wrong
│  └─ construction/foreshortening-and-depth.md
├─ parent mass turn or near/far plane is wrong
│  └─ construction/orientation-and-twist.md
├─ an occluded interval is needed to connect visible depth anchors coherently
│  └─ foundation/occlusion-inference.md
├─ several anchors/overlaps are still uncertain in the reference
│  └─ observation/visual-observation.md
├─ only the local overlap/reappearance edge is wrong after depth is credible
│  └─ description/contour-and-overlap.md
├─ hand terminal projection is locally wrong after the parent chain is credible
│  └─ figure/hands-and-grip.md
├─ foot terminal projection is locally wrong after the parent chain is credible
│  └─ figure/legs-feet.md
└─ prop axis/contact contradicts the figure depth relation
   └─ props/attached-objects.md
```

Do not lengthen compressed segments independently merely because they look anatomically
short. First test whether the projected anchors, parent orientation, overlap, and terminal
orientation are already faithful to the subject. If a segment is occluded, reason through the
minimum hidden continuity needed for those visible anchors; do not render that hidden length as a
visible contour.

## Prop looks wrong

```text
prop residual
├─ dominant axis, thickness, topology, or component break is wrong
│  └─ props/attached-objects.md
├─ body plane / near-far relation makes the prop depth read wrong
│  └─ construction/orientation-and-twist.md
├─ hand/body anchors disagree with the prop position
│  └─ construction/balance-and-limbs.md + figure/hands-and-grip.md
├─ an attachment or connected segment is occluded and the hidden relation matters
│  └─ foundation/occlusion-inference.md
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
├─ the visible fragments require a hidden continuation that was ignored or over-specified
│  └─ foundation/occlusion-inference.md
├─ several neighboring boundaries disagree coherently because a mass is misplaced
│  └─ construction/gesture-and-masses.md
├─ several neighboring boundaries become too frontal/symmetric because turn is wrong
│  └─ construction/orientation-and-twist.md
├─ a limb/body negative space is wrong
│  └─ construction/balance-and-limbs.md
└─ ownership cannot be read confidently from the reference
   └─ observation/visual-observation.md
```

Multiple local contour failures around the same mass usually indicate that the mass premise
is wrong, not that every contour needs independent cleanup. An overlap failure may also belong to
hidden continuity rather than the visible edge itself; separate the two before editing.

## Clothing or folds look wrong

```text
clothing residual
├─ observed anchor, tension, compression, or drape line is locally wrong
│  └─ figure/clothing-folds.md
├─ the body mass or limb beneath the garment is wrong
│  └─ construction/gesture-and-masses.md or construction/balance-and-limbs.md
├─ an occluded garment/body continuation is needed to explain visible drape/contact
│  └─ foundation/occlusion-inference.md
├─ garment symmetry/plane exposure is wrong because the torso turn is wrong
│  └─ construction/orientation-and-twist.md
├─ garment/body/prop overlap ownership is wrong
│  └─ description/contour-and-overlap.md
└─ the issue is value/edge separation rather than geometry
   └─ description/value-edge-and-graphite.md
```

Do not add more folds to hide a wrong torso, arm, leg, turn, or hidden parent relation.

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
├─ major mass turn / twist is too weak to support the tone
│  └─ construction/orientation-and-twist.md
├─ value family, edge behavior, or graphite handling is wrong
│  └─ description/value-edge-and-graphite.md
└─ the value problem comes from a wrong major mass or pose
   └─ construction/gesture-and-masses.md
```

Do not use darker tone to conceal uncertain geometry. In croquis, broad value is not the
repair for unresolved orientation, balance, limb-chain, negative-space, or prop-depth errors.

## Escalation signals

Escalate upstream when any of these occur:

- the same local residual survives a deliberate local correction;
- two or more neighboring parts fail in a coherent direction;
- local parts become cleaner while the whole pose becomes more frontal, parallel, or symmetric;
- fixing one endpoint breaks the other endpoint of the same relation;
- contact cannot be made credible without moving its parent chain or mass;
- a visible downstream anchor drifts because the hidden interval was treated as structural termination;
- a hidden continuation can only be made plausible by moving correct visible anchors or adding an unsupported bend;
- a temporary hidden construction line is being promoted into visible contour without evidence;
- a local contour requires invented visible geometry to connect cleanly;
- the correction would merely cover the mismatch with texture, tone, or extra strokes.

Escalation is not a stage reset. It is a change of responsible scope inside the same
`observe → draw → inspect → correct` loop.
