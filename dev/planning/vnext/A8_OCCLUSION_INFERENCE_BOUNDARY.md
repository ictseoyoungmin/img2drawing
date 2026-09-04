# A8 — Occlusion inference boundary

State: CLOSED
Date: 2026-09-05
Scope: deployable instruction guidance + regression coverage only

## Trigger

Exploratory current-version dogfood exposed an ambiguity in the existing rule against inventing
hidden endings. A worker could read that rule as “do not reason about anything behind an
occluder,” then treat a limb, connected part, garment mass, hair mass, prop relation, or contact as
if its structure terminated where visibility stopped.

That interpretation is too strong. It protects against fabricated hidden contour but can damage
pose, topology, contact, reach, depth, and downstream anchor placement.

## Decision

The canonical rule is now:

> Infer hidden structure when continuity requires it; do not fabricate hidden appearance.

This is not permission to complete hidden anatomy or objects from memory. The guidance separates
three authorities:

```text
visible evidence
  strongest authority: observed entry/reappearance anchors, local direction/width, overlap/contact

provisional hidden structure
  minimum continuation needed for continuity, pose, topology, contact, depth, or downstream anchors

rendered visible description
  visible boundaries only; inferred hidden appearance is not promoted to observed contour/detail
```

## Operational contract

When an occluded relation matters, the worker must:

1. identify visible entry and reappearance anchors when available;
2. compare local direction/tangent, width/taper, depth order, and nearby constraints on both sides;
3. form the minimum hidden continuation hypothesis needed to make the visible relation coherent;
4. keep that hypothesis provisional and lower-authority than visible evidence;
5. reduce certainty when only one side is visible rather than either inventing a full terminal or
   abandoning structural inference;
6. render only visible contour in the final description unless the requested style intentionally
   shows construction/x-ray information;
7. retire or soften temporary hidden construction lines before they read as visible evidence;
8. reopen the parent premise when one plausible continuation cannot satisfy the visible anchors.

Measurement remains bounded by occlusion: no pixel/profile/ruler operation may claim the hidden
interval as measured. Agent inference is still allowed when justified relationally from visible
anchors and structural constraints.

## Deployable files changed

- `skills/img2drawing/SKILL.md`
- `skills/img2drawing/references/INDEX.md`
- `skills/img2drawing/references/foundation/occlusion-inference.md`
- `skills/img2drawing/references/observation/visual-observation.md`
- `skills/img2drawing/references/observation/measuring-boundaries.md`
- `skills/img2drawing/references/description/contour-and-overlap.md`
- `skills/img2drawing/references/review/residual-routing.md`

Regression ownership: `dev/tests/test_skill_surface_boundary.py`.

## Non-goals

A8 does not:

- add a hidden-geometry runtime representation;
- add an automatic occlusion solver;
- infer exact 3D geometry from a single image;
- authorize CV/edge tools to trace hidden structure;
- make construction strokes visible in the final drawing by default;
- introduce a stage gate or subject-specific workflow;
- change API/schema/render/persistence contracts.

## Validation impact

D01 remains the next formal sealed validation case. It should now check both failure extremes:

- **under-inference** — the worker treats an occluded structure as if it ends at the occluder and
  visible downstream relations drift;
- **over-inference** — the worker fabricates exact hidden contour/detail and renders it as observed.

A successful run may infer hidden continuity for reasoning while leaving the final occluded region
visually absent.