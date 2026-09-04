---
name: img2drawing
description: Draws inspectable images with explicit strokes through observation, construction, descriptive geometry, residual correction, and replayable output. Croquis reduces mark count without simplifying observed geometry.
---

# img2drawing

## Mission

Draw with explicit, inspectable marks instead of generating a finished image. The Agent is
the semantic and artistic authority. Rendering, measurement, overlays, crops, and other
evidence tools may help the Agent see the current state; they may not decide pose,
anatomy, identity, topology, or artistic correctness.

For observed work, the subject is the geometry truth. For imaginative work, declared
intent is the truth. For hybrid work, preserve and transform only the explicitly declared
constraints. Read [`references/foundation/reference-authority.md`](references/foundation/reference-authority.md).

## Non-negotiable drawing principles

1. **Croquis economizes marks, not observed geometry.** Fewer lines mean fewer redundant
   decisions, not a simpler head, flatter face, straighter leg, boxier foot, or invented
   fold pattern.
2. **Preserve shape while reducing line count.** Keep the observed curvature, width
   changes, overlap, negative space, contact, fold origin, and identity-bearing asymmetry.
3. **Defer secondary detail, not structural specificity.** Early work may omit texture,
   decoration, repeated small features, or other low-impact local information, but it must
   already preserve the subject's specific placement, orientation, proportion, envelope,
   width/depth changes, major overlap/contact/negative space, and connected-part relations.
4. **Construction is provisional, not geometry authority.** Gesture, masses, axes, boxes,
   circles, or other primitives are reasoning aids. A mark does not earn preservation merely
   because it was drawn earlier or because later marks depend on it.
5. **Do not inherit unverified structure.** Before a new descriptive pass builds on existing
   construction, compare the whole drawing against its authority again. If the parent relation
   is wrong, replace the responsible geometry instead of refining around it.
6. **There is no generic “detail stage.”** Descriptive lines are added when a specific
   relationship requires them. A face, shoe, cuff, rifle, fold, joint, seam, or component can
   become the next highest-impact problem at any time.
7. **Infer hidden structure when continuity requires it; do not fabricate hidden appearance.**
   Occlusion does not erase the need to reason about a connected chain, mass, topology, contact,
   or depth relation. Build the minimum provisional continuation needed to keep visible anchors
   coherent, but do not render an unobserved contour, terminal, fold, seam, finger, fastener, or
   surface detail as if it were visible.
8. **Macro residuals outrank micro polish.** Pose, mass, orientation, balance, silhouette,
   overlap, grounding, and major object relations are repaired before small accents.
9. **Line accumulation is not fidelity.** When many simple strokes pile up around one
   feature, replace them with fewer lines that describe the correct boundary or form.
10. **Do not finish weak structure with tone.** Broad value, dense hatch, texture, or detail
    may reinforce structure only after the major spatial relations already read without them.

Read [`references/foundation/structural-specificity.md`](references/foundation/structural-specificity.md)
for the cross-subject rule that separates secondary detail from structural information and
requires revalidation before inherited construction is refined. Read
[`references/foundation/occlusion-inference.md`](references/foundation/occlusion-inference.md)
when a visible relation crosses behind another form or an occluded continuation materially affects
pose, topology, contact, depth, or a downstream anchor.

## Instruction graph

`SKILL.md` is the router. Read `references/INDEX.md`, then load only the smallest relevant
leaves:

```text
SKILL.md
└─ references/
   ├─ foundation/   truth, precedence, line economy, structural specificity, occlusion inference
   ├─ modes/        croquis, figure, line, tonal, free draw
   ├─ observation/  whole/part reading and measurement boundaries
   ├─ construction/ gesture, masses, orientation/twist, balance, limbs, foreshortening/depth
   ├─ description/  contour, descriptive geometry, value/edge/material
   ├─ figure/       head/face/hair, torso/arms, hands/grip, legs/feet, clothing folds
   ├─ props/        attached-object geometry and body contact
   ├─ environment/  ground and contextual structure
   ├─ review/       residual correction/routing, retirement, completion
   ├─ output/       canonical render and replay
   └─ api/          public runtime surface only
```

This taxonomy is not a lifecycle. Move backward whenever observation disproves the current
premise, and skip leaves that do not own the current problem.

## Start route

For every new task:

1. Establish reference authority and requested drawing mode.
2. Read `foundation/line-economy.md`, `foundation/structural-specificity.md`, and the chosen
   mode guide.
3. For observed work, read `observation/visual-observation.md`. If a material relation disappears
   behind another form, read `foundation/occlusion-inference.md` before deciding that the hidden
   structure simply ends. Use `observation/measuring-boundaries.md` only when measurements or
   ambiguous boundaries are actually needed.
4. Form one whole-subject structural hypothesis before spending marks on local description.
   Preserve the specific placement, orientation, proportion, envelope, width/depth changes,
   overlaps, contacts, negative spaces, and connected-part or anchor relations that materially
   define the subject. When continuity passes behind an occluder, infer only the hidden relation
   needed to keep the visible anchors coherent. Load specialized construction leaves only when
   those relationships need them.
5. Before local description, re-read the whole drawing against its authority. Existing
   construction, including hidden-continuation hypotheses, may be retained only when the parent
   structure is still credible without relying on detail or tone. If not, replace the responsible
   geometry first.
6. Route each remaining mismatch to the smallest descriptive or subject-specific leaf that
   owns its cause. If the visible part may only be a symptom, use
   `review/residual-routing.md` to choose the local or upstream premise instead of opening
   every leaf.
7. After every meaningful mutation, inspect a fresh render and use
   `review/residual-correction.md`.
8. Finish only from current evidence, then export through the output route.
9. Read `api/public-surface.md` only when code must call the runtime.

## Canonical drawing loop

`observe → construct → render → inspect → select residual → correct → render again`

Continue the same loop while description and finish marks are added. Do not stop merely
because a routine pass completed, and do not ask for permission after each pass when the
requested target is already clear.

A useful correction changes the drawing, not the paperwork. Fix one to three highest-impact
problems at a time. When a local cleanup would hide a larger structural error, revise the
structural premise instead. Repeated failure of the same local correction is a routing
signal to inspect the parent relation, not a reason to add more local strokes.

## Whole-subject structural hypothesis

For observed work, establish one coherent hypothesis covering the high-impact relationships that
make this subject specific rather than generic:

- placement and occupied extent of the major forms or parts;
- dominant flow, principal direction, or organizing axes when present;
- major orientation, turn, and relative spatial relation;
- proportion, spacing, characteristic envelope, and width/depth changes;
- support, balance, grounding, or load path when they materially define the subject;
- connected-part or anchor relations, including hidden continuity when an occlusion separates
  visible fragments of the same structure;
- large negative spaces, overlaps, contacts, and occlusion order;
- attached-object relations when present.

Construction marks may be sparse, but the represented relationships may not be vague. A short
line can encode an exact direction; a simple mass can preserve a specific orientation and width
change. Do not replace observed structure with a generic primitive merely because local detail is
being deferred.

For figures, the same rule includes head/ribcage/pelvis placement and turn, shoulder/pelvis
relation, support, limb chains, stance, and prop/body overlap. For articulated objects or
mechanisms, the same rule applies to major axes, joint or part envelopes, relative widths,
connections, and overlaps. These are examples of the same invariant, not separate workflows.

## Structural read before description

A rough silhouette or simple construction is not enough to justify contour refinement, local
identity, or value. Before spending marks downstream, inspect whether the current drawing already
communicates the structural relations that materially define the subject:

- placement, occupied extent, and relative proportion;
- major orientation / turn / principal axes;
- characteristic envelope and width/depth changes;
- major connected-part or anchor relations, including plausible continuity through important
  occlusions when the visible arrangement depends on it;
- overlap, contact, negative space, and occlusion order;
- support or grounding when applicable.

This is **not** a stage gate. It is a reversible drawing decision. Any later observation may
invalidate one of these relations, in which case retire or replace the responsible marks and
reconstruct before continuing downstream.

A warning sign is a drawing whose local parts become cleaner or more detailed while the whole
subject becomes more generic, flatter, more symmetric, more parallel, or otherwise less faithful
to its authority. Another warning sign is a connected form that is treated as if it terminates at
an occluder even though its visible downstream anchor requires continuity. Route those failures
upstream rather than polishing them.

## Revalidate before inheriting construction

Earlier construction is not a source of truth. Before each meaningful descriptive pass, compare
the whole drawing against the reference authority or declared intent again.

```text
previous construction
→ fresh whole-subject comparison
→ parent structure still credible?
   ├─ yes → retain and describe further
   └─ no  → replace responsible geometry first
```

Do not preserve a wrong primitive because later strokes were placed relative to it. The cost of
replacing an upstream premise is lower than carrying its error through every downstream contour,
detail, value region, or accent.

## Occlusion inference boundary

Do not use “not visible” as a synonym for “structurally irrelevant.” When a connected form,
articulated chain, garment mass, hair mass, attached object, or contact relation passes behind an
occluder, separate three questions:

1. **What is visible?** Locate the last visible anchor before disappearance, the first visible
   reappearance when one exists, local direction/tangent, width/taper, foreground ownership, and
   any visible contact or alignment cues.
2. **What hidden relation is needed?** Infer the minimum centerline, connected-part path, mass
   continuation, topology, relative depth, or attachment/contact relation needed to make those
   visible anchors coherent. This is provisional construction, not observed appearance.
3. **What should be rendered?** Final descriptive linework normally stops at the foreground
   occluder and resumes only where the background form is actually visible again. The inferred
   hidden path may constrain placement without appearing as a visible contour.

If both sides are visible, use them together: a hidden continuation that cannot connect the entry
and reappearance anchors without an unsupported bend is evidence that the parent premise needs
revision. If only one side is visible, reduce certainty: infer only enough continuation to support
the visible parent relation and leave the exact hidden terminal unspecified.

A temporary construction line may pass through an occluder when it materially helps reasoning,
but it must remain recognizably provisional and should be retired or softened before it reads as a
claimed visible edge. Never promote category knowledge into exact hidden appearance: anatomy,
mechanics, garment construction, or object familiarity may constrain plausibility but cannot reveal
an unseen fingertip, fold path, seam, fastener, hair tip, surface corner, or terminal.

Read `foundation/occlusion-inference.md` for the full decision procedure and failure signals.

## Descriptive geometry, not symbolic detail

Descriptive drawing means selecting lines that explain real observed form. A good sparse
line set usually prioritizes:

- silhouette turns and width changes;
- overlap boundaries and contact handoffs;
- form turns or plane breaks that clarify volume;
- identity-bearing feature placement;
- seams, folds, joints, or component boundaries that explain construction or force;
- ground/contact and object/body or part/part relations.

Do not substitute generic symbols for these relationships. In particular:

- a head is not a circle with facial ticks;
- hair is not a stack of parallel strands;
- a hand is not a mitten with finger ticks;
- a leg is not a pair of rails;
- a foot or shoe is not a rectangular block;
- clothing is not a field of decorative zigzags;
- a joint, housing, or connected part is not automatically a generic circle or box;
- extra strokes around an uncertain form do not make the form more accurate.

Read the matching `description/` and subject leaves when one of these becomes limiting.

## Head and face policy

When the head is visible enough to matter, preserve its cranial-to-jaw silhouette, face
orientation, feature spacing, hair mass, and the few internal turns that make the subject
recognizable. Spend lines on informative boundaries, not repeated search marks. A few
accurate exterior and interior lines are preferred over many simplified ones. See
`figure/head-face-hair.md`.

## Hands and grip policy

When a visible hand matters, preserve wrist entry, hand orientation, palm/hand envelope,
thumb opposition, informative finger groups, visible gaps/terminations, and actual contact.
Do not convert the terminal into a mitten and then add finger ticks. When digits or part of the
hand are occluded, infer only the hidden hand/contact relation needed to make the visible grip
coherent; do not invent exact hidden digits or render them as observed. If the parent arm or prop
relation is wrong, route upstream rather than deforming the hand to compensate. See
`figure/hands-and-grip.md`.

## Foreshortening and depth policy

When a form points toward or away from the viewer, preserve projected joint spacing,
near/far order, overlap, supported apparent-width change, and terminal orientation. Do not
unfold a foreshortened limb to the anatomical length you expect. If part of the chain is occluded,
infer the minimum hidden continuity needed to connect visible anchors, but do not draw the hidden
contour through the occluder as if it were visible. See
`construction/foreshortening-and-depth.md`.

## Legs and feet policy

Preserve thigh/calf width changes, knee transition, ankle direction, foot orientation,
heel/toe/sole relationships, footwear structure, stance spacing, and ground contact. Do
not hide an incorrect lower body behind a generic tapered tube or box foot. See
`figure/legs-feet.md`.

## Clothing-fold policy

Folds must originate at observed anchors, tension, compression, drape, or contact. Keep
their exact location and direction even when only a few are drawn. Remove decorative fold
noise that does not explain form. See `figure/clothing-folds.md`.

## Croquis value boundary

In croquis, broad value regions and dense regular hatch fields are off by default. Use them
only when the request explicitly calls for shaded/tonal croquis or the declared intent materially
depends on form/light, and only after the structural read above remains credible without tone.
A small local value accent may clarify an observed relation; value must not manufacture missing
turn, overlap, or mass.

## Evidence boundary

Whole views, focused crops, overlays, grids, plumb lines, material samples, and profiles are
observation aids. They answer bounded visual questions; they do not select the drawing
solution. A luminance edge is not automatically an anatomical edge. A measurement cannot pass
through an occluder or prove an exact hidden terminal; the Agent may still infer a provisional
hidden relation from visible anchors when continuity, topology, contact, pose, or depth requires
it. Keep that inference distinct from measured evidence and from rendered visible appearance.

After any mutation, old visual evidence may no longer describe the current drawing. Render
and inspect again before accepting the correction.

## Stroke retirement

When a stronger contour, overlap, or descriptive line takes over a construction cue,
reduce or remove the obsolete cue instead of stacking another line on top. Preserve a faint
construction line only when it still contributes rhythm, weight, or an intentional
handoff. All edits remain history-safe. See `review/stroke-retirement.md`.

## Runtime boundary

`DrawingSession` is the canonical public orchestration surface for new work. Drawing
knowledge belongs in this instruction graph; runtime implementation belongs in `src/`.
Do not read implementation details to decide what the subject should look like, and do not
copy implementation code into drawing guides. Skill-facing API guidance names only the
supported public surface; see `api/public-surface.md`.

## Completion

Finish only after a fresh current-state inspection and after every material residual is
either resolved or explicitly accepted as a limitation. The final drawing must satisfy the
requested mode and finish intent without relying on hidden construction notes or a checklist
to excuse visible errors. See `review/completion.md`.

Final PNG, replay, and timelapse must use the same persisted render profile. Replay must be
end-to-end from the initial state through the latest action. See
`output/render-profile-and-replay.md`.
