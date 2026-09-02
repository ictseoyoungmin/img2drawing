# Canonical render profile, replay, and GIF

`RenderProfile` is the single versioned raster configuration for final PNG, cursor
replay, and GIF export. It is separate from `StyleGuide`: style tells the Agent how to
author marks, while the render profile materializes marks that already exist.

The persisted profile fixes renderer ID/version, canvas, built-in pencil-contact material,
paper tooth/scale/seed, supersampling and output scale, background/graphite colors,
deterministic seed domain, compositing, PNG mode, and GIF palette/loop/disposal. Custom
profile file paths and raster post-filters are not portable and are rejected.

## Canonical output

New sessions receive a canonical profile, or the caller may supply a fully validated
profile with the same canvas dimensions:

```python
profile = RenderProfile.canonical(width, height)
session = DrawingSession.create(
    subject="subject.png",
    output_dir="out",
    intent=intent,
    render_profile=profile,
)
final = session.render_final("out/final.png")
cursor_zero = session.render_at(0, "out/initial.png")
replay = session.export_timelapse("out/replay", mode="every_n", every_n=4)
```

`render_at()` rejects out-of-range cursors and non-PNG output. Cursor N means the state
after the first N authored actions. Cursor 0 and the latest cursor are always included in
replay. `mode="action"` emits every action cursor; `mode="every_n"` samples every N while
retaining both endpoints.

## Frames, timing, and parity

One `fill_region` or `replace_fill_region` action is one authored replay step even though
the renderer deterministically expands the region into many material contacts. It gets a
longer hold, not fake action frames. The replay manifest records ordinary/edit/region/final
timings, the pre-render pixel-work budget, and the enforced GIF byte-size budget.

The exporter renders the latest replay frame and canonical final PNG independently with
the same history/profile, then requires exact decoded PNG pixel equality. GIF is palette
encoded, so its final decoded frame uses the documented manifest tolerance: maximum
channel error 24 and mean channel error 2.0. The measured errors and result are recorded.
Renderer output never mutates geometry or action history.

## Older checkpoints and drift

A vNext checkpoint created before `RenderProfile` was persisted may resume without a
profile for continued editing, but all canonical output methods reject it. Call
`session.migrate_render_profile()` explicitly to attach the canonical profile and rewrite
the renderer header. Unknown renderer versions, canvas mismatch, profile/header mismatch,
unsupported seed/compositing/encoding policy, and custom material paths are rejected
rather than silently defaulted.
