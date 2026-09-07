# S08 — Edit-semantics closure for incremental timelapse replay

State: **CLOSED AS A DEV PROTOTYPE / CONTRACT SLICE**

S08 closes the remaining semantic question before production exporter integration: which current
img2drawing edit operations can use the S02–S07 exact incremental replay path, and which operations
must fall back to the existing canonical full renderer.

Production runtime behavior is unchanged in this slice.

## Current product semantics inspected

The canonical action surface persists these stroke edits:

- `replace_segment` → `stroke.segment_replace`
- `soft_lift_segment` → `stroke.segment_soft_lift` at core action/history level
- `soft_lift` → `stroke.soft_lift`
- `delete_stroke` → `stroke.delete`
- `retune_stroke` → the existing `stroke.replace` path with geometry preserved

These all resolve to a changed/removed current `Stroke` identity in `CanvasHistory.state_at()`. They
are therefore compatible with S06/S07's authoritative dirty-region rebuild: invalidate old/new
bounds, materialize the changed current stroke once, rebuild intersecting active layers, and release
the obsolete material version.

`DrawingSession` currently has no `soft_lift_segment()` convenience helper, although the persisted
core action/history semantics already support it. This is an authoring-ergonomics gap, not a replay
semantic gap, and S08 does not add a second API path just to close the exporter contract.

## Exact semantic regression

A public vNext imaginative line-study session authored three overlapping explicit-pressure strokes
and then applied, in order:

1. segment replacement,
2. core `soft_lift_segment`,
3. whole-stroke soft lift,
4. `retune_stroke`,
5. delete.

At every state the S07 alpha-active incremental compositor was compared with the production
`pillow-pencil-contact-v9` renderer at the same ss2 profile for a fast exact regression.

Result: **6 / 6 frames pixel-exact**.

`retune_stroke` preserved geometry exactly and produced the existing `stroke.replace` history action.
The final edit-action tail was:

```text
stroke.segment_replace
stroke.segment_soft_lift
stroke.soft_lift
stroke.replace
stroke.delete
```

## Spatial eraser compatibility boundary

The lower-level renderer still supports ordered spatial eraser `StrokeIR` marks through
`pillow_eraser_material`: an erase-mode stroke lifts previously deposited graphite in its footprint.
A synthetic raw-IR regression confirms that such an eraser is recognized by the production renderer
and changes output pixels.

However the current canonical vNext authoring path explicitly rejects an erase-mode tool passed to
`draw_stroke`; users retire or lighten authored marks through `soft_lift`, segment lift, or delete.
S07 also intentionally rejects raw spatial eraser strokes.

Therefore the production fast-export contract should be:

```text
canonical vNext semantic edits
    → incremental exact path

raw / legacy StrokeIR containing ordered spatial eraser strokes
    → fail fast-path eligibility
    → fall back to the existing canonical full renderer
```

This preserves compatibility without adding a second destructive-compositing model to the new fast
path before there is a canonical authoring need for it.

## Validation

```text
PYTHONPATH=src pytest -q dev/benchmarks/timelapse_perf/test_s08_edit_semantics.py
2 passed
```

The regression additionally proves:

- raw spatial eraser is recognized by the production renderer,
- its rendered result differs from draw-only output,
- S07 fast replay rejects the raw eraser,
- public vNext rejects erase-mode `draw_stroke`,
- retuning preserves geometry.

## Decision

Fast path supported:

- add / replace,
- `replace_segment`,
- `soft_lift_segment`,
- whole `soft_lift`,
- `retune_stroke` / material-only replacement,
- delete.

Compatibility fallback:

- raw/legacy ordered spatial eraser strokes.

S08 removes the need for another semantic prototype before integration. The next slice should fold
S02–S08 into the canonical streaming timelapse exporter, keep one render profile for the whole GIF,
stream frames without retaining the full frame set, reuse the sampled final state instead of
rendering it twice, and consolidate frame provenance into one replay manifest.
