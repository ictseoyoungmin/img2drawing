# Stroke dynamics

Stroke dynamics are the explicitly authored changes that happen along one mark: pressure, width,
opacity, taper, contact, and related local behavior. They belong below semantic role and tool preset
in the authority hierarchy.

Do not treat dynamics as decoration. They can communicate weight, release, overlap, softness,
acceleration, material contact, and focal hierarchy.

## Authoring order

For a mark whose path is already justified:

1. choose its semantic role;
2. choose the nearest public tool preset;
3. author the local pressure/width/opacity behavior required by the observed or declared relation;
4. render and inspect the actual pixels;
5. retune dynamics without changing geometry when the path is already correct.

## Common dynamics patterns

These are reusable patterns, not fixed curves:

- **light-flat** — low, nearly stable pressure for provisional construction;
- **swell-release** — low to stronger pressure, then a controlled release for gesture/form flow;
- **weighted-contour** — stronger only around the ownership/contact interval that needs emphasis;
- **short-dark-accent** — high local deposition over a short interval, then a clean stop or release;
- **push-flick** — moderate/strong contact followed by rapid pressure collapse for hair-like terminals;
- **broad-contact** — broad diameter with pressure that controls contact/deposition without assuming a
  filled opaque band;
- **hatch-repeat** — repeated related strokes whose small variation still reads as one value family.

## Preserve explicit dynamics in replay

If pressure or another dynamic was explicitly authored, it is part of the drawing decision. A tool
retune or preset revision must not silently regenerate it as though it were derived data.

Preset names explain intent; the resolved tool state and explicit authored dynamics are the replay
authority. Historical output must not change merely because a newer preset definition exists.

## Retune rather than redraw

When geometry is correct but the mark reads wrong because of weight, taper, opacity, pressure, or
material contact, keep the authored points and retune the material through the public runtime.
Do not redraw a different path to compensate for a material defect.

## Explicit curve and pressure helpers

Sample an agent-chosen smooth cubic Bezier interval or resample a smooth
polyline by approximate arc length. Split at real corners; the resampler can
cut across corners and is not a topology detector. Use pressure knots from
normalized path positions 0 to 1 to preserve an observed pressure rhythm even
with uneven sampling. Inspect endpoint gap and tangent change with
`curve_join`, and apply endpoint-locked local displacement with
`deform_interval`. No automatic beautification or smoothing of actual cusps.

To apply geometry edits, import `StrokeEdit` and `apply_stroke_edits` from
`img2drawing.authoring`. The latter takes a session, explicit edit records,
reason and observation_id. `transform_strokes(session, stroke_ids, matrix)`
prepares affine geometry only, retaining material. `preview_stroke_edits`
renders the prospective history using the same profile without committing it.
Pass its base_cursor and base_state_hash as expected_cursor and expected_state_hash
on apply; stale evidence fails closed. Split with an explicit interior point index
and new stroke ID. The appended fragment can alter overlap/contact and is not
promised to render pixel-identically; compare before accepting.

## Explicit local attenuation

When only part of a correct path is too dark, inspect its current stroke samples and use
`session.soft_lift_segment(stroke_id, start_index, end_index, strength=..., feather_points=...,
reason=..., observation_id=...)`. The zero-based range is inclusive, with at least two samples.
Strength is in [0,1]; feathering linearly reduces attenuation on neighboring samples. The method
records a normal history action and retains geometry/material/ownership. This is local pressure
attenuation, not a freeform pixel eraser; the rendered mark may still be visible. Use current
stroke IDs, and optionally pass `expected_cursor` and `expected_state_hash` to reject stale edits.
`retune_stroke` and `reshape_stroke` preserve a locally erased pressure curve; if a replacement
profile is needed, choose it explicitly rather than accidentally restoring a removed mark.

## Preview heterogeneous material corrections

An existing `StrokeEdit` can include optional `material_overrides` for explicit
`width`, `opacity`, `hardness` and `grain` edits. Each stroke can carry different
values in the same atomic preview/apply batch. The overrides are copied and validated;
width must be finite and positive, and the other values finite in [0,1]. The current
pressure curve (including local soft lift), visible opacity and other material fields
remain unchanged unless explicitly replaced. For a pressure change supply the separate
`pressure` samples; this path does not regenerate pressure from taper or grade.

```python
# current is the explicitly selected current stroke, obtained from the session.
edit = StrokeEdit(current.stroke_id, tuple(current.points),
                  material_overrides={"opacity": chosen_opacity, "width": chosen_width})
preview = preview_stroke_edits(session, [edit], preview_path,
                              reason=reason, observation_id=observation_id)
# Read the preview and choose whether to accept it. Re-preview any changed subset.
apply_stroke_edits(session, [edit], reason=reason, observation_id=observation_id,
                   expected_cursor=preview["base_cursor"],
                   expected_state_hash=preview["base_state_hash"])
```

Use the same explicit edits and provenance for apply. A rejected preview changes no
actions. It is not a canonical render until committed and checked. Re-open the geometry
or material premise when the preview reveals wrong overlap or an invented tonal band.

## Preview an explicit stroke-family rewrite

For a wrong value family, editing the old strokes alone may preserve the wrong premise.
The existing preview/apply helpers also accept `retire_ids` and `additions` in the same
atomic batch as ordinary StrokeEdit records. Choose current IDs to retire and author each
new mark as an ordinary draw-kwargs mapping with explicit fresh stroke_id, points, role,
and tool. Edits run first, then retirements, then additions. New strokes append in the
ordinary history/layer order; inspect the resulting overlaps. These are existing replace,
delete and draw actions, not a mask, a raster eraser or automatic hatch generation.

```python
batch = dict(reason=reason, observation_id=observation_id,
             retire_ids=selected_current_ids, additions=explicit_new_marks)
preview = preview_stroke_edits(session, edits, preview_path, **batch)
# Review the candidate visually; reject or re-preview any changed proposal.
apply_stroke_edits(session, edits, **batch,
                   expected_cursor=preview["base_cursor"],
                   expected_state_hash=preview["base_state_hash"],
                   expected_action_digest=preview["action_digest"])
````

The additional digest binds the ordered resolved actions, including material, IDs,
points and provenance. Cursor/state guard against stale drawing evidence; the action
digest rejects changes to the reviewed proposal even on the same drawing state. Supply
all three when committing a reviewed candidate. A rejected preview modifies no drawing
history. Invalid/conflicting IDs or an invalid new mark roll back the entire batch.
