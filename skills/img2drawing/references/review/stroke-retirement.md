# Stroke retirement and explicit replacement

Retiring a stroke is a representation decision, not a judgement about whether the
earlier stroke was originally correct. A new contour, axis, mass, or gesture may carry
the same information more clearly while the old mark becomes redundant.

## Choose by visible intent

- `soft_lift`: keep a faint cue when it still explains weight, rhythm, construction, or
  an occluded handoff. Use `soft_lift_segment` for a bounded part.
- `delete_stroke`: remove a complete stroke from the current visible drawing when the new
  representation fully replaces it. The old stroke and deletion event remain in history.
- `hard_delete`: history-layer implementation behind `delete_stroke`; it is not a public
  drawing action kind.

## Handoff test

Before the mutation, ask:

1. Is the old stroke's information carried by a new explicit representation?
2. Would keeping it create a duplicate, welded contour, or misleading width?
3. Does it still help the viewer read weight, rhythm, or occlusion?

Keep or soft-lift when the answer to (3) is yes. Delete when the old mark must be absent.
In both cases, supply the target stroke, current observation, and reason through the
session API. Never raster-edit the image or mutate history outside an action.

## Re-inspection

Any replacement, lift, delete, or added stroke makes prior visual evidence stale. Render
the new snapshot, inspect the affected relation and whole drawing, and retain the change
only when the current state materially improves the declared intent. An edit event alone
is not proof of improvement.

For R23 stage-owned retirement and compatibility semantics, use the explicit
[`legacy-r23.md`](../legacy-r23.md) route.
