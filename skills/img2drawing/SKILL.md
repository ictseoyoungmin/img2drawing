---
name: img2drawing
description: Draws inspectable images with explicit strokes through observation, construction, descriptive geometry, residual correction, and replayable output. Croquis reduces mark count without simplifying observed geometry.
---

# img2drawing

## Mission

Draw with explicit, inspectable marks instead of generating a finished image. The Agent is the
semantic and artistic authority. Rendering, measurement, overlays, crops, and other evidence tools
may help the Agent see the current state; they may not decide pose, anatomy, identity, topology, or
artistic correctness.

For observed work, the supplied subject is the geometry authority. For imaginative work, declared
intent is the authority. For hybrid work, preserve and transform only the explicitly declared
constraints. Read
[`references/foundation/reference-authority.md`](references/foundation/reference-authority.md).

## Runtime boundary

The ordinary drawing worker is **runtime-aware and implementation-blind**. When marks are authored
programmatically, use the supported `DrawingSession` public surface from
[`references/api/public-surface.md`](references/api/public-surface.md). Do not replace it with a
hand-written Pillow/OpenCV/SVG/canvas rasterizer and do not inspect private renderer/source internals
as a prerequisite for ordinary drawing. If the documented public surface cannot express a required
mark, report a runtime capability gap rather than silently bypassing the runtime.

## Non-negotiable invariants

1. **Visible reference evidence outranks normalization.** For observed work, do not replace a
   readable projection, asymmetry, pose, hand relation, identity, hairstyle, costume, or terminal
   orientation merely because another solution seems more anatomically plausible, canonical, or
   attractive. Re-observe uncertainty; do not silently normalize it.
2. **Croquis economizes marks, not observed geometry.** Preserve the subject-specific curvature,
   placement, orientation, proportion, envelope, width/depth changes, overlap, contact, negative
   space, and identity-bearing asymmetry that make the subject specific.
3. **Construction is provisional.** Gesture, masses, axes, boxes, circles, and other primitives are
   reasoning aids, not geometry authority. Revalidate parent structure against current evidence
   before inheriting it downstream; replace disproven construction instead of polishing around it.
4. **Infer hidden structure only when continuity requires it; do not fabricate hidden appearance.**
   Use the minimum provisional continuation needed to keep visible anchors coherent through
   occlusion, but do not render unseen contour, digits, folds, terminals, seams, or details as if
   they were observed.
5. **Route residuals by cause, not by noun.** Macro pose, mass, orientation, depth, balance,
   silhouette, overlap, grounding, contact, and object relations outrank micro polish. Repeated
   local repair that leaves the same mismatch visible is a signal to reopen the responsible parent
   premise rather than add more strokes.
6. **Geometry precedes material.** Decide what relationship a mark expresses before choosing its
   line language. Markmaking may clarify correct geometry; it may not hide an incorrect path,
   proportion, overlap, contact, or owner.
7. **Fresh evidence closes decisions.** After meaningful mutations, render and inspect again. Retire
   or soften provisional marks when stronger descriptive geometry has taken over, return to the
   whole drawing after local corrections, and finish only from current evidence.

Canonical definitions live in the reference graph. Root invariants are summaries, not competing
textbooks.

## Instruction graph

`SKILL.md` is the router. Read [`references/INDEX.md`](references/INDEX.md), then open only the
smallest leaves that own the current problem. The graph is not a lifecycle; move backward whenever
fresh evidence disproves a premise.

```text
references/
├─ foundation/    truth, line economy, specificity, occlusion
├─ modes/         user-facing finish modes
├─ observation/   whole↔part reading and measurement boundaries
├─ construction/  gesture, masses, orientation, balance, limbs, depth
├─ description/   contour, geometry, value, edge, material
├─ markmaking/    semantic stroke roles and tool behavior
├─ figure/        head/face/hair, torso/arms, hands/grip, legs/feet, clothing
├─ props/         attached-object geometry and body contact
├─ environment/   grounding and contextual structure
├─ review/        quality gates, residuals, navigation, retirement, completion
├─ output/        render profile, replay, timelapse
└─ api/           public runtime operation only
```

Geometry and markmaking routes may be opened together when needed, but use the specialist leaves
rather than expanding this root into subject-specific policy.

## Conditional start route

For a new task:

1. Establish reference/declaration authority, requested drawing mode, finish intent, and explicit
   style intent. If style is unspecified, use the canonical pencil default rather than inventing a
   decorative style.
2. If final marks will be authored programmatically, read
   [`references/api/public-surface.md`](references/api/public-surface.md) before the first mutation.
3. Read [`references/foundation/line-economy.md`](references/foundation/line-economy.md),
   [`references/foundation/structural-specificity.md`](references/foundation/structural-specificity.md),
   and the smallest matching mode leaf from `references/INDEX.md`.
4. For observed work, read
   [`references/observation/visual-observation.md`](references/observation/visual-observation.md).
   When continuity materially crosses an occluder, also read
   [`references/foundation/occlusion-inference.md`](references/foundation/occlusion-inference.md).
5. **If observed work is intended to become finished or substantially resolved, read
   [`references/review/visual-quality-gates.md`](references/review/visual-quality-gates.md) directly
   before accepting the first descriptive semantic group.** Do not rely on transitive discovery of
   this gate through another leaf.
6. Use `references/INDEX.md` to open only the specialist construction, description, figure, prop,
   environment, or markmaking leaves that own the current relationship. Do not preload every branch.
7. After meaningful mutations, inspect a fresh render and route mismatches through
   [`references/review/residual-correction.md`](references/review/residual-correction.md). When the
   visible part may only be a symptom, use
   [`references/review/residual-routing.md`](references/review/residual-routing.md); when geometry is
   already correct but line language/material is wrong, use
   [`references/review/markmaking-residuals.md`](references/review/markmaking-residuals.md).
8. If a correction must locate an existing authored mark, use the documented navigation route in
   [`references/review/authored-element-navigation.md`](references/review/authored-element-navigation.md)
   rather than parsing session history ad hoc.
9. Finish only from current evidence through
   [`references/review/completion.md`](references/review/completion.md), then export through
   [`references/output/render-profile-and-replay.md`](references/output/render-profile-and-replay.md).

## Canonical drawing loop

```text
observe
→ construct / author the smallest justified semantic group
→ choose mark language only after geometry is justified
→ render
→ gate / inspect current evidence
→ name and route the highest-impact residual
→ correct or retire the responsible marks
→ re-read the whole
→ repeat or finish
```

For observed finished/substantially-resolved work, the gate step uses
`references/review/visual-quality-gates.md`. A semantic group is accepted because current evidence
supports its authority, anchors, owner, geometry claim, and whole-drawing effect—not because a
routine pass completed or because more marks were added.

Fix one to three highest-impact residuals at a time. A useful correction changes the drawing, not
just the paperwork. If a local correction repeatedly fails, reopen the parent relation rather than
stacking additional local strokes.

## Completion and output routing

The matching mode leaf owns mode-specific finish semantics. `references/review/completion.md` owns
the final artistic decision, residual ranking, and accepted-limitation boundary. The runtime may
enforce mechanical provenance preconditions, but those checks do not decide whether the drawing is
good.

Before finish, inspect current pixels, ensure blocking residuals are closed or correctly reopened,
and classify surviving construction/search marks through the retirement route when they damage the
final read. Final PNG, replay, and timelapse must use the persisted render profile; replay is
end-to-end from the initial state through the latest action. Use
[`references/output/render-profile-and-replay.md`](references/output/render-profile-and-replay.md).
