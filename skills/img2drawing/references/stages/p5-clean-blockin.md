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

If a superseded line must be completely absent because the decided contour or handoff
fully replaces it, use the public `delete_stroke` action (`hard_delete` is its history
implementation). This is valid even when the earlier line was correct for its earlier
stage. Both actions keep the prior stroke and retirement event replayable; do not
raster-erase or mutate history merely for visual cleanliness.

Read `references/review/stroke-retirement.md` before choosing between a faint cue and a
fully retired stroke.

## Cleanup preflight
If the subject's clean silhouette cannot be drawn without contradicting P3 or P4, reopen
the earliest responsible stage before cleaning. Polishing a wrong structure just makes the
error permanent.

This cuts both ways. P5 is not sealed off from correction — an error that first becomes
visible here still has to be fixed. What P5 may not do is hide it under a better line. Send
it back to the stage that owns it, rebuild the stages below, and clean afterwards.

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
- **Repainting over an error.** A prettier line laid on top of wrong P3/P4 structure, instead of reopening the stage that owns it.
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
8. Construction retirement with `soft_lift` or, when the line must be absent,
   `delete_stroke`.

## Useful local review intents
`head+face`, `hair silhouette`, `garment contour`, `hands`, `footwear`, `overlap regions`.
