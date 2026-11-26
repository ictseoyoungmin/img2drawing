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

## Explicit opacity-normalized contact profile

`RenderProfile.canonical(width, height)` retains exact Pencil v11 behavior.
For a **new** session that needs controllable light graphite deposits, an explicit
opt-in is available:

```python
from img2drawing import DrawingSession, RenderProfile
profile = RenderProfile.opacity_normalized(width, height)
session = DrawingSession.create(subject=subject, output_dir=output_dir,
                                render_profile=profile)
```

The variant `11-opacity-normalized-v1` uses the same pencil engine but integrates
authored contact alpha over traveled distance, constrains continuity floors to
local alpha, and deposits nothing at zero opacity. Intentional overlapping
passes still accumulate. It is not a universal linear opacity guarantee:
pressure, grade, geometry, grain, overlap and sampling all affect the result.
It has a separate immutable renderer contract digest, checked on resume; existing
v11 checkpoints are **not** silently migrated, and v11 remains the default.
Use the same bound variant for inspection, preview, final and GIF replay.
Do not use profile switching as a correction to a finished drawing.

## Agent-facing handoff and recovery

When the user needs the project, put the authored script(s), session checkpoint, reference
location, outputs, environment/dependency instructions and replay manifest together in a
discoverable project directory. Document commands from the stated working directory, and test
them when feasible. Do not imply that a PNG alone contains the drawing history.

The pixel-work error reports the required work and budget before writing output. Increase
`every_n` or explicitly choose a larger budget when warranted; both endpoints remain included.
If the fast GIF's global palette fails final-frame fidelity, export retries with local frame
palettes under the persisted profile and the same tolerance. If that still fails, no unvalidated
GIF is returned; report the measured error and retain the independent final PNG.

For long exports, pass `progress=callback` to `session.export_timelapse()`. The callback
receives dictionaries with `phase` (`render`, `encode`, `verify`, or `retry`) and `completed`/`total` sampled
frames. Callbacks execute synchronously while the session is locked; use them for reporting,
not session mutation. Exceptions in the callback abort the export.


## Memory-bounded palette recovery (v1.2.0 development)

If FFmpeg's global-palette fast GIF fails final-frame fidelity, the exporter
re-reads the exact delta pack and encodes each frame with its own local palette.
The decoder, quantizer, and GIF writer consume **one frame at a time**; they do
not retain a list of decoded or indexed frames and do not spool a PNG sequence.
The canonical GIF writer also streams its input PNG frames. The final GIF is
atomically replaced after encoding, then verified against the independent
canonical final PNG using the unchanged tolerance and file-size budget.

The manifest's authoritative GIF hash is `gif.sha256`; the fast encoding
record's `gif_sha256` refers to the **same final file**. An unsuccessful FFmpeg
attempt is explicitly kept under `fast.encode.initial_attempt`. Retry time is
included in final encoding and pipeline performance figures.

Progress callbacks report render frames, encode 0→1, verify 0→1 and, when
necessary, retry frames 0→N. A completed retry frame count is not an
all-phases-complete signal; the final verify event closes the operation.

Explicit ordered path-lift marks are eligible for Fast replay. The append path
uses the canonical graphite-lifting function; non-append or out-of-layer-order
changes with an active/retired lift conservatively recomposite the full canvas
from cached graphite patches in canonical order. This preserves pixels but can
increase editing/replay cost. Legacy unmarked raw erasers remain ineligible.

Research option: `opacity_normalized(..., pressure_lift=True)` selects
`11-opacity-normalized-v2`, a distinct immutable renderer contract with an
explicit pressure-shaped graphite lift. Existing v11 and normalized v1
identities/digests remain unchanged. No automatic migration. Constant lifts
and ordinary graphite remain unchanged; the new pressure-shaped lift requires
the new profile in both canonical and Fast replay. The research option has
not passed independent visual acceptance or large-session performance gates.
