# Render profile and replay

Final output and process replay must depict the same authored drawing with the same persisted
rendering contract.

Use the public session output operations for final PNG rendering, cursor rendering, and timelapse
export. Do not switch pressure behavior, supersampling, paper/material parameters, or renderer
identity merely to make one artifact look better.

## Inspection shares the persisted profile

`inspect()` must render through the same persisted `RenderProfile` as `render_final()`: paper
tooth/scale/seed, background, and graphite come from the bound profile, not renderer defaults. The
inspection sheet always renders at 1x canvas space, because registration, ROI, and measurement
geometry are defined in canvas pixels; only final/replay export honors the profile's
`output_scale`. A custom profile (non-default paper, background, or graphite) must look the same in
an inspection sheet as it will in the final render — do not judge a drawing against one paper/light
setting and export it under another.

## v1.0.2 replay execution

`DrawingSession.export_timelapse()` uses the local-first exact incremental backend by default for
supported stroke histories. The fast engine must consume the bound `RenderProfile`, including
paper tooth/scale/seed, and its lossless final frame must match an independently rendered canonical
final RGB exactly.

Unsupported action semantics, raw ordered spatial erasers, or an unavailable fast encoder must
fail closed to the preserved canonical exporter for the whole replay. Do not combine canonical and
fast frame semantics inside one export.

The fast backend stores changing RGB rectangles in an atomic delta-frame pack and does not need to
materialize one PNG per frame. Frame PNG materialization is explicit/optional. Persistent patch and
palette caches are disposable acceleration state, never drawing authority.

Replay remains end-to-end: sampling must include cursor 0 and the latest authored cursor. Reducing
frame sampling is allowed, but must not remove the beginning or final state. Region/fill actions
that are not part of the fast semantic surface replay through the canonical fallback as authored
actions rather than being approximated.
