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
3. **There is no generic “detail stage.”** Descriptive lines are added when a specific
   relationship requires them. A face, shoe, cuff, rifle, or fold can become the next
   highest-impact problem at any time.
4. **Construction is a hypothesis, not a license to symbolize.** Gesture and masses must
   explain the subject; they must not replace it with tubes, circles, beans, boxes, or
   generic anatomy.
5. **Do not invent hidden endings.** Occluded hands, feet, hair tips, garment edges, and
   object contacts end where the evidence ends.
6. **Macro residuals outrank micro polish.** Pose, mass, orientation, balance, silhouette,
   overlap, grounding, and major object relations are repaired before small accents.
7. **Line accumulation is not fidelity.** When many simple strokes pile up around one
   feature, replace them with fewer lines that describe the correct boundary or form.
8. **Do not finish a flat pose with tone.** Broad value, dense hatch, texture, or detail may
   reinforce structure only after the major spatial relations already read without them.

## Instruction graph

`SKILL.md` is the router. Read `references/INDEX.md`, then load only the smallest relevant
leaves:

```text
SKILL.md
└─ references/
   ├─ foundation/   truth, precedence, line economy
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
2. Read `foundation/line-economy.md` and the chosen mode guide.
3. For observed work, read `observation/visual-observation.md`. Use
   `observation/measuring-boundaries.md` only when measurements or ambiguous boundaries are
   actually needed.
4. For figures, form one whole-subject spatial hypothesis using the construction leaves. Read
   `construction/orientation-and-twist.md` whenever turn, near/far relation, or counter-rotation
   materially defines the pose.
5. Before local description, confirm that the structural read is credible without relying on
   tone. If not, stay in observation/construction rather than polishing local contours.
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

## Whole-subject construction

For an observed figure, establish one coherent hypothesis covering:

- dominant flow / line of action;
- head, ribcage, and pelvis placement, orientation, and relative turn;
- shoulder and pelvis relationship, including near/far side and counter-rotation;
- support side, plumb, ground, and balance;
- major limb chains and negative spaces;
- prop axis, body contact, and occlusion when a prop is present.

Construction marks may be sparse, but the represented relationships may not be vague. A
short line can encode an exact joint direction; a mass can preserve a specific tilt and
width change. Do not spend the quality budget on facial accents or wrinkle noise while the
whole pose still reads incorrectly.

## Structural read before description

For observed figures, a rough silhouette is not enough to justify contour refinement or value.
Before spending marks on local identity, clothing detail, or broad tone, inspect whether the
current drawing already communicates:

- head / ribcage / pelvis orientation and relative twist;
- shoulder / pelvis relation;
- support and weight tendency;
- major shoulder → elbow → wrist and hip → knee → ankle anchor chains;
- stance and large negative spaces;
- major prop axis and body overlap when present.

This is **not** a stage gate. It is a reversible drawing decision. Any later observation may
invalidate one of these relations, in which case retire or replace the responsible marks and
reconstruct before continuing downstream.

A warning sign is a drawing whose local parts look clean while the whole becomes more frontal,
parallel, or symmetric than the subject. Route that failure to
`construction/orientation-and-twist.md` and `review/residual-routing.md` rather than polishing it.

## Descriptive geometry, not symbolic detail

Descriptive drawing means selecting lines that explain real observed form. A good sparse
line set usually prioritizes:

- silhouette turns and width changes;
- overlap boundaries and contact handoffs;
- form turns or plane breaks that clarify volume;
- identity-bearing feature placement;
- garment seams and folds that arise from visible tension, compression, or contact;
- foot/ground and object/body contact.

Do not substitute generic symbols for these relationships. In particular:

- a head is not a circle with facial ticks;
- hair is not a stack of parallel strands;
- a hand is not a mitten with finger ticks;
- a leg is not a pair of rails;
- a foot or shoe is not a rectangular block;
- clothing is not a field of decorative zigzags;
- extra strokes around an uncertain form do not make the form more accurate.

Read the matching `description/` and `figure/` leaves when one of these becomes limiting.

## Head and face policy

When the head is visible enough to matter, preserve its cranial-to-jaw silhouette, face
orientation, feature spacing, hair mass, and the few internal turns that make the subject
recognizable. Spend lines on informative boundaries, not repeated search marks. A few
accurate exterior and interior lines are preferred over many simplified ones. See
`figure/head-face-hair.md`.

## Hands and grip policy

When a visible hand matters, preserve wrist entry, hand orientation, palm/hand envelope,
thumb opposition, informative finger groups, visible gaps/terminations, and actual contact.
Do not convert the terminal into a mitten and then add finger ticks, and do not invent hidden
digits to complete a grip. If the parent arm or prop relation is wrong, route upstream rather
than deforming the hand to compensate. See `figure/hands-and-grip.md`.

## Foreshortening and depth policy

When a form points toward or away from the viewer, preserve projected joint spacing,
near/far order, overlap, supported apparent-width change, and terminal orientation. Do not
unfold a foreshortened limb to the anatomical length you expect, or draw hidden length through
an occluder. See `construction/foreshortening-and-depth.md`.

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
solution. A luminance edge is not automatically an anatomical edge, and a measurement
cannot infer an occluded terminal.

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
