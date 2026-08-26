# P5 Clean Block-in — deciding which lines survive

**The question this stage answers: which lines are actually the final form?**

## Clean does not mean darker

This is the most misread word in the pipeline. **Clean is selection, not pressure.**

P5 does not go over the existing lines with a heavier stroke. It decides which of the many
exploratory lines is the real contour, and subordinates the rest.

## What P5 states
- the decisive outer silhouette;
- the face form;
- the hair silhouette;
- the garment contour;
- tidied hands and footwear;
- settled equipment form;
- contour ownership where masses overlap.

## What P5 is not

P5 is not a finished illustration. It still has no:
- tonal shading or filled black areas;
- surface texture;
- excessive garment folds;
- fine skin rendering.

The goal is not "looks finished". The goal is **an under-drawing solid enough that starting
detail work will not collapse the form.**

## Construction retirement

Draw the decided contour first, then subordinate the superseded construction with
`soft_lift`. Keep a faint gesture where it still explains weight.

Do not raster-erase history merely for visual cleanliness — the run stays replayable.

## Cleanup preflight
If the subject's clean silhouette cannot be drawn without contradicting P3 or P4, reopen
the earliest responsible stage before cleaning. Polishing a wrong structure just makes the
error permanent.

## Silhouette ownership

Do not weld two independent masses into one continuous contour. Where ownership changes
because of overlap, hand it off explicitly:
- terminate the outer contour;
- leave a visible break or occlusion;
- continue the hidden mass as an `overlap_contour` when needed.

Two independent strokes that come within a few pixels and share a near-parallel tangent can
read as one line after rendering, even though the renderer merges nothing.
`measure_contour_contact()` is evidence for this, not an automatic pass/fail rule.

## Common failures
- **Darkening instead of choosing.** Every exploratory line survives, just heavier.
- **Rendering.** Shading arrives because the drawing "looks unfinished".
- **Beautification.** A prettier line that quietly changes verified P3/P4 structure.
- **Welded contours** between the arm and the torso, or the prop and the body.
- **Hair strands** instead of a resolved hair silhouette.

## Hardening order
1. Cleanup preflight against P3/P4.
2. Decisive outer silhouette.
3. Face form.
4. Hair silhouette.
5. Garment contour.
6. Hands, footwear, equipment.
7. Overlap handoffs.
8. Construction retirement with `soft_lift`.

## Useful local review intents
`head+face`, `hair silhouette`, `garment contour`, `hands`, `footwear`, `overlap regions`.
