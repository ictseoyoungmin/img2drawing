# Instruction graph index

This directory is a routing graph, not a sequential course and not a runtime lifecycle.
Start at `SKILL.md`, then read only the smallest leaves that own the current drawing problem.

Path convention is intentionally different at the two routing levels. `SKILL.md` is at the skill
root, so it names leaves as `references/...`. This file is already inside `references/`, so paths
below are relative to the references root, such as `foundation/line-economy.md`. Do not copy the
INDEX-relative spelling back into `SKILL.md` without the `references/` prefix.

## Runtime-awareness invariant

The ordinary drawing worker is **runtime-aware and implementation-blind**.

Before authoring programmatic marks, know that `img2drawing` has a supported public runtime and
that final drawing mutations belong in `DrawingSession`. Read `api/public-surface.md` when you need
to operate that runtime. Do not replace it with an ad-hoc Pillow, OpenCV, SVG, canvas, or custom
raster drawing script merely because those libraries can draw pixels.

At the same time, ordinary drawing does **not** require reading the renderer implementation or the
whole `src/` tree. Private renderer classes, cache internals, history storage, and implementation
algorithms are framework concerns. Read implementation only for an explicit framework/debugging
task or when a demonstrated runtime defect must be investigated.

Pillow, NumPy, OpenCV, crops, overlays, and related tools may still support bounded observation or
evidence work when appropriate; they are not alternative final-authoring runtimes.

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

- `modes/gesture-drawing.md` — pure gesture vs constructive gesture; unqualified gesture requests default to constructive gesture
- `modes/croquis.md`
- `modes/figure-drawing.md`
- `modes/line-study.md`
- `modes/tonal-study.md`
- `modes/free-draw.md`

A user request for **gesture drawing** is a mode request, not merely permission to stop after the
construction gesture pass. Read `modes/gesture-drawing.md` first. Use pure gesture only when the
request explicitly asks for a quick/pure/line-of-action study; otherwise use constructive gesture.
If the user asks to *start* with gesture and then continue to a fuller drawing, gesture remains an
intermediate construction pass and the larger requested mode still owns completion.

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

## 6. Markmaking

Geometry answers **what relation should be drawn**. Markmaking answers **what kind of mark should
express that relation**. This branch is cross-cutting rather than a stage; construction, contour,
hair, hatching, accents, and environment work may use it whenever line language becomes relevant.

- `markmaking/style-policy.md` — whole-drawing material policy: canonical, manga-light, expressive graphite
- `markmaking/stroke-role-vocabulary.md` — semantic roles such as construction, gesture, form, contour, accent, hair, hatch, broad mass, environment
- `markmaking/tool-preset-selection.md` — reusable tool vocabulary and selection boundary
- `markmaking/stroke-dynamics.md` — authored pressure/width/opacity behavior and retuning
- `markmaking/pressure-and-terminals.md` — contact, gentle release, flick, residue, and physical-span terminal reasoning
- `markmaking/broad-graphite.md` — broad core/shoulder material behavior and style-dependent value authority
- `markmaking/custom-tools.md` — modifier → one-off dynamics → session-local tool → builtin promotion ladder

Do not use markmaking to hide bad geometry. If the visible path, overlap, proportion, or contact is
wrong, route to the visual leaf that owns the geometry first. If the path is correct but line
weight, pressure, taper, terminal, grain, or broad-contact behavior is wrong, preserve the points
and route through markmaking.

## 7. Subject-specific leaves

Figure:
- `figure/head-face-hair.md`
- `figure/torso-arms-hands.md`
- `figure/hands-and-grip.md`
- `figure/legs-feet.md`
- `figure/clothing-folds.md`

Other relationships:
- `props/attached-objects.md`
- `environment/ground-and-context.md`

## 8. Review and output

- `review/residual-correction.md` — inspect, prioritize, distinguish geometry/material residuals, correct coherent groups, re-inspect
- `review/residual-routing.md` — fast decision kernel for routing a visible symptom to one responsible local or upstream premise
- `review/markmaking-residuals.md` — distinguish wrong geometry from wrong role, dynamics, style policy, or runtime capability
- `review/stroke-retirement.md` — remove or soften obsolete marks
- `review/authored-element-navigation.md` — find current authored elements before editing
- `review/completion.md` — current-evidence finish decision
- `output/render-profile-and-replay.md` — final PNG and end-to-end replay

When the cause is not already obvious, enter `review/residual-routing.md` through its fast routing
kernel before opening a subject-specific leaf. First decide whether the evidence itself is uncertain,
the residual is global/multi-part, hidden-continuity, local geometry/contact, mark-language/material,
or another local issue. Then choose one primary owner, state what relationship must change, and
define what fresh visual evidence would prove the correction worked. A deliberate local correction
that leaves the same residual materially unchanged is evidence to escalate to the parent premise
rather than repeat the same local edit.

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
terminal, graphite behavior, or style policy, route to `review/markmaking-residuals.md` and preserve
the authored points while retuning the material. Do not turn a markmaking residual into an
accidental geometry edit.

## 9. Public runtime API

- `api/public-surface.md` — supported public contracts and common operations only

For programmatic drawing, read the public runtime surface before authoring the first mark. This is
not permission to read the whole implementation. The public surface is the operational boundary;
private modules remain implementation details unless the task is framework development or runtime
debugging.

Do not use API or implementation documentation as drawing knowledge. If a contour, head,
foot, fold, prop, or grounding problem remains, route to the visual leaf that owns that
problem rather than adding more generic strokes. If a local correction keeps failing,
escalate to the parent structural or observation premise rather than polishing the symptom.
