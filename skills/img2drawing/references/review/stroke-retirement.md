# Stroke retirement and stage handoff

Retiring a stroke is a representation decision, not a judgement about whether the
earlier stroke was originally correct. A valid gesture line may be removed from the
visible current-stage drawing once a later stage owns that information in a different
representation.

## Choose the operation by visible intent

- `soft_lift`: keep the stroke as a faint underdrawing when it still explains weight,
  pose rhythm, construction or an occluded handoff. Use `soft_lift_segment` when only a
  bounded part of a stroke should recede.
- `delete_stroke`: remove the complete stroke from the active drawing when the current
  stage's representation has taken over and the earlier line must no longer be visible.
  The earlier stroke may have been correct in its own stage. Typical cases include a
  measured block replacing a placement cue, a mass replacing an axis, or a final contour
  replacing exploratory construction.
- `hard_delete`: the history-layer operation executed by `delete_stroke`; it records a
  `stroke.delete` event and removes the target from replayed active state. It is not a
  separate `DrawingAction.kind`, and `kind="hard_delete"` is invalid.

Both retirement paths preserve the action history and provenance. “Delete” means remove
the stroke from the current visible branch, not mutate or raster-erase the evidence.
Use an explicit target stroke id, record the observation and reason, then render a fresh
review after the mutation.

## Stage handoff test

Before retiring a line, ask:

1. Does the current stage contract still require this line to remain visible?
2. Is its information carried by a new axis, block, mass or contour?
3. Should it remain as a useful faint cue, or would its presence create a duplicate or
   violate the current stage grammar?

Keep or `soft_lift` when the answer to (3) is “useful cue”. Use `delete_stroke` when the
answer is “must be absent”. A hard deletion does not invalidate the earlier stage: its
artifact, review evidence and history remain available as the prior.
