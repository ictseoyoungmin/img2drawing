# Instruction graph index

This directory is a routing graph, not a sequential course and not a runtime lifecycle.
Start at `SKILL.md`, then read only the smallest leaves that own the current drawing problem.

## 1. Foundation

- `foundation/line-economy.md` — preserve geometry while reducing redundant marks; group related marks by one coherent relation
- `foundation/structural-specificity.md` — defer secondary detail without genericizing structure; revalidate inherited construction
- `foundation/occlusion-inference.md` — infer hidden continuity when needed while keeping inferred structure separate from visible appearance
- `foundation/reference-authority.md` — observed, imaginative, and hybrid truth
- `foundation/scope-and-precedence.md` — geometry/structure/finish/style precedence and
  macro-before-micro correction

Use `foundation/occlusion-inference.md` when a visible structural relation disappears behind
another form and the hidden continuation materially affects pose, topology, contact, depth, or a
visible downstream anchor. Do not use it merely because some part of the subject is hidden.

## 2. Drawing mode

Choose one primary mode guide. Modes change emphasis, not geometry truth.

- `modes/croquis.md`
- `modes/figure-drawing.md`
- `modes/line-study.md`
- `modes/tonal-study.md`
- `modes/free-draw.md`

## 3. Observation

- `observation/visual-observation.md` — whole → relation → part → relation again, including turn/near-far and occlusion-anchor reads
- `observation/measuring-boundaries.md` — bounded measurements and ambiguous edges; measurement stops at occlusion even when Agent inference continues relationally

## 4. Construction

- `construction/gesture-and-masses.md` — flow and occupied masses
- `construction/orientation-and-twist.md` — major-mass turn, near/far planes, counter-rotation, anti-flattening
- `construction/balance-and-limbs.md` — support, joint chains, terminals, negative space
- `construction/foreshortening-and-depth.md` — projected length, near/far order, overlap, terminal orientation

For any observed subject, local description should not become the default next step merely because
a rough silhouette or simple construction exists. First ask whether the parent structure already
preserves the subject's placement, orientation, proportion, characteristic envelope/width change,
major overlap/contact/negative space, connected-part or anchor relations, and any hidden continuity
that materially constrains the visible arrangement. Defer secondary detail, not structural
specificity.

Earlier construction is provisional. Before a descriptive pass inherits it, compare the whole
drawing against its authority again. The same applies to hidden-continuation hypotheses: if the
visible entry/reappearance anchors no longer support the inference, revise it instead of bending
visible geometry around it. This is a drawing prerequisite, not a runtime stage; later evidence
may invalidate it at any time.

## 5. Description

- `description/descriptive-geometry.md` — exact form with economical lines; topology-aware curve choice and geometry-vs-material correction
- `description/contour-and-overlap.md` — visible contour ownership, occlusion/reappearance, contact, and separation from hidden construction
- `description/value-edge-and-graphite.md` — value family, edge behavior, pencil material

## 6. Subject-specific leaves

Figure:
- `figure/head-face-hair.md`
- `figure/torso-arms-hands.md`
- `figure/hands-and-grip.md`
- `figure/legs-feet.md`
- `figure/clothing-folds.md`

Other relationships:
- `props/attached-objects.md`
- `environment/ground-and-context.md`

## 7. Review and output

- `review/residual-correction.md` — inspect, prioritize, distinguish geometry/material residuals, correct coherent groups, re-inspect
- `review/residual-routing.md` — route a visible symptom to the responsible local or upstream premise
- `review/stroke-retirement.md` — remove or soften obsolete marks
- `review/authored-element-navigation.md` — find current authored elements before editing
- `review/completion.md` — current-evidence finish decision
- `output/render-profile-and-replay.md` — final PNG and end-to-end replay

When a local part looks wrong but its cause is uncertain, read `review/residual-routing.md`
instead of opening every subject leaf. Route by the relationship that must change, not by the
name of the visible part. A wrong shoe may belong to `figure/legs-feet.md`,
`construction/balance-and-limbs.md`, `environment/ground-and-context.md`, or
`description/contour-and-overlap.md` depending on the responsible cause. A whole figure that has
become flatter, more frontal, or more symmetric than the subject belongs upstream in
`construction/orientation-and-twist.md` even when the individual local contours look clean. A
visible fragment that incorrectly behaves as though it terminates at an occluder belongs first to
`foundation/occlusion-inference.md` when continuity is structurally necessary.

If geometry is already correct but a line reads broken because of taper, weight, opacity, pressure,
or graphite behavior, route to `review/residual-correction.md` and preserve the authored points
while retuning the material. Do not turn a material residual into an accidental geometry edit.

## 8. Public runtime API

- `api/public-surface.md` — supported public contracts and common operations only

Do not use API or implementation documentation as drawing knowledge. If a contour, head,
foot, fold, prop, or grounding problem remains, route to the visual leaf that owns that
problem rather than adding more generic strokes. If a local correction keeps failing,
escalate to the parent structural or observation premise rather than polishing the symptom.