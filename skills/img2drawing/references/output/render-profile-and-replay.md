# Render profile and replay

Final output and process replay must depict the same authored drawing under one persisted
rendering contract.

Use the public session output operations for final PNG rendering, cursor rendering, and timelapse
export. Do not switch pressure behavior, supersampling, paper/material parameters, or renderer
identity merely to make one artifact look better.

## Inspection shares the persisted profile

`inspect()` uses the same persisted material authority as `render_final()`: paper tooth/scale/seed,
background, graphite, renderer identity, and seed domain come from the bound profile rather than
renderer defaults. Inspection is nevertheless a derived evidence raster. It is always rendered at
1x canvas space for registration/ROI/measurement geometry and defaults to 3x internal
supersampling; final/replay export use the profile's persisted `output_scale` and `supersample`.

When a test or workflow requires pixel identity between the inspection raw drawing and a 1x final
render, request the profile supersampling explicitly:

```python
session.inspect(supersample=session.render_profile.supersample)
```

Do not change the persisted profile between inspection and export merely to improve one artifact.

## Timelapse export

There is exactly one timelapse operation:

```python
result = session.export_timelapse("out/timelapse", every_n=4)
result.gif_path          # action 0 -> latest GIF
result.final_path        # independently rendered canonical_final.png
result.manifest_path     # replay_manifest.json (backend, sampling, frame hashes)
```

Do not look for, import, or write another replay/timelapse exporter. `export_timelapse()` picks the
exact incremental backend when the history supports it and ffmpeg is available, and otherwise
renders every frame canonically for the whole export; both consume the bound `RenderProfile`, and
the export fails unless its last frame matches `canonical_final.png` exactly. `backend="canonical"`
forces full per-frame PNG rendering; `materialize_frames=True` also writes PNG frames on the fast
backend. Persistent patch and palette caches under the output directory are disposable acceleration
state, never drawing authority.

Replay is end-to-end: sampling always includes cursor 0 and the latest authored cursor. Coarser
`every_n` sampling is allowed; removing the beginning or final state is not.

## Renderer identity

A session's `RenderProfile` binds the renderer identity and its contract digest. A checkpoint bound
to a renderer this package cannot reproduce exactly (for example a pre-1.1 `v9`/`v10` profile, or a
history containing retired region-fill actions) fails closed instead of being silently re-rendered;
replay it with the release that produced it.
