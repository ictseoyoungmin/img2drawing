# Public API and support matrix

Version: **0.6.0rc1** · public contract: **DrawingSession/0.6.0-vnext**

## Canonical vNext

New work imports `DrawingSession` and related plain-data records from `img2drawing`.
The supported mechanical surface is one session/history across:

| Capability | Public entry point |
|---|---|
| create and resume | `DrawingSession.create()`, `DrawingSession.resume()` |
| intent and authority | `DrawingIntent`, `ReferenceAuthority`, `ReferenceConstraint` |
| observe and author | `session.observe()`, `session.draw()`, `session.fill_region()` |
| inspect and correct | `session.inspect()`, residual/correction methods, replacement methods |
| navigate authorship | authored-element and summary methods on `DrawingSession` |
| finish provenance | `session.finish()` and `FinishRecord` |
| output and replay | `session.render_final()`, `session.render_at()`, `session.export_timelapse()` |

`img2drawing.__all__` is the authoritative root export list. A mode/style/finish guide is
authoring guidance, not a second renderer or lifecycle. Completion is an Agent decision
bound to current evidence, not an automatic quality score.

## Legacy compatibility

R23 checkpoint inspection, v1-v3 resume, and one-way migration remain supported only via
`img2drawing.legacy.r23`. Deprecated root attribute shims exist for old direct callers but
are intentionally absent from `img2drawing.__all__`. See `MIGRATION.md`.

Unknown checkpoint schemas are refused. Physical R23 removal is not part of this release
candidate.
