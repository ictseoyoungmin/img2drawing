# Optional Reference — Astra Spatial Study

> **OPTIONAL / NON-CANONICAL / EDIT FREELY**
>
> This document is not part of the canonical img2drawing instruction graph.
> It is intentionally outside `references/`, is not indexed by `references/INDEX.md`, and should not
> be loaded by default progressive routing.
>
> A development Astra that receives only the `skills/img2drawing/` folder may use this document as
> inspiration, copy parts of it into a local workflow, rewrite it, split it, extend it, or ignore it.
> If anything here conflicts with `SKILL.md` or canonical files under `references/`, the canonical
> img2drawing instructions win unless the developer explicitly chooses to fork them.

## Why this note exists

img2drawing is primarily a drawing skill, but drawing can also be used as a way to understand form.
For an Astra-like resident artist, a useful future workflow is not merely:

```text
reference image -> pretty drawing
```

but:

```text
reference image
-> observe projected evidence
-> draw the visible structure faithfully
-> form a provisional spatial hypothesis
-> test that hypothesis in 3D when useful
-> render the 3D result back into a comparable view
-> update the spatial understanding
```

This is especially relevant for cars, cameras, furniture, weapons, machinery, architecture fragments,
products, and other subjects whose identity depends strongly on silhouette, proportion, section,
part hierarchy, perspective, and curvature.

The goal is not to turn img2drawing into a 3D package. The useful idea is that **drawing becomes one
observation instrument in a broader spatial-learning loop**.

## Product-level mental model

Astra may treat drawing and 3D as different media inside one artistic study rather than unrelated jobs.
The artist owns intent and judgment; tool adapters only execute operations.

A possible high-level loop is:

```text
OBSERVE
  -> INTERPRET
  -> CONSTRUCT
  -> DRAW
  -> OBSERVE OWN DRAWING
  -> CRITIQUE
  -> FORM SPATIAL HYPOTHESIS
  -> OPTIONAL 3D CONSTRUCTION
  -> RENDER SAME / COMPARABLE VIEW
  -> COMPARE
  -> CORRECT DRAWING, 3D, OR HYPOTHESIS
```

Do not interpret this as a mandatory stage machine. Reopen upstream assumptions whenever evidence
shows that the current explanation is wrong.

## Suggested optional mode: spatial study

A local Astra fork may introduce a `spatial-study` mode if useful.

Its purpose would be:

> Reconstruct the observed 2D projection without avoidable distortion, while explicitly separating
> what is visible from what is inferred about the underlying 3D form.

This mode is most useful when the drawing may later guide 3D construction or when 3D reconstruction
may improve the artist's understanding of the original image.

### What matters first

For a rigid or semi-rigid object, prefer this order of authority:

1. frame placement and overall projected envelope;
2. silhouette and major negative spaces;
3. dominant axes and perspective relationships;
4. landmark positions and proportional intervals;
5. major visible masses and section changes;
6. part hierarchy, overlaps, seams, openings, and repeated features;
7. local curvature and characteristic details;
8. material/value cues only after the structure they describe is credible.

A detailed drawing with a wrong wheelbase, roof arc, camera angle, or body width is less useful than a
sparse drawing that preserves those relations accurately.

## Example: vehicle study

If the user gives Astra a car image and says "draw this", an optional spatial-study interpretation
could preserve the canonical drawing request while paying special attention to:

- total projected length and height;
- wheel centers, wheel radii, wheelbase, and ground contact;
- front and rear overhang;
- roof, hood, trunk, rocker, and belt-line flow;
- windshield and rear-glass angles;
- wheel-arch envelopes;
- visible near/far-side displacement;
- lamp, intake, window, door, and panel-break topology;
- repeated/symmetric elements;
- visible curvature changes that imply cross-section;
- occlusion order and negative spaces.

Do not replace observation with a generic "car schema". A sports coupe, hatchback, sedan, truck, and
concept vehicle should not collapse into the same memorized construction.

## Observed, inferred, unknown

The most important rule for a Drawing -> 3D bridge is to avoid promoting guesses into facts.
Keep three classes separate.

### Observed

Supported directly by the reference or by measurements made from it.

Examples:

- visible silhouette;
- projected wheel ellipse;
- visible seam;
- lamp boundary;
- near-side rocker line;
- overlap order;
- measured landmark spacing.

### Inferred

A provisional 3D explanation that is useful but not directly visible.

Examples:

- likely symmetry plane;
- hidden continuation of a wheel cylinder;
- estimated body cross-section;
- inferred far-side volume;
- likely part thickness.

### Unknown

Insufficiently constrained by the current evidence.

Examples:

- hidden rear curvature from a single front three-quarter image;
- exact far-side seam path;
- unseen underside topology;
- true depth of a cavity with no supporting cue.

Unknown is a valid state. Do not force completion by inventing geometry.

## Optional `SpatialStudyRecord`

A developer may use a lightweight record like this, rename it, or replace it entirely:

```text
SpatialStudyRecord {
  reference_id

  observed {
    silhouette
    landmarks
    dominant_axes
    symmetry_cues
    visible_part_boundaries
    negative_spaces
    occlusion_order
    repeated_features
    apparent_width_changes
  }

  inferred {
    major_volumes
    section_shapes
    depth_order
    hidden_continuity
    likely_symmetry_plane
    part_hierarchy
  }

  unknown {
    ambiguous_regions
    hidden_form
    weakly_constrained_depth
  }

  drawing_artifact
  critique_history
  optional_3d_artifact
  validation_views
}
```

This is a design sketch, not an img2drawing API contract.

## Optional Drawing -> 3D handoff

If a 3D adapter is available, do not hand off only a PNG.
The useful payload is the drawing **plus the structural understanding acquired while drawing**.

A handoff may include:

- reference identity and crop/view metadata;
- projected silhouette/envelope;
- high-confidence landmarks;
- dominant axes;
- measured ratios;
- part hierarchy;
- visible/inferred/unknown classification;
- cross-contour or section hypotheses;
- symmetry hypotheses;
- occlusion relationships;
- regions that must not be hallucinated;
- the latest drawing and critique residuals.

The 3D tool may then construct a candidate model and render it from the reference camera or the closest
recoverable view.

## Same-view validation

The strongest bridge between drawing and 3D is projection validation.

```text
reference image
      |\
      | \-> authored 2D drawing
      |
      \----> candidate 3D model
                 |
                 v
          same-view render
```

Compare all three where practical:

```text
reference <-> drawing
reference <-> 3D render
drawing   <-> 3D render
```

A 3D model is not validated merely because it looks plausible in orbit view. It should explain the
observed projection that motivated it.

When the 3D result disagrees with the reference, identify which authority is wrong:

- drawing projection;
- camera/view estimate;
- spatial hypothesis;
- 3D geometry;
- or an assumption that should remain unknown.

Then correct the owning layer rather than cosmetically compensating downstream.

## Form memory, not blind self-training

"Astra learns 3D" does not have to mean online weight updates.
A safer first implementation is explicit memory of validated relationships.

Examples:

```text
2D cue                         -> validated spatial interpretation
wheel ellipse                  -> wheel-axis / cylinder orientation
roof + belt convergence        -> body perspective / camera relation
silhouette width transition    -> section change
contour + highlight behavior   -> likely convexity
near/far feature displacement  -> depth ordering
opening boundary + occlusion   -> cavity or inset hypothesis
```

Only promote an inference to reusable form memory when later evidence or a successful 3D projection
supports it. Keep failed hypotheses as failure evidence when useful.

## Suggested Studio-facing interpretation

If img2drawing is embedded in a larger artist system, avoid making "drawing" and "3D" mutually
exclusive session identities.

A useful conceptual model is:

```text
CreativeStudy {
  objective: spatial_understanding
  active_medium: drawing | 3d

  artifacts {
    drawing
    spatial_record
    model_3d
    validation_renders
  }

  critique_history
  current_focus
  uncertainty
}
```

This is intentionally adapter-agnostic. Blender, RefAs, another modeler, or a future tool may occupy
the 3D side without changing the artistic logic.

## Relationship to canonical img2drawing rules

This optional workflow should preserve the important img2drawing principles unless a developer
explicitly chooses otherwise:

- reference authority comes before generic priors;
- do not pixel-paste or trace the reference into the drawing;
- observed evidence and inferred hidden structure are different authorities;
- construct only enough hidden continuity to explain visible anchors;
- macro geometry outranks local detail;
- re-observe the actual rendered/drawn artifact;
- route residuals to their causal owner;
- reopen upstream structure when downstream polish cannot fix the mismatch;
- sparse drawing is acceptable only when the required relationships still read clearly.

## What this document does **not** require

It does not require img2drawing to:

- depend on RefAs, Blender, or any 3D runtime;
- add a canonical `spatial-study` mode;
- change `DrawingSession`;
- expose a new public API;
- generate 3D automatically after every drawing;
- infer invisible geometry from a single image as fact;
- store long-term memory;
- preserve this exact schema or terminology.

A development Astra may use none, some, or all of these ideas.

## Suggested first vertical slice

If this direction is explored, keep the first experiment narrow:

```text
one rigid object
-> one reference view
-> accurate structural drawing
-> explicit observed/inferred/unknown record
-> one simple 3D reconstruction
-> one same-view render
-> one reference/drawing/3D comparison
-> one correction loop
```

A car is a strong test because silhouette, perspective, repeated wheels, large smooth sections, hard
part boundaries, and camera sensitivity all matter at once.

Success should mean that the 3D exercise **improves the explanation of the reference**, not merely that
a plausible asset was produced.

## Freedom to fork

This file is deliberately disposable.

Astra may:

- rewrite the terminology;
- merge it into another skill;
- promote selected ideas into canonical `references/` after dogfooding;
- replace the record schema;
- adapt the workflow to a different 3D tool;
- delete the file if it stops being useful.

Do not preserve this document merely for compatibility. Preserve only the ideas that survive actual
artistic work and visual verification.
