# Authored element navigation and editing

Long correction loops use the action history as their only source of truth. The
navigation API rebuilds immutable `AuthoredElement` records from that history whenever it
is called; it does not persist an ownership index, edit cursor, or summary cache.

## Find the responsible authored decision

```python
near_arm = session.authored_elements(
    element_type="stroke",
    status="current",
    part="near_arm",
    role="contour",
)
from_observation = session.authored_elements(observation_id="body-read")
from_action = session.authored_elements(action_id="replace-arm-contour")
```

Each record carries stroke/fill identity, current/superseded/deleted status, part, role,
creation/latest sequence, every related action and observation id, latest action kind,
reason, replacement target, and revision count. Fill-generated hatch/contact strokes are
render products and never appear as authored elements.

Use `status=None` to audit historical identities. `resolve_authored_element(old_id)`
follows an explicit whole-stroke replacement chain to the current identity. It returns
`None` when that chain ends in deletion. `current_stroke(old_id)` returns a detached copy
of the current stroke; `current_fill_region(fill_id)` returns the latest stable fill
definition. A stroke and fill may share a string id, so pass `element_type` when an id is
ambiguous.

## Edit through the same session

After locating responsibility, use the existing methods:

```text
draw / draw_many
replace_stroke / replace_segment
soft_lift / soft_lift_segment / delete_stroke
fill_region / replace_fill_region
```

`DrawingSession.replace_fill_region()` is the canonical fill revision method. The root
`replace_fill_region(session, ...)` function remains a compatibility delegate and contains
no second implementation.

Every mutation appends through the same atomic checkpointed transaction. A stale or
superseded stroke id, missing fill, duplicate action id, or reused stroke identity fails
before a partial edit can remain. Segment edits preserve stroke identity; whole-stroke
replacement creates explicit ancestry; fill replacement preserves one fill identity and
increments its authored revision.

## Bounded context

```python
summary = session.authoring_summary(limit=12, part="near_arm")
```

The summary binds its counts and limited current records to the current history cursor and
drawing-state hash. It includes open residual ids and reports truncation. It is derived on
demand and absent from checkpoints, so it cannot become a competing state authority.

Use the summary to navigate, not to judge quality or choose a residual automatically. The
Agent still inspects current evidence, names the highest-impact mismatch, performs an
explicit edit, and inspects again.
