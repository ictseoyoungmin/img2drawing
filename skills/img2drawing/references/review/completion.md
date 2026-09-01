# Intent-aware completion

Completion is an Agent decision that no material residual remains for the declared finish
intent in the exact current drawing. It is not a stage, lock, checklist percentage,
stroke threshold, likeness score, or automatic PASS.

## Required current truth

Before calling `finish()`:

1. declare a `DrawingIntent`;
2. inspect the current drawing after the last material mutation and intent change;
3. resolve every recorded material `ResidualRecord`; and
4. state any accepted limitations and nonmaterial notes explicitly.

Then bind the decision to the latest inspection:

```python
inspection_id = session.inspection_history[-1]["inspection_id"]
record = session.finish(
    final_inspection_id=inspection_id,
    rationale="No material pose residual remains in the current whole view.",
    accepted_limitations=("facial features are intentionally omitted",),
    unresolved_nonmaterial_notes=("paper texture is outside this task",),
)
assert session.finish_is_current
```

`FinishRecord` stores the current intent digest, drawing-state hash, action-history
cursor, final inspection ID, limitations, notes, and the Agent's rationale. The session
derives the hashes and cursor; callers do not supply them. The final inspection must be
the latest one, must describe the current drawing, and must have been made under the
current intent.

## Material residuals and limitations

An open `ResidualRecord` is treated as material and prevents completion. Do not copy its
wording into `accepted_limitations` to bypass correction. Resolve it through the ordinary
residual/correction loop. `unresolved_nonmaterial_notes` are observations that do not
materially affect the declared finish intent and therefore were not recorded as material
residuals.

Limitations document scope; they do not erase known defects. For example, omitted facial
features may be acceptable for `pose` finish, while a wrong weight-bearing leg is not.
An occluded hand may be a truthful limitation; inventing fingers or ignoring a broken
forearm-pocket contact is not.

## Stale completion and continued editing

Completion never locks the drawing. A later authored mutation or intent change preserves
the historical record but makes `session.finish_is_current` false. Discovering a new open
material residual also makes it false. Inspect the new state, use the same correction
loop, and record another finish decision. There is no finish stage to reopen.

Checkpoint/resume validates the record against its inspection, intent provenance, and
history bounds. Pre-B10 arbitrary `finish_metadata` may resume as noncanonical historical
metadata for compatibility, but it is not a `FinishRecord` and never makes
`finish_is_current` true.
